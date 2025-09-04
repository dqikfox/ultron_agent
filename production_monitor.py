#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Advanced Production Monitoring
Enhanced monitoring with alerting, metrics collection, and dashboard
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil

# Optional imports with fallbacks
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback classes
    class FakeMetric:
        def set(self, value): pass
        def inc(self, value=1): pass
        def observe(self, value): pass
    
    Counter = Histogram = Gauge = FakeMetric
    CONTENT_TYPE_LATEST = 'text/plain'
    def generate_latest(): return "# Prometheus client not available"

try:
    from aiohttp import web
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    web = None

logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    duration: int  # seconds
    severity: str  # 'critical', 'warning', 'info'
    description: str
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class SystemMetrics:
    """System metrics data."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: float
    gpu_percent: Optional[float] = None
    gpu_memory_percent: Optional[float] = None
    gpu_temperature: Optional[float] = None


class MetricsCollector:
    """Advanced metrics collection system."""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 1000
        
        # Initialize Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self.setup_prometheus_metrics()
        else:
            logger.warning("Prometheus client not available, metrics collection limited")
            
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        # System metrics
        self.cpu_usage = Gauge('ultron_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('ultron_memory_usage_percent', 'Memory usage percentage')
        self.disk_usage = Gauge('ultron_disk_usage_percent', 'Disk usage percentage')
        self.uptime = Gauge('ultron_uptime_seconds', 'System uptime in seconds')
        
        # Optional GPU metrics
        if GPUtil:
            self.gpu_usage = Gauge('ultron_gpu_usage_percent', 'GPU usage percentage')
            self.gpu_memory = Gauge('ultron_gpu_memory_percent', 'GPU memory usage percentage')
            self.gpu_temp = Gauge('ultron_gpu_temperature_celsius', 'GPU temperature')
            
        # Application metrics
        self.http_requests = Counter('ultron_http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
        self.response_time = Histogram('ultron_response_time_seconds', 'Response time distribution')
        self.active_connections = Gauge('ultron_active_connections', 'Active connections')
        self.errors_total = Counter('ultron_errors_total', 'Total errors', ['component', 'type'])
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            uptime = time.time() - self.start_time
            
            # GPU metrics (if available)
            gpu_percent = None
            gpu_memory_percent = None
            gpu_temperature = None
            
            if GPUtil:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        gpu_percent = gpu.load * 100
                        gpu_memory_percent = gpu.memoryUtil * 100
                        gpu_temperature = gpu.temperature
                except Exception as e:
                    logger.debug(f"GPU metrics unavailable: {e}")
                    
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / (1024**3),
                memory_total_gb=memory.total / (1024**3),
                disk_percent=disk.percent,
                disk_used_gb=disk.used / (1024**3),
                disk_total_gb=disk.total / (1024**3),
                uptime_seconds=uptime,
                gpu_percent=gpu_percent,
                gpu_memory_percent=gpu_memory_percent,
                gpu_temperature=gpu_temperature
            )
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.update_prometheus_metrics(metrics)
                
            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            # Return minimal metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_total_gb=0.0,
                uptime_seconds=time.time() - self.start_time
            )
            
    def update_prometheus_metrics(self, metrics: SystemMetrics):
        """Update Prometheus metrics."""
        try:
            self.cpu_usage.set(metrics.cpu_percent)
            self.memory_usage.set(metrics.memory_percent)
            self.disk_usage.set(metrics.disk_percent)
            self.uptime.set(metrics.uptime_seconds)
            
            if hasattr(self, 'gpu_usage') and metrics.gpu_percent is not None:
                self.gpu_usage.set(metrics.gpu_percent)
                self.gpu_memory.set(metrics.gpu_memory_percent or 0)
                self.gpu_temp.set(metrics.gpu_temperature or 0)
                
        except Exception as e:
            logger.error(f"Failed to update Prometheus metrics: {e}")
            
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus formatted metrics."""
        if PROMETHEUS_AVAILABLE:
            return generate_latest()
        else:
            # Fallback manual format
            metrics = self.collect_system_metrics()
            return f"""# HELP ultron_cpu_usage_percent CPU usage percentage
# TYPE ultron_cpu_usage_percent gauge
ultron_cpu_usage_percent {metrics.cpu_percent}

# HELP ultron_memory_usage_percent Memory usage percentage
# TYPE ultron_memory_usage_percent gauge
ultron_memory_usage_percent {metrics.memory_percent}

# HELP ultron_disk_usage_percent Disk usage percentage
# TYPE ultron_disk_usage_percent gauge
ultron_disk_usage_percent {metrics.disk_percent}

# HELP ultron_uptime_seconds System uptime in seconds
# TYPE ultron_uptime_seconds counter
ultron_uptime_seconds {metrics.uptime_seconds}
"""


class SimpleAlertManager:
    """Simple alerting system for production monitoring."""
    
    def __init__(self):
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.thresholds = {
            'cpu_critical': 95.0,
            'cpu_warning': 80.0,
            'memory_critical': 95.0,
            'memory_warning': 85.0,
            'disk_critical': 95.0,
            'disk_warning': 90.0
        }
        
    def check_alerts(self, metrics: SystemMetrics):
        """Check metrics against alert thresholds."""
        current_time = datetime.now()
        
        # CPU alerts
        if metrics.cpu_percent > self.thresholds['cpu_critical']:
            self.trigger_alert('cpu_critical', f"Critical CPU usage: {metrics.cpu_percent:.1f}%", 'critical')
        elif metrics.cpu_percent > self.thresholds['cpu_warning']:
            self.trigger_alert('cpu_warning', f"High CPU usage: {metrics.cpu_percent:.1f}%", 'warning')
        else:
            self.clear_alert('cpu_critical')
            self.clear_alert('cpu_warning')
            
        # Memory alerts
        if metrics.memory_percent > self.thresholds['memory_critical']:
            self.trigger_alert('memory_critical', f"Critical memory usage: {metrics.memory_percent:.1f}%", 'critical')
        elif metrics.memory_percent > self.thresholds['memory_warning']:
            self.trigger_alert('memory_warning', f"High memory usage: {metrics.memory_percent:.1f}%", 'warning')
        else:
            self.clear_alert('memory_critical')
            self.clear_alert('memory_warning')
            
        # Disk alerts
        if metrics.disk_percent > self.thresholds['disk_critical']:
            self.trigger_alert('disk_critical', f"Critical disk usage: {metrics.disk_percent:.1f}%", 'critical')
        elif metrics.disk_percent > self.thresholds['disk_warning']:
            self.trigger_alert('disk_warning', f"High disk usage: {metrics.disk_percent:.1f}%", 'warning')
        else:
            self.clear_alert('disk_critical')
            self.clear_alert('disk_warning')
            
    def trigger_alert(self, alert_id: str, message: str, severity: str):
        """Trigger an alert."""
        if alert_id not in self.active_alerts:
            self.active_alerts[alert_id] = datetime.now()
            
            alert_data = {
                'id': alert_id,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            
            self.alert_history.append(alert_data)
            
            # Keep only last 100 alerts
            if len(self.alert_history) > 100:
                self.alert_history = self.alert_history[-100:]
                
            # Log the alert
            if severity == 'critical':
                logger.error(f"🚨 CRITICAL ALERT: {message}")
            else:
                logger.warning(f"⚠️  WARNING ALERT: {message}")
                
    def clear_alert(self, alert_id: str):
        """Clear an active alert."""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            logger.info(f"✅ Alert cleared: {alert_id}")
            
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts."""
        return [
            {
                'id': alert_id,
                'triggered_at': trigger_time.isoformat(),
                'duration': (datetime.now() - trigger_time).total_seconds()
            }
            for alert_id, trigger_time in self.active_alerts.items()
        ]


class ProductionMonitor:
    """Production monitoring system for ULTRON Agent."""
    
    def __init__(self, dashboard_port: int = 9090):
        self.dashboard_port = dashboard_port
        self.metrics_collector = MetricsCollector()
        self.alert_manager = SimpleAlertManager()
        
        # Monitoring state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Web dashboard (if aiohttp available)
        if AIOHTTP_AVAILABLE:
            self.app = web.Application()
            self.setup_web_routes()
        else:
            self.app = None
            logger.warning("aiohttp not available, web dashboard disabled")
            
    def setup_web_routes(self):
        """Setup web dashboard routes."""
        if not self.app:
            return
            
        self.app.router.add_get('/', self.dashboard_home)
        self.app.router.add_get('/health', self.health_endpoint)
        self.app.router.add_get('/metrics', self.metrics_endpoint)
        self.app.router.add_get('/api/system', self.api_system)
        self.app.router.add_get('/api/alerts', self.api_alerts)
        
    async def dashboard_home(self, request):
        """Main dashboard page."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>ULTRON Agent Production Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #1a1a1a; color: #fff;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .card { 
            background: #2d2d2d; border: 1px solid #444; 
            border-radius: 8px; padding: 20px;
        }
        .metric { font-size: 2em; font-weight: bold; color: #4CAF50; }
        .metric.warning { color: #FF9800; }
        .metric.critical { color: #F44336; }
        .status-good { color: #4CAF50; }
        .status-warning { color: #FF9800; }
        .status-critical { color: #F44336; }
        .alert { 
            background: #FF5722; color: white; 
            padding: 10px; margin: 5px 0; border-radius: 4px;
        }
        .refresh-btn {
            background: #2196F3; color: white; border: none;
            padding: 10px 20px; border-radius: 4px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 ULTRON Agent Production Monitor</h1>
        <p>Real-time system monitoring and alerting</p>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>📊 System Resources</h3>
            <div>CPU: <span class="metric" id="cpu">--</span>%</div>
            <div>Memory: <span class="metric" id="memory">--</span>%</div>
            <div>Disk: <span class="metric" id="disk">--</span>%</div>
        </div>
        
        <div class="card">
            <h3>🔧 System Health</h3>
            <div id="health-status">Loading...</div>
        </div>
        
        <div class="card">
            <h3>🚨 Active Alerts</h3>
            <div id="alerts">Loading...</div>
        </div>
        
        <div class="card">
            <h3>📈 Performance</h3>
            <div>Uptime: <span id="uptime">--</span></div>
            <div>Memory Used: <span id="memory-used">--</span> GB</div>
            <div>Disk Used: <span id="disk-used">--</span> GB</div>
        </div>
    </div>
    
    <script>
        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${days}d ${hours}h ${minutes}m`;
        }
        
        function updateMetricColor(elementId, value, warningThreshold, criticalThreshold) {
            const element = document.getElementById(elementId);
            element.classList.remove('warning', 'critical');
            if (value >= criticalThreshold) {
                element.classList.add('critical');
            } else if (value >= warningThreshold) {
                element.classList.add('warning');
            }
        }
        
        async function updateDashboard() {
            try {
                const systemRes = await fetch('/api/system');
                const systemData = await systemRes.json();
                
                document.getElementById('cpu').textContent = systemData.cpu_percent?.toFixed(1) || '--';
                document.getElementById('memory').textContent = systemData.memory_percent?.toFixed(1) || '--';
                document.getElementById('disk').textContent = systemData.disk_percent?.toFixed(1) || '--';
                document.getElementById('uptime').textContent = formatUptime(systemData.uptime_seconds || 0);
                document.getElementById('memory-used').textContent = systemData.memory_used_gb?.toFixed(1) || '--';
                document.getElementById('disk-used').textContent = systemData.disk_used_gb?.toFixed(1) || '--';
                
                updateMetricColor('cpu', systemData.cpu_percent, 80, 95);
                updateMetricColor('memory', systemData.memory_percent, 85, 95);
                updateMetricColor('disk', systemData.disk_percent, 90, 95);
                
                const healthRes = await fetch('/health');
                const healthData = await healthRes.json();
                const healthDiv = document.getElementById('health-status');
                
                if (healthData.status === 'healthy') {
                    healthDiv.innerHTML = '<span class="status-good">✅ All systems operational</span>';
                } else {
                    healthDiv.innerHTML = '<span class="status-critical">❌ System issues detected</span>';
                }
                
                const alertsRes = await fetch('/api/alerts');
                const alertsData = await alertsRes.json();
                const alertsDiv = document.getElementById('alerts');
                
                if (alertsData.active_alerts && alertsData.active_alerts.length > 0) {
                    alertsDiv.innerHTML = alertsData.active_alerts.map(alert => 
                        `<div class="alert">Alert: ${alert.id} (${Math.floor(alert.duration)}s ago)</div>`
                    ).join('');
                } else {
                    alertsDiv.innerHTML = '<span class="status-good">✅ No active alerts</span>';
                }
                
            } catch (error) {
                console.error('Failed to update dashboard:', error);
            }
        }
        
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
        
    async def health_endpoint(self, request):
        """Health check endpoint."""
        try:
            metrics = self.metrics_collector.collect_system_metrics()
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Determine overall health
            status = "healthy"
            if any(alert['id'].endswith('_critical') for alert in active_alerts):
                status = "unhealthy"
            elif any(alert['id'].endswith('_warning') for alert in active_alerts):
                status = "degraded"
                
            return web.json_response({
                "status": status,
                "timestamp": metrics.timestamp.isoformat(),
                "uptime": metrics.uptime_seconds,
                "active_alerts": len(active_alerts),
                "checks": {
                    "cpu": "critical" if metrics.cpu_percent > 95 else "warning" if metrics.cpu_percent > 80 else "healthy",
                    "memory": "critical" if metrics.memory_percent > 95 else "warning" if metrics.memory_percent > 85 else "healthy",
                    "disk": "critical" if metrics.disk_percent > 95 else "warning" if metrics.disk_percent > 90 else "healthy"
                }
            })
            
        except Exception as e:
            return web.json_response({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
            
    async def metrics_endpoint(self, request):
        """Prometheus metrics endpoint."""
        metrics_text = self.metrics_collector.get_prometheus_metrics()
        return web.Response(text=metrics_text, content_type=CONTENT_TYPE_LATEST)
        
    async def api_system(self, request):
        """System information API."""
        try:
            metrics = self.metrics_collector.collect_system_metrics()
            return web.json_response(asdict(metrics), default=str)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
            
    async def api_alerts(self, request):
        """Alerts API."""
        try:
            active_alerts = self.alert_manager.get_active_alerts()
            recent_history = self.alert_manager.alert_history[-20:]  # Last 20 alerts
            
            return web.json_response({
                "active_alerts": active_alerts,
                "alert_history": recent_history,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
            
    async def start_monitoring(self):
        """Start the monitoring loop."""
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🔍 Production monitoring started")
        
    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("🔍 Production monitoring stopped")
        
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                # Collect metrics
                metrics = self.metrics_collector.collect_system_metrics()
                
                # Check alerts
                self.alert_manager.check_alerts(metrics)
                
                # Log status periodically
                if len(self.metrics_collector.metrics_history) % 60 == 0:  # Every 10 minutes
                    logger.info(f"📊 System status - CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_percent:.1f}%, Disk: {metrics.disk_percent:.1f}%")
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
                
    async def start_dashboard(self):
        """Start the web dashboard."""
        if not AIOHTTP_AVAILABLE or not self.app:
            logger.warning("Web dashboard not available (aiohttp not installed)")
            return None
            
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.dashboard_port)
        await site.start()
        
        logger.info(f"🚀 Monitoring dashboard started on http://0.0.0.0:{self.dashboard_port}")
        return runner
        
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status (synchronous method)."""
        try:
            metrics = self.metrics_collector.collect_system_metrics()
            active_alerts = self.alert_manager.get_active_alerts()
            
            return {
                "status": "healthy" if not active_alerts else "degraded",
                "metrics": asdict(metrics),
                "active_alerts": active_alerts,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


async def main():
    """Main function for standalone monitoring."""
    monitor = ProductionMonitor()
    
    try:
        # Start monitoring
        await monitor.start_monitoring()
        
        # Start dashboard if available
        runner = await monitor.start_dashboard()
        
        logger.info("✅ Production monitoring system started")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down production monitoring...")
        await monitor.stop_monitoring()
        if runner:
            await runner.cleanup()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())