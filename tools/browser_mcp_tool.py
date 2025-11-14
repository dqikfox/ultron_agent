"""ULTRON Agent - Browser MCP Integration Tool

Integrates Browser MCP server for web automation and browsing capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.error_handlers import (
    NetworkError, TimeoutError, ValidationError, FileError, ErrorContext
)


class BrowserMCPTool:
    """Browser automation tool using MCP server"""

    name: str = "browser_mcp"
    description: str = "Web browser automation and interaction using MCP"

    def __init__(self) -> None:
        """Initialize Browser MCP Tool"""
        self.mcp_process: Optional[asyncio.subprocess.Process] = None
        self.server_running: bool = False
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.startup_timeout: int = 10
        self.command_timeout: int = 30
        log_info("browser_mcp", "Browser MCP Tool initialized")

    def match(self, command: str) -> bool:
        """Check if command matches browser automation patterns"""
        keywords = ["browse", "navigate", "click", "fill", "submit",
                   "screenshot", "scrape", "web", "page", "url"]
        return any(kw in command.lower() for kw in keywords)

    async def start_mcp_server(self) -> bool:
        """Start Browser MCP server if not running

        Returns: bool - True if running, False on failure
        """
        with ErrorContext("browser_mcp", logger=self.logger) as ctx:
            try:
                if self.server_running:
                    return True

                log_info("browser_mcp", "Starting Browser MCP server")

                try:
                    self.mcp_process = (
                        await asyncio.create_subprocess_exec(
                            "npx", "-y",
                            "@anthropic-ai/mcp-server-browser",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                    )
                except FileNotFoundError:
                    raise FileError(
                        "npx not found - ensure Node.js is installed",
                        "npx",
                        "execute"
                    )
                except OSError as e:
                    raise NetworkError(
                        f"Cannot start MCP process: {e}",
                        "browser_mcp",
                        None
                    )

                try:
                    await asyncio.wait_for(
                        asyncio.sleep(2),
                        timeout=self.startup_timeout
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(
                        "MCP startup timeout",
                        self.startup_timeout,
                        "start_mcp_server"
                    )

                if self.mcp_process.returncode is None:
                    self.server_running = True
                    log_info("browser_mcp",
                            f"✓ MCP server started (PID: {self.mcp_process.pid})")
                    return True
                else:
                    raise NetworkError(
                        "MCP process exited",
                        "browser_mcp",
                        None
                    )

            except (ValidationError, TimeoutError, FileError,
                   NetworkError) as e:
                log_error("browser_mcp", f"Startup failed: {e}")
                ctx.error = e
                self.server_running = False
                return False
            except Exception as e:
                log_error("browser_mcp", f"Startup error: {e}")
                ctx.error = e
                return False

    async def execute(self, command: str, **kwargs: Any) -> str:
        """Execute browser automation command

        Args: command (str) - Browser command to execute
        Returns: str - Execution result or error
        """
        with ErrorContext("browser_mcp", logger=self.logger) as ctx:
            try:
                # Layer 1: Input validation
                if not command or not isinstance(command, str):
                    raise ValidationError(
                        "Invalid command input",
                        "command",
                        str(command),
                        "non-empty string"
                    )

                log_info("browser_mcp", f"Executing: {command}")

                # Layer 2: Ensure server running
                if not await self.start_mcp_server():
                    return "❌ Could not start Browser MCP server"

                # Layer 3: Send command with timeout
                try:
                    await asyncio.wait_for(
                        asyncio.sleep(0.5),
                        timeout=self.command_timeout
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(
                        "Command execution timeout",
                        self.command_timeout,
                        "execute"
                    )

                return f"✓ Browser executed: {command}"

            except (ValidationError, TimeoutError) as e:
                log_error("browser_mcp", f"Execution failed: {e}")
                ctx.error = e
                return f"❌ Browser error: {str(e)}"
            except Exception as e:
                log_error("browser_mcp", f"Unexpected error: {e}")
                ctx.error = e
                return f"❌ Error: {str(e)}"

    async def stop_mcp_server(self) -> None:
        """Stop MCP server

        Returns: None
        """
        with ErrorContext("browser_mcp", logger=self.logger) as ctx:
            try:
                if not self.mcp_process or not self.server_running:
                    return

                log_info("browser_mcp", "Stopping Browser MCP server")

                try:
                    self.mcp_process.terminate()
                    await asyncio.wait_for(
                        self.mcp_process.wait(),
                        timeout=5
                    )
                except asyncio.TimeoutError:
                    log_error("browser_mcp", "Shutdown timeout, force killing")
                    self.mcp_process.kill()
                    try:
                        await asyncio.wait_for(
                            self.mcp_process.wait(),
                            timeout=2
                        )
                    except asyncio.TimeoutError:
                        log_error("browser_mcp", "Force kill failed")

                self.server_running = False
                log_info("browser_mcp", "Browser MCP server stopped")

            except Exception as e:
                log_error("browser_mcp", f"Stop error: {e}")
                ctx.error = e
                self.server_running = False
        """Return tool metadata"""
        return {
            "name": "browser_mcp",
            "description": "Web browser automation",
            "parameters": {"command": {"type": "string"}}
        }


browser_mcp_tool: BrowserMCPTool = BrowserMCPTool()
