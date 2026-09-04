"""
Comprehensive tests for Config class
"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from config import Config, ConfigValidationError


class TestConfig:
    """Test suite for Config class"""

    def test_config_initialization_default(self):
        """Test config initialization with default path"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{"test": "value"}')):
            config = Config()
            assert config.path == "ultron_config.json"

    def test_config_initialization_custom_path(self):
        """Test config initialization with custom path"""
        custom_path = "custom_config.json"
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{"test": "value"}')):
            config = Config(custom_path)
            assert config.path == custom_path

    def test_load_config_file_exists(self):
        """Test loading config when file exists"""
        test_data = {"openai_api_key": "test_key", "model": "test_model"}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            assert config.data["openai_api_key"] == "test_key"
            assert config.data["model"] == "test_model"

    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist"""
        with patch('os.path.exists', return_value=False), \
             patch.object(Config, 'create_default_config') as mock_create:
            config = Config()
            mock_create.assert_called_once()

    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='invalid json')), \
             pytest.raises(ConfigValidationError):
            Config()

    def test_create_default_config(self):
        """Test creating default configuration"""
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_dump:
            config = Config()
            config.create_default_config()
            mock_file.assert_called_with(config.path, 'w')
            mock_dump.assert_called_once()

    def test_get_existing_key(self):
        """Test getting existing configuration key"""
        test_data = {"test_key": "test_value"}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            assert config.get("test_key") == "test_value"

    def test_get_non_existing_key_with_default(self):
        """Test getting non-existing key with default value"""
        test_data = {}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            assert config.get("non_existing", "default") == "default"

    def test_get_non_existing_key_without_default(self):
        """Test getting non-existing key without default value"""
        test_data = {}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            assert config.get("non_existing") is None

    def test_set_key_value(self):
        """Test setting configuration key-value pair"""
        test_data = {}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            config.set("new_key", "new_value")
            assert config.data["new_key"] == "new_value"

    def test_save_config(self):
        """Test saving configuration to file"""
        test_data = {"test": "value"}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))) as mock_file, \
             patch('json.dump') as mock_dump:
            config = Config()
            config.save_config()
            mock_dump.assert_called_once()

    def test_has_valid_api_keys_true(self):
        """Test checking valid API keys when they exist"""
        test_data = {"openai_api_key": "valid_key", "elevenlabs_api_key": "valid_key"}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            assert config.has_valid_api_keys() is True

    def test_has_valid_api_keys_false(self):
        """Test checking valid API keys when they don't exist"""
        test_data = {}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            assert config.has_valid_api_keys() is False

    def test_load_env_variables(self):
        """Test loading environment variables"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_key'}), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{}')):
            config = Config()
            config.load_env_variables()
            assert config.data.get("openai_api_key") == "env_key"

    def test_get_sanitized_data(self):
        """Test getting sanitized configuration data"""
        test_data = {
            "openai_api_key": "secret_key",
            "elevenlabs_api_key": "secret_key2",
            "normal_setting": "visible"
        }
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            sanitized = config.get_sanitized_data()
            assert "openai_api_key" not in sanitized
            assert "elevenlabs_api_key" not in sanitized
            assert sanitized["normal_setting"] == "visible"

    def test_validate_config_valid(self):
        """Test validating valid configuration"""
        test_data = {
            "model": "test_model",
            "voice_engine": "test_engine",
            "listen_always": False
        }
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            # Should not raise exception
            config.validate_config()

    def test_validate_config_invalid(self):
        """Test validating invalid configuration"""
        test_data = {
            "model": 123,  # Should be string
            "voice_engine": None,
            "listen_always": "not_bool"  # Should be boolean
        }
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))), \
             pytest.raises(ConfigValidationError):
            config = Config()
            config.validate_config()

    def test_str_representation(self):
        """Test string representation of config"""
        test_data = {"test": "value"}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            str_repr = str(config)
            assert "Config" in str_repr
            assert config.path in str_repr

    def test_repr_representation(self):
        """Test repr representation of config"""
        test_data = {"test": "value"}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            config = Config()
            repr_str = repr(config)
            assert "Config" in repr_str
            assert config.path in repr_str
