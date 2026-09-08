"""Health check and metrics endpoints for Ultron Agent."""
from __future__ import annotations

import asyncio
import time
import psutil
import GPUtil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger("ultron.health")


class HealthStatus(str, Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status for a single component."""
    name: str
    status: HealthStatus
    message: str
    last_check: datetime
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    gpu_percent: Optional[float] = None
    gpu_memory_percent: Optional[float] = None
    gpu_memory_used_gb: Optional[float] = None
    gpu_memory_total_gb: Optional[float] = None
    gpu_temperature: Optional[float] = None


class HealthChecker:
    """Central health checking and metrics collection."""

    def __init__(self):
        self.component_health: Dict[str, ComponentHealth] = {}
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.custom_checks: Dict[str, callable] = {}

    def register_check(self, name: str, check_function: callable) -> None:
        """Register a custom health check function."""
        self.custom_checks[name] = check_function
        logger.debug(f"Registered health check: {name}")

    async def check_basic_health(self) -> Dict[str, Any]:
        """
        Basic health check with no dependencies.
        Always returns quickly for load balancer health checks.
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.0.0",
            "uptime_seconds": self._get_uptime_seconds()
        }

    async def check_readiness(self) -> Dict[str, Any]:
        """
        Comprehensive readiness check including dependencies.
        Checks if system is ready to handle requests.
        """
        start_time = time.time()

        # Check all components
        components = await self._check_all_components()

        # Determine overall status
        overall_status = self._calculate_overall_status(components)

        response_time = (time.time() - start_time) * 1000

        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": response_time,
            "components": {comp.name: asdict(comp) for comp in components}
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics in Prometheus format."""
        metrics = await self._collect_system_metrics()

        # Convert to Prometheus text format
        prometheus_metrics = []

        # System metrics
        prometheus_metrics.extend([
            f"# HELP ultron_cpu_percent CPU usage percentage",
            f"# TYPE ultron_cpu_percent gauge",
            f"ultron_cpu_percent {metrics.cpu_percent}",
            f"",
            f"# HELP ultron_memory_percent Memory usage percentage",
            f"# TYPE ultron_memory_percent gauge",
            f"ultron_memory_percent {metrics.memory_percent}",
            f"",
            f"# HELP ultron_memory_used_bytes Memory used in bytes",
            f"# TYPE ultron_memory_used_bytes gauge",
            f"ultron_memory_used_bytes {metrics.memory_used_gb * 1024**3}",
            f"",
            f"# HELP ultron_disk_percent Disk usage percentage",
            f"# TYPE ultron_disk_percent gauge",
            f"ultron_disk_percent {metrics.disk_percent}",
        ])

        # GPU metrics if available
        if metrics.gpu_percent is not None:
            prometheus_metrics.extend([
                f"",
                f"# HELP ultron_gpu_percent GPU usage percentage",
                f"# TYPE ultron_gpu_percent gauge",
                f"ultron_gpu_percent {metrics.gpu_percent}",
                f"",
                f"# HELP ultron_gpu_memory_percent GPU memory usage percentage",
                f"# TYPE ultron_gpu_memory_percent gauge",
                f"ultron_gpu_memory_percent {metrics.gpu_memory_percent or 0}",
            ])

            if metrics.gpu_temperature:
                prometheus_metrics.extend([
                    f"",
                    f"# HELP ultron_gpu_temperature_celsius GPU temperature in Celsius",
                    f"# TYPE ultron_gpu_temperature_celsius gauge",
                    f"ultron_gpu_temperature_celsius {metrics.gpu_temperature}",
                ])

        # Component health metrics
        prometheus_metrics.append("")
        prometheus_metrics.append("# HELP ultron_component_health Component health status (1=healthy, 0=unhealthy)")
        prometheus_metrics.append("# TYPE ultron_component_health gauge")

        for comp_name, comp_health in self.component_health.items():
            health_value = 1 if comp_health.status == HealthStatus.HEALTHY else 0
            prometheus_metrics.append(f'ultron_component_health{{component="{comp_name}"}} {health_value}')

        return {
            "content_type": "text/plain; version=0.0.4; charset=utf-8",
            "body": "\n".join(prometheus_metrics)
        }

    async def _check_all_components(self) -> List[ComponentHealth]:
        """Check health of all system components."""
        components = []

        # Check voice system
        voice_health = await self._check_voice_health()
        components.append(voice_health)

        # Check Ollama
        ollama_health = await self._check_ollama_health()
        components.append(ollama_health)

        # Check GUI (if enabled)
        gui_health = await self._check_gui_health()
        components.append(gui_health)

        # Check system resources
        system_health = await self._check_system_health()
        components.append(system_health)

        # Run custom health checks
        for check_name, check_function in self.custom_checks.items():
            try:
                check_result = await check_function()
                if isinstance(check_result, dict):
                    status = HealthStatus.HEALTHY if check_result.get("healthy", False) else HealthStatus.UNHEALTHY
                    custom_health = ComponentHealth(
                        name=check_name,
                        status=status,
                        message=check_result.get("message", "Custom check"),
                        last_check=datetime.utcnow(),
                        details=check_result
                    )
                    components.append(custom_health)
            except Exception as e:
                error_health = ComponentHealth(
                    name=check_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    last_check=datetime.utcnow()
                )
                components.append(error_health)

        # Store component health
        for comp in components:
            self.component_health[comp.name] = comp

        return components

    async def check_all_health(self) -> Dict[str, Any]:
        """Public method to check all health components."""
        return await self.check_readiness()

    async def _check_voice_health(self) -> ComponentHealth:
        """Check voice system health."""
        start_time = time.time()

        try:
            # Try to import and initialize voice components
            from ultron_agent.voice import VoiceAssistant

            # Basic availability check
            # TODO: Add actual voice engine ping/test
            status = HealthStatus.HEALTHY
            message = "Voice system available"

        except ImportError as e:
            status = HealthStatus.UNHEALTHY
            message = f"Voice system import failed: {e}"
        except Exception as e:
            status = HealthStatus.DEGRADED
            message = f"Voice system partially available: {e}"

        response_time = (time.time() - start_time) * 1000

        return ComponentHealth(
            name="voice",
            status=status,
            message=message,
            last_check=datetime.utcnow(),
            response_time_ms=response_time
        )

    async def _check_ollama_health(self) -> ComponentHealth:
        """Check Ollama server health."""
        start_time = time.time()

        try:
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get("http://localhost:11434/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        model_count = len(data.get("models", []))
                        status = HealthStatus.HEALTHY
                        message = f"Ollama healthy with {model_count} models"
                        details = {"model_count": model_count}
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"Ollama returned status {response.status}"
                        details = None

        except asyncio.TimeoutError:
            status = HealthStatus.UNHEALTHY
            message = "Ollama timeout"
            details = None
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = f"Ollama connection failed: {e}"
            details = None

        response_time = (time.time() - start_time) * 1000

        return ComponentHealth(
            name="ollama",
            status=status,
            message=message,
            last_check=datetime.utcnow(),
            response_time_ms=response_time,
            details=details
        )

    async def _check_gui_health(self) -> ComponentHealth:
        """Check GUI health."""
        # Simple check - GUI is healthy if it can be imported
        try:
            import tkinter
            status = HealthStatus.HEALTHY
            message = "GUI subsystem available"
        except ImportError:
            status = HealthStatus.DEGRADED
            message = "GUI subsystem not available (tkinter missing)"

        return ComponentHealth(
            name="gui",
            status=status,
            message=message,
            last_check=datetime.utcnow()
        )

    async def _check_system_health(self) -> ComponentHealth:
        """Check system resource health."""
        try:
            # Check critical resources
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determine status based on thresholds
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                status = HealthStatus.UNHEALTHY
                message = "System resources critical"
            elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
                status = HealthStatus.DEGRADED
                message = "System resources under pressure"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources healthy"

            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }

        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Could not check system health: {e}"
            details = None

        return ComponentHealth(
            name="system",
            status=status,
            message=message,
            last_check=datetime.utcnow(),
            details=details
        )

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # GPU metrics
        gpu_percent = None
        gpu_memory_percent = None
        gpu_memory_used_gb = None
        gpu_memory_total_gb = None
        gpu_temperature = None

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                gpu_percent = gpu.load * 100
                gpu_memory_percent = gpu.memoryUtil * 100
                gpu_memory_used_gb = gpu.memoryUsed / 1024
                gpu_memory_total_gb = gpu.memoryTotal / 1024
                gpu_temperature = gpu.temperature
        except Exception as e:
            logger.debug(f"Could not collect GPU metrics: {e}")

        metrics = SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_total_gb=memory.total / (1024**3),
            disk_percent=disk.percent,
            gpu_percent=gpu_percent,
            gpu_memory_percent=gpu_memory_percent,
            gpu_memory_used_gb=gpu_memory_used_gb,
            gpu_memory_total_gb=gpu_memory_total_gb,
            gpu_temperature=gpu_temperature
        )

        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)

        return metrics

    def _calculate_overall_status(self, components: List[ComponentHealth]) -> HealthStatus:
        """Calculate overall status from component health."""
        if not components:
            return HealthStatus.UNKNOWN

        # If any critical component is unhealthy, overall is unhealthy
        critical_components = {"ollama", "system"}
        for comp in components:
            if comp.name in critical_components and comp.status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY

        # If any component is unhealthy (non-critical), overall is degraded
        if any(comp.status == HealthStatus.UNHEALTHY for comp in components):
            return HealthStatus.DEGRADED

        # If any component is degraded, overall is degraded
        if any(comp.status == HealthStatus.DEGRADED for comp in components):
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _get_uptime_seconds(self) -> float:
        """Get system uptime in seconds."""
        try:
            return time.time() - psutil.boot_time()
        except Exception:
            return 0.0


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
