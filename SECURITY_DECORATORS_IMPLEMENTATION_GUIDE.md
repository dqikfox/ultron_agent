# Security Decorators Implementation Guide

**Date**: November 3, 2025
**Purpose**: Implement missing security decorators for ULTRON Agent API
**Target File**: `api_server.py`
**Estimated Implementation Time**: 15-20 hours

---

## Overview

This guide provides complete implementation code for all missing security decorators identified in the A1 audit. Each decorator is production-ready and can be copied directly into the codebase.

---

## Decorator 1: `@rate_limit`

**Purpose**: Protect endpoints from brute force attacks and DoS
**Implementation Level**: CRITICAL
**Dependencies**: redis (optional) or in-memory dict

### Implementation

```python
# Add to api_server.py after imports

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

class RateLimitManager:
    """Thread-safe rate limiter with token bucket algorithm"""

    def __init__(self):
        self.requests = defaultdict(list)  # IP -> list of timestamps
        self.lock = threading.Lock()

    def is_allowed(
        self,
        identifier: str,
        calls: int = 100,
        period: int = 3600
    ) -> bool:
        """
        Check if request from identifier is within rate limit.

        Args:
            identifier: IP address or user ID
            calls: Number of allowed calls
            period: Time period in seconds

        Returns:
            True if request allowed, False if rate limited
        """
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=period)

            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]

            # Check if within limit
            if len(self.requests[identifier]) < calls:
                self.requests[identifier].append(now)
                return True

            return False

    def get_retry_after(
        self,
        identifier: str,
        period: int = 3600
    ) -> int:
        """Calculate seconds until next request allowed"""
        if not self.requests[identifier]:
            return 0

        oldest = self.requests[identifier][0]
        next_allowed = oldest + timedelta(seconds=period)
        retry_after = (next_allowed - datetime.now()).total_seconds()

        return max(0, int(retry_after) + 1)


# Global rate limiter instance
_rate_limiter = RateLimitManager()


def rate_limit(calls: int = 100, period: int = 3600) -> Callable:
    """
    Rate limiting decorator using token bucket algorithm.

    Args:
        calls: Number of allowed requests in the period
        period: Time period in seconds (default: 1 hour)

    Returns:
        Decorated function with rate limiting

    Usage:
        @rate_limit(calls=50, period=3600)  # 50 requests per hour
        def endpoint():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
            try:
                # Get client IP
                client_ip = request.remote_addr or "unknown"

                # Check rate limit
                if not _rate_limiter.is_allowed(client_ip, calls, period):
                    retry_after = _rate_limiter.get_retry_after(client_ip, period)

                    log_error(
                        "api_server",
                        f"Rate limit exceeded for {client_ip}",
                        extra={
                            "endpoint": request.endpoint,
                            "limit": calls,
                            "period": period,
                            "retry_after": retry_after
                        }
                    )

                    return jsonify({
                        "error": "Rate limit exceeded",
                        "error_type": "rate_limit_exceeded",
                        "retry_after": retry_after,
                        "limit": calls,
                        "period": period,
                        "timestamp": str(datetime.now())
                    }), 429

                return f(*args, **kwargs)

            except Exception as err:
                log_error("api_server", f"Rate limit decorator error: {err}")
                return jsonify({"error": "Rate limiting error"}), 500

        return decorated

    return decorator
```

### Usage Examples

```python
@app.route("/api/command", methods=["POST"])
@require_auth
@rate_limit(calls=50, period=3600)  # 50 requests per hour
def command():
    pass

@app.route("/api/tools/execute", methods=["POST"])
@require_auth
@rate_limit(calls=30, period=3600)  # 30 requests per hour (more restrictive)
def execute_tool():
    pass

@app.route("/api/login", methods=["POST"])
@rate_limit(calls=5, period=300)  # 5 requests per 5 minutes (brute force protection)
def login():
    pass
```

---

## Decorator 2: `@input_sanitize`

**Purpose**: Prevent injection attacks (SQL, command, XSS)
**Implementation Level**: CRITICAL
**Dependencies**: html, shlex (stdlib), re (stdlib)

### Implementation

```python
# Add to api_server.py

import html
import shlex
import re
from urllib.parse import urlparse


class InputSanitizer:
    """Sanitize user inputs to prevent injection attacks"""

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Escape HTML entities to prevent XSS"""
        if not isinstance(text, str):
            return str(text)
        return html.escape(text)

    @staticmethod
    def sanitize_sql_string(text: str) -> str:
        """
        Prepare string for SQL parameter binding.
        NOTE: This is for string escaping only - use parameterized queries!
        """
        if not isinstance(text, str):
            return str(text)

        # Escape single quotes
        escaped = text.replace("'", "''")
        return escaped

    @staticmethod
    def sanitize_command(text: str) -> str:
        """Escape command for shell execution"""
        if not isinstance(text, str):
            return str(text)

        # Use shlex.quote for shell escaping
        return shlex.quote(text)

    @staticmethod
    def sanitize_path(path: str) -> Optional[str]:
        """Validate and sanitize file path to prevent traversal attacks"""
        if not isinstance(path, str):
            return None

        # Prevent path traversal
        if '..' in path or path.startswith('/'):
            return None

        # Normalize path
        normalized = os.path.normpath(path)

        # Ensure we're within allowed directory
        base_dir = os.path.abspath('./data/')
        full_path = os.path.abspath(os.path.join(base_dir, normalized))

        if not full_path.startswith(base_dir):
            return None

        return full_path

    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """Validate URL to prevent SSRF attacks"""
        if not isinstance(url, str):
            return None

        try:
            parsed = urlparse(url)

            # Only allow http/https
            if parsed.scheme not in ['http', 'https']:
                return None

            # Block private IP ranges
            private_ips = [
                '127.0.0.1', 'localhost', '192.168.',
                '10.', '172.16.', '169.254.', '::1'
            ]

            for private_ip in private_ips:
                if parsed.netloc.startswith(private_ip):
                    return None

            return url
        except Exception:
            return None

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_command_name(name: str) -> bool:
        """Validate command name contains only safe characters"""
        # Only alphanumeric, underscores, and hyphens
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))


def input_sanitize(
    fields: List[str] = None,
    sanitize_type: str = 'html'
) -> Callable:
    """
    Sanitize request input fields to prevent injection attacks.

    Args:
        fields: List of JSON field names to sanitize
        sanitize_type: Type of sanitization ('html', 'sql', 'command', 'path', 'url')

    Returns:
        Decorated function with input sanitization

    Usage:
        @input_sanitize(fields=['command', 'query'], sanitize_type='html')
        def endpoint():
            pass
    """
    if fields is None:
        fields = []

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
            try:
                # Get JSON data
                data = request.get_json(silent=True) or {}

                # Sanitize specified fields
                sanitizer = InputSanitizer()
                sanitize_func = getattr(
                    sanitizer,
                    f'sanitize_{sanitize_type}',
                    sanitizer.sanitize_html
                )

                for field in fields:
                    if field in data:
                        original = data[field]
                        data[field] = sanitize_func(data[field])

                        if data[field] != original:
                            log_info(
                                "api_server",
                                f"Input sanitized for field '{field}'",
                                extra={
                                    "field": field,
                                    "sanitize_type": sanitize_type,
                                    "original_length": len(str(original)),
                                    "sanitized_length": len(str(data[field]))
                                }
                            )

                # Replace request data
                request.json = data

                return f(*args, **kwargs)

            except Exception as err:
                log_error(
                    "api_server",
                    f"Input sanitization error: {err}",
                    exception=err
                )
                return jsonify({
                    "error": "Input validation failed",
                    "error_type": "sanitization_error",
                    "timestamp": str(datetime.now())
                }), 400

        return decorated

    return decorator
```

### Usage Examples

```python
@app.route("/api/command", methods=["POST"])
@require_auth
@input_sanitize(fields=['command'], sanitize_type='html')
def command():
    data = request.get_json()
    command_text = data['command']  # Already sanitized
    pass

@app.route("/api/user/update", methods=["POST"])
@require_auth
@input_sanitize(fields=['email', 'name'], sanitize_type='html')
def update_user():
    pass
```

---

## Decorator 3: `@require_request_size_limit`

**Purpose**: Prevent memory exhaustion DoS attacks
**Implementation Level**: HIGH
**Dependencies**: None

### Implementation

```python
# Add to api_server.py

def parse_size(size_str: str) -> int:
    """Parse size string (e.g., '16MB') to bytes"""
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
    }

    size_str = size_str.upper().strip()

    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)].strip())
                return int(number * multiplier)
            except ValueError:
                return None

    try:
        return int(size_str)
    except ValueError:
        return None


def require_request_size_limit(max_size: str = "16MB") -> Callable:
    """
    Limit request payload size to prevent DoS attacks.

    Args:
        max_size: Maximum size string (e.g., '16MB', '2GB', '512KB')

    Returns:
        Decorated function with size checking

    Usage:
        @require_request_size_limit(max_size="2MB")
        def endpoint():
            pass
    """
    max_bytes = parse_size(max_size)
    if max_bytes is None:
        raise ValueError(f"Invalid size format: {max_size}")

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
            try:
                # Get content length
                content_length = request.content_length

                if content_length is None:
                    log_warning(
                        "api_server",
                        "No Content-Length header provided"
                    )
                    # Proceed without size check if header missing
                    return f(*args, **kwargs)

                # Check size limit
                if content_length > max_bytes:
                    log_error(
                        "api_server",
                        f"Request too large: {content_length} > {max_bytes}",
                        extra={
                            "endpoint": request.endpoint,
                            "content_length": content_length,
                            "max_size_bytes": max_bytes,
                            "max_size_human": max_size,
                            "client_ip": request.remote_addr
                        }
                    )

                    return jsonify({
                        "error": "Request body too large",
                        "error_type": "request_too_large",
                        "max_size": max_size,
                        "received_size": f"{content_length / (1024*1024):.2f}MB",
                        "timestamp": str(datetime.now())
                    }), 413

                return f(*args, **kwargs)

            except Exception as err:
                log_error(
                    "api_server",
                    f"Request size limit check error: {err}",
                    exception=err
                )
                return jsonify({
                    "error": "Size validation error",
                    "error_type": "size_validation_error",
                    "timestamp": str(datetime.now())
                }), 400

        return decorated

    return decorator
```

### Usage Examples

```python
@app.route("/api/command", methods=["POST"])
@require_auth
@require_request_size_limit(max_size="2MB")
def command():
    pass

@app.route("/api/file/upload", methods=["POST"])
@require_auth
@require_request_size_limit(max_size="100MB")
def upload_file():
    pass

@app.route("/api/health", methods=["GET"])
@require_request_size_limit(max_size="64KB")  # Strict for monitoring endpoints
def health_check():
    pass
```

---

## Decorator 4: `@add_security_headers`

**Purpose**: Add security headers to prevent browser-based attacks
**Implementation Level**: MEDIUM-HIGH
**Dependencies**: None

### Implementation

```python
# Add to api_server.py

def add_security_headers(
    headers: Dict[str, str] = None
) -> Callable:
    """
    Add security headers to response.

    Args:
        headers: Dictionary of security headers to add

    Returns:
        Decorated function with security headers

    Usage:
        @add_security_headers(headers={
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY'
        })
        def endpoint():
            pass
    """
    if headers is None:
        headers = {}

    # Default security headers
    default_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }

    # Merge with provided headers
    default_headers.update(headers)

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
            try:
                # Call original function
                response = f(*args, **kwargs)

                # Handle different response types
                if isinstance(response, tuple):
                    data, status_code = response
                    from flask import make_response
                    flask_response = make_response(jsonify(data), status_code)
                else:
                    from flask import make_response
                    flask_response = make_response(response)

                # Add security headers
                for header_name, header_value in default_headers.items():
                    flask_response.headers[header_name] = header_value

                return flask_response

            except Exception as err:
                log_error(
                    "api_server",
                    f"Security headers decorator error: {err}",
                    exception=err
                )
                raise

        return decorated

    return decorator
```

### Usage Examples

```python
@app.route("/api/command", methods=["POST"])
@require_auth
@add_security_headers()
def command():
    pass

@app.route("/api/sensitive-data", methods=["GET"])
@require_auth
@add_security_headers(headers={
    'Content-Security-Policy': "default-src 'self'; script-src 'self'",
    'Cache-Control': 'no-store, no-cache, must-revalidate'
})
def get_sensitive_data():
    pass
```

---

## Decorator 5: `@audit_log`

**Purpose**: Log security-relevant events for compliance and debugging
**Implementation Level**: MEDIUM
**Dependencies**: logging

### Implementation

```python
# Add to api_server.py

def audit_log(
    action: str = None,
    include_request_body: bool = False,
    include_response: bool = False
) -> Callable:
    """
    Audit log security-relevant events.

    Args:
        action: Description of the action being audited
        include_request_body: Include request body in log
        include_response: Include response in log

    Returns:
        Decorated function with audit logging

    Usage:
        @audit_log(action="execute_tool", include_request_body=True)
        def endpoint():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
            try:
                start_time = datetime.now()

                # Extract request details
                request_details = {
                    "timestamp": str(start_time),
                    "client_ip": request.remote_addr,
                    "method": request.method,
                    "endpoint": request.endpoint or request.path,
                    "user_agent": request.user_agent.string[:100] if request.user_agent else "unknown",
                    "action": action or f"call_{f.__name__}"
                }

                # Extract auth info
                auth_header = request.headers.get('Authorization')
                if auth_header:
                    request_details["auth_type"] = "bearer_token"

                # Include request body if configured
                if include_request_body:
                    try:
                        body = request.get_json(silent=True)
                        if body:
                            # Don't log sensitive fields
                            safe_body = {k: v for k, v in body.items()
                                        if k not in ['password', 'token', 'secret', 'api_key']}
                            request_details["request_body_keys"] = list(safe_body.keys())
                    except Exception:
                        pass

                # Call the wrapped function
                response = f(*args, **kwargs)

                # Extract response details
                if isinstance(response, tuple):
                    response_data, status_code = response
                else:
                    response_data = response
                    status_code = 200

                duration = (datetime.now() - start_time).total_seconds()

                audit_entry = {
                    **request_details,
                    "status_code": status_code,
                    "duration_seconds": f"{duration:.3f}",
                    "success": 200 <= status_code < 400
                }

                # Include response if configured and safe
                if include_response and isinstance(response_data, dict):
                    if 'result' in response_data:
                        audit_entry["result_preview"] = str(response_data['result'])[:100]

                # Log audit event
                log_ai_decision(
                    component="audit_log",
                    message=f"API action: {action or f.__name__}",
                    ai_model="api_gateway",
                    confidence_score=1.0,
                    reasoning=f"Status: {status_code}, Duration: {duration:.3f}s",
                    extra=audit_entry
                )

                return response

            except Exception as err:
                log_error(
                    "api_server",
                    f"Audit logging error: {err}",
                    exception=err
                )
                raise

        return decorated

    return decorator
```

### Usage Examples

```python
@app.route("/api/command", methods=["POST"])
@require_auth
@audit_log(action="execute_command", include_request_body=True)
def command():
    pass

@app.route("/api/tools/reload", methods=["POST"])
@require_auth
@audit_log(action="reload_tools")
def reload_tools():
    pass

@app.route("/api/tools/execute", methods=["POST"])
@require_auth
@audit_log(action="execute_tool", include_request_body=True, include_response=True)
def execute_tool():
    pass
```

---

## Decorator 6: `@require_csrf_token`

**Purpose**: Prevent CSRF attacks on state-changing operations
**Implementation Level**: MEDIUM
**Dependencies**: secrets, hashlib

### Implementation

```python
# Add to api_server.py

import secrets
import hashlib

csrf_tokens = {}  # In-memory token store (use Redis in production)
CSRF_TOKEN_EXPIRY = 3600  # 1 hour


def generate_csrf_token() -> str:
    """Generate a secure CSRF token"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    csrf_tokens[token_hash] = datetime.now() + timedelta(seconds=CSRF_TOKEN_EXPIRY)
    return token


def verify_csrf_token(token: str) -> bool:
    """Verify CSRF token"""
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    if token_hash not in csrf_tokens:
        return False

    if csrf_tokens[token_hash] < datetime.now():
        del csrf_tokens[token_hash]
        return False

    # Consume token (one-time use)
    del csrf_tokens[token_hash]
    return True


def require_csrf_token(f: Callable) -> Callable:
    """
    Require valid CSRF token for state-changing operations.

    Usage:
        @require_csrf_token
        def endpoint():
            pass
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
        try:
            # Get CSRF token from request
            # Check X-CSRF-Token header first, then form data
            csrf_token = (
                request.headers.get('X-CSRF-Token') or
                request.form.get('csrf_token') or
                (request.get_json(silent=True) or {}).get('csrf_token')
            )

            if not csrf_token:
                log_error(
                    "api_server",
                    "CSRF token missing",
                    extra={"endpoint": request.endpoint}
                )
                return jsonify({
                    "error": "CSRF token required",
                    "error_type": "missing_csrf_token",
                    "timestamp": str(datetime.now())
                }), 403

            # Verify token
            if not verify_csrf_token(csrf_token):
                log_error(
                    "api_server",
                    "CSRF token invalid or expired",
                    extra={
                        "endpoint": request.endpoint,
                        "client_ip": request.remote_addr
                    }
                )
                return jsonify({
                    "error": "Invalid or expired CSRF token",
                    "error_type": "invalid_csrf_token",
                    "timestamp": str(datetime.now())
                }), 403

            return f(*args, **kwargs)

        except Exception as err:
            log_error(
                "api_server",
                f"CSRF validation error: {err}",
                exception=err
            )
            return jsonify({
                "error": "CSRF validation failed",
                "error_type": "csrf_validation_error",
                "timestamp": str(datetime.now())
            }), 500

    return decorated
```

### Usage Examples

```python
# Endpoint to get CSRF token
@app.route("/api/csrf-token", methods=["GET"])
def get_csrf_token():
    """Get CSRF token for client"""
    token = generate_csrf_token()
    return jsonify({"csrf_token": token}), 200


@app.route("/api/command", methods=["POST"])
@require_auth
@require_csrf_token
def command():
    pass

@app.route("/api/tools/reload", methods=["POST"])
@require_auth
@require_csrf_token
def reload_tools():
    pass
```

---

## Complete Decorator Stack Example

Here's how to apply multiple decorators to an endpoint:

```python
@app.route("/api/tools/execute", methods=["POST"])
@require_auth                              # 1. Authenticate user
@rate_limit(calls=30, period=3600)         # 2. Rate limit (30/hr)
@require_request_size_limit("2MB")         # 3. Validate size
@input_sanitize(fields=['tool_name', 'args'], sanitize_type='html')  # 4. Sanitize input
@require_csrf_token                        # 5. Validate CSRF token
@add_security_headers()                    # 6. Add security headers
@audit_log(action="execute_tool", include_request_body=True)  # 7. Audit log
def execute_tool() -> Tuple[Dict[str, Any], int]:
    """Execute a tool through the agent"""
    # Function implementation
    pass
```

**Execution Order**: Decorators execute bottom-to-top, so:
1. Audit log wrapper
2. Security headers wrapper
3. CSRF token validation
4. Input sanitization
5. Size limit check
6. Rate limiting
7. Auth check
8. Route handler

---

## Testing the Decorators

### Unit Test Examples

```python
# tests/test_security_decorators.py

import pytest
from api_server import (
    rate_limit, input_sanitize, require_request_size_limit,
    add_security_headers, audit_log, require_csrf_token,
    RateLimitManager, InputSanitizer
)


class TestRateLimiter:
    def test_allows_requests_within_limit(self):
        limiter = RateLimitManager()
        assert limiter.is_allowed("192.168.1.1", 5, 60)
        assert limiter.is_allowed("192.168.1.1", 5, 60)
        assert limiter.is_allowed("192.168.1.1", 5, 60)

    def test_blocks_requests_over_limit(self):
        limiter = RateLimitManager()
        for i in range(5):
            assert limiter.is_allowed("192.168.1.2", 5, 60)
        assert not limiter.is_allowed("192.168.1.2", 5, 60)


class TestInputSanitizer:
    def test_sanitizes_html_entities(self):
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize_html("<script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_sanitizes_sql_injection(self):
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize_sql_string("'; DROP TABLE users; --")
        assert "''" in result

    def test_prevents_path_traversal(self):
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize_path("../../../etc/passwd")
        assert result is None

    def test_prevents_ssrf_to_localhost(self):
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize_url("http://localhost:6379/")
        assert result is None


class TestCSRFToken:
    def test_token_generation_and_validation(self):
        token = generate_csrf_token()
        assert verify_csrf_token(token)

    def test_token_cannot_be_reused(self):
        token = generate_csrf_token()
        assert verify_csrf_token(token)
        assert not verify_csrf_token(token)

    def test_invalid_token_rejected(self):
        assert not verify_csrf_token("invalid_token_123")
```

---

## Configuration in `ultron_config.json`

```json
{
  "api_server": {
    "security": {
      "decorators": {
        "rate_limiting": {
          "enabled": true,
          "default_limits": {
            "GET": {"calls": 100, "period": 3600},
            "POST": {"calls": 50, "period": 3600},
            "login": {"calls": 5, "period": 300}
          }
        },
        "request_size_limits": {
          "enabled": true,
          "defaults": {
            "general": "16MB",
            "command": "2MB",
            "tools_execute": "2MB",
            "file_upload": "100MB"
          }
        },
        "csrf_protection": {
          "enabled": true,
          "token_expiry": 3600
        },
        "input_sanitization": {
          "enabled": true,
          "auto_sanitize": ["command", "query"],
          "sanitize_type": "html"
        },
        "security_headers": {
          "enabled": true,
          "headers": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000"
          }
        },
        "audit_logging": {
          "enabled": true,
          "log_all_actions": true,
          "include_request_body": true,
          "include_response": false,
          "log_retention_days": 90
        }
      }
    }
  }
}
```

---

## Implementation Checklist

- [ ] Copy `RateLimitManager` class
- [ ] Copy `@rate_limit` decorator
- [ ] Copy `InputSanitizer` class
- [ ] Copy `@input_sanitize` decorator
- [ ] Copy `@require_request_size_limit` decorator
- [ ] Copy `@add_security_headers` decorator
- [ ] Copy `@audit_log` decorator
- [ ] Copy `@require_csrf_token` decorator
- [ ] Apply decorators to all endpoints
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Update `ultron_config.json`
- [ ] Update documentation
- [ ] Deploy and test

---

**Status**: Ready for Implementation
**Next Steps**: Apply decorators to endpoints in priority order
**Document Version**: 1.0
**Last Updated**: November 3, 2025
