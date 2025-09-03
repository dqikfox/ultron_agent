#!/usr/bin/env python3
"""
NVIDIA NIM Integration Module
============================

Provides seamless integration with NVIDIA NIM (NVIDIA Inference Microservices)
for enterprise-grade AI model access and local LLM deployment.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import requests
import aiohttp
from pathlib import Path

@dataclass
class NIMModelConfig:
    """Configuration for NVIDIA NIM models"""
    model_id: str
    model_name: str
    api_endpoint: str
    api_key: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    supported_features: List[str] = None
    
    def __post_init__(self):
        if self.supported_features is None:
            self.supported_features = ["text_generation", "chat_completion"]

class NVIDIANIMClient:
    """NVIDIA NIM Client for enterprise AI model access"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ULTRON.NIM")
        self.session: Optional[aiohttp.ClientSession] = None
        self.models: Dict[str, NIMModelConfig] = {}
        self.current_model: Optional[str] = None
        self._setup_models()
        
    def _setup_models(self):
        """Setup available NVIDIA NIM models"""
        # Enterprise models
        enterprise_models = {
            "llama-3.1-70b-instruct": NIMModelConfig(
                model_id="llama-3.1-70b-instruct",
                model_name="Llama 3.1 70B Instruct",
                api_endpoint="https://integrate.api.nvidia.com/v1/chat/completions",
                supported_features=["chat_completion", "reasoning", "multilingual"]
            ),
            "nemotron-4-340b-instruct": NIMModelConfig(
                model_id="nemotron-4-340b-instruct", 
                model_name="Nemotron 4 340B Instruct",
                api_endpoint="https://integrate.api.nvidia.com/v1/chat/completions",
                supported_features=["chat_completion", "advanced_reasoning", "enterprise"]
            ),
            "mixtral-8x7b-instruct": NIMModelConfig(
                model_id="mixtral-8x7b-instruct",
                model_name="Mixtral 8x7B Instruct",
                api_endpoint="https://integrate.api.nvidia.com/v1/chat/completions",
                supported_features=["chat_completion", "multilingual", "efficient"]
            )
        }
        
        # Add API keys from config
        nvidia_api_key = self.config.get('nvidia_api_key', '')
        for model in enterprise_models.values():
            model.api_key = nvidia_api_key
            
        self.models.update(enterprise_models)
        
        # Set default model
        self.current_model = "llama-3.1-70b-instruct"
        self.logger.info(f"NVIDIA NIM initialized with {len(self.models)} models")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate chat completion using NVIDIA NIM"""
        try:
            model_id = model or self.current_model
            model_config = self.models.get(model_id)
            
            if not model_config:
                raise ValueError(f"Model {model_id} not found")
            
            if not model_config.api_key:
                self.logger.warning(f"No API key for NVIDIA NIM model {model_id}")
                return {"error": "NVIDIA API key not configured"}
            
            headers = {
                "Authorization": f"Bearer {model_config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_config.model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            start_time = time.time()
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.post(
                model_config.api_endpoint,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    processing_time = time.time() - start_time
                    
                    self.logger.info(
                        f"NVIDIA NIM completion: {model_id} in {processing_time:.2f}s"
                    )
                    
                    return {
                        "content": result["choices"][0]["message"]["content"],
                        "model": model_id,
                        "usage": result.get("usage", {}),
                        "processing_time": processing_time
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"NVIDIA NIM API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
                    
        except Exception as e:
            self.logger.error(f"NVIDIA NIM completion error: {e}")
            return {"error": str(e)}
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        callback=None
    ):
        """Stream chat completion with real-time response"""
        try:
            model_id = model or self.current_model
            model_config = self.models.get(model_id)
            
            if not model_config or not model_config.api_key:
                yield {"error": "Model or API key not available"}
                return
                
            headers = {
                "Authorization": f"Bearer {model_config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_config.model_id,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": True
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.post(
                model_config.api_endpoint,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and data['choices']:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        if callback:
                                            await callback(content)
                                        yield {"content": content, "model": model_id}
                            except json.JSONDecodeError:
                                continue
                else:
                    yield {"error": f"Streaming error: {response.status}"}
                    
        except Exception as e:
            self.logger.error(f"NVIDIA NIM streaming error: {e}")
            yield {"error": str(e)}
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available NVIDIA NIM models"""
        return [
            {
                "id": model_id,
                "name": config.model_name,
                "features": config.supported_features,
                "available": bool(config.api_key)
            }
            for model_id, config in self.models.items()
        ]
    
    def switch_model(self, model_id: str) -> bool:
        """Switch to a different model"""
        if model_id in self.models:
            self.current_model = model_id
            self.logger.info(f"Switched to NVIDIA NIM model: {model_id}")
            return True
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check NVIDIA NIM service health"""
        try:
            # Test with a simple completion
            test_messages = [{"role": "user", "content": "Hello"}]
            result = await self.chat_completion(
                messages=test_messages,
                max_tokens=10
            )
            
            return {
                "status": "healthy" if "content" in result else "unhealthy",
                "current_model": self.current_model,
                "available_models": len(self.models),
                "last_check": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": time.time()
            }


class MultiLLMRouter:
    """Intelligent routing between multiple AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ULTRON.MultiLLM")
        self.providers: Dict[str, Any] = {}
        self.fallback_chain: List[str] = []
        self.performance_metrics: Dict[str, Dict] = {}
        self._setup_providers()
        
    def _setup_providers(self):
        """Initialize AI providers"""
        try:
            # Initialize NVIDIA NIM if available
            if self.config.get('nvidia_api_key'):
                self.providers['nvidia'] = NVIDIANIMClient(self.config)
                self.fallback_chain.append('nvidia')
                self.logger.info("NVIDIA NIM provider initialized")
            
            # Initialize OpenAI if available
            if self.config.get('openai_api_key'):
                from openai import AsyncOpenAI
                self.providers['openai'] = AsyncOpenAI(
                    api_key=self.config['openai_api_key']
                )
                self.fallback_chain.append('openai')
                self.logger.info("OpenAI provider initialized")
            
            # Initialize Anthropic if available  
            if self.config.get('anthropic_api_key'):
                try:
                    import anthropic
                    self.providers['anthropic'] = anthropic.AsyncAnthropic(
                        api_key=self.config['anthropic_api_key']
                    )
                    self.fallback_chain.append('anthropic')
                    self.logger.info("Anthropic provider initialized")
                except ImportError:
                    self.logger.warning("Anthropic library not available")
            
            # Initialize Google Gemini if available
            if self.config.get('google_api_key'):
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.config['google_api_key'])
                    self.providers['google'] = genai
                    self.fallback_chain.append('google')
                    self.logger.info("Google Gemini provider initialized")
                except ImportError:
                    self.logger.warning("Google Generative AI library not available")
            
            # Initialize Local Ollama if available
            try:
                import ollama
                self.providers['ollama'] = ollama.AsyncClient()
                self.fallback_chain.append('ollama')
                self.logger.info("Ollama local provider initialized")
            except ImportError:
                self.logger.warning("Ollama library not available")
                
        except Exception as e:
            self.logger.error(f"Provider setup error: {e}")
    
    async def route_completion(
        self,
        messages: List[Dict[str, str]],
        preferred_provider: Optional[str] = None,
        task_type: str = "general"
    ) -> Dict[str, Any]:
        """Route completion request to best available provider"""
        
        # Determine optimal provider
        provider = self._select_provider(preferred_provider, task_type)
        
        # Try providers in fallback chain
        for attempt_provider in ([provider] if provider else self.fallback_chain):
            try:
                result = await self._call_provider(attempt_provider, messages)
                if result and "content" in result:
                    # Update performance metrics
                    self._update_metrics(attempt_provider, True, result.get('processing_time', 0))
                    return {**result, "provider": attempt_provider}
                    
            except Exception as e:
                self.logger.warning(f"Provider {attempt_provider} failed: {e}")
                self._update_metrics(attempt_provider, False, 0)
                continue
        
        return {"error": "All AI providers failed", "provider": "none"}
    
    def _select_provider(self, preferred: Optional[str], task_type: str) -> Optional[str]:
        """Select optimal provider based on task and performance"""
        
        # Use preferred if specified and available
        if preferred and preferred in self.providers:
            return preferred
            
        # Task-based routing
        if task_type == "reasoning" and "nvidia" in self.providers:
            return "nvidia"  # NVIDIA models excel at reasoning
        elif task_type == "creative" and "anthropic" in self.providers:
            return "anthropic"  # Claude is great for creative tasks
        elif task_type == "coding" and "openai" in self.providers:
            return "openai"  # GPT-4 is strong for coding
        elif task_type == "local" and "ollama" in self.providers:
            return "ollama"  # For privacy-sensitive tasks
            
        # Fallback to best performing provider
        if self.performance_metrics:
            best_provider = min(
                self.performance_metrics.items(),
                key=lambda x: x[1].get('avg_response_time', float('inf'))
            )[0]
            if best_provider in self.providers:
                return best_provider
                
        # Default to first available
        return self.fallback_chain[0] if self.fallback_chain else None
    
    async def _call_provider(self, provider: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call specific AI provider"""
        
        if provider == "nvidia":
            async with self.providers['nvidia'] as nim_client:
                return await nim_client.chat_completion(messages)
                
        elif provider == "openai":
            client = self.providers['openai']
            start_time = time.time()
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return {
                "content": response.choices[0].message.content,
                "model": "gpt-4o-mini",
                "processing_time": time.time() - start_time
            }
            
        elif provider == "anthropic":
            client = self.providers['anthropic']
            start_time = time.time()
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=messages
            )
            return {
                "content": response.content[0].text,
                "model": "claude-3-haiku",
                "processing_time": time.time() - start_time
            }
            
        elif provider == "google":
            genai = self.providers['google']
            start_time = time.time()
            model = genai.GenerativeModel('gemini-pro')
            # Convert messages format
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = await model.generate_content_async(prompt)
            return {
                "content": response.text,
                "model": "gemini-pro",
                "processing_time": time.time() - start_time
            }
            
        elif provider == "ollama":
            client = self.providers['ollama']
            start_time = time.time()
            response = await client.chat(
                model="llama3.2:1b",  # Lightweight model
                messages=messages
            )
            return {
                "content": response['message']['content'],
                "model": "llama3.2:1b",
                "processing_time": time.time() - start_time
            }
        
        raise ValueError(f"Unknown provider: {provider}")
    
    def _update_metrics(self, provider: str, success: bool, response_time: float):
        """Update provider performance metrics"""
        if provider not in self.performance_metrics:
            self.performance_metrics[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0,
                "avg_response_time": 0
            }
        
        metrics = self.performance_metrics[provider]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
            metrics["total_response_time"] += response_time
            metrics["avg_response_time"] = (
                metrics["total_response_time"] / metrics["successful_requests"]
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get multi-LLM router status"""
        return {
            "providers": list(self.providers.keys()),
            "fallback_chain": self.fallback_chain,
            "performance_metrics": self.performance_metrics,
            "total_providers": len(self.providers)
        }
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check all providers"""
        results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                if provider_name == "nvidia":
                    async with provider as nim_client:
                        results[provider_name] = await nim_client.health_check()
                else:
                    # Simple test for other providers
                    test_messages = [{"role": "user", "content": "Test"}]
                    result = await self._call_provider(provider_name, test_messages)
                    results[provider_name] = {
                        "status": "healthy" if "content" in result else "unhealthy",
                        "last_check": time.time()
                    }
            except Exception as e:
                results[provider_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": time.time()
                }
        
        return results