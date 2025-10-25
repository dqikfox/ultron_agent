"""
ULTRON Agent Diagnostics System
Unity Cloud Diagnostics-inspired monitoring and error tracking

Provides:
- Real-time crash reporting
- Exception tracking with stack traces
- Performance telemetry
- System health monitoring
- Multi-service diagnostics
- AWS CloudWatch integration
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from pathlib import Path
import psutil

from utils.ultron_logger import log_info, log_error


@dataclass
class CrashReport:
    """Crash report structure similar to Unity diagnostics"""
    crash_id: str
    timestamp: str
    component: str
    exception_type: str
    exception_message: str
    stack_trace: str
    system_info: Dict[str, Any]
    severity: str  # critical, error, warning
    resolved: bool = False
    resolution_notes: Optional[str] = None


@dataclass
class PerformanceMetric:
    """Performance telemetry data point"""
    timestamp: str
    component: str
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]


@dataclass
class SystemHealth:
    """System health snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    active_threads: int
    ollama_status: str
    api_server_status: str
    gui_server_status: str
    services_healthy: bool


class DiagnosticsCore:
    """
    Core diagnostics system for ULTRON Agent

    Inspired by Unity Cloud Diagnostics with features:
    - Crash/exception tracking
    - Performance monitoring
    - System health checks
    - Multi-service status
    - Real-time telemetry
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.diagnostics_dir = Path("diagnostics/data")
        self.diagnostics_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.crash_reports: List[CrashReport] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.system_health_history: List[SystemHealth] = []

        # Statistics
        self.component_error_counts = defaultdict(int)
        self.component_crash_counts = defaultdict(int)
        self.session_start_time = datetime.now()

        # Configuration
        self.max_stored_crashes = 1000
        self.max_stored_metrics = 10000
        self.max_health_snapshots = 1000
        self.telemetry_interval = config.get("performance_monitoring_interval", 10)

        # Service endpoints
        self.service_ports = {
            "ollama": 11434,
            "api_server": 5000,
            "gui_server": 8080,
            "ai_chat": 8000,
            "avatar_server": 8090
        }

        log_info("diagnostics_core", "Diagnostics system initialized")

    async def capture_crash(
        self,
        component: str,
        exception: Exception,
        severity: str = "error",
        additional_context: Optional[Dict] = None
    ) -> str:
        """
        Capture a crash/exception report

        Similar to Unity's crash reporting with full context
        """
        crash_id = f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Extract stack trace
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # Gather system info
        system_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "ultron_version": "3.0",
            "session_uptime_seconds": (datetime.now() - self.session_start_time).total_seconds(),
            "additional_context": additional_context or {}
        }

        # Create crash report
        report = CrashReport(
            crash_id=crash_id,
            timestamp=datetime.now().isoformat(),
            component=component,
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            stack_trace=stack_trace,
            system_info=system_info,
            severity=severity
        )

        # Store report
        self.crash_reports.append(report)
        self.component_crash_counts[component] += 1

        # Save to disk
        await self._save_crash_report(report)

        # Log
        log_error(
            "diagnostics_core",
            f"Crash captured: {crash_id} in {component}",
            exception=exception,
            crash_id=crash_id,
            severity=severity
        )

        # Trim old reports
        if len(self.crash_reports) > self.max_stored_crashes:
            self.crash_reports = self.crash_reports[-self.max_stored_crashes:]

        return crash_id

    async def record_performance_metric(
        self,
        component: str,
        metric_name: str,
        value: float,
        unit: str = "count",
        tags: Optional[Dict[str, str]] = None
    ):
        """Record a performance metric (telemetry)"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            component=component,
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )

        self.performance_metrics.append(metric)

        # Trim old metrics
        if len(self.performance_metrics) > self.max_stored_metrics:
            self.performance_metrics = self.performance_metrics[-self.max_stored_metrics:]

    async def capture_system_health(self) -> SystemHealth:
        """
        Capture current system health snapshot

        Similar to Unity's performance monitoring
        """
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Check service health
        ollama_healthy = await self._check_service_health("ollama", 11434)
        api_healthy = await self._check_service_health("api_server", 5000)
        gui_healthy = await self._check_service_health("gui_server", 8080)

        health = SystemHealth(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024**2),
            memory_available_mb=memory.available / (1024**2),
            disk_usage_percent=disk.percent,
            active_threads=len(psutil.Process().threads()),
            ollama_status="healthy" if ollama_healthy else "unhealthy",
            api_server_status="healthy" if api_healthy else "unhealthy",
            gui_server_status="healthy" if gui_healthy else "unhealthy",
            services_healthy=all([ollama_healthy, api_healthy, gui_healthy])
        )

        self.system_health_history.append(health)

        # Trim old snapshots
        if len(self.system_health_history) > self.max_health_snapshots:
            self.system_health_history = self.system_health_history[-self.max_health_snapshots:]

        return health

    async def _check_service_health(self, service_name: str, port: int) -> bool:
        """Check if a service is responding"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://localhost:{port}/health",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    return resp.status == 200
        except:
            # If no /health endpoint, check if port is listening
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                return result == 0
            except:
                return False

    def get_diagnostics_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostics summary

        Returns dashboard-ready data
        """
        now = datetime.now()
        session_uptime = now - self.session_start_time

        # Recent crashes (last hour)
        recent_crashes = [
            c for c in self.crash_reports
            if datetime.fromisoformat(c.timestamp) > now - timedelta(hours=1)
        ]

        # Latest health
        latest_health = self.system_health_history[-1] if self.system_health_history else None

        return {
            "session": {
                "start_time": self.session_start_time.isoformat(),
                "uptime_seconds": session_uptime.total_seconds(),
                "uptime_formatted": str(session_uptime).split('.')[0]
            },
            "crashes": {
                "total": len(self.crash_reports),
                "last_hour": len(recent_crashes),
                "by_component": dict(self.component_crash_counts),
                "unresolved": len([c for c in self.crash_reports if not c.resolved])
            },
            "performance": {
                "total_metrics": len(self.performance_metrics),
                "latest_health": asdict(latest_health) if latest_health else None
            },
            "services": {
                name: {
                    "port": port,
                    "status": getattr(latest_health, f"{name.replace('_server', '')}_status", "unknown")
                }
                for name, port in self.service_ports.items()
            } if latest_health else {}
        }

    async def _save_crash_report(self, report: CrashReport):
        """Save crash report to disk"""
        try:
            report_file = self.diagnostics_dir / f"{report.crash_id}.json"
            with open(report_file, 'w') as f:
                json.dump(asdict(report), f, indent=2)
        except Exception as e:
            log_error("diagnostics_core", f"Failed to save crash report: {e}")

    def export_diagnostics(self, output_path: Optional[str] = None) -> str:
        """
        Export all diagnostics data to JSON

        Similar to Unity's diagnostic reports export
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"diagnostics/data/ultron_diagnostics_{timestamp}.json"

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_diagnostics_summary(),
            "crash_reports": [asdict(c) for c in self.crash_reports],
            "performance_metrics": [asdict(m) for m in self.performance_metrics[-1000:]],
            "system_health": [asdict(h) for h in self.system_health_history[-100:]]
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        log_info("diagnostics_core", f"Diagnostics exported to {output_path}")
        return str(output_file)


# Singleton instance
_diagnostics_instance: Optional[DiagnosticsCore] = None


def get_diagnostics(config: Optional[Dict[str, Any]] = None) -> DiagnosticsCore:
    """Get or create diagnostics instance"""
    global _diagnostics_instance
    if _diagnostics_instance is None:
        if config is None:
            # Load default config
            try:
                with open("ultron_config.json") as f:
                    config = json.load(f)
            except:
                config = {}
        _diagnostics_instance = DiagnosticsCore(config)
    return _diagnostics_instance
