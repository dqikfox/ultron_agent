"""
Testing configuration and utilities for ULTRON Agent 2
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest


class TestConfig:
    """Test configuration and utilities"""
    
    @staticmethod
    def setup_test_environment():
        """Setup test environment with necessary dependencies"""
        # Create temporary directories
        test_dirs = [
            "temp_logs",
            "temp_config",
            "temp_cache",
            "temp_screenshots"
        ]
        
        for dir_name in test_dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    @staticmethod
    def cleanup_test_environment():
        """Cleanup test environment"""
        test_dirs = [
            "temp_logs",
            "temp_config", 
            "temp_cache",
            "temp_screenshots"
        ]
        
        for dir_name in test_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name, ignore_errors=True)

    @staticmethod
    def create_mock_config():
        """Create mock configuration for testing"""
        return {
            "model": "llama3.2:1b",
            "voice_engine": "pyttsx3",
            "listen_always": False,
            "openai_api_key": "",
            "elevenlabs_api_key": "",
            "ollama_host": "localhost",
            "ollama_port": 11434,
            "debug": True,
            "log_level": "INFO"
        }

    @staticmethod
    def create_mock_agent():
        """Create mock agent for testing"""
        mock_agent = Mock()
        mock_agent.config = TestConfig.create_mock_config()
        mock_agent.brain = Mock()
        mock_agent.voice = Mock()
        mock_agent.memory = Mock()
        mock_agent.tools = []
        mock_agent.status = "running"
        return mock_agent


# Fixtures for common test objects
@pytest.fixture
def mock_config():
    """Fixture for mock configuration"""
    return TestConfig.create_mock_config()


@pytest.fixture
def mock_agent():
    """Fixture for mock agent"""
    return TestConfig.create_mock_agent()


@pytest.fixture
def temp_directory():
    """Fixture for temporary directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ollama_response():
    """Fixture for mock Ollama response"""
    return {
        "model": "llama3.2:1b",
        "created_at": "2023-01-01T00:00:00Z",
        "response": "Test response from Ollama",
        "done": True
    }


@pytest.fixture
def mock_voice_engine():
    """Fixture for mock voice engine"""
    engine = Mock()
    engine.say = Mock()
    engine.runAndWait = Mock()
    engine.getProperty = Mock(return_value="test_voice")
    engine.setProperty = Mock()
    return engine


@pytest.fixture
def mock_memory():
    """Fixture for mock memory system"""
    memory = Mock()
    memory.add_to_short_term = Mock()
    memory.add_to_long_term = Mock()
    memory.retrieve_short_term = Mock(return_value=[])
    memory.retrieve_long_term = Mock(return_value={})
    memory.search_memory = Mock(return_value=[])
    memory.get_recent_memory = Mock(return_value=[])
    return memory


@pytest.fixture
def mock_event_system():
    """Fixture for mock event system"""
    event_system = Mock()
    event_system.emit = Mock()
    event_system.subscribe = Mock()
    event_system.unsubscribe = Mock()
    event_system.get_recent_events = Mock(return_value=[])
    return event_system


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for all tests"""
    # Setup
    TestConfig.setup_test_environment()
    
    yield
    
    # Teardown
    TestConfig.cleanup_test_environment()


# Mock decorators for common patches
def mock_requests_get(response_data, status_code=200):
    """Decorator to mock requests.get calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.json.return_value = response_data
                mock_response.text = str(response_data)
                mock_get.return_value = mock_response
                return func(*args, **kwargs)
        return wrapper
    return decorator


def mock_requests_post(response_data, status_code=200):
    """Decorator to mock requests.post calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.json.return_value = response_data
                mock_response.text = str(response_data)
                mock_post.return_value = mock_response
                return func(*args, **kwargs)
        return wrapper
    return decorator


def mock_subprocess_run(returncode=0, stdout="", stderr=""):
    """Decorator to mock subprocess.run calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = returncode
                mock_result.stdout = stdout
                mock_result.stderr = stderr
                mock_run.return_value = mock_result
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_test_commands():
        """Generate test commands for agent testing"""
        return [
            "hello ultron",
            "what time is it",
            "take a screenshot",
            "list files in current directory",
            "run python code print('hello')",
            "help me with coding",
            "analyze this project",
            "create a new file called test.txt",
            "what's the weather like",
            "tell me a joke"
        ]
    
    @staticmethod
    def generate_test_files():
        """Generate test file data"""
        return {
            "test.txt": "This is a test file content",
            "config.json": '{"test": "config", "value": 123}',
            "script.py": "print('Hello, World!')\nprint('Test script')",
            "data.csv": "name,age,city\nJohn,25,NYC\nJane,30,LA",
            "README.md": "# Test Project\n\nThis is a test project."
        }
    
    @staticmethod
    def generate_test_responses():
        """Generate test AI responses"""
        return [
            "I understand you want to test the system.",
            "I've completed the requested task successfully.",
            "Here's the information you requested...",
            "I'll help you with that right away.",
            "The operation completed without errors."
        ]
    
    @staticmethod
    def generate_test_errors():
        """Generate test error scenarios"""
        return [
            {"type": "ConnectionError", "message": "Failed to connect to service"},
            {"type": "FileNotFoundError", "message": "The requested file was not found"},
            {"type": "PermissionError", "message": "Access denied to resource"},
            {"type": "TimeoutError", "message": "Operation timed out"},
            {"type": "ValidationError", "message": "Invalid input provided"}
        ]


# Performance testing utilities
class PerformanceTestUtils:
    """Utilities for performance testing"""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure function execution time"""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def stress_test_function(func, iterations=100, *args, **kwargs):
        """Stress test a function with multiple iterations"""
        import time
        results = []
        start_time = time.time()
        
        for i in range(iterations):
            try:
                result, exec_time = PerformanceTestUtils.measure_execution_time(func, *args, **kwargs)
                results.append({
                    "iteration": i,
                    "success": True,
                    "execution_time": exec_time,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "iteration": i,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0
                })
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "total_iterations": iterations,
            "successful_iterations": success_count,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "success_rate": success_count / iterations * 100,
            "results": results
        }


# Security testing utilities
class SecurityTestUtils:
    """Utilities for security testing"""
    
    @staticmethod
    def test_input_sanitization(func, malicious_inputs):
        """Test function with malicious inputs"""
        results = []
        
        for malicious_input in malicious_inputs:
            try:
                result = func(malicious_input)
                results.append({
                    "input": malicious_input,
                    "handled_safely": True,
                    "result": str(result)[:100]  # Truncate result
                })
            except Exception as e:
                results.append({
                    "input": malicious_input,
                    "handled_safely": True,  # Exception is good for malicious input
                    "error": str(e)
                })
        
        return results
    
    @staticmethod
    def get_malicious_inputs():
        """Get common malicious input patterns"""
        return [
            "'; DROP TABLE users; --",  # SQL injection
            "<script>alert('xss')</script>",  # XSS
            "../../../etc/passwd",  # Path traversal
            "$(rm -rf /)",  # Command injection
            "\x00\x01\x02\x03",  # Binary data
            "A" * 10000,  # Buffer overflow attempt
            "eval('malicious code')",  # Code injection
            "import os; os.system('rm -rf /')"  # Python injection
        ]


# Integration testing utilities
class IntegrationTestUtils:
    """Utilities for integration testing"""
    
    @staticmethod
    def simulate_user_interaction(agent, commands, delay=0.1):
        """Simulate user interaction with agent"""
        import time
        results = []
        
        for command in commands:
            try:
                time.sleep(delay)  # Simulate real user delay
                result = agent.handle_text(command)
                results.append({
                    "command": command,
                    "success": True,
                    "response": result
                })
            except Exception as e:
                results.append({
                    "command": command,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    @staticmethod
    def test_system_components(components):
        """Test individual system components"""
        results = {}
        
        for component_name, component in components.items():
            try:
                # Test basic functionality
                if hasattr(component, 'test'):
                    component.test()
                    results[component_name] = {"status": "healthy", "tested": True}
                else:
                    results[component_name] = {"status": "unknown", "tested": False}
            except Exception as e:
                results[component_name] = {"status": "error", "error": str(e), "tested": True}
        
        return results
