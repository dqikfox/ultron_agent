from tools.tool_interface import ToolInterface
from tools.aws_bedrock_tool import AWSBedrockTool
from utils.ultron_logger import log_info

class VoiceAWSTool(ToolInterface):
    """Voice-activated AWS operations for ULTRON Agent"""

    def __init__(self):
        self.bedrock_tool = AWSBedrockTool()

    @property
    def name(self) -> str:
        return "Voice AWS"

    @property
    def description(self) -> str:
        return "Voice-activated AWS Bedrock and cloud operations"

    def match(self, command: str) -> bool:
        voice_aws_keywords = [
            "hey ultron aws", "voice bedrock", "speak to cloud",
            "ultron cloud", "voice ai aws"
        ]
        return any(kw in command.lower() for kw in voice_aws_keywords)

    def execute(self, command: str, **kwargs) -> str:
        log_info("voice_aws", f"Voice AWS command: {command}")

        # Extract the actual query from voice command
        query = self._extract_query(command)

        # Use AWS Bedrock for response
        try:
            response = self.bedrock_tool.execute(query)
            # Add voice-friendly formatting
            return f"🎤 Voice AWS Response:\n{response}"
        except Exception as e:
            return f"❌ Voice AWS error: {str(e)}"

    def _extract_query(self, command: str) -> str:
        """Extract query from voice command"""
        prefixes = ["hey ultron aws", "voice bedrock", "speak to cloud", "ultron cloud"]

        query = command.lower()
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        return query if query else command

    @classmethod
    def schema(cls):
        return {
            "name": "voice_aws",
            "description": "Voice-activated AWS operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Voice command for AWS"}
                },
                "required": ["command"]
            }
        }
