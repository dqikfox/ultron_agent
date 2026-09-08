#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Web GUI Server Integration
Serves the beautiful web-based Pokédx GUI and integrates with agent backend
"""

import os
import sys
import json
import logging
import threading
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import http.server
import socketserver
import urllib.parse
import webbrowser
from datetime import datetime

# Import agent components
try:
    from agent_core import UltronAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logging.warning("Agent core not available")

class UltronWebHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for ULTRON web interface"""

    def __init__(self, *args, agent_ref=None, **kwargs):
        self.agent_ref = agent_ref
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        logging.info(f"📡 GET request: {self.path}")

        if self.path.startswith('/api/'):
            self._handle_api_get()
        elif self.path == '/' or self.path == '':
            self.path = '/index.html'
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        logging.info(f"📡 POST request: {self.path}")

        if self.path.startswith('/api/'):
            self._handle_api_post()
        else:
            self.send_error(404)

    def _handle_api_get(self):
        """Handle API GET requests"""
        try:
            if self.path == '/api/status':
                self._send_json_response(self._get_system_status())
            elif self.path == '/api/agent/info':
                self._send_json_response(self._get_agent_info())
            elif self.path == '/api/tools':
                self._send_json_response(self._get_tools_list())
            else:
                self.send_error(404, "API endpoint not found")

        except Exception as e:
            logging.error(f"API GET error: {e}")
            self.send_error(500, str(e))

    def _handle_api_post(self):
        """Handle API POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if self.path == '/api/command':
                response = self._process_command(data.get('command', ''))
                self._send_json_response({'response': response})
            elif self.path == '/api/voice/toggle':
                response = self._toggle_voice()
                self._send_json_response(response)
            else:
                self.send_error(404, "API endpoint not found")

        except Exception as e:
            logging.error(f"API POST error: {e}")
            self.send_error(500, str(e))

    def _send_json_response(self, data):
        """Send JSON response"""
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def _get_system_status(self):
        """Get system status information"""
        try:
            import psutil

            status = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent,
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
                },
                'agent': {
                    'status': 'online' if self.agent_ref else 'offline',
                    'uptime': '00:00:00'  # TODO: Calculate actual uptime
                }
            }

            # Add GPU info if available
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    status['system']['gpu'] = {
                        'memory_percent': int(mem_info.used) / int(mem_info.total) * 100,
                        'temperature': temp
                    }
            except:
                pass

            return status

        except Exception as e:
            return {'error': str(e)}

    def _get_agent_info(self):
        """Get agent information"""
        if not self.agent_ref:
            return {'status': 'offline', 'message': 'Agent not available'}

        info = {
            'status': getattr(self.agent_ref, 'status', 'unknown'),
            'tools_count': len(getattr(self.agent_ref, 'tools', [])),
            'components': {
                'brain': hasattr(self.agent_ref, 'brain') and self.agent_ref.brain is not None,
                'voice': hasattr(self.agent_ref, 'voice') and self.agent_ref.voice is not None,
                'memory': hasattr(self.agent_ref, 'memory') and self.agent_ref.memory is not None,
                'vision': hasattr(self.agent_ref, 'vision') and self.agent_ref.vision is not None
            }
        }

        return info

    def _get_tools_list(self):
        """Get list of available tools"""
        if not self.agent_ref or not hasattr(self.agent_ref, 'tools'):
            return {'tools': []}

        tools = []
        for tool in self.agent_ref.tools:
            tool_info = {
                'name': tool.__class__.__name__,
                'description': getattr(tool, 'description', 'No description available')
            }
            tools.append(tool_info)

        return {'tools': tools}

    def _process_command(self, command: str) -> str:
        """Process command through agent"""
        if not self.agent_ref:
            return "❌ Agent not available"

        try:
            if hasattr(self.agent_ref, 'process_command'):
                return self.agent_ref.process_command(command)
            elif hasattr(self.agent_ref, 'handle_text'):
                return self.agent_ref.handle_text(command)
            else:
                return "❌ Agent command processing not available"

        except Exception as e:
            logging.error(f"Command processing error: {e}")
            return f"❌ Error: {str(e)}"

    def _toggle_voice(self):
        """Toggle voice listening"""
        # This would integrate with voice system
        return {'status': 'not_implemented', 'message': 'Voice toggle not yet implemented'}

    def log_message(self, format, *args):
        """Custom log format"""
        logging.info(f"🌐 {format % args}")


class UltronWebServer:
    """ULTRON Web Server with agent integration"""

    def __init__(self, agent_ref: Optional[Any] = None, port: int = 8080):
        self.agent_ref = agent_ref
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def start_server(self):
        """Start the web server"""
        try:
            # Change to web_gui directory
            web_dir = Path(__file__).parent / "web_gui"
            if not web_dir.exists():
                raise FileNotFoundError("Web GUI directory not found. Please run the setup first.")

            os.chdir(web_dir)

            # Create handler with agent reference
            def handler_factory(*args, **kwargs):
                return UltronWebHandler(*args, agent_ref=self.agent_ref, **kwargs)

            # Create server
            self.server = socketserver.TCPServer(("", self.port), handler_factory)
            self.server.allow_reuse_address = True

            self.logger.info(f"🚀 ULTRON Web Server starting on port {self.port}")
            self.logger.info(f"📂 Serving from: {web_dir}")
            self.logger.info(f"🌐 Access GUI at: http://localhost:{self.port}")

            # Start server in background thread
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()

            # Open browser
            try:
                webbrowser.open(f"http://localhost:{self.port}")
                self.logger.info("🌍 Browser opened automatically")
            except:
                self.logger.warning("Could not open browser automatically")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to start web server: {e}")
            return False

    def _run_server(self):
        """Run the server loop"""
        try:
            self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"Server error: {e}")

    def stop_server(self):
        """Stop the web server"""
        if self.server and self.running:
            self.logger.info("🛑 Shutting down web server...")
            self.running = False
            self.server.shutdown()
            self.server.server_close()

            if self.server_thread:
                self.server_thread.join(timeout=2)

            self.logger.info("✅ Web server stopped")

    def wait_for_shutdown(self):
        """Wait for server to shutdown"""
        try:
            if self.server_thread:
                self.server_thread.join()
        except KeyboardInterrupt:
            self.logger.info("🔴 Shutdown requested by user")
            self.stop_server()


def main():
    """Main entry point for web GUI"""
    print("🤖 ULTRON Agent 3.0 - Web GUI Server")
    print("=" * 50)

    # Initialize agent if available
    agent = None
    if AGENT_AVAILABLE:
        try:
            print("🧠 Initializing ULTRON Agent...")
            agent = UltronAgent()
            print(f"✅ Agent initialized with status: {agent.status}")
        except Exception as e:
            print(f"⚠️ Agent initialization failed: {e}")
            print("🌐 Starting web server without agent backend")
    else:
        print("🌐 Starting web server in standalone mode")

    # Create and start web server
    server = UltronWebServer(agent_ref=agent, port=8080)

    if server.start_server():
        print("\n🎉 ULTRON Web GUI is now running!")
        print(f"🌐 Open your browser to: http://localhost:8080")
        print("🔴 Press Ctrl+C to stop")

        try:
            server.wait_for_shutdown()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            server.stop_server()
    else:
        print("❌ Failed to start web server")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
