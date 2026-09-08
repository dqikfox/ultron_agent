"""
NVIDIA NIM AI Router for ULTRON Agent 2
Provides cloud-based AI model routing with multiple model support
Integrates with existing voice and automation systems
"""

import requests
import json
import logging
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class UltronNvidiaRouter:
    """NVIDIA NIM API integration for ULTRON Agent"""
    
    def __init__(self, api_key: str = None, config: Dict[str, Any] = None):
        """Initialize NVIDIA NIM router"""
        self.api_key = api_key or "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"
        self.chat_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        
        # Supported NIM Models with enhanced capabilities
        self.models = {
            "gpt-oss": {
                "id": "openai/gpt-oss-120b",
                "name": "GPT-OSS 120B",
                "description": "Open-source GPT model for general tasks",
                "max_tokens": 8192,
                "capabilities": ["chat", "coding", "analysis"]
            },
            "llama": {
                "id": "meta/llama-4-maverick-17b-128e-instruct", 
                "name": "Llama 4 Maverick",
                "description": "Meta's advanced instruction-tuned model",
                "max_tokens": 128000,
                "capabilities": ["chat", "reasoning", "long-context"]
            },
            "qwen-coder": {
                "id": "qwen2.5-coder:1.5b",
                "name": "Qwen2.5-Coder 1.5B (Memory Optimized)",
                "description": "Lightweight coding model for ULTRON development (~1GB RAM)",
                "max_tokens": 2048,  # Reduced for memory efficiency
                "capabilities": ["coding", "debugging", "architecture"]
            }
        }
        
        self.current_model = "gpt-oss"  # Default model
        self.request_history = []
        
        # Integration callbacks
        self.voice_callback = None
        self.memory_callback = None
        
        logger.info(f"NVIDIA NIM Router initialized with {len(self.models)} models")
    
    def set_callbacks(self, voice_callback=None, memory_callback=None):
        """Set integration callbacks for voice and memory"""
        self.voice_callback = voice_callback
        self.memory_callback = memory_callback
        logger.info("Integration callbacks configured")
    
    def route_model(self, model_key: str) -> str:
        """Route to specific model"""
        model_key = model_key.lower().strip()
        
        if model_key in self.models:
            old_model = self.current_model
            self.current_model = model_key
            
            model_info = self.models[model_key]
            result = f"🤖 Model routed from {self.models[old_model]['name']} to {model_info['name']}"
            
            logger.info(f"Model switched: {old_model} -> {model_key}")
            return result
        
        available = ", ".join(self.models.keys())
        return f"❌ Unknown model: {model_key}. Available: {available}"
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        return self.models[self.current_model]
    
    def list_models(self) -> str:
        """List all available models"""
        model_list = []
        for key, info in self.models.items():
            status = "🟢 ACTIVE" if key == self.current_model else "⚪ Available"
            model_list.append(f"  {status} {key}: {info['name']} - {info['description']}")
        
        return f"🤖 NVIDIA NIM Models:\n" + "\n".join(model_list)
    
    async def ask_nvidia_async(self, prompt: str, **kwargs) -> str:
        """Async version of NVIDIA API call"""
        return await asyncio.to_thread(self.ask_nvidia, prompt, **kwargs)
    
    def ask_nvidia(self, prompt: str, max_tokens: int = None, temperature: float = 0.7, **kwargs) -> str:
        """Send prompt to current NVIDIA model"""
        
        model_info = self.models[self.current_model]
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ULTRON-Agent-2.0"
        }
        
        # Prepare payload
        payload = {
            "model": model_info["id"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or min(512, model_info["max_tokens"]),
            "temperature": temperature,
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "stream": kwargs.get("stream", False)
        }
        
        try:
            logger.info(f"Sending request to {model_info['name']}: {prompt[:100]}...")
            
            response = requests.post(
                self.chat_url, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "[No output]")
            
            # Log request for debugging
            self.request_history.append({
                "timestamp": datetime.now().isoformat(),
                "model": self.current_model,
                "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "response": content[:200] + "..." if len(content) > 200 else content,
                "success": True
            })
            
            logger.info(f"NVIDIA response received: {len(content)} characters")
            return content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"[NVIDIA REQUEST ERROR] {str(e)}"
            logger.error(error_msg)
            
            # Log failed request
            self.request_history.append({
                "timestamp": datetime.now().isoformat(),
                "model": self.current_model,
                "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "error": str(e),
                "success": False
            })
            
            return error_msg
            
        except Exception as e:
            error_msg = f"[NVIDIA ERROR] {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def ask_coding_assistant(self, code_prompt: str) -> str:
        """Specialized method for coding queries using Qwen2.5-Coder"""
        # Temporarily switch to coding model if available
        original_model = self.current_model
        
        if "qwen-coder" in self.models:
            self.current_model = "qwen-coder"
            
        # Enhance prompt for coding context
        enhanced_prompt = f"""
        As a coding assistant for ULTRON Agent 2 project:
        
        Project Context:
        - Python 3.10+ with FastAPI and asyncio
        - Voice interaction with pyttsx3
        - PyAutoGUI automation with 25+ features
        - Accessibility focus for disabled users
        - Integration with Ollama and NVIDIA NIM
        
        Coding Query: {code_prompt}
        
        Please provide clear, documented code with error handling.
        """
        
        try:
            response = self.ask_nvidia(enhanced_prompt, max_tokens=2048, temperature=0.3)
            return response
        finally:
            # Restore original model
            self.current_model = original_model
    
    def get_status(self) -> Dict[str, Any]:
        """Get router status information"""
        return {
            "current_model": self.current_model,
            "model_info": self.models[self.current_model],
            "total_requests": len(self.request_history),
            "successful_requests": sum(1 for req in self.request_history if req.get("success", False)),
            "available_models": list(self.models.keys()),
            "last_request": self.request_history[-1] if self.request_history else None
        }


# Voice Command Integration
class UltronNvidiaVoiceIntegration:
    """Voice command integration for NVIDIA NIM router"""
    
    def __init__(self, nvidia_router: UltronNvidiaRouter, voice_manager=None, memory_manager=None):
        self.router = nvidia_router
        self.voice_manager = voice_manager  
        self.memory_manager = memory_manager
        
        # Set up callbacks
        self.router.set_callbacks(
            voice_callback=self.speak_response,
            memory_callback=self.log_memory
        )
        
        logger.info("NVIDIA voice integration initialized")
    
    def speak_response(self, text: str):
        """Speak response using voice manager"""
        if self.voice_manager and hasattr(self.voice_manager, 'speak'):
            self.voice_manager.speak(text)
        else:
            print(f"🔊 ULTRON: {text}")
    
    def log_memory(self, content: str):
        """Log to memory manager"""
        if self.memory_manager and hasattr(self.memory_manager, 'add_memory'):
            self.memory_manager.add_memory(content)
        else:
            logger.info(f"Memory: {content}")
    
    def execute_voice_command(self, command: str) -> str:
        """Execute voice command through NVIDIA router"""
        command = command.strip().lower()
        
        try:
            # Model routing commands
            if command.startswith("route model to") or command.startswith("switch model to"):
                model_key = command.split()[-1].strip()
                result = self.router.route_model(model_key)
                self.speak_response(result)
                return result
            
            elif command in ["list models", "show models", "available models"]:
                result = self.router.list_models()
                self.speak_response("Models listed in chat")
                return result
            
            elif command in ["model status", "current model", "what model"]:
                info = self.router.get_current_model_info()
                result = f"🤖 Current model: {info['name']} - {info['description']}"
                self.speak_response(result)
                return result
            
            elif command.startswith("code help") or command.startswith("coding"):
                code_query = command.replace("code help", "").replace("coding", "").strip()
                if not code_query:
                    code_query = "Help me with ULTRON Agent development"
                
                result = self.router.ask_coding_assistant(code_query)
                self.speak_response("Coding assistance provided")
                self.log_memory(f"Coding help: {result[:100]}...")
                return result
            
            # Default: send to current NVIDIA model
            else:
                result = self.router.ask_nvidia(command)
                self.speak_response("Response received")
                self.log_memory(f"NVIDIA Reply: {result[:100]}...")
                return result
                
        except Exception as e:
            error_msg = f"Voice command error: {str(e)}"
            logger.error(error_msg)
            self.speak_response("Sorry, there was an error processing your request")
            return error_msg


# ULTRON Integration Function
def create_nvidia_integration(voice_manager=None, memory_manager=None, api_key: str = None) -> UltronNvidiaVoiceIntegration:
    """Create NVIDIA NIM integration for ULTRON Agent"""
    
    # Initialize router
    router = UltronNvidiaRouter(api_key=api_key)
    
    # Create voice integration
    integration = UltronNvidiaVoiceIntegration(router, voice_manager, memory_manager)
    
    logger.info("NVIDIA NIM integration created for ULTRON Agent")
    return integration


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔴 ULTRON NVIDIA NIM Router Test 🔴")
    print("=" * 50)
    
    # Create router
    router = UltronNvidiaRouter()
    
    # Test model routing
    print("\n1. Testing Model Routing:")
    print(router.route_model("llama"))
    print(router.route_model("qwen-coder"))
    
    # Test model listing
    print("\n2. Available Models:")
    print(router.list_models())
    
    # Test basic query
    print("\n3. Test Query:")
    response = router.ask_nvidia("Hello, can you help with Python automation?")
    print(f"Response: {response[:200]}...")
    
    # Test coding assistant
    print("\n4. Test Coding Assistant:")
    code_response = router.ask_coding_assistant("How do I create a thread-safe voice recognition system?")
    print(f"Coding Response: {code_response[:200]}...")
    
    # Show status
    print("\n5. Router Status:")
    status = router.get_status()
    print(f"Current Model: {status['current_model']}")
    print(f"Total Requests: {status['total_requests']}")
    
    print("\n✅ NVIDIA NIM Router ready for ULTRON integration!")
