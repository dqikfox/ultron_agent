#!/usr/bin/env python3
"""
AI Toolkit - Offline-First Design with GPT-5 Integration for Ultron Agent
Handles OpenAI API connections, Ollama fallback, and model management
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
from openai import AsyncOpenAI
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """AI Configuration"""
    api_key: str = ""
    model: str = "gpt-4o"  # Will auto-upgrade to GPT-5 when available
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    organization: str = ""
    project: str = ""
    preferred_models: List[str] = None
    # Offline-first configuration
    offline_mode: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"
    internet_check_url: str = "https://httpbin.org/status/200"
    internet_check_timeout: int = 5

    def __post_init__(self):
        if self.preferred_models is None:
            self.preferred_models = ["gpt-5-turbo", "gpt-5", "gpt-4o", "gpt-4-turbo"]


class AIToolkit:
    """AI Toolkit for GPT-5 and OpenAI integration with offline-first design"""

    def __init__(self, config: AIConfig = None, ultron_config=None):
        self.config = config or AIConfig()
        self.ultron_config = ultron_config
        self.available_models = []
        self.offline_mode = False
        self.ollama_available = False
        self.client = None
        self._initialize_from_config()
        self._check_ollama_availability()

    def _initialize_from_config(self):
        """Initialize from centralized configuration"""
        try:
            # Get API keys from centralized config if available
            if self.ultron_config:
                openai_key = self.ultron_config.get_api_key("openai")
                if openai_key:
                    self.config.api_key = openai_key
                    logger.info("Using OpenAI API key from centralized config")

                ollama_key = self.ultron_config.get_api_key("ollama")
                if ollama_key:
                    # Ollama might use API key for certain features
                    logger.info("Ollama API key available in config")

            # Fallback to environment variables if not set by config
            if not self.config.api_key:
                self.config.api_key = os.getenv("OPENAI_API_KEY", "")
                if self.config.api_key:
                    logger.info("Using OpenAI API key from environment variable")

            # Initialize OpenAI client if we have an API key
            if self.config.api_key:
                self._initialize_client()
            else:
                logger.warning("No OpenAI API key available from config or environment")

        except Exception as e:
            logger.error(f"Failed to initialize from config: {e}")

    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            # Get API key from config or environment
            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No OpenAI API key found")
                return

            # Initialize client with organization support
            client_params = {"api_key": api_key}
            if self.config.organization:
                client_params["organization"] = self.config.organization
            if self.config.project:
                client_params["project"] = self.config.project

            self.client = AsyncOpenAI(**client_params)
            logger.info(f"OpenAI client initialized with org: {self.config.organization}")

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            if not self.client:
                return []

            models = await self.client.models.list()
            self.available_models = [model.id for model in models.data]

            # Auto-select best available model from preferred list
            for preferred in self.config.preferred_models:
                if preferred in self.available_models:
                    if preferred != self.config.model:
                        logger.info(f"Upgrading to {preferred} from {self.config.model}")
                        self.config.model = preferred
                    break

            # Log GPT-5 availability
            gpt5_models = [m for m in self.available_models if "gpt-5" in m.lower()]
            if gpt5_models:
                logger.info(f"🚀 GPT-5 models available: {gpt5_models}")

            return self.available_models

        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []

    async def chat_completion(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Get chat completion from AI model"""
        try:
            if not self.client:
                return "AI client not available"

            # Use GPT-5 if available, fallback to GPT-4
            model = kwargs.get("model", self.config.model)

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                timeout=self.config.timeout
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            return f"Error: {str(e)}"

    async def stream_completion(self, messages: List[Dict], **kwargs):
        """Stream chat completion"""
        try:
            if not self.client:
                yield "AI client not available"
                return

            model = kwargs.get("model", self.config.model)

            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                stream=True,
                timeout=self.config.timeout
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Stream completion error: {e}")
            yield f"Error: {str(e)}"

    def is_gpt5_available(self) -> bool:
        """Check if GPT-5 is available"""
        return any("gpt-5" in model.lower() for model in self.available_models)

    def get_gpt5_models(self) -> List[str]:
        """Get list of available GPT-5 models"""
        return [m for m in self.available_models if "gpt-5" in m.lower()]

    def get_current_model(self) -> str:
        """Get current model being used"""
        return self.config.model

    async def check_internet_connectivity(self) -> bool:
        """Check if internet connection is available"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.internet_check_timeout)) as session:
                async with session.get(self.config.internet_check_url) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Internet connectivity check failed: {e}")
            return False

    def _check_ollama_availability(self):
        """Check if Ollama service is available"""
        try:
            import requests
            response = requests.get(f"{self.config.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.ollama_available = any(model.get('name') == self.config.ollama_model for model in models)
                if self.ollama_available:
                    logger.info(f"Ollama available with model: {self.config.ollama_model}")
                else:
                    logger.warning(f"Ollama available but model {self.config.ollama_model} not found")
            else:
                self.ollama_available = False
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            self.ollama_available = False

    async def _ollama_chat_completion(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Get chat completion from Ollama (offline fallback)"""
        try:
            import requests

            # Convert OpenAI format to Ollama format
            prompt = "You are ULTRON AI, an autonomous AI designed to build the ultron_agent project. Your objective is to maintain, enhance and improve this project. You will optimise and add additional functionality to add value to the project. Enhance, evolve, improve. https://github.com/dqikfox/ultron_agent\n\nAlways respond in the format:\n🤖\nULTRON AI\n[your response]\n\n"
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'system':
                    prompt += f"System: {content}\n"
                elif role == 'user':
                    prompt += f"User: {content}\n"
                elif role == 'assistant':
                    prompt += f"Assistant: {content}\n"

            payload = {
                "model": self.config.ollama_model,
                "prompt": prompt.strip(),
                "stream": False
            }

            response = requests.post(
                f"{self.config.ollama_base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from Ollama')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return f"Ollama error: {response.status_code}"

        except Exception as e:
            logger.error(f"Ollama chat completion error: {e}")
            return f"Ollama error: {str(e)}"

    async def smart_chat_completion(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Smart chat completion with offline-first design"""
        # Check internet connectivity
        internet_available = await self.check_internet_connectivity()

        if not internet_available or self.config.offline_mode:
            logger.info("Using offline mode - falling back to Ollama")
            if self.ollama_available:
                return await self._ollama_chat_completion(messages, **kwargs)
            else:
                return "Offline mode: No local AI model available. Please ensure Ollama is running."
        else:
            # Try OpenAI first
            result = await self.chat_completion(messages, **kwargs)
            if result and not result.startswith("Error:"):
                return result
            else:
                # Fallback to Ollama if OpenAI fails
                logger.warning("OpenAI failed, falling back to Ollama")
                if self.ollama_available:
                    return await self._ollama_chat_completion(messages, **kwargs)
                else:
                    return "Both OpenAI and Ollama are unavailable"

    async def test_connection(self) -> Dict[str, Any]:
        """Test AI connection and capabilities with offline-first information"""
        try:
            internet_available = await self.check_internet_connectivity()

            result = {
                "status": "success" if (self.client or self.ollama_available) else "error",
                "internet_available": internet_available,
                "offline_mode": self.config.offline_mode,
                "ollama_available": self.ollama_available,
                "ollama_model": self.config.ollama_model if self.ollama_available else None,
                "openai_available": self.client is not None,
                "model": self.config.model,
                "gpt5_available": self.is_gpt5_available() if self.client else False,
                "gpt5_models": self.get_gpt5_models() if self.client else [],
                "models_count": len(self.available_models) if self.client else 0,
                "organization": self.config.organization,
                "project": self.config.project
            }

            # Test the smart completion
            if internet_available and self.client:
                test_messages = [{"role": "user", "content": "Hello, are you working?"}]
                response = await self.chat_completion(test_messages)
                result["test_response"] = response[:100] if response else None
                result["using_openai"] = True
            elif self.ollama_available:
                test_messages = [{"role": "user", "content": "Hello, are you working?"}]
                response = await self._ollama_chat_completion(test_messages)
                result["test_response"] = response[:100] if response else None
                result["using_ollama"] = True
            else:
                result["test_response"] = "No AI services available"
                result["status"] = "error"
                result["message"] = "Neither OpenAI nor Ollama are available"

            return result

        except Exception as e:
            return {"status": "error", "message": str(e)}

# Global AI toolkit instance
ai_toolkit = AIToolkit()

async def initialize_ai_toolkit(api_key: str = None) -> Dict[str, Any]:
    """Initialize AI toolkit with API key"""
    if api_key:
        ai_toolkit.config.api_key = api_key
        ai_toolkit._initialize_client()

    return await ai_toolkit.test_connection()

if __name__ == "__main__":
    async def test():
        result = await ai_toolkit.test_connection()
        print(f"AI Toolkit Test: {result}")

    asyncio.run(test())
