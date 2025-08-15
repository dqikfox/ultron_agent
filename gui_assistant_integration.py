#!/usr/bin/env python3
"""
GUI-Assistant Integration Module
Provides communication between the GUI and assistant components
"""

import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from pathlib import Path

class GuiAssistantIntegration:
    """Integration layer between GUI and Assistant"""
    
    def __init__(self, assistant_url: str = "http://localhost:5173"):
        self.assistant_url = assistant_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_to_assistant(self, message: str, message_type: str = "command") -> Optional[Dict[str, Any]]:
        """Send message to assistant"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            payload = {
                "message": message,
                "type": message_type,
                "source": "gui",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            async with self.session.post(
                f"{self.assistant_url}/api/message",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def get_assistant_status(self) -> Dict[str, Any]:
        """Get assistant status"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(
                f"{self.assistant_url}/api/status",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "offline", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    def is_assistant_available(self) -> bool:
        """Check if assistant is available"""
        try:
            import requests
            response = requests.get(f"{self.assistant_url}/api/health", timeout=2)
            return response.status_code == 200
        except:
            return False

# Utility functions for GUI integration
def create_assistant_link_html() -> str:
    """Create HTML link to assistant"""
    return """
    <div style="position: fixed; top: 10px; right: 10px; z-index: 9999;">
        <a href="http://localhost:5173" target="_blank" 
           style="background: #ff0000; color: white; padding: 8px 16px; 
                  text-decoration: none; border-radius: 4px; font-size: 12px;">
            🤖 AI Assistant
        </a>
    </div>
    """

def inject_assistant_link(html_content: str) -> str:
    """Inject assistant link into HTML content"""
    link_html = create_assistant_link_html()
    
    # Try to inject after <body> tag
    if "<body>" in html_content:
        return html_content.replace("<body>", f"<body>{link_html}")
    # Fallback: inject at the end
    elif "</body>" in html_content:
        return html_content.replace("</body>", f"{link_html}</body>")
    else:
        return html_content + link_html

# Example usage for GUI components
async def example_gui_integration():
    """Example of how to use the integration"""
    async with GuiAssistantIntegration() as integration:
        # Check if assistant is available
        status = await integration.get_assistant_status()
        print(f"Assistant status: {status}")
        
        # Send a command to assistant
        if status.get("status") != "offline":
            response = await integration.send_to_assistant(
                "Hello from GUI", 
                "greeting"
            )
            print(f"Assistant response: {response}")

if __name__ == "__main__":
    # Test the integration
    asyncio.run(example_gui_integration())