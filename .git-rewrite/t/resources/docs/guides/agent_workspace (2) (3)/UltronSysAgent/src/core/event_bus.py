"""
Event Bus for inter-module communication in UltronSysAgent
Provides pub/sub messaging between components
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class Event:
    """Event data structure"""
    id: str
    type: str
    data: Any
    source: str
    timestamp: datetime
    priority: int = 0  # Higher priority = processed first

class EventBus:
    """Central event bus for UltronSysAgent"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        self.processing = False
        
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to {event_type}: {callback.__name__}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                self.logger.debug(f"Unsubscribed from {event_type}: {callback.__name__}")
            except ValueError:
                pass
    
    async def publish(self, event_type: str, data: Any = None, source: str = "unknown", priority: int = 0):
        """Publish an event"""
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            source=source,
            timestamp=datetime.now(),
            priority=priority
        )
        
        await self.event_queue.put(event)
        self.logger.debug(f"Published event: {event_type} from {source}")
    
    async def process_events(self):
        """Process events from the queue"""
        if self.processing:
            return
            
        self.processing = True
        
        try:
            # Process all queued events
            events = []
            
            # Collect all pending events
            while not self.event_queue.empty():
                try:
                    event = self.event_queue.get_nowait()
                    events.append(event)
                except asyncio.QueueEmpty:
                    break
            
            # Sort by priority (higher priority first)
            events.sort(key=lambda e: e.priority, reverse=True)
            
            # Process events
            for event in events:
                await self._handle_event(event)
                
        finally:
            self.processing = False
    
    async def _handle_event(self, event: Event):
        """Handle a single event"""
        if event.type not in self.subscribers:
            return
        
        callbacks = self.subscribers[event.type].copy()  # Avoid modification during iteration
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
                    
            except Exception as e:
                self.logger.error(f"Error in event handler {callback.__name__}: {e}")
    
    def get_event_types(self) -> List[str]:
        """Get all subscribed event types"""
        return list(self.subscribers.keys())
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type"""
        return len(self.subscribers.get(event_type, []))

# Common event types
class EventTypes:
    """Standard event types used throughout UltronSysAgent"""
    
    # Voice events
    SPEECH_DETECTED = "speech_detected"
    SPEECH_RECOGNIZED = "speech_recognized"
    TTS_START = "tts_start"
    TTS_COMPLETE = "tts_complete"
    
    # AI events
    AI_THINKING = "ai_thinking"
    AI_RESPONSE = "ai_response"
    AI_ERROR = "ai_error"
    
    # System events
    SYSTEM_COMMAND = "system_command"
    SYSTEM_RESPONSE = "system_response"
    ADMIN_REQUEST = "admin_request"
    
    # GUI events
    GUI_COMMAND = "gui_command"
    GUI_UPDATE = "gui_update"
    MUTE_TOGGLE = "mute_toggle"
    
    # File events
    FILE_DROPPED = "file_dropped"
    FILE_PROCESSED = "file_processed"
    
    # Memory events
    MEMORY_STORE = "memory_store"
    MEMORY_RECALL = "memory_recall"
    
    # Plugin events
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_ERROR = "plugin_error"
    
    # Application events
    APP_STARTUP = "app_startup"
    APP_SHUTDOWN = "app_shutdown"
    MODULE_STARTED = "module_started"
    MODULE_STOPPED = "module_stopped"
