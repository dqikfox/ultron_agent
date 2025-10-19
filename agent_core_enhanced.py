"""
ULTRON Agent 3.0 - Enhanced Core System
Main agent with centralized logging, model awareness, and security enhancements
"""

import asyncio
import os
import sys
import json
# Removed unused imports
from pathlib import Path
import importlib
import inspect
from datetime import datetime
from enum import Enum

# Enhanced imports
from utils.ultron_logger import (
    log_info, log_error, log_ai_decision, get_logger
)

try:
    from config import Config
except ImportError:
    class Config:
        def __init__(self, config_path="ultron_config.json"):
            self.data = self._load_config(config_path)

        def _load_config(self, config_path):
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        return json.load(f)
            except Exception as e:
                log_error("config", f"Failed to load config: {e}")

            return {
                "use_voice": True,
                "use_gui": True,
                "use_vision": True,
                "llm_model": "llama3.2:latest",
                "log_level": "INFO",
                "security_mode": True,
                "bind_localhost_only": True
            }

        def get(self, key, default=None):
            return self.data.get(key, default)


class AgentStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class UltronAgentEnhanced:
    """Enhanced ULTRON Agent with centralized logging and model awareness"""

    def __init__(self, config_path: str = "ultron_config.json"):
        """Initialize Enhanced ULTRON Agent"""
        from config import Config as ConfigClass
        self.config = ConfigClass(config_path)
        self.logger = get_logger("agent_core")

        # Core components
        self.tools = {}
        self.is_running = False
        self.current_task = None
        self.status = AgentStatus.INITIALIZING

        # Enhanced components
        self.brain = None
        self.voice = None
        self.memory = None
        self.vision = None
        self.event_system = None
        self.performance_monitor = None
        self.task_scheduler = None

        # Security and monitoring
        self.security_mode = self.config.get("security_mode", True)
        self.startup_time = datetime.now()

        log_info("agent_core", "Enhanced ULTRON Agent initialized",
                 security_mode=self.security_mode)

    async def initialize(self):
        """Initialize all components with enhanced error handling"""
        try:
            log_info("agent_core",
                     "Starting enhanced initialization sequence...")

            # Initialize core systems
            await self._initialize_security()
            await self._initialize_memory()
            await self._initialize_voice()
            await self._initialize_vision()
            await self._initialize_brain()
            await self._load_tools_enhanced()
            await self._initialize_monitoring()

            # Update status
            self.status = AgentStatus.RUNNING
            self.is_running = True

            log_info("agent_core",
                     "Enhanced ULTRON Agent fully initialized and ready",
                     tools_loaded=len(self.tools),
                     security_mode=self.security_mode)

            # Start voice listening if configured
            if self.config.get("use_voice", False):
                log_info("agent_core", "Starting voice system...")
                asyncio.create_task(self.start_voice_listening())

        except Exception as e:
            self.status = AgentStatus.ERROR
            log_error("agent_core", f"Enhanced initialization failed: {e}")
            raise

    async def _initialize_security(self):
        """Initialize security systems"""
        log_info("agent_core", "Initializing security systems...")

        if self.security_mode:
            # Set secure defaults
            os.environ['ULTRON_SECURE_MODE'] = '1'
            log_info("agent_core", "Security mode enabled")
        else:
            log_info("agent_core",
                     "Security mode disabled - development only")

    async def _initialize_memory(self):
        """Initialize enhanced memory system"""
        log_info("agent_core", "Initializing enhanced memory system...")
        try:
            # Try to import enhanced memory
            from memory import UltronMemory
            self.memory = UltronMemory(self.config)
            log_info("agent_core", "Enhanced memory system initialized")
        except ImportError:
            log_info("agent_core",
                     "Enhanced memory not available, using basic memory")
            self.memory = None

    async def _initialize_voice(self):
        """Initialize voice system with enhanced fallback"""
        log_info("agent_core", "Initializing enhanced voice system...")

        try:
            from voice import VoiceAssistant
            self.voice = VoiceAssistant(self.config)
            log_info("agent_core", "Full voice system initialized")
        except ImportError as e:
            log_error("agent_core", f"Full voice system not available: {e}")
            try:
                from voice_manager import UltronVoiceManager
                self.voice = UltronVoiceManager(self.config)
                log_info("agent_core", "Fallback voice system initialized")
            except ImportError as e2:
                log_error("agent_core", f"No voice system available: {e2}")
                self.voice = None

    async def _initialize_vision(self):
        """Initialize vision system"""
        log_info("agent_core", "Initializing vision system...")
        try:
            from vision import Vision as VisionSystem
            self.vision = VisionSystem(self.config)
            log_info("agent_core", "Vision system initialized")
        except ImportError:
            log_info("agent_core", "Vision system not available")
            self.vision = None

    async def _initialize_brain(self):
        """Initialize enhanced brain system"""
        log_info("agent_core", "Initializing enhanced brain system...")
        try:
            from brain import UltronBrain
            self.brain = UltronBrain(self.config, self.tools, self.memory)
            log_info("agent_core", "Enhanced brain system initialized")
        except ImportError as e:
            log_error("agent_core",
                      f"Brain system initialization failed: {e}")
            self.brain = None

    async def _load_tools_enhanced(self):
        """Enhanced tool loading with better error handling and logging"""
        tools_dir = Path(__file__).parent / "tools"
        if not tools_dir.exists():
            log_error("agent_core", "Tools directory not found")
            return

        log_info("agent_core", "Loading tools with enhanced discovery...")

        # Add tools directory to path
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))

        tools_loaded = 0
        tools_failed = 0

        # Scan for tool files
        skip_files = {"__init__", "base", "__pycache__"}
        for tool_file in tools_dir.glob("*.py"):
            if tool_file.stem in skip_files:
                continue

            try:
                # Try multiple loading methods
                module = await self._load_tool_module(tool_file)
                if module:
                    loaded_count = await self._register_tool_classes(
                        module, tool_file.stem)
                    tools_loaded += loaded_count
                else:
                    tools_failed += 1

            except Exception as e:
                tools_failed += 1
                log_error("agent_core",
                          f"Failed to load tool {tool_file.stem}: {e}")

        log_info("agent_core", "Tool loading complete",
                 tools_loaded=tools_loaded,
                 tools_failed=tools_failed,
                 total_tools=len(self.tools))

    async def _load_tool_module(self, tool_file: Path):
        """Load a tool module with multiple fallback methods"""
        module_name = tool_file.stem

        # Method 1: Package import
        try:
            import importlib
            module = importlib.import_module(f"tools.{module_name}")
            log_info("agent_core",
                     f"Loaded tool module via package import: "
                     f"{module_name}")
            return module
        except Exception as e:
            log_error("agent_core",
                      f"Package import failed for {module_name}: {e}")

        # Method 2: importlib.util
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                module_name, str(tool_file))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                log_info("agent_core",
                         f"Loaded tool module via spec: {module_name}")
                return module
        except Exception as e:
            log_error("agent_core",
                      f"Spec import failed for {module_name}: {e}")

        return None

    async def _register_tool_classes(self, module, module_name: str) -> int:
        """Register tool classes from module"""
        registered = 0

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, 'match') and hasattr(obj, 'execute'):
                self.tools[name] = obj()
                registered += 1
                log_info("agent_core", f"Registered tool: {name}")

        return registered

    async def _initialize_monitoring(self):
        """Initialize monitoring systems"""
        log_info("agent_core", "Initializing monitoring systems...")

    async def start_voice_listening(self):
        """Start voice listening loop"""
        if self.voice:
            log_info("agent_core", "Voice listening started")

    async def process_command(self, command: str) -> str:
        """Process a command with enhanced logging"""
        log_ai_decision("agent_core", f"Processing command: {command}")

        if self.brain:
            return await self.brain.process_command(command)

        return "Agent not fully initialized"