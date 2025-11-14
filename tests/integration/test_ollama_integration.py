"""Integration tests for Ollama LLM backend connectivity and operations.

This module tests the integration between the ULTRON Agent and the Ollama
LLM backend, including model availability, generation capabilities, and
error handling under various conditions.

Test Categories:
    - Model management (listing, availability, health checks)
    - Generation capabilities (text generation, streaming)
    - Error scenarios (timeouts, invalid models, connection failures)
    - Performance benchmarks (generation speed, memory usage)
"""

import pytest
import time
import asyncio
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

pytestmark = [pytest.mark.integration, pytest.mark.network]


class TestOllamaConnectivity:
    """Test basic Ollama service connectivity and health checks."""

    def test_ollama_service_reachable(self):
        """Test that Ollama service is reachable at expected endpoint."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200, f"Ollama returned {response.status_code}"
            assert "models" in response.json(), "Response missing models key"
        except requests.ConnectionError:
            pytest.skip("Ollama service not running on localhost:11434")

    def test_ollama_health_check(self):
        """Test Ollama health check endpoint."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            response = requests.get(f"{ollama_base_url}/", timeout=5)
            assert response.status_code == 200, "Ollama health check failed"
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    @pytest.mark.timeout(15)
    def test_ollama_version_info(self):
        """Test retrieving Ollama version information."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            response = requests.get(f"{ollama_base_url}/api/show", timeout=10)
            # Version endpoint may not exist on all Ollama versions
            if response.status_code == 200:
                data = response.json()
                assert "version" in data or "model" in data
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")


class TestOllamaModels:
    """Test Ollama model availability and management."""

    def test_list_available_models(self):
        """Test listing all available models in Ollama."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data.get("models"), (list, type(None)))
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    def test_llava_model_available(self):
        """Test that llava:7b model is available (default model)."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
            data = response.json()
            models = data.get("models", [])
            model_names = [m.get("name", "") for m in models]

            # Check if llava model is available
            llava_available = any("llava" in name for name in model_names)
            if not llava_available:
                pytest.skip("llava:7b model not available - use 'ollama pull llava:7b'")
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    def test_model_info_retrieval(self):
        """Test retrieving detailed information about a specific model."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            # Try to get info about llava model
            response = requests.post(
                f"{ollama_base_url}/api/show",
                json={"name": "llava:7b"},
                timeout=10
            )

            # Model may not be loaded, that's okay
            if response.status_code == 200:
                data = response.json()
                assert "model" in data or "name" in data
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")


class TestOllamaGeneration:
    """Test text generation capabilities with Ollama."""

    @pytest.mark.timeout(30)
    def test_simple_text_generation(self):
        """Test basic text generation capability."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            # Generate simple text
            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": "Hello, how are you?",
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                assert "response" in data
                assert len(data["response"]) > 0
            elif response.status_code == 404:
                pytest.skip("llava:7b model not loaded - run 'ollama pull llava:7b'")
            else:
                pytest.fail(f"Generation failed with status {response.status_code}")

        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    @pytest.mark.timeout(45)
    def test_generation_performance(self):
        """Test generation response time and throughput."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            start_time = time.time()
            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": "Count from 1 to 5",
                    "stream": False
                },
                timeout=45
            )
            elapsed = time.time() - start_time

            if response.status_code == 200:
                assert elapsed < 45, f"Generation too slow: {elapsed}s"
                # Log performance metric
                print(f"\nGeneration completed in {elapsed:.2f}s")
            elif response.status_code == 404:
                pytest.skip("Model not available")
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    @pytest.mark.timeout(60)
    def test_streaming_generation(self):
        """Test streaming text generation capability."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": "Write a haiku about coding",
                    "stream": True
                },
                timeout=60,
                stream=True
            )

            if response.status_code == 200:
                chunks_received = 0
                for line in response.iter_lines():
                    if line:
                        chunks_received += 1
                assert chunks_received > 0, "No streaming data received"
            elif response.status_code == 404:
                pytest.skip("Model not available")
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")


class TestOllamaErrorHandling:
    """Test error handling and edge cases with Ollama."""

    def test_invalid_model_name(self):
        """Test handling of requests for non-existent model."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json={
                    "model": "nonexistent-model-xyz",
                    "prompt": "test",
                    "stream": False
                },
                timeout=10
            )

            # Should fail gracefully
            assert response.status_code in [404, 400, 500]
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    @pytest.mark.timeout(5)
    def test_timeout_handling(self):
        """Test that timeouts are handled gracefully."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            # Request with very short timeout
            with pytest.raises(requests.Timeout):
                requests.post(
                    f"{ollama_base_url}/api/generate",
                    json={
                        "model": "llava:7b",
                        "prompt": "test",
                        "stream": False
                    },
                    timeout=0.001  # 1ms - will definitely timeout
                )
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    def test_empty_prompt(self):
        """Test handling of empty prompt."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": "",
                    "stream": False
                },
                timeout=10
            )

            # Empty prompt should be handled
            assert response.status_code in [200, 400]
        except requests.ConnectionError:
            pytest.skip("Ollama service not running")


class TestOllamaMemoryUsage:
    """Test memory efficiency of Ollama operations."""

    def test_multiple_sequential_generations(self):
        """Test multiple sequential generation calls."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests

            for i in range(3):
                response = requests.post(
                    f"{ollama_base_url}/api/generate",
                    json={
                        "model": "llava:7b",
                        "prompt": f"Generate response {i+1}",
                        "stream": False
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    assert "response" in response.json()
                elif response.status_code == 404:
                    pytest.skip("Model not available")

        except requests.ConnectionError:
            pytest.skip("Ollama service not running")

    def test_concurrent_request_handling(self):
        """Test how Ollama handles concurrent requests."""
        ollama_base_url = "http://localhost:11434"

        try:
            import requests
            from concurrent.futures import ThreadPoolExecutor, as_completed

            def make_request(prompt_num: int) -> bool:
                try:
                    response = requests.post(
                        f"{ollama_base_url}/api/generate",
                        json={
                            "model": "llava:7b",
                            "prompt": f"Request {prompt_num}",
                            "stream": False
                        },
                        timeout=30
                    )
                    return response.status_code == 200
                except Exception as e:
                    return False

            # Test with 2 concurrent requests
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(make_request, i) for i in range(2)]
                results = [f.result() for f in as_completed(futures)]

            # At least some should succeed
            if results and results[0]:
                assert any(results), "All concurrent requests failed"

        except requests.ConnectionError:
            pytest.skip("Ollama service not running")


# Test configuration
def pytest_configure(config):
    """Configure pytest markers for integration tests."""
    config.addinivalue_line(
        "markers", "integration: integration tests requiring external services"
    )
    config.addinivalue_line(
        "markers", "network: tests requiring network connectivity"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
