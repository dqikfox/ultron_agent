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
from typing import Optional, Dict, Any
from pathlib import Path
from utils.startup import ensure_ollama_running

class AgentStatus:
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class UltronAgent:
    def _setup_event_handlers(self):
        """Setup event handlers for various system events."""
        def on_error(error_data):
            self.status = AgentStatus.ERROR
            logging.error(f"System error: {error_data} - agent_core.py:27")
        def on_command(command_data):
            self.status = AgentStatus.BUSY
            logging.info(f"Processing command: {command_data} - agent_core.py:30")
        def on_command_complete(result_data):
            self.status = AgentStatus.READY
            logging.info(f"Command completed: {result_data} - agent_core.py:33")
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
            
            logging.info("Default tasks scheduled successfully - agent_core.py:175")
            
        except Exception as e:
            logging.error(f"Error setting up default tasks: {e} - agent_core.py:178")

    def list_tools(self):
        """Return a list of all available tool schemas."""
        return [tool.__class__.schema() for tool in self.tools]

    def handle_text(self, text: str, progress_callback=None) -> str:
        """For GUI: handle user text input and return agent response. Supports progress callback."""
        if not text or not text.strip():
            return "Please provide a valid command."
            
        logging.info(f"Processing user input: {text[:100]}... - agent_core.py:189")
        
        def progress(percent, status, error=False):
            msg = f"[Ultron] {status} ({percent}%)"
            if error:
                msg = f"[Ultron][ERROR] {status} ({percent}%)"
                logging.error(msg)
            else:
                logging.info(msg)
            if progress_callback:
                progress_callback(percent, status, error)
                
        try:
            # Tool listing command
            if text.strip().lower() in ["list tools", "show tools", "tools"]:
                tools = self.list_tools()
                result = "Available tools:\n" + "\n".join([
                    f"- {t.get('name', 'Unknown')}: {t.get('description', 'No description')}\n  Parameters: {t.get('parameters', {})}" for t in tools
                ])
            else:
                # Run the async function in a new event loop
                import asyncio
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.brain.plan_and_act(text, progress_callback=progress))
                    loop.close()
                except Exception as e:
                    logging.error(f"Error in brain.plan_and_act: {e} - agent_core.py:217")
                    result = f"Error processing command: {str(e)}"
                    
            logging.info("Command processing completed successfully - agent_core.py:220")
            if progress_callback:
                progress_callback(100, "Done.")
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in handle_text: {str(e)}"
            logging.error(error_msg)
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg
    def __init__(self):
        self.status = AgentStatus.INITIALIZING
        self._initialize_logging()
        
        try:
            # Initialize core systems
            self.config = Config()
            ensure_ollama_running(self.config)
            
            self.event_system = EventSystem()
            self.performance_monitor = PerformanceMonitor()
            self.task_scheduler = TaskScheduler()
            
            # Initialize core components
            self.memory = Memory()
            self.voice = VoiceAssistant(self.config)
            self.vision = Vision()
            
            # Load tools and initialize brain
            self.tools = self.load_tools()
            self._initialize_pochi()
            self.brain = UltronBrain(self.config, self.tools, self.memory)
            
            # Setup handlers and tasks
            self.task_scheduler.register_command_handler(self.handle_command)
            self._setup_event_handlers()
            self._setup_default_tasks()
            
            # Finalize initialization
            self._speak_on_boot()
            self._initialize_gui()
            
            logging.info("Ultron Agent initialized successfully. - agent_core.py:263")
            self.status = AgentStatus.READY

        except Exception as e:
            logging.critical(f"Fatal error during agent initialization: {e} - agent_core.py:267", exc_info=True)
            self.status = AgentStatus.ERROR
            # Optionally, re-raise or handle the exit gracefully
            raise

    def _initialize_logging(self):
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            filename='ultron_agent.log',
            filemode='a',
            force=True # Override any existing handlers
        )
        logging.info("Logging system initialized. - agent_core.py:281")

    def _initialize_pochi(self):
        self.pochi = None
        if self.config.get("use_pochi", False):
            try:
                from tools.pochi_tool import get_pochi_manager, create_pochi_tool
                self.pochi = get_pochi_manager()
                if self.pochi.is_available():
                    pochi_tool = create_pochi_tool(self.pochi)
                    self.tools.append(pochi_tool)
                    logging.info("🤖 POCHI integration and tool added successfully. - agent_core.py:292")
                else:
                    logging.warning("POCHI is enabled but not available/configured. - agent_core.py:294")
            except ImportError:
                logging.error("POCHI tool files are missing. Cannot initialize. - agent_core.py:296")
            except Exception as e:
                logging.error(f"Failed to initialize POCHI: {e} - agent_core.py:298")

    def _speak_on_boot(self):
        if self.config.get("use_voice", False) and self.voice:
            try:
                boot_message = self.config.get("voice_boot_message", "There's No Strings On Me")
                # Running in a separate thread to avoid blocking
                import threading
                threading.Thread(target=lambda: asyncio.run(self.voice.speak(boot_message)), daemon=True).start()
            except Exception as e:
                logging.error(f"Voice boot message failed: {e} - agent_core.py:308")

    def _initialize_gui(self):
        self.gui = None
        if self.config.get("use_gui", True):
            try:
                from queue import Queue
                from gui_ultimate import UltimateAgentGUI as AgentGUI
                import threading
                self.log_queue = Queue()
                
                def run_gui():
                    self.gui = AgentGUI(self, self.log_queue)
                    self.gui.run()
                
                self.gui_thread = threading.Thread(target=run_gui, daemon=True)
                self.gui_thread.start()
                logging.info("GUI initialized and started in a background thread. - agent_core.py:325")
            except Exception as e:
                logging.error(f"Failed to start GUI: {e} - agent_core.py:327")

    def load_tools(self):
        """Dynamically load all Tool subclasses from the tools package."""
        import pkgutil
        import importlib
        import tools
        from tools.base import Tool
        
        tools_list = []
        loaded_tools = set()  # Track loaded tools to avoid duplicates
        
        try:
            for finder, name, ispkg in pkgutil.iter_modules(tools.__path__, prefix="tools."):
                if ispkg:
                    continue
                    
                try:
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
                            and attr.__name__ not in loaded_tools
                        ):
                            try:
                                # Pass agent reference if the tool constructor accepts it
                                import inspect
                                sig = inspect.signature(attr.__init__)
                                if len(sig.parameters) > 1:  # More than just 'self'
                                    tool_instance = attr(self)
                                else:
                                    tool_instance = attr()
                                    
                                tools_list.append(tool_instance)
                                loaded_tools.add(attr.__name__)
                                logging.info(f"Loaded tool: {attr.__name__} - agent_core.py:368")
                                
                            except Exception as e:
                                logging.warning(f"Failed to load tool {attr.__name__}: {e} - agent_core.py:371")
                                continue
                                
                except Exception as e:
                    logging.warning(f"Failed to import module {name}: {e} - agent_core.py:375")
                    continue
                    
        except Exception as e:
            logging.error(f"Error during tool loading: {e} - agent_core.py:379")
            
        logging.info(f"Successfully loaded {len(tools_list)} tools - agent_core.py:381")
        return tools_list

    def plan_and_act(self, user_input: str) -> str:
        """Delegate planning and acting to the modular brain module."""
        # Create event loop to handle async brain.plan_and_act
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.brain.plan_and_act(user_input))
            return result
        finally:
            loop.close()

    def handle_command(self, command: str):
        logging.info(f"Received command: {command} - agent_core.py:396")
        response = self.plan_and_act(command)
        logging.info(f"Agent response: {response} - agent_core.py:398")
        return response

    async def run(self):
        """Start the agent and all its subsystems."""
        logging.info("Starting Ultron Agent with enhanced systems... - agent_core.py:403")
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
                    boot_message = self.config.data.get("voice_boot_message", "Theres No Strings On Me")
                    await self.voice.speak(boot_message)
            except Exception as e:
                logging.error(f"Voice boot message failed: {e}  boot - agent_core.py:420")

            # Start main loop
            while True:
                try:
                    user_input = input("Ultron> ")
                    if not user_input:
                        continue
                    if user_input.lower() in ("exit", "quit"):
                        print("Goodbye. - agent_core.py:429")
                        break
                    result = self.plan_and_act(user_input)
                    print(f"Ultron: {result} - agent_core.py:432")
                except (EOFError, KeyboardInterrupt):
                    print("\nShutting down. - agent_core.py:434")
                    break
                except Exception as e:
                    print(f"Error: {e} - agent_core.py:437")
                    await self.event_system.emit("error", str(e))
        except Exception as e:
            logging.error(f"Fatal error in run(): {e} - agent_core.py:440")
            await self.event_system.emit("error", str(e))
        finally:
            # Cleanup
            logging.info("Ultron Agent closed  shutdown - agent_core.py:444")
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
            logging.error(f"Error stopping agent: {e} - agent_core.py:461")

    async def process_command(self, command: str) -> str:
        """Process a user command with event tracking."""
        try:
            await self.event_system.emit("command_start", command)
            
            # Add command to memory
            self.memory.add_to_short_term({"role": "user", "content": command})
            
            # Get current system metrics
            metrics = self.performance_monitor.get_metrics_summary()
            if metrics.get('cpu_avg', 0) > 90:
                return "System is under heavy load. Please try again later."
            
            # Process command
            result = await self.brain.plan_and_act(command)
            
            # Add response to memory
            self.memory.add_to_short_term({"role": "system", "content": result})
            
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
    if agent.gui:
        try:
            # The GUI is running in a daemon thread. We need to keep the main thread
            # alive. Joining the thread achieves this and allows for graceful shutdown.
            agent.gui_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down GUI...  main - agent_core.py:502")
    else:
        # If GUI is not enabled, start the command-line interface
        agent.start()
