import asyncio
from typing import Dict, List, Callable, Any
from datetime import datetime
import logging

class EventSystem:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000

    async def emit(self, event_name: str, data: Any = None) -> None:
        """Emit an event to all subscribers."""
        try:
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'event': event_name,
                'data': data
            }
            self.event_history.append(event_data)
            
            # Trim history if needed
            if len(self.event_history) > self.max_history:
                self.event_history = self.event_history[-self.max_history:]
            
            if event_name in self.subscribers:
                for callback in self.subscribers[event_name]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(data)
                        else:
                            callback(data)
                    except Exception as e:
                        logging.error(f"Error in event handler for {event_name}: {e} - event_system.py:34")
        except Exception as e:
            logging.error(f"Error emitting event {event_name}: {e} - event_system.py:36")

    def subscribe(self, event_name: str, callback: Callable) -> Callable:
        """Subscribe to an event."""
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)
        
        def unsubscribe():
            if event_name in self.subscribers and callback in self.subscribers[event_name]:
                self.subscribers[event_name].remove(callback)
        
        return unsubscribe

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from history."""
        return self.event_history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self.event_history = []
