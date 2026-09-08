import psutil
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional
import asyncio

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.max_history = 3600  # 1 hour of metrics at 1-second intervals
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Start collecting performance metrics."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._collect_metrics())
        logging.info("Performance monitoring started")

    async def stop_monitoring(self):
        """Stop collecting performance metrics."""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logging.info("Performance monitoring stopped")

    async def _collect_metrics(self):
        """Continuously collect performance metrics."""
        try:
            while self.monitoring:
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu': {
                        'percent': psutil.cpu_percent(interval=1),
                        'per_cpu': psutil.cpu_percent(interval=None, percpu=True)
                    },
                    'memory': dict(psutil.virtual_memory()._asdict()),
                    'disk': {
                        'usage': dict(psutil.disk_usage('/')._asdict()),
                        'io': dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else None
                    },
                    'network': dict(psutil.net_io_counters()._asdict()),
                    'process': {
                        'memory': dict(psutil.Process().memory_info()._asdict()),
                        'cpu': psutil.Process().cpu_percent()
                    }
                }

                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history = self.metrics_history[-self.max_history:]

                await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error collecting performance metrics: {e}")
            self.monitoring = False

    def get_metrics_summary(self) -> Dict:
        """Get a summary of recent performance metrics."""
        if not self.metrics_history:
            return {}

        recent = self.metrics_history[-60:]  # Last minute
        return {
            'cpu_avg': sum(m['cpu']['percent'] for m in recent) / len(recent),
            'memory_avg': sum(m['memory']['percent'] for m in recent) / len(recent),
            'network': {
                'bytes_sent': recent[-1]['network']['bytes_sent'] - recent[0]['network']['bytes_sent'],
                'bytes_recv': recent[-1]['network']['bytes_recv'] - recent[0]['network']['bytes_recv']
            },
            'process': {
                'cpu_avg': sum(m['process']['cpu'] for m in recent) / len(recent),
                'memory_current': recent[-1]['process']['memory']['rss'] / (1024 * 1024)  # MB
            }
        }

    def get_metrics_history(self, minutes: int = 5) -> List[Dict]:
        """Get metrics history for the specified duration."""
        samples = minutes * 60
        return self.metrics_history[-samples:] if self.metrics_history else []

    def clear_history(self):
        """Clear metrics history."""
        self.metrics_history = []
