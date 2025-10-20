"""
GitHub Models Integration Tool for ULTRON Agent
Provides access to GitHub's hosted AI models including Mistral
"""

import os
from utils.ultron_logger import log_info, log_error
from .tool_interface import ToolInterface

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    log_error("github_models", "mistralai package not available. Install with: pip install mistralai>=1.0.0")


class GitHubModelsTool(ToolInterface):
    """Tool for accessing GitHub Models API"""
    
    @property
    def name(self) -> str:
        return "GitHub Models Tool"
    @property
    def description(self) -> str:
        return "Access GitHub's hosted AI models including Mistral"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.github_token = os.getenv("GITHUB_TOKEN", "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")
        
        if MISTRAL_AVAILABLE:
            self.client = Mistral(
                api_key=self.github_token,
                server_url="https://models.github.ai/inference"
            )
            log_info("github_models", "GitHub Models client initialized")
        else:
            self.client = None
    
    def match(self, command: str) -> bool:
        """Check if command matches GitHub Models operations"""
        return any(keyword in command.lower() for keyword in [
            "github model", "mistral", "github ai", "github inference"
        ])
    
    def execute(self, command: str) -> str:
        """Execute GitHub Models operations"""
        if not MISTRAL_AVAILABLE:
            return "GitHub Models not available. Install: pip install mistralai>=1.0.0"
        
        if not self.client:
            return "GitHub Models client not initialized"
        
        try:
            # Extract query from command
            query = command.lower()
            if "ask" in query or "question" in query:
                # Extract the actual question
                parts = command.split("ask", 1)
                if len(parts) > 1:
                    question = parts[1].strip()
                else:
                    question = "Hello, how can you help me?"
            else:
                question = command
            
            log_info("github_models", f"Sending query to Mistral: {question[:50]}...")
            
            response = self.client.chat.complete(
                model="mistral-ai/Mistral-Nemo",
                messages=[
                    {"role": "system", "content": "You are ULTRON AI assistant integrated with GitHub Models. Provide helpful, accurate responses."},
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0
            )
            
            result = response.choices[0].message.content
            log_info("github_models", f"Received response from Mistral: {len(result)} characters")
            
            return f"GitHub Models (Mistral):\n{result}"
            
        except Exception as e:
            log_error("github_models", f"GitHub Models query failed: {e}")
            return f"GitHub Models error: {str(e)}"
    
    def get_available_models(self) -> list:
        """Get list of available GitHub Models"""
        return [
            "mistral-ai/Mistral-Nemo",
            "mistral-ai/Mistral-7B-Instruct-v0.3",
            "microsoft/Phi-3-medium-4k-instruct",
            "microsoft/Phi-3-mini-4k-instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-405B-Instruct"
        ]
    
    def test_connection(self) -> bool:
        """Test GitHub Models connection"""
        if not MISTRAL_AVAILABLE or not self.client:
            return False
        
        try:
            response = self.client.chat.complete(
                model="mistral-ai/Mistral-Nemo",
                messages=[
                    {"role": "system", "content": "Test"},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            log_error("github_models", f"Connection test failed: {e}")
            return False
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command or question for GitHub Models"
                    }
                },
                "required": ["command"]
            }
        }