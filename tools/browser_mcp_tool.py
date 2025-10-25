"""
ULTRON Agent - Browser MCP Integration Tool

Integrates Browser MCP server for web automation and browsing capabilities.
"""

import json
import subprocess
import asyncio
from typing import Dict, Any, Optional
from utils.ultron_logger import log_info, log_error


class BrowserMCPTool:
    """Browser automation tool using MCP server"""
    
    name = "browser_mcp"
    description = "Web browser automation and interaction using MCP"
    
    def __init__(self):
        self.mcp_process = None
        self.server_running = False
    
    def match(self, command: str) -> bool:
        """Check if command matches browser automation patterns"""
        browser_keywords = [
            "browse", "navigate", "click", "fill", "submit", 
            "screenshot", "scrape", "web", "page", "url"
        ]
        return any(keyword in command.lower() for keyword in browser_keywords)
    
    async def start_mcp_server(self) -> bool:
        """Start Browser MCP server if not running"""
        if self.server_running:
            return True
            
        try:
            log_info("browser_mcp", "Starting Browser MCP server")
            
            # Start MCP server process
            self.mcp_process = await asyncio.create_subprocess_exec(
                "npx", "-y", "@anthropic-ai/mcp-server-browser",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(2)
            
            if self.mcp_process.returncode is None:
                self.server_running = True
                log_info("browser_mcp", "Browser MCP server started successfully")
                return True
            else:
                log_error("browser_mcp", "Browser MCP server failed to start")
                return False
                
        except Exception as e:
            log_error("browser_mcp", f"Error starting MCP server: {str(e)}")
            return False
    
    async def execute(self, command: str, **kwargs) -> str:
        """Execute browser automation command"""
        try:
            log_info("browser_mcp", f"Executing browser command: {command}")
            
            # Ensure MCP server is running
            if not await self.start_mcp_server():
                return "Error: Could not start Browser MCP server"
            
            # Parse command for browser actions
            if "navigate" in command.lower() or "go to" in command.lower():
                return await self._navigate_to_url(command)
            elif "click" in command.lower():
                return await self._click_element(command)
            elif "fill" in command.lower() or "type" in command.lower():
                return await self._fill_form(command)
            elif "screenshot" in command.lower():
                return await self._take_screenshot()
            elif "scrape" in command.lower():
                return await self._scrape_page(command)
            else:
                return await self._general_browser_action(command)
                
        except Exception as e:
            log_error("browser_mcp", f"Browser command failed: {str(e)}")
            return f"Error executing browser command: {str(e)}"
    
    async def _navigate_to_url(self, command: str) -> str:
        """Navigate to a URL"""
        # Extract URL from command
        words = command.split()
        url = None
        
        for word in words:
            if word.startswith("http") or "." in word:
                url = word
                break
        
        if not url:
            return "Error: No valid URL found in command"
        
        # Send navigation command to MCP server
        result = await self._send_mcp_command({
            "action": "navigate",
            "url": url
        })
        
        return f"Navigated to {url}: {result}"
    
    async def _click_element(self, command: str) -> str:
        """Click on a page element"""
        # Extract selector from command
        selector = self._extract_selector(command)
        
        result = await self._send_mcp_command({
            "action": "click",
            "selector": selector
        })
        
        return f"Clicked element '{selector}': {result}"
    
    async def _fill_form(self, command: str) -> str:
        """Fill form fields"""
        # Parse command for field and value
        parts = command.lower().split()
        
        result = await self._send_mcp_command({
            "action": "fill",
            "command": command
        })
        
        return f"Form filled: {result}"
    
    async def _take_screenshot(self) -> str:
        """Take page screenshot"""
        result = await self._send_mcp_command({
            "action": "screenshot"
        })
        
        return f"Screenshot taken: {result}"
    
    async def _scrape_page(self, command: str) -> str:
        """Scrape page content"""
        result = await self._send_mcp_command({
            "action": "scrape",
            "command": command
        })
        
        return f"Page scraped: {result}"
    
    async def _general_browser_action(self, command: str) -> str:
        """Handle general browser actions"""
        result = await self._send_mcp_command({
            "action": "general",
            "command": command
        })
        
        return f"Browser action completed: {result}"
    
    async def _send_mcp_command(self, command_data: Dict[str, Any]) -> str:
        """Send command to MCP server"""
        try:
            # For now, return a placeholder response
            # In full implementation, this would communicate with the MCP server
            log_info("browser_mcp", f"MCP command: {command_data}")
            return "Command sent to browser MCP server"
            
        except Exception as e:
            log_error("browser_mcp", f"MCP communication error: {str(e)}")
            return f"MCP error: {str(e)}"
    
    def _extract_selector(self, command: str) -> str:
        """Extract CSS selector from command"""
        # Simple selector extraction logic
        if "button" in command.lower():
            return "button"
        elif "link" in command.lower():
            return "a"
        elif "input" in command.lower():
            return "input"
        else:
            return "*"
    
    async def stop_mcp_server(self):
        """Stop MCP server"""
        if self.mcp_process and self.server_running:
            try:
                self.mcp_process.terminate()
                await self.mcp_process.wait()
                self.server_running = False
                log_info("browser_mcp", "Browser MCP server stopped")
            except Exception as e:
                log_error("browser_mcp", f"Error stopping MCP server: {str(e)}")
    
    @staticmethod
    def schema():
        return {
            "name": "browser_mcp",
            "description": "Web browser automation and interaction using MCP",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Browser automation command"
                }
            }
        }


# Tool instance for ULTRON Agent
browser_mcp_tool = BrowserMCPTool()