"""
GitHub Models Integration Tool for ULTRON Agent
Provides access to GitHub's hosted AI models including Mistral
"""

import os
from typing import Any, Dict, List, Optional

from utils.ultron_logger import log_error, log_info

from .tool_interface import ToolInterface

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE: bool = True
except ImportError:
    MISTRAL_AVAILABLE = False
    log_error(
        "github_models",
        "mistralai package not available. "
        "Install: pip install mistralai>=1.0.0"
    )


class GitHubModelsTool(ToolInterface):
    """Tool for accessing GitHub Models API"""

    @property
    def name(self) -> str:
        return "GitHub Models Tool"

    @property
    def description(self) -> str:
        return "Access GitHub's hosted AI models including Mistral"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        default_token: str = (
            "github_pat_11A2OOLTI0dp9bJ2EvWmyJ_vsONjQsbtLqd9t4q"
            "VRRk7s7dIFbYGLr5dH6RxIfMhzkSDNL6OXZhGwH4Jyy"
        )
        self.github_token: str = os.getenv("GITHUB_TOKEN", default_token)

        if MISTRAL_AVAILABLE:
            self.client: Optional[Any] = Mistral(
                api_key=self.github_token,
                server_url="https://models.github.ai/inference"
            )
            log_info("github_models", "GitHub Models client initialized")
        else:
            self.client = None

    def match(self, command: str) -> bool:
        """Check if command matches GitHub Models operations"""
        keywords: List[str] = [
            "github model", "mistral", "github ai", "github inference"
        ]
        return any(keyword in command.lower() for keyword in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute GitHub Models operations"""
        if not MISTRAL_AVAILABLE:
            msg: str = (
                "GitHub Models not available. "
                "Install: pip install mistralai>=1.0.0"
            )
            return msg

        if not self.client:
            return "GitHub Models client not initialized"

        try:
            # Extract query from command
            query: str = command.lower()
            if "ask" in query or "question" in query:
                # Extract the actual question
                parts: List[str] = command.split("ask", 1)
                if len(parts) > 1:
                    question: str = parts[1].strip()
                else:
                    question = "Hello, how can you help me?"
            else:
                question = command

            query_preview: str = question[:50]
            log_info(
                "github_models",
                f"Sending query to Mistral: {query_preview}..."
            )

            response: Any = self.client.chat.complete(
                model="mistral-ai/Mistral-Nemo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are ULTRON AI assistant integrated "
                            "with GitHub Models. Provide helpful responses."
                        )
                    },
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0
            )

            result: str = response.choices[0].message.content
            log_info(
                "github_models",
                f"Received response from Mistral: {len(result)} characters"
            )

            return f"GitHub Models (Mistral):\n{result}"

        except Exception as e:
            log_error("github_models", f"GitHub Models query failed: {e}")
            return f"GitHub Models error: {str(e)}"

    def get_available_models(self) -> List[str]:
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
            response: Any = self.client.chat.complete(
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

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "github_models_tool",
            "description": (
                "Access GitHub's hosted AI models including Mistral"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Command or question for GitHub Models"
                        )
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> GitHubModelsTool:
    """Required function for tool loader"""
    return GitHubModelsTool()
