"""
MCP Integration Tool for ULTRON Agent
Manages Model Context Protocol servers and provides unified access to external tools
"""
import os
import json
import subprocess
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision


class MCPIntegrationTool(ToolInterface):
    """
    Manages MCP (Model Context Protocol) servers for ULTRON Agent.
    Provides access to external tools like browser automation, GitHub, filesystem, and databases.
    """

    def __init__(self):
        self.mcp_config_path = Path("C:/Projects/ultron_agent/mcp.json")
        self.active_servers: Dict[str, subprocess.Popen] = {}
        self.server_tools: Dict[str, List[Dict]] = {}
        log_info("mcp_integration", "MCP Integration Tool initialized")

    @property
    def name(self) -> str:
        return "MCP Integration"

    @property
    def description(self) -> str:
        return "Manages Model Context Protocol servers for browser automation, GitHub, filesystem, and database access"

    def match(self, command: str) -> bool:
        """Check if command should trigger MCP integration"""
        keywords = [
            "mcp", "model context protocol", "browser automate", "github access",
            "filesystem access", "database query", "external tool", "mcp server",
            "start mcp", "stop mcp", "list mcp", "mcp status"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        """Execute MCP-related commands"""
        log_info("mcp_integration", f"Executing MCP command: {command}")

        try:
            cmd_lower = command.lower()

            # List available MCP servers
            if "list" in cmd_lower or "show" in cmd_lower or "status" in cmd_lower:
                return self._list_servers()

            # Start specific MCP server
            elif "start" in cmd_lower:
                server_name = self._extract_server_name(command)
                return self._start_server(server_name)

            # Stop specific MCP server
            elif "stop" in cmd_lower:
                server_name = self._extract_server_name(command)
                return self._stop_server(server_name)

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

    def _load_config(self) -> Dict:
        """Load MCP configuration from mcp.json"""
        try:
            if not self.mcp_config_path.exists():
                log_error("mcp_integration", "mcp.json not found")
                return {"servers": {}}

            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)

            log_info("mcp_integration", f"Loaded MCP config with {len(config.get('servers', {}))} servers")
            return config
        except Exception as e:
            log_error("mcp_integration", f"Error loading MCP config: {e}", exception=e)
            return {"servers": {}}

    def _list_servers(self) -> str:
        """List all available MCP servers and their status"""
        config = self._load_config()
        servers = config.get("servers", {})

        if not servers:
            return "⚠️ No MCP servers configured. Check mcp.json file."

        result = "📋 **MCP Servers Status**\n\n"

        for server_name, server_config in servers.items():
            status = "🟢 Running" if server_name in self.active_servers else "⚪ Stopped"
            description = server_config.get("description", "No description")
            command = server_config.get("command", "Unknown")

            result += f"**{server_name}**\n"
            result += f"  Status: {status}\n"
            result += f"  Description: {description}\n"
            result += f"  Command: {command}\n"
            result += f"  Type: {server_config.get('type', 'stdio')}\n\n"

        result += f"\n**Active Servers**: {len(self.active_servers)}/{len(servers)}\n"
        result += f"\n💡 Use 'start mcp [server_name]' to start a server"

        return result

    def _start_server(self, server_name: str) -> str:
        """Start a specific MCP server"""
        if not server_name:
            return "❌ Please specify a server name. Available: browsermcp, github, filesystem, postgres, puppeteer"

        if server_name in self.active_servers:
            return f"⚠️ Server '{server_name}' is already running"

        config = self._load_config()
        servers = config.get("servers", {})

        if server_name not in servers:
            return f"❌ Server '{server_name}' not found in mcp.json"

        try:
            server_config = servers[server_name]
            command = server_config.get("command")
            args = server_config.get("args", [])
            env = os.environ.copy()
            env.update(server_config.get("env", {}))

            # Resolve npx path on Windows if command is "npx"
            if command == "npx" and os.name == "nt":
                # Try to find npx.cmd in PATH
                npx_path = "npx.cmd"  # Windows uses .cmd extension
                # Could also use shutil.which("npx") but npx.cmd works with subprocess
                command = npx_path

            # Start the MCP server process
            process = subprocess.Popen(
                [command] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                shell=True  # Use shell on Windows to resolve PATH
            )

            self.active_servers[server_name] = process

            log_info("mcp_integration", f"Started MCP server: {server_name}")
            log_ai_decision(
                "mcp_integration",
                f"Started MCP server '{server_name}'",
                ai_model="ultron_agent",
                confidence_score=1.0,
                reasoning=f"User requested to start {server_name} server"
            )

            return f"✅ MCP server '{server_name}' started successfully!\n\n" \
                   f"Description: {server_config.get('description', 'N/A')}\n" \
                   f"Process ID: {process.pid}\n\n" \
                   f"💡 You can now use {server_name} tools in your commands."

        except Exception as e:
            error_msg = f"Error starting server {server_name}: {str(e)}"
            log_error("mcp_integration", error_msg)
            return f"❌ Failed to start server '{server_name}': {str(e)}"

    def _stop_server(self, server_name: str) -> str:
        """Stop a specific MCP server"""
        if not server_name:
            return "❌ Please specify a server name"

        if server_name not in self.active_servers:
            return f"⚠️ Server '{server_name}' is not running"

        try:
            process = self.active_servers[server_name]
            process.terminate()
            process.wait(timeout=5)

            del self.active_servers[server_name]

            log_info("mcp_integration", f"Stopped MCP server: {server_name}")
            return f"✅ MCP server '{server_name}' stopped successfully"

        except Exception as e:
            log_error("mcp_integration", f"Error stopping server {server_name}: {e}", exception=e)
            # Force kill if terminate fails
            try:
                process.kill()
                del self.active_servers[server_name]
                return f"⚠️ Server '{server_name}' forcefully terminated"
            except:
                return f"❌ Failed to stop server '{server_name}': {str(e)}"

    def _start_all_servers(self) -> str:
        """Start all configured MCP servers"""
        config = self._load_config()
        servers = config.get("servers", {})

        if not servers:
            return "⚠️ No MCP servers configured"

        results = []
        success_count = 0

        for server_name in servers.keys():
            result = self._start_server(server_name)
            if "✅" in result:
                success_count += 1
            results.append(f"{server_name}: {result.split('!')[0]}")

        summary = f"✅ Started {success_count}/{len(servers)} MCP servers\n\n"
        return summary + "\n".join(results)

    def _stop_all_servers(self) -> str:
        """Stop all running MCP servers"""
        if not self.active_servers:
            return "⚠️ No MCP servers are currently running"

        server_names = list(self.active_servers.keys())
        results = []

        for server_name in server_names:
            result = self._stop_server(server_name)
            results.append(f"{server_name}: {result}")

        return "🛑 Stopped all MCP servers\n\n" + "\n".join(results)

    def _extract_server_name(self, command: str) -> Optional[str]:
        """Extract server name from command"""
        config = self._load_config()
        servers = config.get("servers", {})

        for server_name in servers.keys():
            if server_name.lower() in command.lower():
                return server_name

        return None

    def _browser_automation(self, command: str) -> str:
        """Execute browser automation through Browser MCP"""
        if "browsermcp" not in self.active_servers:
            return "⚠️ Browser MCP server not running. Start it with: 'start mcp browsermcp'"

        log_info("mcp_integration", f"Browser automation: {command}")
        return f"🌐 Browser automation command: {command}\n\n" \
               f"💡 This would be executed through Browser MCP server.\n" \
               f"Note: Full implementation requires MCP client integration."

    def _github_operation(self, command: str) -> str:
        """Execute GitHub operations through GitHub MCP"""
        if "github" not in self.active_servers:
            return "⚠️ GitHub MCP server not running. Start it with: 'start mcp github'"

        log_info("mcp_integration", f"GitHub operation: {command}")
        return f"🐙 GitHub operation: {command}\n\n" \
               f"💡 This would be executed through GitHub MCP server.\n" \
               f"Note: Requires GitHub Personal Access Token in environment."

    def _filesystem_operation(self, command: str) -> str:
        """Execute filesystem operations through Filesystem MCP"""
        if "filesystem" not in self.active_servers:
            return "⚠️ Filesystem MCP server not running. Start it with: 'start mcp filesystem'"

        log_info("mcp_integration", f"Filesystem operation: {command}")
        return f"📁 Filesystem operation: {command}\n\n" \
               f"💡 This would be executed through Filesystem MCP server."

    def _database_operation(self, command: str) -> str:
        """Execute database operations through Postgres MCP"""
        if "postgres" not in self.active_servers:
            return "⚠️ Postgres MCP server not running. Start it with: 'start mcp postgres'"

        log_info("mcp_integration", f"Database operation: {command}")
        return f"🗄️ Database operation: {command}\n\n" \
               f"💡 This would be executed through Postgres MCP server.\n" \
               f"Note: Requires PostgreSQL connection string in environment."

    @classmethod
    def schema(cls) -> dict:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "mcp_integration",
            "description": "Manages Model Context Protocol servers for external tool access (browser, GitHub, filesystem, databases)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "MCP command to execute (list, start, stop, browser, github, filesystem, database operations)"
                    },
                    "server_name": {
                        "type": "string",
                        "description": "Optional: Specific MCP server name (browsermcp, github, filesystem, postgres, puppeteer)",
                        "enum": ["browsermcp", "github", "filesystem", "postgres", "puppeteer"]
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool for auto-discovery
def get_tool():
    """Required function for tool loader"""
    return MCPIntegrationTool()
