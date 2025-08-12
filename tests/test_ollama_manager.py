"""
Comprehensive tests for Ollama Manager
"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from ollama_manager import OllamaManager


class TestOllamaManager:
    """Test suite for OllamaManager"""

    def test_ollama_manager_initialization_with_config(self):
        """Test initialization with config"""
        mock_config = Mock()
        mock_config.get.return_value = "localhost"
        
        manager = OllamaManager(config=mock_config)
        assert manager.config == mock_config

    def test_ollama_manager_initialization_without_config(self):
        """Test initialization without config"""
        with patch('config.Config') as mock_config_class:
            manager = OllamaManager()
            mock_config_class.assert_called_once()

    @patch('requests.get')
    def test_check_connection_success(self, mock_get):
        """Test successful connection check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        
        manager = OllamaManager()
        result = manager.check_connection()
        
        assert result is True
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_check_connection_failure(self, mock_get):
        """Test connection check failure"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        result = manager.check_connection()
        
        assert result is False

    @patch('requests.get')
    def test_check_connection_timeout(self, mock_get):
        """Test connection check timeout"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        manager = OllamaManager()
        result = manager.check_connection()
        
        assert result is False

    @patch('requests.get')
    def test_get_status_running(self, mock_get):
        """Test getting status when Ollama is running"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        manager = OllamaManager()
        status = manager.get_status()
        
        assert status["running"] is True
        assert "models" in status

    @patch('requests.get')
    def test_get_status_not_running(self, mock_get):
        """Test getting status when Ollama is not running"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        status = manager.get_status()
        
        assert status["running"] is False
        assert status["error"] is not None

    @patch('requests.get')
    def test_list_running_models_success(self, mock_get):
        """Test listing running models successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:7b", "size": 1000000},
                {"name": "codellama:13b", "size": 2000000}
            ]
        }
        mock_get.return_value = mock_response
        
        manager = OllamaManager()
        models = manager.list_running_models()
        
        assert len(models) == 2
        assert models[0]["name"] == "llama2:7b"
        assert models[1]["name"] == "codellama:13b"

    @patch('requests.get')
    def test_list_running_models_failure(self, mock_get):
        """Test listing running models failure"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        models = manager.list_running_models()
        
        assert models == []

    @patch('subprocess.run')
    def test_pull_model_success(self, mock_run):
        """Test pulling model successfully"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Model pulled successfully"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.pull_model("llama2:7b")
        
        assert result is True
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_pull_model_failure(self, mock_run):
        """Test pulling model failure"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Model not found"
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.pull_model("nonexistent:model")
        
        assert result is False

    @patch('subprocess.run')
    def test_remove_model_success(self, mock_run):
        """Test removing model successfully"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.remove_model("llama2:7b")
        
        assert result is True
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_remove_model_failure(self, mock_run):
        """Test removing model failure"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager.remove_model("nonexistent:model")
        
        assert result is False

    @patch('requests.post')
    def test_test_model_success(self, mock_post):
        """Test testing model successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Hello! I'm working correctly."
        }
        mock_post.return_value = mock_response
        
        manager = OllamaManager()
        result = manager.test_model("llama2:7b")
        
        assert result is True
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_test_model_failure(self, mock_post):
        """Test testing model failure"""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        result = manager.test_model("llama2:7b")
        
        assert result is False

    @patch('requests.post')
    def test_switch_model_success(self, mock_post):
        """Test switching model successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        mock_config = Mock()
        manager = OllamaManager(config=mock_config)
        result = manager.switch_model("new_model:7b")
        
        assert result is True
        mock_config.set.assert_called_with("model", "new_model:7b")
        mock_config.save_config.assert_called_once()

    @patch('requests.post')
    def test_switch_model_failure(self, mock_post):
        """Test switching model failure"""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        result = manager.switch_model("nonexistent:model")
        
        assert result is False

    @patch('subprocess.run')
    def test_show_model_info_success(self, mock_run):
        """Test showing model info successfully"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"modelfile": "FROM llama2:7b", "parameters": {}}'
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        info = manager.show_model_info("llama2:7b")
        
        assert info is not None
        assert "modelfile" in info

    @patch('subprocess.run')
    def test_show_model_info_failure(self, mock_run):
        """Test showing model info failure"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        info = manager.show_model_info("nonexistent:model")
        
        assert info is None

    def test_parse_models_success(self):
        """Test parsing models from response"""
        response_data = {
            "models": [
                {"name": "llama2:7b", "size": 1000000, "modified_at": "2023-01-01"},
                {"name": "codellama:13b", "size": 2000000, "modified_at": "2023-01-02"}
            ]
        }
        
        manager = OllamaManager()
        models = manager._parse_models(response_data)
        
        assert len(models) == 2
        assert models[0]["name"] == "llama2:7b"
        assert models[1]["name"] == "codellama:13b"

    def test_parse_models_empty(self):
        """Test parsing empty models response"""
        response_data = {"models": []}
        
        manager = OllamaManager()
        models = manager._parse_models(response_data)
        
        assert models == []

    def test_parse_models_malformed(self):
        """Test parsing malformed models response"""
        response_data = {"invalid": "data"}
        
        manager = OllamaManager()
        models = manager._parse_models(response_data)
        
        assert models == []

    @patch('requests.get')
    def test_get_model_sizes_success(self, mock_get):
        """Test getting model sizes successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:7b", "size": 3825819519},
                {"name": "codellama:13b", "size": 7365960935}
            ]
        }
        mock_get.return_value = mock_response
        
        manager = OllamaManager()
        sizes = manager.get_model_sizes()
        
        assert len(sizes) == 2
        assert "llama2:7b" in sizes
        assert "codellama:13b" in sizes

    @patch('requests.get')
    def test_get_model_sizes_failure(self, mock_get):
        """Test getting model sizes failure"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        manager = OllamaManager()
        sizes = manager.get_model_sizes()
        
        assert sizes == {}

    @patch('subprocess.run')
    def test_stop_running_models_success(self, mock_run):
        """Test stopping running models successfully"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager._stop_running_models()
        
        assert result is True

    @patch('subprocess.run')
    def test_stop_running_models_failure(self, mock_run):
        """Test stopping running models failure"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        manager = OllamaManager()
        result = manager._stop_running_models()
        
        assert result is False

    def test_get_current_model_with_config(self):
        """Test getting current model from config"""
        mock_config = Mock()
        mock_config.get.return_value = "llama2:7b"
        
        manager = OllamaManager(config=mock_config)
        model = manager._get_current_model()
        
        assert model == "llama2:7b"

    def test_get_current_model_default(self):
        """Test getting current model with default"""
        mock_config = Mock()
        mock_config.get.return_value = None
        
        manager = OllamaManager(config=mock_config)
        model = manager._get_current_model()
        
        assert model == "llama3.2:1b"  # Default model

    @patch('ollama_manager.OllamaManager.pull_model')
    @patch('ollama_manager.OllamaManager._get_current_model')
    @patch('ollama_manager.OllamaManager.list_running_models')
    def test_ensure_default_model_already_available(self, mock_list_models, mock_get_model, mock_pull):
        """Test ensuring default model when it's already available"""
        mock_get_model.return_value = "llama2:7b"
        mock_list_models.return_value = [{"name": "llama2:7b"}]
        
        manager = OllamaManager()
        result = manager.ensure_default_model()
        
        assert result is True
        mock_pull.assert_not_called()

    @patch('ollama_manager.OllamaManager.pull_model')
    @patch('ollama_manager.OllamaManager._get_current_model')
    @patch('ollama_manager.OllamaManager.list_running_models')
    def test_ensure_default_model_needs_pull(self, mock_list_models, mock_get_model, mock_pull):
        """Test ensuring default model when it needs to be pulled"""
        mock_get_model.return_value = "llama2:7b"
        mock_list_models.return_value = []
        mock_pull.return_value = True
        
        manager = OllamaManager()
        result = manager.ensure_default_model()
        
        assert result is True
        mock_pull.assert_called_once_with("llama2:7b")

    def test_get_ollama_manager_singleton(self):
        """Test ollama manager singleton pattern"""
        with patch('ollama_manager.OllamaManager') as mock_manager_class:
            mock_instance = Mock()
            mock_manager_class.return_value = mock_instance
            
            from ollama_manager import get_ollama_manager
            
            # First call should create instance
            result1 = get_ollama_manager()
            # Second call should return same instance
            result2 = get_ollama_manager()
            
            assert result1 == result2
            mock_manager_class.assert_called_once()

    def test_test_ollama_connection_function(self):
        """Test standalone test ollama connection function"""
        with patch('ollama_manager.get_ollama_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.check_connection.return_value = True
            mock_get_manager.return_value = mock_manager
            
            from ollama_manager import test_ollama_connection
            result = test_ollama_connection()
            
            assert result is True
            mock_manager.check_connection.assert_called_once()
