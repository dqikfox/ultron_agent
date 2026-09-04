# ULTRON Agent Testing Guide

Complete guide to testing the ULTRON Agent 3.0 framework.

## Quick Start

```bash
# Run all tests
pytest

# Run specific test markers
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m slow -v     # Slow tests with verbose output

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/utils/test_scheduler.py -v
```

## Configuration Files

### Root: `./conftest.py`
- **Scope:** Project-wide pytest configuration
- **Purpose:** Session-level setup for all tests
- **Features:**
  - Sets `TESTING=1` and `ULTRON_TEST_MODE=1` environment variables
  - Configures pytest to stop at first failure (`maxfail=1`)
  - Sets traceback style to short format
  - Adds project root to Python path

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Runs once per test session"""
    os.environ["TESTING"] = "1"
    os.environ["ULTRON_TEST_MODE"] = "1"
```

### Tests Utils: `./tests/utils/conftest.py`
- **Scope:** Shared fixtures for utility tests
- **Purpose:** Provides reusable mock objects and test data
- **Fixtures Available:**

#### File System Fixtures
- `temp_dir` - Temporary directory for test files
- `temp_schedule_file` - Schedule file for task scheduler tests

#### Async Fixtures
- `event_loop` - Event loop for async tests
- `mock_async_function` - Mock async function that succeeds
- `mock_failing_function` - Mock async function that raises error
- `mock_slow_function` - Mock async function that times out

#### Security & Testing Data
- `sample_xss_inputs` - XSS attack vectors for security testing
- `sample_csrf_tokens` - CSRF tokens (valid, invalid, expired)
- `sample_secrets` - API keys, tokens, credentials for secret detection
- `sample_schedule_data` - Task scheduler test data
- `sample_plugin_metadata` - Plugin metadata for dynamic loader tests
- `mock_plugin_class` - Full mock plugin class

#### Configuration Fixtures
- `security_context` - SecurityContext with session_id
- `rate_limit_config` - RateLimitConfig with request limits
- `model_profiles` - LLM model profiles (llava:7b, gpt-4o)

#### Logging Fixtures
- `mock_logger` - Mocked ultron_logger for test isolation

## Test Markers

Defined in `pytest.ini` and `conftest.py`:

```python
@pytest.mark.unit         # Unit tests (fast, no I/O)
@pytest.mark.integration  # Integration tests (may touch real services)
@pytest.mark.slow         # Slow tests (> 10 seconds)
@pytest.mark.asyncio      # Async tests
```

**Example:**
```python
@pytest.mark.unit
def test_parser_simple():
    assert 1 + 1 == 2

@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_request():
    result = await api.call()
    assert result.status == 200
```

## Key Test Fixtures

### Using Fixtures

```python
def test_with_temp_dir(temp_dir):
    """Test using temporary directory"""
    test_file = temp_dir / "test.json"
    test_file.write_text('{"key": "value"}')
    assert test_file.exists()

async def test_async_function(mock_async_function):
    """Test using mock async function"""
    result = await mock_async_function(arg1="test")
    assert result["result"] == "success"

def test_security_context(security_context):
    """Test using security context"""
    assert security_context.session_id == "test_session_123"
```

### Creating Custom Fixtures

```python
# In tests/conftest.py or test file
import pytest

@pytest.fixture
def custom_config():
    """Custom configuration for tests"""
    return {
        "api_port": 5000,
        "debug": True,
        "max_retries": 3
    }

def test_with_custom_config(custom_config):
    assert custom_config["api_port"] == 5000
```

## Environment Detection

Tests automatically detect the test environment:

```python
import os

# In your code
if os.environ.get("TESTING") == "1":
    # Use test database, skip real API calls
    db = MockDatabase()
else:
    # Use production configuration
    db = RealDatabase()

if os.environ.get("ULTRON_TEST_MODE") == "1":
    # ULTRON-specific test behavior
    pass
```

## Running Different Test Suites

```bash
# Run all unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"

# Run unit + integration, skip slow
pytest -m "unit or integration"

# Run with full output
pytest -vv -s

# Run with coverage and HTML report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Run specific test by name
pytest -k test_agent_initialization -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests
pytest --lf

# Run failed tests first, then others
pytest --ff
```

## Async Test Examples

```python
import pytest
import asyncio

# Pytest recognizes async test functions automatically
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None

# Using event_loop fixture
@pytest.mark.asyncio
async def test_with_event_loop(event_loop):
    async def wait_and_return():
        await asyncio.sleep(0.1)
        return "done"
    
    result = await wait_and_return()
    assert result == "done"
```

## Security Testing

```python
def test_xss_protection(sample_xss_inputs):
    """Test XSS vulnerability handling"""
    from utils.security_utils import sanitize_html
    
    malicious = sample_xss_inputs["script_tag"]
    safe = sanitize_html(malicious)
    assert "<script>" not in safe

def test_secret_detection(sample_secrets):
    """Test secret detection"""
    from utils.security_utils import detect_secrets
    
    detected = detect_secrets(sample_secrets["github_token"])
    assert detected is True
    
    detected = detect_secrets(sample_secrets["safe_text"])
    assert detected is False

def test_rate_limiting(rate_limit_config):
    """Test rate limiting"""
    from utils.security_utils import RateLimiter
    
    limiter = RateLimiter(rate_limit_config)
    
    # First 10 requests should pass
    for _ in range(10):
        assert limiter.allow_request() is True
    
    # 11th request should fail
    assert limiter.allow_request() is False
```

## Plugin Testing

```python
def test_plugin_initialization(mock_plugin_class):
    """Test plugin initialization"""
    plugin = mock_plugin_class()
    
    config = {"setting": "value"}
    result = plugin.initialize(config)
    
    assert result is True
    assert plugin.initialized is True
    assert plugin.config == config

def test_plugin_execution(mock_plugin_class):
    """Test plugin execution"""
    plugin = mock_plugin_class()
    plugin.initialize({})
    
    result = plugin.execute(arg1="test", arg2="value")
    
    assert result["result"] == "executed"
    assert result["kwargs"]["arg1"] == "test"

def test_plugin_cleanup(mock_plugin_class):
    """Test plugin cleanup"""
    plugin = mock_plugin_class()
    plugin.cleanup()
    
    assert plugin.cleaned_up is True
```

## Coverage Reports

```bash
# Generate coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML report (opens in browser)
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Set minimum coverage threshold
pytest --cov=. --cov-fail-under=80
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -v --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Troubleshooting

### Issue: Tests fail with import errors

**Solution:** Ensure root directory is in Python path (conftest.py handles this)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Issue: Async tests fail with "no running event loop"

**Solution:** Use `@pytest.mark.asyncio` decorator or event_loop fixture

```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_function()
    assert result
```

### Issue: Tests pass locally but fail in CI

**Common causes:**
- Missing environment variables (check `.env.test`)
- Port conflicts (CI uses different ports)
- Timezone issues (use UTC for tests)
- File system permissions

**Solution:**
```python
import os
import pytest

@pytest.fixture(autouse=True)
def setup_ci_env():
    """Setup CI environment variables"""
    os.environ.setdefault("CI", "false")
    os.environ.setdefault("TESTING", "1")
    os.environ.setdefault("TZ", "UTC")
```

### Issue: Fixtures not found

**Solution:** Ensure conftest.py is in:
- Project root: `./conftest.py` (session-level)
- Test directory: `./tests/conftest.py` (test-level)
- Utils directory: `./tests/utils/conftest.py` (utils tests)

## Best Practices

1. **Test Organization**
   - One test file per module
   - Group related tests in classes
   - Use clear, descriptive test names

2. **Fixtures**
   - Use fixtures for setup/teardown
   - Share fixtures via conftest.py
   - Scope fixtures appropriately (function, class, module, session)

3. **Markers**
   - Mark slow tests with `@pytest.mark.slow`
   - Mark integration tests with `@pytest.mark.integration`
   - Use markers to run test subsets

4. **Async Tests**
   - Always use `@pytest.mark.asyncio` for async tests
   - Use event_loop fixture for complex async scenarios
   - Be careful with timeouts in CI environments

5. **Coverage**
   - Aim for 80%+ code coverage
   - Use `--cov-report=html` for detailed analysis
   - Don't obsess over 100% (focus on logic coverage)

## Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **ULTRON Repository:** https://github.com/dqikfox/ultron_agent
