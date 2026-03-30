"""Observability system for ULTRON Agent - Tracing, Metrics, Logging"""
from typing import Dict, Any, Optional
from datetime import datetime
import time
from contextlib import contextmanager
from utils.ultron_logger import log_info, log_error

class Tracer:
    """Distributed tracing"""
    def __init__(self):
        self.traces: Dict[str, list] = {}
    
    @contextmanager
    def trace(self, operation: str, metadata: Optional[Dict] = None):
        """Trace an operation"""
        trace_id = f"{operation}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            log_info("tracer", f"Starting: {operation}", extra=metadata or {})
            yield trace_id
        finally:
            duration = time.time() - start_time
            self.traces.setdefault(operation, []).append({
                "trace_id": trace_id,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata
            })
            log_info("tracer", f"Completed: {operation} ({duration:.3f}s)")

class MetricsCollector:
    """Metrics collection"""
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record(self, metric: str, value: float, tags: Optional[Dict] = None):
        """Record a metric"""
        self.metrics.setdefault(metric, []).append({
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        })
    
    def get_stats(self, metric: str) -> Dict[str, Any]:
        """Get metric statistics"""
        values = [m["value"] for m in self.metrics.get(metric, [])]
        if not values:
            return {}
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }

class ObservabilitySystem:
    """Unified observability system"""
    def __init__(self):
        self.tracer = Tracer()
        self.metrics = MetricsCollector()
    
    def trace_operation(self, operation: str, metadata: Optional[Dict] = None):
        """Trace an operation"""
        return self.tracer.trace(operation, metadata)
    
    def record_metric(self, metric: str, value: float, tags: Optional[Dict] = None):
        """Record a metric"""
        self.metrics.record(metric, value, tags)
    
    def get_health(self) -> Dict[str, Any]:
        """Get system health"""
        return {
            "status": "healthy",
            "traces_count": sum(len(t) for t in self.tracer.traces.values()),
            "metrics_count": sum(len(m) for m in self.metrics.metrics.values()),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
_observability = ObservabilitySystem()

def get_observability() -> ObservabilitySystem:
    """Get observability system"""
    return _observability
