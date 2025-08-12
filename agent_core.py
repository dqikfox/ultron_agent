from logging import getLogger, info, error, warning, critical, basicConfig, INFO
from asyncio import new_event_loop, set_event_loop, run, create_task
from os import getenv
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
            from security_utils import sanitize_log_input
            self.status = AgentStatus.ERROR
            error(f"System error: {sanitize_log_input(str(error_data))}")
        def on_command(command_data):
            from security_utils import sanitize_log_input
            self.status = AgentStatus.BUSY
            info(f"Processing command: {sanitize_log_input(str(command_data)[:100])}")
        def on_command_complete(result_data):
            from security_utils import sanitize_log_input
            self.status = AgentStatus.READY
            info(f"Command completed: {sanitize_log_input(str(result_data)[:100])}")
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

            info("Default tasks scheduled successfully")

        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"Error setting up default tasks: {sanitize_log_input(str(e))}")

    def list_tools(self):
        """Return a list of all available tool schemas."""
        return [tool.__class__.schema() for tool in self.tools]

    def handle_text(self, text: str, progress_callback=None) -> str:
        """For GUI: handle user text input and return agent response. Supports progress callback."""
        if not text or not text.strip():
            return "Please provide a valid command."

        from security_utils import sanitize_log_input
        info(f"Processing user input: {sanitize_log_input(text[:100])}...")

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
                    from security_utils import sanitize_log_input
                    error(f"Error in brain.plan_and_act: {sanitize_log_input(str(e))}")
                    result = f"Error processing command: {str(e)}"

            info("Command processing completed successfully")
            if progress_callback:
                progress_callback(100, "Done.")
            return result

        except Exception as e:
            from security_utils import sanitize_log_input
            error_msg = f"Unexpected error in handle_text: {str(e)}"
            error(sanitize_log_input(error_msg))
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

            # Initialize Maverick Auto-Improvement Engine
            self._initialize_maverick()

            # Setup handlers and tasks
            self.task_scheduler.register_command_handler(self.handle_command)
            self._setup_event_handlers()
            self._setup_default_tasks()

            # Finalize initialization
            self._speak_on_boot()
            self._initialize_gui()

            info("Ultron Agent initialized successfully")
            self.status = AgentStatus.READY

        except Exception as e:
            from security_utils import sanitize_log_input
            critical(f"Fatal error during agent initialization: {sanitize_log_input(str(e))}", exc_info=True)
            self.status = AgentStatus.ERROR
            raise

    def _initialize_logging(self):
        from logging.handlers import RotatingFileHandler
        import logging

        log_level = getenv("LOG_LEVEL", "INFO").upper()

        # Create rotating file handler to prevent large log files
        handler = RotatingFileHandler(
            'ultron_agent.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        ))

        logger = getLogger()
        logger.setLevel(getattr(logging, log_level, INFO))
        logger.addHandler(handler)

        info("Logging system initialized with rotation")

    def _initialize_pochi(self):
        self.pochi = None
        if self.config.get("use_pochi", False):
            try:
                from tools.pochi_tool import get_pochi_manager, create_pochi_tool
                self.pochi = get_pochi_manager()
                if self.pochi.is_available():
                    pochi_tool = create_pochi_tool(self.pochi)
                    self.tools.append(pochi_tool)
                    info("🤖 POCHI integration and tool added successfully")
                else:
                    warning("POCHI is enabled but not available/configured")
            except ImportError:
                error("POCHI tool files are missing. Cannot initialize")
            except Exception as e:
                from security_utils import sanitize_log_input
                error(f"Failed to initialize POCHI: {sanitize_log_input(str(e))}")

    def _initialize_maverick(self):
        """Initialize Maverick Auto-Improvement Engine"""
        self.maverick = None
        try:
            from maverick_engine import create_maverick_engine
            import asyncio

            # Create Maverick engine
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.maverick = loop.run_until_complete(
                create_maverick_engine(self.config.data, self.event_system)
            )
            loop.close()

            # Start Maverick monitoring in background if enabled
            if self.config.get("enable_maverick", True):
                from threading import Thread

                def start_maverick():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self.maverick.start_monitoring())
                    finally:
                        loop.close()

                maverick_thread = Thread(target=start_maverick, daemon=True)
                maverick_thread.start()

                info("🚀 Maverick Auto-Improvement Engine initialized and monitoring started")

                # Add Maverick analysis task to scheduler
                self.task_scheduler.schedule_task(
                    "maverick_analysis",
                    "force maverick analysis",
                    {
                        "type": "interval",
                        "interval": {"minutes": 30}
                    },
                    "Maverick auto-improvement analysis"
                )
            else:
                info("🚀 Maverick Auto-Improvement Engine initialized (monitoring disabled)")

        except ImportError:
            warning("Maverick engine not available - continuing without auto-improvement")
        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"Failed to initialize Maverick: {sanitize_log_input(str(e))}")

    def get_maverick_status(self) -> Dict[str, Any]:
        """Get current Maverick system status and suggestions"""
        if not self.maverick:
            return {"status": "disabled", "message": "Maverick engine not initialized"}

        try:
            return {
                "status": "active" if self.maverick.running else "inactive",
                "summary": self.maverick.get_suggestion_summary()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _speak_on_boot(self):
        if self.config.get("use_voice", False) and self.voice:
            try:
                boot_message = self.config.get("voice_boot_message", "There's No Strings On Me")
                # Use thread-safe async execution
                from threading import Thread

                def voice_task():
                    loop = new_event_loop()
                    try:
                        loop.run_until_complete(self.voice.speak(boot_message))
                    finally:
                        loop.close()

                Thread(target=voice_task, daemon=True).start()
            except Exception as voice_error:
                from security_utils import sanitize_log_input
                error(f"Voice boot message failed: {sanitize_log_input(str(voice_error))}")

    def _initialize_gui(self):
        self.gui = None
        if self.config.get("use_gui", True):
            try:
                from queue import Queue
                from gui_ultimate import UltimateAgentGUI as AgentGUI
                import threading
                self.log_queue = Queue()

                def run_gui():
                    self.gui = AgentGUI(self)  # UltimateAgentGUI only takes agent parameter
                    self.gui.run()

                self.gui_thread = threading.Thread(target=run_gui, daemon=True)
                self.gui_thread.start()
                info("GUI initialized and started in a background thread")
            except Exception as e:
                from security_utils import sanitize_log_input
                error(f"Failed to start GUI: {sanitize_log_input(str(e))}")

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
                                info(f"Loaded tool: {attr.__name__}")

                            except Exception as e:
                                from security_utils import sanitize_log_input
                                warning(f"Failed to load tool {attr.__name__}: {sanitize_log_input(str(e))}")
                                continue

                except Exception as e:
                    from security_utils import sanitize_log_input
                    warning(f"Failed to import module {name}: {sanitize_log_input(str(e))}")
                    continue

        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"Error during tool loading: {sanitize_log_input(str(e))}")

        info(f"Successfully loaded {len(tools_list)} tools")
        return tools_list

    def plan_and_act(self, user_input: str) -> str:
        """Delegate planning and acting to the modular brain module."""
        # Create event loop to handle async brain.plan_and_act with proper resource management
        loop = new_event_loop()
        set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.brain.plan_and_act(user_input))
            return result
        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"Error in plan_and_act: {sanitize_log_input(str(e))}")
            return f"Error processing request: {str(e)}"
        finally:
            try:
                loop.close()
            except Exception:
                pass  # Ignore cleanup errors

    def handle_command(self, command: str):
        from security_utils import sanitize_log_input
        info(f"Received command: {sanitize_log_input(command[:100])}")
        response = self.plan_and_act(command)
        info(f"Agent response: {sanitize_log_input(str(response)[:100])}")
        return response

    async def run(self):
        """Start the agent and all its subsystems."""
        logging.info("Starting Ultron Agent with enhanced systems... - agent_core.py:404")
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
                logging.error(f"Voice boot message failed: {e}  boot - agent_core.py:421")

            # Start main loop
            while True:
                try:
                    user_input = input("Ultron> ")
                    if not user_input:
                        continue
                    if user_input.lower() in ("exit", "quit"):
                        print("Goodbye. - agent_core.py:430")
                        break
                    result = self.plan_and_act(user_input)
                    print(f"Ultron: {result} - agent_core.py:433")
                except (EOFError, KeyboardInterrupt):
                    print("\nShutting down. - agent_core.py:435")
                    break
                except Exception as e:
                    print(f"Error: {e} - agent_core.py:438")
                    await self.event_system.emit("error", str(e))
        except Exception as e:
            logging.error(f"Fatal error in run(): {e} - agent_core.py:441")
            await self.event_system.emit("error", str(e))
        finally:
            # Cleanup
            logging.info("Ultron Agent closed  shutdown - agent_core.py:445")
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
            logging.error(f"Error stopping agent: {e} - agent_core.py:462")

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
            print("\nShutting down GUI...  main - agent_core.py:503")
    else:
        # If GUI is not enabled, start the command-line interface
        agent.start()
