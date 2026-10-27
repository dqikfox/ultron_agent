"""
ULTRON Agent Event System
Provides cross-component communication and event handling

Enhancements over the original:
- Wildcard / glob-style event subscriptions (e.g. "tool.*", "*")
- subscribe_once() for one-shot callbacks
- Middleware chain: transform / gate events before dispatch
- Dead-letter queue: failed handler calls are stored for inspection / replay
- Event replay: re-dispatch a slice of the history to a new subscriber
"""

import asyncio
import fnmatch
import logging
import re
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from enum import Enum
from utils.ultron_logger import ultron_logger


class EventPriority(Enum):
    """Event subscriber priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Event:
    """Represents an event in the system"""
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    event_id: str
    priority: EventPriority = EventPriority.NORMAL


@dataclass
class Subscriber:
    """Represents an event subscriber with priority and optional one-shot flag"""
    callback: Callable
    priority: EventPriority = EventPriority.NORMAL
    filter_pattern: Optional[str] = None  # Regex pattern for filtering event data
    once: bool = False  # If True, remove after first successful invocation


@dataclass
class DeadLetterEntry:
    """Record of a handler that raised an exception"""
    event: Event
    callback_name: str
    error: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EventMetrics:
    """Event system performance metrics"""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    subscriber_performance: Dict[str, float] = field(default_factory=dict)
    failed_handlers: int = 0


class EventSystem:

    def self_test(self) -> dict:
        """
        Run diagnostics on the event system: check subscriptions, emit a test
        event, and return stats.  Returns a dict with status and details.
        """
        result = {"status": "ok", "errors": [], "details": {}}
        try:
            stats = self.get_stats()
            result["details"]["stats"] = stats
            try:
                self.emit_sync("diagnostic_test_event", {"msg": "test"})
                result["details"]["emit_test"] = "ok"
            except Exception as emit_err:
                result["status"] = "fail"
                result["errors"].append(f"Emit test event failed: {emit_err}")
        except Exception as e:
            result["status"] = "fail"
            result["errors"].append(str(e))
        return result

    def __init__(self):
        self.logger = ultron_logger
        # Exact-name subscribers
        self.subscribers: Dict[str, List[Subscriber]] = defaultdict(list)
        # Wildcard/glob pattern subscribers stored as (pattern, List[Subscriber])
        self._wildcard_subscribers: List[tuple] = []
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="event-system"
        )
        self._shutdown = False
        self.metrics = EventMetrics()
        # Dead-letter queue: events whose handlers raised exceptions
        self.dead_letter_queue: List[DeadLetterEntry] = []
        self.max_dead_letters = 200
        # Middleware chain: list of async callables (event) -> Optional[Event]
        # Return None to drop the event; return (possibly modified) event to continue.
        self._middleware: List[Callable] = []
        self._batch_lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Middleware management
    # ------------------------------------------------------------------

    def add_middleware(self, fn: Callable) -> None:
        """
        Add a middleware function to the processing chain.

        The middleware receives an ``Event`` and must return either the
        (possibly mutated) ``Event`` to continue processing, or ``None``
        to drop it silently.  Async middlewares are fully supported.

        Example::

            async def log_middleware(event: Event) -> Event:
                print(f"[middleware] {event.name}")
                return event

            event_system.add_middleware(log_middleware)
        """
        self._middleware.append(fn)

    def remove_middleware(self, fn: Callable) -> None:
        """Remove a previously registered middleware."""
        self._middleware = [m for m in self._middleware if m is not fn]

    async def _apply_middleware(self, event: Event) -> Optional[Event]:
        """Run the event through the middleware chain."""
        for mw in self._middleware:
            try:
                if asyncio.iscoroutinefunction(mw):
                    event = await mw(event)
                else:
                    event = mw(event)
                if event is None:
                    return None
            except Exception as exc:
                self.logger.error(f"Middleware error ({mw.__name__}): {exc}")
        return event

    # ------------------------------------------------------------------
    # Subscription helpers
    # ------------------------------------------------------------------

    def _is_wildcard(self, pattern: str) -> bool:
        """Return True when *pattern* contains glob wildcards."""
        return "*" in pattern or "?" in pattern or "[" in pattern

    async def subscribe(self, event_name: str, callback: Callable,
                       priority: EventPriority = EventPriority.NORMAL,
                       filter_pattern: Optional[str] = None) -> None:
        """
        Subscribe to an event with optional priority and filtering.

        *event_name* may contain shell-style wildcards (``*``, ``?``,
        ``[seq]``) to match multiple event types, e.g. ``"tool.*"`` or
        ``"*"`` for every event.

        Args:
            event_name: Name (or glob pattern) of the event to subscribe to.
            callback: Function to call when event is emitted.
            priority: Subscriber priority level (CRITICAL, HIGH, NORMAL, LOW).
            filter_pattern: Optional regex applied to the event payload str.
        """
        subscriber = Subscriber(
            callback=callback,
            priority=priority,
            filter_pattern=filter_pattern,
        )
        if self._is_wildcard(event_name):
            # Store (pattern, subscriber_list) for wildcard matching
            # Keep a single list per pattern to allow priority-sorted dispatch
            for pat, subs in self._wildcard_subscribers:
                if pat == event_name:
                    subs.append(subscriber)
                    subs.sort(key=lambda s: s.priority.value)
                    self.logger.info(
                        f"Subscribed (wildcard) to pattern: {event_name}"
                    )
                    return
            self._wildcard_subscribers.append((event_name, [subscriber]))
        else:
            self.subscribers[event_name].append(subscriber)
            self.subscribers[event_name].sort(key=lambda s: s.priority.value)

        self.logger.info(
            f"Subscribed to event: {event_name} (priority: {priority.name})"
        )

    async def subscribe_once(self, event_name: str, callback: Callable,
                             priority: EventPriority = EventPriority.NORMAL,
                             filter_pattern: Optional[str] = None) -> None:
        """
        Subscribe to exactly one occurrence of *event_name*.

        The callback is automatically removed after its first successful
        invocation, even for wildcard patterns.
        """
        subscriber = Subscriber(
            callback=callback,
            priority=priority,
            filter_pattern=filter_pattern,
            once=True,
        )
        if self._is_wildcard(event_name):
            for pat, subs in self._wildcard_subscribers:
                if pat == event_name:
                    subs.append(subscriber)
                    subs.sort(key=lambda s: s.priority.value)
                    return
            self._wildcard_subscribers.append((event_name, [subscriber]))
        else:
            self.subscribers[event_name].append(subscriber)
            self.subscribers[event_name].sort(key=lambda s: s.priority.value)

        self.logger.info(
            f"Subscribed (once) to event: {event_name}"
        )

    async def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """
        Unsubscribe from an event

        Args:
            event_name: Name of the event (exact or wildcard pattern)
            callback: Function to remove
        """
        if self._is_wildcard(event_name):
            for pat, subs in self._wildcard_subscribers:
                if pat == event_name:
                    before = len(subs)
                    subs[:] = [s for s in subs if s.callback != callback]
                    if len(subs) < before:
                        self.logger.info(
                            f"Unsubscribed from wildcard pattern: {event_name}"
                        )
                    return
        elif event_name in self.subscribers:
            original_count = len(self.subscribers[event_name])
            self.subscribers[event_name] = [
                s for s in self.subscribers[event_name]
                if s.callback != callback
            ]
            if len(self.subscribers[event_name]) < original_count:
                self.logger.info(f"Unsubscribed from event: {event_name}")
            else:
                self.logger.warning(
                    f"Callback not found for event: {event_name}"
                )

    async def validate_event(self, event_type: str, payload: dict) -> bool:
        """
        Validate event type and payload structure

        Args:
            event_type: Event type name
            payload: Event payload dictionary

        Returns:
            True if event is valid
        """
        if not isinstance(event_type, str) or not event_type.strip():
            self.logger.warning("Invalid event type: must be non-empty string")
            return False
        if not isinstance(payload, dict):
            self.logger.warning("Invalid payload: must be dictionary")
            return False
        return True

    def _matches_filter(self, payload: dict, filter_pattern: str) -> bool:
        """Check if payload matches filter pattern"""
        try:
            payload_str = str(payload)
            return bool(re.search(filter_pattern, payload_str))
        except re.error:
            self.logger.error(f"Invalid regex pattern: {filter_pattern}")
            return True  # Default to accepting if pattern is invalid

    def _collect_subscribers_for_event(
        self, event_name: str
    ) -> List[tuple]:
        """
        Return all (subscriber, list_ref) pairs that apply to *event_name*,
        including wildcard matches.  list_ref is needed so we can remove
        once-subscribers in-place.
        """
        result: List[tuple] = []
        # Exact-match subscribers
        if event_name in self.subscribers:
            for sub in list(self.subscribers[event_name]):
                result.append((sub, self.subscribers[event_name]))
        # Wildcard-pattern subscribers
        for pat, subs in self._wildcard_subscribers:
            if fnmatch.fnmatch(event_name, pat):
                for sub in list(subs):
                    result.append((sub, subs))
        return result

    async def _dispatch_subscriber(
        self,
        subscriber: "Subscriber",
        subs_list: list,
        event: Event,
    ) -> None:
        """Invoke a single subscriber, handling dead-letter and once-cleanup."""
        event_data = event.data
        try:
            if asyncio.iscoroutinefunction(subscriber.callback):
                await subscriber.callback(event_data)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor, subscriber.callback, event_data
                )
            # Remove once-subscriber on success
            if subscriber.once and subscriber in subs_list:
                subs_list.remove(subscriber)
        except Exception as exc:
            self.logger.error(
                f"Handler error [{subscriber.callback.__name__}] "
                f"for event '{event.name}': {exc}"
            )
            self.metrics.failed_handlers += 1
            self._add_dead_letter(event, subscriber.callback.__name__, str(exc))

    def _add_dead_letter(
        self, event: Event, callback_name: str, error: str
    ) -> None:
        """Record a failed handler invocation in the dead-letter queue."""
        entry = DeadLetterEntry(
            event=event, callback_name=callback_name, error=error
        )
        self.dead_letter_queue.append(entry)
        if len(self.dead_letter_queue) > self.max_dead_letters:
            self.dead_letter_queue = self.dead_letter_queue[-self.max_dead_letters:]

    async def emit(self, event_name: str, data: Optional[Dict[str, Any]] = None,
                   source: str = "system",
                   priority: EventPriority = EventPriority.NORMAL) -> None:
        """
        Emit an event to all matching subscribers.

        The event first passes through the middleware chain; if any middleware
        returns ``None`` the event is silently dropped.  Wildcard subscribers
        registered with patterns like ``"tool.*"`` or ``"*"`` are also notified.

        Args:
            event_name: Name of the event
            data: Event data payload
            source: Source component that emitted the event
            priority: Priority level of this event
        """
        if self._shutdown:
            return

        event_data = data or {}

        # Validate event before processing
        if not await self.validate_event(event_name, event_data):
            return

        event = Event(
            name=event_name,
            data=event_data,
            timestamp=datetime.now(),
            source=source,
            event_id=f"{event_name}_{int(datetime.now().timestamp() * 1000)}",
            priority=priority,
        )

        # Apply middleware chain
        event = await self._apply_middleware(event)
        if event is None:
            return  # Dropped by middleware

        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

        # Update metrics
        self.metrics.total_events += 1
        self.metrics.events_by_type[event_name] = (
            self.metrics.events_by_type.get(event_name, 0) + 1
        )

        self.logger.info(f"Emitted event: {event_name}")

        # Collect all applicable subscribers (exact + wildcard)
        applicable = self._collect_subscribers_for_event(event_name)
        if not applicable:
            return

        tasks = []
        for subscriber, subs_list in applicable:
            if (subscriber.filter_pattern and
                    not self._matches_filter(event.data, subscriber.filter_pattern)):
                continue
            tasks.append(
                asyncio.create_task(
                    self._dispatch_subscriber(subscriber, subs_list, event)
                )
            )

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def emit_sync(self, event_name: str, data: Optional[Dict[str, Any]] = None,
                  source: str = "system") -> None:
        """
        Synchronous version of emit for non-async contexts
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create task
                asyncio.create_task(self.emit(event_name, data, source))
            else:
                # Run in new loop
                loop.run_until_complete(self.emit(event_name, data, source))
        except RuntimeError:
            # No event loop, create new one
            asyncio.run(self.emit(event_name, data, source))

    def get_event_history(self, event_name: Optional[str] = None,
                         limit: Optional[int] = None) -> List[Event]:
        """
        Get event history with optional filtering

        Args:
            event_name: Filter by event name (optional)
            limit: Maximum number of events to return (optional)

        Returns:
            List of events
        """
        events = self.event_history

        if event_name:
            events = [e for e in events if e.name == event_name]

        if limit:
            events = events[-limit:]

        return events.copy()

    async def batch_events(self, batch_size: int = 10, timeout_ms: int = 1000) -> List[Event]:
        """
        Batch events by type for efficient processing

        Args:
            batch_size: Number of events to batch together
            timeout_ms: Timeout in milliseconds for batch collection

        Returns:
            List of batched events
        """
        async with self._batch_lock:
            batched = []
            current_batch = []

            for event in self.event_history[-batch_size:]:
                current_batch.append(event)
                if len(current_batch) >= batch_size:
                    batched.extend(current_batch)
                    current_batch = []

            if current_batch:
                batched.extend(current_batch)

            return batched

    def get_subscribers(self, event_name: str) -> List[Callable]:
        """Get list of subscribers for an event (exact match only)."""
        return [s.callback for s in self.subscribers.get(event_name, [])]

    def clear_history(self) -> None:
        """Clear event history"""
        self.event_history.clear()
        self.logger.info("Event history cleared")

    # ------------------------------------------------------------------
    # Dead-letter queue
    # ------------------------------------------------------------------

    def get_dead_letters(self, limit: Optional[int] = None) -> List[DeadLetterEntry]:
        """Return entries from the dead-letter queue (most recent first)."""
        entries = list(reversed(self.dead_letter_queue))
        return entries[:limit] if limit else entries

    def clear_dead_letters(self) -> None:
        """Clear the dead-letter queue."""
        self.dead_letter_queue.clear()

    async def replay_dead_letters(self, max_entries: int = 10) -> int:
        """
        Re-emit events from the dead-letter queue.

        Only entries whose event name still has at least one subscriber are
        replayed.  Successfully replayed entries are removed from the queue.

        Returns:
            Number of events successfully replayed.
        """
        replayed = 0
        remaining: List[DeadLetterEntry] = []
        for entry in list(self.dead_letter_queue)[:max_entries]:
            if (entry.event.name in self.subscribers or
                    any(fnmatch.fnmatch(entry.event.name, pat)
                        for pat, _ in self._wildcard_subscribers)):
                try:
                    await self.emit(
                        entry.event.name,
                        entry.event.data,
                        source=f"replay:{entry.event.source}",
                    )
                    replayed += 1
                except Exception:
                    remaining.append(entry)
            else:
                remaining.append(entry)
        self.dead_letter_queue = remaining + self.dead_letter_queue[max_entries:]
        return replayed

    # ------------------------------------------------------------------
    # Event replay from history
    # ------------------------------------------------------------------

    async def replay_history(
        self,
        callback: Callable,
        event_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> int:
        """
        Replay historical events to a single callback.

        Useful for catching a new subscriber up to recent state without
        having to re-emit events from source components.

        Args:
            callback: The function to call for each replayed event.
            event_name: Optional filter — only replay events with this name
                        (glob patterns supported).
            limit: Maximum number of events to replay (most recent first
                   when capped).

        Returns:
            Number of events replayed.
        """
        events = list(self.event_history)
        if event_name:
            if self._is_wildcard(event_name):
                events = [e for e in events if fnmatch.fnmatch(e.name, event_name)]
            else:
                events = [e for e in events if e.name == event_name]
        if limit:
            events = events[-limit:]
        count = 0
        for event in events:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event.data)
                else:
                    callback(event.data)
                count += 1
            except Exception as exc:
                self.logger.error(f"Replay callback error: {exc}")
        return count

    async def shutdown(self) -> None:
        """Shutdown the event system"""
        self._shutdown = True
        self.executor.shutdown(wait=True)
        self.logger.info("Event system shutdown")

    def get_stats(self) -> Dict[str, Any]:
        """Get event system statistics including metrics"""
        exact_subs = sum(len(subs) for subs in self.subscribers.values())
        wildcard_subs = sum(len(subs) for _, subs in self._wildcard_subscribers)
        total_subscribers = exact_subs + wildcard_subs

        return {
            "total_events": self.metrics.total_events,
            "events_by_type": dict(self.metrics.events_by_type),
            "active_subscriptions": total_subscribers,
            "exact_subscriptions": exact_subs,
            "wildcard_subscriptions": wildcard_subs,
            "wildcard_patterns": [p for p, _ in self._wildcard_subscribers],
            "subscribed_events": list(self.subscribers.keys()),
            "max_history": self.max_history,
            "shutdown": self._shutdown,
            "failed_handlers": self.metrics.failed_handlers,
            "dead_letter_count": len(self.dead_letter_queue),
            "middleware_count": len(self._middleware),
            "subscriber_count": total_subscribers,
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed event system metrics"""
        return {
            "total_events_emitted": self.metrics.total_events,
            "events_by_type": dict(self.metrics.events_by_type),
            "failed_handler_count": self.metrics.failed_handlers,
            "history_size": len(self.event_history),
            "max_history": self.max_history,
            "dead_letter_count": len(self.dead_letter_queue),
            "middleware_count": len(self._middleware),
            "subscriber_priorities": {
                event_name: [
                    f"{s.callback.__name__}:{s.priority.name}"
                    for s in subs
                ]
                for event_name, subs in self.subscribers.items()
            },
        }

# Global event system instance
_event_system_instance: Optional[EventSystem] = None
_event_system_lock = threading.Lock()

def get_event_system() -> EventSystem:
    """Get or create global event system instance"""
    global _event_system_instance
    if _event_system_instance is None:
        with _event_system_lock:
            if _event_system_instance is None:
                _event_system_instance = EventSystem()
    return _event_system_instance

# Convenience functions
async def subscribe_event(event_name: str, callback: Callable) -> None:
    """Subscribe to an event (supports wildcard patterns)."""
    system = get_event_system()
    await system.subscribe(event_name, callback)

async def subscribe_event_once(event_name: str, callback: Callable) -> None:
    """Subscribe to exactly one occurrence of an event."""
    system = get_event_system()
    await system.subscribe_once(event_name, callback)

async def emit_event(event_name: str, data: Optional[Dict[str, Any]] = None,
                    source: str = "system") -> None:
    """Emit an event"""
    system = get_event_system()
    await system.emit(event_name, data, source)

def emit_event_sync(event_name: str, data: Optional[Dict[str, Any]] = None,
                   source: str = "system") -> None:
    """Emit an event synchronously"""
    system = get_event_system()
    system.emit_sync(event_name, data, source)
