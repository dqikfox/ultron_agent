def tool_self_test(self) -> dict:
    """
    Run self-test on all loaded tools that implement self_test().
    Returns a dict with results for each tool.
    """
    results = {}
    if not hasattr(self, "tools") or not self.tools:
        return {"success": False, "error": "No tools loaded"}
    for name, tool in self.tools.items():
        if hasattr(tool, "self_test"):
            try:
                results[name] = tool.self_test()
            except Exception as e:
                results[name] = {"status": "fail", "error": str(e)}
        else:
            results[name] = {"status": "skipped", "error": "No self_test() method"}
    return {"success": True, "tool_diagnostics": results}
"""
ULTRON Agent Core System
Main agent initialization and core functionality
Following copilot instructions architecture
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import importlib
import inspect
from datetime import datetime
from enum import Enum
from diagnostics import diagnostic_wrapper, track_metric, get_diagnostics
from utils.error_handlers import (
    ConfigError, ToolError, AsyncError, ResourceError, ValidationError,
    TimeoutError as UltronTimeoutError, NetworkError, ErrorContext, with_retry
)
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.error_recovery import retry_on_failure
from utils.command_history import CommandHistory
from utils.performance_tracker import PerformanceMonitor, track_performance
from utils.performance_tracker import track_performance

# Import consciousness system for NPC-like behavior
try:
    from cognition.ollama_conscious_agent import OllamaConsciousAgent
    CONSCIOUSNESS_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_AVAILABLE = False
    OllamaConsciousAgent = None

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# Import performance profiler and analytics
from utils.performance_profiler import (
    get_performance_profiler, start_performance_monitoring
)
try:
    from utils.performance_analytics import get_performance_analytics
    PERFORMANCE_ANALYTICS_AVAILABLE = True
except ImportError:
    PERFORMANCE_ANALYTICS_AVAILABLE = False
    def get_performance_analytics():
        return None

try:
    from ultron.supabase_client import create_client_from_config
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client_from_config = None

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
    ERROR = "error"


class UltronAgent:
    async def periodic_self_check_loop(self, interval_seconds: int = 60):
        """Background loop: periodically run self-tests and auto-repair if needed."""
        self.logger.info("Starting periodic self-diagnosis and auto-repair loop...")
        while True:
            try:
                # Run self-tests
                results = {
                    "memory": self.memory_self_test() if hasattr(self, "memory_self_test") else {"success": False},
                    "brain": self.brain_self_test() if hasattr(self, "brain_self_test") else {"success": False},
                    "tools": self.tool_self_test() if hasattr(self, "tool_self_test") else {"success": False},
                }
                # Voice and event system diagnostics (if available)
                if self.voice and hasattr(self.voice, "self_test"):
                    try:
                        results["voice"] = self.voice.self_test()
                    except Exception as e:
                        results["voice"] = {"success": False, "error": str(e)}
                if self.event_system and hasattr(self.event_system, "self_test"):
                    try:
                        results["event_system"] = self.event_system.self_test()
                    except Exception as e:
                        results["event_system"] = {"success": False, "error": str(e)}

                # Log results
                self.logger.info(f"Self-diagnosis results: {results}")

                # Auto-repair for failed components
                for comp, res in results.items():
                    if not res.get("success", False):
                        self.logger.warning(f"Component '{comp}' failed self-test. Attempting auto-repair...")
                        await self._auto_repair_component(comp)

            except Exception as e:
                self.logger.error(f"Periodic self-check loop error: {e}")
            await asyncio.sleep(interval_seconds)

    async def _auto_repair_component(self, component: str):
        """Attempt to auto-repair a failed component by reinitializing it."""
        try:
            if component == "memory":
                if hasattr(self, "_initialize_memory"):
                    await self._initialize_memory()
                    self.logger.info("Memory system reinitialized.")
            elif component == "brain":
                if hasattr(self, "_initialize_brain"):
                    await self._initialize_brain()
                    self.logger.info("Brain system reinitialized.")
            elif component == "tools":
                if hasattr(self, "_load_tools"):
                    await self._load_tools()
                    self.logger.info("Tools reloaded.")
            elif component == "voice":
                if hasattr(self, "_initialize_voice"):
                    await self._initialize_voice()
                    self.logger.info("Voice system reinitialized.")
            elif component == "event_system":
                if hasattr(self, "_initialize_event_system"):
                    await self._initialize_event_system()
                    self.logger.info("Event system reinitialized.")
            else:
                self.logger.warning(f"No auto-repair routine for component: {component}")
        except Exception as e:
            self.logger.error(f"Auto-repair failed for {component}: {e}")

    def memory_self_test(self) -> dict:
        """Run self-test on memory system if available."""
        if self.memory and hasattr(self.memory, "self_test"):
            return self.memory.self_test()
        return {"success": False, "error": "No memory or self_test method"}

    def brain_self_test(self) -> dict:
        """Run self-test on brain system if available."""
        if self.brain and hasattr(self.brain, "self_test"):
            return self.brain.self_test()
        return {"success": False, "error": "No brain or self_test method"}

    def is_healthy(self) -> bool:
        """Return True if all core systems are present and agent is running."""
        return (
            self.status == AgentStatus.RUNNING
            and self.memory is not None
            and self.brain is not None
            and self.voice is not None
            and self.event_system is not None
            and len(self.tools) > 0
        )

    """
    Main ULTRON Agent class - Main integration hub per copilot instructions
    Handles command routing, tool loading, and system events
    """

    def __init__(self, config_path: str = "ultron_config.json"):
        """Initialize ULTRON Agent following project architecture"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # Initialize performance profiler
        config_dict = (self.config.__dict__ if hasattr(self.config, '__dict__')
                       else {})
        self.performance_profiler = get_performance_profiler(config_dict)

        # Initialize performance analytics
        self.performance_analytics = None
        if PERFORMANCE_ANALYTICS_AVAILABLE:
            self.performance_analytics = get_performance_analytics()
            self.logger.info("Performance analytics initialized")

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
        self.supabase = None  # SupabaseClient — wired in initialize()
        self.llamaindex_bridge = None  # LlamaIndexBridge — wired in initialize()

        self.logger.info("ULTRON Agent core initialized")

    def _load_config(self, config_path: str = "ultron_config.json"):
        """Load configuration following project patterns"""
        try:
            if ULTRON_CONFIG_AVAILABLE:
                return load_config(config_path)
            else:
                # Fallback config
                return UltronConfig()
        except Exception as e:
            log_error("agent_core", f"Config loading failed: {e}")
            return UltronConfig()

            # Initialize consciousness system for personality & self-awareness
            self.conscious_mode: bool = False
            self.consciousness: Optional[OllamaConsciousAgent] = None
            if CONSCIOUSNESS_AVAILABLE:
                try:
                    self.consciousness = OllamaConsciousAgent(
                        name="ULTRON",
                        role="AI Assistant",
                        personality_type="balanced",
                        model=getattr(self.config, 'llm_model', 'llava:7b')
                    )
                    log_info("agent_core", "Consciousness system initialized (personality-driven mode)")
                except Exception as conscious_err:
                    log_error("agent_core", f"Consciousness init failed: {conscious_err}")
                    self.consciousness = None

            log_info("agent_core", "ULTRON Agent core initialized successfully",
                    extra={"config_path": config_path, "components_initialized": 10,
                           "consciousness_enabled": self.consciousness is not None})

        except ConfigError as cfg_err:
            log_error("agent_core", f"Configuration error during init: {cfg_err.message}",
                     extra=cfg_err.to_dict())
            raise
        except ValidationError as val_err:
            log_error("agent_core", f"Validation error during init: {val_err.message}",
                     extra=val_err.to_dict())
            raise
        except Exception as init_err:
            error_msg = f"Unexpected error during agent initialization: {str(init_err)}"
            log_error("agent_core", error_msg, exception=init_err)
            raise ResourceError(error_msg, {"error_type": type(init_err).__name__,
                                           "config_path": config_path}) from init_err

    def _load_config(self, config_path: str = "ultron_config.json") -> Any:
        """Load configuration following project patterns

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration object

        Raises:
            ConfigError: If configuration cannot be loaded or validated
            ValidationError: If configuration values are invalid
        """
        try:
            with ErrorContext("config_load_config"):
                # Validate config path
                if not config_path or not isinstance(config_path, str):
                    raise ValidationError("Invalid config path", {"config_path": config_path})

                log_info("agent_core", f"Loading configuration from {config_path}")

                try:
                    if ULTRON_CONFIG_AVAILABLE:
                        # Use the proper UltronConfig from ultron_agent package
                        config_file = Path(config_path)
                        if config_file.exists():
                            config_obj = load_config(config_file)
                        else:
                            log_error("agent_core", f"Config file not found at {config_path}, using defaults")
                            config_obj = load_config()  # Use defaults
                    else:
                        # Fallback to simple config
                        log_error("agent_core", "ULTRON_CONFIG not available, using UltronConfig fallback")
                        config_obj = UltronConfig()

                    if not config_obj:
                        raise ConfigError("Configuration object is None", {"config_path": config_path})

                    log_info("agent_core", "Configuration loaded successfully",
                            extra={"config_path": config_path})
                    return config_obj

                except ConfigError:
                    raise  # Re-raise ConfigError
                except ValidationError:
                    raise  # Re-raise ValidationError
                except FileNotFoundError as file_err:
                    raise ConfigError(f"Configuration file not found: {config_path}",
                                    {"config_path": config_path, "error": str(file_err)}) from file_err
                except Exception as load_err:
                    raise ConfigError(f"Failed to load configuration: {str(load_err)}",
                                    {"config_path": config_path, "error": str(load_err)}) from load_err

        except ConfigError as cfg_err:
            log_error("agent_core", f"Configuration error: {cfg_err.message}",
                     extra=cfg_err.to_dict())
            raise
        except ValidationError as val_err:
            log_error("agent_core", f"Configuration validation error: {val_err.message}",
                     extra=val_err.to_dict())
            raise
        except Exception as unexpected_err:
            error_msg = f"Unexpected error loading configuration: {str(unexpected_err)}"
            log_error("agent_core", error_msg, exception=unexpected_err)
            # Attempt to use default config as last resort
            try:
                return UltronConfig()
            except Exception as default_err:
                raise ConfigError(error_msg, {"error_type": type(unexpected_err).__name__,
                                             "default_error": str(default_err)}) from unexpected_err

    def _setup_logging(self) -> logging.Logger:
        """Setup logging per copilot instructions

        Returns:
            Configured logger instance

        Raises:
            ValidationError: If logging configuration is invalid
        """
        try:
            with ErrorContext("logging_setup"):
                # Get log level from config with safe access
                log_level_str: str = getattr(self.config, 'log_level', 'INFO')
                if not isinstance(log_level_str, str):
                    log_level_str = 'INFO'

                # Validate log level
                log_level: int = getattr(logging, log_level_str.upper(), logging.INFO)
                if not isinstance(log_level, int):
                    log_level = logging.INFO

                # Configure logging with error handling for handlers
                try:
                    handlers: List[logging.Handler] = []

                    # File handler with safe path
                    try:
                        file_handler = logging.FileHandler("ultron.log")
                        handlers.append(file_handler)
                    except Exception as file_err:
                        print(f"Warning: Could not create file handler: {file_err}")

                    # Console handler (always available)
                    try:
                        console_handler = logging.StreamHandler(sys.stdout)
                        handlers.append(console_handler)
                    except Exception as console_err:
                        print(f"Warning: Could not create console handler: {console_err}")

                    if not handlers:
                        raise ValidationError("No logging handlers could be created",
                                            {"log_level": log_level_str})

                    logging.basicConfig(
                        level=log_level,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        handlers=handlers,
                    )

                    logger = logging.getLogger(__name__)
                    log_info("agent_core", "Logging system initialized",
                            extra={"log_level": log_level_str, "handlers": len(handlers)})
                    return logger

                except ValidationError:
                    raise
                except Exception as config_err:
                    raise ValidationError(f"Logging configuration failed: {str(config_err)}",
                                        {"log_level": log_level_str, "error": str(config_err)}) from config_err

        except ValidationError as val_err:
            print(f"Logging validation error: {val_err.message}")
            raise
        except Exception as unexpected_err:
            print(f"Unexpected logging setup error: {str(unexpected_err)}")
            # Fallback logger with minimal config
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger(__name__)

    async def initialize(self) -> None:
        """Initialize all components per copilot architecture

        Performs comprehensive initialization of agent subsystems with cascading
        error recovery and progress tracking.

        Raises:
            AsyncError: If critical initialization operations fail
            ResourceError: If system resources cannot be initialized
            ConfigError: If component configuration is invalid
        """
        init_start_time: float = datetime.now().timestamp()
        initialized_components: List[str] = []

        try:
            with ErrorContext("agent_initialization"):
                log_info("agent_core", "Starting ULTRON Agent component initialization...")
                self.status = AgentStatus.INITIALIZING

                # Start periodic self-diagnosis loop in background
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.periodic_self_check_loop())
                    self.logger.info("Periodic self-diagnosis loop started.")
                except Exception as e:
                    self.logger.error(f"Failed to start periodic self-diagnosis loop: {e}")

                # Start performance monitoring with error isolation
                try:
                    config_dict: Dict[str, Any] = (self.config.__dict__ if hasattr(self.config, '__dict__')
                                                   else {})
                    start_performance_monitoring(config_dict)
                    initialized_components.append("performance_monitoring")
                except Exception as perf_err:
                    log_error("agent_core", f"Performance monitoring setup failed: {perf_err}")
                    # Continue - this is non-critical

                # Initialize core systems with cascading error recovery
                # Use function references instead of immediate coroutine creation
                init_sequence: List[Tuple[str, Any]] = [
                    ("memory", self._initialize_memory),
                    ("supabase", self._initialize_supabase),
                    ("voice", self._initialize_voice),
                    ("vision", self._initialize_vision),
                    ("brain", self._initialize_brain),
                    ("computer_use", self._initialize_computer_use),
                    ("event_system", self._initialize_event_system),
                    ("platform_manager", self._initialize_platform_manager),
                    ("idle_monitor", self._initialize_idle_monitor),
                    ("keyboard_listener", self._initialize_keyboard_listener),
                    ("tools", self._load_tools),
                ]

                # Execute initialization tasks sequentially with individual error handling
                for task_name, task_func in init_sequence:
                    try:
                        # Create and await coroutine when we're ready
                        await task_func()
                        initialized_components.append(task_name)
                        log_info("agent_core", f"Initialized {task_name} successfully",
                                extra={"component": task_name})
                    except AsyncError as async_err:
                        log_error("agent_core", f"Async error initializing {task_name}: {async_err.message}",
                                 extra=async_err.to_dict())
                        # Continue with next component
                    except Exception as comp_err:
                        error_msg = f"Failed to initialize {task_name}: {str(comp_err)}"
                        log_error("agent_core", error_msg, exception=comp_err)
                        # Continue with next component for resilience

                # Start web interface after tools loaded with error isolation
                try:
                    await self._start_web_interface()
                    initialized_components.append("web_interface")
                except Exception as web_err:
                    log_error("agent_core", f"Web interface startup failed: {web_err}")
                    # Continue - web interface is non-critical

                # Update brain with loaded tools
                try:
                    if self.brain:
                        self.update_brain_context()
                        log_info("agent_core", "Brain updated with loaded tools")
                except Exception as brain_update_err:
                    log_error("agent_core", f"Brain update failed: {brain_update_err}")
                    # Continue - non-critical

                # Sync memory with Supabase (load remote, merge local)
                if self.supabase and self.memory:
                    try:
                        await self.memory.load_from_supabase(self.supabase)
                        log_info("agent_core", "Long-term memory loaded from Supabase")
                    except Exception as mem_sync_err:
                        log_error("agent_core", f"Memory Supabase sync failed: {mem_sync_err}")

                # Initialise LlamaIndex bridge (non-critical)
                try:
                    cfg_dict = (
                        self.config.__dict__
                        if hasattr(self.config, "__dict__")
                        else dict(self.config)
                    )
                    from ultron.llamaindex_integration import init_bridge
                    bridge = await asyncio.get_event_loop().run_in_executor(
                        None, init_bridge, cfg_dict
                    )
                    self.llamaindex_bridge = bridge
                    if bridge.ready:
                        from tools.llamaindex_tool import LlamaIndexTool
                        LlamaIndexTool.set_bridge(bridge)
                        initialized_components.append("llamaindex")
                        log_info("agent_core", "LlamaIndex bridge initialised and shared with tools")
                    else:
                        log_info("agent_core", "LlamaIndex bridge init returned not-ready (check logs)")
                except Exception as llama_err:
                    log_error("agent_core", f"LlamaIndex bridge init failed (non-critical): {llama_err}")

                # Update status and markers
                self.status = AgentStatus.RUNNING
                self.is_running = True

                init_duration: float = datetime.now().timestamp() - init_start_time
                log_ai_decision("agent_core", "Agent initialization completed",
                               ai_model="agent_core",
                               confidence_score=0.95,  # Fixed: removed reference to undefined init_tasks
                               reasoning=f"Initialized {len(initialized_components)} components in {init_duration:.2f}s")

                # Perform initial identity maintenance with error isolation
                try:
                    await self.maintain_ultron_identity()
                except Exception as identity_err:
                    log_error("agent_core", f"Identity maintenance failed: {identity_err}")
                    # Continue - this is non-critical

                # Start voice listening if configured with error isolation
                voice_enabled: bool = (self.config.get('use_voice', False) or
                                      self.config.get('voice_enabled', False))
                if voice_enabled:
                    try:
                        msg = "Voice system enabled, starting voice listening..."
                        log_info("agent_core", msg)
                        asyncio.create_task(self.start_voice_listening())
                    except Exception as voice_err:
                        log_error("agent_core", f"Voice listening startup failed: {voice_err}")
                        # Continue - voice is non-critical

                log_info("agent_core", "ULTRON Agent fully initialized and ready",
                        extra={"initialized_components": len(initialized_components),
                               "duration_seconds": f"{init_duration:.2f}",
                               "components": initialized_components})

                # Register OS signal handlers for graceful shutdown
                try:
                    self.register_shutdown_signals()
                    log_info("agent_core", "Shutdown signal handlers registered (SIGTERM/SIGINT)")
                except Exception as sig_err:
                    log_error("agent_core", f"Signal handler registration failed: {sig_err}")

        except AsyncError as async_err:
            self.status = AgentStatus.ERROR
            error_msg = f"Async error during initialization: {async_err.message}"
            log_error("agent_core", error_msg, extra=async_err.to_dict())
            raise
        except Exception as init_err:
            self.status = AgentStatus.ERROR
            error_msg = f"Unexpected error during agent initialization: {str(init_err)}"
            log_error("agent_core", error_msg, exception=init_err)
            raise ResourceError(error_msg, {"initialized_count": len(initialized_components),
                                           "error_type": type(init_err).__name__}) from init_err

    def initialize_sync(self):
        """Synchronous initialize method for non-async contexts"""
        try:
            # Run async initialize in event loop
            asyncio.run(self.initialize())
        except Exception as e:
            self.logger.error(f"Sync initialization failed: {e}")
            raise

    # ------------------------------------------------------------------
    # Graceful shutdown
    # ------------------------------------------------------------------

    async def shutdown(self) -> None:
        """Persist memory/state and release all resources on exit."""
        self.logger.info("ULTRON Agent shutting down — persisting state…")

        # Flush memory to Supabase
        if self.memory is not None:
            try:
                await self.memory.sync_to_supabase()
                self.logger.info("Memory synced to Supabase on shutdown.")
            except Exception as exc:
                self.logger.warning("Memory sync on shutdown failed: %s", exc)

        # Close Supabase HTTP session
        if self.supabase is not None:
            try:
                await self.supabase.close()
                self.logger.info("Supabase session closed.")
            except Exception as exc:
                self.logger.warning("Supabase close on shutdown failed: %s", exc)

        self.status = AgentStatus.OFFLINE
        self.logger.info("ULTRON Agent shutdown complete.")

    def register_shutdown_signals(self) -> None:
        """Register SIGTERM/SIGINT handlers so shutdown() runs on Ctrl-C or kill."""
        loop = asyncio.get_event_loop()

        def _handle(sig_name: str):
            self.logger.info("Received %s — scheduling graceful shutdown.", sig_name)
            loop.create_task(self.shutdown())

        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(sig, lambda s=sig.name: _handle(s))
            except (NotImplementedError, RuntimeError):
                # Windows doesn't support add_signal_handler
                pass

    async def _initialize_memory(self) -> None:
        """Initialize enhanced ULTRON memory system (REQUIRED for identity)"""
        self.logger.info("Initializing ULTRON memory system...")
        try:
            from memory import UltronMemory
            self.memory = UltronMemory(self.config)
            self.logger.info("✅ ULTRON memory system initialized with identity awareness")

            # Verify system prompt is available
            if hasattr(self.memory, 'get_system_prompt'):
                test_prompt = self.memory.get_system_prompt()
                if "ULTRON" in test_prompt:
                    self.logger.info("✅ ULTRON identity confirmed in system prompt")
                else:
                    self.logger.warning("⚠️ ULTRON identity missing from system prompt")

        except ImportError as e:
            self.logger.error(f"❌ CRITICAL: UltronMemory not available - identity will be compromised: {e}")
            self.logger.error("Attempting fallback to basic Memory (NOT RECOMMENDED)")
            try:
                from memory import Memory
                self.memory = Memory()
                self.logger.warning("⚠️ Basic memory initialized - ULTRON identity features disabled")
            except ImportError as e2:
                self.logger.error(f"❌ No memory system available: {e2}")
                self.memory = None
        except Exception as e:
            self.logger.error(f"❌ Memory initialization failed: {e}")
            self.memory = None

    async def _initialize_supabase(self) -> None:
        """Initialize Supabase client and start a new conversation session."""
        if not SUPABASE_AVAILABLE:
            log_info("agent_core", "Supabase module not available, skipping")
            return
        try:
            client = create_client_from_config()
            if not client:
                log_info("agent_core", "Supabase config missing, skipping persistence")
                return
            connected = await client.connect()
            if not connected:
                log_info("agent_core", "Supabase unreachable, running without persistence")
                return
            self.supabase = client
            model = getattr(self.config, "llm_model", None) or "local"
            await self.supabase.start_conversation(
                title=f"ULTRON Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model_name=str(model),
            )
            log_info("agent_core", "Supabase persistence active",
                     extra={"conversation_id": self.supabase.current_conversation_id})
        except Exception as exc:
            log_error("agent_core", f"Supabase init failed (non-critical): {exc}")
            self.supabase = None

    async def _initialize_voice(self) -> None:
        """Initialize voice system with fallback chain per copilot instructions"""
        self.logger.info(
            "Initializing voice system "
            "(Enhanced -> pyttsx3 -> OpenAI -> Console)..."
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

    async def _initialize_vision(self) -> None:
        """Initialize vision system"""
        self.logger.info("Initializing vision system...")
        try:
            from tools.multimodal_vision_tool import MultimodalVisionTool
            self.vision = MultimodalVisionTool()
            self.logger.info("Vision system initialized successfully")
        except ImportError as e:
            self.logger.error(f"Vision system initialization failed: {e}")
            self.vision = None

    async def _initialize_brain(self) -> None:
        """Initialize brain system with tools and memory"""
        self.logger.info("Initializing brain system...")
        try:
            from brain import UltronBrain
            # Pass empty tools initially - will update after tools are loaded
            self.brain = UltronBrain(self.config, {}, self.memory)
            self.logger.info("Brain system initialized successfully (tools will be updated after loading)")
        except ImportError as e:
            self.logger.error(f"Brain system initialization failed: {e}")
            self.brain = None
        except Exception as e:
            self.logger.error(f"Brain system initialization error: {e}")
            self.brain = None

    def update_brain_context(self):
        """Update brain's context provider with current agent state"""
        if self.brain and hasattr(self.brain, 'update_context_provider'):
            try:
                config_dict = (self.config.__dict__ if hasattr(self.config, '__dict__')
                               else {})
                self.brain.update_context_provider(
                    memory=self.memory,
                    tools=self.tools,
                    config=config_dict
                )
                self.logger.info("Brain context provider updated with current agent state")
            except Exception as e:
                self.logger.error(f"Failed to update brain context: {e}")

    async def _initialize_computer_use(self) -> None:
        """Initialize OpenAI Computer Use integration"""
        self.logger.info("Initializing OpenAI Computer Use...")
        try:
            from openai_computer_use_integration import ultron_computer_use
            self.computer_use = ultron_computer_use
            self.logger.info("OpenAI Computer Use initialized successfully")
        except ImportError as e:
            self.logger.error(f"Computer Use initialization failed: {e}")
            self.computer_use = None

    async def _initialize_event_system(self) -> None:
        """Initialize event system for inter-component communication"""
        self.logger.info("Initializing event system...")
        from utils.event_system import EventSystem
        self.event_system = EventSystem()
        self.logger.info("Event system initialized successfully")

    async def _initialize_platform_manager(self) -> None:
        """Initialize platform manager for cross-platform support"""
        self.logger.info("Initializing platform manager...")
        try:
            from platform_manager import PlatformManager
            self.platform_manager = PlatformManager()
            self.logger.info("Platform manager initialized successfully")
        except ImportError as e:
            self.logger.error(f"Platform manager initialization failed: {e}")
            self.platform_manager = None

    async def _initialize_idle_monitor(self) -> None:
        """Initialize idle monitor for auto-analysis triggering"""
        self.logger.info("Initializing idle monitor...")
        if not self.event_system:
            await self._initialize_event_system()

        from utils.idle_monitor import IdleMonitor
        idle_threshold = getattr(self.config, 'idle_threshold_minutes', 5)
        self.idle_monitor = IdleMonitor(self.event_system, idle_threshold)

        # Set callback for idle trigger
        async def on_idle() -> None:
            await self._trigger_auto_analysis()

        self.idle_monitor.set_idle_callback(on_idle)
        await self.idle_monitor.start_monitoring()
        self.logger.info("Idle monitor initialized and started")

    async def _initialize_keyboard_listener(self) -> None:
        """Initialize Print Screen key listener for automatic screenshot analysis"""
        if not KEYBOARD_AVAILABLE:
            self.logger.warning("Keyboard library not available, Print Screen functionality disabled")
            return

        self.logger.info("Initializing Print Screen key listener...")

        def on_print_screen():
            """Handle Print Screen key press"""
            try:
                self.logger.info("Print Screen detected, triggering vision analysis...")
                # Run vision capture and analysis in background
                asyncio.create_task(self._handle_print_screen_capture())
            except Exception as e:
                self.logger.error(f"Error handling Print Screen: {e}")

        # Register the hotkey
        try:
            keyboard.add_hotkey('print screen', on_print_screen)
            keyboard.add_hotkey('printscreen', on_print_screen)  # Alternative key name
            self.logger.info("Print Screen key listener registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register Print Screen hotkey: {e}")

    async def _handle_print_screen_capture(self):
        """Handle the Print Screen capture and analysis workflow"""
        try:
            # Capture screenshot
            if self.vision:
                capture_result = self.vision.capture_and_ocr()
                if capture_result.get('has_text') or capture_result.get('screenshot_path'):
                    image_path = capture_result.get('screenshot_path')
                    self.logger.info(f"Screenshot captured: {image_path}")

                    # Trigger analysis via multimodal vision tool
                    from tools.multimodal_vision_tool import MultimodalVisionTool
                    vision_tool = MultimodalVisionTool()
                    analysis = vision_tool.analyze_image(image_path)

                    # Emit event for GUI updates
                    if self.event_system:
                        await self.event_system.emit('vision_analysis_complete', {
                            'image_path': image_path,
                            'analysis': analysis,
                            'trigger': 'print_screen'
                        })

                    self.logger.info("Print Screen analysis completed successfully")
                else:
                    self.logger.error("Screenshot capture failed")
            else:
                self.logger.error("Vision system not available for Print Screen capture")
        except Exception as e:
            self.logger.error(f"Print Screen capture failed: {e}")

    async def _start_web_interface(self):
        """Start the web interface after all tools are loaded"""
        self.logger.info("Starting web interface...")
        try:
            # Find the mobile web interface tool and start it
            for tool_name, tool in self.tools.items():
                if tool_name.lower() == 'mobilewebinterfacetool':
                    # Start the interface in a separate thread to avoid blocking
                    import threading
                    def start_interface():
                        try:
                            tool.start_interface()
                        except Exception as e:
                            self.logger.error(f"Failed to start web interface: {e}")

                    interface_thread = threading.Thread(target=start_interface, daemon=True)
                    interface_thread.start()
                    self.logger.info("Web interface started in background thread")
                    break
        except Exception as e:
            self.logger.error(f"Error starting web interface: {e}")

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
                    from utils.ultron_logger import log_info
                    log_info("auto_patch_manager", "No valid suggestions generated")

        except Exception as e:
            from utils.ultron_logger import log_error
            log_error("agent_core", f"Auto-analysis failed: {str(e)}")
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
        from utils.ultron_logger import log_info
        log_info("agent_core", f"Auto-patch results: {results}")

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

    async def _load_tools(self) -> None:
        """Dynamically load tools from tools/ directory with robust fallback

        Implements resilient tool discovery and loading with multiple fallback
        strategies and comprehensive error isolation.

        Raises:
            ToolError: If tool loading fails critically
            ValidationError: If tool validation fails
        """
        tools_loaded: int = 0
        tools_failed: int = 0

        try:
            with ErrorContext("tool_loading"):
                tools_dir: Path = Path(__file__).parent / "tools"
                if not tools_dir.exists():
                    error_msg = f"Tools directory not found at {tools_dir}"
                    log_error("agent_core", error_msg)
                    raise ToolError(error_msg, {"tools_dir": str(tools_dir)})

                log_info("agent_core", f"Loading tools from {tools_dir}...")

                # Add tools directory to path with validation
                if str(tools_dir) not in sys.path:
                    try:
                        sys.path.insert(0, str(tools_dir))
                    except Exception as path_err:
                        log_error("agent_core", f"Failed to add tools directory to path: {path_err}")
                        # Continue anyway

                # Helper: load module using importlib.util
                def _load_module_importlib(module_name: str, file_path: Path) -> Optional[Any]:
                    try:
                        util = getattr(importlib, "util", None)
                        if util is None:
                            return None
                        spec = util.spec_from_file_location(module_name, str(file_path))
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            return module
                        return None
                    except Exception as import_err:
                        log_error("agent_core", f"importlib load failed for {file_path}: {import_err}")
                        return None

                # Helper: fallback loader using runpy
                def _load_module_runpy(module_name: str, file_path: Path) -> Optional[Any]:
                    try:
                        import runpy
                        ns: Dict[str, Any] = runpy.run_path(str(file_path))
                        # Create minimal container for attributes
                        class _Mod:  # type: ignore
                            pass
                        mod = _Mod()
                        for k, v in ns.items():
                            setattr(mod, k, v)
                        return mod
                    except Exception as runpy_err:
                        log_error("agent_core", f"runpy load failed for {file_path}: {runpy_err}")
                        return None

                # Scan for tool files
                skip_files: set = {"__init__", "base", "tool_interface", "tool_loader"}
                for tool_file in tools_dir.glob("*.py"):
                    stem: str = tool_file.stem
                    if stem in skip_files:
                        continue

                    try:
                        with ErrorContext(f"tool_load_{stem}"):
                            module: Optional[Any] = None

                            # 1) Try importing as package module
                            try:
                                module = importlib.import_module(f"tools.{stem}")
                            except ImportError as import_err:
                                log_error("agent_core", f"Package import failed for tools.{stem}: {import_err}")
                                # Continue to fallback methods
                            except Exception as import_err:
                                log_error("agent_core", f"Unexpected error importing tools.{stem}: {import_err}")
                                continue

                            # 2) Fallback to importlib.util by path
                            if module is None:
                                module = _load_module_importlib(stem, tool_file)

                            # 3) Fallback to runpy execution
                            if module is None:
                                module = _load_module_runpy(stem, tool_file)

                            if module is None:
                                log_error("agent_core", f"All loading methods failed for {tool_file}")
                                tools_failed += 1
                                continue

                            # Find and register tool classes
                            try:
                                for name, obj in inspect.getmembers(module, inspect.isclass):
                                    if name in {"Tool", "BaseTool", "Base", "ToolInterface"}:
                                        continue

                                    # Validate tool interface
                                    if not (hasattr(obj, "match") and hasattr(obj, "execute")):
                                        continue

                                    # Try to instantiate with cascading parameter strategies
                                    instance: Optional[Any] = None
                                    init_params: List[str] = []

                                    try:
                                        instance = obj(self.config, self.memory)
                                        init_params = ["config", "memory"]
                                    except TypeError:
                                        try:
                                            instance = obj(self.config)
                                            init_params = ["config"]
                                        except TypeError:
                                            try:
                                                instance = obj()
                                                init_params = []
                                            except Exception as init_err:
                                                log_error("agent_core", f"Tool {name} instantiation failed with all strategies: {init_err}")
                                                tools_failed += 1
                                                continue
                                    except Exception as init_err:
                                        log_error("agent_core", f"Tool {name} initialization failed: {init_err}")
                                        tools_failed += 1
                                        continue

                                    # Validate instance
                                    if instance is None:
                                        log_error("agent_core", f"Tool {name} instantiation returned None")
                                        tools_failed += 1
                                        continue

                                    try:
                                        self.tools[name.lower()] = instance
                                        tools_loaded += 1
                                        log_info("agent_core", f"Loaded tool: {name}",
                                                extra={"tool_name": name, "init_params": init_params})
                                    except Exception as reg_err:
                                        log_error("agent_core", f"Failed to register tool {name}: {reg_err}")
                                        tools_failed += 1

                            except Exception as inspect_err:
                                log_error("agent_core", f"Failed to inspect classes in {tool_file}: {inspect_err}")
                                tools_failed += 1

                    except ErrorContext:
                        raise  # Re-raise context manager errors
                    except Exception as tool_err:
                        log_error("agent_core", f"Unexpected error loading tool {stem}: {tool_err}")
                        tools_failed += 1

                log_ai_decision("agent_core", f"Tool loading completed",
                               ai_model="agent_core",
                               confidence_score=tools_loaded / max(1, tools_loaded + tools_failed),
                               reasoning=f"Loaded {tools_loaded} tools, {tools_failed} failed")

                if tools_loaded == 0:
                    log_error("agent_core", "No tools were successfully loaded")
                    # Don't raise - agent can function without tools

                # Update brain context after all tools are loaded
                if hasattr(self, 'update_brain_context') and callable(self.update_brain_context):
                    try:
                        self.update_brain_context()
                    except Exception as ctx_err:
                        log_error("agent_core", f"Failed to update brain context: {ctx_err}")

                # Share Supabase client with all tool instances
                if self.supabase:
                    try:
                        from tools.tool_interface import ToolInterface as TI
                        TI.shared_supabase = self.supabase
                        log_info("agent_core", "Supabase client shared with all tools")
                        # Also inject into the dedicated Data API tool
                        from tools.supabase_data_api_tool import SupabaseDataAPITool
                        SupabaseDataAPITool.set_client(self.supabase)
                    except Exception as sb_tool_err:
                        log_error("agent_core", f"Failed to share Supabase with tools: {sb_tool_err}")

        except ToolError as tool_err:
            log_error("agent_core", f"Tool loading error: {tool_err.message}",
                     extra=tool_err.to_dict())
            raise
        except Exception as load_err:
            error_msg = f"Unexpected error during tool loading: {str(load_err)}"
            log_error("agent_core", error_msg, exception=load_err)
            # Don't raise - agent can function without tools as fallback

    async def speak(self, text: str, async_mode: bool = True) -> bool:
        """Speak text using the initialized voice system."""
        if not self.voice or not text:
            return False

        try:
            speak_async = getattr(self.voice, "speak_async", None)
            speak_sync = getattr(self.voice, "speak", None)

            if async_mode and callable(speak_async):
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(speak_async(text))
                    return True
                except RuntimeError:
                    import threading

                    def run_in_thread():
                        try:
                            asyncio.run(speak_async(text))
                        except Exception as thread_exc:
                            self.logger.error(
                                f"Voice speak_async thread failed: {thread_exc}"
                            )

                    threading.Thread(target=run_in_thread, daemon=True).start()
                    return True

            if callable(speak_async):
                return await speak_async(text)

            if callable(speak_sync):
                if async_mode:
                    await asyncio.to_thread(speak_sync, text)
                    return True
                return bool(speak_sync(text))

            self.logger.warning(
                "Voice assistant lacks speak interfaces; skipping audio output"
            )
            return False

        except Exception as exc:
            self.logger.error(f"Voice speaking failed: {exc}")
            return False

    @diagnostic_wrapper("agent_core", track_performance=True)
    async def handle_voice_command(self, command: str):
        """Process a voice command through the agent system"""
        try:
            self.logger.info(f"Processing voice command: {command}")
            track_metric("agent_core", "voice_commands", 1, "count")

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
                "Voice recognition active."
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

    @retry_on_failure(max_retries=3)
    @track_performance
    async def process_command(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process command through agent system per copilot instructions

        Implements multi-phase command routing with tool-first strategy,
        brain processing fallback, and comprehensive error isolation.

        Args:
            command: The command string to process
            context: Optional context dictionary

        Returns:
            Response dictionary with command, response, metadata

        Raises:
            AsyncError: If processing fails critically
        """
        if not self.is_running:
            error_msg = "Agent is not running. Call initialize() first."
            log_error("agent_core", error_msg)
            raise AsyncError(error_msg, {"agent_running": False})

        if not command or not isinstance(command, str):
            error_msg = f"Invalid command: {command}"
            log_error("agent_core", error_msg)
            raise ValidationError(error_msg, {"command": str(command)})

        context: Dict[str, Any] = context or {}
        self.current_task = command
        processing_start: float = datetime.now().timestamp()

        try:
            with ErrorContext("command_processing"):
                log_info("agent_core", f"Processing command: {command}",
                        extra={"context_keys": list(context.keys())})

                # PHASE 1A: Brain Tool Routing with error isolation
                if self.brain:
                    try:
                        can_handle: bool
                        tool_name: Optional[str]
                        can_handle, tool_name = (
                            self.brain.can_tool_handle_this(command)
                        )

                        if can_handle and tool_name:
                            try:
                                tool_result: str = self.brain.execute_tool(
                                    tool_name, command
                                )
                                processing_time: float = datetime.now().timestamp() - processing_start
                                log_info("agent_core", f"Tool executed successfully: {tool_name}",
                                        extra={"tool": tool_name, "duration_seconds": f"{processing_time:.3f}"})
                                return {
                                    "command": command,
                                    "response": tool_result,
                                    "tool": tool_name,
                                    "timestamp": str(datetime.now()),
                                    "success": True,
                                    "processing_time_seconds": processing_time,
                                }
                            except Exception as tool_exec_err:
                                log_error("agent_core", f"Brain tool execution failed: {tool_exec_err}",
                                         exception=tool_exec_err)
                                # Fall through to other methods

                    except Exception as brain_err:
                        log_error("agent_core", f"Brain command evaluation failed: {brain_err}",
                                 exception=brain_err)
                        # Fall through to tool matching

                # Initialize base response
                response: Dict[str, Any] = {
                    "command": command,
                    "response": f"ULTRON received: {command}",
                    "timestamp": str(datetime.now()),
                    "success": True,
                    "tool_count": 0,
                }

                # PHASE 1B: Tool Matching with error isolation
                matching_tools: List[Tuple[str, Any]] = []

                try:
                    for tool_name, tool in self.tools.items():
                        try:
                            if hasattr(tool, "match"):
                                match_fn: Any = tool.match

                                # Determine match function signature
                                try:
                                    sig: inspect.Signature = inspect.signature(match_fn)
                                    param_count: int = len(sig.parameters)
                                except Exception:
                                    param_count = 2  # Default to (command, context)

                                # Invoke with appropriate parameters
                                try:
                                    match_result: Any
                                    if param_count <= 1:
                                        match_result = match_fn(command)
                                    else:
                                        match_result = match_fn(command, context)

                                    if inspect.isawaitable(match_result):
                                        match_result = await match_result

                                except TypeError:
                                    # Fallback to single-arg
                                    match_result = match_fn(command)
                                    if inspect.isawaitable(match_result):
                                        match_result = await match_result

                                if match_result:
                                    matching_tools.append((tool_name, tool))
                                    log_info("agent_core", f"Tool matched: {tool_name}")

                        except Exception as match_err:
                            log_error("agent_core", f"Tool {tool_name} match failed: {match_err}")
                            # Continue with next tool

                except Exception as match_phase_err:
                    log_error("agent_core", f"Tool matching phase failed: {match_phase_err}")
                    # Continue with response

                # PHASE 2: Tool Execution with error isolation
                if matching_tools:
                    tool_results: List[Dict[str, Any]] = []

                    for tool_name, tool in matching_tools:
                        try:
                            exec_result: Any = tool.execute(command)
                            if inspect.isawaitable(exec_result):
                                exec_result = await exec_result

                            tool_results.append({
                                "tool": tool_name,
                                "result": exec_result,
                                "success": True
                            })
                            log_info("agent_core", f"Tool {tool_name} executed successfully")

                        except Exception as exec_err:
                            log_error("agent_core", f"Tool {tool_name} execution failed: {exec_err}",
                                     exception=exec_err)
                            tool_results.append({
                                "tool": tool_name,
                                "error": str(exec_err),
                                "success": False
                            })

                    response["tools"] = tool_results
                    response["response"] = (
                        f"Executed {len([t for t in tool_results if t['success']])} of {len(tool_results)} tools"
                    )
                    response["tool_count"] = len(matching_tools)

                # Log performance and complete
                processing_time = datetime.now().timestamp() - processing_start
                log_ai_decision("agent_core", "Command processing completed",
                               ai_model="agent_core",
                               confidence_score=1.0 if response["success"] else 0.5,
                               reasoning=f"Processed with {len(matching_tools)} tools in {processing_time:.3f}s")

                response["processing_time_seconds"] = processing_time

                # Record in command history
                self.command_history.add(command, response, success=response.get("success", True))

                # Persist to Supabase (fire-and-forget, non-blocking)
                if self.supabase:
                    try:
                        proc_ms = int(processing_time * 1000)
                        await self.supabase.persist_message(None, "user", command)
                        await self.supabase.persist_message(
                            None,
                            "assistant",
                            str(response.get("response", "")),
                            processing_time_ms=proc_ms,
                        )
                        # Log any tool executions
                        for tr in response.get("tools", []):
                            await self.supabase.log_tool_execution(
                                tool_name=tr.get("tool", "unknown"),
                                input_text=command,
                                output_text=str(tr.get("result", tr.get("error", ""))),
                                status="success" if tr.get("success") else "failure",
                                duration_ms=proc_ms,
                            )
                    except Exception as sb_err:
                        log_error("agent_core", f"Supabase persist failed: {sb_err}")

                return response

        except AsyncError as async_err:
            error_time = datetime.now().timestamp() - processing_start
            log_error("agent_core", f"Async error during command processing: {async_err.message}",
                     extra=async_err.to_dict())
            return {
                "command": command,
                "error": async_err.message,
                "error_type": "async_error",
                "success": False,
                "timestamp": str(datetime.now()),
                "processing_time_seconds": error_time,
            }
        except ValidationError as val_err:
            error_time = datetime.now().timestamp() - processing_start
            log_error("agent_core", f"Validation error: {val_err.message}",
                     extra=val_err.to_dict())
            return {
                "command": command,
                "error": val_err.message,
                "error_type": "validation_error",
                "success": False,
                "timestamp": str(datetime.now()),
                "processing_time_seconds": error_time,
            }
        except Exception as proc_err:
            error_time = datetime.now().timestamp() - processing_start
            error_msg = f"Unexpected error during command processing: {str(proc_err)}"
            log_error("agent_core", error_msg, exception=proc_err)
            return {
                "command": command,
                "error": error_msg,
                "error_type": type(proc_err).__name__,
                "success": False,
                "timestamp": str(datetime.now()),
                "processing_time_seconds": error_time,
            }

    async def maintain_ultron_identity(self) -> bool:
        """Maintain ULTRON's identity through periodic self-awareness checks"""
        try:
            self.logger.info("Performing ULTRON identity maintenance...")

            # Check if brain is available
            if not self.brain:
                self.logger.warning("Brain not available for identity maintenance")
                return False

            # Perform identity awareness check
            identity_maintained = await self.brain.check_identity_awareness()

            if not identity_maintained:
                self.logger.warning("Identity awareness check failed - reinforcing identity")
                # Reinforce identity if check failed
                reinforcement_result = await self.brain.reinforce_ultron_identity()
                self.logger.info(f"Identity reinforcement completed: {reinforcement_result[:100]}...")

                # Check again after reinforcement
                identity_maintained = await self.brain.check_identity_awareness()

            if identity_maintained:
                self.logger.info("ULTRON identity maintenance successful")
            else:
                self.logger.error("ULTRON identity maintenance failed")

            return identity_maintained

        except Exception as e:
            self.logger.error(f"Identity maintenance failed: {e}")
            return False

    async def get_ultron_status(self) -> Dict[str, Any]:
        """Get comprehensive ULTRON system status including identity awareness"""
        try:
            status = {
                "identity": "ULTRON",
                "version": "3.0",
                "timestamp": str(datetime.now()),
                "systems": {}
            }

            # Check system components
            status["systems"]["memory"] = self.memory is not None
            status["systems"]["brain"] = self.brain is not None
            status["systems"]["tools"] = len(self.tools) > 0
            status["systems"]["voice"] = self.voice is not None
            status["systems"]["config"] = self.config is not None
            status["systems"]["platform_manager"] = self.platform_manager is not None

            # Add platform information
            if self.platform_manager:
                status["platform"] = self.platform_manager.get_platform_info()
                status["platform_features"] = (
                    self.platform_manager.get_platform_specific_features()
                )

            # Check identity awareness
            if self.brain:
                try:
                    identity_aware = await self.brain.check_identity_awareness()
                    status["identity_awareness"] = identity_aware
                except Exception as e:
                    self.logger.error(f"Identity awareness check failed: {e}")
                    status["identity_awareness"] = False
            else:
                status["identity_awareness"] = False

            # Get tool count
            status["tool_count"] = len(self.tools)

            # Get memory stats if available
            if self.memory and hasattr(self.memory, 'get_memory_stats'):
                status["memory_stats"] = self.memory.get_memory_stats()

            return status

        except Exception as e:
            self.logger.error(f"Status retrieval failed: {e}")
            return {
                "error": str(e),
                "timestamp": str(datetime.now())
            }
        finally:
            self.current_task = None
