"""Error recovery and retry logic for ULTRON Agent"""
import time
from functools import wraps
from utils.ultron_logger import log_error, log_info

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for automatic retry on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        log_error("error_recovery", f"{func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    log_info("error_recovery", f"{func.__name__} attempt {attempt + 1} failed, retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

def safe_execute(func, fallback=None):
    """Execute function with fallback on error"""
    try:
        return func()
    except Exception as e:
        log_error("error_recovery", f"Execution failed: {e}")
        return fallback() if fallback else None
