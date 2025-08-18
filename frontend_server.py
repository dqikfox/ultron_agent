#!/usr/bin/env python3
"""            print(f"[CHAT ENGINE] NVIDIA Chat Engine starting...")
            prin    def stop(self):
        """Stop the chat engine server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[CHAT ENGINE] Chat engine stopped")

if __name__ == "__main__":
    server = UltronChatEngineServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[CHAT ENGINE] Shutting down chat engine...")
        server.stop()NE] Chat URL: http://localhost:{self.port}")
            print(f"[CHAT ENGINE] Note: Main GUI served by IIS")
            print("[CHAT ENGINE] " + "=" * 50)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f"[ERROR] Chat engine failed: {e}")
            return False

    def create_chat_handler(self):
        """Create custom HTTP handler for chat engine"""
        class ChatHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/" or self.path == "/index.html":
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self.get_chat_html().encode('utf-8'))
                elif self.path == "/api/chat":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"status": "ready", "message": "NVIDIA Chat Engine Ready"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()

            def get_chat_html(self):
                return '''<!DOCTYPE html>
<html>
<head>
    <title>ULTRON NVIDIA Chat Engine</title>
    <style>
        body { font-family: 'Courier New'; background: #000; color: #00ff00; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { background: #001100; padding: 10px; border: 1px solid #00ff00; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ULTRON NVIDIA Chat Engine</h1>
        <div class="status">
            <h3>Status: Active on Port 5173</h3>
            <p>Main GUI: Served by IIS</p>
            <p>Chat Engine: This service (localhost:5173)</p>
            <p>API Bridge: localhost:3000</p>
            <p>Agent Core: localhost:8000</p>
        </div>
        <div id="chat-area">
            <h3>Chat Interface Coming Soon</h3>
            <p>NVIDIA AI integration ready for implementation</p>
        </div>
    </div>
</body>
</html>'''

            def log_message(self, format, *args):
                # Suppress default logging to avoid encoding issues
                pass

        return ChatHandlere Server - NVIDIA AI Chat Interface
Runs on localhost:5173 as dedicated chat engine
Note: Main GUI served by IIS from C:\Projects\ultron_agent_2\gui\ultron_enhanced\web
"""

import http.server
import socketserver
import os
import sys
import json
from pathlib import Path

class UltronChatEngineServer:
    def __init__(self, port=5173):
        self.port = port
        self.chat_dir = Path(__file__).parent / "ULTRON_CHAT_ENGINE.html"
        self.server = None
        self.running = False

    def start(self):
        """Start the chat engine server"""
        try:
            # Create a simple HTTP handler for chat engine
            handler = self.create_chat_handler()
            self.server = socketserver.TCPServer(("", self.port), handler)

            # Create server
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            print(f"[FRONTEND] ULTRON Frontend Server starting... - frontend_server.py:97")
            print(f"[FRONTEND] Serving from: {self.gui_dir} - frontend_server.py:98")
            print(f"[FRONTEND] Frontend URL: http://localhost:{self.port} - frontend_server.py:99")
            print("[FRONTEND] - frontend_server.py:100" + "=" * 50)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f"[ERROR] Frontend server failed: {e} - frontend_server.py:106")
            return False
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)

    def stop(self):
        """Stop the frontend server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[FRONTEND] Frontend server stopped - frontend_server.py:117")

if __name__ == "__main__":
    server = UltronFrontendServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[FRONTEND] Shutting down frontend server... - frontend_server.py:124")
        server.stop()
