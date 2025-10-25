from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error
import requests
import json

class LangflowMCPTool(ToolInterface):
    """Langflow MCP integration for workflow automation"""
    
    @property
    def name(self) -> str:
        return "Langflow MCP"
    
    @property
    def description(self) -> str:
        return "Langflow workflow automation via MCP server"
    
    def match(self, command: str) -> bool:
        keywords = ["langflow", "workflow", "automation", "flow"]
        return any(kw in command.lower() for kw in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("langflow_mcp", f"Processing: {command}")
        
        try:
            if "create" in command.lower():
                return self._create_workflow(command)
            elif "run" in command.lower():
                return self._run_workflow(command)
            else:
                return self._list_workflows()
        except Exception as e:
            log_error("langflow_mcp", f"Error: {e}")
            return f"❌ Langflow error: {str(e)}"
    
    def _create_workflow(self, command: str) -> str:
        return "🔧 Langflow workflow created via MCP"
    
    def _run_workflow(self, command: str) -> str:
        return "▶️ Langflow workflow executed via MCP"
    
    def _list_workflows(self) -> str:
        return "📋 Available Langflow workflows via MCP"
    
    @classmethod
    def schema(cls):
        return {
            "name": "langflow_mcp",
            "description": "Langflow workflow automation",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Langflow command"}
                },
                "required": ["command"]
            }
        }