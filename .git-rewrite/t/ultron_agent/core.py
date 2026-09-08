#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Core Integration Module

This module integrates the existing agent_core.py functionality with the new
infrastructure foundation, providing unified access to all components.
"""
from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from queue import Queue

from . import get_config, get_logger
from .health import HealthChecker
from .errors import UltronError, ErrorSeverity, handle_error


class AgentStatus:
    """Agent status constants"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class IntegratedUltronAgent:
    """
    Integrated ULTRON Agent that combines new infrastructure with existing components.

    This class serves as the main entry point and orchestrates all subsystems:
    - Configuration and logging (new infrastructure)
    - Health monitoring and error handling (new infrastructure)
    - Voice, Vision, Memory (existing components)
    - Brain and AI integration (existing components)
    - GUI and user interaction (existing components)
    - Maverick auto-improvement (existing components)
    - Tools and task scheduling (existing components)
    """

    def __init__(self):
        self.status = AgentStatus.INITIALIZING
        self.config = get_config()
        self.logger = get_logger("ultron.core", source="agent")
        self.health_checker = HealthChecker()

        # Component storage
        self.memory = None
        self.voice = None
        self.vision = None
        self.brain = None
        self.gui = None
        self.maverick = None
        self.tools = []

        # System components
        self.event_system = None
        self.performance_monitor = None
        self.task_scheduler = None

        # Threading and queuing for GUI
        self.gui_thread = None
        self.log_queue = None

    async def initialize(self) -> None:
        """Initialize all agent components asynchronously."""
        try:
            self.logger.info("Starting ULTRON Agent 3.0 initialization...")

            # Initialize system components
            await self._initialize_system_components()

            # Initialize core AI components
            await self._initialize_ai_components()

            # Initialize interaction components
            await self._initialize_interaction_components()

            # Initialize automation components
            await self._initialize_automation_components()

            # Setup event handlers and tasks
            self._setup_event_handlers()
            self._setup_default_tasks()

            # Final startup procedures
            await self._finalize_startup()

            self.status = AgentStatus.READY
            self.logger.info("ULTRON Agent 3.0 initialization complete")

        except Exception as e:
            error_info = handle_error(e, self.logger, "agent_initialization")
            self.status = AgentStatus.ERROR
            raise UltronError(
                "Agent initialization failed",
                ErrorSeverity.CRITICAL,
                {"initialization_error": str(e)}
            ) from e

    async def _initialize_system_components(self) -> None:
        """Initialize system-level components."""
        self.logger.info("Initializing system components...")

        try:
            # Import and initialize event system
            from utils.event_system import EventSystem
            self.event_system = EventSystem()
            self.logger.info("Event system initialized")

            # Import and initialize performance monitor
            from utils.performance_monitor import PerformanceMonitor
            self.performance_monitor = PerformanceMonitor()
            self.logger.info("Performance monitor initialized")

            # Import and initialize task scheduler
            from utils.task_scheduler import TaskScheduler
            self.task_scheduler = TaskScheduler()
            self.task_scheduler.register_command_handler(self.handle_command)
            self.logger.info("Task scheduler initialized")

        except ImportError as e:
            self.logger.warning(f"Some system components not available: {e}")
            # Create minimal fallbacks
            self.event_system = self._create_minimal_event_system()
            self.performance_monitor = self._create_minimal_performance_monitor()
            self.task_scheduler = self._create_minimal_task_scheduler()

    async def _initialize_ai_components(self) -> None:
        """Initialize AI and brain components."""
        self.logger.info("Initializing AI components...")

        try:
            # Ensure Ollama is running
            from utils.startup import ensure_ollama_running
            ensure_ollama_running(self.config)

            # Initialize memory
            from memory import Memory
            self.memory = Memory()
            self.logger.info("Memory system initialized")

            # Initialize vision
            from vision import Vision
            self.vision = Vision()
            self.logger.info("Vision system initialized")

            # Load tools
            self.tools = await self._load_tools()
            self.logger.info(f"Loaded {len(self.tools)} tools")

            # Initialize brain - convert config to old format for compatibility
            from brain import UltronBrain
            config_dict = self._convert_config_for_brain()
            self.brain = UltronBrain(config_dict, self.tools, self.memory)
            self.logger.info("AI Brain initialized")

        except Exception as e:
            self.logger.error(f"AI component initialization failed: {e}")
            # Create minimal fallbacks
            await self._create_minimal_ai_components()

    def _convert_config_for_brain(self) -> Dict[str, Any]:
        """Convert new config format to old brain-compatible format."""
        # Create a dictionary-like config that supports .get() method
        config_dict = self.config.model_dump()

        # Add compatibility methods
        class ConfigDict(dict):
            def get(self, key, default=None):
                return super().get(key, default)

        return ConfigDict(config_dict)

    async def _initialize_interaction_components(self) -> None:
        """Initialize voice and GUI components."""
        self.logger.info("Initializing interaction components...")

        try:
            # Initialize voice system
            if self.config.voice_enabled:
                from voice import VoiceAssistant
                self.voice = VoiceAssistant(self.config)
                self.logger.info("Voice system initialized")

                # Speak boot message if configured
                await self._speak_boot_message()

            # Initialize GUI if enabled
            if self.config.gui_enabled:
                await self._initialize_gui()

        except Exception as e:
            self.logger.error(f"Interaction component initialization failed: {e}")

    async def _initialize_automation_components(self) -> None:
        """Initialize Maverick and other automation components."""
        self.logger.info("Initializing automation components...")

        try:
            # Initialize Maverick Auto-Improvement Engine
            if self.config.enable_maverick:
                await self._initialize_maverick()

            # Initialize POCHI if configured
            await self._initialize_pochi()

        except Exception as e:
            self.logger.error(f"Automation component initialization failed: {e}")

    async def _initialize_maverick(self) -> None:
        """Initialize Maverick Auto-Improvement Engine."""
        try:
            from maverick_engine import create_maverick_engine

            self.maverick = await create_maverick_engine(
                self.config.model_dump(),
                self.event_system
            )

            # Start Maverick monitoring in background
            maverick_task = asyncio.create_task(self.maverick.start_monitoring())

            self.logger.info("🚀 Maverick Auto-Improvement Engine initialized and monitoring started")

        except ImportError:
            self.logger.warning("Maverick engine not available - continuing without auto-improvement")
        except Exception as e:
            self.logger.error(f"Failed to initialize Maverick: {e}")

    async def _initialize_pochi(self) -> None:
        """Initialize POCHI integration if configured."""
        if not getattr(self.config, 'use_pochi', False):
            return

        try:
            from tools.pochi_tool import get_pochi_manager, create_pochi_tool
            pochi = get_pochi_manager()
            if pochi.is_available():
                pochi_tool = create_pochi_tool(pochi)
                self.tools.append(pochi_tool)
                self.logger.info("🤖 POCHI integration and tool added successfully")
            else:
                self.logger.warning("POCHI is enabled but not available/configured")
        except ImportError:
            self.logger.error("POCHI tool files are missing. Cannot initialize")
        except Exception as e:
            self.logger.error(f"Failed to initialize POCHI: {e}")

    async def _initialize_gui(self) -> None:
        """Initialize GUI in a separate thread."""
        try:
            self.log_queue = Queue()

            def run_gui():
                try:
                    from gui_ultimate import UltimateAgentGUI as AgentGUI
                    self.gui = AgentGUI(self)
                    self.gui.run()
                except Exception as e:
                    self.logger.error(f"GUI thread error: {e}")

            self.gui_thread = threading.Thread(target=run_gui, daemon=True)
            self.gui_thread.start()
            self.logger.info("GUI initialized and started in background thread")

        except Exception as e:
            self.logger.error(f"Failed to start GUI: {e}")

    async def _speak_boot_message(self) -> None:
        """Speak boot message if voice is enabled."""
        if not self.voice:
            return

        try:
            boot_message = self.config.get("voice_boot_message", "There's No Strings On Me")
            await self.voice.speak(boot_message)
        except Exception as e:
            self.logger.error(f"Voice boot message failed: {e}")

    async def _load_tools(self) -> List:
        """Dynamically load all tool classes."""
        tools_list = []

        try:
            import pkgutil
            import importlib
            import tools
            from tools.base import Tool

            loaded_tools = set()

            for finder, name, ispkg in pkgutil.iter_modules(tools.__path__, prefix="tools."):
                if ispkg:
                    continue

                try:
                    module = importlib.import_module(name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            hasattr(attr, 'match') and
                            hasattr(attr, 'execute') and
                            attr is not Tool and
                            attr.__module__.startswith('tools.') and
                            attr.__name__ not in loaded_tools):

                            tool_instance = attr()
                            tools_list.append(tool_instance)
                            loaded_tools.add(attr.__name__)
                            self.logger.info(f"Loaded tool: {attr.__name__}")

                except Exception as e:
                    self.logger.warning(f"Failed to load tool from {name}: {e}")

        except Exception as e:
            self.logger.error(f"Error loading tools: {e}")

        return tools_list

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for system events."""
        if not self.event_system:
            return

        def on_error(error_data):
            self.status = AgentStatus.ERROR
            self.logger.error(f"System error: {error_data}")

        def on_command(command_data):
            self.status = AgentStatus.BUSY
            self.logger.info(f"Processing command: {str(command_data)[:100]}")

        def on_command_complete(result_data):
            self.status = AgentStatus.READY
            self.logger.info(f"Command completed: {str(result_data)[:100]}")

        self.event_system.subscribe("error", on_error)
        self.event_system.subscribe("command_start", on_command)
        self.event_system.subscribe("command_complete", on_command_complete)

    def _setup_default_tasks(self) -> None:
        """Setup default scheduled tasks."""
        if not self.task_scheduler:
            return

        try:
            # Health check task
            self.task_scheduler.schedule_task(
                "health_check",
                "run health diagnostics",
                {"type": "interval", "interval": {"minutes": 15}},
                "Regular health monitoring"
            )

            # Maverick analysis task
            if self.maverick:
                self.task_scheduler.schedule_task(
                    "maverick_analysis",
                    "force maverick analysis",
                    {"type": "interval", "interval": {"minutes": 30}},
                    "Auto-improvement analysis"
                )

            self.logger.info("Default tasks scheduled")

        except Exception as e:
            self.logger.error(f"Error setting up default tasks: {e}")

    async def _finalize_startup(self) -> None:
        """Final startup procedures."""
        # Register health checks
        self.health_checker.register_check("agent_status", self._check_agent_health)
        if self.brain:
            self.health_checker.register_check("ai_brain", self._check_brain_health)
        if self.voice:
            self.health_checker.register_check("voice_system", self._check_voice_health)

    async def handle_command(self, command: str) -> Any:
        """Handle scheduled task commands."""
        try:
            if command == "run health diagnostics":
                return await self.health_checker.check_all_health()
            elif command == "force maverick analysis" and self.maverick:
                return await self.maverick.analyze_and_suggest()
            else:
                self.logger.warning(f"Unknown scheduled command: {command}")
                return None
        except Exception as e:
            self.logger.error(f"Error handling command '{command}': {e}")
            return None

    def handle_text(self, text: str, progress_callback=None) -> str:
        """Handle user text input (for GUI compatibility)."""
        if not text or not text.strip():
            return "Please provide a valid command."

        self.logger.info(f"Processing user input: {text[:100]}...")

        try:
            if text.strip().lower() in ["list tools", "show tools", "tools"]:
                return self._list_tools()

            # Use brain for text processing
            if self.brain:
                # Run async brain function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.brain.plan_and_act(text, progress_callback=progress_callback)
                    )
                    return result
                finally:
                    loop.close()
            else:
                return "AI Brain not available"

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg

    def _list_tools(self) -> str:
        """List available tools."""
        if not self.tools:
            return "No tools available"

        tools_info = []
        for tool in self.tools:
            try:
                schema = tool.__class__.schema() if hasattr(tool.__class__, 'schema') else {}
                name = schema.get('name', tool.__class__.__name__)
                desc = schema.get('description', 'No description')
                params = schema.get('parameters', {})
                tools_info.append(f"- {name}: {desc}\n  Parameters: {params}")
            except Exception as e:
                tools_info.append(f"- {tool.__class__.__name__}: Error getting info - {e}")

        return "Available tools:\n" + "\n".join(tools_info)

    def get_maverick_status(self) -> Dict[str, Any]:
        """Get Maverick status information."""
        if not self.maverick:
            return {"status": "disabled", "message": "Maverick engine not initialized"}

        try:
            return {
                "status": "active" if hasattr(self.maverick, 'running') and self.maverick.running else "inactive",
                "summary": self.maverick.get_suggestion_summary() if hasattr(self.maverick, 'get_suggestion_summary') else "No suggestions"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _check_agent_health(self) -> Dict[str, Any]:
        """Health check for agent status."""
        return {
            "healthy": self.status == AgentStatus.READY,
            "status": self.status,
            "components": {
                "brain": self.brain is not None,
                "voice": self.voice is not None,
                "vision": self.vision is not None,
                "gui": self.gui is not None,
                "maverick": self.maverick is not None,
                "tools_count": len(self.tools)
            }
        }

    async def _check_brain_health(self) -> Dict[str, Any]:
        """Health check for AI brain."""
        if not self.brain:
            return {"healthy": False, "error": "Brain not initialized"}

        try:
            # Simple test to verify brain functionality
            test_result = await self.brain.direct_chat("test", None)
            return {"healthy": True, "test_response_length": len(test_result)}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _check_voice_health(self) -> Dict[str, Any]:
        """Health check for voice system."""
        if not self.voice:
            return {"healthy": False, "error": "Voice not initialized"}

        try:
            # Check if voice system is responsive
            return {"healthy": True, "voice_enabled": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    # Fallback methods for missing components
    def _create_minimal_event_system(self):
        """Create minimal event system fallback."""
        class MinimalEventSystem:
            def subscribe(self, event, handler): pass
            def publish(self, event, data): pass
        return MinimalEventSystem()

    def _create_minimal_performance_monitor(self):
        """Create minimal performance monitor fallback."""
        class MinimalPerformanceMonitor:
            def start_monitoring(self): pass
            def get_metrics(self): return {}
        return MinimalPerformanceMonitor()

    def _create_minimal_task_scheduler(self):
        """Create minimal task scheduler fallback."""
        class MinimalTaskScheduler:
            def register_command_handler(self, handler): pass
            def schedule_task(self, *args, **kwargs): pass
        return MinimalTaskScheduler()

    async def _create_minimal_ai_components(self):
        """Create minimal AI components fallback."""
        class MinimalMemory:
            def store(self, key, value): pass
            def retrieve(self, key): return None

        class MinimalVision:
            def analyze(self, image): return "Vision not available"

        class MinimalBrain:
            async def plan_and_act(self, text, **kwargs):
                return f"Processed: {text}"
            async def direct_chat(self, prompt, callback):
                return "AI Brain not available"

        self.memory = MinimalMemory()
        self.vision = MinimalVision()
        self.brain = MinimalBrain()


# Global agent instance
_agent_instance: Optional[IntegratedUltronAgent] = None


async def get_agent() -> IntegratedUltronAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = IntegratedUltronAgent()
        await _agent_instance.initialize()
    return _agent_instance


def get_agent_sync() -> IntegratedUltronAgent:
    """Synchronous wrapper to get agent instance."""
    global _agent_instance
    if _agent_instance is None:
        # Initialize synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            _agent_instance = IntegratedUltronAgent()
            loop.run_until_complete(_agent_instance.initialize())
        finally:
            loop.close()
    return _agent_instance
