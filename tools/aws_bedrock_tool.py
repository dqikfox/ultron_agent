import json
import requests
from typing import Dict, Any, Optional
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision

class AWSBedrockTool(ToolInterface):
    """AWS Bedrock integration tool for cloud-based AI inference"""
    
    def __init__(self):
        self.api_endpoint = None
        self.conversation_id = None
        
    @property
    def name(self) -> str:
        return "AWS Bedrock AI"
    
    @property
    def description(self) -> str:
        return "Cloud-based AI inference using AWS Bedrock models with conversation persistence"
    
    def match(self, command: str) -> bool:
        """Check if command should use AWS Bedrock"""
        bedrock_keywords = [
            "bedrock", "aws ai", "cloud ai", "nova", "claude bedrock",
            "aws inference", "cloud model", "bedrock chat"
        ]
        return any(keyword in command.lower() for keyword in bedrock_keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute Bedrock AI inference"""
        log_info("aws_bedrock_tool", f"Processing command: {command}")
        
        try:
            # Load configuration
            config = self._load_config()
            if not config:
                return "❌ AWS Bedrock not configured. Check ultron_config.json"
            
            # Extract message from command
            message = self._extract_message(command)
            if not message:
                return "❌ No message found in command"
            
            # Prepare request
            request_data = {
                "message": message,
                "conversation_id": self.conversation_id or f"ultron_{int(__import__('time').time())}",
                "model": kwargs.get("model", "amazon.nova-pro-v1:0")
            }
            
            # Make API call to Lambda function
            response = self._call_bedrock_api(config["api_endpoint"], request_data)
            
            if response:
                self.conversation_id = response.get("conversation_id")
                ai_response = response.get("response", "No response received")
                
                log_ai_decision(
                    "aws_bedrock_tool", 
                    f"Bedrock response generated",
                    ai_model=request_data["model"],
                    confidence_score=0.95
                )
                
                return f"🤖 **AWS Bedrock ({request_data['model']}):**\n\n{ai_response}"
            else:
                return "❌ Failed to get response from AWS Bedrock"
                
        except Exception as e:
            log_error("aws_bedrock_tool", f"Error: {e}")
            return f"❌ AWS Bedrock error: {str(e)}"
    
    def _load_config(self) -> Optional[Dict]:
        """Load AWS Bedrock configuration"""
        try:
            with open("ultron_config.json", "r") as f:
                config = json.load(f)
            
            aws_config = config.get("aws_bedrock", {})
            if not aws_config.get("enabled", False):
                return None
            
            api_endpoint = aws_config.get("api_endpoint")
            if not api_endpoint:
                log_error("aws_bedrock_tool", "No API endpoint configured")
                return None
            
            return {
                "api_endpoint": api_endpoint,
                "region": aws_config.get("region", "us-east-1"),
                "timeout": aws_config.get("timeout", 30)
            }
            
        except Exception as e:
            log_error("aws_bedrock_tool", f"Config load error: {e}")
            return None
    
    def _extract_message(self, command: str) -> str:
        """Extract the actual message from the command"""
        # Remove bedrock-specific keywords
        bedrock_keywords = ["bedrock", "aws ai", "cloud ai", "nova", "claude bedrock"]
        
        message = command.lower()
        for keyword in bedrock_keywords:
            message = message.replace(keyword, "").strip()
        
        # Remove common command prefixes
        prefixes = ["ask", "tell", "query", "chat", "talk to"]
        for prefix in prefixes:
            if message.startswith(prefix):
                message = message[len(prefix):].strip()
        
        return message if message else command
    
    def _call_bedrock_api(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make API call to AWS Lambda Bedrock handler"""
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ULTRON-Agent/3.0"
            }
            
            response = requests.post(
                f"{endpoint}/chat",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                log_error("aws_bedrock_tool", f"API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            log_error("aws_bedrock_tool", "API request timeout")
            return None
        except Exception as e:
            log_error("aws_bedrock_tool", f"API call error: {e}")
            return None
    
    def get_conversation_history(self) -> str:
        """Get conversation history for current session"""
        if not self.conversation_id:
            return "No active conversation"
        
        try:
            config = self._load_config()
            if not config:
                return "Configuration not available"
            
            # This would call a separate endpoint to get conversation history
            # For now, return placeholder
            return f"Conversation ID: {self.conversation_id}"
            
        except Exception as e:
            log_error("aws_bedrock_tool", f"History error: {e}")
            return f"Error getting history: {str(e)}"
    
    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for OpenAI-compatible function calling"""
        return {
            "name": "aws_bedrock_ai",
            "description": "Use AWS Bedrock for cloud-based AI inference with models like Nova Pro",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send to the AI model"
                    },
                    "model": {
                        "type": "string",
                        "description": "Bedrock model to use (default: amazon.nova-pro-v1:0)",
                        "enum": [
                            "amazon.nova-pro-v1:0",
                            "amazon.nova-lite-v1:0",
                            "anthropic.claude-3-sonnet-20240229-v1:0",
                            "anthropic.claude-3-haiku-20240307-v1:0"
                        ]
                    }
                },
                "required": ["message"]
            }
        }