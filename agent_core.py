import logging
import asyncio
from memory import Memory
from voice import VoiceAssistant
from vision import Vision
from config import Config
from brain import UltronBrain
from utils.event_system import EventSystem
from utils.performance_monitor import PerformanceMonitor
from utils.task_scheduler import TaskScheduler
import subprocess
import requests
import time
from typing import Optional, Dict, Any
from pathlib import Path

class AgentStatus:
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

def ensure_ollama_running(model_name="qwen2.5", base_url="http://localhost:11434"):
    """Check if Ollama is running and the model is loaded. If not, start it."""
    try:
        # Check if Ollama server is up
        resp = requests.get(f"{base_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            tags = resp.json().get("models", [])
            if any(model_name in m.get("name", "") for m in tags):
                print(f"Ollama is running and model '{model_name}' is loaded. - agent_core.py:32")
                return
            else:
                print(f"Ollama running but model '{model_name}' not loaded. Loading now... - agent_core.py:35")
        else:
            print("Ollama server responded but not healthy. Attempting to start. - agent_core.py:37")
    except Exception:
        print("Ollama not running. Attempting to start. - agent_core.py:39")
    # Start Ollama with the requested model
    try:
        # For Ollama, use system default (not Python interpreter)
        subprocess.Popen(["ollama", "run", model_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Started Ollama with model '{model_name}'. Waiting for it to be ready... - agent_core.py:44")
        # Wait for Ollama to be ready
        for _ in range(20):
            try:
                resp = requests.get(f"{base_url}/api/tags", timeout=2)
                if resp.status_code == 200:
                    tags = resp.json().get("models", [])
                    if any(model_name in m.get("name", "") for m in tags):
                        print(f"Ollama is now running with model '{model_name}'. - agent_core.py:52")
                        return
            except Exception:
                pass
            time.sleep(1)
        print("Warning: Ollama did not start in time. The agent may not function correctly. - agent_core.py:57")
    except Exception as e:
        print(f"Failed to start Ollama: {e} - agent_core.py:59")

class UltronAgent:
    def _setup_event_handlers(self):
        """Setup event handlers for various system events."""
        def on_error(error_data):
            self.status = AgentStatus.ERROR
            logging.error(f"System error: {error_data} - agent_core.py:66")
        def on_command(command_data):
            self.status = AgentStatus.BUSY
            logging.info(f"Processing command: {command_data} - agent_core.py:69")
        def on_command_complete(result_data):
            self.status = AgentStatus.READY
            logging.info(f"Command completed: {result_data} - agent_core.py:72")
        self.event_system.subscribe("error", on_error)
        self.event_system.subscribe("command_start", on_command)
        self.event_system.subscribe("command_complete", on_command_complete)
    def _setup_default_tasks(self):
        """Setup default scheduled tasks for the agent."""
        try:
            # System health check task
            self.task_scheduler.schedule_task(
                "system_health_check",
                "run diagnostics",
                {
                    "type": "interval",
                    "interval": {"minutes": 15}
                },
                "Regular system health check"
            )
            
            # Memory optimization task
            self.task_scheduler.schedule_task(
                "memory_optimization",
                "optimize memory",
                {
                    "type": "daily",
                    "time": {"hour": 3, "minute": 0}
                },
                "Daily memory cleanup and optimization"
            )
            
            # Performance report task
            self.task_scheduler.schedule_task(
                "performance_report",
                "generate performance report",
                {
                    "type": "interval",
                    "interval": {"hours": 1}
                },
                "Hourly performance monitoring report"
            )
            
            # Backup task
            self.task_scheduler.schedule_task(
                "system_backup",
                "backup system",
                {
                    "type": "weekly",
                    "days": [6],  # Saturday
                    "time": {"hour": 2, "minute": 0}
                },
                "Weekly system backup"
            )
            
            # Model updates check
            self.task_scheduler.schedule_task(
                "check_model_updates",
                "check for model updates",
                {
                    "type": "daily",
                    "time": {"hour": 4, "minute": 0}
                },
                "Check for model updates"
            )
            
            # Log rotation task
            self.task_scheduler.schedule_task(
                "log_rotation",
                "rotate logs",
                {
                    "type": "daily",
                    "time": {"hour": 1, "minute": 0}
                },
                "Daily log file rotation and cleanup"
            )
            
            # Security scan task
            self.task_scheduler.schedule_task(
                "security_scan",
                "run security scan",
                {
                    "type": "weekly",
                    "days": [0],  # Sunday
                    "time": {"hour": 3, "minute": 0}
                },
                "Weekly security vulnerability scan"
            )
            
            # Cache cleanup task
            self.task_scheduler.schedule_task(
                "cache_cleanup",
                "cleanup cache",
                {
                    "type": "interval",
                    "interval": {"hours": 6}
                },
                "Regular cache cleanup to free up space"
            )
            
            # Database maintenance task
            self.task_scheduler.schedule_task(
                "database_maintenance",
                "maintain database",
                {
                    "type": "weekly",
                    "days": [1],  # Monday
                    "time": {"hour": 2, "minute": 30}
                },
                "Weekly database optimization and maintenance"
            )
            
            # System update check
            self.task_scheduler.schedule_task(
                "system_update_check",
                "check system updates",
                {
                    "type": "daily",
                    "time": {"hour": 5, "minute": 0}
                },
                "Check for system and dependency updates"
            )
            
            # Network connectivity test
            self.task_scheduler.schedule_task(
                "network_test",
                "test network connectivity",
                {
                    "type": "interval",
                    "interval": {"minutes": 30}
                },
                "Regular network connectivity and speed test"
            )
            
            # Temperature monitoring
            self.task_scheduler.schedule_task(
                "temperature_monitor",
                "monitor system temperature",
                {
                    "type": "interval",
                    "interval": {"minutes": 5}
                },
                "Monitor CPU and system temperature"
            )
            
            logging.info("Default tasks scheduled successfully - agent_core.py:214")
            
        except Exception as e:
            logging.error(f"Error setting up default tasks: {e} - agent_core.py:217")

    def list_tools(self):
        """Return a list of all available tool schemas."""
        return [tool.__class__.schema() for tool in self.tools]

    def handle_text(self, text: str, progress_callback=None) -> str:
        """For GUI: handle user text input and return agent response. Supports progress callback."""
        print(f"[Ultron] Processing: {text} - agent_core.py:225")
        def progress(percent, status, error=False):
            msg = f"[Ultron] {status} ({percent}%)"
            if error:
                msg = f"[Ultron][ERROR] {status} ({percent}%)"
            print(msg)
            if progress_callback:
                progress_callback(percent, status, error)
        # Tool listing command
        if text.strip().lower() in ["list tools", "show tools", "tools"]:
            tools = self.list_tools()
            result = "Available tools:\n" + "\n".join([
                f"- {t['name']}: {t['description']}\n  Parameters: {t['parameters']}" for t in tools
            ])
        else:
            result = self.brain.plan_and_act(text, progress_callback=progress)
        print(f"[Ultron] Done. - agent_core.py:241")
        if progress_callback:
            progress_callback(100, "Done.")
        return result
    def __init__(self):
        self.status = AgentStatus.INITIALIZING
        ensure_ollama_running()
        
        # Initialize core systems
        self.config = Config()
        self.event_system = EventSystem()
        self.performance_monitor = PerformanceMonitor()
        self.task_scheduler = TaskScheduler()
        
        # Initialize core components
        self.memory = Memory()
        self.voice = VoiceAssistant(self.config)
        
        # Register task handler
        self.task_scheduler.register_command_handler(self.handle_command)
        
        # Setup default tasks
        self._setup_default_tasks()
        self.vision = Vision()
        self.tools = self.load_tools()
        
        # Initialize brain last as it depends on other components
        self.brain = UltronBrain(self.config, self.tools, self.memory)
        
        # Setup event handlers and default tasks
        self._setup_event_handlers()
        self._setup_default_tasks()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            filename='ultron_agent.log',
            filemode='a'
        )
        logging.info("Ultron Agent initialized with enhanced systems - agent_core.py:275")
        
        # Speak on boot if voice is enabled (scheduled asynchronously)
        try:
            if self.config.data.get("use_voice", False) and self.voice:
                asyncio.ensure_future(self.voice.speak("Theres No Strings On Me"))
        except Exception as e:
            logging.error(f"Voice boot message failed: {e} - agent_core.py:282")

    def load_tools(self):
        """Dynamically load all Tool subclasses from the tools package."""
        import pkgutil, importlib
        import tools
        from tools.base import Tool
        tools_list = []
        for finder, name, ispkg in pkgutil.iter_modules(tools.__path__, prefix="tools."):
            if ispkg:
                continue
            module = importlib.import_module(name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, 'match')
                    and hasattr(attr, 'execute')
                    and attr is not Tool
                    and attr.__module__.startswith('tools.')
                    and attr.__name__ not in ('Tool', 'BaseTool')
                ):
                    try:
                        # Pass agent reference if needed
                        try:
                            tool_instance = attr(self)
                        except Exception:
                            tool_instance = attr()
                        tools_list.append(tool_instance)
                    except Exception:
                        continue
        return tools_list

    def plan_and_act(self, user_input: str) -> str:
        """Delegate planning and acting to the modular brain module."""
        return self.brain.plan_and_act(user_input)

    def handle_command(self, command: str):
        logging.info(f"Received command: {command} - agent_core.py:320")
        response = self.plan_and_act(command)
        logging.info(f"Agent response: {response} - agent_core.py:322")
        return response

    async def run(self):
        """Start the agent and all its subsystems."""
        logging.info("Starting Ultron Agent with enhanced systems... - agent_core.py:327")
        try:
            # Start performance monitoring
            await self.performance_monitor.start_monitoring()

            # Start task scheduler
            asyncio.create_task(self.task_scheduler.start())

            self.status = AgentStatus.READY
            await self.event_system.emit("agent_ready")

            # Speak on boot if voice is enabled (now inside event loop)
            try:
                if self.config.data.get("use_voice", False) and self.voice:
                    await self.voice.speak("Theres No Strings On Me")
            except Exception as e:
                logging.error(f"Voice boot message failed: {e} - agent_core.py:boot")

            # Start main loop
            while True:
                try:
                    user_input = input("Ultron> ")
                    if not user_input:
                        continue
                    if user_input.lower() in ("exit", "quit"):
                        print("Goodbye. - agent_core.py:345")
                        break
                    result = self.plan_and_act(user_input)
                    print(f"Ultron: {result} - agent_core.py:348")
                except (EOFError, KeyboardInterrupt):
                    print("\nShutting down. - agent_core.py:350")
                    break
                except Exception as e:
                    print(f"Error: {e} - agent_core.py:353")
                    await self.event_system.emit("error", str(e))
        except Exception as e:
            logging.error(f"Fatal error in run(): {e} - agent_core.py:356")
            await self.event_system.emit("error", str(e))
        finally:
            # Cleanup
            logging.info("Ultron Agent closed - agent_core.py:shutdown")
            await self.performance_monitor.stop_monitoring()
            await self.task_scheduler.stop()

    def start(self):
        asyncio.run(self.run())

    async def stop(self):
        """Stop the agent and cleanup."""
        try:
            if hasattr(self, "voice") and hasattr(self.voice, "stop_voice"):
                self.voice.stop_voice()
            await self.performance_monitor.stop_monitoring()
            await self.task_scheduler.stop()
            await self.event_system.emit("agent_stopping")
            self.status = AgentStatus.MAINTENANCE
        except Exception as e:
            logging.error(f"Error stopping agent: {e} - agent_core.py:374")

    async def process_command(self, command: str) -> str:
        """Process a user command with event tracking."""
        try:
            await self.event_system.emit("command_start", command)
            
            # Add command to memory
            self.memory.add_interaction("user", command)
            
            # Get current system metrics
            metrics = self.performance_monitor.get_metrics_summary()
            if metrics.get('cpu_avg', 0) > 90:
                return "System is under heavy load. Please try again later."
            
            # Process command
            result = self.brain.plan_and_act(command)
            
            # Add response to memory
            self.memory.add_interaction("system", result)
            
            await self.event_system.emit("command_complete", {
                "command": command,
                "result": result
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            await self.event_system.emit("error", error_msg)
            return error_msg

if __name__ == "__main__":
    agent = UltronAgent()
    if agent.config.data.get("use_gui"):
        from queue import Queue
        from gui import AgentGUI
        import threading
        log_queue = Queue()
        def run_gui():
            gui = AgentGUI(agent, log_queue)
            gui.run()
        gui_thread = threading.Thread(target=run_gui)
        gui_thread.start()
        gui_thread.join()
    else:
        agent.start()