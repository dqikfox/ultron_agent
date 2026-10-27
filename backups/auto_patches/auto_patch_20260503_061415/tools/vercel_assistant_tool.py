"""Vercel AI Assistant Integration Tool"""

import requests
from utils.ultron_logger import log_info, log_error, log_ai_decision
from tools.base import Tool


class VercelAssistantTool(Tool):
    name = "vercel_assistant"
    description = "Connect to deployed Vercel AI assistant"
    
    def __init__(self):
        self.base_url = "https://ultron-agent-ai-assistant-dkgcuzmbr-dqikfoxs-projects.vercel.app"
    
    @staticmethod
    def schema():
        return {
            "name": VercelAssistantTool.name,
            "description": VercelAssistantTool.description,
            "parameters": {
                "query": {"type": "string", "description": "Query for the AI assistant"}
            }
        }
    
    def match(self, command: str) -> bool:
        keywords = ["vercel", "web assistant", "deployed ai", "cloud assistant"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, query: str = "", **kwargs) -> str:
        """Send query to Vercel AI assistant"""
        if not query:
            query = kwargs.get("command", "")
        
        try:
            log_ai_decision("vercel_assistant", f"Querying: {query}", 
                          ai_model="vercel_ai", confidence_score=0.8)
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"message": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log_info("vercel_assistant", "Query successful")
                return f"🌐 Vercel AI: {result.get('response', 'No response')}"
            else:
                log_error("vercel_assistant", f"HTTP {response.status_code}")
                return f"❌ Error: HTTP {response.status_code}"
                
        except Exception as e:
            log_error("vercel_assistant", f"Request failed: {e}")
            return f"❌ Connection error: {str(e)}"