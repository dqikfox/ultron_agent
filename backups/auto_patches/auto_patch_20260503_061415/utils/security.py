"""Security utilities for ULTRON Agent"""
from functools import wraps
from typing import Callable, Dict, Any
import time
from utils.ultron_logger import log_error, log_info

# Rate limiting storage
_rate_limits: Dict[str, list] = {}

class SecurityError(Exception):
    """Base security exception"""
    pass

class RateLimitExceeded(SecurityError):
    """Rate limit exceeded"""
    pass

class Unauthorized(SecurityError):
    """Unauthorized access"""
    pass

class ValidationError(SecurityError):
    """Input validation failed"""
    pass

def rate_limit(calls: int, period: int):
    """Rate limiting decorator"""
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = f.__name__
            now = time.time()
            
            if key not in _rate_limits:
                _rate_limits[key] = []
            
            _rate_limits[key] = [t for t in _rate_limits[key] if now - t < period]
            
            if len(_rate_limits[key]) >= calls:
                log_error("security", f"Rate limit exceeded: {key}")
                raise RateLimitExceeded(f"Rate limit: {calls} calls per {period}s")
            
            _rate_limits[key].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_auth(f: Callable):
    """Authentication decorator"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # TODO: Implement token validation
        log_info("security", f"Auth check: {f.__name__}")
        return f(*args, **kwargs)
    return wrapper

def validate_input(schema: dict):
    """Input validation decorator"""
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # TODO: Implement schema validation
            return f(*args, **kwargs)
        return wrapper
    return decorator
