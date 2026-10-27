"""
ULTRON Agent Performance Dashboard Tool
Real-time performance monitoring and analytics interface
"""

import json
from datetime import datetime
from typing import Optional

from utils.performance_analytics import get_performance_analytics
from utils.cache_manager import get_cache_manager
from utils.ultron_logger import get_logger

logger = get_logger("performance_dashboard")


class PerformanceDashboardTool:
    """
    Real-time performance monitoring dashboard.
    Provides insights into system performance, traces, and anomalies.
    """
    
    name = "Performance Dashboard"
    description = "Monitor system performance, traces, and detect anomalies"
    
    def __init__(self):
        try:
            self.analytics = get_performance_analytics()
            self.cache = get_cache_manager()
            logger.info("Performance Dashboard Tool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize dashboard: {e}")
            self.analytics = None
            self.cache = None
    
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        keywords = [
            'performance', 'dashboard', 'monitor', 'trace',
            'anomaly', 'latency', 'response time', 'metrics'
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in keywords)
    
    def execute(self, command: str) -> str:
        """Execute dashboard command"""
        if not self.analytics:
            return "❌ Performance analytics not available"
        
        command_lower = command.lower()
        
        try:
            if 'dashboard' in command_lower or 'overview' in command_lower:
                return self._show_dashboard()
            
            elif 'trace' in command_lower:
                return self._show_traces()
            
            elif 'anomaly' in command_lower or 'anomalies' in command_lower:
                return self._show_anomalies()
            
            elif 'system' in command_lower:
                return self._show_system_metrics()
            
            elif 'cache' in command_lower:
                return self._show_cache_performance()
            
            else:
                return self._show_dashboard()
        
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return f"Error displaying dashboard: {str(e)}"
    
    def _show_dashboard(self) -> str:
        """Show comprehensive performance dashboard"""
        try:
            dashboard_data = self.analytics.get_dashboard_data()
            stats = dashboard_data['stats']
            system = dashboard_data['system_metrics']
            trace_summary = dashboard_data['trace_summary']
            
            dashboard = f"""
╔══════════════════════════════════════════════════════════════════╗
║          ULTRON PERFORMANCE DASHBOARD                            ║
╚══════════════════════════════════════════════════════════════════╝

📊 SYSTEM METRICS (Real-time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CPU Usage:     {system.get('cpu_percent', 0):.1f}%
Memory Usage:  {system.get('memory_percent', 0):.1f}% ({system.get('memory_used_mb', 0):.1f} MB)
Disk Usage:    {system.get('disk_percent', 0):.1f}% ({system.get('disk_used_gb', 0):.1f} GB)

⚡ PERFORMANCE METRICS (Last 5 minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Traces:       {stats.get('total_traces', 0):,}
Total Spans:        {stats.get('total_spans', 0):,}
Avg Response Time:  {stats.get('avg_response_time_ms', 0):.2f}ms

Active Traces:      {trace_summary.get('total_traces', 0)}
P95 Duration:       {trace_summary.get('p95_duration_ms', 0):.2f}ms
Success Rate:       {trace_summary.get('success_rate', 0):.1f}%
Active Spans:       {trace_summary.get('active_spans', 0)}

🔔 ANOMALY DETECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Anomalies:    {stats.get('total_anomalies', 0)}
Recent Alerts:      {len(dashboard_data.get('recent_anomalies', []))}

"""
            
            # Add recent anomalies if any
            recent_anomalies = dashboard_data.get('recent_anomalies', [])
            if recent_anomalies:
                dashboard += "⚠️  RECENT ANOMALIES:\n"
                for anomaly in recent_anomalies[:3]:
                    severity_icon = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(anomaly.get('severity', 'low'), '⚪')
                    
                    dashboard += f"{severity_icon} {anomaly.get('message', 'Unknown anomaly')}\n"
            
            # Add slow traces if any
            slow_traces = dashboard_data.get('slow_traces', [])
            if slow_traces:
                dashboard += "\n🐌 SLOW TRACES (>1s):\n"
                for trace in slow_traces[:3]:
                    dashboard += f"  • {trace.get('operation', 'unknown')}: {trace.get('duration_ms', 0):.2f}ms\n"
            
            dashboard += f"\n📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            dashboard += "\n\nStatus: ✅ OPERATIONAL"
            
            return dashboard.strip()
        
        except Exception as e:
            logger.error(f"Error showing dashboard: {e}")
            return f"Error displaying dashboard: {str(e)}"
    
    def _show_traces(self) -> str:
        """Show trace analysis"""
        try:
            trace_summary = self.analytics.get_trace_summary(window_seconds=300)
            slow_traces = self.analytics.get_slow_traces(threshold_ms=500, limit=10)
            
            report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          TRACE ANALYSIS (Last 5 Minutes)                         ║
╚══════════════════════════════════════════════════════════════════╝

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Traces:       {trace_summary.get('total_traces', 0)}
Avg Duration:       {trace_summary.get('avg_duration_ms', 0):.2f}ms
Min Duration:       {trace_summary.get('min_duration_ms', 0):.2f}ms
Max Duration:       {trace_summary.get('max_duration_ms', 0):.2f}ms
P95 Duration:       {trace_summary.get('p95_duration_ms', 0):.2f}ms
Success Rate:       {trace_summary.get('success_rate', 0):.1f}%

🐌 SLOWEST TRACES (>{500}ms)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            if slow_traces:
                for i, trace in enumerate(slow_traces, 1):
                    status_icon = '✅' if trace.status == 'success' else '❌'
                    report += f"{i}. {status_icon} {trace.operation}\n"
                    report += f"   Duration: {trace.duration_ms:.2f}ms | Status: {trace.status}\n"
                    if trace.tags:
                        report += f"   Tags: {json.dumps(trace.tags, indent=4)}\n"
            else:
                report += "No slow traces detected. Performance is optimal! 🚀\n"
            
            return report.strip()
        
        except Exception as e:
            logger.error(f"Error showing traces: {e}")
            return f"Error displaying traces: {str(e)}"
    
    def _show_anomalies(self) -> str:
        """Show anomaly detection results"""
        try:
            anomalies = self.analytics.get_recent_anomalies(limit=20)
            
            report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          ANOMALY DETECTION REPORT                                ║
╚══════════════════════════════════════════════════════════════════╝

Total Anomalies Detected: {len(anomalies)}

"""
            
            if anomalies:
                severity_groups = {'critical': [], 'high': [], 'medium': [], 'low': []}
                for anomaly in anomalies:
                    severity = anomaly.severity
                    severity_groups[severity].append(anomaly)
                
                for severity in ['critical', 'high', 'medium', 'low']:
                    group = severity_groups[severity]
                    if group:
                        icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                        report += f"\n{icon} {severity.upper()} SEVERITY ({len(group)} alerts)\n"
                        report += "━" * 66 + "\n"
                        
                        for anomaly in group[:5]:  # Show max 5 per severity
                            timestamp = datetime.fromtimestamp(anomaly.timestamp)
                            report += f"• {timestamp.strftime('%H:%M:%S')} - {anomaly.message}\n"
                            report += f"  Value: {anomaly.current_value:.2f} (expected: {anomaly.expected_range[0]:.2f}-{anomaly.expected_range[1]:.2f})\n"
            else:
                report += "✅ No anomalies detected. System is performing normally.\n"
            
            return report.strip()
        
        except Exception as e:
            logger.error(f"Error showing anomalies: {e}")
            return f"Error displaying anomalies: {str(e)}"
    
    def _show_system_metrics(self) -> str:
        """Show detailed system metrics"""
        try:
            system = self.analytics.get_system_metrics()
            
            # Get metric statistics for key metrics
            cpu_stats = self.analytics.get_metric_stats('system.cpu_percent', window_seconds=300)
            memory_stats = self.analytics.get_metric_stats('system.memory_percent', window_seconds=300)
            
            report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          SYSTEM RESOURCE METRICS                                 ║
╚══════════════════════════════════════════════════════════════════╝

💻 CPU METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current:    {system.get('cpu_percent', 0):.1f}%
"""
            
            if cpu_stats:
                report += f"""Average:    {cpu_stats.get('mean', 0):.1f}%
Min:        {cpu_stats.get('min', 0):.1f}%
Max:        {cpu_stats.get('max', 0):.1f}%
P95:        {cpu_stats.get('p95', 0):.1f}%
"""
            
            report += f"""
💾 MEMORY METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current:    {system.get('memory_percent', 0):.1f}%
Used:       {system.get('memory_used_mb', 0):.1f} MB
Available:  {system.get('memory_available_mb', 0):.1f} MB
"""
            
            if memory_stats:
                report += f"""Average:    {memory_stats.get('mean', 0):.1f}%
Min:        {memory_stats.get('min', 0):.1f}%
Max:        {memory_stats.get('max', 0):.1f}%
"""
            
            report += f"""
💽 DISK METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Usage:      {system.get('disk_percent', 0):.1f}%
Used:       {system.get('disk_used_gb', 0):.1f} GB
Free:       {system.get('disk_free_gb', 0):.1f} GB

🌐 NETWORK METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bytes Sent: {system.get('net_bytes_sent', 0) / 1024 / 1024:.2f} MB
Bytes Recv: {system.get('net_bytes_recv', 0) / 1024 / 1024:.2f} MB
"""
            
            return report.strip()
        
        except Exception as e:
            logger.error(f"Error showing system metrics: {e}")
            return f"Error displaying system metrics: {str(e)}"
    
    def _show_cache_performance(self) -> str:
        """Show cache performance metrics"""
        if not self.cache:
            return "❌ Cache manager not available"
        
        try:
            stats = self.cache.get_stats()
            
            hit_rate = float(stats['hit_rate'].strip('%'))
            performance_status = '🟢 Excellent' if hit_rate > 70 else '🟡 Good' if hit_rate > 50 else '🔴 Needs Tuning'
            
            report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          CACHE PERFORMANCE ANALYSIS                              ║
╚══════════════════════════════════════════════════════════════════╝

📊 CACHE EFFICIENCY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hit Rate:       {stats['hit_rate']} {performance_status}
Total Hits:     {stats['hits']:,}
Total Misses:   {stats['misses']:,}

💾 STORAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cached Entries: {stats['entries']:,}
Cache Size:     {stats['size_mb']} MB
Backend:        {'Redis + SQLite' if stats['redis_connected'] else 'SQLite Only'}

⚡ OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sets:           {stats['sets']:,}
Deletes:        {stats['deletes']:,}
Evictions:      {stats['evictions']:,}

💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            if hit_rate < 50:
                report += "• Consider increasing cache TTL\n"
                report += "• Review cache invalidation strategy\n"
            elif hit_rate < 70:
                report += "• Cache is performing well\n"
                report += "• Minor optimizations possible\n"
            else:
                report += "• Cache is performing excellently!\n"
                report += "• Current configuration is optimal\n"
            
            return report.strip()
        
        except Exception as e:
            logger.error(f"Error showing cache performance: {e}")
            return f"Error displaying cache performance: {str(e)}"
    
    @classmethod
    def schema(cls):
        """Return tool schema for AI integration"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Dashboard command (dashboard, traces, anomalies, system, cache)"
                }
            }
        }


# Export for tool discovery
__all__ = ['PerformanceDashboardTool']
