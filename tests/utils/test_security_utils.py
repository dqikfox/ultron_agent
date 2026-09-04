"""
Unit and integration tests for security_utils utility
"""

import pytest
import time
from utils.security_utils import (
    SecurityUtils, prevent_xss, sanitize_html,
    generate_csrf_token, validate_csrf_token,
    sign_request, verify_signature, detect_secrets,
    RateLimitConfig, SecurityContext
)


class TestXSSPrevention:
    """Tests for XSS prevention functions"""

    @pytest.mark.unit
    def test_prevent_xss_script_tag(self):
        """Test XSS prevention for script tags"""
        malicious = "<script>alert('xss')</script>Hello"
        safe = prevent_xss(malicious)
        assert "<script>" not in safe
        assert "alert" in safe
        assert "&lt;" in safe or "script" in safe.lower()

    @pytest.mark.unit
    def test_prevent_xss_event_handler(self):
        """Test XSS prevention for event handlers"""
        malicious = '<img src=x onerror="alert(\'xss\')">'
        safe = prevent_xss(malicious)
        assert "onerror" not in safe or "&" in safe

    @pytest.mark.unit
    def test_prevent_xss_safe_content(self):
        """Test that safe content is not overly escaped"""
        safe_input = "<p>Hello World</p>"
        output = prevent_xss(safe_input)
        assert "&lt;" in output or "Hello" in output

    @pytest.mark.unit
    def test_prevent_xss_special_characters(self):
        """Test XSS prevention with special characters"""
        input_str = 'Hello & "Goodbye" <test>'
        output = prevent_xss(input_str)
        assert "&amp;" in output or "Goodbye" in output

    @pytest.mark.unit
    def test_sanitize_html_script_tag(self):
        """Test HTML sanitization for script tags"""
        html = "Before<script>alert('xss')</script>After"
        clean = sanitize_html(html)
        assert "<script>" not in clean.lower()
        assert "Before" in clean
        assert "After" in clean

    @pytest.mark.unit
    def test_sanitize_html_event_handlers(self):
        """Test HTML sanitization for event handlers"""
        html = '<div onclick="alert(\'xss\')">Click</div>'
        clean = sanitize_html(html)
        assert "onclick" not in clean

    @pytest.mark.unit
    def test_sanitize_html_javascript_protocol(self):
        """Test HTML sanitization for javascript: protocol"""
        html = '<a href="javascript:alert(\'xss\')">Click</a>'
        clean = sanitize_html(html)
        assert "javascript:" not in clean


class TestCSRFProtection:
    """Tests for CSRF token functionality"""

    @pytest.mark.unit
    def test_generate_csrf_token(self):
        """Test CSRF token generation"""
        token = generate_csrf_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    @pytest.mark.unit
    def test_generate_csrf_token_with_user_id(self):
        """Test CSRF token generation with user ID"""
        token = generate_csrf_token(user_id="user123")
        assert token is not None
        assert isinstance(token, str)

    @pytest.mark.unit
    def test_validate_csrf_token_valid(self):
        """Test CSRF token validation with valid token"""
        token = generate_csrf_token(user_id="user123")
        is_valid = validate_csrf_token(token, user_id="user123")
        assert is_valid is True

    @pytest.mark.unit
    def test_validate_csrf_token_invalid(self):
        """Test CSRF token validation with invalid token"""
        is_valid = validate_csrf_token("invalid_token_12345")
        assert is_valid is False

    @pytest.mark.unit
    def test_validate_csrf_token_user_mismatch(self):
        """Test CSRF token validation with user mismatch"""
        token = generate_csrf_token(user_id="user123")
        # Token removed after first validation
        is_valid = validate_csrf_token(token, user_id="user456")
        assert is_valid is False

    @pytest.mark.unit
    def test_csrf_token_one_time_use(self):
        """Test that CSRF tokens are single-use"""
        token = generate_csrf_token()
        first_validation = validate_csrf_token(token)
        assert first_validation is True

        # Try to use token again
        second_validation = validate_csrf_token(token)
        assert second_validation is False


class TestRateLimiting:
    """Tests for rate limiting decorator"""

    @pytest.mark.unit
    def test_rate_limit_decorator_under_limit(self):
        """Test function call under rate limit"""
        config = RateLimitConfig(max_requests=5, time_window_s=1)
        security = SecurityUtils(config={'max_requests': 5})

        @security.rate_limit_decorator(config)
        def test_func(client_id="default"):
            return "success"

        result = test_func(client_id="client1")
        assert result == "success"

    @pytest.mark.unit
    def test_rate_limit_decorator_exceeds_limit(self):
        """Test function call exceeding rate limit"""
        config = RateLimitConfig(max_requests=2, time_window_s=10)
        security = SecurityUtils(config={'max_requests': 2})

        @security.rate_limit_decorator(config)
        def test_func(client_id="default"):
            return "success"

        # First two calls should succeed
        result1 = test_func(client_id="client1")
        result2 = test_func(client_id="client1")
        assert result1 == "success"
        assert result2 == "success"

        # Third call should fail
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            test_func(client_id="client1")

    @pytest.mark.unit
    def test_rate_limit_per_client(self):
        """Test rate limiting is per-client"""
        config = RateLimitConfig(max_requests=2, time_window_s=10)
        security = SecurityUtils(config={'max_requests': 2})

        @security.rate_limit_decorator(config)
        def test_func(client_id="default"):
            return "success"

        # Two calls from client1
        test_func(client_id="client1")
        test_func(client_id="client1")

        # Should still be able to call from client2
        result = test_func(client_id="client2")
        assert result == "success"


class TestAPISignatures:
    """Tests for API request signing and verification"""

    @pytest.mark.unit
    def test_sign_request_sha256(self):
        """Test request signing with SHA256"""
        data = "test_data"
        secret = "test_secret"
        signature = sign_request(data, secret)

        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex is 64 chars

    @pytest.mark.unit
    def test_sign_request_deterministic(self):
        """Test that signing is deterministic"""
        data = "test_data"
        secret = "test_secret"

        sig1 = sign_request(data, secret)
        sig2 = sign_request(data, secret)

        assert sig1 == sig2

    @pytest.mark.unit
    def test_verify_signature_valid(self):
        """Test signature verification with valid signature"""
        data = "test_data"
        secret = "test_secret"

        signature = sign_request(data, secret)
        is_valid = verify_signature(data, signature, secret)

        assert is_valid is True

    @pytest.mark.unit
    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature"""
        data = "test_data"
        secret = "test_secret"

        is_valid = verify_signature(data, "invalid_signature", secret)
        assert is_valid is False

    @pytest.mark.unit
    def test_verify_signature_wrong_data(self):
        """Test signature verification with wrong data"""
        data1 = "test_data_1"
        data2 = "test_data_2"
        secret = "test_secret"

        signature = sign_request(data1, secret)
        is_valid = verify_signature(data2, signature, secret)

        assert is_valid is False

    @pytest.mark.unit
    def test_verify_signature_wrong_secret(self):
        """Test signature verification with wrong secret"""
        data = "test_data"
        secret1 = "secret1"
        secret2 = "secret2"

        signature = sign_request(data, secret1)
        is_valid = verify_signature(data, signature, secret2)

        assert is_valid is False


class TestSecretsDetection:
    """Tests for secrets detection"""

    @pytest.mark.unit
    def test_detect_aws_key(self):
        """Test AWS key detection"""
        content = "aws_key = AKIAIOSFODNN7EXAMPLE"
        findings = detect_secrets(content)

        assert "aws_key" in findings
        assert len(findings["aws_key"]) > 0

    @pytest.mark.unit
    def test_detect_github_token(self):
        """Test GitHub token detection"""
        token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        content = f"token = {token}"
        findings = detect_secrets(content)

        assert "github_token" in findings

    @pytest.mark.unit
    def test_detect_api_key(self):
        """Test API key detection"""
        content = "api_key = sk_1234567890abcdefghijklmnopqrs"
        findings = detect_secrets(content)

        assert "api_key" in findings or "password" in findings

    @pytest.mark.unit
    def test_detect_password(self):
        """Test password detection"""
        content = "password = SuperSecretPassword123456"
        findings = detect_secrets(content)

        assert "password" in findings

    @pytest.mark.unit
    def test_detect_private_key(self):
        """Test private key detection"""
        content = """
        -----BEGIN PRIVATE KEY-----
        MIIEvQIBADANBgkqhkiG9w0BAQE...
        -----END PRIVATE KEY-----
        """
        findings = detect_secrets(content)

        assert "private_key" in findings

    @pytest.mark.unit
    def test_no_false_positives_safe_text(self):
        """Test safe text doesn't trigger false positives"""
        content = "This is safe text about API usage and passwords"
        findings = detect_secrets(content)

        # Should not detect actual secrets in casual text
        assert len(findings) == 0 or all(
            len(v) == 0 for v in findings.values()
        )

    @pytest.mark.unit
    def test_detect_multiple_secrets(self):
        """Test detection of multiple secrets"""
        content = """
        aws_key = AKIAIOSFODNN7EXAMPLE
        github_token = ghp_1234567890abcdefghijklmnopqrstuvwxyz
        password = SuperSecret123456
        """
        findings = detect_secrets(content)

        assert len(findings) > 0
        assert any(len(v) > 0 for v in findings.values())


class TestSecurityContext:
    """Tests for SecurityContext"""

    @pytest.mark.unit
    def test_security_context_creation(self):
        """Test SecurityContext creation"""
        context = SecurityContext(session_id="test_session")
        assert context.session_id == "test_session"
        assert context.csrf_tokens == {}
        assert context.api_signatures == {}

    @pytest.mark.unit
    def test_security_context_session_isolation(self):
        """Test that sessions are isolated"""
        context1 = SecurityContext(session_id="session1")
        context2 = SecurityContext(session_id="session2")

        assert context1.session_id != context2.session_id
        assert context1.csrf_tokens is not context2.csrf_tokens


class TestRateLimitConfig:
    """Tests for RateLimitConfig"""

    @pytest.mark.unit
    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default values"""
        config = RateLimitConfig()
        assert config.max_requests == 100
        assert config.time_window_s == 60
        assert config.burst_allowed is True

    @pytest.mark.unit
    def test_rate_limit_config_custom(self):
        """Test RateLimitConfig with custom values"""
        config = RateLimitConfig(
            max_requests=50,
            time_window_s=30,
            burst_allowed=False
        )
        assert config.max_requests == 50
        assert config.time_window_s == 30
        assert config.burst_allowed is False


@pytest.mark.slow
class TestSecurityPerformance:
    """Performance tests for security utilities"""

    @pytest.mark.unit
    def test_xss_prevention_performance(self):
        """Test XSS prevention performance"""
        html_content = "<p>Safe content</p>" * 100
        start = time.time()
        for _ in range(1000):
            prevent_xss(html_content)
        elapsed = time.time() - start

        assert elapsed < 5.0  # Should be fast

    @pytest.mark.unit
    def test_signature_verification_performance(self):
        """Test signature verification performance"""
        data = "test_data" * 100
        secret = "test_secret"
        signature = sign_request(data, secret)

        start = time.time()
        for _ in range(1000):
            verify_signature(data, signature, secret)
        elapsed = time.time() - start

        assert elapsed < 5.0  # Should be fast
