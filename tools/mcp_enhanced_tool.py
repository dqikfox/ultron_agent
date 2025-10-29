import json
import requests
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error

class MCPEnhancedTool(ToolInterface):
    """Enhanced MCP server integration for ULTRON Agent"""

    @property
    def name(self) -> str:
        return "MCP Enhanced"

    @property
    def description(self) -> str:
        return "Advanced MCP server operations with browser automation and memory"

    def match(self, command: str) -> bool:
        keywords = ["mcp", "browser", "memory", "context", "web automation"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        log_info("mcp_enhanced", f"Processing: {command}")

        try:
            if "browser" in command.lower():
                return self._browser_automation(command)
            elif "memory" in command.lower():
                return self._memory_operation(command)
            else:
                return self._general_mcp(command)
        except Exception as e:
            log_error("mcp_enhanced", f"Error: {e}")
            return f"❌ MCP error: {str(e)}"

    def _browser_automation(self, command: str) -> str:
        """Handle browser automation via MCP"""
        try:
            mcp_url = "http://localhost:5175/api/mcp/browser"
            payload = {"command": command}
            response = requests.post(mcp_url, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            log_info("mcp_enhanced", f"Browser automation result: {result}")
            return f"🌐 Browser automation: {result.get('message', 'Success')}"
        except Exception as e:
            log_error("mcp_enhanced", f"Browser automation failed: {e}")
            return f"❌ Browser automation error: {str(e)}"

    def _memory_operation(self, command: str) -> str:
        """Handle memory operations via MCP"""
        try:
            mcp_url = "http://localhost:5175/api/mcp/memory"
            payload = {"command": command}
            response = requests.post(mcp_url, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            log_info("mcp_enhanced", f"Memory operation result: {result}")
            return f"🧠 Memory operation: {result.get('message', 'Success')}"
        except Exception as e:
            log_error("mcp_enhanced", f"Memory operation failed: {e}")
            return f"❌ Memory operation error: {str(e)}"

    def _general_mcp(self, command: str) -> str:
        """Handle general MCP operations"""
        try:
            mcp_url = "http://localhost:5175/api/mcp/command"
            payload = {"command": command}
            response = requests.post(mcp_url, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            log_info("mcp_enhanced", f"MCP response: {result}")
            return f"🔧 MCP operation: {result.get('message', 'Success')}"
        except Exception as e:
            log_error("mcp_enhanced", f"MCP request failed: {e}")
            return f"❌ MCP error: {str(e)}"

    @classmethod
    def schema(cls):
        return {
            "name": "mcp_enhanced",
            "description": "Enhanced MCP server operations with browser automation and memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "MCP command to execute (browser, memory, or general operations)"
                    }
                },
                "required": ["command"]
            }
        }
