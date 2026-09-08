"""
ULTRON Agent 3.0 - Enhanced Core System
Main agent with centralized logging, model awareness, and security enhancements
"""

import asyncio
import logging
import os
import sys
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import importlib
import inspect
from datetime import datetime
from enum import Enum

# Enhanced imports
from utils.ultron_logger import log_info, log_error, log_ai_decision, get_logger
from utils.model_awareness import should_modify_file, check_file_context, record_file_modification

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
        self.config = Config(config_path)
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
            log_info("agent_core", "Starting enhanced initialization sequence...")
            
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
            
            log_info("agent_core", "Enhanced ULTRON Agent fully initialized and ready",
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
            log_info("agent_core", "Security mode disabled - development only")
    
    async def _initialize_memory(self):
        """Initialize enhanced memory system"""
        log_info("agent_core", "Initializing enhanced memory system...")
        try:
            # Try to import enhanced memory
            from memory import UltronMemory
            self.memory = UltronMemory(self.config)
            log_info("agent_core", "Enhanced memory system initialized")
        except ImportError:
            log_info("agent_core", "Enhanced memory not available, using basic memory")
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
            from vision import VisionSystem
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
            log_error("agent_core", f"Brain system initialization failed: {e}")
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
                    loaded_count = await self._register_tool_classes(module, tool_file.stem)
                    tools_loaded += loaded_count
                else:
                    tools_failed += 1
                    
            except Exception as e:
                tools_failed += 1
                log_error("agent_core", f"Failed to load tool {tool_file.stem}: {e}")
        
        log_info("agent_core", f"Tool loading complete",
                tools_loaded=tools_loaded,
                tools_failed=tools_failed,
                total_tools=len(self.tools))
    
    async def _load_tool_module(self, tool_file: Path):
        """Load a tool module with multiple fallback methods"""
        module_name = tool_file.stem
        
        # Method 1: Package import
        try:
            module = importlib.import_module(f"tools.{module_name}")
            log_info("agent_core", f"Loaded tool module via package import: {module_name}")
            return module
        except Exception as e:
            log_error("agent_core", f"Package import failed for {module_name}: {e}")
        
        # Method 2: importlib.util
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, str(tool_file))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                log_info("agent_core", f"Loaded tool module via importlib.util: {module_name}")
                return module
        except Exception as e:
            log_error("agent_core", f"importlib.util failed for {module_name}: {e}")
        
        # Method 3: runpy fallback
        try:
            import runpy
            namespace = runpy.run_path(str(tool_file))
            
            # Create module-like object
            class ModuleWrapper:
                pass
            
            module = ModuleWrapper()
            for key, value in namespace.items():
                setattr(module, key, value)
            
            log_info("agent_core", f"Loaded tool module via runpy: {module_name}")
            return module
        except Exception as e:
            log_error("agent_core", f"runpy failed for {module_name}: {e}")
        
        return None
    
    async def _register_tool_classes(self, module, module_name: str) -> int:
        """Register tool classes from a module"""
        registered = 0
        
        try:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name in {"Tool", "BaseTool", "Base"}:
                    continue
                
                if hasattr(obj, "match") and hasattr(obj, "execute"):
                    try:
                        # Try to instantiate with config
                        instance = None
                        try:
                            instance = obj(self.config)
                        except TypeError:
                            try:
                                instance = obj()
                            except Exception as e:
                                log_error("agent_core", f"Tool {name} instantiation failed: {e}")
                                continue
                        
                        if instance:
                            self.tools[name.lower()] = instance
                            registered += 1
                            log_info("agent_core", f"Registered tool: {name}")
                            
                    except Exception as e:
                        log_error("agent_core", f"Failed to register tool {name}: {e}")
        
        except Exception as e:
            log_error("agent_core", f"Failed to inspect module {module_name}: {e}")
        
        return registered
    
    async def _initialize_monitoring(self):
        """Initialize performance monitoring"""
        log_info("agent_core", "Initializing performance monitoring...")
        try:
            from utils.performance_monitor import PerformanceMonitor
            self.performance_monitor = PerformanceMonitor()
            log_info("agent_core", "Performance monitoring initialized")
        except ImportError:
            log_info("agent_core", "Performance monitoring not available")
            self.performance_monitor = None
    
    async def process_command_enhanced(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced command processing with model awareness"""
        if not self.is_running:
            raise RuntimeError("Enhanced agent is not running. Call initialize() first.")
        
        context = context or {}
        self.current_task = command
        
        # Log command processing start
        log_ai_decision("agent_core", f"Processing command: {command}",
                       ai_model="ultron_agent", confidence_score=0.9)
        
        try:
            response = {
                "command": command,
                "response": f"ULTRON Enhanced received: {command}",
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "agent_version": "3.0_enhanced"
            }
            
            # Enhanced tool matching with logging
            matching_tools = []
            for tool_name, tool in self.tools.items():
                try:
                    if hasattr(tool, "match"):
                        match_result = await self._safe_tool_match(tool, command, context)
                        if match_result:
                            matching_tools.append((tool_name, tool))
                            log_info("agent_core", f"Tool matched: {tool_name}")
                except Exception as e:
                    log_error("agent_core", f"Tool {tool_name} match failed: {e}")
            
            # Execute matching tools with enhanced error handling
            if matching_tools:
                tool_results = []
                for tool_name, tool in matching_tools:
                    try:
                        result = await self._safe_tool_execute(tool, command, context)
                        tool_results.append({
                            "tool": tool_name,
                            "result": result,
                            "success": True
                        })
                        log_info("agent_core", f"Tool {tool_name} executed successfully")
                    except Exception as e:
                        log_error("agent_core", f"Tool {tool_name} execution failed: {e}")
                        tool_results.append({
                            "tool": tool_name,
                            "error": str(e),
                            "success": False
                        })
                
                response["tools"] = tool_results
                response["response"] = f"Executed {len(tool_results)} tools for: {command}"
            
            # Try brain processing if available
            if self.brain and not matching_tools:
                try:
                    brain_response = await self.brain.plan_and_act(command)
                    if brain_response:
                        response["brain_response"] = brain_response
                        response["response"] = brain_response
                        log_info("agent_core", "Brain processing completed")
                except Exception as e:
                    log_error("agent_core", f"Brain processing failed: {e}")
            
            return response
        
        except Exception as e:
            log_error("agent_core", f"Enhanced command processing failed: {e}")
            return {
                "command": command,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent_version": "3.0_enhanced"
            }
        finally:
            self.current_task = None
    
    async def _safe_tool_match(self, tool, command: str, context: Dict[str, Any]):
        """Safely execute tool match with proper error handling"""
        try:
            match_fn = tool.match
            sig = inspect.signature(match_fn)
            param_count = len(sig.parameters)
            
            if param_count <= 1:
                result = match_fn(command)
            else:
                result = match_fn(command, context)
            
            if inspect.isawaitable(result):
                result = await result
            
            return result
        except Exception as e:
            log_error("agent_core", f"Tool match error: {e}")
            return False
    
    async def _safe_tool_execute(self, tool, command: str, context: Dict[str, Any]):
        """Safely execute tool with proper error handling"""
        try:
            result = tool.execute(command, context)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as e:
            log_error("agent_core", f"Tool execution error: {e}")
            raise
    
    async def speak_enhanced(self, text: str, async_mode: bool = True):
        """Enhanced speak with better error handling"""
        if self.voice and hasattr(self.voice, 'speak'):
            try:
                if async_mode:
                    import threading
                    threading.Thread(target=self.voice.speak, args=(text,)).start()
                else:
                    await self.voice.speak(text) if inspect.iscoroutinefunction(self.voice.speak) else self.voice.speak(text)
                
                log_info("agent_core", f"Voice output: {text[:50]}...")
                return True
            except Exception as e:
                log_error("agent_core", f"Voice speaking failed: {e}")
                return False
        return False
    
    async def start_voice_listening_enhanced(self):
        """Enhanced voice listening with better error recovery"""
        if not self.voice:
            log_error("agent_core", "Voice system not initialized")
            return False
        
        try:
            log_info("agent_core", "Starting enhanced voice listening...")
            await self.speak_enhanced("Enhanced voice system activated. I'm listening for commands.")
            
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while self.is_running:
                try:
                    if hasattr(self.voice, 'listen'):
                        command = await self.voice.listen() if inspect.iscoroutinefunction(self.voice.listen) else self.voice.listen()
                        
                        if command and command.strip():
                            log_info("agent_core", f"Voice command received: {command}")
                            response = await self.process_command_enhanced(command)
                            
                            if response.get("success") and response.get("response"):
                                await self.speak_enhanced(response["response"])
                            
                            consecutive_errors = 0  # Reset error counter on success
                    else:
                        log_error("agent_core", "Voice system doesn't support listening")
                        break
                    
                    await asyncio.sleep(0.1)
                
                except Exception as e:
                    consecutive_errors += 1
                    log_error("agent_core", f"Voice listening error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        log_error("agent_core", "Too many consecutive voice errors, stopping voice listening")
                        break
                    
                    await asyncio.sleep(1)  # Wait before retrying
            
            return True
        
        except Exception as e:
            log_error("agent_core", f"Enhanced voice listening failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        uptime = datetime.now() - self.startup_time
        
        status = {
            "agent_version": "3.0_enhanced",
            "status": self.status.value,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime),
            "security_mode": self.security_mode,
            "tools_loaded": len(self.tools),
            "current_task": self.current_task,
            "components": {
                "brain": self.brain is not None,
                "voice": self.voice is not None,
                "vision": self.vision is not None,
                "memory": self.memory is not None,
                "performance_monitor": self.performance_monitor is not None
            }
        }
        
        # Add performance metrics if available
        if self.performance_monitor:
            try:
                status["performance"] = self.performance_monitor.get_metrics()
            except Exception as e:
                log_error("agent_core", f"Failed to get performance metrics: {e}")
        
        return status
    
    def list_tools_enhanced(self) -> List[Dict[str, Any]]:
        """Get detailed list of loaded tools"""
        tools_info = []
        
        for name, tool in self.tools.items():
            tool_info = {
                "name": name,
                "class": tool.__class__.__name__,
                "description": getattr(tool, 'description', 'No description available'),
                "has_match": hasattr(tool, 'match'),
                "has_execute": hasattr(tool, 'execute'),
                "has_schema": hasattr(tool, 'schema')
            }
            
            if hasattr(tool, 'schema'):
                try:
                    tool_info["schema"] = tool.schema()
                except Exception as e:
                    tool_info["schema_error"] = str(e)
            
            tools_info.append(tool_info)
        
        return sorted(tools_info, key=lambda x: x["name"])
    
    async def shutdown_enhanced(self):
        """Enhanced shutdown with proper cleanup"""
        log_info("agent_core", "Starting enhanced shutdown sequence...")
        
        self.is_running = False
        self.status = AgentStatus.MAINTENANCE
        
        # Stop voice system
        if self.voice and hasattr(self.voice, 'stop_voice'):
            try:
                self.voice.stop_voice()
                log_info("agent_core", "Voice system stopped")
            except Exception as e:
                log_error("agent_core", f"Error stopping voice system: {e}")
        
        # Cleanup performance monitor
        if self.performance_monitor and hasattr(self.performance_monitor, 'stop'):
            try:
                self.performance_monitor.stop()
                log_info("agent_core", "Performance monitor stopped")
            except Exception as e:
                log_error("agent_core", f"Error stopping performance monitor: {e}")
        
        # Clean up model awareness data
        try:
            from utils.model_awareness import cleanup_old_tracking_data
            cleanup_old_tracking_data(days=1)  # Clean up old data
            log_info("agent_core", "Model awareness cleanup completed")
        except Exception as e:
            log_error("agent_core", f"Error during model awareness cleanup: {e}")
        
        log_info("agent_core", "Enhanced ULTRON Agent shutdown complete")

# Convenience function for backward compatibility
async def create_enhanced_agent(config_path: str = "ultron_config.json") -> UltronAgentEnhanced:
    """Create and initialize an enhanced ULTRON agent"""
    agent = UltronAgentEnhanced(config_path)
    await agent.initialize()
    return agent