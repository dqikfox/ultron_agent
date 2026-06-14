"""
ULTRON Agent Security Utilities
Provides XSS prevention, CSRF tokens, rate limiting, and API security
"""

import html
import hmac
import hashlib
import secrets
import re
import time
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass, field
from collections import defaultdict
from utils.ultron_logger import ultron_logger


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests: int = 100
    time_window_s: int = 60
    burst_allowed: bool = True


@dataclass
class SecurityContext:
    """Security context for request validation"""
    session_id: str
    csrf_tokens: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )
    request_history: Dict[str, list] = field(
        default_factory=lambda: defaultdict(list)
    )
    api_signatures: Dict[str, str] = field(default_factory=dict)


class SecurityUtils:
    """
    Security utilities for ULTRON Agent
    Handles XSS prevention, CSRF, rate limiting, and API security
    """

    # Secrets regex patterns for detection
    SECRETS_PATTERNS = {
        'aws_key': r'AKIA[0-9A-Z]{16}',
        'github_token': r'ghp_[A-Za-z0-9_]{36,255}',
        'api_key': r'[Aa]pi[_-]?[Kk]ey[=:\s]*[\'\"]?'
                   r'[A-Za-z0-9\-_]{20,}',
        'slack_token': (
            r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-'
            r'[A-Za-z0-9_-]{24}'
        ),
        'private_key': r'-----BEGIN PRIVATE KEY-----',
        'password': (
            r'[Pp]assword[=:\s]*[\'\"]?[^\s\'\"\n]{8,}'
        ),
    }

    def __init__(
        self, config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.rate_limit_config = RateLimitConfig()
        self.rate_limit_tracker: Dict[str, list] = defaultdict(list)
        self.csrf_context = SecurityContext(
            session_id=self._generate_session_id()
        )
        self.algorithm = 'HS256'

    @staticmethod
    def prevent_xss(user_input: str) -> str:
        """
        Prevent XSS attacks by escaping HTML entities

        Args:
            user_input: User-provided input

        Returns:
            HTML-escaped string safe for rendering
        """
        if not isinstance(user_input, str):
            return str(user_input)

        return html.escape(user_input, quote=True)

    @staticmethod
    def sanitize_html(content: str) -> str:
        """
        Remove potentially dangerous HTML/script tags

        Args:
            content: HTML content to sanitize

        Returns:
            Sanitized content
        """
        # Remove script tags and content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Remove on* event handlers
        content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)

        # Remove javascript: protocol
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)

        return content

    def generate_csrf_token(
        self, user_id: Optional[str] = None
    ) -> str:
        """
        Generate CSRF token for session

        Args:
            user_id: Optional user identifier

        Returns:
            Secure random CSRF token
        """
        token = secrets.token_urlsafe(32)

        token_data = {
            'token': token,
            'created_at': datetime.now().isoformat(),
            'user_id': user_id,
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }

        self.csrf_context.csrf_tokens[token] = token_data
        ultron_logger.log_info("security_utils", f"CSRF token generated for user: {user_id}")

        return token

    def validate_csrf_token(
        self, token: str, user_id: Optional[str] = None
    ) -> bool:
        """
        Validate CSRF token

        Args:
            token: Token to validate
            user_id: Optional user identifier for verification

        Returns:
            True if token is valid
        """
        if token not in self.csrf_context.csrf_tokens:
            ultron_logger.log_error("security_utils", "CSRF token not found")
            return False

        token_data = self.csrf_context.csrf_tokens[token]

        # Check expiration
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() > expires_at:
            ultron_logger.log_error("security_utils", "CSRF token expired")
            del self.csrf_context.csrf_tokens[token]
            return False

        # Check user if provided
        if user_id and token_data.get('user_id') != user_id:
            ultron_logger.log_error("security_utils", f"CSRF token user mismatch: {user_id}")
            return False

        # Remove used token
        del self.csrf_context.csrf_tokens[token]
        return True

    def rate_limit_decorator(
        self, config: Optional[RateLimitConfig] = None
    ) -> Callable:
        """
        Decorator for rate limiting functions

        Args:
            config: Rate limit configuration

        Returns:
            Decorated function with rate limiting
        """
        config = config or self.rate_limit_config

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                client_id = kwargs.get('client_id', 'default')
                current_time = time.time()

                # Clean old requests outside time window
                cutoff_time = current_time - config.time_window_s
                self.rate_limit_tracker[client_id] = [
                    req_time for req_time in self.rate_limit_tracker[client_id]
                    if req_time > cutoff_time
                ]

                # Check rate limit
                request_count = len(self.rate_limit_tracker[client_id])

                if request_count >= config.max_requests:
                    ultron_logger.log_error("security_utils",
                                          f"Rate limit exceeded for {client_id}: {request_count}/{config.max_requests}")
                    raise RuntimeError(f"Rate limit exceeded: {config.max_requests} requests per {config.time_window_s}s")

                # Record request
                self.rate_limit_tracker[client_id].append(current_time)

                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def sign_request(
        data: str, secret: str, algorithm: str = 'sha256'
    ) -> str:
        """
        Sign API request using HMAC

        Args:
            data: Data to sign
            secret: Secret key
            algorithm: Hash algorithm (sha256, sha512, etc.)

        Returns:
            Hex-encoded signature
        """
        signature = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            algorithm
        )
        return signature.hexdigest()

    @staticmethod
    def verify_signature(data: str, signature: str, secret: str, algorithm: str = 'sha256') -> bool:
        """
        Verify HMAC signature

        Args:
            data: Original data
            signature: Signature to verify
            secret: Secret key
            algorithm: Hash algorithm

        Returns:
            True if signature is valid
        """
        expected_signature = SecurityUtils.sign_request(data, secret, algorithm)
        return hmac.compare_digest(signature, expected_signature)

    def detect_secrets(
        self, content: str, patterns: Optional[List[str]] = None
    ) -> Dict[str, list]:
        """
        Scan content for potential secrets (API keys, tokens, etc.)

        Args:
            content: Content to scan
            patterns: Optional list of pattern names to check (default: all)

        Returns:
            Dictionary mapping pattern names to found matches
        """
        findings = {}
        patterns_to_check = patterns or list(self.SECRETS_PATTERNS.keys())

        for pattern_name in patterns_to_check:
            if pattern_name not in self.SECRETS_PATTERNS:
                continue

            pattern = self.SECRETS_PATTERNS[pattern_name]
            matches = re.findall(pattern, content)

            if matches:
                findings[pattern_name] = matches
                ultron_logger.log_error("security_utils",
                                      f"Potential secret detected: {pattern_name} - {len(matches)} match(es)")

        return findings

    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_hex(16)

    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.csrf_context.session_id

    def reset_session(self) -> None:
        """Reset security context for new session"""
        self.csrf_context = SecurityContext(session_id=self._generate_session_id())
        self.rate_limit_tracker.clear()
        ultron_logger.log_info("security_utils", "Security context reset for new session")


# Module-level convenience functions
_security_utils_instance = SecurityUtils()


def prevent_xss(user_input: str) -> str:
    """Convenience function for XSS prevention"""
    return SecurityUtils.prevent_xss(user_input)


def sanitize_html(content: str) -> str:
    """Convenience function for HTML sanitization"""
    return SecurityUtils.sanitize_html(content)


def generate_csrf_token(user_id: Optional[str] = None) -> str:
    """Convenience function for CSRF token generation"""
    return _security_utils_instance.generate_csrf_token(user_id)


def validate_csrf_token(
    token: str, user_id: Optional[str] = None
) -> bool:
    """Convenience function for CSRF token validation"""
    return _security_utils_instance.validate_csrf_token(token, user_id)


def sign_request(data: str, secret: str) -> str:
    """Convenience function for request signing"""
    return SecurityUtils.sign_request(data, secret)


def verify_signature(data: str, signature: str, secret: str) -> bool:
    """Convenience function for signature verification"""
    return SecurityUtils.verify_signature(data, signature, secret)


def detect_secrets(content: str) -> Dict[str, list]:
    """Convenience function for secrets detection"""
    return _security_utils_instance.detect_secrets(content)
