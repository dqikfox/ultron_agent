"""Performance tracking for ULTRON Agent"""
import time
from functools import wraps
from utils.ultron_logger import log_info

def track_performance(func):
    """Decorator to track function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        if duration > 1.0:  # Only log slow operations
            log_info("performance", f"{func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation, duration):
        """Record operation performance"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
    
    def get_stats(self, operation):
        """Get performance statistics"""
        if operation not in self.metrics:
            return None
        
        times = self.metrics[operation]
        return {
            'count': len(times),
            'avg': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }
