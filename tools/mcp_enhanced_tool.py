"""
Enhanced MCP Tool for ULTRON Agent
Provides advanced MCP server operations with browser automation and memory context
"""
import json
import requests
from typing import Dict, Any, Optional, List, Tuple
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision


class MCPEnhancedTool(ToolInterface):
    """Enhanced MCP server integration for ULTRON Agent"""

    def __init__(self) -> None:
        """Initialize Enhanced MCP Tool"""
        self.mcp_base_url: str = "http://localhost:5175/api/mcp"
        self.request_timeout: int = 15
        self.last_memory_context: Optional[Dict[str, Any]] = None
        log_info("mcp_enhanced", "Enhanced MCP Tool initialized")

    @property
    def name(self) -> str:
        return "MCP Enhanced"

    @property
    def description(self) -> str:
        return "Advanced MCP operations with browser automation"

    def match(self, command: str) -> bool:
        """Check if command matches MCP Enhanced criteria"""
        keywords: List[str] = [
            "mcp", "browser", "memory", "context",
            "web automation", "enhanced", "advanced"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute enhanced MCP commands"""
        log_info("mcp_enhanced", f"Processing: {command}")

        try:
            cmd_lower: str = command.lower()

            if "browser" in cmd_lower:
                return self._browser_automation(command)
            elif "memory" in cmd_lower:
                return self._memory_operation(command)
            else:
                return self._general_mcp(command)
        except Exception as e:
            error_msg: str = f"Execute error: {str(e)}"
            log_error("mcp_enhanced", error_msg)
            return f"❌ MCP error: {str(e)}"

    def _browser_automation(self, command: str) -> str:
        """Handle browser automation via MCP"""
        log_info("mcp_enhanced", f"Browser automation: {command}")

        try:
            endpoint: str = f"{self.mcp_base_url}/browser"
            payload: Dict[str, str] = {"command": command}
            response: requests.Response = requests.post(
                endpoint,
                json=payload,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()

            log_ai_decision(
                "mcp_enhanced",
                "Browser automation executed",
                ai_model="ultron_agent",
                confidence_score=1.0,
                reasoning=f"Command: {command}"
            )

            message: str = result.get('message', 'Success')
            return f"🌐 Browser automation: {message}"

        except requests.exceptions.RequestException as e:
            error_msg: str = f"Browser request failed: {str(e)}"
            log_error("mcp_enhanced", error_msg)
            return f"❌ Browser error: {str(e)}"
        except Exception as e:
            log_error("mcp_enhanced", f"Browser automation failed: {e}")
            return f"❌ Browser error: {str(e)}"

    def _memory_operation(self, command: str) -> str:
        """Handle memory operations via MCP"""
        log_info("mcp_enhanced", f"Memory operation: {command}")

        try:
            endpoint: str = f"{self.mcp_base_url}/memory"
            payload: Dict[str, str] = {"command": command}
            response: requests.Response = requests.post(
                endpoint,
                json=payload,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()

            self.last_memory_context = result.get('context', {})

            log_ai_decision(
                "mcp_enhanced",
                "Memory operation executed",
                ai_model="ultron_agent",
                confidence_score=1.0
            )

            message: str = result.get('message', 'Success')
            return f"🧠 Memory operation: {message}"

        except requests.exceptions.RequestException as e:
            error_msg: str = f"Memory request failed: {str(e)}"
            log_error("mcp_enhanced", error_msg)
            return f"❌ Memory error: {str(e)}"
        except Exception as e:
            log_error("mcp_enhanced", f"Memory operation failed: {e}")
            return f"❌ Memory error: {str(e)}"

    def _general_mcp(self, command: str) -> str:
        """Handle general MCP operations"""
        log_info("mcp_enhanced", f"General MCP operation: {command}")

        try:
            endpoint: str = f"{self.mcp_base_url}/command"
            payload: Dict[str, str] = {"command": command}
            response: requests.Response = requests.post(
                endpoint,
                json=payload,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()

            log_ai_decision(
                "mcp_enhanced",
                "General MCP command executed",
                ai_model="ultron_agent",
                confidence_score=1.0
            )

            message: str = result.get('message', 'Success')
            return f"🔧 MCP operation: {message}"

        except requests.exceptions.RequestException as e:
            error_msg: str = f"MCP request failed: {str(e)}"
            log_error("mcp_enhanced", error_msg)
            return f"❌ MCP error: {str(e)}"
        except Exception as e:
            log_error("mcp_enhanced", f"MCP request failed: {e}")
            return f"❌ MCP error: {str(e)}"

    def get_memory_context(self) -> Optional[Dict[str, Any]]:
        """Retrieve last memory context"""
        return self.last_memory_context

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "mcp_enhanced",
            "description": "Advanced MCP operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> MCPEnhancedTool:
    """Required function for tool loader"""
    return MCPEnhancedTool()
