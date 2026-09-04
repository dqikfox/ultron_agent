"""MiniMax AI Integration Tool for ULTRON Agent"""

import json
import requests
from typing import Dict, Any
from utils.ultron_logger import log_info, log_error
from tools.base import Tool

class MinimaxAITool(Tool):
    name = "minimax_ai"
    description = "MiniMax AI chat and coding assistance"
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("minimax_api_key", "")
        self.base_url = config.get("minimax_base_url", "https://api.minimax.chat/v1")
        self.model = config.get("minimax_model", "abab6.5s-chat")
        self.enabled = config.get("minimax_enabled", False)
    
    def match(self, command: str) -> bool:
        return any(keyword in command.lower() for keyword in [
            "minimax", "abab", "coding help", "ai chat"
        ])
    
    def execute(self, command: str, **kwargs) -> str:
        if not self.enabled or not self.api_key:
            return "MiniMax AI not configured. Check ultron_config.json"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": command}],
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/text/chatcompletion",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    log_info("minimax_ai", f"Response generated: {len(content)} chars")
                    return content
                else:
                    return f"MiniMax API response format error: {result}"
            else:
                log_error("minimax_ai", f"API error: {response.status_code} - {response.text}")
                return f"MiniMax API error: {response.status_code} - Check API key"
                
        except Exception as e:
            log_error("minimax_ai", f"Error: {str(e)}")
            return f"MiniMax error: {str(e)}"
    
    @staticmethod
    def schema():
        return {
            "name": "minimax_ai",
            "description": "MiniMax AI chat and coding assistance",
            "parameters": {
                "command": {"type": "string", "description": "Query for MiniMax AI"}
            }
        }