"""Voice AWS Integration Tool for ULTRON Agent"""

from typing import Any, Dict, List

from utils.ultron_logger import log_info

from tools.aws_bedrock_tool import AWSBedrockTool
from tools.tool_interface import ToolInterface


class VoiceAWSTool(ToolInterface):
    """Voice-activated AWS operations for ULTRON Agent"""

    def __init__(self) -> None:
        self.bedrock_tool: AWSBedrockTool = AWSBedrockTool()

    @property
    def name(self) -> str:
        return "Voice AWS"

    @property
    def description(self) -> str:
        return "Voice-activated AWS Bedrock and cloud operations"

    def match(self, command: str) -> bool:
        """Check if command matches voice AWS operations"""
        voice_aws_keywords: List[str] = [
            "hey ultron aws", "voice bedrock", "speak to cloud",
            "ultron cloud", "voice ai aws"
        ]
        return any(
            kw in command.lower() for kw in voice_aws_keywords
        )

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute voice AWS operation"""
        log_info("voice_aws", f"Voice AWS command: {command}")

        # Extract the actual query from voice command
        query: str = self._extract_query(command)

        # Use AWS Bedrock for response
        try:
            response: str = self.bedrock_tool.execute(query)
            # Add voice-friendly formatting
            return f"🎤 Voice AWS Response:\n{response}"
        except Exception as e:
            return f"❌ Voice AWS error: {str(e)}"

    def _extract_query(self, command: str) -> str:
        """Extract query from voice command"""
        prefixes: List[str] = [
            "hey ultron aws", "voice bedrock", "speak to cloud",
            "ultron cloud"
        ]

        query: str = command.lower()
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        return query if query else command

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "voice_aws",
            "description": "Voice-activated AWS operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Voice command for AWS"
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> VoiceAWSTool:
    """Required function for tool loader"""
    return VoiceAWSTool()

