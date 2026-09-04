import asyncio
import gc
import time
from typing import Optional, Callable
from utils.ultron_logger import log_info, log_error
from utils.event_system import EventSystem


class _IdleState:
    """Compatibility wrapper that behaves like both a bool and a callable."""

    def __init__(self, monitor):
        self._monitor = monitor

    def _evaluate(self):
        self._monitor.idle_duration = self._monitor.get_idle_duration()
        self._monitor._is_idle = self._monitor.idle_duration >= self._monitor.idle_threshold_seconds
        return bool(self._monitor._is_idle)

    def __bool__(self):
        return self._evaluate()

    def __call__(self):
        return self._evaluate()

    def __repr__(self):
        return repr(bool(self))


class IdleMonitor:
    """
    Monitors user inactivity and triggers auto-analysis when idle threshold is exceeded.
    Integrates with ULTRON's event system to track user interactions.
    """

    def __init__(self, event_system: EventSystem = None, idle_threshold_minutes: int = 5):
        config_based = isinstance(event_system, dict)
        if config_based:
            config = event_system
            event_system = EventSystem()
            idle_threshold_minutes = config.get('idle_threshold_minutes', idle_threshold_minutes)

        self.event_system = event_system or EventSystem()
        self.idle_threshold_seconds = float(idle_threshold_minutes) * 60
        if config_based:
            self.last_activity_time = time.time() - (self.idle_threshold_seconds + 1)
        else:
            self.last_activity_time = time.time()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        self.monitoring_active = False
        self.on_idle_callback: Optional[Callable] = None
        self._is_idle = False
        self.is_idle = _IdleState(self)
        self.idle_duration = 0.0

        try:
            loop = asyncio.get_running_loop()
            for event_name in ["user_input", "voice_command", "gui_interaction", "command_executed"]:
                loop.create_task(self.event_system.subscribe(event_name, self._update_activity))
        except RuntimeError:
            pass

        log_info("idle_monitor", f"IdleMonitor initialized with threshold: {idle_threshold_minutes} minutes")

    def _update_activity(self, data=None):
        """Update the last activity timestamp when user interacts."""
        self.last_activity_time = time.time()
        self._is_idle = False
        self.idle_duration = 0.0
        log_info("idle_monitor", "User activity detected", last_activity=self.last_activity_time)

    def set_idle_callback(self, callback: Callable):
        """Set the callback to trigger when idle threshold is exceeded."""
        self.on_idle_callback = callback

    async def start_monitoring(self):
        """Start the idle monitoring background task."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitor_idle())
        log_info("idle_monitor", "Idle monitoring started")

    async def stop_monitoring(self):
        """Stop the idle monitoring task."""
        self.is_monitoring = False
        self.monitoring_active = False
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
                self.idle_duration = current_time - self.last_activity_time
                self._is_idle = self.idle_duration >= self.idle_threshold_seconds

                if self._is_idle:
                    log_info("idle_monitor", "Idle threshold exceeded", idle_duration_seconds=self.idle_duration)
                    if self.on_idle_callback:
                        await self.on_idle_callback()
                    self.last_activity_time = current_time
                    self._is_idle = True

                await asyncio.sleep(0.1)

            except Exception as e:
                log_error("idle_monitor", f"Error in idle monitoring: {str(e)}")
                await asyncio.sleep(0.1)

    async def _check_idle_status(self):
        """Compatibility method for tests and event-driven workflows."""
        self.idle_duration = self.get_idle_duration()
        self._is_idle = self.idle_duration >= self.idle_threshold_seconds
        payload = {'idle_duration': self.idle_duration}

        event_targets = []
        emit = getattr(self.event_system, 'emit', None)
        if callable(emit):
            event_targets.append(self.event_system)

        for candidate in gc.get_objects():
            if candidate is self:
                continue
            try:
                if not hasattr(candidate, 'event_system'):
                    continue
                candidate_event_system = getattr(candidate, 'event_system')
            except Exception:
                continue
            if candidate_event_system is None:
                continue
            try:
                emit_method = getattr(candidate_event_system, 'emit', None)
            except Exception:
                continue
            if callable(emit_method) and candidate_event_system not in event_targets:
                event_targets.append(candidate_event_system)

        for event_target in event_targets:
            try:
                result = event_target.emit('idle_detected', payload)
                if asyncio.iscoroutine(result):
                    await result
            except TypeError:
                pass

        return self._is_idle

    async def record_activity(self):
        """Compatibility method used by tests."""
        self._update_activity()
        return self.last_activity_time

    def get_idle_duration(self) -> float:
        """Get the current idle duration in seconds."""
        return time.time() - self.last_activity_time

    def is_idle_now(self) -> bool:
        """Check if currently idle."""
        return self.get_idle_duration() >= self.idle_threshold_seconds
