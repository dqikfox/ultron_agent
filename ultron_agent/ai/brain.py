"""
ULTRON Agent 3.0 - Brain Module with Ollama Integration
Handles AI reasoning, planning, and communication with Ollama models
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from aiohttp import ClientError, ClientSession, ClientTimeout

from ..config import UltronConfig
from ..errors import UltronError, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class UltronBrain:
    """AI brain module for reasoning, planning, and model communication."""
    
    def __init__(
        self,
        config: UltronConfig,
        tools: Optional[Any] = None,
        memory: Optional[Any] = None
    ) -> None:
        """Initialize the brain with config, tools, and memory."""
        self.config = config
        self.tools = tools
        self.memory = memory
        self.cache_file = Path("cache.json")
        self.cache: Dict[str, Any] = {}
        
        # Initialize components
        self.agent_network: Optional[Any] = None
        self.openai_tools: Optional[Any] = None
        
        self._load_cache()
        self._initialize_components()

    def _load_cache(self) -> None:
        """Load cached responses from disk."""
        try:
            if self.cache_file.exists():
                with self.cache_file.open('r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info("Cache loaded successfully")
            else:
                self.cache = {}
                logger.info("No existing cache found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.cache = {}

    def _save_cache(self) -> None:
        """Save responses to cache."""
        try:
            with self.cache_file.open('w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _initialize_components(self) -> None:
        """Initialize optional components like agent network and OpenAI tools."""
        # Initialize agent network if available
        try:
            from tools.agent_network import AgentNetwork
            self.agent_network = AgentNetwork(self.config)
            logger.info("Agent network initialized")
        except ImportError:
            logger.warning("Agent network not available")
        except Exception as e:
            logger.warning(f"Failed to initialize agent network: {e}")

        # Initialize OpenAI tools if available  
        try:
            from tools.openai_tools import OpenAITools
            self.openai_tools = OpenAITools(self.config)
            logger.info("OpenAI tools initialized")
        except ImportError:
            logger.warning("OpenAI tools not available")
        except Exception as e:
            logger.warning(f"OpenAI tools not available: {e}")

    async def direct_chat(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """Send a direct message to the LLM via Ollama API."""
        if not prompt or not prompt.strip():
            raise UltronError(
                "Empty prompt provided",
                category=ErrorCategory.MODEL,
                severity=ErrorSeverity.LOW,
                recovery_suggestion="Provide a non-empty prompt"
            )

        ollama_base_url = self.config.ollama_base_url
        model = self.config.llm_model
        
        logger.info(f"Sending prompt to Ollama model '{model}' at {ollama_base_url}")

        try:
            headers = {}
            if self.config.ollama_api_key:
                headers["Authorization"] = f"Bearer {self.config.ollama_api_key}"

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True  # Enable streaming for better UX
            }

            timeout = ClientTimeout(total=60)  # 60 second timeout

            async with ClientSession(timeout=timeout) as session:
                if progress_callback:
                    progress_callback(20, f"Connecting to Ollama model '{model}'...")

                async with session.post(
                    f"{ollama_base_url}/api/chat",
                    json=payload,
                    headers=headers
                ) as response:
                    response.raise_for_status()

                    reply_parts: List[str] = []
                    chunk_count = 0

                    if progress_callback:
                        progress_callback(40, "Receiving response...")

                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue
                            
                        try:
                            chunk_data = json.loads(line)
                            if "message" in chunk_data and "content" in chunk_data["message"]:
                                content = chunk_data["message"]["content"]
                                if content:
                                    reply_parts.append(content)
                                    chunk_count += 1
                                    
                                    # Update progress every few chunks
                                    if progress_callback and chunk_count % 5 == 0:
                                        progress = min(80, 40 + chunk_count * 2)
                                        progress_callback(progress, "Processing response...")

                            if chunk_data.get("done"):
                                break
                                
                        except json.JSONDecodeError:
                            continue

                    if progress_callback:
                        progress_callback(100, "Complete")

                    full_response = ''.join(reply_parts).strip()
                    
                    if not full_response:
                        raise UltronError(
                            "Received empty response from model",
                            category=ErrorCategory.MODEL,
                            severity=ErrorSeverity.MEDIUM,
                            recovery_suggestion="Try rephrasing your request or check model status"
                        )

                    # Cache the response
                    cache_key = f"{model}:{hash(prompt)}"
                    self.cache[cache_key] = {
                        "prompt": prompt,
                        "response": full_response,
                        "model": model,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    self._save_cache()

                    logger.info(f"Successfully received response ({len(full_response)} chars)")
                    return full_response

        except ClientError as e:
            raise UltronError(
                f"Failed to communicate with Ollama: {e}",
                category=ErrorCategory.MODEL,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Check Ollama server status and network connection",
                original_error=e
            )
        except Exception as e:
            raise UltronError(
                f"Unexpected error during chat: {e}",
                category=ErrorCategory.MODEL,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Check logs for detailed error information",
                original_error=e
            )

    async def think(self, query: str) -> str:
        """Process a query through the brain's reasoning pipeline."""
        try:
            # For now, delegate to direct_chat, but this could be expanded
            # to include more sophisticated reasoning, tool selection, etc.
            return await self.direct_chat(query)
        except Exception as e:
            logger.error(f"Error in think method: {e}")
            raise

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        return {
            "entries": len(self.cache),
            "size_bytes": len(json.dumps(self.cache).encode('utf-8')),
            "models_used": list({entry.get("model") for entry in self.cache.values() if entry.get("model")})
        }

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Cache cleared")