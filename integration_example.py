"""Example integration showing how to use enhanced monitoring in ULTRON Agent components."""

import asyncio
import time
import random
from typing import Optional
from ultron_agent.health import get_health_checker
from ultron_agent.logging_config import setup_logging, get_logger, LogContext

logger = get_logger("ultron.integration_example", source="example")


class MonitoredAITool:
    """Example AI tool with monitoring integration."""
    
    def __init__(self, name: str):
        self.name = name
        self.health_checker = get_health_checker()
        
        # Register custom health check
        self.health_checker.register_check(
            f"{name}_tool", 
            self._health_check
        )
    
    async def _health_check(self) -> bool:
        """Custom health check for this tool."""
        # Simulate health check logic
        return random.random() > 0.1  # 90% healthy
    
    async def execute_command(self, command: str, context: Optional[dict] = None) -> dict:
        """Execute a command with full monitoring integration."""
        
        with LogContext(f"{self.name}_command", command=command, tool=self.name) as ctx:
            start_time = time.time()
            
            try:
                ctx.log(f"Executing command: {command}")
                
                # Simulate command processing
                processing_time = random.uniform(0.1, 0.5)
                await asyncio.sleep(processing_time)
                
                # Simulate occasional failures
                if random.random() < 0.05:  # 5% failure rate
                    raise Exception("Simulated processing error")
                
                # Record successful execution
                execution_time = time.time() - start_time
                self.health_checker.record_command_execution(
                    f"{self.name}:{command}", 
                    execution_time, 
                    success=True
                )
                
                # Update custom metrics
                self.health_checker.set_custom_metric(
                    f"{self.name}_last_execution_time", 
                    execution_time
                )
                
                ctx.log(f"Command completed successfully in {execution_time:.3f}s")
                
                return {
                    "success": True,
                    "result": f"Command '{command}' executed by {self.name}",
                    "execution_time": execution_time
                }
                
            except Exception as e:
                # Record failed execution
                execution_time = time.time() - start_time
                self.health_checker.record_command_execution(
                    f"{self.name}:{command}", 
                    execution_time, 
                    success=False
                )
                
                ctx.log(f"Command failed: {str(e)}", level=40)  # ERROR level
                
                return {
                    "success": False,
                    "error": str(e),
                    "execution_time": execution_time
                }


class MonitoredVoiceInterface:
    """Example voice interface with monitoring."""
    
    def __init__(self):
        self.health_checker = get_health_checker()
        
    def process_voice_command(self, audio_data: bytes) -> str:
        """Process voice command with monitoring."""
        
        # Record voice command usage
        self.health_checker.record_voice_command()
        
        # Simulate voice processing
        command = "example voice command"
        
        logger.info("Voice command processed", extra={
            "command": command,
            "audio_size": len(audio_data),
            "source": "voice"
        })
        
        return command


class MonitoredGUI:
    """Example GUI with interaction tracking."""
    
    def __init__(self):
        self.health_checker = get_health_checker()
    
    def handle_button_click(self, button_id: str) -> None:
        """Handle GUI button click with monitoring."""
        
        # Record GUI interaction
        self.health_checker.record_gui_interaction()
        
        # Update custom metric for button usage
        current_count = self.health_checker.custom_metrics.get(f"button_{button_id}_clicks", 0)
        self.health_checker.set_custom_metric(f"button_{button_id}_clicks", current_count + 1)
        
        logger.info("GUI interaction", extra={
            "interaction_type": "button_click",
            "button_id": button_id,
            "source": "gui"
        })


class MonitoredSession:
    """Example session manager with monitoring."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.health_checker = get_health_checker()
        self.start_time = time.time()
        
        # Record session start
        self.health_checker.record_session_start()
        
        logger.info("Session started", extra={
            "session_id": session_id,
            "source": "session"
        })
    
    def end_session(self):
        """End session with monitoring."""
        duration = time.time() - self.start_time
        
        # Update session metrics
        self.health_checker.set_custom_metric("last_session_duration", duration)
        
        logger.info("Session ended", extra={
            "session_id": self.session_id,
            "duration_seconds": duration,
            "source": "session"
        })


async def demonstrate_monitoring_integration():
    """Demonstrate comprehensive monitoring integration."""
    
    print("🚀 Starting ULTRON Agent Monitoring Integration Demo")
    print("=" * 60)
    
    # Initialize components with monitoring
    ai_tool = MonitoredAITool("GPT4Tool")
    voice_interface = MonitoredVoiceInterface()
    gui = MonitoredGUI()
    
    # Start a monitored session
    session = MonitoredSession("demo_session_001")
    
    # Simulate various interactions
    print("\n📝 Simulating AI tool operations...")
    for i in range(5):
        command = f"analyze_data_batch_{i}"
        result = await ai_tool.execute_command(command)
        print(f"   {command}: {'✅' if result['success'] else '❌'} ({result['execution_time']:.3f}s)")
    
    print("\n🎤 Simulating voice interactions...")
    for i in range(3):
        voice_interface.process_voice_command(b"fake_audio_data" * 100)
        print(f"   Voice command {i+1} processed")
    
    print("\n🖱️  Simulating GUI interactions...")
    buttons = ["start", "stop", "settings", "help"]
    for button in buttons:
        gui.handle_button_click(button)
        print(f"   Button '{button}' clicked")
    
    # End session
    session.end_session()
    
    # Display current metrics
    print("\n📊 Current Monitoring Status:")
    health = get_health_checker()
    usage = health.usage_metrics
    
    print(f"   Commands Executed: {usage.commands_executed}")
    print(f"   Command Errors: {usage.error_count}")
    print(f"   Voice Commands: {usage.voice_commands}")
    print(f"   GUI Interactions: {usage.gui_interactions}")
    print(f"   Active Sessions: {usage.session_count}")
    print(f"   Custom Metrics: {len(health.custom_metrics)}")
    
    # Show custom metrics
    if health.custom_metrics:
        print("\n🔧 Custom Metrics:")
        for name, value in health.custom_metrics.items():
            print(f"   {name}: {value}")
    
    # Get and display sample Prometheus metrics
    print("\n📈 Sample Prometheus Metrics:")
    metrics = await health.get_metrics()
    lines = metrics["body"].split("\n")
    
    # Show key metrics
    key_metrics = [
        "ultron_commands_total",
        "ultron_error_rate", 
        "ultron_voice_commands_total",
        "ultron_response_time_seconds"
    ]
    
    for line in lines:
        for metric in key_metrics:
            if line.startswith(metric + " "):
                print(f"   {line}")
    
    print("\n" + "=" * 60)
    print("✅ Monitoring integration demonstration complete!")
    print("\n💡 Key Integration Points:")
    print("   • Command execution tracking with success/failure")
    print("   • Voice and GUI interaction monitoring")
    print("   • Custom metrics for business logic")
    print("   • Structured logging with correlation")
    print("   • Health checks for custom components")
    print("   • Session lifecycle tracking")


async def main():
    """Main demo function."""
    # Setup logging
    setup_logging()
    
    # Run the demonstration
    await demonstrate_monitoring_integration()
    
    print(f"\n🔗 Integration Examples:")
    print(f"   • Metrics endpoint: http://localhost:8000/metrics")
    print(f"   • Health check: http://localhost:8000/healthz")
    print(f"   • Logs directory: ./logs/")
    print(f"   • Grafana dashboard: ./docs/grafana-dashboard.json")


if __name__ == "__main__":
    asyncio.run(main())