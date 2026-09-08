#!/usr/bin/env python3
"""
AI Toolkit - GPT-5 Integration for Ultron Agent
Handles OpenAI API connections and model management
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
from openai import AsyncOpenAI
import logging

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
    
    def __post_init__(self):
        if self.preferred_models is None:
            self.preferred_models = ["gpt-5-turbo", "gpt-5", "gpt-4o", "gpt-4-turbo"]

class AIToolkit:
    """AI Toolkit for GPT-5 and OpenAI integration"""
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.client = None
        self.available_models = []
        self._initialize_client()
    
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
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test AI connection and capabilities"""
        try:
            if not self.client:
                return {"status": "error", "message": "No API key configured"}
            
            # Get available models
            models = await self.get_available_models()
            
            # Test simple completion
            test_messages = [{"role": "user", "content": "Hello, are you working?"}]
            response = await self.chat_completion(test_messages)
            
            return {
                "status": "success",
                "model": self.config.model,
                "gpt5_available": self.is_gpt5_available(),
                "gpt5_models": self.get_gpt5_models(),
                "models_count": len(models),
                "test_response": response[:100] if response else None,
                "organization": self.config.organization,
                "project": self.config.project
            }
            
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