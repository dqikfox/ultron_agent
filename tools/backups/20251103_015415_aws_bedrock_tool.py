import json
import requests
from typing import Dict, Any, Optional, List, Tuple, Union
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.error_handlers import (
    NetworkError, TimeoutError, ValidationError, FileError, ErrorContext
)

class AWSBedrockTool(ToolInterface):
    """AWS Bedrock integration tool for cloud-based AI inference"""

    def __init__(self) -> None:
        self.api_endpoint: Optional[str] = None
        self.conversation_id: Optional[str] = None

    @property
    def name(self) -> str:
        return "AWS Bedrock AI"

    @property
    def description(self) -> str:
        return "Cloud-based AI inference using AWS Bedrock models with conversation persistence"

    def match(self, command: str) -> bool:
        """Check if command should use AWS Bedrock"""
        bedrock_keywords: List[str] = [
            "bedrock", "aws ai", "cloud ai", "nova", "claude bedrock",
            "aws inference", "cloud model", "bedrock chat"
        ]
        return any(keyword in command.lower() for keyword in bedrock_keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute Bedrock AI inference"""
        log_info("aws_bedrock_tool", f"Processing command: {command}")

        try:
            # Load configuration
            config: Optional[Dict[str, Any]] = self._load_config()
            if not config:
                return "❌ AWS Bedrock not configured. Check ultron_config.json"

            # Extract message from command
            message: Optional[str] = self._extract_message(command)
            if not message:
                return "❌ No message found in command"

            # Prepare request
            request_data: Dict[str, Any] = {
                "message": message,
                "conversation_id": self.conversation_id or f"ultron_{int(__import__('time').time())}",
                "model": kwargs.get("model", "amazon.nova-pro-v1:0")
            }

            # Make API call to Lambda function
            response: Optional[Dict[str, Any]] = self._call_bedrock_api(config["api_endpoint"], request_data)

            if response:
                self.conversation_id = response.get("conversation_id")
                ai_response: str = response.get("response", "No response received")

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

    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load AWS Bedrock configuration

        Returns: Optional[Dict] - Config dict or None on failure
        Raises: FileError on config file issues
        """
        with ErrorContext("aws_bedrock", logger=None) as ctx:
            try:
                # Layer 1: File existence and readability
                try:
                    with open("ultron_config.json", "r") as f:
                        config: Dict[str, Any] = json.load(f)
                except FileNotFoundError:
                    log_error("aws_bedrock_tool", "Config file not found")
                    raise FileError(
                        "ultron_config.json not found",
                        "ultron_config.json",
                        "read"
                    )
                except json.JSONDecodeError as e:
                    log_error("aws_bedrock_tool", f"Invalid JSON: {e}")
                    raise ValidationError(
                        "Invalid JSON in config file",
                        "config",
                        str(e),
                        "valid JSON"
                    )

                # Layer 2: Configuration validation
                aws_config: Dict[str, Any] = config.get("aws_bedrock", {})
                if not aws_config.get("enabled", False):
                    log_info("aws_bedrock_tool", "AWS Bedrock disabled")
                    return None

                # Layer 3: Required field validation
                api_endpoint: Optional[str] = aws_config.get("api_endpoint")
                if not api_endpoint:
                    raise ValidationError(
                        "Missing API endpoint in config",
                        "api_endpoint",
                        "",
                        "valid AWS Bedrock endpoint"
                    )

                log_info("aws_bedrock_tool", "Config loaded successfully")
                return {
                    "api_endpoint": api_endpoint,
                    "region": aws_config.get("region", "us-east-1"),
                    "timeout": aws_config.get("timeout", 30)
                }

            except (FileError, ValidationError) as e:
                log_error("aws_bedrock_tool", f"Config error: {e}")
                ctx.error = e
                return None
            except Exception as e:
                log_error("aws_bedrock_tool", f"Unexpected config error: {e}")
                ctx.error = e
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

    def _call_bedrock_api(self, endpoint: str,
                          data: Dict) -> Optional[Dict]:
        """Make API call to AWS Lambda Bedrock handler

        Args: endpoint (str) - API endpoint URL
              data (Dict) - Request payload
        Returns: Optional[Dict] - Response or None on failure
        Raises: NetworkError, TimeoutError on failures
        """
        with ErrorContext("aws_bedrock", logger=None) as ctx:
            try:
                # Layer 1: Input validation
                if not endpoint or not isinstance(endpoint, str):
                    raise ValidationError(
                        "Invalid endpoint",
                        "endpoint",
                        str(endpoint),
                        "non-empty string"
                    )
                if not data or not isinstance(data, dict):
                    raise ValidationError(
                        "Invalid request data",
                        "data",
                        str(data),
                        "dict"
                    )

                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "ULTRON-Agent/3.0"
                }

                # Layer 2: Make request with timeout handling
                try:
                    response = requests.post(
                        f"{endpoint}/chat",
                        json=data,
                        headers=headers,
                        timeout=30
                    )
                except requests.Timeout:
                    log_error("aws_bedrock_tool",
                             "API request timeout")
                    raise TimeoutError(
                        "Bedrock API timeout",
                        30,
                        "_call_bedrock_api"
                    )
                except requests.ConnectionError as e:
                    log_error("aws_bedrock_tool",
                             f"Connection failed: {e}")
                    raise NetworkError(
                        f"API connection failed: {e}",
                        endpoint,
                        "POST"
                    )

                # Layer 3: Response validation
                if response.status_code == 200:
                    try:
                        result = response.json()
                        log_info("aws_bedrock_tool",
                                "API call successful")
                        return result
                    except json.JSONDecodeError as e:
                        raise ValidationError(
                            "Invalid JSON response",
                            "response",
                            str(e),
                            "valid JSON"
                        )
                else:
                    log_error("aws_bedrock_tool",
                             f"API error: {response.status_code}")
                    raise NetworkError(
                        f"API error: {response.status_code}",
                        endpoint,
                        "POST",
                        response.status_code
                    )

            except (ValidationError, TimeoutError,
                   NetworkError) as e:
                log_error("aws_bedrock_tool",
                         f"API call failed: {e}")
                ctx.error = e
                return None
            except Exception as e:
                log_error("aws_bedrock_tool",
                         f"Unexpected API error: {e}")
                ctx.error = e
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
