"""
OpenAI Tools Integration for ULTRON Agent
Provides OpenAI API integration for enhanced AI capabilities
"""

import logging
from typing import Dict, Any, Optional, List
import aiohttp
import json


class OpenAITools:
    """OpenAI tools integration for ULTRON"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = config.get('openai_api_key') if config else None
        self.base_url = "https://api.openai.com/v1"
        self.available = bool(self.api_key)

        if not self.available:
            self.logger.warning("OpenAI API key not configured - OpenAI tools disabled")

    async def generate_completion(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> Optional[str]:
        """Generate completion using OpenAI API"""
        if not self.available:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/chat/completions", headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        self.logger.error(f"OpenAI API error: {response.status}")
                        return None

        except Exception as e:
            self.logger.error(f"OpenAI completion failed: {e}")
            return None

    async def get_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> Optional[List[float]]:
        """Get embeddings for text using OpenAI"""
        if not self.available:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "input": text,
                "model": model
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/embeddings", headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["data"][0]["embedding"]
                    else:
                        self.logger.error(f"OpenAI embeddings error: {response.status}")
                        return None

        except Exception as e:
            self.logger.error(f"OpenAI embeddings failed: {e}")
            return None
