"""Monitoring demonstration and integration examples."""
import asyncio
import time
from typing import Dict, Any

from ultron_agent.health import get_health_checker
from ultron_agent.logging_config import setup_logging, get_logger

logger = get_logger("ultron.monitoring_demo", source="demo")


class MonitoringDemo:
    """Demonstration of enhanced monitoring features."""
    
    def __init__(self):
        self.health_checker = get_health_checker()
        
    async def simulate_workload(self, commands: int = 10, error_rate: float = 0.1):
        """Simulate a workload with commands and errors."""
        logger.info(f"Starting workload simulation: {commands} commands, {error_rate*100}% error rate")
        
        # Start a session
        self.health_checker.record_session_start()
        
        for i in range(commands):
            command_name = f"simulated_command_{i}"
            
            # Simulate variable execution times
            execution_time = 0.1 + (i % 5) * 0.05  # 0.1 to 0.3 seconds
            
            # Simulate errors based on error rate
            success = (i % int(1 / error_rate if error_rate > 0 else 1)) != 0
            
            # Record command execution
            start_time = time.time()
            await asyncio.sleep(execution_time)  # Simulate work
            actual_time = time.time() - start_time
            
            self.health_checker.record_command_execution(command_name, actual_time, success)
            
            # Simulate some voice commands
            if i % 3 == 0:
                self.health_checker.record_voice_command()
            
            # Simulate GUI interactions
            if i % 4 == 0:
                self.health_checker.record_gui_interaction()
        
        # Set some custom metrics
        self.health_checker.set_custom_metric("demo_workload_size", commands)
        self.health_checker.set_custom_metric("demo_completion_time", time.time())
        
        logger.info("Workload simulation completed")
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get a summary of current monitoring data."""
        metrics_response = await self.health_checker.get_metrics()
        usage = self.health_checker.usage_metrics
        
        summary = {
            "usage_stats": {
                "total_commands": usage.commands_executed,
                "total_errors": usage.error_count,
                "error_rate_percent": (usage.error_count / usage.commands_executed * 100) if usage.commands_executed > 0 else 0,
                "api_requests": usage.api_requests,
                "api_errors": usage.api_errors,
                "voice_commands": usage.voice_commands,
                "gui_interactions": usage.gui_interactions,
                "sessions": usage.session_count,
                "last_activity": usage.last_activity.isoformat() if usage.last_activity else None
            },
            "performance": {
                "avg_response_time_ms": usage.avg_response_time * 1000,
                "p95_response_time_ms": usage.p95_response_time * 1000,
                "p99_response_time_ms": usage.p99_response_time * 1000
            },
            "custom_metrics": dict(self.health_checker.custom_metrics),
            "prometheus_metrics_size": len(metrics_response["body"])
        }
        
        return summary
    
    def print_monitoring_dashboard(self, summary: Dict[str, Any]):
        """Print a monitoring dashboard-style output."""
        print("\n" + "="*60)
        print("         ULTRON AGENT MONITORING DASHBOARD")
        print("="*60)
        
        usage = summary["usage_stats"]
        perf = summary["performance"]
        
        print(f"\n📊 USAGE STATISTICS:")
        print(f"   Commands Executed:    {usage['total_commands']:>8}")
        print(f"   Command Errors:       {usage['total_errors']:>8}")
        print(f"   Error Rate:          {usage['error_rate_percent']:>7.1f}%")
        print(f"   API Requests:         {usage['api_requests']:>8}")
        print(f"   Voice Commands:       {usage['voice_commands']:>8}")
        print(f"   GUI Interactions:     {usage['gui_interactions']:>8}")
        print(f"   Active Sessions:      {usage['sessions']:>8}")
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Avg Response Time:   {perf['avg_response_time_ms']:>7.1f}ms")
        print(f"   95th Percentile:     {perf['p95_response_time_ms']:>7.1f}ms")
        print(f"   99th Percentile:     {perf['p99_response_time_ms']:>7.1f}ms")
        
        if summary["custom_metrics"]:
            print(f"\n🔧 CUSTOM METRICS:")
            for name, value in summary["custom_metrics"].items():
                print(f"   {name:<20} {value:>8}")
        
        print(f"\n📈 MONITORING STATUS:")
        print(f"   Prometheus Metrics:   {summary['prometheus_metrics_size']:>8} bytes")
        print(f"   Last Activity:        {usage['last_activity'] or 'Never'}")
        
        print("\n" + "="*60)


async def main():
    """Main demo function."""
    setup_logging()
    
    demo = MonitoringDemo()
    
    print("🚀 ULTRON Agent Monitoring Enhancement Demo")
    print("\nRunning workload simulation...")
    
    # Simulate different workloads
    await demo.simulate_workload(commands=20, error_rate=0.15)
    
    # Get and display monitoring summary
    summary = await demo.get_monitoring_summary()
    demo.print_monitoring_dashboard(summary)
    
    print(f"\n✅ Enhanced monitoring features demonstrated!")
    print(f"   - Usage tracking: Commands, errors, API requests")
    print(f"   - Performance metrics: Response times, percentiles")
    print(f"   - Custom metrics: Business logic tracking")
    print(f"   - Prometheus format: Ready for Grafana/monitoring tools")
    print(f"\n📊 Access metrics at: http://localhost:8000/metrics")
    print(f"📋 Health status at:  http://localhost:8000/healthz")


if __name__ == "__main__":
    asyncio.run(main())