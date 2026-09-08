# Basic smoke test for Ultron Agent
import pytest
import asyncio
from unittest.mock import Mock, patch

from ultron_agent import get_config, setup_logging, get_health_checker


class TestBasicFunctionality:
    """Basic smoke tests to ensure core components load."""

    def test_config_loads(self):
        """Test that configuration loads without errors."""
        config = get_config()
        assert config is not None
        assert config.app_name == "Ultron Agent"
        assert config.version == "3.0.0"

    def test_logging_initializes(self):
        """Test that logging system initializes."""
        logger = setup_logging(log_level="INFO", enable_console=True)
        assert logger is not None

    @pytest.mark.asyncio
    async def test_health_checker(self):
        """Test health checker basic functionality."""
        health_checker = get_health_checker()

        # Test basic health
        health = await health_checker.check_basic_health()
        assert health["status"] == "healthy"
        assert "timestamp" in health
        assert "version" in health

    @pytest.mark.asyncio
    async def test_api_imports(self):
        """Test that API module can be imported and basic functionality works."""
        from ultron_agent.api import app

        # Basic FastAPI app check
        assert app is not None
        assert app.title == "Ultron Agent API"


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_validation_valid(self):
        """Test valid configuration passes validation."""
        from ultron_agent.config import UltronConfig

        config = UltronConfig(
            api_port=5000,
            voice_rate=180,
            voice_volume=0.9
        )

        assert config.api_port == 5000
        assert config.voice_rate == 180
        assert config.voice_volume == 0.9

    def test_config_validation_invalid_port(self):
        """Test invalid port raises validation error."""
        from ultron_agent.config import UltronConfig
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UltronConfig(api_port=999)  # Below minimum

        with pytest.raises(ValidationError):
            UltronConfig(api_port=70000)  # Above maximum


class TestErrorHandling:
    """Test error handling and classification."""

    def test_error_classification(self):
        """Test that errors are properly classified."""
        from ultron_agent.errors import VoiceError, ModelError, handle_error
        import logging

        # Test VoiceError
        voice_error = VoiceError("Microphone not available", engine="pyttsx3")
        assert voice_error.category.value == "voice"
        assert "engine" in voice_error.details

        # Test error handling
        mock_logger = Mock(spec=logging.Logger)
        original_error = ConnectionError("Connection failed")

        handled = handle_error(original_error, mock_logger, "test_context")
        assert handled.category.value == "api"
        assert handled.original_error == original_error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
