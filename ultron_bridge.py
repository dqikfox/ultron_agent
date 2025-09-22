#!/usr/bin/env python3
"""
Ultron Agent Bridge - Integration Script
Connects to and manages Ultron Agent modules with Ollama integration
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import json

# Add Ultron Agent project to Python path
sys.path.insert(0, r'C:\Projects\ultron_agent_2')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultron_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UltronBridge:
    """Bridge class for Ultron Agent integration with Ollama"""

    def __init__(self, port: int = 5001):
        self.port = port
        self.brain = None
        self.config = {}
        self.initialized = False

        # Module availability flags
        self.brain_available = False
        self.file_manager_available = False
        self.voice_recognizer_available = False
        self.computer_vision_available = False
        self.system_controller_available = False

        logger.info(f"UltronBridge initialized on port {port}")

    async def initialize(self) -> bool:
        """Initialize Ultron Agent brain and modules"""
        try:
            logger.info("Initializing Ultron Agent brain...")

            # Load configuration
            await self._load_config()

            # Initialize brain with Ollama integration
            await self._init_brain()

            # Set other modules as unavailable for now
            self.file_manager_available = False
            self.voice_recognizer_available = False
            self.computer_vision_available = False
            self.system_controller_available = False

            self.initialized = True
            logger.info("Ultron Agent modules initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")
            return False

    async def _load_config(self):
        """Load Ultron configuration"""
        try:
            config_path = Path(r'C:\Projects\ultron_agent_2\ultron_config.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info("Configuration loaded successfully")
            else:
                logger.warning("Configuration file not found, using defaults")
                self.config = {
                    "ollama_base_url": "http://localhost:11434",
                    "llm_model": "llama3.2:latest"
                }
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = {
                "ollama_base_url": "http://localhost:11434",
                "llm_model": "llama3.2:latest"
            }

    async def _init_brain(self):
        """Initialize Ultron Brain with Ollama integration"""
        try:
            # Create a minimal brain class for Ollama integration
            class MinimalBrain:
                def __init__(self, config):
                    self.config = config

                async def direct_chat(self, prompt: str) -> str:
                    """Send a direct message to the LLM via Ollama API."""
                    if not prompt or not prompt.strip():
                        return "Empty prompt provided."

                    logger.info(f"Processing prompt: '{prompt[:100]}...' (length: {len(prompt)})")
                    ollama_base_url = self.config.get("ollama_base_url", "http://localhost:11434")
                    model = self.config.get("llm_model", "llama3.2:latest")

                    logger.info(f"Sending prompt to Ollama model '{model}' at {ollama_base_url}")

                    try:
                        import aiohttp
                        from aiohttp import ClientSession, ClientTimeout, ClientError
                        import json

                        payload = {
                            "model": model,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are ULTRON AI, a helpful AI assistant with system control capabilities. You have access to voice commands, system diagnostics, file operations, and web browsing."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "stream": False  # Disable streaming for simplicity
                        }

                        timeout = ClientTimeout(total=60)  # Increased timeout for system commands

                        async with ClientSession(timeout=timeout) as session:
                            async with session.post(f"{ollama_base_url}/api/chat",
                                                   json=payload,
                                                   headers={"Accept": "application/json"}) as response:
                                response.raise_for_status()
                                # Handle both JSON and text responses
                                if response.content_type == 'application/json':
                                    data = await response.json()
                                else:
                                    # Fallback for text/plain responses
                                    text_content = await response.text()
                                    try:
                                        data = json.loads(text_content)
                                    except json.JSONDecodeError:
                                        return f"[LLM error: Invalid response format: {text_content[:100]}...]"

                                reply = data.get("message", {}).get("content", "").strip()

                                if reply:
                                    logger.info(f"Successfully received response from {model} ({len(reply)} chars)")
                                    return reply
                                else:
                                    return "[LLM error: No content received]"

                    except ClientError as e:
                        logger.error(f"Network error connecting to Ollama: {e}")
                        return f"[Network error: {e}]"
                    except Exception as e:
                        logger.error(f"Unexpected error in direct_chat: {type(e).__name__}: {str(e)}")
                        logger.error(f"Error details: {repr(e)}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return f"[LLM error: {type(e).__name__}: {str(e)}]"

                def think(self, message: str) -> str:
                    """Sync wrapper for direct_chat"""
                    try:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            response = loop.run_until_complete(self.direct_chat(message))
                            return response
                        finally:
                            loop.close()
                    except Exception as e:
                        logger.error(f"Error in think method: {e}")
                        return f"Error processing request: {e}"

            self.brain = MinimalBrain(self.config)
            self.brain_available = True
            logger.info("Minimal Brain with Ollama integration initialized")
        except Exception as e:
            logger.error(f"Brain initialization failed: {e}")
            self.brain = self._create_fallback_brain()

    def _create_fallback_brain(self):
        """Create fallback brain when main brain unavailable"""
        class FallbackBrain:
            async def direct_chat(self, prompt: str) -> str:
                return f"Fallback Brain: Would process '{prompt[:50]}...' but Ollama not connected"

            def think(self, message: str) -> str:
                return f"Fallback Brain: {message}"

        return FallbackBrain()

    # Fallback implementations
    def _create_fallback_file_manager(self):
        """Create fallback FileManager"""
        class FallbackFileManager:
            def create_file(self, path: str, content: str = "") -> bool:
                try:
                    Path(path).write_text(content)
                    return True
                except Exception as e:
                    logger.error(f"File creation failed: {e}")
                    return False

            def read_file(self, path: str) -> Optional[str]:
                try:
                    return Path(path).read_text()
                except Exception as e:
                    logger.error(f"File read failed: {e}")
                    return None

            def delete_file(self, path: str) -> bool:
                try:
                    Path(path).unlink()
                    return True
                except Exception as e:
                    logger.error(f"File deletion failed: {e}")
                    return False

        return FallbackFileManager()

    def _create_fallback_ai_engine(self):
        """Create fallback AIEngine"""
        class FallbackAIEngine:
            def process_command(self, command: str) -> str:
                return f"Fallback AI: Processed command '{command}'"

            def chat(self, message: str) -> str:
                return f"Fallback AI: {message}"

        return FallbackAIEngine()

    def _create_fallback_voice_recognizer(self):
        """Create fallback VoiceRecognizer"""
        class FallbackVoiceRecognizer:
            def listen(self) -> Optional[str]:
                logger.info("Fallback voice: No voice input available")
                return None

            def speak(self, text: str) -> bool:
                print(f"Voice: {text}")
                return True

        return FallbackVoiceRecognizer()

    def _create_fallback_computer_vision(self):
        """Create fallback ComputerVision"""
        class FallbackComputerVision:
            def analyze_screen(self) -> Dict[str, Any]:
                return {"status": "fallback", "message": "Computer vision not available"}

            def find_element(self, element: str) -> Optional[Dict[str, int]]:
                return None

        return FallbackComputerVision()

    def _create_fallback_system_controller(self):
        """Create fallback SystemController"""
        class FallbackSystemController:
            def execute_command(self, command: str) -> str:
                return f"Fallback system: Command '{command}' not executed"

            def get_system_info(self) -> Dict[str, Any]:
                return {"status": "fallback", "system": "unknown"}

        return FallbackSystemController()

    # Command processing methods
    async def process_command(self, command: str) -> Dict[str, Any]:
        """Process natural language command and route to appropriate module"""
        if not self.initialized:
            return {"error": "Bridge not initialized"}

        logger.info(f"Processing command: {command}")

        try:
            # Route command based on keywords
            command_lower = command.lower()

            if any(word in command_lower for word in ['create', 'file', 'write', 'save']):
                return await self._handle_file_command(command)
            elif any(word in command_lower for word in ['ai', 'chat', 'ask', 'think']):
                return await self._handle_ai_command(command)
            elif any(word in command_lower for word in ['voice', 'speak', 'listen', 'say']):
                return await self._handle_voice_command(command)
            elif any(word in command_lower for word in ['vision', 'see', 'screen', 'image']):
                return await self._handle_vision_command(command)
            elif any(word in command_lower for word in ['system', 'execute', 'run', 'command']):
                return await self._handle_system_command(command)
            else:
                return {"result": "Command not recognized", "module": "none"}

        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {"error": str(e)}

    async def _handle_file_command(self, command: str) -> Dict[str, Any]:
        """Handle file-related commands using brain with Ollama"""
        try:
            # Use brain to process file commands via Ollama
            if self.brain and self.brain_available:
                ollama_prompt = f"Process this file command as ULTRON AI assistant: {command}"
                result = await self.brain.direct_chat(ollama_prompt)
                return {"result": result, "module": "brain_ollama"}
            else:
                return {"error": "Brain not available for file commands"}

        except Exception as e:
            return {"error": f"File command failed: {e}"}

    async def _handle_ai_command(self, command: str) -> Dict[str, Any]:
        """Handle AI-related commands using brain with Ollama"""
        try:
            if not self.brain:
                return {"error": "Brain not available"}

            # Use brain's direct_chat method for Ollama integration
            if hasattr(self.brain, 'direct_chat') and self.brain_available:
                result = await self.brain.direct_chat(command)
                return {"result": result, "module": "brain_ollama"}
            else:
                # Fallback to think method
                result = self.brain.think(command)
                return {"result": result, "module": "brain_fallback"}

        except Exception as e:
            return {"error": f"AI command failed: {e}"}

    async def _handle_voice_command(self, command: str) -> Dict[str, Any]:
        """Handle voice-related commands using brain with Ollama"""
        try:
            # Use brain to process voice commands via Ollama
            if self.brain and self.brain_available:
                ollama_prompt = f"Process this voice command as ULTRON AI assistant: {command}"
                result = await self.brain.direct_chat(ollama_prompt)
                return {"result": result, "module": "brain_ollama"}
            else:
                return {"error": "Brain not available for voice commands"}

        except Exception as e:
            return {"error": f"Voice command failed: {e}"}

    async def _handle_vision_command(self, command: str) -> Dict[str, Any]:
        """Handle computer vision commands using brain with Ollama"""
        try:
            # Use brain to process vision commands via Ollama
            if self.brain and self.brain_available:
                ollama_prompt = f"Process this vision command as ULTRON AI assistant: {command}"
                result = await self.brain.direct_chat(ollama_prompt)
                return {"result": result, "module": "brain_ollama"}
            else:
                return {"error": "Brain not available for vision commands"}

        except Exception as e:
            return {"error": f"Vision command failed: {e}"}

    async def _handle_system_command(self, command: str) -> Dict[str, Any]:
        """Handle system-related commands using brain with Ollama"""
        try:
            # Use brain to process system commands via Ollama with retry logic
            if self.brain and self.brain_available:
                ollama_prompt = f"As ULTRON AI, provide system information. Command: {command}"

                # Try up to 3 times for system commands
                for attempt in range(3):
                    try:
                        logger.info(f"Attempt {attempt + 1}/3 for system command")
                        result = await self.brain.direct_chat(ollama_prompt)
                        return {"result": result, "module": "brain_ollama"}
                    except Exception as e:
                        if attempt < 2:  # Don't wait after last attempt
                            logger.warning(f"System command attempt {attempt + 1} failed: {e}, retrying...")
                            await asyncio.sleep(2)  # Wait 2 seconds before retry
                        else:
                            logger.error(f"All attempts failed for system command: {e}")
                            return {"error": f"System command failed after 3 attempts: {e}"}

                return {"error": "System command failed after retries"}
            else:
                return {"error": "Brain not available for system commands"}

        except Exception as e:
            return {"error": f"System command failed: {e}"}

    def get_status(self) -> Dict[str, Any]:
        """Get bridge and module status"""
        return {
            "initialized": self.initialized,
            "port": self.port,
            "modules": {
                "brain": self.brain_available,
                "file_manager": self.file_manager_available,
                "voice_recognizer": self.voice_recognizer_available,
                "computer_vision": self.computer_vision_available,
                "system_controller": self.system_controller_available
            },
            "ollama_config": {
                "base_url": self.config.get("ollama_base_url", "http://localhost:11434"),
                "model": self.config.get("llm_model", "llama3.2:latest")
            },
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Example usage of UltronBridge"""
    logger.info("Starting Ultron Bridge example")

    # Create and initialize bridge
    bridge = UltronBridge(port=5001)
    success = await bridge.initialize()

    if not success:
        logger.error("Failed to initialize bridge")
        return

    # Show status
    status = bridge.get_status()
    logger.info(f"Bridge status: {status}")

    # Example commands
    commands = [
        "create a test file",
        "ask ai about the weather",
        "speak hello world",
        "analyze the screen",
        "get system information"
    ]

    for command in commands:
        logger.info(f"Executing: {command}")
        result = await bridge.process_command(command)
        logger.info(f"Result: {result}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
