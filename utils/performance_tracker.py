"""Performance tracking for ULTRON Agent"""
import time
from functools import wraps
from utils.ultron_logger import log_info

def track_performance(func):
    """Decorator to track function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        if duration > 1.0:  # Only log slow operations
            log_info("performance", f"{func.__name__} took {duration:.2f}s")

        return result
    return wrapper

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation_name, duration):
        """Record operation performance"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(duration)

    def get_stats(self, operation_name):
        """Get performance statistics"""
        if operation_name not in self.metrics:
            return None

        recorded_durations = self.metrics[operation_name]
        return {
            'count': len(recorded_durations),
            'avg': sum(recorded_durations) / len(recorded_durations),
            'min': min(recorded_durations),
            'max': max(recorded_durations)
        }
