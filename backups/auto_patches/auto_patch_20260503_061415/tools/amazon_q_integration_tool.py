"""
Amazon Q Integration Tool for ULTRON Agent
Handles auto-run commands and Amazon Q specific functionality
"""

import asyncio
import threading
import time
from typing import Any, Dict, List, Optional

from utils.ultron_logger import log_error, log_info

from .tool_interface import ToolInterface


class AmazonQIntegrationTool(ToolInterface):
    """Amazon Q integration with auto-run capabilities"""

    @property
    def name(self) -> str:
        return "Amazon Q Integration"

    @property
    def description(self) -> str:
        return "Amazon Q auto-run commands and integration features"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self.auto_run_enabled: bool = True
        self.startup_commands: List[str] = [
            "search tor for latest news in ai",
            "start web interface",
            "system status",
            "check ollama status"
        ]
        self.auto_run_executed: bool = False

    def match(self, command: str) -> bool:
        """Check if command matches Amazon Q operations"""
        keywords: List[str] = [
            "amazon q", "auto run", "startup commands", "q integration"
        ]
        return any(keyword in command.lower() for keyword in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute Amazon Q operations"""
        try:
            cmd_lower: str = command.lower()
            if "auto run" in cmd_lower:
                return self._execute_auto_run()
            elif "startup" in cmd_lower:
                return self._get_startup_info()
            elif "enable" in cmd_lower:
                self.auto_run_enabled = True
                return "Amazon Q auto-run enabled"
            elif "disable" in cmd_lower:
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

            results: List[str] = []
            for cmd in self.startup_commands:
                try:
                    # Import agent core to execute commands
                    from agent_core import UltronAgent

                    async def run_command() -> Any:
                        agent: UltronAgent = UltronAgent()
                        await agent.initialize()
                        cmd_result: Any = await agent.process_command(cmd)
                        return cmd_result

                    asyncio.run(run_command())
                    results.append(f"✓ {cmd}: Success")
                    log_info(
                        "amazon_q_integration", f"Auto-run command: {cmd}"
                    )

                except Exception as e:
                    results.append(f"✗ {cmd}: {str(e)}")
                    log_error(
                        "amazon_q_integration", f"Auto-run failed: {cmd}"
                    )

            self.auto_run_executed = True
            return "Amazon Q Auto-run completed:\n" + "\n".join(results)

        except Exception as e:
            log_error(
                "amazon_q_integration", f"Auto-run execution failed: {e}"
            )
            return f"Auto-run failed: {str(e)}"

    def _get_startup_info(self) -> str:
        """Get startup command information"""
        status: str = 'Enabled' if self.auto_run_enabled else 'Disabled'
        executed: str = 'Yes' if self.auto_run_executed else 'No'
        commands_list: str = "\n".join(
            f"• {cmd}" for cmd in self.startup_commands
        )

        return f"""Amazon Q Auto-Run Configuration:

Status: {status}
Executed: {executed}

Startup Commands:
{commands_list}

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

    def start_auto_run_on_startup(self) -> None:
        """Start auto-run commands with delay"""
        if not self.auto_run_enabled:
            return

        def delayed_auto_run() -> None:
            time.sleep(3)  # 3 second delay
            self._execute_auto_run()

        thread: threading.Thread = threading.Thread(
            target=delayed_auto_run, daemon=True
        )
        thread.start()
        log_info("amazon_q_integration", "Auto-run scheduled for startup")

    @staticmethod
    def schema() -> Dict[str, Any]:
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
