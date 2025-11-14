"""Integration tests module for ULTRON Agent.

This package contains integration tests that verify cross-component
functionality and external service connectivity.

Modules:
    - test_ollama_integration: Ollama LLM backend tests
    - test_docker_stack: Docker Compose stack tests
    - test_api_endpoints: REST API endpoint tests
    - test_file_operations: File system operation tests

Running Integration Tests:

    # All integration tests
    pytest tests/integration/

    # Specific test file
    pytest tests/integration/test_ollama_integration.py

    # Specific test class
    pytest tests/integration/test_api_endpoints.py::TestAuthentication

    # With markers
    pytest -m integration
    pytest -m "integration and not network"

    # With verbose output
    pytest tests/integration/ -v -s

Test Categories:
    - integration: All integration tests (require services)
    - network: Tests requiring network connectivity
    - docker_compose: Docker Compose stack tests
    - filesystem: File system operation tests

Service Requirements:
    - Ollama: http://localhost:11434 (for Ollama tests)
    - API Server: http://localhost:5000 (for API tests)
    - Docker: localhost socket (for Docker tests)

Skip Configuration:
    Tests will automatically skip if required services are unavailable.
    This allows CI/CD pipelines to run safely without all services.
"""


def pytest_configure(config):
    """Register integration test markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (require services)"
    )
    config.addinivalue_line(
        "markers",
        "network: marks tests requiring network connectivity"
    )
    config.addinivalue_line(
        "markers",
        "docker_compose: marks Docker Compose stack tests"
    )
    config.addinivalue_line(
        "markers",
        "filesystem: marks file system operation tests"
    )
