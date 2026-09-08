"""
Performance Optimizer for ULTRON Agent 3.0
Provides system monitoring, optimization, and resource management
"""

import psutil
import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from collections import deque
from logging import getLogger
from security_utils import sanitize_log_input

logger = getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: float


class PerformanceOptimizer:
    """Advanced performance monitoring and optimization."""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable] = []
        
        # Performance thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        
    def start_monitoring(self, interval: float = 2.0):
        """Start performance monitoring."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("Performance monitoring stopped")
        
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Check thresholds and trigger callbacks
                self._check_thresholds(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {sanitize_log_input(str(e))}")
                time.sleep(interval)
                
    def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage (root partition)
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_percent,
                network_io=network_io,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {sanitize_log_input(str(e))}")
            # Return default metrics on error
            return SystemMetrics(0.0, 0.0, 0.0, {}, time.time())
            
    def _check_thresholds(self, metrics: SystemMetrics):
        """Check if metrics exceed thresholds."""
        alerts = []
        
        if metrics.cpu_percent > self.cpu_threshold:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
            
        if metrics.memory_percent > self.memory_threshold:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
            
        if metrics.disk_usage > self.disk_threshold:
            alerts.append(f"High disk usage: {metrics.disk_usage:.1f}%")
            
        if alerts:
            for callback in self.callbacks:
                try:
                    callback(alerts, metrics)
                except Exception as e:
                    logger.error(f"Error in performance callback: {sanitize_log_input(str(e))}")
                    
    def add_callback(self, callback: Callable):
        """Add performance alert callback."""
        self.callbacks.append(callback)
        
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
        
    def get_average_metrics(self, minutes: int = 5) -> Dict[str, float]:
        """Get average metrics over specified time period."""
        if not self.metrics_history:
            return {}
            
        cutoff_time = time.time() - (minutes * 60)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
            
        return {
            'avg_cpu': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'avg_disk': sum(m.disk_usage for m in recent_metrics) / len(recent_metrics),
            'sample_count': len(recent_metrics)
        }
        
    def optimize_system(self) -> List[str]:
        """Perform system optimization tasks."""
        optimizations = []
        
        try:
            # Clear Python cache
            import gc
            collected = gc.collect()
            if collected > 0:
                optimizations.append(f"Cleared {collected} Python objects from memory")
                
            # Get current metrics
            current = self.get_current_metrics()
            if not current:
                return optimizations
                
            # Memory optimization
            if current.memory_percent > 70:
                try:
                    # Force garbage collection
                    gc.collect()
                    optimizations.append("Performed aggressive garbage collection")
                except Exception as e:
                    logger.error(f"Memory optimization failed: {sanitize_log_input(str(e))}")
                    
            # CPU optimization suggestions
            if current.cpu_percent > 60:
                optimizations.append("Consider reducing concurrent operations")
                
            return optimizations
            
        except Exception as e:
            logger.error(f"System optimization failed: {sanitize_log_input(str(e))}")
            return ["Optimization failed - check logs"]
            
    def get_system_info(self) -> Dict[str, str]:
        """Get detailed system information."""
        try:
            return {
                'platform': psutil.WINDOWS if psutil.WINDOWS else 'Unix-like',
                'cpu_count': str(psutil.cpu_count()),
                'cpu_freq': f"{psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "Unknown",
                'total_memory': f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
                'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time())),
                'python_processes': str(len([p for p in psutil.process_iter() if 'python' in p.name().lower()]))
            }
        except Exception as e:
            logger.error(f"Error getting system info: {sanitize_log_input(str(e))}")
            return {'error': 'Unable to retrieve system information'}


# Global performance optimizer instance
_performance_optimizer = None

# Alias for backward compatibility
PerformanceMonitor = PerformanceOptimizer

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def start_performance_monitoring(interval: float = 2.0):
    """Start global performance monitoring."""
    optimizer = get_performance_optimizer()
    optimizer.start_monitoring(interval)


def stop_performance_monitoring():
    """Stop global performance monitoring."""
    optimizer = get_performance_optimizer()
    optimizer.stop_monitoring()


def get_system_status() -> Dict[str, any]:
    """Get comprehensive system status."""
    optimizer = get_performance_optimizer()
    current_metrics = optimizer.get_current_metrics()
    avg_metrics = optimizer.get_average_metrics()
    system_info = optimizer.get_system_info()
    
    return {
        'current': current_metrics.__dict__ if current_metrics else None,
        'averages': avg_metrics,
        'system_info': system_info,
        'monitoring_active': optimizer.monitoring
    }