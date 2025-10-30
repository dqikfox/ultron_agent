"""
Amazon Q Integration Tool for ULTRON Agent
Handles auto-run commands and Amazon Q specific functionality
"""

import json
import os
import time
import threading
from utils.ultron_logger import log_info, log_error
from .tool_interface import ToolInterface

class AmazonQIntegrationTool(ToolInterface):
    """Amazon Q integration with auto-run capabilities"""
    
    @property
    def name(self) -> str:
        return "Amazon Q Integration"
    
    @property
    def description(self) -> str:
        return "Amazon Q auto-run commands and integration features"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.auto_run_enabled = True
        self.startup_commands = [
            "search tor for latest news in ai",
            "start web interface", 
            "system status",
            "check ollama status"
        ]
        self.auto_run_executed = False
        
    def match(self, command: str) -> bool:
        """Check if command matches Amazon Q operations"""
        return any(keyword in command.lower() for keyword in [
            "amazon q", "auto run", "startup commands", "q integration"
        ])
    
    def execute(self, command: str) -> str:
        """Execute Amazon Q operations"""
        try:
            if "auto run" in command.lower():
                return self._execute_auto_run()
            elif "startup" in command.lower():
                return self._get_startup_info()
            elif "enable" in command.lower():
                self.auto_run_enabled = True
                return "Amazon Q auto-run enabled"
            elif "disable" in command.lower():
                self.auto_run_enabled = False
                return "Amazon Q auto-run disabled"
            else:
                return self._show_help()
        except Exception as e:
            log_error("amazon_q_integration", f"Operation failed: {e}")
            return f"Amazon Q error: {str(e)}"
    
    def _execute_auto_run(self) -> str:
        """Execute auto-run commands"""
        if not self.auto_run_enabled:
            return "Auto-run is disabled"
            
        if self.auto_run_executed:
            return "Auto-run commands already executed"
        
        try:
            log_info("amazon_q_integration", "Executing auto-run commands")
            
            results = []
            for cmd in self.startup_commands:
                try:
                    # Import agent core to execute commands
                    from agent_core import UltronAgent
                    import asyncio
                    
                    async def run_command():
                        agent = UltronAgent()
                        await agent.initialize()
                        return await agent.process_command(cmd)
                    
                    result = asyncio.run(run_command())
                    results.append(f"✓ {cmd}: Success")
                    log_info("amazon_q_integration", f"Auto-run command executed: {cmd}")
                    
                except Exception as e:
                    results.append(f"✗ {cmd}: {str(e)}")
                    log_error("amazon_q_integration", f"Auto-run command failed: {cmd} - {e}")
            
            self.auto_run_executed = True
            return "Amazon Q Auto-run completed:\n" + "\n".join(results)
            
        except Exception as e:
            log_error("amazon_q_integration", f"Auto-run execution failed: {e}")
            return f"Auto-run failed: {str(e)}"
    
    def _get_startup_info(self) -> str:
        """Get startup command information"""
        return f"""Amazon Q Auto-Run Configuration:
        
Status: {'Enabled' if self.auto_run_enabled else 'Disabled'}
Executed: {'Yes' if self.auto_run_executed else 'No'}

Startup Commands:
{chr(10).join(f'• {cmd}' for cmd in self.startup_commands)}

Use 'amazon q auto run' to execute manually"""
    
    def _show_help(self) -> str:
        """Show help information"""
        return """Amazon Q Integration Commands:
        
• amazon q auto run - Execute startup commands
• amazon q startup - Show startup configuration  
• amazon q enable - Enable auto-run
• amazon q disable - Disable auto-run

Auto-run commands will execute:
• Tor search for AI news
• Start web interface
• System status check
• Ollama status check"""
    
    def start_auto_run_on_startup(self):
        """Start auto-run commands with delay"""
        if not self.auto_run_enabled:
            return
            
        def delayed_auto_run():
            time.sleep(3)  # 3 second delay
            self._execute_auto_run()
        
        thread = threading.Thread(target=delayed_auto_run, daemon=True)
        thread.start()
        log_info("amazon_q_integration", "Auto-run scheduled for startup")
    
    @classmethod
    def schema(cls):
        return {
            "name": "amazon_q_integration",
            "description": "Amazon Q auto-run commands and integration",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Amazon Q integration command"
                    }
                },
                "required": ["command"]
            }
        }