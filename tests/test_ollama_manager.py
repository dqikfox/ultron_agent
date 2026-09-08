"""
Comprehensive tests for Ollama Manager
"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import ollama_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_manager import OllamaManager, get_ollama_manager, test_ollama_connection


class TestOllamaManager:
    """Test suite for OllamaManager"""

    @patch('ollama_manager.requests.get')
    def test_check_connection_success(self, mock_get):
        """Test successful connection check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        manager = OllamaManager()
        result = manager.check_connection()
        
        assert result is True
        assert manager.is_connected is True

    @patch('ollama_manager.requests.get')
    def test_check_connection_failure(self, mock_get):
        """Test connection check failure"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        result = manager.check_connection()
        
        assert result is False
        assert manager.is_connected is False

    @patch('ollama_manager.requests.get')
    def test_check_connection_timeout(self, mock_get):
        """Test connection check timeout"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        manager = OllamaManager()
        result = manager.check_connection()
        
        assert result is False
        assert manager.is_connected is False

    def test_parse_models_success(self):
        """Test parsing models from response"""
        response_data = {
            "models": [
                {"name": "llama2:7b", "size": 1000000},
                {"name": "codellama:13b", "size": 2000000}
            ]
        }
        
        manager = OllamaManager.__new__(OllamaManager)
        models = manager._parse_models(response_data)
        
        assert len(models) == 2
        assert "llama2:7b" in models
        assert "codellama:13b" in models

    def test_parse_models_empty(self):
        """Test parsing empty models response"""
        response_data = {"models": []}
        
        manager = OllamaManager.__new__(OllamaManager)
        models = manager._parse_models(response_data)
        
        assert models == []

    def test_parse_models_no_models_key(self):
        """Test parsing response without models key"""
        response_data = {"invalid": "data"}
        
        manager = OllamaManager.__new__(OllamaManager)
        models = manager._parse_models(response_data)
        
        assert models == []

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_list_running_models_success(self, mock_run, mock_get):
        """Test listing running models successfully"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama ps output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "NAME                ID              SIZE    UNTIL\nllama2:7b          abc123          3.8GB   4 minutes\n"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        models = manager.list_running_models()
        
        assert len(models) == 1
        assert models[0]['name'] == "llama2:7b"

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_list_running_models_failure(self, mock_run, mock_get):
        """Test listing running models failure"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        mock_run.side_effect = Exception("Command failed")
        
        manager = OllamaManager()
        models = manager.list_running_models()
        
        assert models == []

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_pull_model_success(self, mock_run, mock_get):
        """Test pulling model successfully"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama2:7b"}]}
        mock_get.return_value = mock_response
        
        # Mock ollama pull
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Model pulled successfully"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.pull_model("llama2:7b")
        
        assert result is True
        mock_run.assert_called_once()

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_pull_model_failure(self, mock_run, mock_get):
        """Test pulling model failure"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama pull failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Model not found"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.pull_model("nonexistent:model")
        
        assert result is False

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_pull_model_timeout(self, mock_run, mock_get):
        """Test pulling model timeout"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock timeout
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("ollama", 600)
        
        manager = OllamaManager()
        result = manager.pull_model("large:model")
        
        assert result is False

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_remove_model_success(self, mock_run, mock_get):
        """Test removing model successfully"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama rm
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.remove_model("llama2:7b")
        
        assert result is True
        mock_run.assert_called_once()

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_remove_model_failure(self, mock_run, mock_get):
        """Test removing model failure"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama rm failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Model not found"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.remove_model("nonexistent:model")
        
        assert result is False

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.requests.post')
    def test_test_model_success(self, mock_post, mock_get):
        """Test testing model successfully"""
        # Mock connection check
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"models": [{"name": "llama2:7b"}]}
        mock_get.return_value = mock_get_response
        
        # Mock model test
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"response": "OK"}
        mock_post.return_value = mock_post_response
        
        manager = OllamaManager()
        manager.current_model = "llama2:7b"
        result = manager.test_model("llama2:7b")
        
        assert result is True
        mock_post.assert_called_once()

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.requests.post')
    def test_test_model_failure(self, mock_post, mock_get):
        """Test testing model failure"""
        # Mock connection check
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"models": []}
        mock_get.return_value = mock_get_response
        
        # Mock model test failure
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        result = manager.test_model("llama2:7b")
        
        assert result is False

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_show_model_info_success(self, mock_run, mock_get):
        """Test showing model info successfully"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama show
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Model: llama2:7b\nSize: 3.8GB"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        info = manager.show_model_info("llama2:7b")
        
        assert info is not None
        assert "llama2:7b" in info

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_show_model_info_failure(self, mock_run, mock_get):
        """Test showing model info failure"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama show failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Model not found"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        info = manager.show_model_info("nonexistent:model")
        
        assert info is None

    @patch('ollama_manager.requests.get')
    def test_get_status_connected(self, mock_get):
        """Test getting status when connected"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama2:7b"}]}
        mock_get.return_value = mock_response
        
        manager = OllamaManager()
        status = manager.get_status()
        
        assert status['connected'] is True
        assert 'available_models' in status
        assert 'model_count' in status

    @patch('ollama_manager.requests.get')
    def test_get_status_disconnected(self, mock_get):
        """Test getting status when disconnected"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        status = manager.get_status()
        
        assert status['connected'] is False

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_get_model_sizes_success(self, mock_run, mock_get):
        """Test getting model sizes successfully"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock ollama list
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "NAME                ID              SIZE    MODIFIED\nllama2:7b          abc123          3.8GB   2 days ago\n"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        sizes = manager.get_model_sizes()
        
        assert "llama2:7b" in sizes
        assert sizes["llama2:7b"]["size"] == "3.8GB"

    @patch('ollama_manager.requests.get')
    @patch('ollama_manager.subprocess.run')
    def test_get_model_sizes_failure(self, mock_run, mock_get):
        """Test getting model sizes failure"""
        # Mock connection check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        # Mock failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        sizes = manager.get_model_sizes()
        
        assert sizes == {}

    @patch('ollama_manager.OllamaManager')
    def test_get_ollama_manager_singleton(self, mock_manager_class):
        """Test ollama manager singleton pattern"""
        mock_instance = Mock()
        mock_manager_class.return_value = mock_instance
        
        # Reset the global instance
        import ollama_manager
        ollama_manager._ollama_manager = None
        
        # First call should create instance
        result1 = get_ollama_manager()
        # Second call should return same instance
        result2 = get_ollama_manager()
        
        assert result1 == result2
        mock_manager_class.assert_called_once()

    @patch('ollama_manager.get_ollama_manager')
    def test_test_ollama_connection_function(self, mock_get_manager):
        """Test standalone test ollama connection function"""
        mock_manager = Mock()
        mock_manager.check_connection.return_value = True
        mock_get_manager.return_value = mock_manager
        
        result = test_ollama_connection()
        
        assert result is True
        mock_manager.check_connection.assert_called_once()


if __name__ == "__main__":
    try:
        pytest.main([__file__, "-v"])

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
