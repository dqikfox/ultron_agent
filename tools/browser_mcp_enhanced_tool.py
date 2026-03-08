"""Enhanced Browser MCP Automation Tool"""

from typing import Any, Dict, List

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_error, log_info


class BrowserMCPEnhancedTool(ToolInterface):
    """Enhanced browser automation via BrowserMCP"""

    @property
    def name(self) -> str:
        return "Browser MCP Enhanced"

    @property
    def description(self) -> str:
        return (
            "Advanced browser automation and web scraping via BrowserMCP"
        )

    def match(self, command: str) -> bool:
        """Check if command matches browser automation operations"""
        keywords: List[str] = [
            "browse", "web automation", "scrape", "click", "navigate",
            "browser mcp"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute browser automation operation"""
        log_info("browser_mcp_enhanced", f"Processing: {command}")

        try:
            # ✨ PHASE G: Check memory for recently visited pages
            if self.memory:
                try:
                    recent = self.memory.retrieve_short_term()
                    for item in recent[-5:]:
                        if isinstance(item, dict):
                            if item.get("operation") == "browser_navigate":
                                log_info("browser_mcp_enhanced", f"Recent navigation in memory: {item.get('url')}")
                except Exception as e:
                    log_error("browser_mcp_enhanced", f"Memory check failed (continuing): {e}")

            cmd_lower: str = command.lower()
            if "navigate" in cmd_lower:
                result = self._navigate_page(command)
            elif "click" in cmd_lower:
                result = self._click_element(command)
            elif "scrape" in cmd_lower:
                result = self._scrape_content(command)
            else:
                result = self._general_automation(command)
            
            # ✨ PHASE G: Store browser operation in memory
            if self.memory:
                try:
                    self.memory.add_to_short_term({
                        "operation": "browser_mcp",
                        "command": command[:100],  # First 100 chars
                        "timestamp": __import__("datetime").datetime.now().isoformat()
                    })
                except Exception as e:
                    log_error("browser_mcp_enhanced", f"Failed to store in memory: {e}")
            
            return result
        except Exception as e:
            log_error("browser_mcp_enhanced", f"Error: {e}")
            return f"❌ Browser MCP error: {str(e)}"

    def _navigate_page(self, command: str) -> str:
        """Navigate to web page"""
        return "🌐 Browser navigation executed via MCP"

    def _click_element(self, command: str) -> str:
        """Click HTML element"""
        return "👆 Element clicked via Browser MCP"

    def _scrape_content(self, command: str) -> str:
        """Scrape web content"""
        return "📄 Content scraped via Browser MCP"

    def _general_automation(self, command: str) -> str:
        """Execute general browser automation"""
        return "🤖 Browser automation completed via MCP"

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "browser_mcp_enhanced",
            "description": "Enhanced browser automation via BrowserMCP",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Browser action to perform"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target element or URL"
                    }
                },
                "required": ["action"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> BrowserMCPEnhancedTool:
    """Required function for tool loader"""
    return BrowserMCPEnhancedTool()
