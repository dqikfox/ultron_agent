import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

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
    """Allow all tests to run (no limits for utils tests)"""
    # Don't limit tests - run all
    pass
