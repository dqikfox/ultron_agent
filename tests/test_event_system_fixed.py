"""
Comprehensive tests for EventSystem component
Tests event emission, subscription, history tracking, and async handling
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import logging

# Import the EventSystem
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils'))
from event_system import EventSystem


class TestEventSystem:
    """Test EventSystem functionality"""
    
    @pytest.fixture
    def event_system(self):
        """Create EventSystem instance for testing"""
        return EventSystem()

    def test_init_event_system(self, event_system):
        """Test EventSystem initialization"""
        assert event_system.subscribers == {}
        assert event_system.event_history == []
        assert event_system.max_history == 1000

    @pytest.mark.asyncio
    async def test_emit_event_basic(self, event_system):
        """Test basic event emission"""
        await event_system.emit("test_event", {"data": "value"})
        
        assert len(event_system.event_history) == 1
        event = event_system.event_history[0]
        
        assert event["event"] == "test_event"
        assert event["data"]["data"] == "value"
        assert "timestamp" in event

    @pytest.mark.asyncio
    async def test_emit_event_no_data(self, event_system):
        """Test event emission without data"""
        await event_system.emit("simple_event")
        
        assert len(event_system.event_history) == 1
        event = event_system.event_history[0]
        
        assert event["event"] == "simple_event"
        assert event["data"] is None

    @pytest.mark.asyncio
    async def test_emit_event_with_subscribers(self, event_system):
        """Test event emission with subscribers"""
        callback_called = []
        
        def sync_callback(data):
            callback_called.append(("sync", data))
        
        async def async_callback(data):
            callback_called.append(("async", data))
        
        # Subscribe callbacks
        event_system.subscribe("test_event", sync_callback)
        event_system.subscribe("test_event", async_callback)
        
        # Emit event
        await event_system.emit("test_event", {"test": "data"})
        
        # Both callbacks should be called
        assert len(callback_called) == 2
        assert ("sync", {"test": "data"}) in callback_called
        assert ("async", {"test": "data"}) in callback_called

    def test_subscribe_event(self, event_system):
        """Test event subscription"""
        def callback(data):
            pass
        
        unsubscribe = event_system.subscribe("test_event", callback)
        
        assert "test_event" in event_system.subscribers
        assert callback in event_system.subscribers["test_event"]
        assert callable(unsubscribe)

    def test_subscribe_multiple_callbacks(self, event_system):
        """Test subscribing multiple callbacks to same event"""
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        event_system.subscribe("test_event", callback1)
        event_system.subscribe("test_event", callback2)
        
        assert len(event_system.subscribers["test_event"]) == 2
        assert callback1 in event_system.subscribers["test_event"]
        assert callback2 in event_system.subscribers["test_event"]

    def test_unsubscribe_event(self, event_system):
        """Test event unsubscription"""
        def callback(data):
            pass
        
        unsubscribe = event_system.subscribe("test_event", callback)
        assert callback in event_system.subscribers["test_event"]
        
        # Unsubscribe
        unsubscribe()
        assert callback not in event_system.subscribers["test_event"]

    def test_unsubscribe_nonexistent_callback(self, event_system):
        """Test unsubscribing nonexistent callback"""
        def callback(data):
            pass
        
        unsubscribe = event_system.subscribe("test_event", callback)
        
        # Remove callback manually
        event_system.subscribers["test_event"].remove(callback)
        
        # Unsubscribe should not raise error
        unsubscribe()  # Should not raise exception

    def test_unsubscribe_nonexistent_event(self, event_system):
        """Test unsubscribing from nonexistent event"""
        def callback(data):
            pass
        
        unsubscribe = event_system.subscribe("test_event", callback)
        
        # Remove event manually
        del event_system.subscribers["test_event"]
        
        # Unsubscribe should not raise error
        unsubscribe()  # Should not raise exception

    @pytest.mark.asyncio
    async def test_event_history_tracking(self, event_system):
        """Test event history tracking"""
        await event_system.emit("event1", {"data": 1})
        await event_system.emit("event2", {"data": 2})
        await event_system.emit("event3", {"data": 3})
        
        assert len(event_system.event_history) == 3
        
        # Check order (newest first)
        assert event_system.event_history[0]["event"] == "event1"
        assert event_system.event_history[1]["event"] == "event2"
        assert event_system.event_history[2]["event"] == "event3"

    @pytest.mark.asyncio
    async def test_event_history_limit(self, event_system):
        """Test event history size limit"""
        event_system.max_history = 5
        
        # Emit more events than max_history
        for i in range(10):
            await event_system.emit(f"event_{i}", {"data": i})
        
        # Should only keep last 5 events
        assert len(event_system.event_history) == 5
        
        # Should be the last 5 events
        for i, event in enumerate(event_system.event_history):
            expected_event_name = f"event_{i + 5}"
            assert event["event"] == expected_event_name

    def test_get_recent_events_default(self, event_system):
        """Test getting recent events with default limit"""
        # Add some events to history
        for i in range(10):
            event_system.event_history.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"event_{i}",
                "data": {"index": i}
            })
        
        recent = event_system.get_recent_events()
        
        # Should return all events (default limit 100)
        assert len(recent) == 10

    def test_get_recent_events_with_limit(self, event_system):
        """Test getting recent events with custom limit"""
        # Add some events to history
        for i in range(10):
            event_system.event_history.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"event_{i}",
                "data": {"index": i}
            })
        
        recent = event_system.get_recent_events(limit=5)
        
        # Should return last 5 events
        assert len(recent) == 5
        # Should be the most recent ones
        for i, event in enumerate(recent):
            expected_index = i + 5
            assert event["data"]["index"] == expected_index

    def test_get_recent_events_empty(self, event_system):
        """Test getting recent events when history is empty"""
        recent = event_system.get_recent_events()
        assert recent == []

    def test_clear_history(self, event_system):
        """Test clearing event history"""
        # Add some events
        for i in range(5):
            event_system.event_history.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"event_{i}",
                "data": {"index": i}
            })
        
        assert len(event_system.event_history) == 5
        
        event_system.clear_history()
        
        assert len(event_system.event_history) == 0

    @pytest.mark.asyncio
    async def test_callback_exception_handling(self, event_system):
        """Test handling of exceptions in callbacks"""
        def failing_callback(data):
            raise ValueError("Test error")
        
        def working_callback(data):
            working_callback.called = True
        
        working_callback.called = False
        
        event_system.subscribe("test_event", failing_callback)
        event_system.subscribe("test_event", working_callback)
        
        with patch('logging.error') as mock_error:
            await event_system.emit("test_event", {"test": "data"})
        
        # Error should be logged
        mock_error.assert_called()
        
        # Working callback should still be called
        assert working_callback.called

    @pytest.mark.asyncio
    async def test_async_callback_exception_handling(self, event_system):
        """Test handling of exceptions in async callbacks"""
        async def failing_async_callback(data):
            raise ValueError("Async test error")
        
        async def working_async_callback(data):
            working_async_callback.called = True
        
        working_async_callback.called = False
        
        event_system.subscribe("test_event", failing_async_callback)
        event_system.subscribe("test_event", working_async_callback)
        
        with patch('logging.error') as mock_error:
            await event_system.emit("test_event", {"test": "data"})
        
        # Error should be logged
        mock_error.assert_called()
        
        # Working callback should still be called
        assert working_async_callback.called

    @pytest.mark.asyncio
    async def test_emit_exception_handling(self, event_system):
        """Test handling of exceptions during emit"""
        with patch.object(event_system, 'event_history', side_effect=Exception("History error")):
            with patch('logging.error') as mock_error:
                await event_system.emit("test_event", {"test": "data"})
        
        # Error should be logged
        mock_error.assert_called()

    @pytest.mark.asyncio
    async def test_mixed_sync_async_callbacks(self, event_system):
        """Test mixing synchronous and asynchronous callbacks"""
        results = []
        
        def sync_callback(data):
            results.append("sync")
        
        async def async_callback(data):
            results.append("async")
        
        event_system.subscribe("mixed_event", sync_callback)
        event_system.subscribe("mixed_event", async_callback)
        
        await event_system.emit("mixed_event", {"test": "data"})
        
        assert "sync" in results
        assert "async" in results
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_event_data_preservation(self, event_system):
        """Test that event data is preserved correctly"""
        complex_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        received_data = []
        
        def callback(data):
            received_data.append(data)
        
        event_system.subscribe("data_test", callback)
        await event_system.emit("data_test", complex_data)
        
        assert len(received_data) == 1
        assert received_data[0] == complex_data
        
        # Check history also preserves data
        history_event = event_system.event_history[0]
        assert history_event["data"] == complex_data

    @pytest.mark.asyncio
    async def test_event_timestamp_format(self, event_system):
        """Test event timestamp format"""
        await event_system.emit("timestamp_test")
        
        event = event_system.event_history[0]
        timestamp = event["timestamp"]
        
        # Should be valid ISO format
        datetime.fromisoformat(timestamp)

    @pytest.mark.asyncio
    async def test_multiple_events_ordering(self, event_system):
        """Test that multiple events maintain proper ordering"""
        import time
        
        await event_system.emit("first_event")
        time.sleep(0.001)  # Small delay to ensure different timestamps
        await event_system.emit("second_event")
        time.sleep(0.001)
        await event_system.emit("third_event")
        
        assert len(event_system.event_history) == 3
        assert event_system.event_history[0]["event"] == "first_event"
        assert event_system.event_history[1]["event"] == "second_event"
        assert event_system.event_history[2]["event"] == "third_event"
        
        # Timestamps should be in order
        timestamps = [datetime.fromisoformat(e["timestamp"]) for e in event_system.event_history]
        assert timestamps[0] <= timestamps[1] <= timestamps[2]

    def test_subscribe_same_callback_multiple_times(self, event_system):
        """Test subscribing the same callback multiple times"""
        def callback(data):
            callback.call_count += 1
        
        callback.call_count = 0
        
        # Subscribe same callback multiple times
        event_system.subscribe("test_event", callback)
        event_system.subscribe("test_event", callback)
        
        # Should appear twice in subscribers list
        assert len(event_system.subscribers["test_event"]) == 2

    @pytest.mark.asyncio
    async def test_performance_many_events(self, event_system):
        """Test performance with many events"""
        import time
        
        start_time = time.time()
        
        # Emit many events quickly
        for i in range(100):
            await event_system.emit(f"perf_event_{i}", {"index": i})
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete reasonably quickly (less than 1 second)
        assert execution_time < 1.0
        
        # All events should be recorded
        assert len(event_system.event_history) == 100

    @pytest.mark.asyncio
    async def test_performance_many_subscribers(self, event_system):
        """Test performance with many subscribers"""
        import time
        
        # Create many subscribers
        callbacks = []
        for i in range(100):
            def make_callback(index):
                def callback(data):
                    callback.called = True
                return callback
            
            cb = make_callback(i)
            cb.called = False
            callbacks.append(cb)
            event_system.subscribe("mass_event", cb)
        
        start_time = time.time()
        await event_system.emit("mass_event", {"test": "data"})
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete reasonably quickly
        assert execution_time < 1.0
        
        # All callbacks should be called
        for cb in callbacks:
            assert cb.called


class TestEventSystemIntegration:
    """Integration tests for EventSystem"""
    
    @pytest.mark.asyncio
    async def test_event_chain_workflow(self):
        """Test chaining events through multiple components"""
        event_system = EventSystem()
        workflow_steps = []
        
        async def step1_handler(data):
            workflow_steps.append("step1")
            await event_system.emit("step2", {"from": "step1", "data": data})
        
        async def step2_handler(data):
            workflow_steps.append("step2")
            await event_system.emit("step3", {"from": "step2", "data": data})
        
        def step3_handler(data):
            workflow_steps.append("step3")
        
        # Subscribe handlers
        event_system.subscribe("step1", step1_handler)
        event_system.subscribe("step2", step2_handler)
        event_system.subscribe("step3", step3_handler)
        
        # Start workflow
        await event_system.emit("step1", {"initial": "data"})
        
        # All steps should have executed
        assert workflow_steps == ["step1", "step2", "step3"]
        
        # Should have 3 events in history
        assert len(event_system.event_history) == 3

    @pytest.mark.asyncio
    async def test_real_world_simulation(self):
        """Simulate real-world usage scenario"""
        event_system = EventSystem()
        system_state = {
            "user_inputs": 0,
            "ai_responses": 0,
            "errors": 0,
            "system_status": "ok"
        }
        
        # System monitoring handlers
        def track_user_input(data):
            system_state["user_inputs"] += 1
        
        def track_ai_response(data):
            system_state["ai_responses"] += 1
        
        def track_error(data):
            system_state["errors"] += 1
            system_state["system_status"] = "error"
        
        def track_recovery(data):
            system_state["system_status"] = "ok"
        
        # Subscribe handlers
        event_system.subscribe("user_input", track_user_input)
        event_system.subscribe("ai_response", track_ai_response)
        event_system.subscribe("error", track_error)
        event_system.subscribe("recovery", track_recovery)
        
        # Simulate user interaction
        await event_system.emit("user_input", {"text": "Hello"})
        await event_system.emit("ai_response", {"text": "Hi there!"})
        await event_system.emit("user_input", {"text": "How are you?"})
        await event_system.emit("ai_response", {"text": "I'm doing well!"})
        
        # Simulate error and recovery
        await event_system.emit("error", {"type": "ConnectionError"})
        await event_system.emit("recovery", {"message": "Connection restored"})
        
        # Check final state
        assert system_state["user_inputs"] == 2
        assert system_state["ai_responses"] == 2
        assert system_state["errors"] == 1
        assert system_state["system_status"] == "ok"
        
        # Check event history
        assert len(event_system.event_history) == 6
        event_types = [e["event"] for e in event_system.event_history]
        assert "user_input" in event_types
        assert "ai_response" in event_types
        assert "error" in event_types
        assert "recovery" in event_types
