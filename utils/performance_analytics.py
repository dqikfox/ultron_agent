"""
ULTRON Agent 3.0 - Advanced Performance Analytics
Distributed tracing, real-time metrics, and anomaly detection
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

from utils.ultron_logger import get_logger

logger = get_logger("performance_analytics")


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: float
    value: float
    labels: Dict[str, str]


@dataclass
class PerformanceTrace:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation: str
    start_time: float
    end_time: Optional[float]
    duration_ms: Optional[float]
    tags: Dict[str, Any]
    status: str  # success, error, timeout


@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    timestamp: float
    metric_name: str
    current_value: float
    expected_range: Tuple[float, float]
    severity: str  # low, medium, high, critical
    message: str


class PerformanceAnalytics:
    """
    Advanced performance monitoring with distributed tracing and anomaly detection.
    Provides real-time insights into system performance and health.
    """

    def __init__(self, 
                 history_size: int = 1000,
                 anomaly_threshold: float = 2.5):
        """
        Initialize performance analytics
        
        Args:
            history_size: Number of metric points to keep in memory
            anomaly_threshold: Standard deviations for anomaly detection
        """
        self.history_size = history_size
        self.anomaly_threshold = anomaly_threshold
        
        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.traces: Dict[str, PerformanceTrace] = {}
        self.active_spans: Dict[str, PerformanceTrace] = {}
        self.anomalies: deque = deque(maxlen=100)
        
        # Statistics
        self.stats = {
            'total_traces': 0,
            'total_spans': 0,
            'total_anomalies': 0,
            'avg_response_time_ms': 0.0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Background monitoring
        self._monitoring = False
        self._monitor_thread = None
        
        logger.info("Performance Analytics initialized")

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Record a metric value
        
        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels for filtering
        """
        with self._lock:
            point = MetricPoint(
                timestamp=time.time(),
                value=value,
                labels=labels or {}
            )
            
            self.metrics[name].append(point)
            
            # Check for anomalies
            self._check_anomaly(name, value)

    def start_trace(self, operation: str, tags: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a distributed trace
        
        Args:
            operation: Name of the operation being traced
            tags: Optional tags for the trace
            
        Returns:
            Trace ID
        """
        import uuid
        
        with self._lock:
            trace_id = str(uuid.uuid4())
            span_id = str(uuid.uuid4())
            
            trace = PerformanceTrace(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                operation=operation,
                start_time=time.time(),
                end_time=None,
                duration_ms=None,
                tags=tags or {},
                status='in_progress'
            )
            
            self.active_spans[trace_id] = trace
            self.stats['total_traces'] += 1
            self.stats['total_spans'] += 1
            
            return trace_id

    def end_trace(self, trace_id: str, status: str = 'success', tags: Optional[Dict[str, Any]] = None) -> Optional[PerformanceTrace]:
        """
        End a distributed trace
        
        Args:
            trace_id: ID of the trace to end
            status: Final status (success, error, timeout)
            tags: Additional tags to add
            
        Returns:
            Completed trace or None if not found
        """
        with self._lock:
            if trace_id not in self.active_spans:
                logger.warning(f"Trace {trace_id} not found in active spans")
                return None
            
            trace = self.active_spans.pop(trace_id)
            trace.end_time = time.time()
            trace.duration_ms = (trace.end_time - trace.start_time) * 1000
            trace.status = status
            
            if tags:
                trace.tags.update(tags)
            
            # Store completed trace
            self.traces[trace_id] = trace
            
            # Update average response time
            self._update_avg_response_time(trace.duration_ms)
            
            # Record metric
            self.record_metric(
                f"trace.{trace.operation}.duration_ms",
                trace.duration_ms,
                {'status': status}
            )
            
            logger.debug(f"Trace completed: {trace.operation} ({trace.duration_ms:.2f}ms) - {status}")
            
            return trace

    def _update_avg_response_time(self, duration_ms: float) -> None:
        """Update average response time with exponential moving average"""
        alpha = 0.1  # Smoothing factor
        current_avg = self.stats['avg_response_time_ms']
        self.stats['avg_response_time_ms'] = alpha * duration_ms + (1 - alpha) * current_avg

    def _check_anomaly(self, metric_name: str, value: float) -> None:
        """
        Check if a metric value is anomalous
        
        Args:
            metric_name: Name of the metric
            value: Current value
        """
        points = self.metrics[metric_name]
        
        if len(points) < 10:  # Need enough data for statistics
            return
        
        # Calculate mean and standard deviation
        values = [p.value for p in points]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        # Check if value is outside expected range
        lower_bound = mean - self.anomaly_threshold * stdev
        upper_bound = mean + self.anomaly_threshold * stdev
        
        if value < lower_bound or value > upper_bound:
            # Determine severity
            z_score = abs((value - mean) / stdev) if stdev > 0 else 0
            
            if z_score > 4:
                severity = 'critical'
            elif z_score > 3:
                severity = 'high'
            elif z_score > 2.5:
                severity = 'medium'
            else:
                severity = 'low'
            
            alert = AnomalyAlert(
                timestamp=time.time(),
                metric_name=metric_name,
                current_value=value,
                expected_range=(lower_bound, upper_bound),
                severity=severity,
                message=f"{metric_name} anomaly: {value:.2f} (expected {lower_bound:.2f}-{upper_bound:.2f})"
            )
            
            self.anomalies.append(alert)
            self.stats['total_anomalies'] += 1
            
            logger.warning(f"Anomaly detected: {alert.message}")

    def get_metric_stats(self, metric_name: str, window_seconds: int = 300) -> Dict[str, float]:
        """
        Get statistics for a metric
        
        Args:
            metric_name: Name of the metric
            window_seconds: Time window in seconds
            
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            if metric_name not in self.metrics:
                return {}
            
            cutoff_time = time.time() - window_seconds
            points = [p for p in self.metrics[metric_name] if p.timestamp >= cutoff_time]
            
            if not points:
                return {}
            
            values = [p.value for p in points]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'p95': self._percentile(values, 95),
                'p99': self._percentile(values, 99)
            }

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / 1024 / 1024,
                'memory_available_mb': memory.available / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / 1024 / 1024 / 1024,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024,
                'net_bytes_sent': net_io.bytes_sent,
                'net_bytes_recv': net_io.bytes_recv,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}

    def get_recent_anomalies(self, limit: int = 10) -> List[AnomalyAlert]:
        """Get recent anomaly alerts"""
        with self._lock:
            return list(self.anomalies)[-limit:]

    def get_slow_traces(self, threshold_ms: float = 1000, limit: int = 10) -> List[PerformanceTrace]:
        """
        Get traces that exceeded a duration threshold
        
        Args:
            threshold_ms: Minimum duration in milliseconds
            limit: Maximum number of traces to return
            
        Returns:
            List of slow traces
        """
        with self._lock:
            slow_traces = [
                trace for trace in self.traces.values()
                if trace.duration_ms and trace.duration_ms > threshold_ms
            ]
            
            # Sort by duration (slowest first)
            slow_traces.sort(key=lambda t: t.duration_ms or 0, reverse=True)
            
            return slow_traces[:limit]

    def get_trace_summary(self, window_seconds: int = 300) -> Dict[str, Any]:
        """
        Get summary of traces in time window
        
        Args:
            window_seconds: Time window in seconds
            
        Returns:
            Summary statistics
        """
        with self._lock:
            cutoff_time = time.time() - window_seconds
            
            recent_traces = [
                trace for trace in self.traces.values()
                if trace.end_time and trace.end_time >= cutoff_time
            ]
            
            if not recent_traces:
                return {
                    'total_traces': 0,
                    'avg_duration_ms': 0.0,
                    'success_rate': 0.0
                }
            
            durations = [t.duration_ms for t in recent_traces if t.duration_ms]
            successes = sum(1 for t in recent_traces if t.status == 'success')
            
            return {
                'total_traces': len(recent_traces),
                'avg_duration_ms': statistics.mean(durations) if durations else 0.0,
                'min_duration_ms': min(durations) if durations else 0.0,
                'max_duration_ms': max(durations) if durations else 0.0,
                'p95_duration_ms': self._percentile(durations, 95) if durations else 0.0,
                'success_rate': (successes / len(recent_traces) * 100) if recent_traces else 0.0,
                'active_spans': len(self.active_spans)
            }

    def start_monitoring(self, interval_seconds: int = 10) -> None:
        """
        Start background system monitoring
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if self._monitoring:
            logger.warning("Monitoring already active")
            return
        
        self._monitoring = True
        
        def monitor_loop():
            while self._monitoring:
                try:
                    # Collect system metrics
                    system_metrics = self.get_system_metrics()
                    
                    for metric_name, value in system_metrics.items():
                        if metric_name != 'timestamp' and isinstance(value, (int, float)):
                            self.record_metric(f"system.{metric_name}", float(value))
                    
                    time.sleep(interval_seconds)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(interval_seconds)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info(f"Performance monitoring started (interval: {interval_seconds}s)")

    def stop_monitoring(self) -> None:
        """Stop background system monitoring"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        with self._lock:
            return {
                'timestamp': datetime.now().isoformat(),
                'stats': self.stats.copy(),
                'system_metrics': self.get_system_metrics(),
                'trace_summary': self.get_trace_summary(window_seconds=300),
                'recent_anomalies': [asdict(a) for a in self.get_recent_anomalies(limit=5)],
                'slow_traces': [asdict(t) for t in self.get_slow_traces(threshold_ms=1000, limit=5)]
            }

    def export_metrics(self, format: str = 'json') -> str:
        """
        Export metrics in specified format
        
        Args:
            format: Export format (json, prometheus)
            
        Returns:
            Formatted metrics string
        """
        if format == 'json':
            import json
            return json.dumps(self.get_dashboard_data(), indent=2)
        
        elif format == 'prometheus':
            # Prometheus text format
            lines = []
            
            for metric_name, points in self.metrics.items():
                if not points:
                    continue
                
                latest_point = points[-1]
                # Sanitize metric name for Prometheus
                prom_name = metric_name.replace('.', '_')
                lines.append(f"# TYPE {prom_name} gauge")
                lines.append(f"{prom_name} {latest_point.value}")
            
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global instance
_performance_analytics: Optional[PerformanceAnalytics] = None


def get_performance_analytics() -> PerformanceAnalytics:
    """Get or create global performance analytics instance"""
    global _performance_analytics
    if _performance_analytics is None:
        _performance_analytics = PerformanceAnalytics()
    return _performance_analytics


# Convenience functions
def record_metric(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Record a metric"""
    get_performance_analytics().record_metric(name, value, labels)


def start_trace(operation: str, tags: Optional[Dict[str, Any]] = None) -> str:
    """Start a trace"""
    return get_performance_analytics().start_trace(operation, tags)


def end_trace(trace_id: str, status: str = 'success', tags: Optional[Dict[str, Any]] = None) -> Optional[PerformanceTrace]:
    """End a trace"""
    return get_performance_analytics().end_trace(trace_id, status, tags)


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data"""
    return get_performance_analytics().get_dashboard_data()
