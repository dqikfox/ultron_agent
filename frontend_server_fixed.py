#!/usr/bin/env python3
"""
ULTRON Chat Engine Server - Serves NVIDIA AI Chat on port 5173
This is separate from the main GUI which serves on port 5000
"""

import http.server
import socketserver
import json
import os
from pathlib import Path

class UltronChatEngineServer:
    def __init__(self, port=5173):
        self.port = port
        self.server = None
        self.running = False

    def start(self):
        """Start the chat engine server"""
        try:
            # Create custom handler for chat functionality
            handler = self.create_chat_handler()
            self.server = socketserver.TCPServer(("", self.port), handler)

            print(f"[CHAT ENGINE] NVIDIA Chat Engine starting... - frontend_server_fixed.py:26")
            print(f"[CHAT ENGINE] Chat URL: http://localhost:{self.port} - frontend_server_fixed.py:27")
            print(f"[CHAT ENGINE] This serves the NVIDIA AI Assistant - frontend_server_fixed.py:28")
            print("[CHAT ENGINE] - frontend_server_fixed.py:29" + "=" * 50)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f"[ERROR] Chat engine failed: {e} - frontend_server_fixed.py:35")
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

            def log_message(self, format, *args):
                # Suppress default logging to avoid encoding issues
                pass

            def get_chat_html(self):
                return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRON NVIDIA Chat Engine</title>
    <style>
        body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }

        .header {
            text-align: center;
            border: 2px solid #00ff00;
            padding: 20px;
            margin-bottom: 20px;
            background: rgba(0, 255, 0, 0.1);
        }

        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #00ff00;
            background: rgba(0, 255, 0, 0.05);
            padding: 20px;
        }

        .chat-messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #004400;
            background: #000;
            padding: 10px;
            margin-bottom: 20px;
        }

        .message {
            margin-bottom: 10px;
            padding: 5px;
        }

        .system-message {
            color: #ffaa00;
        }

        .user-message {
            color: #00ffff;
        }

        .ai-message {
            color: #00ff00;
        }

        .input-area {
            display: flex;
            gap: 10px;
        }

        input[type="text"] {
            flex: 1;
            background: #000;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 10px;
            font-family: inherit;
        }

        button {
            background: #004400;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 10px 20px;
            cursor: pointer;
            font-family: inherit;
        }

        button:hover {
            background: #006600;
        }

        .status {
            text-align: center;
            padding: 10px;
            margin-top: 20px;
            border: 1px solid #004400;
            background: rgba(0, 255, 0, 0.05);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ULTRON NVIDIA CHAT ENGINE</h1>
        <p>AI-Powered Assistant Interface</p>
        <p>Port 5173 - NVIDIA Backend Integration</p>
    </div>

    <div class="chat-container">
        <div class="chat-messages" id="messages">
            <div class="message system-message">
                [SYSTEM] NVIDIA Chat Engine initialized
            </div>
            <div class="message system-message">
                [SYSTEM] Ready to process AI requests
            </div>
            <div class="message ai-message">
                [ULTRON] Hello! I'm your NVIDIA-powered AI assistant. How can I help you today?
            </div>
        </div>

        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message here..." />
            <button onclick="sendMessage()">Send</button>
            <button onclick="clearChat()">Clear</button>
        </div>
    </div>

    <div class="status">
        <p>Status: <span id="status">ACTIVE</span></p>
        <p>Backend: NVIDIA AI Processing</p>
        <p>Main GUI: <a href="http://localhost:5000" target="_blank" style="color: #00ffff;">ULTRON Pokédex GUI</a></p>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const messages = document.getElementById('messages');

            if (input.value.trim()) {
                // Add user message
                const userMsg = document.createElement('div');
                userMsg.className = 'message user-message';
                userMsg.textContent = '[USER] ' + input.value;
                messages.appendChild(userMsg);

                // Simulate AI response
                setTimeout(() => {
                    const aiMsg = document.createElement('div');
                    aiMsg.className = 'message ai-message';
                    aiMsg.textContent = '[ULTRON] Processing your request with NVIDIA AI...';
                    messages.appendChild(aiMsg);
                    messages.scrollTop = messages.scrollHeight;
                }, 500);

                input.value = '';
                messages.scrollTop = messages.scrollHeight;
            }
        }

        function clearChat() {
            const messages = document.getElementById('messages');
            messages.innerHTML = `
                <div class="message system-message">[SYSTEM] Chat cleared</div>
                <div class="message ai-message">[ULTRON] Ready for new conversation</div>
            `;
        }

        // Handle Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Update status indicator
        setInterval(() => {
            document.getElementById('status').textContent = 'ACTIVE - ' + new Date().toLocaleTimeString();
        }, 1000);
    </script>
</body>
</html>"""

        return ChatHandler

    def stop(self):
        """Stop the chat engine server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[CHAT ENGINE] Chat engine stopped - frontend_server_fixed.py:245")

if __name__ == "__main__":
    server = UltronChatEngineServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[CHAT ENGINE] Shutting down chat engine... - frontend_server_fixed.py:252")
        server.stop()
