import asyncio
import time
from typing import Optional, Callable
from utils.ultron_logger import log_info, log_error
from utils.event_system import EventSystem

class IdleMonitor:
    """
    Monitors user inactivity and triggers auto-analysis when idle threshold is exceeded.
    Integrates with ULTRON's event system to track user interactions.
    """

    def __init__(self, event_system: EventSystem, idle_threshold_minutes: int = 5):
        self.event_system = event_system
        self.idle_threshold_seconds = idle_threshold_minutes * 60
        self.last_activity_time = time.time()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        self.on_idle_callback: Optional[Callable] = None

        # Subscribe to user activity events (async)
        asyncio.create_task(self.event_system.subscribe("user_input", self._update_activity))
        asyncio.create_task(self.event_system.subscribe("voice_command", self._update_activity))
        asyncio.create_task(self.event_system.subscribe("gui_interaction", self._update_activity))
        asyncio.create_task(self.event_system.subscribe("command_executed", self._update_activity))

        log_info("idle_monitor", f"IdleMonitor initialized with threshold: {idle_threshold_minutes} minutes")

    def _update_activity(self, data=None):
        """Update the last activity timestamp when user interacts."""
        self.last_activity_time = time.time()
        log_info("idle_monitor", "User activity detected", last_activity=self.last_activity_time)

    def set_idle_callback(self, callback: Callable):
        """Set the callback to trigger when idle threshold is exceeded."""
        self.on_idle_callback = callback

    async def start_monitoring(self):
        """Start the idle monitoring background task."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_idle())
        log_info("idle_monitor", "Idle monitoring started")

    async def stop_monitoring(self):
        """Stop the idle monitoring task."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        log_info("idle_monitor", "Idle monitoring stopped")

    async def _monitor_idle(self):
        """Background task that checks for idle periods."""
        while self.is_monitoring:
            try:
                current_time = time.time()
                idle_duration = current_time - self.last_activity_time

                if idle_duration >= self.idle_threshold_seconds:
                    log_info("idle_monitor", "Idle threshold exceeded", idle_duration_seconds=idle_duration)
                    if self.on_idle_callback:
                        await self.on_idle_callback()
                    # Reset to prevent continuous triggering
                    self.last_activity_time = current_time

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                log_error("idle_monitor", f"Error in idle monitoring: {str(e)}")
                await asyncio.sleep(30)

    def get_idle_duration(self) -> float:
        """Get the current idle duration in seconds."""
        return time.time() - self.last_activity_time

    def is_idle(self) -> bool:
        """Check if currently idle."""
        return self.get_idle_duration() >= self.idle_threshold_seconds
