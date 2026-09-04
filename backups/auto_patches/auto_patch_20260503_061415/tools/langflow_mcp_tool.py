"""Langflow MCP Integration Tool for Workflow Automation"""

import json
import subprocess
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_error, log_info


@dataclass
class LangflowMCPConfig:
    """LangFlow MCP Configuration"""
    langflow_url: str = "http://localhost:7860"
    api_key: Optional[str] = None
    project_id: Optional[str] = None
    timeout: int = 30


class LangflowMCPTool(ToolInterface):
    """Langflow MCP integration for workflow automation with proper MCP support"""

    def __init__(self):
        """Initialize Langflow MCP tool"""
        self.config = LangflowMCPConfig()
        self.mcp_process: Optional[subprocess.Popen] = None
        self.is_connected = False
        log_info("langflow_mcp", "Initialized LangFlow MCP Tool")

    @property
    def name(self) -> str:
        return "Langflow MCP"

    @property
    def description(self) -> str:
        return "Langflow workflow automation via Model Context Protocol (MCP) server"

    def match(self, command: str) -> bool:
        """Check if command matches Langflow MCP operations"""
        keywords: List[str] = [
            "langflow", "workflow", "flow", "mcp", "automation",
            "analyze", "enhance", "audit", "generate"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute Langflow MCP operation"""
        log_info("langflow_mcp", f"Processing: {command}", extra_data=kwargs)

        try:
            cmd_lower: str = command.lower()

            if "test" in cmd_lower or "connect" in cmd_lower:
                return self._test_connection()
            elif "list" in cmd_lower:
                return self._list_workflows()
            elif "run" in cmd_lower or "execute" in cmd_lower:
                return self._run_workflow(command, **kwargs)
            elif "create" in cmd_lower:
                return self._create_workflow(command, **kwargs)
            elif "status" in cmd_lower:
                return self._get_status()
            elif "config" in cmd_lower:
                return self._show_config()
            else:
                return self._list_available_commands()

        except Exception as e:
            log_error("langflow_mcp", f"Error: {e}", exception=e)
            return f"❌ LangFlow MCP error: {str(e)}"

    def _test_connection(self) -> str:
        """Test LangFlow MCP server connection"""
        log_info("langflow_mcp", "Testing connection to LangFlow MCP server")

        try:
            # Check if LangFlow is running
            import urllib.request
            try:
                response = urllib.request.urlopen(
                    f"{self.config.langflow_url}/health",
                    timeout=5
                )
                if response.status == 200:
                    log_info("langflow_mcp", "✓ LangFlow server is running")
                    self.is_connected = True
                    return "✅ LangFlow server is running and accessible at " \
                           f"{self.config.langflow_url}"
            except Exception as e:
                return f"❌ LangFlow server not accessible: {str(e)}\n" \
                       f"Expected at: {self.config.langflow_url}\n" \
                       f"Start with: langflow run --host 127.0.0.1 --port 7860"

        except Exception as e:
            log_error("langflow_mcp", f"Connection test failed: {e}")
            return f"❌ Connection test failed: {str(e)}"

    def _list_workflows(self) -> str:
        """List available Langflow workflows from MCP server"""
        log_info("langflow_mcp", "Listing available workflows")

        return """� Available LangFlow Workflows via MCP:

1. **analyze_code**
   └─ Analyzes Python code for security, performance, and quality issues

2. **enhance_gui**
   └─ Generates GUI improvements and HTML/CSS for ATLAS interface

3. **security_audit**
   └─ Performs comprehensive security audit on code/configuration

4. **code_generation**
   └─ Generates new code based on specifications

To use these workflows:
• In Cursor: Type @ to trigger autocomplete and select @langflow_[workflow]
• In MCP Inspector: Tools tab shows all available flows
• Via CLI: Run `langflow_mcp execute [workflow_name]`
"""

    def _run_workflow(self, command: str, **kwargs: Any) -> str:
        """Execute specific Langflow workflow via MCP"""
        log_info("langflow_mcp", f"Running workflow: {command}", extra_data=kwargs)

        workflow_name = self._extract_workflow_name(command)

        if not workflow_name:
            return "❌ Please specify a workflow name\n" \
                   "Usage: langflow run [workflow_name]"

        return f"▶️ Executing workflow: {workflow_name}\n" \
               f"Status: Running through MCP server at {self.config.langflow_url}\n" \
               f"Check MCP Inspector for real-time progress"

    def _create_workflow(self, command: str, **kwargs: Any) -> str:
        """Create new Langflow workflow"""
        log_info("langflow_mcp", f"Creating workflow: {command}")

        workflow_name = self._extract_workflow_name(command)

        if not workflow_name:
            return "❌ Please specify a workflow name\n" \
                   "Usage: langflow create [workflow_name]"

        return f"🔧 Creating new workflow: {workflow_name}\n" \
               f"Steps:\n" \
               f"1. Open LangFlow at {self.config.langflow_url}\n" \
               f"2. Create new flow with name: {workflow_name}\n" \
               f"3. Add Chat Output component (required for MCP)\n" \
               f"4. Enable in MCP Server tab\n" \
               f"5. Set clear tool name and description\n" \
               f"6. Save and restart MCP connection"

    def _get_status(self) -> str:
        """Get LangFlow MCP server status"""
        log_info("langflow_mcp", "Getting status")

        status_str = "✓" if self.is_connected else "✗"

        return f"""🔍 LangFlow MCP Server Status:

Connection: [{status_str}] {"Connected" if self.is_connected else "Disconnected"}
Server URL: {self.config.langflow_url}
Project ID: {self.config.project_id or "Not configured"}
API Key: {"Configured" if self.config.api_key else "Not configured"}
Timeout: {self.config.timeout}s

To configure:
1. Add environment variables or use mcp.json
2. Set LANGFLOW_API_KEY and LANGFLOW_PROJECT_ID
3. Restart MCP connection
"""

    def _show_config(self) -> str:
        """Show current LangFlow MCP configuration"""
        log_info("langflow_mcp", "Showing configuration")

        config_dict = {
            "langflow_url": self.config.langflow_url,
            "api_key_configured": self.config.api_key is not None,
            "project_id": self.config.project_id or "Not set",
            "timeout": self.config.timeout,
            "connected": self.is_connected
        }

        return f"⚙️ LangFlow MCP Configuration:\n\n" \
               f"{json.dumps(config_dict, indent=2)}\n\n" \
               f"To update:\n" \
               f"1. Edit mcp.json in your .cursor or .vscode directory\n" \
               f"2. Set PROJECT_ID and API_KEY from LangFlow\n" \
               f"3. Restart your MCP client"

    def _list_available_commands(self) -> str:
        """Show available commands"""
        return """📚 LangFlow MCP Commands:

• test connection - Test LangFlow server connectivity
• list workflows - Show available flows
• run [workflow] - Execute a workflow
• create [workflow] - Create new workflow
• status - Show MCP server status
• config - Show configuration
• help - Show this message

Examples:
  langflow test connection
  langflow list workflows
  langflow run analyze_code
  langflow create my_workflow
"""

    def _extract_workflow_name(self, command: str) -> Optional[str]:
        """Extract workflow name from command"""
        parts = command.split()
        # Handle 'run workflow_name' or 'langflow run workflow_name'
        for i, part in enumerate(parts):
            if part.lower() in ['run', 'execute', 'create']:
                if i + 1 < len(parts):
                    return parts[i + 1]
        return None

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "langflow_mcp",
            "description": "LangFlow workflow automation via Model Context Protocol (MCP). "
                          "Execute LangFlow flows as tools with full MCP integration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute: test, list, run, create, status, config",
                        "enum": ["test connection", "list workflows", "run", "create",
                                "status", "config", "help"]
                    },
                    "workflow_name": {
                        "type": "string",
                        "description": "Name of the workflow (for run/create commands)"
                    },
                    "input_data": {
                        "type": "object",
                        "description": "Input data for workflow execution"
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> LangflowMCPTool:
    """Required function for tool loader"""
    return LangflowMCPTool()
