#!/usr/bin/env python3
"""
ULTRON Unified Server - Single Port Architecture
Serves everything on port 5000:
- Main Pokédx GUI at /
- Dashboard at /dashboard
- Chat engine at /chat
- API endpoints at /api/*
- Static assets at /assets/*
- Health checks at /health
"""

import http.server
import socketserver
import json
import os
import urllib.parse
from pathlib import Path

class UltronUnifiedServer:
    def __init__(self, port=5000):
        self.port = port
        self.gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
        self.server = None
        self.running = False

    def start(self):
        """Start the unified server"""
        try:
            if not self.gui_dir.exists():
                print(f"[ERROR] GUI directory not found: {self.gui_dir}")
                return False

            # Create custom handler for unified functionality
            handler = self.create_unified_handler()
            self.server = socketserver.TCPServer(("", self.port), handler)

            print(f"[ULTRON] Unified Server starting on port {self.port}")
            print(f"[ULTRON] Main Pokédx GUI:    http://localhost:{self.port}/")
            print(f"[ULTRON] Dashboard:          http://localhost:{self.port}/dashboard")
            print(f"[ULTRON] Chat Engine:        http://localhost:{self.port}/chat")
            print(f"[ULTRON] API Endpoints:      http://localhost:{self.port}/api/*")
            print(f"[ULTRON] Health Check:       http://localhost:{self.port}/health")
            print("[ULTRON] " + "=" * 60)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f"[ERROR] Unified server failed: {e}")
            return False

    def create_unified_handler(self):
        """Create unified HTTP handler for all routes"""
        gui_dir = self.gui_dir

        class UnifiedHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                # Parse the URL path
                parsed_path = urllib.parse.urlparse(self.path)
                path = parsed_path.path

                # Log all requests
                print(f"[REQUEST] {path}")

                # Route handling
                if path == "/" or path == "/index.html":
                    # Main Pokédx GUI
                    self.serve_pokedx_gui()
                elif path == "/dashboard.html":
                    # Serve existing dashboard.html from root
                    self.serve_root_html_file("dashboard.html")
                elif path == "/ULTRON_CHAT_ENGINE.html":
                    # Serve existing ULTRON_CHAT_ENGINE.html from root
                    self.serve_root_html_file("ULTRON_CHAT_ENGINE.html")
                elif path == "/dashboard":
                    # Dashboard interface
                    self.serve_dashboard()
                elif path == "/chat":
                    # Chat engine interface
                    self.serve_chat()
                elif path.startswith("/api/"):
                    # API endpoints
                    self.serve_api(path)
                elif path == "/health":
                    # Health check
                    self.serve_health()
                elif path.startswith("/assets/") or path.endswith((".css", ".js", ".png", ".ico", ".wav")):
                    # Static assets from GUI directory
                    self.serve_static(path)
                else:
                    # 404 for unknown routes
                    print(f"[404] Unknown route: {path}")
                    self.send_error(404, "Not Found")

            def do_POST(self):
                # Handle POST requests for API interactions
                parsed_path = urllib.parse.urlparse(self.path)
                path = parsed_path.path

                print(f"[POST] {path}")

                if path.startswith("/api/"):
                    self.serve_api(path)
                else:
                    self.send_error(404, "Not Found")

            def serve_pokedx_gui(self):
                """Serve the main Pokédx GUI"""
                try:
                    gui_file = gui_dir / "index.html"
                    if gui_file.exists():
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        with open(gui_file, 'r', encoding='utf-8') as f:
                            self.wfile.write(f.read().encode('utf-8'))
                    else:
                        self.send_error(404, "Pokédx GUI not found")
                except Exception as e:
                    self.send_error(500, f"Error serving GUI: {e}")

            def serve_dashboard(self):
                """Serve dashboard interface"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ULTRON Dashboard</title>
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: monospace; padding: 20px; }
        .header { text-align: center; border: 2px solid #00ff00; padding: 20px; margin-bottom: 20px; }
        .nav { display: flex; justify-content: center; gap: 20px; margin: 20px 0; }
        .nav a { color: #00ffff; text-decoration: none; padding: 10px 20px; border: 1px solid #00ffff; }
        .nav a:hover { background: rgba(0,255,255,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>ULTRON SYSTEM DASHBOARD</h1>
        <p>Unified Control Center</p>
    </div>
    <div class="nav">
        <a href="/">🏠 Main GUI</a>
        <a href="/chat">💬 AI Chat</a>
        <a href="/api/status">🔌 API Status</a>
        <a href="/health">❤️ Health</a>
    </div>
    <div style="text-align: center; margin-top: 40px;">
        <h2>System Status: OPERATIONAL</h2>
        <p>All services running on unified port 5000</p>
    </div>
</body>
</html>"""
                self.wfile.write(dashboard_html.encode('utf-8'))

            def serve_chat(self):
                """Serve chat engine interface"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                chat_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ULTRON AI Chat</title>
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: monospace; margin: 0; padding: 20px; }
        .header { text-align: center; border: 2px solid #00ff00; padding: 20px; margin-bottom: 20px; }
        .chat-container { max-width: 800px; margin: 0 auto; border: 1px solid #00ff00; padding: 20px; }
        .messages { height: 400px; overflow-y: auto; border: 1px solid #004400; background: #000; padding: 10px; margin-bottom: 20px; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; background: #000; color: #00ff00; border: 1px solid #00ff00; padding: 10px; }
        button { background: #004400; color: #00ff00; border: 1px solid #00ff00; padding: 10px 20px; cursor: pointer; }
        .nav-link { color: #00ffff; text-decoration: none; margin-right: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ULTRON AI CHAT ENGINE</h1>
        <p>NVIDIA-Powered Assistant</p>
        <p><a href="/" class="nav-link">← Back to Main GUI</a> <a href="/dashboard" class="nav-link">Dashboard</a></p>
    </div>
    <div class="chat-container">
        <div class="messages" id="messages">
            <div style="color: #ffaa00;">[SYSTEM] NVIDIA Chat Engine initialized</div>
            <div style="color: #00ff00;">[ULTRON] Hello! How can I assist you today?</div>
        </div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const messages = document.getElementById('messages');
            if (input.value.trim()) {
                messages.innerHTML += '<div style="color: #00ffff;">[USER] ' + input.value + '</div>';
                setTimeout(() => {
                    messages.innerHTML += '<div style="color: #00ff00;">[ULTRON] Processing your request...</div>';
                    messages.scrollTop = messages.scrollHeight;
                }, 500);
                input.value = '';
                messages.scrollTop = messages.scrollHeight;
            }
        }
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>"""
                self.wfile.write(chat_html.encode('utf-8'))

            def serve_api(self, path):
                """Serve API endpoints"""
                if path == "/api/log":
                    # Handle GUI interaction logging
                    try:
                        content_length = int(self.headers.get('Content-Length', 0))
                        if content_length > 0:
                            post_data = self.rfile.read(content_length)
                            log_data = json.loads(post_data.decode('utf-8'))

                            # Log to console and file
                            log_msg = f"[GUI-INTERACTION] {log_data.get('action', 'unknown')} - {log_data.get('element', 'unknown')} - {log_data.get('details', {})}"
                            print(log_msg)

                            # Log to file
                            with open('logs/gui_interactions.log', 'a', encoding='utf-8') as f:
                                f.write(f"{log_data.get('timestamp', '')} {log_msg}\n")

                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {"status": "logged"}
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                        return
                    except Exception as e:
                        print(f"[ERROR] Logging failed: {e}")

                # Regular API responses
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                if path == "/api/status":
                    response = {
                        "status": "operational",
                        "services": {
                            "main_gui": "active",
                            "chat_engine": "active",
                            "dashboard": "active",
                            "api": "active"
                        },
                        "port": 5000,
                        "architecture": "unified"
                    }
                elif path == "/api/chat":
                    response = {"message": "Chat API ready", "status": "active"}
                else:
                    response = {"error": "Unknown API endpoint", "path": path}

                self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

            def serve_health(self):
                """Serve health check"""
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                health_data = {
                    "status": "healthy",
                    "timestamp": "2025-08-18",
                    "services": ["gui", "chat", "dashboard", "api"],
                    "port": 5000
                }
                self.wfile.write(json.dumps(health_data, indent=2).encode('utf-8'))

            def serve_static(self, path):
                """Serve static assets from GUI directory"""
                try:
                    # Remove leading slash and resolve path
                    file_path = gui_dir / path.lstrip('/')

                    if file_path.exists() and file_path.is_file():
                        # Determine content type
                        content_type = "text/plain"
                        if path.endswith('.css'):
                            content_type = "text/css"
                        elif path.endswith('.js'):
                            content_type = "application/javascript"
                        elif path.endswith('.png'):
                            content_type = "image/png"
                        elif path.endswith('.ico'):
                            content_type = "image/x-icon"
                        elif path.endswith('.wav'):
                            content_type = "audio/wav"

                        self.send_response(200)
                        self.send_header('Content-type', content_type)
                        self.end_headers()

                        # Read and serve file
                        if content_type.startswith('text') or content_type == 'application/javascript':
                            with open(file_path, 'r', encoding='utf-8') as f:
                                self.wfile.write(f.read().encode('utf-8'))
                        else:
                            with open(file_path, 'rb') as f:
                                self.wfile.write(f.read())
                    else:
                        self.send_error(404, f"Static file not found: {path}")
                except Exception as e:
                    self.send_error(500, f"Error serving static file: {e}")

            def serve_root_html_file(self, filename):
                """Serve HTML files from the project root directory"""
                try:
                    root_dir = Path(__file__).parent
                    file_path = root_dir / filename

                    if file_path.exists() and file_path.is_file():
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()

                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.wfile.write(content.encode('utf-8'))

                        print(f"[SUCCESS] Served {filename} from root directory")
                    else:
                        self.send_error(404, f"HTML file not found: {filename}")
                        print(f"[ERROR] File not found: {file_path}")

                except Exception as e:
                    self.send_error(500, f"Error serving HTML file: {e}")
                    print(f"[ERROR] Error serving {filename}: {e}")

            def log_message(self, format, *args):
                # Suppress default request logging to keep output clean
                pass

        return UnifiedHandler

    def stop(self):
        """Stop the unified server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[ULTRON] Unified server stopped")

if __name__ == "__main__":
    server = UltronUnifiedServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[ULTRON] Shutting down unified server...")
        server.stop()
