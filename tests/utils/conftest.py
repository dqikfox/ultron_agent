"""
Shared pytest fixtures and configuration for utility tests
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import asyncio


@pytest.fixture
def temp_dir():
    """Temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_schedule_file(temp_dir):
    """Temporary schedule file for task scheduler tests"""
    schedule_file = temp_dir / "schedules.json"
    return schedule_file


@pytest.fixture
def sample_schedule_data():
    """Sample schedule data for testing"""
    return {
        "timestamp": datetime.now().isoformat(),
        "tasks": [
            {
                "name": "test_task",
                "cron_expression": "0 12 * * *",
                "max_retries": 3,
                "backoff_factor": 2.0,
                "timeout_s": 30.0,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "last_status": "pending"
            }
        ]
    }


@pytest.fixture
def mock_async_function():
    """Mock async function for testing"""
    async def test_func(*args, **kwargs):
        await asyncio.sleep(0.01)
        return {"result": "success", "args": args, "kwargs": kwargs}
    return test_func


@pytest.fixture
def mock_failing_function():
    """Mock async function that fails"""
    async def test_func(*args, **kwargs):
        await asyncio.sleep(0.01)
        raise ValueError("Test error")
    return test_func


@pytest.fixture
def mock_slow_function():
    """Mock async function that times out"""
    async def test_func(*args, **kwargs):
        await asyncio.sleep(5.0)
        return {"result": "success"}
    return test_func


@pytest.fixture
def sample_xss_inputs():
    """Sample XSS attack inputs"""
    return {
        "script_tag": "<script>alert('xss')</script>Hello",
        "event_handler": '<img src=x onerror="alert(\'xss\')">',
        "javascript_protocol": '<a href="javascript:alert(\'xss\')">Click</a>',
        "html_entities": "<div>&lt;script&gt;alert('xss')&lt;/script&gt;</div>",
        "safe_html": "<div><p>Safe content</p></div>"
    }


@pytest.fixture
def sample_csrf_tokens():
    """Sample CSRF tokens for testing"""
    return {
        "valid_token": "abcd1234efgh5678ijkl9012mnop3456",
        "invalid_token": "invalid_token_format",
        "expired_token": "expired_abcd1234efgh5678ijkl9012"
    }


@pytest.fixture
def sample_secrets():
    """Sample secrets for detection testing"""
    return {
        "aws_key": "AKIAIOSFODNN7EXAMPLE",
        "github_token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
        "api_key": "api_key = sk-1234567890abcdefghijklmnopqrstuvwxyz",
        "slack_token": "xoxb-1234567890-1234567890-abcdefghijklmnop",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQE...",
        "password": "password123456789",
        "safe_text": "This is safe text with no secrets"
    }


@pytest.fixture
def sample_plugin_metadata():
    """Sample plugin metadata"""
    from utils.dynamic_loader import PluginMetadata
    return PluginMetadata(
        name="test_plugin",
        version="1.0.0",
        author="Test Author",
        description="Test plugin",
        dependencies=["json", "asyncio"]
    )


@pytest.fixture
def mock_plugin_class():
    """Mock plugin class for testing"""
    from utils.dynamic_loader import PluginBase, PluginMetadata

    class MockPlugin(PluginBase):
        def __init__(self):
            self.initialized = False
            self.cleaned_up = False

        @property
        def metadata(self):
            return PluginMetadata(
                name="mock_plugin",
                version="1.0.0",
                author="Test",
                description="Mock plugin for testing",
                dependencies=[]
            )

        def initialize(self, config):
            self.initialized = True
            self.config = config
            return True

        def execute(self, *args, **kwargs):
            if not self.initialized:
                raise RuntimeError("Plugin not initialized")
            return {"result": "executed", "args": args, "kwargs": kwargs}

        def cleanup(self):
            self.cleaned_up = True

    return MockPlugin


@pytest.fixture
def event_loop():
    """Event loop fixture for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('utils.ultron_logger.ultron_logger') as mock:
        yield mock


@pytest.fixture
def rate_limit_config():
    """Rate limit configuration for testing"""
    from utils.security_utils import RateLimitConfig
    return RateLimitConfig(
        max_requests=10,
        time_window_s=5,
        burst_allowed=True
    )


@pytest.fixture
def security_context():
    """Security context for testing"""
    from utils.security_utils import SecurityContext
    return SecurityContext(session_id="test_session_123")


@pytest.fixture
def model_profiles():
    """Sample model profiles for testing"""
    return {
        "llava:7b": {
            "model": "llava:7b",
            "version": "7b",
            "max_tokens": 2048,
            "cost_per_1k_tokens": 0.0
        },
        "gpt-4o": {
            "model": "gpt-4o",
            "version": "2024-01-01",
            "max_tokens": 128000,
            "cost_per_1k_tokens": 0.03
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


# Disable warnings for tests
pytest.skip_markers = ["slow", "asyncio"]
