"""
Comprehensive tests for ActionLogger component
Tests all logging functionality, file operations, and error handling
"""
import pytest
import tempfile
import json
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
from pathlib import Path

# Import the ActionLogger
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from action_logger import ActionLogger, get_action_logger, init_action_logger


class TestActionLogger:
    """Test ActionLogger functionality"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file"""
        config_data = {
            "model": "llama3.2:1b",
            "voice_engine": "pyttsx3",
            "debug": True
        }
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(config_data, f)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def action_logger(self, temp_log_file, temp_config_file):
        """Create ActionLogger instance for testing"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(temp_log_file, temp_config_file)
            logger.logger = Mock()
            logger.actions = []
            return logger

    def test_init_action_logger(self, temp_log_file, temp_config_file):
        """Test ActionLogger initialization"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(temp_log_file, temp_config_file)
            
            assert logger.log_file == Path(temp_log_file)
            assert logger.config_file == Path(temp_config_file)
            assert hasattr(logger, 'session_id')
            assert hasattr(logger, 'lock')
            assert hasattr(logger, 'actions')

    def test_setup_logging(self, temp_log_file, temp_config_file):
        """Test logging setup"""
        with patch('logging.basicConfig') as mock_basic_config, \
             patch('logging.getLogger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            logger = ActionLogger(temp_log_file, temp_config_file)
            
            # Check if logging was configured
            mock_basic_config.assert_called_once()
            mock_get_logger.assert_called_once()

    def test_load_config_success(self, temp_config_file):
        """Test successful config loading"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(config_file=temp_config_file)
            
            # Config should be loaded
            assert logger.config is not None
            assert isinstance(logger.config, dict)

    def test_load_config_failure(self):
        """Test config loading failure"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(config_file="nonexistent.json")
            
            # Should return empty dict on failure
            assert logger.config == {}

    def test_log_action(self, action_logger):
        """Test basic action logging"""
        action_logger.save_action_log = Mock()
        
        action_logger.log_action("TEST_ACTION", "Test description", {"key": "value"})
        
        # Check if action was added to list
        assert len(action_logger.actions) == 1
        action = action_logger.actions[0]
        
        assert action["action_type"] == "TEST_ACTION"
        assert action["description"] == "Test description"
        assert action["details"]["key"] == "value"
        assert "timestamp" in action
        assert "session_id" in action
        
        # Check if logger was called
        action_logger.logger.info.assert_called_once()
        
        # Check if save was called
        action_logger.save_action_log.assert_called_once()

    def test_log_user_input(self, action_logger):
        """Test user input logging"""
        action_logger.save_action_log = Mock()
        
        input_text = "Hello, how are you?"
        action_logger.log_user_input(input_text, "voice")
        
        assert len(action_logger.actions) == 1
        action = action_logger.actions[0]
        
        assert action["action_type"] == "USER_INPUT"
        assert action["details"]["input_method"] == "voice"
        assert action["details"]["full_text"] == input_text
        assert action["details"]["text_length"] == len(input_text)

    def test_log_user_input_long_text(self, action_logger):
        """Test user input logging with long text"""
        action_logger.save_action_log = Mock()
        
        long_text = "A" * 200
        action_logger.log_user_input(long_text)
        
        action = action_logger.actions[0]
        # Description should be truncated but full text preserved
        assert "..." in action["description"]
        assert action["details"]["full_text"] == long_text

    def test_log_ai_response(self, action_logger):
        """Test AI response logging"""
        action_logger.save_action_log = Mock()
        
        response = "I understand your request."
        model = "llama3.2:1b"
        processing_time = 1.5
        
        action_logger.log_ai_response(response, model, processing_time)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "AI_RESPONSE"
        assert action["details"]["model"] == model
        assert action["details"]["full_response"] == response
        assert action["details"]["processing_time_seconds"] == processing_time

    def test_log_voice_activity_success(self, action_logger):
        """Test voice activity logging - success"""
        action_logger.save_action_log = Mock()
        
        details = {"engine": "pyttsx3", "duration": 2.5}
        action_logger.log_voice_activity("speak", True, details)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "VOICE_ACTIVITY"
        assert "SUCCESS" in action["description"]
        assert action["details"]["engine"] == "pyttsx3"

    def test_log_voice_activity_failure(self, action_logger):
        """Test voice activity logging - failure"""
        action_logger.save_action_log = Mock()
        
        action_logger.log_voice_activity("speak", False)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "VOICE_ACTIVITY"
        assert "FAILED" in action["description"]

    def test_log_system_status(self, action_logger):
        """Test system status logging"""
        action_logger.save_action_log = Mock()
        
        metrics = {"cpu": "45%", "memory": "2.1GB"}
        action_logger.log_system_status("cpu_monitor", "healthy", metrics)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "SYSTEM_STATUS"
        assert action["details"]["component"] == "cpu_monitor"
        assert action["details"]["status"] == "healthy"
        assert action["details"]["metrics"] == metrics

    def test_log_error(self, action_logger):
        """Test error logging"""
        action_logger.save_action_log = Mock()
        
        error_type = "ConnectionError"
        error_message = "Failed to connect to service"
        traceback_info = "Traceback details..."
        
        action_logger.log_error(error_type, error_message, traceback_info)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "ERROR"
        assert action["details"]["error_type"] == error_type
        assert action["details"]["error_message"] == error_message
        assert action["details"]["traceback"] == traceback_info

    def test_log_file_operation_success(self, action_logger):
        """Test file operation logging - success"""
        action_logger.save_action_log = Mock()
        
        action_logger.log_file_operation("create", "/path/to/file.txt", True)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "FILE_OPERATION"
        assert "SUCCESS" in action["description"]
        assert action["details"]["operation"] == "create"
        assert action["details"]["file_path"] == "/path/to/file.txt"
        assert action["details"]["success"] is True

    def test_log_file_operation_failure(self, action_logger):
        """Test file operation logging - failure"""
        action_logger.save_action_log = Mock()
        
        action_logger.log_file_operation("delete", "/path/to/file.txt", False)
        
        action = action_logger.actions[0]
        assert "FAILED" in action["description"]
        assert action["details"]["success"] is False

    def test_log_network_activity(self, action_logger):
        """Test network activity logging"""
        action_logger.save_action_log = Mock()
        
        action_logger.log_network_activity("GET", "https://api.example.com", 200)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "NETWORK_ACTIVITY"
        assert action["details"]["activity"] == "GET"
        assert action["details"]["url"] == "https://api.example.com"
        assert action["details"]["response_code"] == 200

    def test_log_gui_event(self, action_logger):
        """Test GUI event logging"""
        action_logger.save_action_log = Mock()
        
        details = {"button_id": "submit", "value": "test"}
        action_logger.log_gui_event("click", "main_window", details)
        
        action = action_logger.actions[0]
        assert action["action_type"] == "GUI_EVENT"
        assert action["details"]["event"] == "click"
        assert action["details"]["component"] == "main_window"
        assert action["details"]["details"]["button_id"] == "submit"

    def test_save_action_log_success(self, action_logger, temp_log_file):
        """Test successful action log saving"""
        # Add some actions
        action_logger.actions = [
            {
                "timestamp": datetime.now().isoformat(),
                "action_type": "TEST",
                "description": "Test action"
            }
        ]
        
        # Set action log file path
        action_logger.action_log_file = Path(temp_log_file.replace('.log', '_actions.json'))
        
        # Save should not raise exception
        action_logger.save_action_log()
        
        # Check if file was created
        assert action_logger.action_log_file.exists()

    def test_save_action_log_failure(self, action_logger):
        """Test action log saving failure"""
        # Set invalid path
        action_logger.action_log_file = Path("/invalid/path/actions.json")
        action_logger.actions = [{"test": "data"}]
        
        # Should not raise exception, just log error
        action_logger.save_action_log()
        
        # Logger should have been called with error
        action_logger.logger.error.assert_called()

    def test_get_session_summary(self, action_logger):
        """Test getting session summary"""
        # Add various actions
        action_logger.actions = [
            {
                "timestamp": datetime.now().isoformat(),
                "action_type": "USER_INPUT",
                "description": "Test input"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "action_type": "AI_RESPONSE",
                "description": "Test response"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "action_type": "USER_INPUT",
                "description": "Another input"
            }
        ]
        
        summary = action_logger.get_session_summary()
        
        assert summary["total_actions"] == 3
        assert summary["action_counts"]["USER_INPUT"] == 2
        assert summary["action_counts"]["AI_RESPONSE"] == 1
        assert "session_id" in summary
        assert "session_start" in summary

    def test_get_session_summary_empty(self, action_logger):
        """Test session summary with no actions"""
        action_logger.actions = []
        
        summary = action_logger.get_session_summary()
        
        assert summary["total_actions"] == 0
        assert summary["action_counts"] == {}
        assert summary["session_start"] is None

    def test_shutdown(self, action_logger, temp_log_file):
        """Test logger shutdown"""
        action_logger.save_action_log = Mock()
        action_logger.get_session_summary = Mock(return_value={"test": "summary"})
        
        # Mock the summary file path
        summary_file = Path(temp_log_file.replace('.log', '_summary.json'))
        action_logger.log_file = Path(temp_log_file)
        
        with patch('builtins.open', mock_open()) as mock_file:
            action_logger.shutdown()
        
        # Should log shutdown action
        assert len(action_logger.actions) == 1
        assert action_logger.actions[0]["action_type"] == "SYSTEM_SHUTDOWN"
        
        # Should save action log and summary
        action_logger.save_action_log.assert_called_once()
        action_logger.get_session_summary.assert_called_once()

    def test_shutdown_with_save_error(self, action_logger):
        """Test shutdown with summary save error"""
        action_logger.save_action_log = Mock()
        action_logger.get_session_summary = Mock(return_value={"test": "summary"})
        
        # Mock file operations to raise exception
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            action_logger.shutdown()
        
        # Should still complete shutdown process
        action_logger.logger.error.assert_called()

    def test_thread_safety(self, action_logger):
        """Test thread safety of logging operations"""
        import threading
        import time
        
        action_logger.save_action_log = Mock()
        results = []
        
        def log_actions(thread_id):
            for i in range(10):
                action_logger.log_action(f"THREAD_{thread_id}", f"Action {i}")
                time.sleep(0.001)  # Small delay to increase chance of race condition
            results.append(thread_id)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_actions, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have completed
        assert len(results) == 5
        # Should have logged 50 actions total (5 threads * 10 actions)
        assert len(action_logger.actions) == 50

    def test_global_logger_functions(self):
        """Test global logger functions"""
        # Test get_action_logger
        with patch('action_logger.ActionLogger') as mock_logger_class:
            mock_instance = Mock()
            mock_logger_class.return_value = mock_instance
            
            # First call should create new instance
            logger1 = get_action_logger()
            mock_logger_class.assert_called_once()
            
            # Second call should return same instance
            logger2 = get_action_logger()
            assert logger1 == logger2
            # Constructor should only be called once
            assert mock_logger_class.call_count == 1

    def test_init_action_logger_function(self):
        """Test init action logger function"""
        with patch('action_logger.ActionLogger') as mock_logger_class:
            mock_instance = Mock()
            mock_logger_class.return_value = mock_instance
            
            result = init_action_logger("test.log")
            
            mock_logger_class.assert_called_once_with("test.log")
            assert result == mock_instance

    def test_session_id_format(self, action_logger):
        """Test session ID format"""
        session_id = action_logger.session_id
        
        # Should be in format YYYYMMDD_HHMMSS
        assert len(session_id) == 15
        assert session_id[8] == '_'
        
        # Should be parseable as datetime
        datetime.strptime(session_id, "%Y%m%d_%H%M%S")

    def test_action_log_file_naming(self, action_logger, temp_log_file):
        """Test action log file naming convention"""
        action_logger.log_file = Path(temp_log_file)
        
        expected_name = f"actions_{action_logger.session_id}.json"
        expected_path = action_logger.log_file.parent / expected_name
        
        assert action_logger.action_log_file == expected_path

    def test_config_context_in_logging(self, temp_config_file):
        """Test that config context is available for logging"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(config_file=temp_config_file)
            
            # Config should be loaded and available
            assert logger.config is not None
            assert "model" in logger.config
            assert logger.config["model"] == "llama3.2:1b"

    def test_large_action_log_performance(self, action_logger):
        """Test performance with large number of actions"""
        import time
        
        action_logger.save_action_log = Mock()
        
        # Log many actions quickly
        start_time = time.time()
        for i in range(1000):
            action_logger.log_action("PERF_TEST", f"Action {i}")
        end_time = time.time()
        
        # Should complete reasonably quickly (less than 1 second)
        execution_time = end_time - start_time
        assert execution_time < 1.0
        
        # All actions should be logged
        assert len(action_logger.actions) == 1000

    def test_memory_usage_with_many_actions(self, action_logger):
        """Test memory usage doesn't grow excessively"""
        import sys
        
        action_logger.save_action_log = Mock()
        
        # Get initial memory usage
        initial_size = sys.getsizeof(action_logger.actions)
        
        # Add many actions
        for i in range(100):
            action_logger.log_action("MEMORY_TEST", f"Action {i}", {"data": "x" * 100})
        
        # Memory should grow proportionally, not excessively
        final_size = sys.getsizeof(action_logger.actions)
        growth_ratio = final_size / initial_size
        
        # Should be reasonable growth (less than 1000x)
        assert growth_ratio < 1000


class TestActionLoggerIntegration:
    """Integration tests for ActionLogger"""
    
    def test_full_logging_workflow(self, temp_log_file, temp_config_file):
        """Test complete logging workflow"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(temp_log_file, temp_config_file)
            logger.logger = Mock()
            
            # Simulate a complete user interaction
            logger.log_user_input("Hello, create a file for me")
            logger.log_ai_response("I'll create a file for you", "llama3.2:1b", 1.2)
            logger.log_file_operation("create", "test_file.txt", True)
            logger.log_system_status("file_system", "healthy")
            
            # Get summary
            summary = logger.get_session_summary()
            
            assert summary["total_actions"] == 4
            assert "USER_INPUT" in summary["action_counts"]
            assert "AI_RESPONSE" in summary["action_counts"]
            assert "FILE_OPERATION" in summary["action_counts"]
            assert "SYSTEM_STATUS" in summary["action_counts"]

    def test_error_recovery_workflow(self, temp_log_file, temp_config_file):
        """Test error handling and recovery workflow"""
        with patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger(temp_log_file, temp_config_file)
            logger.logger = Mock()
            
            # Simulate error scenario
            logger.log_user_input("Delete important file")
            logger.log_error("PermissionError", "Access denied to file", "Traceback...")
            logger.log_system_status("error_handler", "recovering")
            logger.log_ai_response("I couldn't delete the file due to permissions", "llama3.2:1b")
            
            # Check error was properly logged
            error_actions = [a for a in logger.actions if a["action_type"] == "ERROR"]
            assert len(error_actions) == 1
            assert "PermissionError" in error_actions[0]["details"]["error_type"]
