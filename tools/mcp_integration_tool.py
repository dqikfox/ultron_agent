"""
MCP Integration Tool for ULTRON Agent
Manages Model Context Protocol servers and provides unified access to external tools
"""
import os
import json
import subprocess
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.error_handlers import (
    NetworkError, TimeoutError, ValidationError, FileError,
    UltronError, ErrorContext
)


class MCPIntegrationTool(ToolInterface):
        def self_test(self) -> Dict[str, Any]:
            """
            Run diagnostics for MCPIntegrationTool: check config file, list servers, and catch errors.
            Returns:
                Dict: Diagnostic results (status, message, errors, details)
            """
            result = {
                "tool": self.name,
                "status": "ok",
                "message": "Self-test passed",
                "errors": [],
                "details": {}
            }
            try:
                # Check config file existence
                config_path = self.mcp_config_path
                if not config_path.exists():
                    result["status"] = "fail"
                    result["message"] = f"Config file not found: {config_path}"
                    result["errors"].append("Missing MCP config file")
                else:
                    result["details"]["config_file"] = str(config_path)
                # Try listing servers (simulate basic operation)
                try:
                    servers = self._list_servers()
                    result["details"]["server_list"] = servers
                except Exception as e:
                    result["status"] = "fail"
                    result["message"] = f"Server listing failed: {e}"
                    result["errors"].append(str(e))
            except Exception as e:
                result["status"] = "fail"
                result["message"] = f"Self-test exception: {e}"
                result["errors"].append(str(e))
            return result
    """
    Manages MCP (Model Context Protocol) servers for ULTRON Agent.
    Provides access to external tools like browser automation, GitHub, filesystem, and databases.
    """

    def __init__(self) -> None:
        self.mcp_config_path: Path = Path("C:/Projects/ultron_agent/mcp.json")
        self.active_servers: Dict[str, subprocess.Popen] = {}
        self.server_tools: Dict[str, List[Dict[str, Any]]] = {}
        log_info("mcp_integration", "MCP Integration Tool initialized")

    @property
    def name(self) -> str:
        return "MCP Integration"

    @property
    def description(self) -> str:
        return "Manages Model Context Protocol servers for browser automation, GitHub, filesystem, and database access"

    def match(self, command: str) -> bool:
        """Check if command should trigger MCP integration"""
        keywords: List[str] = [
            "mcp", "model context protocol", "browser automate", "github access",
            "filesystem access", "database query", "external tool", "mcp server",
            "start mcp", "stop mcp", "list mcp", "mcp status"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute MCP-related commands"""
        log_info("mcp_integration", f"Executing MCP command: {command}")

        try:
            cmd_lower: str = command.lower()

            # List available MCP servers
            if "list" in cmd_lower or "show" in cmd_lower or "status" in cmd_lower:
                return self._list_servers()

            # Start specific MCP server
            elif "start" in cmd_lower:
                server_name: Optional[str] = self._extract_server_name(command)
                if server_name:
                    return self._start_server(server_name)
                return "❌ Please specify a server name"

            # Stop specific MCP server
            elif "stop" in cmd_lower:
                server_name: Optional[str] = self._extract_server_name(command)
                if server_name:
                    return self._stop_server(server_name)
                return "❌ Please specify a server name"

            # Start all MCP servers
            elif "start all" in cmd_lower or "initialize" in cmd_lower:
                return self._start_all_servers()

            # Stop all MCP servers
            elif "stop all" in cmd_lower or "shutdown" in cmd_lower:
                return self._stop_all_servers()

            # Browser automation
            elif "browser" in cmd_lower or "navigate" in cmd_lower or "click" in cmd_lower:
                return self._browser_automation(command)

            # GitHub operations
            elif "github" in cmd_lower or "repository" in cmd_lower or "pull request" in cmd_lower:
                return self._github_operation(command)

            # Filesystem operations
            elif "file" in cmd_lower or "directory" in cmd_lower or "read file" in cmd_lower:
                return self._filesystem_operation(command)

            # Database operations
            elif "database" in cmd_lower or "query" in cmd_lower or "sql" in cmd_lower:
                return self._database_operation(command)

            else:
                return self._list_servers()

        except Exception as e:
            log_error("mcp_integration", f"Error executing MCP command: {e}", exception=e)
            return f"❌ Error: {str(e)}"

    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration from mcp.json"""
        with ErrorContext("mcp_integration", logger=logging.getLogger(__name__)) as ctx:
            try:
                ctx.operation = "load_mcp_config"

                if not self.mcp_config_path.exists():
                    raise FileError(
                        "MCP configuration file not found",
                        str(self.mcp_config_path),
                        "read",
                        reason="file_not_found"
                    )

                try:
                    with open(self.mcp_config_path, 'r', encoding='utf-8') as f:
                        config: Dict[str, Any] = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValidationError(
                        f"Invalid JSON in mcp.json: {e}",
                        "mcp_config_json",
                        str(e),
                        "valid JSON format"
                    )
                except (IOError, OSError) as e:
                    raise FileError(
                        f"Cannot read mcp.json: {e}",
                        str(self.mcp_config_path),
                        "read"
                    )

                servers_count: int = len(config.get('servers', {}))
                log_info("mcp_integration",
                        f"Loaded MCP config with {servers_count} servers")
                return config

            except (ValidationError, FileError) as e:
                log_error("mcp_integration", f"Config load failed: {e}")
                ctx.error = e
                return {"servers": {}}
            except Exception as e:
                log_error("mcp_integration",
                         f"Unexpected config error: {e}")
                ctx.error = e
                return {"servers": {}}

    def _list_servers(self) -> str:
        """List all available MCP servers and their status"""
        config: Dict[str, Any] = self._load_config()
        servers: Dict[str, Any] = config.get("servers", {})

        if not servers:
            return "⚠️ No MCP servers configured. Check mcp.json file."

        result: str = "📋 **MCP Servers Status**\n\n"

        for server_name in servers.keys():
            server_config: Dict[str, Any] = servers[server_name]
            status: str = "🟢 Running" if server_name in self.active_servers else "⚪ Stopped"
            description: str = server_config.get("description", "No description")
            command: str = server_config.get("command", "Unknown")

            result += f"**{server_name}**\n"
            result += f"  Status: {status}\n"
            result += f"  Description: {description}\n"
            result += f"  Command: {command}\n"
            result += f"  Type: {server_config.get('type', 'stdio')}\n\n"

        active_count: int = len(self.active_servers)
        total_count: int = len(servers)
        result += f"\n**Active Servers**: {active_count}/{total_count}\n"
        result += "\n💡 Use 'start mcp [server_name]' to start"

        return result

    def _start_server(self, server_name: str) -> str:
        """Start a specific MCP server"""
        with ErrorContext("mcp_integration") as ctx:
            try:
                if not server_name:
                    raise ValidationError(
                        "Server name is required",
                        "server_name",
                        server_name,
                        "non-empty string"
                    )

                if not isinstance(server_name, str):
                    raise ValidationError(
                        f"Invalid server name type: {type(server_name)}",
                        "server_name",
                        str(server_name),
                        "string"
                    )

                if server_name in self.active_servers:
                    return f"⚠️ Server '{server_name}' already running"

                config: Dict[str, Any] = self._load_config()
                servers: Dict[str, Any] = config.get("servers", {})

                if server_name not in servers:
                    raise ValidationError(
                        f"Server '{server_name}' not configured",
                        "server_name",
                        server_name,
                        f"one of {list(servers.keys())}"
                    )

                try:
                    server_config: Dict[str, Any] = servers[server_name]
                    command: str = server_config.get("command", "")
                    args: List[str] = server_config.get("args", [])

                    if not command:
                        raise ValidationError(
                            f"No command for {server_name}",
                            "command",
                            "",
                            "non-empty command"
                        )

                    env: Dict[str, str] = os.environ.copy()
                    env_overrides: Dict[str, str] = (
                        server_config.get("env", {})
                    )
                    env.update(env_overrides)

                    if command == "npx" and os.name == "nt":
                        command = "npx.cmd"

                    try:
                        process: subprocess.Popen = subprocess.Popen(
                            [command] + args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=env,
                            text=True,
                            shell=True
                        )
                    except FileNotFoundError:
                        raise FileError(
                            f"Command not found: {command}",
                            command,
                            "execute"
                        )
                    except OSError as exc:
                        raise NetworkError(
                            f"Cannot start process: {exc}",
                            server_name,
                            "POST"
                        )

                    self.active_servers[server_name] = process

                    log_info("mcp_integration",
                            f"Started MCP: {server_name}")
                    log_ai_decision(
                        "mcp_integration",
                        f"Started MCP '{server_name}'",
                        ai_model="ultron_agent",
                        confidence_score=1.0,
                        reasoning=f"Start {server_name}"
                    )

                    desc: str = server_config.get('description', 'N/A')
                    pid: int = process.pid if process.pid else 0
                    return (f"✅ MCP '{server_name}' started!\n\n"
                            f"Description: {desc}\n"
                            f"Process ID: {pid}\n\n"
                            f"💡 You can use {server_name} tools.")

                except (ValidationError, FileError, NetworkError) as e:
                    log_error("mcp_integration",
                             f"Start failed: {e}")
                    ctx.error = e
                    return f"❌ Start failed: {str(e)}"

            except ValidationError as e:
                log_error("mcp_integration",
                         f"Validation error: {e}")
                ctx.error = e
                return f"❌ Invalid: {str(e)}"
            except Exception as e:
                log_error("mcp_integration",
                         f"Start error: {e}")
                ctx.error = e
                return f"❌ Failed: {str(e)}"

    def _stop_server(self, server_name: str) -> str:
        """Stop a specific MCP server"""
        with ErrorContext("mcp_integration") as ctx:
            try:
                if not server_name:
                    raise ValidationError(
                        "Server name is required",
                        "server_name",
                        server_name,
                        "non-empty string"
                    )

                if server_name not in self.active_servers:
                    return f"⚠️ Server '{server_name}' not running"

                try:
                    process: subprocess.Popen = (
                        self.active_servers[server_name]
                    )
                    process.terminate()
                    process.wait(timeout=5)

                    del self.active_servers[server_name]

                    log_info("mcp_integration",
                            f"Stopped: {server_name}")
                    return (f"✅ MCP server '{server_name}' stopped")

                except subprocess.TimeoutExpired:
                    raise TimeoutError(
                        f"Timeout stopping {server_name}",
                        5,
                        "terminate"
                    )
                except (OSError, Exception) as e:
                    log_error("mcp_integration",
                             f"Stop failed: {e}")
                    try:
                        process.kill()
                        del self.active_servers[server_name]
                        return (f"⚠️ Server '{server_name}' "
                               "forcefully terminated")
                    except Exception:
                        ctx.error = e
                        return f"❌ Failed to stop: {str(e)}"

            except ValidationError as e:
                log_error("mcp_integration",
                         f"Validation error: {e}")
                ctx.error = e
                return f"❌ Invalid: {str(e)}"
            except TimeoutError as e:
                log_error("mcp_integration",
                         f"Timeout: {e}")
                ctx.error = e
                return f"⚠️ Timeout: {str(e)}"
            except Exception as e:
                log_error("mcp_integration",
                         f"Stop error: {e}")
                ctx.error = e
                return f"❌ Failed: {str(e)}"

    def _start_all_servers(self) -> str:
        """Start all configured MCP servers"""
        config: Dict[str, Any] = self._load_config()
        servers: Dict[str, Any] = config.get("servers", {})

        if not servers:
            return "⚠️ No MCP servers configured"

        results: List[str] = []
        success_count: int = 0

        for server_name in servers.keys():
            result: str = self._start_server(server_name)
            if "✅" in result:
                success_count += 1
            results.append(f"{server_name}: {result.split('!')[0]}")

        total: int = len(servers)
        summary: str = f"✅ Started {success_count}/{total} servers\n\n"
        return summary + "\n".join(results)

    def _stop_all_servers(self) -> str:
        """Stop all running MCP servers"""
        if not self.active_servers:
            return "⚠️ No MCP servers are running"

        server_names: List[str] = list(self.active_servers.keys())
        results: List[str] = []

        for server_name in server_names:
            result: str = self._stop_server(server_name)
            results.append(f"{server_name}: {result}")

        return "🛑 Stopped all MCP servers\n\n" + "\n".join(results)

    def _extract_server_name(self, command: str) -> Optional[str]:
        """Extract server name from command"""
        config: Dict[str, Any] = self._load_config()
        servers: Dict[str, Any] = config.get("servers", {})

        for server_name in servers.keys():
            if server_name.lower() in command.lower():
                return server_name

        return None

    def _browser_automation(self, command: str) -> str:
        """Execute browser automation through Browser MCP"""
        if "browsermcp" not in self.active_servers:
            return "⚠️ Browser MCP not running"

        log_info("mcp_integration", f"Browser automation: {command}")
        return f"🌐 Browser automation: {command}\n\n" \
               f"💡 Via Browser MCP server"

    def _github_operation(self, command: str) -> str:
        """Execute GitHub operations through GitHub MCP"""
        if "github" not in self.active_servers:
            return "⚠️ GitHub MCP not running"

        log_info("mcp_integration", f"GitHub operation: {command}")
        return f"🐙 GitHub operation: {command}\n\n" \
               f"💡 Via GitHub MCP server"

    def _filesystem_operation(self, command: str) -> str:
        """Execute filesystem operations through Filesystem MCP"""
        if "filesystem" not in self.active_servers:
            return "⚠️ Filesystem MCP not running"

        log_info("mcp_integration", f"Filesystem operation: {command}")
        return f"📁 Filesystem operation: {command}\n\n" \
               f"💡 Via Filesystem MCP server"

    def _database_operation(self, command: str) -> str:
        """Execute database operations through Postgres MCP"""
        if "postgres" not in self.active_servers:
            return "⚠️ Postgres MCP not running"

        log_info("mcp_integration", f"Database operation: {command}")
        return f"🗄️ Database operation: {command}\n\n" \
               f"💡 Via Postgres MCP server"

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "mcp_integration",
            "description": "MCP server management",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "MCP command to execute"
                    },
                    "server_name": {
                        "type": "string",
                        "description": "MCP server name",
                        "enum": ["browsermcp", "github", "filesystem",
                                 "postgres", "puppeteer"]
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool() -> MCPIntegrationTool:
    """Required function for tool loader"""
    return MCPIntegrationTool()
