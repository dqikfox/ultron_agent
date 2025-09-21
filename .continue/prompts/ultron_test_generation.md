# ULTRON Agent Test Generation Prompt

You are generating comprehensive tests for ULTRON Agent 3.0 components. Follow these testing guidelines:

## Test Categories

### 1. Unit Tests
Generate pytest unit tests for individual functions and methods:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from ultron_agent.component import ComponentClass

class TestComponentClass:
    """Test cases for ComponentClass."""

    def setup_method(self):
        """Set up test fixtures."""
        self.component = ComponentClass()
        self.mock_logger = Mock()

    def test_initialization(self):
        """Test component initialization."""
        assert self.component is not None
        assert hasattr(self.component, 'required_attribute')

    def test_core_functionality(self):
        """Test core business logic."""
        with patch('ultron_agent.utils.ultron_logger') as mock_logger:
            result = self.component.core_method('test_input')
            assert result is not None
            mock_logger.log_info.assert_called_once()

    def test_error_handling(self):
        """Test error conditions and logging."""
        with patch('ultron_agent.utils.ultron_logger') as mock_logger:
            with pytest.raises(ValueError):
                self.component.method_with_validation(None)
            mock_logger.log_error.assert_called_once()

    def test_voice_integration(self):
        """Test voice accessibility features."""
        with patch('ultron_agent.voice_manager.get_voice_manager') as mock_voice:
            self.component.speak_result('test message')
            mock_voice.return_value.speak.assert_called_once_with('test message')
```

### 2. Integration Tests
Generate tests for component interactions:

```python
import pytest
from fastapi.testclient import TestClient
from ultron_agent.api_server import app

class TestAPIServer:
    """Integration tests for API server."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_model_awareness_integration(self):
        """Test integration with model awareness system."""
        with patch('ultron_agent.utils.model_awareness.should_modify_file') as mock_check:
            mock_check.return_value = (True, 'approved', {})
            response = self.client.post('/api/files/modify', json={
                'file_path': 'test.py',
                'modification': 'test change'
            })
            assert response.status_code == 200
            mock_check.assert_called_once()

    def test_voice_system_integration(self):
        """Test voice system integration."""
        with patch('ultron_agent.voice_manager.get_voice_manager') as mock_voice:
            response = self.client.post('/api/voice/speak', json={
                'message': 'test message'
            })
            assert response.status_code == 200
            mock_voice.return_value.speak.assert_called_once()
```

### 3. Mock Tests for External Services
Generate tests with proper mocking:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestExternalServiceIntegration:
    """Test external service integrations with mocks."""

    @patch('ultron_agent.brain.OllamaManager')
    @patch('ultron_agent.voice_manager.ElevenLabsManager')
    def test_full_system_integration(self, mock_voice, mock_ollama):
        """Test full system with mocked external services."""
        # Setup mocks
        mock_ollama.return_value.generate_response.return_value = 'Mock response'
        mock_voice.return_value.speak.return_value = True

        # Test system integration
        from ultron_agent.agent_core import AgentCore
        agent = AgentCore()

        result = agent.process_command('test command')
        assert result is not None
        assert 'response' in result

        # Verify external service calls
        mock_ollama.return_value.generate_response.assert_called_once()
        mock_voice.return_value.speak.assert_called_once()

    def test_error_recovery(self):
        """Test error recovery with service failures."""
        with patch('ultron_agent.brain.OllamaManager') as mock_ollama:
            mock_ollama.return_value.generate_response.side_effect = Exception('Service down')

            from ultron_agent.agent_core import AgentCore
            agent = AgentCore()

            # Should handle error gracefully
            result = agent.process_command('test command')
            assert 'error' in result or 'fallback' in result
```

### 4. Edge Case and Error Tests
Generate comprehensive error handling tests:

```python
import pytest

class TestErrorHandling:
    """Test error conditions and edge cases."""

    def test_invalid_input_validation(self):
        """Test input validation for invalid data."""
        from ultron_agent.component import ComponentClass

        component = ComponentClass()

        # Test various invalid inputs
        invalid_inputs = [None, '', 'a' * 10000, '\x00\x01\x02']

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                component.process_input(invalid_input)

    def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()

            from ultron_agent.api_client import APIClient
            client = APIClient()

            with pytest.raises(APIClient.TimeoutError):
                client.make_request('test_endpoint')

    def test_concurrent_access_safety(self):
        """Test thread safety for concurrent operations."""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id):
            try:
                from ultron_agent.component import ComponentClass
                component = ComponentClass()
                result = component.thread_safe_operation(f'worker_{worker_id}')
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors and consistent results
        assert len(errors) == 0
        assert len(results) == 10
        assert all(r == results[0] for r in results)
```

## Test Structure Guidelines

### File Organization
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_agent_core.py
│   ├── test_brain.py
│   ├── test_voice_manager.py
│   └── test_gui.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_event_system.py
│   └── test_tool_plugins.py
└── e2e/
    ├── test_full_system.py
    └── test_voice_integration.py
```

### Test Configuration (conftest.py)
```python
import pytest
from unittest.mock import Mock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()

@pytest.fixture
def mock_voice_manager():
    """Mock voice manager for testing."""
    mock = Mock()
    mock.speak.return_value = True
    return mock

@pytest.fixture
def mock_model_awareness():
    """Mock model awareness for testing."""
    mock = Mock()
    mock.should_modify_file.return_value = (True, 'approved', {})
    mock.check_file_context.return_value = {'exists': True}
    return mock

@pytest.fixture
def test_client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from ultron_agent.api_server import app
    return TestClient(app)
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ultron_agent --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_voice" -v
```

## Test Quality Standards

### Coverage Requirements
- Unit tests: >90% coverage for core components
- Integration tests: Cover all API endpoints and component interactions
- E2E tests: Cover critical user workflows

### Mock Usage Guidelines
- Mock external services (APIs, databases, file systems)
- Mock expensive operations (network calls, heavy computations)
- Use realistic mock return values
- Verify mock interactions where important

### Async Test Patterns
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test async functions."""
    from ultron_agent.component import AsyncComponent

    component = AsyncComponent()
    result = await component.async_method('test_input')
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent async operations."""
    tasks = [component.async_operation(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 5
```

### Performance Testing
```python
import time
import pytest

def test_operation_performance():
    """Test operation performance meets requirements."""
    from ultron_agent.component import ComponentClass

    component = ComponentClass()

    start_time = time.time()
    result = component.performance_critical_operation()
    end_time = time.time()

    duration = end_time - start_time
    assert duration < 1.0  # Should complete within 1 second
    assert result is not None
```

Remember to generate tests that are:
- Comprehensive in coverage
- Realistic in scenarios
- Maintainable and readable
- Following pytest best practices
- Including proper error handling
- Testing both success and failure paths
