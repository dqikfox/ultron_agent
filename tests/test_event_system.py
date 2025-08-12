"""
Comprehensive tests for Event System
"""
import pytest
import threading
import time
from unittest.mock import Mock, patch
from utils.event_system import EventSystem


class TestEventSystem:
    """Test suite for EventSystem"""

    def test_event_system_initialization(self):
        """Test event system initialization"""
        event_system = EventSystem()
        assert event_system._subscribers == {}
        assert event_system._event_history == []

    def test_subscribe_single_callback(self):
        """Test subscribing a single callback to an event"""
        event_system = EventSystem()
        callback = Mock()
        
        event_system.subscribe("test_event", callback)
        
        assert "test_event" in event_system._subscribers
        assert callback in event_system._subscribers["test_event"]

    def test_subscribe_multiple_callbacks(self):
        """Test subscribing multiple callbacks to same event"""
        event_system = EventSystem()
        callback1 = Mock()
        callback2 = Mock()
        
        event_system.subscribe("test_event", callback1)
        event_system.subscribe("test_event", callback2)
        
        assert len(event_system._subscribers["test_event"]) == 2
        assert callback1 in event_system._subscribers["test_event"]
        assert callback2 in event_system._subscribers["test_event"]

    def test_emit_event_with_subscribers(self):
        """Test emitting event with registered subscribers"""
        event_system = EventSystem()
        callback = Mock()
        
        event_system.subscribe("test_event", callback)
        event_system.emit("test_event", {"data": "test"})
        
        callback.assert_called_once_with({"data": "test"})

    def test_emit_event_without_subscribers(self):
        """Test emitting event without any subscribers"""
        event_system = EventSystem()
        
        # Should not raise any exception
        event_system.emit("nonexistent_event", {"data": "test"})

    def test_emit_event_multiple_subscribers(self):
        """Test emitting event to multiple subscribers"""
        event_system = EventSystem()
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()
        
        event_system.subscribe("test_event", callback1)
        event_system.subscribe("test_event", callback2)
        event_system.subscribe("other_event", callback3)
        
        event_system.emit("test_event", {"data": "test"})
        
        callback1.assert_called_once_with({"data": "test"})
        callback2.assert_called_once_with({"data": "test"})
        callback3.assert_not_called()

    def test_emit_event_with_none_data(self):
        """Test emitting event with None data"""
        event_system = EventSystem()
        callback = Mock()
        
        event_system.subscribe("test_event", callback)
        event_system.emit("test_event", None)
        
        callback.assert_called_once_with(None)

    def test_emit_event_callback_exception(self):
        """Test handling callback exceptions during emit"""
        event_system = EventSystem()
        failing_callback = Mock(side_effect=Exception("Callback failed"))
        working_callback = Mock()
        
        event_system.subscribe("test_event", failing_callback)
        event_system.subscribe("test_event", working_callback)
        
        # Should not raise exception and should call working callback
        event_system.emit("test_event", {"data": "test"})
        
        failing_callback.assert_called_once()
        working_callback.assert_called_once()

    def test_event_history_tracking(self):
        """Test event history tracking"""
        event_system = EventSystem()
        
        event_system.emit("event1", {"data": "first"})
        event_system.emit("event2", {"data": "second"})
        
        assert len(event_system._event_history) == 2
        assert event_system._event_history[0]["event_name"] == "event1"
        assert event_system._event_history[1]["event_name"] == "event2"

    def test_get_recent_events_default(self):
        """Test getting recent events with default limit"""
        event_system = EventSystem()
        
        # Emit more than default limit
        for i in range(150):
            event_system.emit(f"event_{i}", {"index": i})
        
        recent = event_system.get_recent_events()
        assert len(recent) == 100  # Default limit

    def test_get_recent_events_custom_limit(self):
        """Test getting recent events with custom limit"""
        event_system = EventSystem()
        
        for i in range(50):
            event_system.emit(f"event_{i}", {"index": i})
        
        recent = event_system.get_recent_events(limit=10)
        assert len(recent) == 10

    def test_get_recent_events_less_than_limit(self):
        """Test getting recent events when fewer than limit exist"""
        event_system = EventSystem()
        
        event_system.emit("event1", {"data": "test"})
        event_system.emit("event2", {"data": "test"})
        
        recent = event_system.get_recent_events(limit=10)
        assert len(recent) == 2

    def test_clear_history(self):
        """Test clearing event history"""
        event_system = EventSystem()
        
        event_system.emit("event1", {"data": "test"})
        event_system.emit("event2", {"data": "test"})
        
        assert len(event_system._event_history) == 2
        
        event_system.clear_history()
        
        assert len(event_system._event_history) == 0

    def test_unsubscribe(self):
        """Test unsubscribing from events"""
        event_system = EventSystem()
        callback1 = Mock()
        callback2 = Mock()
        
        event_system.subscribe("test_event", callback1)
        event_system.subscribe("test_event", callback2)
        
        # Unsubscribe one callback
        unsubscribe_func = event_system.unsubscribe("test_event", callback1)
        
        # Should be callable function
        assert callable(unsubscribe_func)
        
        # Call unsubscribe
        unsubscribe_func()
        
        # Emit event - only callback2 should be called
        event_system.emit("test_event", {"data": "test"})
        
        callback1.assert_not_called()
        callback2.assert_called_once()

    def test_unsubscribe_nonexistent_event(self):
        """Test unsubscribing from nonexistent event"""
        event_system = EventSystem()
        callback = Mock()
        
        # Should not raise exception
        unsubscribe_func = event_system.unsubscribe("nonexistent_event", callback)
        assert callable(unsubscribe_func)

    def test_unsubscribe_nonexistent_callback(self):
        """Test unsubscribing nonexistent callback"""
        event_system = EventSystem()
        callback1 = Mock()
        callback2 = Mock()
        
        event_system.subscribe("test_event", callback1)
        
        # Try to unsubscribe callback that wasn't subscribed
        unsubscribe_func = event_system.unsubscribe("test_event", callback2)
        unsubscribe_func()  # Should not raise exception

    def test_thread_safety_emit(self):
        """Test thread safety of emit operations"""
        event_system = EventSystem()
        results = []
        
        def callback(data):
            results.append(data["value"])
        
        event_system.subscribe("test_event", callback)
        
        def emit_events(start_value):
            for i in range(10):
                event_system.emit("test_event", {"value": start_value + i})
        
        # Start multiple threads emitting events
        threads = []
        for i in range(5):
            thread = threading.Thread(target=emit_events, args=(i * 10,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have received all events
        assert len(results) == 50

    def test_thread_safety_subscribe(self):
        """Test thread safety of subscribe operations"""
        event_system = EventSystem()
        callbacks = []
        
        def create_and_subscribe():
            callback = Mock()
            callbacks.append(callback)
            event_system.subscribe("test_event", callback)
        
        # Start multiple threads subscribing
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_and_subscribe)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All callbacks should be subscribed
        assert len(event_system._subscribers["test_event"]) == 10
        
        # Emit event - all callbacks should be called
        event_system.emit("test_event", {"data": "test"})
        
        for callback in callbacks:
            callback.assert_called_once()

    def test_event_data_types(self):
        """Test various data types in events"""
        event_system = EventSystem()
        callback = Mock()
        
        event_system.subscribe("test_event", callback)
        
        # Test different data types
        test_data = [
            {"dict": "value"},
            ["list", "data"],
            "string_data",
            123,
            3.14,
            True,
            None
        ]
        
        for data in test_data:
            event_system.emit("test_event", data)
        
        assert callback.call_count == len(test_data)

    def test_complex_event_scenarios(self):
        """Test complex event emission scenarios"""
        event_system = EventSystem()
        
        # Setup multiple events with multiple subscribers
        results = {"event1": [], "event2": [], "event3": []}
        
        def callback_event1(data):
            results["event1"].append(data)
        
        def callback_event2(data):
            results["event2"].append(data)
        
        def callback_event3(data):
            results["event3"].append(data)
        
        def callback_all_events(data):
            for key in results:
                results[key].append(f"all_events: {data}")
        
        # Subscribe to different events
        event_system.subscribe("event1", callback_event1)
        event_system.subscribe("event2", callback_event2)
        event_system.subscribe("event3", callback_event3)
        
        # Subscribe to all events
        event_system.subscribe("event1", callback_all_events)
        event_system.subscribe("event2", callback_all_events)
        event_system.subscribe("event3", callback_all_events)
        
        # Emit events
        event_system.emit("event1", "data1")
        event_system.emit("event2", "data2")
        event_system.emit("event3", "data3")
        
        # Verify results
        assert len(results["event1"]) == 2  # specific + all_events callback
        assert len(results["event2"]) == 2
        assert len(results["event3"]) == 2
        
        assert "data1" in results["event1"]
        assert "all_events: data2" in results["event2"]

    def test_event_system_performance(self):
        """Test event system performance"""
        event_system = EventSystem()
        callback = Mock()
        
        event_system.subscribe("test_event", callback)
        
        # Time large number of events
        start_time = time.time()
        
        for i in range(1000):
            event_system.emit("test_event", {"index": i})
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should handle 1000 events quickly
        assert execution_time < 1.0  # Less than 1 second
        assert callback.call_count == 1000

    def test_event_history_structure(self):
        """Test event history data structure"""
        event_system = EventSystem()
        
        event_system.emit("test_event", {"key": "value"})
        
        history = event_system.get_recent_events(limit=1)
        event_record = history[0]
        
        # Verify history record structure
        assert "event_name" in event_record
        assert "data" in event_record
        assert "timestamp" in event_record
        
        assert event_record["event_name"] == "test_event"
        assert event_record["data"]["key"] == "value"
        
        # Timestamp should be recent
        import datetime
        timestamp = datetime.datetime.fromisoformat(event_record["timestamp"])
        now = datetime.datetime.now()
        time_diff = (now - timestamp).total_seconds()
        assert time_diff < 1.0  # Should be very recent
