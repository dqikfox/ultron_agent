import time
import psutil
import asyncio
import tracemalloc
import json
import cProfile
import pstats
from io import StringIO
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
from utils.ultron_logger import ultron_logger
import threading
from contextlib import contextmanager
from functools import wraps

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    thread_count: int
    operation_metadata: Dict[str, Any]
    peak_memory_mb: float = 0.0  # Peak memory during execution
    allocated_memory_mb: float = 0.0  # Memory allocated

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SystemMetrics:
    """Data class for system-wide performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_used_mb: float
    memory_available_mb: float
    memory_percent: float
    disk_usage_percent: float
    network_connections: int
    active_threads: int

@dataclass
class MemoryStats:
    """Memory usage statistics"""
    current_usage_mb: float
    peak_usage_mb: float
    allocated_mb: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceAlert:
    """Performance threshold violation alert"""
    component: str
    metric: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceProfiler:
    """Performance profiling system for ULTRON auto-analysis"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history: List[PerformanceMetrics] = []
        self.system_metrics_history: List[SystemMetrics] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.collection_interval = config.get('performance_collection_interval', 1.0)  # seconds
        self.performance_thresholds: Dict[str, float] = {}
        self.alerts: List[PerformanceAlert] = []
        self.historical_comparisons: Dict[str, List[PerformanceMetrics]] = {}

        # Initialize memory tracking
        tracemalloc.start()
        self.peak_memory = 0.0

    def start_system_monitoring(self):
        """Start background system monitoring"""
        if self.monitoring_active:
            ultron_logger.log_info("performance_profiler", "System monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system_loop, daemon=True)
        self.monitoring_thread.start()
        ultron_logger.log_info("performance_profiler", "Started system performance monitoring")

    def stop_system_monitoring(self):
        """Stop background system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        ultron_logger.log_info("performance_profiler", "Stopped system performance monitoring")

    def _monitor_system_loop(self):
        """Background loop for collecting system metrics"""
        while self.monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.system_metrics_history.append(metrics)

                # Keep only recent history to prevent memory bloat
                if len(self.system_metrics_history) > 1000:
                    self.system_metrics_history = self.system_metrics_history[-500:]

                time.sleep(self.collection_interval)
            except Exception as e:
                ultron_logger.log_error("performance_profiler", f"Error in system monitoring: {str(e)}")
                time.sleep(self.collection_interval)

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network_connections = len(psutil.net_connections())
        active_threads = threading.active_count()

        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            memory_percent=memory.percent,
            disk_usage_percent=disk.percent,
            network_connections=network_connections,
            active_threads=active_threads
        )

    @contextmanager
    def profile_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for profiling specific operations"""
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)
        start_memory = psutil.virtual_memory()

        ultron_logger.log_info("performance_profiler", f"Starting profiling for: {operation_name}")

        try:
            yield
        finally:
            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=None)
            end_memory = psutil.virtual_memory()

            duration = end_time - start_time
            avg_cpu = (start_cpu + end_cpu) / 2
            avg_memory_mb = ((start_memory.used + end_memory.used) / 2) / 1024 / 1024
            avg_memory_percent = (start_memory.percent + end_memory.percent) / 2

            metrics = PerformanceMetrics(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                cpu_percent=avg_cpu,
                memory_mb=avg_memory_mb,
                memory_percent=avg_memory_percent,
                thread_count=threading.active_count(),
                operation_metadata=metadata or {}
            )

            self.metrics_history.append(metrics)

            ultron_logger.log_info("performance_profiler",
                f"Completed profiling for: {operation_name}",
                extra={
                    'duration': duration,
                    'cpu_percent': avg_cpu,
                    'memory_mb': avg_memory_mb
                }
            )

    async def profile_async_operation(self, operation_name: str, coro, metadata: Optional[Dict[str, Any]] = None):
        """Profile an async operation"""
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)
        start_memory = psutil.virtual_memory()

        ultron_logger.log_info("performance_profiler", f"Starting async profiling for: {operation_name}")

        try:
            result = await coro
        finally:
            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=None)
            end_memory = psutil.virtual_memory()

            duration = end_time - start_time
            avg_cpu = (start_cpu + end_cpu) / 2
            avg_memory_mb = ((start_memory.used + end_memory.used) / 2) / 1024 / 1024
            avg_memory_percent = (start_memory.percent + end_memory.percent) / 2

            metrics = PerformanceMetrics(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                cpu_percent=avg_cpu,
                memory_mb=avg_memory_mb,
                memory_percent=avg_memory_percent,
                thread_count=threading.active_count(),
                operation_metadata=metadata or {}
            )

            self.metrics_history.append(metrics)

            ultron_logger.log_info("performance_profiler",
                f"Completed async profiling for: {operation_name}",
                extra={
                    'duration': duration,
                    'cpu_percent': avg_cpu,
                    'memory_mb': avg_memory_mb
                }
            )

        return result

    def get_operation_metrics(self, operation_name: Optional[str] = None) -> List[PerformanceMetrics]:
        """Get metrics for specific operation or all operations"""
        if operation_name:
            return [m for m in self.metrics_history if m.operation_name == operation_name]
        return self.metrics_history.copy()

    def get_system_metrics_history(self, limit: Optional[int] = None) -> List[SystemMetrics]:
        """Get system metrics history"""
        if limit:
            return self.system_metrics_history[-limit:]
        return self.system_metrics_history.copy()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary statistics"""
        if not self.metrics_history:
            return {"error": "No metrics collected"}

        operations = {}
        for metric in self.metrics_history:
            if metric.operation_name not in operations:
                operations[metric.operation_name] = []
            operations[metric.operation_name].append(metric.duration)

        summary = {}
        for op_name, durations in operations.items():
            summary[op_name] = {
                "count": len(durations),
                "total_duration": sum(durations),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "median_duration": sorted(durations)[len(durations) // 2]
            }

        # System metrics summary
        if self.system_metrics_history:
            cpu_usage = [m.cpu_percent for m in self.system_metrics_history]
            memory_usage = [m.memory_percent for m in self.system_metrics_history]

            summary["system"] = {
                "avg_cpu_percent": sum(cpu_usage) / len(cpu_usage),
                "max_cpu_percent": max(cpu_usage),
                "avg_memory_percent": sum(memory_usage) / len(memory_usage),
                "max_memory_percent": max(memory_usage),
                "monitoring_duration": (
                    self.system_metrics_history[-1].timestamp - self.system_metrics_history[0].timestamp
                )
            }

        return summary

    def identify_bottlenecks(self) -> Dict[str, Any]:
        """Identify performance bottlenecks"""
        summary = self.get_performance_summary()

        bottlenecks = {
            "slow_operations": [],
            "high_cpu_operations": [],
            "high_memory_operations": [],
            "recommendations": []
        }

        # Find slow operations (duration > threshold)
        slow_threshold = self.config.get('slow_operation_threshold', 5.0)  # 5 seconds
        for op_name, stats in summary.items():
            if op_name == "system":
                continue
            if stats.get('avg_duration', 0) > slow_threshold:
                bottlenecks["slow_operations"].append({
                    "operation": op_name,
                    "avg_duration": stats["avg_duration"],
                    "max_duration": stats["max_duration"]
                })

        # Find operations with high CPU usage
        high_cpu_threshold = self.config.get('high_cpu_threshold', 80.0)
        for metric in self.metrics_history:
            if metric.cpu_percent > high_cpu_threshold:
                bottlenecks["high_cpu_operations"].append({
                    "operation": metric.operation_name,
                    "cpu_percent": metric.cpu_percent,
                    "duration": metric.duration
                })

        # Find operations with high memory usage
        high_memory_threshold = self.config.get('high_memory_threshold', 85.0)
        for metric in self.metrics_history:
            if metric.memory_percent > high_memory_threshold:
                bottlenecks["high_memory_operations"].append({
                    "operation": metric.operation_name,
                    "memory_percent": metric.memory_percent,
                    "memory_mb": metric.memory_mb
                })

        # Generate recommendations
        if bottlenecks["slow_operations"]:
            bottlenecks["recommendations"].append(
                "Consider optimizing slow operations or running them asynchronously"
            )

        if bottlenecks["high_cpu_operations"]:
            bottlenecks["recommendations"].append(
                "High CPU usage detected - consider distributing workload or optimizing algorithms"
            )

        if bottlenecks["high_memory_operations"]:
            bottlenecks["recommendations"].append(
                "High memory usage detected - consider memory optimization or increasing system RAM"
            )

        return bottlenecks

    def set_performance_threshold(self, component: str, metric: str, threshold: float) -> None:
        """Set performance threshold for a component metric"""
        key = f"{component}:{metric}"
        self.performance_thresholds[key] = threshold
        ultron_logger.log_info("performance_profiler", f"Threshold set: {key} = {threshold}")

    async def get_memory_usage(self) -> MemoryStats:
        """Get current memory usage statistics"""
        current, peak = tracemalloc.get_traced_memory()
        return MemoryStats(
            current_usage_mb=current / (1024 * 1024),
            peak_usage_mb=peak / (1024 * 1024),
            allocated_mb=psutil.Process().memory_info().rss / (1024 * 1024)
        )

    async def profile_async(self, coro) -> Any:
        """Profile an async coroutine"""
        start = time.time()
        start_memory = tracemalloc.get_traced_memory()[0]

        try:
            result = await coro
            duration = (time.time() - start) * 1000
            end_memory = tracemalloc.get_traced_memory()[0]
            memory_used = (end_memory - start_memory) / (1024 * 1024)

            ultron_logger.log_info("performance_profiler",
                                 f"Async operation: {duration:.2f}ms, Memory: {memory_used:.2f}MB")
            return result
        except Exception as e:
            ultron_logger.log_error("performance_profiler", f"Async profiling error: {str(e)}")
            raise

    def generate_report(self, format: str = 'json') -> str:
        """Generate performance report in specified format"""
        summary = self.get_performance_summary()
        bottlenecks = self.identify_bottlenecks()

        if format == 'json':
            report = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "bottlenecks": bottlenecks,
                "alerts": [asdict(a) for a in self.alerts]
            }
            return json.dumps(report, indent=2, default=str)
        elif format == 'csv':
            lines = ["metric,value"]
            for key, value in summary.items():
                lines.append(f"{key},{value}")
            return '\n'.join(lines)
        elif format == 'html':
            return self._generate_html_report(summary, bottlenecks)
        else:
            return str(summary)

    def _generate_html_report(self, summary: dict, bottlenecks: dict) -> str:
        """Generate HTML performance report"""
        html = "<html><body><h1>Performance Report</h1>"
        html += f"<p>Generated: {datetime.now().isoformat()}</p>"
        html += "<h2>Summary</h2><ul>"
        for key, value in summary.items():
            html += f"<li>{key}: {value}</li>"
        html += "</ul><h2>Bottlenecks</h2><ul>"
        for key, value in bottlenecks.items():
            if isinstance(value, list):
                for item in value:
                    html += f"<li>{item}</li>"
            else:
                html += f"<li>{key}: {value}</li>"
        html += "</ul></body></html>"
        return html

    async def compare_with_history(self, component: str) -> Dict[str, Any]:
        """Compare current performance with historical data"""
        current_metrics = [m for m in self.metrics_history if component in m.operation_name]

        if not current_metrics:
            return {"error": f"No metrics found for component: {component}"}

        current_avg = sum(m.duration for m in current_metrics) / len(current_metrics)

        return {
            "component": component,
            "current_avg_ms": current_avg,
            "metric_count": len(current_metrics),
            "trend": "improving" if current_avg < 1000 else "degrading"
        }

    def export_metrics(self, filepath: str):
        """Export all metrics to JSON file"""
        export_data = {
            "performance_metrics": [m.to_dict() for m in self.metrics_history],
            "system_metrics": [asdict(m) for m in self.system_metrics_history],
            "summary": self.get_performance_summary(),
            "bottlenecks": self.identify_bottlenecks(),
            "export_timestamp": time.time()
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        ultron_logger.log_info("performance_profiler", f"Metrics exported to: {filepath}")

    def clear_metrics(self):
        """Clear all collected metrics"""
        self.metrics_history.clear()
        self.system_metrics_history.clear()
        ultron_logger.log_info("performance_profiler", "Metrics cleared")

# Global profiler instance
_profiler_instance: Optional[PerformanceProfiler] = None

def get_performance_profiler(config: Optional[Dict[str, Any]] = None) -> PerformanceProfiler:
    """Get or create global performance profiler instance"""
    global _profiler_instance
    if _profiler_instance is None:
        if config is None:
            config = {}
        _profiler_instance = PerformanceProfiler(config)
    return _profiler_instance

# Convenience functions for easy profiling
def start_performance_monitoring(config: Optional[Dict[str, Any]] = None):
    """Start performance monitoring"""
    profiler = get_performance_profiler(config)
    profiler.start_system_monitoring()

def stop_performance_monitoring():
    """Stop performance monitoring"""
    profiler = get_performance_profiler()
    profiler.stop_system_monitoring()

def profile_function(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for profiling functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = get_performance_profiler()
            with profiler.profile_operation(operation_name, metadata):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def profile_async_function(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for profiling async functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            profiler = get_performance_profiler()
            return await profiler.profile_async_operation(operation_name, func(*args, **kwargs), metadata)
        return wrapper
    return decorator
