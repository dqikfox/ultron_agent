"""SSH Server Management Tool for ULTRON Agent"""

import subprocess
import threading
import socket
import time
from pathlib import Path
from tools.tool_interface import ToolInterface


class SSHServerTool(ToolInterface):
    """Manages SSH reverse tunnel server for remote Android/Termux connections"""

    def __init__(self):
        self.process = None
        self.port = 2222
        self.password = "password"
        self.script_path = Path(__file__).parent.parent / "ssh_server.py"

    @property
    def name(self) -> str:
        return "SSH Server Manager"

    @property
    def description(self) -> str:
        return "Start, stop, and manage SSH reverse tunnel server for Android/Termux connections"

    def match(self, command: str) -> bool:
        """Check if command should trigger this tool"""
        ssh_keywords = [
            "ssh server", "ssh start", "ssh stop", "ssh status",
            "ssh restart", "reverse tunnel", "android ssh",
            "termux connection", "remote shell"
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in ssh_keywords)

    def execute(self, command: str, **kwargs) -> str:
        """Execute SSH server management commands"""
        command_lower = command.lower()

        try:
            if any(word in command_lower for word in ["start", "begin", "launch"]):
                return self.start_server()
            elif any(word in command_lower for word in ["stop", "halt", "terminate"]):
                return self.stop_server()
            elif any(word in command_lower for word in ["restart", "reload", "reboot"]):
                return self.restart_server()
            elif any(word in command_lower for word in ["status", "state", "check"]):
                return self.get_status()
            elif any(word in command_lower for word in ["info", "details", "connection"]):
                return self.get_connection_info()
            else:
                return self.get_help()
        except Exception as e:
            return f"❌ SSH server error: {e}"

    def start_server(self) -> str:
        """Start the SSH server"""
        if self.is_running():
            return f"✅ SSH server already running on port {self.port}"

        if not self.script_path.exists():
            return f"❌ SSH server script not found: {self.script_path}"

        try:
            # Check if port is available
            if not self.is_port_available(self.port):
                return f"❌ Port {self.port} is already in use"

            # Start the SSH server in background
            self.process = subprocess.Popen(
                ["python", str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.script_path.parent
            )

            # Give it time to start
            time.sleep(2)

            if self.process.poll() is None and self.is_running():
                return (f"✅ SSH server started on port {self.port}\n"
                       f"🔗 Connect: ssh -p {self.port} user@<your-windows-ip>\n"
                       f"🔑 Password: {self.password}")
            else:
                return "❌ SSH server failed to start"

        except Exception as e:
            return f"❌ Failed to start SSH server: {e}"

    def stop_server(self) -> str:
        """Stop the SSH server"""
        if not self.is_running():
            return "⚠️ SSH server is not running"

        try:
            # Try graceful shutdown first
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)

            # Force kill any remaining SSH processes
            subprocess.run([
                "powershell", "-Command",
                "Get-Process python | Where-Object {$_.CommandLine -like '*ssh_server*'} | Stop-Process -Force"
            ], capture_output=True)

            self.process = None

            # Verify it stopped
            time.sleep(1)
            if not self.is_running():
                return "✅ SSH server stopped"
            else:
                return "⚠️ SSH server may still be running"

        except Exception as e:
            return f"❌ Failed to stop SSH server: {e}"

    def restart_server(self) -> str:
        """Restart the SSH server"""
        stop_result = self.stop_server()
        time.sleep(2)
        start_result = self.start_server()
        return f"{stop_result}\n{start_result}"

    def get_status(self) -> str:
        """Get SSH server status"""
        if self.is_running():
            return (f"✅ SSH server: ONLINE\n"
                   f"📡 Port: {self.port}\n"
                   f"🔗 Connect: ssh -p {self.port} user@<your-windows-ip>\n"
                   f"🔑 Password: {self.password}")
        else:
            return "❌ SSH server: OFFLINE"

    def get_connection_info(self) -> str:
        """Get SSH connection information"""
        local_ip = self.get_local_ip()
        return (f"📋 SSH CONNECTION INFO\n"
               f"🖥️  Server: {local_ip}:{self.port}\n"
               f"🔑 Password: {self.password}\n"
               f"📱 Android/Termux command:\n"
               f"   ssh -p {self.port} anyuser@{local_ip}\n\n"
               f"🪟 Windows command:\n"
               f"   ssh -p {self.port} anyuser@localhost\n\n"
               f"Status: {'ONLINE' if self.is_running() else 'OFFLINE'}")

    def get_help(self) -> str:
        """Get help information"""
        return ("📚 SSH SERVER COMMANDS\n"
               "• ssh start - Start the SSH server\n"
               "• ssh stop - Stop the SSH server\n"
               "• ssh restart - Restart the SSH server\n"
               "• ssh status - Check server status\n"
               "• ssh info - Get connection details\n\n"
               "🔗 Purpose: Allows Android/Termux devices to connect to Windows via reverse SSH tunnel")

    def is_running(self) -> bool:
        """Check if SSH server is running on the port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', self.port))
                return result == 0
        except Exception:
            return False

    def is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
                return True
        except Exception:
            return False

    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote server to get local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "localhost"

    @classmethod
    def schema(cls) -> dict:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "ssh_server_tool",
            "description": "Manage SSH reverse tunnel server for Android/Termux connections",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "SSH server command: start, stop, restart, status, info, or help"
                    }
                },
                "required": ["command"]
            }
        }
