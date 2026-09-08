"""
ULTRON Agent Core System
Main agent initialization and core functionality
Following copilot instructions architecture
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

# Core imports following project patterns
try:
    from config import Config
except ImportError:
    # Simple config fallback
    class Config:
        def __init__(self):
            self.data = {
                "use_voice": False,
                "use_gui": False,
                "use_vision": False,
                "llm_model": "llama3.2:latest",
                "log_level": "INFO"
            }

        def get(self, key, default=None):
            return self.data.get(key, default)

class UltronAgent:
    """
    Main ULTRON Agent class - Main integration hub per copilot instructions
    Handles command routing, tool loading, and system events
    """

    def __init__(self, config_path: str = "ultron_config.json"):
        """Initialize ULTRON Agent following project architecture"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # Core components per copilot instructions
        self.tools = {}
        self.is_running = False
        self.current_task = None

        # Initialize state
        self.status = {
            'running': False,
            'tools_loaded': 0,
            'memory_size': 0,
            'performance': {},
            'current_task': None
        }

        self.logger.info("ULTRON Agent core initialized")

    def _load_config(self, config_path: str) -> Config:
        """Load configuration following project patterns"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    config = Config()
                    config.data = config_data
                    return config
            else:
                print(f"Config file {config_path} not found, using defaults")
                return Config()
        except Exception as e:
            print(f"Failed to load config: {e}, using defaults")
            return Config()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging per copilot instructions"""
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ultron.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    async def initialize(self):
        """Initialize all components per copilot architecture"""
        try:
            self.logger.info("Initializing ULTRON Agent components...")

            # Initialize core systems per copilot instructions
            await self._initialize_memory()
            await self._initialize_voice()
            await self._initialize_vision()
            await self._initialize_brain()
            await self._load_tools()

            # Update status
            self.status['running'] = True
            self.status['tools_loaded'] = len(self.tools)
            self.is_running = True

            self.logger.info("ULTRON Agent fully initialized and ready")

        except Exception as e:
            self.logger.error(f"Failed to initialize ULTRON Agent: {e}")
            raise

    async def _initialize_memory(self):
        """Initialize memory system"""
        self.logger.info("Initializing memory system...")
        # Placeholder for memory initialization
        pass

    async def _initialize_voice(self):
        """Initialize voice system with fallback chain per copilot instructions"""
        self.logger.info("Initializing voice system (Enhanced → pyttsx3 → OpenAI → Console)...")
        # Placeholder for voice initialization
        pass

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

    async def _load_tools(self):
        """Dynamically load tools from tools/ directory per copilot instructions"""
        tools_dir = Path(__file__).parent / "tools"
        if not tools_dir.exists():
            self.logger.warning("Tools directory not found")
            return

        self.logger.info("Loading tools...")

        # Add tools directory to path
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))

        # Scan for tool files
        for tool_file in tools_dir.glob("*.py"):
            if tool_file.name.startswith("__"):
                continue

            try:
                # Import module
                module_name = tool_file.stem
                spec = importlib.util.spec_from_file_location(module_name, tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find tool classes with match and execute methods
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, 'match') and hasattr(obj, 'execute'):
                        tool_instance = obj(self.config)
                        self.tools[name.lower()] = tool_instance
                        self.logger.info(f"Loaded tool: {name}")

            except Exception as e:
                self.logger.error(f"Failed to load tool from {tool_file}: {e}")

        self.logger.info(f"Loaded {len(self.tools)} tools")

    async def process_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process command through agent system per copilot instructions"""
        if not self.is_running:
            raise RuntimeError("Agent is not running. Call initialize() first.")

        context = context or {}
        self.current_task = command
        self.status['current_task'] = command

        try:
            self.logger.info(f"Processing command: {command}")

            # Basic response
            response = {
                'command': command,
                'response': f"ULTRON received: {command}",
                'timestamp': str(datetime.now()),
                'success': True
            }

            # Check for matching tools
            matching_tools = []
            for tool_name, tool in self.tools.items():
                try:
                    if hasattr(tool, 'match') and await tool.match(command, context):
                        matching_tools.append((tool_name, tool))
                except Exception as e:
                    self.logger.error(f"Tool {tool_name} match failed: {e}")

            # Execute matching tools
            if matching_tools:
                tool_results = []
                for tool_name, tool in matching_tools:
                    try:
                        result = await tool.execute(command, context)
                        tool_results.append({
                            'tool': tool_name,
                            'result': result,
                            'success': True
                        })
                        self.logger.info(f"Tool {tool_name} executed successfully")

                    except Exception as e:
                        self.logger.error(f"Tool {tool_name} execution failed: {e}")
                        tool_results.append({
                            'tool': tool_name,
                            'error': str(e),
                            'success': False
                        })

                response['tools'] = tool_results
                response['response'] = f"Executed {len(tool_results)} tools for: {command}"

            return response

        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            return {
                'command': command,
                'error': str(e),
                'success': False,
                'timestamp': str(datetime.now())
            }
        finally:
            self.current_task = None
            self.status['current_task'] = None

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status per copilot instructions"""
        return {
            'running': self.is_running,
            'current_task': self.current_task,
            'tools_loaded': len(self.tools),
            'memory_size': 0,  # Placeholder
            'performance': {},  # Placeholder
            'config_loaded': bool(self.config)
        }

    def get_available_tools(self) -> List[str]:
        """Get list of available tools per copilot instructions"""
        return list(self.tools.keys())

    async def shutdown(self):
        """Gracefully shutdown agent per copilot instructions"""
        self.logger.info("Shutting down ULTRON Agent...")

        self.is_running = False
        self.status['running'] = False

        # Cleanup components
        # Placeholder for cleanup

        self.logger.info("ULTRON Agent shutdown complete")

# Global agent instance per copilot patterns
_agent_instance = None

async def get_agent(config_path: str = "ultron_config.json") -> UltronAgent:
    """Get or create global agent instance per copilot instructions"""
    global _agent_instance

    if _agent_instance is None:
        _agent_instance = UltronAgent(config_path)
        await _agent_instance.initialize()

    return _agent_instance

if __name__ == "__main__":
    # Test the agent per copilot instructions
    async def test_agent():
        agent = UltronAgent()
        await agent.initialize()

        print("ULTRON Agent Status:", agent.get_status())
        print("Available Tools:", agent.get_available_tools())

        # Test command
        response = await agent.process_command("Hello, what can you do?")
        print("Response:", response)

        await agent.shutdown()

    asyncio.run(test_agent())
