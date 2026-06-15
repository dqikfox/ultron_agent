"""
Performance Monitoring Tool for ULTRON Agent

Provides comprehensive performance metrics, monitoring, and optimization insights
"""

import logging
import psutil
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import json
from pathlib import Path

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision


class PerformanceMonitor:
    """
    Tool for monitoring system and application performance metrics
    """

    name = "Performance Monitor"
    description = "Monitor system performance, memory usage, CPU utilization, and provide optimization recommendations"

    def __init__(self):
        self.monitoring_active = False
        self.metrics_history = []
        self.max_history_size = 1000
        self.monitor_thread = None
        self.metrics_file = Path("logs/performance_metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        self.load_metrics_history()

    def match(self, command: str) -> bool:
        """Check if command matches performance monitoring operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "performance", "monitor", "metrics", "cpu usage", "memory usage",
            "system stats", "optimization", "benchmark", "performance report"
        ])

    def execute(self, command: str) -> str:
        """Execute performance monitoring operations"""
        try:
            command_lower = command.lower()

            if "start monitoring" in command_lower or "begin monitoring" in command_lower:
                return self.start_monitoring()
            elif "stop monitoring" in command_lower:
                return self.stop_monitoring()
            elif "performance report" in command_lower or "metrics report" in command_lower:
                return self.generate_performance_report()
            elif "system stats" in command_lower or "current stats" in command_lower:
                return self.get_current_system_stats()
            elif "memory usage" in command_lower:
                return self.get_memory_analysis()
            elif "cpu usage" in command_lower:
                return self.get_cpu_analysis()
            elif "optimization" in command_lower:
                return self.get_optimization_recommendations()
            else:
                return self.get_help()

        except Exception as e:
            log_error("performance_monitor", f"Performance monitoring failed: {e}")
            return f"Performance monitoring failed: {str(e)}"

    def start_monitoring(self) -> str:
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            return "Performance monitoring is already active"

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        log_info("performance_monitor", "Started continuous performance monitoring")
        return "✅ Performance monitoring started. Collecting metrics in background."

    def stop_monitoring(self) -> str:
        """Stop continuous performance monitoring"""
        if not self.monitoring_active:
            return "Performance monitoring is not currently active"

        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.save_metrics_history()
        log_info("performance_monitor", "Stopped performance monitoring")
        return "✅ Performance monitoring stopped. Metrics saved to logs."

    def get_current_system_stats(self) -> str:
        """Get current system performance statistics"""
        try:
            # CPU stats
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory stats
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB

            # Disk stats
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB

            # Network stats
            net = psutil.net_io_counters()
            bytes_sent = net.bytes_sent / (1024**2)  # MB
            bytes_recv = net.bytes_recv / (1024**2)  # MB

            # Process info
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024**2)  # MB
            process_cpu = process.cpu_percent()

            stats = f"""
📊 **Current System Performance Statistics**

**CPU:**
• Usage: {cpu_percent:.1f}%
• Cores: {cpu_count}
• Frequency: {cpu_freq.current:.0f}MHz (max: {cpu_freq.max:.0f}MHz)
• ULTRON Process CPU: {process_cpu:.1f}%

**Memory:**
• Usage: {memory_percent:.1f}% ({memory_used:.1f}GB / {memory_total:.1f}GB)
• ULTRON Process Memory: {process_memory:.1f}MB

**Disk:**
• Usage: {disk_percent:.1f}% ({disk_used:.1f}GB / {disk_total:.1f}GB)

**Network (since boot):**
• Sent: {bytes_sent:.1f}MB
• Received: {bytes_recv:.1f}MB

**System Load:**
• Load Average: {os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'}
"""

            return stats

        except Exception as e:
            log_error("performance_monitor", f"Failed to get system stats: {e}")
            return f"Failed to get system stats: {str(e)}"

    def get_memory_analysis(self) -> str:
        """Get detailed memory usage analysis"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            analysis = f"""
🧠 **Memory Usage Analysis**

**Physical Memory:**
• Total: {memory.total / (1024**3):.1f}GB
• Used: {memory.used / (1024**3):.1f}GB ({memory.percent:.1f}%)
• Available: {memory.available / (1024**3):.1f}GB
• Cached: {getattr(memory, 'cached', 0) / (1024**3):.1f}GB

**Swap Memory:**
• Total: {swap.total / (1024**3):.1f}GB
• Used: {swap.used / (1024**3):.1f}GB ({swap.percent:.1f}%)
• Free: {swap.free / (1024**3):.1f}GB

**Top Memory Processes:**
"""
            # Get top 5 memory-consuming processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append((proc.info['name'], proc.info['memory_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            top_processes = sorted(processes, key=lambda x: x[1], reverse=True)[:5]
            for name, mem_percent in top_processes:
                analysis += f"• {name}: {mem_percent:.1f}%\n"

            return analysis

        except Exception as e:
            log_error("performance_monitor", f"Memory analysis failed: {e}")
            return f"Memory analysis failed: {str(e)}"

    def get_cpu_analysis(self) -> str:
        """Get detailed CPU usage analysis"""
        try:
            cpu_times = psutil.cpu_times_percent(interval=1)

            analysis = f"""
⚡ **CPU Usage Analysis**

**Overall CPU Usage:**
• User: {cpu_times.user:.1f}%
• System: {cpu_times.system:.1f}%
• Idle: {cpu_times.idle:.1f}%
• CPU Count: {psutil.cpu_count()} logical, {psutil.cpu_count(logical=False)} physical

**Top CPU Processes:**
"""
            # Get top 5 CPU-consuming processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc.cpu_percent()  # First call to get initial value
                    time.sleep(0.1)
                    cpu_percent = proc.cpu_percent()
                    processes.append((proc.info['name'], cpu_percent))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            top_processes = sorted(processes, key=lambda x: x[1], reverse=True)[:5]
            for name, cpu_percent in top_processes:
                analysis += f"• {name}: {cpu_percent:.1f}%\n"

            return analysis

        except Exception as e:
            log_error("performance_monitor", f"CPU analysis failed: {e}")
            return f"CPU analysis failed: {str(e)}"

    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report from collected metrics"""
        if not self.metrics_history:
            return "No performance metrics collected yet. Start monitoring first."

        try:
            # Calculate averages and trends
            recent_metrics = self.metrics_history[-min(60, len(self.metrics_history)):]  # Last hour or available

            avg_cpu = sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m['memory_percent'] for m in recent_metrics) / len(recent_metrics)
            max_cpu = max(m['cpu_percent'] for m in recent_metrics)
            max_memory = max(m['memory_percent'] for m in recent_metrics)

            report = f"""
📈 **Performance Report** (Last {len(recent_metrics)} measurements)

**Average Metrics:**
• CPU Usage: {avg_cpu:.1f}%
• Memory Usage: {avg_memory:.1f}%

**Peak Metrics:**
• Max CPU: {max_cpu:.1f}%
• Max Memory: {max_memory:.1f}%

**Trends:**
• CPU Stability: {'Stable' if max_cpu - min(m['cpu_percent'] for m in recent_metrics) < 20 else 'Variable'}
• Memory Stability: {'Stable' if max_memory - min(m['memory_percent'] for m in recent_metrics) < 20 else 'Variable'}

**Recommendations:**
{self.get_optimization_recommendations()}
"""

            return report

        except Exception as e:
            log_error("performance_monitor", f"Report generation failed: {e}")
            return f"Report generation failed: {str(e)}"

    def get_optimization_recommendations(self) -> str:
        """Get optimization recommendations based on current metrics"""
        try:
            current_stats = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()

            recommendations = []

            if current_stats.percent > 80:
                recommendations.append("⚠️ High memory usage detected. Consider closing unused applications.")
            if cpu_percent > 80:
                recommendations.append("⚠️ High CPU usage detected. Check for resource-intensive processes.")
            if len(self.metrics_history) > 100:
                recommendations.append("✅ Monitoring active. Consider reviewing historical trends.")

            if not recommendations:
                recommendations.append("✅ System performance looks good.")

            return "\n".join(recommendations)

        except Exception as e:
            return "Unable to generate recommendations"

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect current metrics
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'memory_used': psutil.virtual_memory().used,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'process_memory': psutil.Process().memory_info().rss,
                    'process_cpu': psutil.Process().cpu_percent()
                }

                self.metrics_history.append(metrics)

                # Maintain history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]

                time.sleep(10)  # Collect every 10 seconds

            except Exception as e:
                log_error("performance_monitor", f"Monitoring loop error: {e}")
                time.sleep(30)  # Wait longer on error

    def load_metrics_history(self):
        """Load metrics history from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    self.metrics_history = json.load(f)
        except Exception as e:
            log_error("performance_monitor", f"Failed to load metrics history: {e}")

    def save_metrics_history(self):
        """Save metrics history to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            log_error("performance_monitor", f"Failed to save metrics history: {e}")

    def get_help(self) -> str:
        """Get help information for the tool"""
        return """
📊 **Performance Monitor Tool**

**Capabilities:**
• Real-time system performance monitoring
• CPU, memory, and disk usage tracking
• Process-level performance analysis
• Historical metrics collection
• Optimization recommendations

**Commands:**
• "start monitoring" - Begin continuous performance monitoring
• "stop monitoring" - Stop monitoring and save metrics
• "performance report" - Generate comprehensive performance report
• "system stats" - Get current system statistics
• "memory usage" - Detailed memory analysis
• "cpu usage" - Detailed CPU analysis
• "optimization" - Get performance recommendations

**Features:**
• Background monitoring with automatic data collection
• Metrics persistence across sessions
• Trend analysis and stability assessment
• Process-level insights
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Performance monitoring command"
                    }
                },
                "required": ["command"]
            }
        }
