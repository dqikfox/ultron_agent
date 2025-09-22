"""
ULTRON Agent Event System
Provides cross-component communication and event handling
"""

import asyncio
import logging
from typing import Dict, List, Any, Callable, Awaitable, Optional
from dataclasses import dataclass
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from utils.ultron_logger import ultron_logger

@dataclass
class Event:
    """Represents an event in the system"""
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    event_id: str

class EventSystem:
    """
    Centralized event system for ULTRON Agent
    Handles event subscription, emission, and processing
    """

    def __init__(self):
        self.logger = ultron_logger
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="event-system")
        self._shutdown = False

    async def subscribe(self, event_name: str, callback: Callable) -> None:
        """
        Subscribe to an event

        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is emitted
        """
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []

        self.subscribers[event_name].append(callback)
        self.logger.info(f"Subscribed to event: {event_name}")

    async def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """
        Unsubscribe from an event

        Args:
            event_name: Name of the event
            callback: Function to remove
        """
        if event_name in self.subscribers:
            try:
                self.subscribers[event_name].remove(callback)
                self.logger.info(f"Unsubscribed from event: {event_name}")
            except ValueError:
                self.logger.warning(f"Callback not found for event: {event_name}")

    async def emit(self, event_name: str, data: Optional[Dict[str, Any]] = None,
                   source: str = "system") -> None:
        """
        Emit an event to all subscribers

        Args:
            event_name: Name of the event
            data: Event data payload
            source: Source component that emitted the event
        """
        if self._shutdown:
            return

        event_data = data or {}
        event = Event(
            name=event_name,
            data=event_data,
            timestamp=datetime.now(),
            source=source,
            event_id=f"{event_name}_{int(datetime.now().timestamp() * 1000)}"
        )

        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

        self.logger.info(f"Emitted event: {event_name}")

        # Notify subscribers
        if event_name in self.subscribers:
            tasks = []
            for callback in self.subscribers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        # Async callback
                        task = asyncio.create_task(callback(event_data))
                        tasks.append(task)
                    else:
                        # Sync callback - run in thread pool
                        task = asyncio.get_event_loop().run_in_executor(
                            self.executor, callback, event_data
                        )
                        tasks.append(task)
                except Exception as e:
                    self.logger.info(f"Error calling callback for event {event_name}: {str(e)}")
                    # Wait for all callbacks to complete
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
        Get event history

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

    def get_subscribers(self, event_name: str) -> List[Callable]:
        """Get list of subscribers for an event"""
        return self.subscribers.get(event_name, []).copy()

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
        """Get event system statistics"""
        total_events = len(self.event_history)
        events_by_type = {}

        for event in self.event_history:
            events_by_type[event.name] = events_by_type.get(event.name, 0) + 1

        return {
            "total_events": total_events,
            "events_by_type": events_by_type,
            "active_subscriptions": len(self.subscribers),
            "subscribed_events": list(self.subscribers.keys()),
            "max_history": self.max_history,
            "shutdown": self._shutdown
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
