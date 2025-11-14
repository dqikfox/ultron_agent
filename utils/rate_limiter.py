"""Rate limiting utilities for ULTRON Agent API endpoints."""

import time
import threading
from collections import deque
from functools import wraps
from typing import Dict, Callable
from flask import request, jsonify

class RateLimitManager:
    """Thread-safe rate limiter using token bucket algorithm."""
    
    def __init__(self, requests_per_hour: int = 100, burst_size: int = 10):
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        self.window_seconds = 3600  # 1 hour
        self.requests: Dict[str, deque] = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier (IP address)."""
        current_time = time.time()
        
        with self.lock:
            # Initialize deque for new identifiers
            if identifier not in self.requests:
                self.requests[identifier] = deque()
            
            request_times = self.requests[identifier]
            
            # Remove requests outside the time window
            while request_times and current_time - request_times[0] > self.window_seconds:
                request_times.popleft()
            
            # Check if limit exceeded
            if len(request_times) >= self.requests_per_hour:
                return False
            
            # Add current request
            request_times.append(current_time)
            return True
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        current_time = time.time()
        
        with self.lock:
            if identifier not in self.requests:
                return self.requests_per_hour
            
            request_times = self.requests[identifier]
            
            # Clean old requests
            while request_times and current_time - request_times[0] > self.window_seconds:
                request_times.popleft()
            
            return max(0, self.requests_per_hour - len(request_times))


# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter(requests_per_hour: int = 100, burst_size: int = 10) -> RateLimitManager:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimitManager(requests_per_hour, burst_size)
    return _rate_limiter


def rate_limit(requests_per_hour: int = 100, burst_size: int = 10) -> Callable:
    """
    Decorator to apply rate limiting to Flask endpoints.
    
    Args:
        requests_per_hour: Maximum requests per hour per IP
        burst_size: Maximum burst size (not used in basic implementation)
    
    Returns:
        Decorated function with rate limiting
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter(requests_per_hour, burst_size)
            
            # Get client IP
            client_ip = request.remote_addr or 'unknown'
            
            # Check rate limit
            if not limiter.is_allowed(client_ip):
                remaining = limiter.get_remaining(client_ip)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Try again later.',
                    'remaining': remaining
                }), 429
            
            # Execute original function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
