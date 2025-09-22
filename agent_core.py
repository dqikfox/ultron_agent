"""
ULTRON Agent Core System
Main agent initialization and core functionality
Following copilot instructions architecture
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import importlib
import inspect
from datetime import datetime
from enum import Enum

# Import performance profiler
from utils.performance_profiler import get_performance_profiler, start_performance_monitoring

# Import the correct UltronConfig from ultron_agent package
try:
    from ultron_agent.config import UltronConfig, load_config
    ULTRON_CONFIG_AVAILABLE = True
except ImportError:
    ULTRON_CONFIG_AVAILABLE = False
    # Fallback config class
    class UltronConfig:
        def __init__(self):
            self.use_voice = False
            self.use_gui = False
            self.use_vision = False
            self.llm_model = "llama3.2:latest"
            self.log_level = "INFO"
            self.voice_enabled = True
            self.vision_enabled = True
            self.memory_enabled = True
            self.tools_enabled = True

        def get(self, key, default=None):
            return getattr(self, key, default)


class AgentStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    MAINTENANCE = "maintenance"


class UltronAgent:
    """
    Main ULTRON Agent class - Main integration hub per copilot instructions
    Handles command routing, tool loading, and system events
    """

    def __init__(self, config_path: str = "ultron_config.json"):
        """Initialize ULTRON Agent following project architecture"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # Initialize performance profiler
        self.performance_profiler = get_performance_profiler(self.config.__dict__ if hasattr(self.config, '__dict__') else {})

        # Core components per copilot instructions
        self.tools = {}
        self.is_running = False
        self.current_task = None

        # Initialize state
        self.status = AgentStatus.INITIALIZING
        self.brain = None
        self.voice = None
        self.memory = None
        self.vision = None
        self.event_system = None
        self.performance_monitor = None
        self.task_scheduler = None

        self.logger.info("ULTRON Agent core initialized")

    def _load_config(self, config_path: str = "ultron_config.json"):
        """Load configuration following project patterns"""
        try:
            if ULTRON_CONFIG_AVAILABLE:
                # Use the proper UltronConfig from ultron_agent package
                config_file = Path(config_path)
                if config_file.exists():
                    return load_config(config_file)
                else:
                    return load_config()  # Use defaults
            else:
                # Fallback to simple config
                return UltronConfig()
        except Exception as e:
            print(f"Failed to load config: {e}, using defaults")
            return UltronConfig()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging per copilot instructions"""
        # Get log level from config
        log_level_str = getattr(self.config, 'log_level', 'INFO')
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("ultron.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        return logging.getLogger(__name__)

    async def initialize(self):
        """Initialize all components per copilot architecture"""
        try:
            self.logger.info("Initializing ULTRON Agent components...")

            # Start performance monitoring
            start_performance_monitoring(self.config.__dict__ if hasattr(self.config, '__dict__') else {})

            # Initialize core systems per copilot instructions
            await self._initialize_memory()
            await self._initialize_voice()
            await self._initialize_vision()
            await self._initialize_brain()
            await self._initialize_event_system()
            await self._initialize_idle_monitor()
            await self._load_tools()

            # Update status
            self.status = AgentStatus.RUNNING
            self.is_running = True

            self.logger.info("ULTRON Agent fully initialized and ready")

            # Start voice listening if configured
            voice_enabled = (getattr(self.config, 'use_voice', False) or
                             getattr(self.config, 'voice_enabled', True))
            if voice_enabled:
                msg = "Voice system enabled, starting voice listening..."
                self.logger.info(msg)
                # Start voice listening in background task
                import asyncio
                asyncio.create_task(self.start_voice_listening())

        except Exception as e:
            self.logger.error(f"Failed to initialize ULTRON Agent: {e}")
            raise

    def initialize_sync(self):
        """Synchronous initialize method for non-async contexts"""
        try:
            # Run async initialize in event loop
            asyncio.run(self.initialize())
        except Exception as e:
            self.logger.error(f"Sync initialization failed: {e}")
            raise

    async def _initialize_memory(self):
        """Initialize memory system"""
        self.logger.info("Initializing memory system...")
        # Placeholder for memory initialization
        pass

    async def _initialize_voice(self):
        """Initialize voice system with fallback chain per copilot instructions"""
        self.logger.info(
            "Initializing voice system (Enhanced -> pyttsx3 -> OpenAI -> Console)..."
        )

        # Import and initialize the full voice system
        try:
            from voice import VoiceAssistant
            self.voice = VoiceAssistant(self.config)
            self.logger.info("Voice system initialized successfully")
        except ImportError as e:
            self.logger.warning(f"Full voice system not available: {e}")
            # Fallback to simple voice manager
            try:
                from voice_manager import UltronVoiceManager
                self.voice = UltronVoiceManager(self.config)
                self.logger.info("Fallback voice system initialized")
            except ImportError as e2:
                self.logger.error(f"No voice system available: {e2}")
                self.voice = None
        except Exception as e:
            self.logger.error(f"Voice system initialization failed: {e}")
            self.voice = None

    async def _initialize_vision(self):
        """Initialize vision system"""
        self.logger.info("Initializing vision system...")
        # Placeholder for vision initialization
        pass

    async def _initialize_brain(self):
        """Initialize brain system"""
        self.logger.info("Initializing brain system...")
        # Placeholder for brain initialization
        pass

    async def _initialize_event_system(self):
        """Initialize event system for inter-component communication"""
        self.logger.info("Initializing event system...")
        from utils.event_system import EventSystem
        self.event_system = EventSystem()
        self.logger.info("Event system initialized successfully")

    async def _initialize_idle_monitor(self):
        """Initialize idle monitor for auto-analysis triggering"""
        self.logger.info("Initializing idle monitor...")
        if not self.event_system:
            await self._initialize_event_system()

        from utils.idle_monitor import IdleMonitor
        idle_threshold = getattr(self.config, 'idle_threshold_minutes', 5)
        self.idle_monitor = IdleMonitor(self.event_system, idle_threshold)

        # Set callback for idle trigger
        async def on_idle():
            await self._trigger_auto_analysis()

        self.idle_monitor.set_idle_callback(on_idle)
        await self.idle_monitor.start_monitoring()
        self.logger.info("Idle monitor initialized and started")

    async def _trigger_auto_analysis(self):
        """Trigger auto-analysis workflow when idle threshold is exceeded"""
        self.logger.info("Triggering auto-analysis due to idle timeout")

        try:
            # Profile the entire auto-analysis workflow
            with self.performance_profiler.profile_operation("auto_analysis_workflow", {"trigger": "idle_timeout"}):
                # Import required modules
                from nvidia_nim_router import UltronNvidiaRouter
                from utils.auto_patch_manager import AutoPatchManager

                # Profile codebase context gathering
                with self.performance_profiler.profile_operation("gather_codebase_context"):
                    codebase_context = await self._gather_codebase_context()

                # Profile NIM analysis
                with self.performance_profiler.profile_operation("nim_codebase_analysis", {"context_length": len(codebase_context)}):
                    nim_router = UltronNvidiaRouter()
                    analysis_result = nim_router.analyze_codebase_for_improvements(codebase_context)

                # Profile suggestion parsing and validation
                with self.performance_profiler.profile_operation("parse_and_validate_suggestions"):
                    patch_manager = AutoPatchManager(self.config)
                    suggestions, metadata = patch_manager.parse_suggestions(analysis_result)

                if suggestions:
                    # Apply suggestions if auto-apply is enabled
                    if self.config.get('auto_apply_patches', False):
                        with self.performance_profiler.profile_operation("apply_auto_patches", {"suggestion_count": len(suggestions)}):
                            results = patch_manager.apply_suggestions(suggestions, metadata)

                        # Notify user of results
                        await self._notify_auto_patch_results(results, metadata)
                    else:
                        # Just notify about available suggestions
                        await self._notify_available_suggestions(suggestions, metadata)
                else:
                    ultron_logger.log_info("auto_patch_manager", "No valid suggestions generated")

        except Exception as e:
            ultron_logger.log_error("agent_core", f"Auto-analysis failed: {str(e)}")
            await self.speak("Auto-analysis encountered an error. Check logs for details.")

    async def _gather_codebase_context(self) -> str:
        """Gather context about the current codebase state"""
        context_parts = []

        # Get recent file changes
        try:
            from utils.model_awareness import get_recent_changes
            recent_changes = get_recent_changes()
            context_parts.append(f"Recent Changes:\n{recent_changes}")
        except Exception as e:
            context_parts.append(f"Recent Changes: Error gathering - {str(e)}")

        # Get current system status
        context_parts.append(f"Current Status: {self.status.value}")
        context_parts.append(f"Running: {self.is_running}")

        # Get loaded tools
        tools_list = list(self.tools.keys())
        context_parts.append(f"Loaded Tools: {', '.join(tools_list)}")

        return "\n\n".join(context_parts)

    async def _notify_auto_patch_results(self, results: Dict[str, Any], metadata: Dict[str, Any]):
        """Notify user about auto-patch application results"""
        applied = results.get('applied', 0)
        failed = results.get('failed', 0)
        total = results.get('total_suggestions', 0)

        message = f"Auto-analysis complete. Applied {applied} of {total} suggestions."
        if failed > 0:
            message += f" {failed} suggestions failed."

        # Log detailed results
        ultron_logger.log_info("agent_core", f"Auto-patch results: {results}")

        # Speak notification
        await self.speak(message)

        # Emit event for GUI notification
        if self.event_system:
            await self.event_system.emit("auto_patch_complete", {
                "results": results,
                "metadata": metadata,
                "message": message
            })

    async def _notify_available_suggestions(self, suggestions: List[Dict[str, Any]], metadata: Dict[str, Any]):
        """Notify user about available suggestions (when auto-apply is disabled)"""
        count = len(suggestions)
        message = f"Auto-analysis found {count} improvement suggestions. Manual review required."

        await self.speak(message)

        # Emit event for GUI
        if self.event_system:
            await self.event_system.emit("suggestions_available", {
                "suggestions": suggestions,
                "metadata": metadata,
                "count": count
            })

    async def _load_tools(self):
        """Dynamically load tools from tools/ directory with robust fallback"""
        tools_dir = Path(__file__).parent / "tools"
        if not tools_dir.exists():
            self.logger.warning("Tools directory not found")
            return

        self.logger.info("Loading tools...")

        # Add tools directory to path
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))

        # Helper: load a module object from a path using importlib.util if available
        def _load_module_importlib(module_name: str, file_path: Path):
            try:
                util = getattr(importlib, "util", None)
                if util is None:
                    return None
                spec = util.spec_from_file_location(module_name, str(file_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore[attr-defined]
                    return module
                return None
            except Exception as e:
                self.logger.debug(f"importlib load failed for {file_path}: {e}")
                return None

        # Helper: fallback loader using runpy.run_path
        def _load_module_runpy(module_name: str, file_path: Path):
            try:
                import runpy
                ns = runpy.run_path(str(file_path))
                # Create a simple object to attach attributes for inspect to work
                class _Mod:  # minimal container
                    pass
                mod = _Mod()
                for k, v in ns.items():
                    setattr(mod, k, v)
                return mod
            except Exception as e:
                self.logger.debug(f"runpy load failed for {file_path}: {e}")
                return None

        # Scan for tool files
        skip_files = {"__init__", "base"}
        for tool_file in tools_dir.glob("*.py"):
            stem = tool_file.stem
            if stem in skip_files:
                continue

            module = None
            # 1) Try importing as package module (tools.<name>)
            try:
                import importlib as _importlib
                module = _importlib.import_module(f"tools.{stem}")
            except Exception as e:
                self.logger.debug(f"package import failed for tools.{stem}: {e}")

            # 2) Fallback to importlib.util by path
            if module is None:
                module = _load_module_importlib(stem, tool_file)

            # 3) Fallback to runpy execution
            if module is None:
                module = _load_module_runpy(stem, tool_file)

            if module is None:
                self.logger.error(f"Failed to load tool module from {tool_file}")
                continue

            # Find tool classes with match and execute methods
            try:
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name in {"Tool", "BaseTool", "Base"}:
                        continue
                    if hasattr(obj, "match") and hasattr(obj, "execute"):
                        # Try to construct with config; if signature doesn't accept it, try default ctor
                        instance = None
                        try:
                            instance = obj(self.config)
                        except TypeError:
                            try:
                                instance = obj()
                            except Exception as inst_e:
                                self.logger.error(f"Tool class {name} init failed: {inst_e}")
                                continue
                        except Exception as inst_e:
                            self.logger.error(f"Tool class {name} init failed: {inst_e}")
                            continue

                        try:
                            self.tools[name.lower()] = instance
                            self.logger.info(f"Loaded tool: {name}")
                        except Exception as e2:
                            self.logger.error(f"Failed to register tool {name}: {e2}")
            except Exception as e:
                self.logger.error(f"Failed to inspect tool classes in {tool_file}: {e}")

    async def speak(self, text: str, async_mode: bool = True):
        """Speak text using the initialized voice system"""
        if self.voice and hasattr(self.voice, 'speak'):
            try:
                if async_mode:
                    # Run in background thread to not block
                    import threading
                    def speak_in_thread():
                        try:
                            # Create new event loop for the thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            # Get the coroutine and run it
                            speak_coro = self.voice.speak(text)
                            loop.run_until_complete(speak_coro)
                            loop.close()
                        except Exception as e:
                            self.logger.error(f"Voice speaking in thread failed: {e}")
                    threading.Thread(target=speak_in_thread).start()
                else:
                    await self.voice.speak(text)
                return True
            except Exception as e:
                self.logger.error(f"Voice speaking failed: {e}")
                return False
        return False

    async def handle_voice_command(self, command: str):
        """Process a voice command through the agent system"""
        try:
            self.logger.info(f"Processing voice command: {command}")

            # Process through brain for AI response
            if self.brain:
                response = await self.brain.process_command(command)
                if response:
                    # Speak the response
                    await self.speak(response)
                    return response

            # Fallback to tool processing
            for tool in self.tools.values():
                if tool.match(command):
                    result = tool.execute(command)
                    if result:
                        await self.speak(str(result))
                        return result

            # Default response
            default_response = "I heard you, but I'm not sure how to help with that."
            await self.speak(default_response)
            return default_response

        except Exception as e:
            error_msg = f"Sorry, I encountered an error processing your command: {str(e)}"
            self.logger.error(f"Voice command processing error: {e}")
            await self.speak(error_msg)
            return error_msg

    async def start_voice_listening(self):
        """Start continuous voice listening and command processing"""
        if not self.voice:
            self.logger.warning("Voice system not initialized, cannot start listening")
            return False

        try:
            self.logger.info("Starting voice listening...")
            speak_result = await self.speak(
                "Voice system activated. I'm listening for commands."
            )
            if not speak_result:
                self.logger.warning("Failed to announce voice activation")

            # Start listening loop
            while self.is_running:
                try:
                    # Listen for voice input
                    if hasattr(self.voice, 'listen_async'):
                        command = await self.voice.listen_async()
                        if command and command.strip():
                            self.logger.info(f"Heard command: {command}")
                            await self.handle_voice_command(command)
                    elif hasattr(self.voice, 'listen'):
                        # Fallback to sync listen method
                        command = self.voice.listen()
                        if command and command.strip():
                            self.logger.info(f"Heard command: {command}")
                            await self.handle_voice_command(command)
                    else:
                        self.logger.warning(
                            "Voice system doesn't support listening"
                        )
                        break

                    # Small delay to prevent tight loop
                    await asyncio.sleep(0.1)

                except Exception as e:
                    self.logger.error(f"Voice listening error: {e}")
                    await asyncio.sleep(1)  # Wait before retrying

            return True

        except Exception as e:
            self.logger.error(f"Failed to start voice listening: {e}")
            return False

    def list_tools(self) -> List[str]:
        """Return a sorted list of loaded tool names."""
        return sorted(self.tools.keys())

    def get_tool(self, name: str):
        """Get a loaded tool instance by name (case-insensitive)."""
        key = name.lower()
        return self.tools.get(key)

    def register_tool(self, name: str, instance: Any) -> None:
        """Register a tool instance programmatically (external bootstrap)."""
        if not name or instance is None:
            raise ValueError("name and instance are required")
        self.tools[name.lower()] = instance
        self.logger.info(f"Registered tool: {name}")

    async def process_command(
        self, command: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process command through agent system per copilot instructions"""
        if not self.is_running:
            raise RuntimeError(
                "Agent is not running. Call initialize() first."
            )

        context = context or {}
        self.current_task = command

        try:
            self.logger.info(f"Processing command: {command}")

            # Basic response
            response = {
                "command": command,
                "response": f"ULTRON received: {command}",
                "timestamp": str(datetime.now()),
                "success": True,
            }

            # Check for matching tools (support sync or async match)
            matching_tools = []
            for tool_name, tool in self.tools.items():
                try:
                    if hasattr(tool, "match"):
                        match_fn = tool.match
                        # Determine if match expects (command) or
                        # (command, context)
                        try:
                            sig = inspect.signature(match_fn)
                            param_count = len(sig.parameters)
                        except Exception:
                            param_count = 2  # default to (command, context)
                        try:
                            if param_count <= 1:
                                match_result = match_fn(command)
                            else:
                                match_result = match_fn(command, context)
                            if inspect.isawaitable(match_result):
                                match_result = await match_result
                        except TypeError:
                            # Fallback to single-arg call
                            match_result = match_fn(command)
                            if inspect.isawaitable(match_result):
                                match_result = await match_result
                        if match_result:
                            matching_tools.append((tool_name, tool))
                except Exception as e:
                    self.logger.error(f"Tool {tool_name} match failed: {e}")

            # Execute matching tools (support sync or async execute)
            if matching_tools:
                tool_results = []
                for tool_name, tool in matching_tools:
                    try:
                        exec_result = tool.execute(command, context)
                        if inspect.isawaitable(exec_result):
                            exec_result = await exec_result
                        tool_results.append(
                            {
                                "tool": tool_name,
                                "result": exec_result,
                                "success": True
                            }
                        )
                        self.logger.info(
                            f"Tool {tool_name} executed successfully"
                        )

                    except Exception as e:
                        self.logger.error(
                            f"Tool {tool_name} execution failed: {e}"
                        )
                        tool_results.append(
                            {
                                "tool": tool_name,
                                "error": str(e),
                                "success": False
                            }
                        )

                response["tools"] = tool_results
                response["response"] = (
                    f"Executed {len(tool_results)} tools for: {command}"
                )

            return response

        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            return {
                "command": command,
                "error": str(e),
                "success": False,
                "timestamp": str(datetime.now()),
            }
        finally:
            self.current_task = None
