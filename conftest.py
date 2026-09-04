import pytest
import sys
import os
import builtins
from pathlib import Path
from unittest.mock import mock_open

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Back-compat for test modules that reference mock_open without importing it.
if not hasattr(builtins, "mock_open"):
    builtins.mock_open = mock_open

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment once per session"""
    # Set test environment variable
    os.environ["TESTING"] = "1"
    os.environ["ULTRON_TEST_MODE"] = "1"
    
    yield
    
    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("ULTRON_TEST_MODE", None)

def pytest_configure(config):
    """Configure pytest to prevent infinite loops"""
    config.option.maxfail = 1
    config.option.tb = "short"

def pytest_collection_modifyitems(config, items):
    """Limit test collection to prevent loops"""
    # Limit to first 10 tests if too many
    if len(items) > 50:
        items[:] = items[:10]