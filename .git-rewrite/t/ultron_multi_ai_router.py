"""
ULTRON Multi-AI Router
Combines Together.xyz, NVIDIA NIM, and other AI providers into a unified interface
Enhanced auto-improvement system with real AI integration
"""

import requests
import json
import logging
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    id: str
    name: str
    provider: str
    description: str
    max_tokens: int
    capabilities: List[str]
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    free_tier: bool = False

class UltronMultiAIRouter:
    """Multi-provider AI routing system for ULTRON Agent"""

    def __init__(self):
        """Initialize multi-AI router with all providers"""

        # API Keys (in production, use environment variables)
        self.together_api_key = "4e6755926525a8f9903ba7dc5bc259708b41fb57d849415e22495754faa64ff9"
        self.nvidia_api_key = "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"

        # Provider configurations
        self.providers = {
            "together": {
                "url": "https://api.together.xyz/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {self.together_api_key}",
                    "Content-Type": "application/json"
                }
            },
            "nvidia": {
                "url": "https://integrate.api.nvidia.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {self.nvidia_api_key}",
                    "Content-Type": "application/json"
                }
            }
        }

        # Available models across all providers
        self.models = {
            # Together.xyz Free Tier Models
            "gpt-oss-20b": ModelConfig(
                id="openai/gpt-oss-20b",
                name="GPT-OSS 20B",
                provider="together",
                description="OpenAI GPT-OSS 20B - Great for general tasks",
                max_tokens=131072,
                capabilities=["chat", "analysis", "creative"],
                cost_per_1k_input=0.05,
                cost_per_1k_output=0.20,
                free_tier=True
            ),
            "mistral-7b": ModelConfig(
                id="mistralai/Mistral-7B-Instruct-v0.2",
                name="Mistral 7B Instruct",
                provider="together",
                description="Mistral's instruction-tuned model",
                max_tokens=32768,
                capabilities=["chat", "coding", "reasoning"],
                cost_per_1k_input=0.20,
                cost_per_1k_output=0.20,
                free_tier=True
            ),
            "gemma-3n": ModelConfig(
                id="google/gemma-3n-E4B-it",
                name="Gemma 3N E4B",
                provider="together",
                description="Google's Gemma model - lightweight and fast",
                max_tokens=32768,
                capabilities=["chat", "coding"],
                cost_per_1k_input=0.02,
                cost_per_1k_output=0.04,
                free_tier=True
            ),

            # NVIDIA NIM Models
            "llama-maverick": ModelConfig(
                id="meta/llama-4-maverick-17b-128e-instruct",
                name="Llama 4 Maverick",
                provider="nvidia",
                description="Meta's advanced instruction-tuned model",
                max_tokens=128000,
                capabilities=["chat", "reasoning", "long-context", "auto-improvement"],
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                free_tier=False
            ),
            "qwen-coder": ModelConfig(
                id="qwen2.5-coder:1.5b",
                name="Qwen2.5-Coder",
                provider="nvidia",
                description="Specialized coding model",
                max_tokens=2048,
                capabilities=["coding", "debugging", "refactoring"],
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                free_tier=False
            )
        }

        self.current_model = "gpt-oss-20b"  # Default to working free model
        self.request_history = []
        self.auto_improvement_active = False

    def list_models(self, filter_by: str = None) -> List[Dict[str, Any]]:
        """List available models, optionally filtered by capability"""
        models = []
        for key, model in self.models.items():
            if filter_by and filter_by not in model.capabilities:
                continue
            models.append({
                "key": key,
                "name": model.name,
                "provider": model.provider,
                "description": model.description,
                "capabilities": model.capabilities,
                "free_tier": model.free_tier,
                "max_tokens": model.max_tokens
            })
        return models

    def set_model(self, model_key: str) -> bool:
        """Set the current model"""
        if model_key in self.models:
            self.current_model = model_key
            logger.info(f"🔄 Switched to model: {self.models[model_key].name}")
            return True
        logger.error(f"❌ Model not found: {model_key}")
        return False

    def get_model_for_task(self, task_type: str) -> str:
        """Auto-select best model for specific task types"""
        task_model_map = {
            "coding": "qwen-coder",
            "auto-improvement": "llama-maverick",
            "analysis": "gpt-oss-20b",
            "chat": "mistral-7b",
            "creative": "gpt-oss-20b"
        }
        return task_model_map.get(task_type, self.current_model)

    async def chat_completion(self, messages: List[Dict[str, str]],
                            model: str = None, temperature: float = 0.7,
                            max_tokens: int = 1500) -> Dict[str, Any]:
        """Send chat completion request to appropriate provider"""

        model_key = model or self.current_model
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not available")

        model_config = self.models[model_key]
        provider_config = self.providers[model_config.provider]

        # Prepare request payload
        payload = {
            "model": model_config.id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": min(max_tokens, model_config.max_tokens)
        }

        try:
            logger.info(f"🚀 Sending request to {model_config.name} ({model_config.provider})")

            response = requests.post(
                provider_config["url"],
                headers=provider_config["headers"],
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # Log successful request
                self.request_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "model": model_key,
                    "provider": model_config.provider,
                    "status": "success",
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                })

                logger.info(f"✅ Response received from {model_config.name}")
                return result
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                return {"error": error_msg, "status_code": response.status_code}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg}

    async def auto_improve_system(self, system_context: str,
                                improvement_focus: str = "performance") -> Dict[str, Any]:
        """Use Llama 4 Maverick for auto-improvement suggestions"""

        logger.info("🔧 Starting auto-improvement analysis...")

        improvement_prompt = f"""
        You are ULTRON's Auto-Improvement AI. Analyze the following system context and provide specific, actionable improvements.

        System Context:
        {system_context}

        Focus Area: {improvement_focus}

        Please provide:
        1. 3-5 specific improvement recommendations
        2. Risk assessment for each (Low/Medium/High)
        3. Implementation priority (1-5, where 1 is highest)
        4. Expected impact on system performance
        5. Code changes needed (if applicable)

        Format your response as JSON for easy parsing.
        """

        messages = [
            {"role": "system", "content": "You are an expert system architect and automation specialist focused on continuous improvement."},
            {"role": "user", "content": improvement_prompt}
        ]

        # Use Llama 4 Maverick for auto-improvement
        result = await self.chat_completion(
            messages=messages,
            model="llama-maverick",
            temperature=0.3,  # Lower temperature for more focused analysis
            max_tokens=2000
        )

    async def get_improvement_suggestions(self, prompt: str) -> Dict[str, Any]:
        """Get improvement suggestions (alias for auto_improve_system for backward compatibility)"""
        return await self.auto_improve_system(prompt, "general")

        if "error" not in result:
            logger.info("✅ Auto-improvement analysis complete")
            return {
                "status": "success",
                "recommendations": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "model_used": "llama-maverick",
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error("❌ Auto-improvement analysis failed")
            return {"status": "error", "error": result.get("error")}

    def get_system_status(self) -> Dict[str, Any]:
        """Get router system status and statistics"""
        total_requests = len(self.request_history)
        successful_requests = len([r for r in self.request_history if r["status"] == "success"])

        provider_usage = {}
        for record in self.request_history:
            provider = record["provider"]
            provider_usage[provider] = provider_usage.get(provider, 0) + 1

        return {
            "current_model": self.models[self.current_model].name,
            "total_requests": total_requests,
            "success_rate": (successful_requests / max(total_requests, 1)) * 100,
            "provider_usage": provider_usage,
            "available_models": len(self.models),
            "auto_improvement_active": self.auto_improvement_active,
            "last_request": self.request_history[-1]["timestamp"] if self.request_history else "Never"
        }

# Usage example and testing
async def test_router():
    """Test the multi-AI router"""
    router = UltronMultiAIRouter()

    print("🤖 ULTRON Multi-AI Router Test")
    print("=" * 50)

    # List available models
    print("\n📋 Available Models:")
    for model in router.list_models():
        print(f"  • {model['name']} ({model['provider']}) - {model['description']}")

    # Test basic chat
    test_messages = [
        {"role": "user", "content": "Hello! Can you help me improve my Python code?"}
    ]

    print(f"\n💬 Testing chat with {router.models[router.current_model].name}...")
    result = await router.chat_completion(test_messages)

    if "error" not in result:
        response = result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        print(f"✅ Response: {response[:200]}...")
    else:
        print(f"❌ Error: {result['error']}")

    # Test auto-improvement
    print("\n🔧 Testing auto-improvement system...")
    improvement_result = await router.auto_improve_system(
        "ULTRON Agent system with voice commands, GUI, and automation features",
        "performance"
    )

    if improvement_result["status"] == "success":
        print("✅ Auto-improvement analysis complete!")
        print(f"📊 Recommendations: {improvement_result['recommendations'][:300]}...")
    else:
        print(f"❌ Auto-improvement failed: {improvement_result.get('error')}")

    # System status
    print("\n📊 System Status:")
    status = router.get_system_status()
    for key, value in status.items():
        print(f"  • {key}: {value}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_router())
