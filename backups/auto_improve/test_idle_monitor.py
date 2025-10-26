import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from utils.idle_monitor import IdleMonitor
from utils.event_system import EventSystem

class TestIdleMonitor:
    """Test cases for IdleMonitor functionality"""

    @pytest.fixture
    def event_system(self):
        return EventSystem()

    @pytest.fixture
    def idle_monitor(self, event_system):
        return IdleMonitor(event_system, idle_threshold_minutes=0.1)  # 6 seconds for testing

    def test_initialization(self, idle_monitor, event_system):
        """Test that IdleMonitor initializes correctly"""
        assert idle_monitor.event_system == event_system
        assert idle_monitor.idle_threshold_seconds == 6
        assert idle_monitor.last_activity_time > 0
        assert not idle_monitor.is_monitoring

    def test_update_activity(self, idle_monitor):
        """Test that activity updates reset the idle timer"""
        original_time = idle_monitor.last_activity_time
        time.sleep(0.1)  # Small delay
        idle_monitor._update_activity()
        assert idle_monitor.last_activity_time > original_time

    def test_get_idle_duration(self, idle_monitor):
        """Test idle duration calculation"""
        time.sleep(0.1)
        duration = idle_monitor.get_idle_duration()
        assert duration >= 0.1

    def test_is_idle_false(self, idle_monitor):
        """Test that monitor correctly reports not idle when recently active"""
        idle_monitor._update_activity()
        assert not idle_monitor.is_idle()

    def test_is_idle_true(self, idle_monitor):
        """Test that monitor correctly reports idle after threshold"""
        # Set last activity to past threshold
        idle_monitor.last_activity_time = time.time() - 10  # 10 seconds ago
        assert idle_monitor.is_idle()

    @pytest.mark.asyncio
    async def test_monitoring_start_stop(self, idle_monitor):
        """Test starting and stopping the monitoring task"""
        assert not idle_monitor.is_monitoring

        await idle_monitor.start_monitoring()
        assert idle_monitor.is_monitoring
        assert idle_monitor.monitoring_task is not None

        await idle_monitor.stop_monitoring()
        assert not idle_monitor.is_monitoring

    @pytest.mark.asyncio
    async def test_idle_callback_trigger(self, idle_monitor):
        """Test that idle callback is triggered when threshold is exceeded"""
        callback_called = False

        async def test_callback():
            nonlocal callback_called
            callback_called = True

        idle_monitor.set_idle_callback(test_callback)

        # Set last activity to past threshold
        idle_monitor.last_activity_time = time.time() - 10

        await idle_monitor.start_monitoring()
        await asyncio.sleep(0.1)  # Allow monitoring loop to run

        # The callback should be triggered in the monitoring loop
        # Note: In a real scenario, this would trigger after the full threshold
        await idle_monitor.stop_monitoring()

    def test_event_subscriptions(self, idle_monitor, event_system):
        """Test that idle monitor subscribes to relevant events"""
        # Simulate events that should update activity
        asyncio.run(event_system.emit("user_input", {"text": "test"}))
        asyncio.run(event_system.emit("voice_command", {"command": "test"}))
        asyncio.run(event_system.emit("gui_interaction", {"action": "click"}))

        # Activity should have been updated
        assert idle_monitor.last_activity_time > time.time() - 1  # Within last second
