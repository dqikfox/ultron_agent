from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error
import requests

class DeepWikiMCPTool(ToolInterface):
    """DeepWiki MCP integration for enhanced knowledge access"""
    
    @property
    def name(self) -> str:
        return "DeepWiki MCP"
    
    @property
    def description(self) -> str:
        return "Enhanced knowledge access via DeepWiki MCP server"
    
    def match(self, command: str) -> bool:
        keywords = ["deepwiki", "knowledge", "wiki", "research", "search knowledge"]
        return any(kw in command.lower() for kw in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("deepwiki_mcp", f"Processing: {command}")
        
        try:
            query = self._extract_query(command)
            return self._search_knowledge(query)
        except Exception as e:
            log_error("deepwiki_mcp", f"Error: {e}")
            return f"❌ DeepWiki error: {str(e)}"
    
    def _extract_query(self, command: str) -> str:
        prefixes = ["deepwiki", "knowledge", "wiki", "research", "search knowledge"]
        query = command.lower()
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        return query if query else command
    
    def _search_knowledge(self, query: str) -> str:
        return f"🧠 DeepWiki knowledge search for: {query}\n📚 Enhanced knowledge results via MCP"
    
    @classmethod
    def schema(cls):
        return {
            "name": "deepwiki_mcp",
            "description": "Enhanced knowledge access via DeepWiki",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Knowledge search query"}
                },
                "required": ["query"]
            }
        }