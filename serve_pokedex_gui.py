#!/usr/bin/env python3
"""
Simple static file server for ULTRON Pokédex GUI
Serves the existing Pokédex interface and connects to the mobile web interface API
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class PokedexGUIHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for serving Pokédex GUI files"""

    def __init__(self, *args, api_port=8001, **kwargs):
        self.api_port = api_port
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests with dynamic API port injection"""
        try:
            # Map URL path to file path
            if self.path == '/':
                file_path = 'index.html'
            else:
                file_path = self.path.lstrip('/')

            # Get the web directory
            web_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
            full_path = web_dir / file_path

            # Check if file exists
            if not full_path.exists():
                self.send_error(404, "File not found")
                return

            # Read file content
            with open(full_path, 'rb') as f:
                content = f.read()

            # Inject API config into HTML files
            if file_path.endswith('.html'):
                content_str = content.decode('utf-8')
                api_config = f'<script>window.ULTRON_API_CONFIG = {{baseUrl: "http://localhost:{self.api_port}"}};</script>'
                content_str = content_str.replace('<head>', f'<head>{api_config}')
                content = content_str.encode('utf-8')

            # Send response
            self.send_response(200)
            if file_path.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif file_path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif file_path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            else:
                self.send_header('Content-type', 'application/octet-stream')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print(f"Error in do_GET: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Internal server error: {e}")

def main():
    """Start the Pokédex GUI server"""
    # Find API port (where mobile web interface is running)
    api_port = None
    for check_port in [8001, 8002, 8003, 8000]:  # Check common ports
        try:
            from utils.port_manager import PortManager
            if PortManager.is_port_available(check_port, 'localhost') == False:  # Port is in use
                # Quick check if it responds like our API
                try:
                    import requests
                    response = requests.get(f'http://localhost:{check_port}/api/status', timeout=2)
                    if response.status_code == 200:
                        api_port = check_port
                        break
                except:
                    continue
        except ImportError:
            # Fallback check
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', check_port))
            sock.close()
            if result == 0:
                api_port = check_port
                break

    if not api_port:
        print("Could not find ULTRON API server. Please ensure the mobile web interface is running.")
        print("Start ULTRON Agent first: python main.py")
        sys.exit(1)

    # Get available port for GUI server (prefer 8081)
    try:
        from utils.port_manager import PortManager
        port_manager = PortManager()
        port = port_manager.find_available_port(start_port=8081)  # Start from 8081
        if not port:
            port = 8081  # Fallback
    except ImportError:
        port = 8081  # Fallback

    print("Starting ULTRON Pokédex GUI Server...")
    print("=" * 50)
    print(f"Serving files from: gui/ultron_enhanced/web/")
    print(f"Local access: http://localhost:{port}")
    print(f"Network access: http://0.0.0.0:{port}")
    print(f"API backend: http://localhost:{api_port} (Mobile Web Interface)")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()

    try:
        # Create handler with API port configuration
        def handler_class(*args, **kwargs):
            return PokedexGUIHandler(*args, api_port=api_port, **kwargs)

        print("Creating server...")
        with socketserver.TCPServer(("", port), handler_class) as httpd:
            print(f"Server running on port {port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
