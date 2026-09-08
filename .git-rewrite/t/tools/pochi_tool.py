"""
POCHI Integration Module for Ultron Agent
=========================================
Integrates POCHI AI assistant capabilities with Claude models
"""

import json
import yaml
import requests
import logging
from typing import Dict, List, Optional, Any
import asyncio
from pathlib import Path

class POCHIManager:
    """Manager for POCHI AI assistant integration with Claude models"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_pochi_config()
        self.config = self._load_pochi_config()
        self.current_model = None
        self.api_key = None
        self._initialize_pochi()
        
    def _find_pochi_config(self) -> str:
        """Find POCHI configuration file"""
        possible_paths = [
            Path.home() / ".continue" / "config.yaml",
            Path.cwd() / "config.yaml",
            Path.cwd() / "pochi_config.yaml"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def _load_pochi_config(self) -> Dict:
        """Load POCHI configuration from YAML file"""
        if not self.config_path or not Path(self.config_path).exists():
            logging.warning("POCHI config file not found")
            return {}
            
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                logging.info(f"🤖 POCHI config loaded from {self.config_path}")
                return config
        except Exception as e:
            logging.error(f"Failed to load POCHI config: {e}")
            return {}
    
    def _initialize_pochi(self):
        """Initialize POCHI with available models"""
        if not self.config.get('models'):
            logging.warning("No POCHI models configured")
            return
            
        # Get the first available Claude model
        for model in self.config['models']:
            if 'provider' in model and model['provider'] == 'anthropic':
                self.current_model = model
                self.api_key = model.get('apiKey')
                break
            elif 'uses' in model and 'anthropic' in model['uses']:
                # Handle the 'uses' format
                self.current_model = model
                self.api_key = model.get('with', {}).get('ANTHROPIC_API_KEY')
                break
        
        if self.current_model:
            logging.info(f"🎯 POCHI initialized with model: {self.current_model.get('name', 'Claude')}")
        else:
            logging.warning("No compatible POCHI models found")
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available POCHI models"""
        return self.config.get('models', [])
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different POCHI model"""
        for model in self.config.get('models', []):
            if model.get('name') == model_name:
                self.current_model = model
                self.api_key = model.get('apiKey') or model.get('with', {}).get('ANTHROPIC_API_KEY')
                logging.info(f"🔄 Switched to POCHI model: {model_name}")
                return True
        return False
    
    async def chat_with_pochi(self, message: str, context: List[Dict] = None) -> str:
        """Send message to POCHI Claude model"""
        if not self.current_model or not self.api_key:
            return "POCHI not properly configured"
        
        try:
            # Prepare messages for Claude API
            messages = context or []
            messages.append({"role": "user", "content": message})
            
            # Claude API endpoint
            url = "https://api.anthropic.com/v1/messages"
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            # Get model name
            model_name = self.current_model.get('model', 'claude-3-5-sonnet-latest')
            
            payload = {
                "model": model_name,
                "max_tokens": 4096,
                "messages": messages
            }
            
            # Make async request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(url, headers=headers, json=payload, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('content', [{}])[0].get('text', 'No response')
            else:
                logging.error(f"POCHI API error: {response.status_code} - {response.text}")
                return f"POCHI error: {response.status_code}"
                
        except Exception as e:
            logging.error(f"POCHI chat error: {e}")
            return f"POCHI error: {str(e)}"
    
    def get_model_info(self) -> Dict:
        """Get current model information"""
        if not self.current_model:
            return {}
        
        return {
            "name": self.current_model.get('name', 'Unknown'),
            "model": self.current_model.get('model', 'Unknown'),
            "provider": self.current_model.get('provider', 'anthropic'),
            "available": bool(self.api_key)
        }
    
    def is_available(self) -> bool:
        """Check if POCHI is available and configured"""
        return bool(self.current_model and self.api_key)


class POCHITool:
    """Tool wrapper for POCHI integration"""
    
    def __init__(self, pochi_manager: POCHIManager):
        self.pochi = pochi_manager
        self.name = "pochi_chat"
        self.description = "Chat with POCHI AI assistant using Claude models"
        self.parameters = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to send to POCHI"
                },
                "model": {
                    "type": "string", 
                    "description": "Optional: specific model to use",
                    "default": "current"
                }
            },
            "required": ["message"]
        }
    
    def match(self, text: str) -> bool:
        """Check if this tool should handle the request"""
        pochi_keywords = [
            "pochi", "claude", "anthropic", "ask claude", 
            "pochi chat", "claude help", "anthropic ai"
        ]
        return any(keyword in text.lower() for keyword in pochi_keywords)
    
    async def execute(self, message: str, model: str = "current", **kwargs) -> str:
        """Execute POCHI chat request"""
        if not self.pochi.is_available():
            return "❌ POCHI is not available or not configured properly"
        
        # Switch model if specified
        if model != "current":
            if not self.pochi.switch_model(model):
                return f"❌ Model '{model}' not found"
        
        # Get response from POCHI
        response = await self.pochi.chat_with_pochi(message)
        
        # Format response
        model_info = self.pochi.get_model_info()
        return f"🤖 **POCHI ({model_info.get('name', 'Claude')})**: {response}"


def get_pochi_manager(config_path: str = None) -> POCHIManager:
    """Get POCHI manager instance"""
    return POCHIManager(config_path)


def create_pochi_tool(pochi_manager: POCHIManager) -> POCHITool:
    """Create POCHI tool instance"""
    return POCHITool(pochi_manager)


# Test function
async def test_pochi():
    """Test POCHI integration"""
    print("🧪 Testing POCHI integration...")
    
    pochi = get_pochi_manager()
    
    if not pochi.is_available():
        print("❌ POCHI not available")
        return
    
    print(f"✅ POCHI available: {pochi.get_model_info()}")
    
    # Test chat
    response = await pochi.chat_with_pochi("Hello, can you introduce yourself?")
    print(f"🤖 POCHI: {response}")


if __name__ == "__main__":
    asyncio.run(test_pochi())
