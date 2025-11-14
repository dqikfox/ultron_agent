"""
ULTRON Agent Event System
Provides cross-component communication and event handling
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Callable, Awaitable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
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
    """Represents an event subscriber with priority"""
    callback: Callable
    priority: EventPriority = EventPriority.NORMAL
    filter_pattern: Optional[str] = None  # Regex pattern for filtering event data

@dataclass
class EventMetrics:
    """Event system performance metrics"""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    subscriber_performance: Dict[str, float] = field(default_factory=dict)
    failed_handlers: int = 0

class EventSystem:
    """
    Centralized event system for ULTRON Agent
    Handles event subscription, emission, and processing
    """

    def __init__(self):
        self.logger = ultron_logger
        self.subscribers: Dict[str, List[Subscriber]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="event-system")
        self._shutdown = False
        self.metrics = EventMetrics()
        self._event_batches: Dict[str, List[Event]] = defaultdict(list)
        self._batch_lock = asyncio.Lock()

    async def subscribe(self, event_name: str, callback: Callable,
                       priority: EventPriority = EventPriority.NORMAL,
                       filter_pattern: Optional[str] = None) -> None:
        """
        Subscribe to an event with optional priority and filtering

        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is emitted
            priority: Subscriber priority level (CRITICAL, HIGH, NORMAL, LOW)
            filter_pattern: Optional regex pattern to filter events
        """
        subscriber = Subscriber(callback=callback, priority=priority, filter_pattern=filter_pattern)
        self.subscribers[event_name].append(subscriber)

        # Sort by priority (lower value = higher priority)
        self.subscribers[event_name].sort(key=lambda s: s.priority.value)

        self.logger.info(f"Subscribed to event: {event_name} (priority: {priority.name})")

    async def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """
        Unsubscribe from an event

        Args:
            event_name: Name of the event
            callback: Function to remove
        """
        if event_name in self.subscribers:
            original_count = len(self.subscribers[event_name])
            self.subscribers[event_name] = [
                s for s in self.subscribers[event_name] if s.callback != callback
            ]
            if len(self.subscribers[event_name]) < original_count:
                self.logger.info(f"Unsubscribed from event: {event_name}")
            else:
                self.logger.warning(f"Callback not found for event: {event_name}")

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

    async def emit(self, event_name: str, data: Optional[Dict[str, Any]] = None,
                   source: str = "system", priority: EventPriority = EventPriority.NORMAL) -> None:
        """
        Emit an event to all subscribers

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
            priority=priority
        )

        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

        # Update metrics
        self.metrics.total_events += 1
        self.metrics.events_by_type[event_name] = self.metrics.events_by_type.get(event_name, 0) + 1

        self.logger.info(f"Emitted event: {event_name}")

        # Notify subscribers, respecting their priority
        if event_name in self.subscribers:
            tasks = []
            for subscriber in self.subscribers[event_name]:
                # Check filter pattern
                if subscriber.filter_pattern and not self._matches_filter(event_data, subscriber.filter_pattern):
                    continue

                try:
                    if asyncio.iscoroutinefunction(subscriber.callback):
                        task = asyncio.create_task(subscriber.callback(event_data))
                        tasks.append(task)
                    else:
                        task = asyncio.get_event_loop().run_in_executor(
                            self.executor, subscriber.callback, event_data
                        )
                        tasks.append(task)
                except Exception as e:
                    self.logger.error(f"Error calling callback for event {event_name}: {str(e)}")
                    self.metrics.failed_handlers += 1

            if tasks:
                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    self.logger.error(f"Error in event callbacks for {event_name}: {str(e)}")

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
        """Get list of subscribers for an event"""
        return [s.callback for s in self.subscribers.get(event_name, [])]

    def clear_history(self) -> None:
        """Clear event history"""
        self.event_history.clear()
        self.logger.info("Event history cleared")

    async def shutdown(self) -> None:
        """Shutdown the event system"""
        self._shutdown = True
        self.executor.shutdown(wait=True)
        self.logger.info("Event system shutdown")

    def get_stats(self) -> Dict[str, Any]:
        """Get event system statistics including metrics"""
        total_subscribers = sum(len(subs) for subs in self.subscribers.values())

        return {
            "total_events": self.metrics.total_events,
            "events_by_type": dict(self.metrics.events_by_type),
            "active_subscriptions": total_subscribers,
            "subscribed_events": list(self.subscribers.keys()),
            "max_history": self.max_history,
            "shutdown": self._shutdown,
            "failed_handlers": self.metrics.failed_handlers,
            "subscriber_count": total_subscribers
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed event system metrics"""
        return {
            "total_events_emitted": self.metrics.total_events,
            "events_by_type": dict(self.metrics.events_by_type),
            "failed_handler_count": self.metrics.failed_handlers,
            "history_size": len(self.event_history),
            "max_history": self.max_history,
            "subscriber_priorities": {
                event_name: [f"{s.callback.__name__}:{s.priority.name}" for s in subs]
                for event_name, subs in self.subscribers.items()
            }
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
    """Subscribe to an event"""
    system = get_event_system()
    await system.subscribe(event_name, callback)

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
