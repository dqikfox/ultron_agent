"""
ULTRON Evolution Phase 2 - WebSocket Real-time Updates & Performance Profiling
Enables live metric streaming and function-level performance analysis
"""

import asyncio
import json
import time
import logging
import threading
import functools
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Any, Optional, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """
    Lightweight function-level performance tracking.
    Tracks execution time, call counts, and identifies bottlenecks.
    """

    def __init__(self, max_history: int = 1000):
        """Initialize performance profiler"""
        self.metrics = defaultdict(lambda: {
            'calls': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'history': deque(maxlen=max_history)
        })
        self.lock = threading.Lock()

    def profile(self, func: Callable) -> Callable:
        """Decorator to profile function execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start_time
                self._record_metric(func.__name__, elapsed)

        return wrapper

    def _record_metric(self, func_name: str, elapsed: float):
        """Record function execution metric"""
        with self.lock:
            metric = self.metrics[func_name]
            metric['calls'] += 1
            metric['total_time'] += elapsed
            metric['min_time'] = min(metric['min_time'], elapsed)
            metric['max_time'] = max(metric['max_time'], elapsed)
            metric['history'].append({
                'timestamp': datetime.now().isoformat(),
                'duration': elapsed
            })

    def get_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        with self.lock:
            stats = {}
            for func_name, metric in self.metrics.items():
                if metric['calls'] > 0:
                    avg_time = metric['total_time'] / metric['calls']
                    stats[func_name] = {
                        'calls': metric['calls'],
                        'total_time_ms': round(metric['total_time'] * 1000, 2),
                        'avg_time_ms': round(avg_time * 1000, 2),
                        'min_time_ms': round(metric['min_time'] * 1000, 2),
                        'max_time_ms': round(metric['max_time'] * 1000, 2),
                        'history_size': len(metric['history'])
                    }
            return stats

    def get_bottlenecks(self, top_n: int = 5) -> list:
        """Identify top performance bottlenecks"""
        stats = self.get_stats()
        sorted_funcs = sorted(
            stats.items(),
            key=lambda x: x[1]['total_time_ms'],
            reverse=True
        )
        return [
            {
                'function': name,
                'total_time_ms': stat['total_time_ms'],
                'avg_time_ms': stat['avg_time_ms'],
                'calls': stat['calls']
            }
            for name, stat in sorted_funcs[:top_n]
        ]

    def get_history(self, func_name: str, limit: int = 100) -> list:
        """Get execution history for a function"""
        with self.lock:
            if func_name in self.metrics:
                history = list(self.metrics[func_name]['history'])
                return history[-limit:]
        return []


class MetricsStreamBuffer:
    """
    Maintains a buffer of recent metrics for WebSocket streaming.
    Efficiently handles multiple subscribers requesting real-time data.
    """

    def __init__(self, capacity: int = 500, interval: float = 1.0):
        """
        Initialize metrics buffer.

        Args:
            capacity: Max metrics to store
            interval: Collection interval in seconds
        """
        self.capacity = capacity
        self.interval = interval
        self.buffer = deque(maxlen=capacity)
        self.subscribers = set()
        self.lock = threading.Lock()
        self.last_update = time.time()

    def add_metric(self, metric: Dict[str, Any]):
        """Add a metric to the buffer"""
        with self.lock:
            metric['timestamp'] = datetime.now().isoformat()
            self.buffer.append(metric)
            self.last_update = time.time()

    def get_latest(self, count: int = 10) -> list:
        """Get latest N metrics"""
        with self.lock:
            return list(self.buffer)[-count:]

    def get_since(self, timestamp: str) -> list:
        """Get all metrics since a specific timestamp"""
        try:
            cutoff = datetime.fromisoformat(timestamp)
            with self.lock:
                return [
                    m for m in self.buffer
                    if datetime.fromisoformat(m['timestamp']) >= cutoff
                ]
        except ValueError:
            return []

    def subscribe(self, subscriber_id: str):
        """Add a WebSocket subscriber"""
        with self.lock:
            self.subscribers.add(subscriber_id)

    def unsubscribe(self, subscriber_id: str):
        """Remove a WebSocket subscriber"""
        with self.lock:
            self.subscribers.discard(subscriber_id)

    def get_subscriber_count(self) -> int:
        """Get number of active subscribers"""
        with self.lock:
            return len(self.subscribers)


class RealtimeMetricsCollector:
    """Collects and aggregates real-time system metrics"""

    def __init__(self, buffer: MetricsStreamBuffer):
        """Initialize metrics collector"""
        self.buffer = buffer
        self.running = False
        self.collection_thread = None

    def start(self, interval: float = 1.0):
        """Start collecting metrics"""
        if not self.running:
            self.running = True
            self.collection_thread = threading.Thread(
                target=self._collection_loop,
                args=(interval,),
                daemon=True
            )
            self.collection_thread.start()
            logger.info("Real-time metrics collection started")

    def stop(self):
        """Stop collecting metrics"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
            logger.info("Real-time metrics collection stopped")

    def _collection_loop(self, interval: float):
        """Main collection loop"""
        import psutil

        while self.running:
            try:
                metric = {
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'process_count': len(psutil.pids())
                }
                self.buffer.add_metric(metric)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                time.sleep(interval)


class WebSocketMetricsHandler:
    """Handles WebSocket connections for real-time metric streaming"""

    def __init__(self, profiler: PerformanceProfiler,
                 metrics_buffer: MetricsStreamBuffer):
        """Initialize WebSocket handler"""
        self.profiler = profiler
        self.metrics_buffer = metrics_buffer
        self.connections = {}

    def register_connection(self, client_id: str):
        """Register a new WebSocket connection"""
        self.connections[client_id] = {
            'connected_at': datetime.now().isoformat(),
            'last_heartbeat': time.time()
        }
        self.metrics_buffer.subscribe(client_id)
        logger.info(f"WebSocket client connected: {client_id}")

    def unregister_connection(self, client_id: str):
        """Unregister a WebSocket connection"""
        if client_id in self.connections:
            del self.connections[client_id]
        self.metrics_buffer.unsubscribe(client_id)
        logger.info(f"WebSocket client disconnected: {client_id}")

    def get_metrics_update(self) -> Dict[str, Any]:
        """Get current metrics update for broadcasting"""
        return {
            'type': 'metrics_update',
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics_buffer.get_latest(1),
            'active_subscribers': self.metrics_buffer.get_subscriber_count()
        }

    def get_performance_update(self) -> Dict[str, Any]:
        """Get performance profiling update"""
        return {
            'type': 'performance_update',
            'timestamp': datetime.now().isoformat(),
            'bottlenecks': self.profiler.get_bottlenecks(top_n=5),
            'total_functions_tracked': len(self.profiler.metrics)
        }

    def get_health_update(self) -> Dict[str, Any]:
        """Get system health update"""
        import psutil

        memory = psutil.virtual_memory()
        return {
            'type': 'health_update',
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'processes': len(psutil.pids())
            }
        }


# Global instances
profiler = PerformanceProfiler()
metrics_buffer = MetricsStreamBuffer()
metrics_collector = RealtimeMetricsCollector(metrics_buffer)
ws_handler = WebSocketMetricsHandler(profiler, metrics_buffer)


def start_phase2_services():
    """Start all Phase 2 services"""
    metrics_collector.start(interval=1.0)
    logger.info("ULTRON Evolution Phase 2 services started")


def stop_phase2_services():
    """Stop all Phase 2 services"""
    metrics_collector.stop()
    logger.info("ULTRON Evolution Phase 2 services stopped")
