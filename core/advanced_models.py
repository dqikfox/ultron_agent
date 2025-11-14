#!/usr/bin/env python3
"""Advanced AI Models Manager for ULTRON Agent"""

import requests
import json
from typing import Dict, List, Optional
from utils.ultron_logger import log_info, log_error

class AdvancedModelsManager:
    """Manages advanced AI models and routing"""
    
    def __init__(self):
        self.models = {
            "reasoning": ["deepseek-r1:14b", "qwen3-coder:480b-cloud"],
            "vision": ["llava:7b", "llava:13b"],
            "coding": ["qwen3-coder:480b-cloud", "codestral"],
            "chat": ["llama3.1", "mistral-small"],
            "cloud": ["amazon.nova-pro-v1:0", "claude-3-5-sonnet"]
        }
        self.ollama_base = "http://localhost:11434"
    
    async def route_to_best_model(self, task_type: str, prompt: str) -> str:
        """Route request to best model for task type"""
        best_models = self.models.get(task_type, ["llava:7b"])
        
        for model in best_models:
            if await self._is_model_available(model):
                log_info("advanced_models", f"Routing to {model} for {task_type}")
                return await self._generate_response(model, prompt)
        
        return "❌ No suitable model available"
    
    async def _is_model_available(self, model: str) -> bool:
        """Check if model is available"""
        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"] == model for m in models)
        except:
            pass
        return False
    
    async def _generate_response(self, model: str, prompt: str) -> str:
        """Generate response using specified model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_base}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response")
            else:
                return f"❌ Model error: {response.status_code}"
                
        except Exception as e:
            log_error("advanced_models", f"Generation failed: {e}")
            return f"❌ Generation failed: {str(e)}"
    
    def get_model_capabilities(self) -> Dict[str, List[str]]:
        """Get model capabilities mapping"""
        return {
            "deepseek-r1:14b": ["reasoning", "analysis", "complex_problems"],
            "qwen3-coder:480b-cloud": ["coding", "debugging", "refactoring"],
            "llava:7b": ["vision", "image_analysis", "multimodal"],
            "amazon.nova-pro-v1:0": ["cloud_ai", "advanced_reasoning", "enterprise"]
        }

# Global models manager
models_manager = AdvancedModelsManager()