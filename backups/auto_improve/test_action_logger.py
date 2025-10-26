"""
Comprehensive tests for Action Logger
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from action_logger import ActionLogger


class TestActionLogger:
    """Test suite for ActionLogger"""

    def test_action_logger_initialization_default(self):
        """Test action logger initialization with default parameters"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            assert logger.log_file == "ultron_actions.log"
            assert logger.config_file == "ultron_config.json"

    def test_action_logger_initialization_custom(self):
        """Test action logger initialization with custom parameters"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger("custom.log", "custom_config.json")
            assert logger.log_file == "custom.log"
            assert logger.config_file == "custom_config.json"

    def test_load_config_file_exists(self):
        """Test loading config when file exists"""
        test_config = {"test_key": "test_value"}
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_config))), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            assert logger.config == test_config

    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist"""
        with patch('os.path.exists', return_value=False), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            assert logger.config == {}

    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='invalid json')), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            assert logger.config == {}

    @patch('logging.basicConfig')
    @patch('logging.getLogger')
    def test_setup_logging(self, mock_get_logger, mock_basic_config):
        """Test logging setup"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        with patch('action_logger.ActionLogger.load_config'):
            logger = ActionLogger()
            
        mock_basic_config.assert_called_once()
        mock_get_logger.assert_called_once()

    def test_log_action_basic(self):
        """Test basic action logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_action("test_action", "test description")
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "test_action" in call_args
            assert "test description" in call_args

    def test_log_action_with_details(self):
        """Test action logging with details"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            details = {"param1": "value1", "param2": "value2"}
            logger.log_action("test_action", "test description", details)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "test_action" in call_args
            assert "param1" in call_args

    def test_log_user_input(self):
        """Test user input logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_user_input("test input", "voice")
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "USER_INPUT" in call_args
            assert "test input" in call_args
            assert "voice" in call_args

    def test_log_ai_response(self):
        """Test AI response logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_ai_response("AI response", "gpt-4", 1.5)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "AI_RESPONSE" in call_args
            assert "AI response" in call_args
            assert "gpt-4" in call_args
            assert "1.5" in call_args

    def test_log_error(self):
        """Test error logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_error("connection_error", "Failed to connect", "traceback info")
            
            logger.logger.error.assert_called_once()
            call_args = logger.logger.error.call_args[0][0]
            assert "ERROR" in call_args
            assert "connection_error" in call_args
            assert "Failed to connect" in call_args

    def test_log_system_status(self):
        """Test system status logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            metrics = {"cpu": "50%", "memory": "2GB"}
            logger.log_system_status("cpu", "running", metrics)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "SYSTEM_STATUS" in call_args
            assert "cpu" in call_args
            assert "running" in call_args

    def test_log_voice_activity(self):
        """Test voice activity logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            details = {"engine": "pyttsx3", "duration": "2s"}
            logger.log_voice_activity("speak", True, details)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "VOICE_ACTIVITY" in call_args
            assert "speak" in call_args
            assert "SUCCESS" in call_args

    def test_log_voice_activity_failure(self):
        """Test voice activity logging on failure"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_voice_activity("speak", False)
            
            logger.logger.warning.assert_called_once()
            call_args = logger.logger.warning.call_args[0][0]
            assert "VOICE_ACTIVITY" in call_args
            assert "FAILED" in call_args

    def test_log_file_operation(self):
        """Test file operation logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_file_operation("create", "/path/to/file.txt", True)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "FILE_OPERATION" in call_args
            assert "create" in call_args
            assert "/path/to/file.txt" in call_args

    def test_log_network_activity(self):
        """Test network activity logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.log_network_activity("GET", "https://api.example.com", 200)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "NETWORK_ACTIVITY" in call_args
            assert "GET" in call_args
            assert "https://api.example.com" in call_args
            assert "200" in call_args

    def test_log_gui_event(self):
        """Test GUI event logging"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            
            details = {"x": 100, "y": 200}
            logger.log_gui_event("button_click", "main_window", details)
            
            logger.logger.info.assert_called_once()
            call_args = logger.logger.info.call_args[0][0]
            assert "GUI_EVENT" in call_args
            assert "button_click" in call_args
            assert "main_window" in call_args

    def test_get_session_summary(self):
        """Test getting session summary"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.session_stats = {
                "actions_logged": 10,
                "errors_logged": 2,
                "voice_activities": 5
            }
            
            summary = logger.get_session_summary()
            
            assert "actions_logged" in summary
            assert summary["actions_logged"] == 10
            assert summary["errors_logged"] == 2

    def test_save_action_log(self):
        """Test saving action log"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.action_history = [
                {"action": "test1", "timestamp": "2023-01-01"},
                {"action": "test2", "timestamp": "2023-01-02"}
            ]
            
            with patch('builtins.open', mock_open()) as mock_file, \
                 patch('json.dump') as mock_dump:
                logger.save_action_log()
                
                mock_file.assert_called_once()
                mock_dump.assert_called_once()

    def test_shutdown(self):
        """Test logger shutdown"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'), \
             patch('action_logger.ActionLogger.save_action_log') as mock_save:
            logger = ActionLogger()
            logger.logger = Mock()
            
            logger.shutdown()
            
            mock_save.assert_called_once()
            logger.logger.info.assert_called_once()

    def test_get_action_logger_singleton(self):
        """Test action logger singleton pattern"""
        with patch('action_logger.ActionLogger') as mock_logger_class:
            mock_instance = Mock()
            mock_logger_class.return_value = mock_instance
            
            from action_logger import get_action_logger
            
            # First call should create instance
            result1 = get_action_logger()
            # Second call should return same instance
            result2 = get_action_logger()
            
            assert result1 == result2
            mock_logger_class.assert_called_once()

    def test_init_action_logger_function(self):
        """Test standalone init action logger function"""
        with patch('action_logger.ActionLogger') as mock_logger_class:
            mock_instance = Mock()
            mock_logger_class.return_value = mock_instance
            
            from action_logger import init_action_logger
            result = init_action_logger("test.log")
            
            mock_logger_class.assert_called_once_with("test.log")
            assert result == mock_instance

    def test_action_history_tracking(self):
        """Test action history tracking"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            logger.action_history = []
            
            logger.log_action("test_action", "description")
            
            assert len(logger.action_history) == 1
            assert logger.action_history[0]["action_type"] == "test_action"

    def test_session_stats_tracking(self):
        """Test session statistics tracking"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            logger.session_stats = {"actions_logged": 0}
            
            logger.log_action("test_action", "description")
            
            assert logger.session_stats["actions_logged"] == 1

    def test_error_count_tracking(self):
        """Test error count tracking"""
        with patch('action_logger.ActionLogger.load_config'), \
             patch('action_logger.ActionLogger.setup_logging'):
            logger = ActionLogger()
            logger.logger = Mock()
            logger.session_stats = {"errors_logged": 0}
            
            logger.log_error("test_error", "error message")
            
            assert logger.session_stats["errors_logged"] == 1
