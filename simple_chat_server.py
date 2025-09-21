#!/usr/bin/env python3
"""
Simple ULTRON AI Chat Server
Provides basic AI chat functionality on port 8000
"""

import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List
import uvicorn
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ULTRON AI Chat Server", version="1.0.0")

class ChatServer:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversations: Dict[str, List[Dict]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected: {session_id}")

        if session_id not in self.conversations:
            self.conversations[session_id] = []

    def disconnect(self, websocket: WebSocket, session_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected: {session_id}")

    async def process_message(self, message: str, session_id: str) -> str:
        """Process user message and generate AI response"""
        try:
            # Add user message to conversation
            if session_id not in self.conversations:
                self.conversations[session_id] = []

            self.conversations[session_id].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })

            # Generate simple AI response (placeholder)
            ai_response = await self.generate_ai_response(message)

            # Add AI response to conversation
            self.conversations[session_id].append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat()
            })

            return ai_response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Sorry, I encountered an error processing your message."

    async def generate_ai_response(self, message: str) -> str:
        """Generate AI response (placeholder - integrate with actual AI)"""
        # Simple placeholder response
        responses = [
            "I understand you're asking about: " + message,
            "That's an interesting question about " + message,
            "Let me help you with: " + message,
            "I'd be happy to assist with: " + message
        ]

        # Simple keyword-based responses
        message_lower = message.lower()
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm ULTRON AI Assistant. How can I help you today?"
        elif "help" in message_lower:
            return "I'm here to help! You can ask me questions, request information, or give me commands."
        elif "status" in message_lower:
            return "All systems operational. ULTRON AI is ready to assist."
        else:
            return responses[len(message) % len(responses)]

chat_server = ChatServer()

@app.get("/")
async def get_chat_interface():
    """Serve the chat interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRON AI Chat</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #ffffff;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(45deg, #00d4ff, #090979);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background: rgba(0, 0, 0, 0.2);
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            max-width: 70%;
        }
        .user-message {
            background: linear-gradient(45deg, #667eea, #764ba2);
            margin-left: auto;
            text-align: right;
        }
        .assistant-message {
            background: linear-gradient(45deg, #f093fb, #f5576c);
            margin-right: auto;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }
        input[type="text"]::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        button {
            padding: 15px 25px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #00d4ff, #090979);
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .status {
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 10px;
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ULTRON AI Assistant</h1>
        <div id="status" class="status">🔴 Connecting...</div>
        <div id="messages" class="chat-messages"></div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message here...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let socket;
        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const status = document.getElementById('status');

        function connect() {
            socket = new WebSocket('ws://localhost:8000/ws');

            socket.onopen = function(event) {
                status.textContent = '🟢 Connected to ULTRON AI';
                status.style.background = 'rgba(0, 255, 0, 0.1)';
                status.style.borderColor = 'rgba(0, 255, 0, 0.3)';
                addMessage('ULTRON', 'Hello! I\\'m ULTRON AI Assistant. How can I help you today?');
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage('ULTRON', data.response);
            };

            socket.onclose = function(event) {
                status.textContent = '🔴 Disconnected';
                status.style.background = 'rgba(255, 0, 0, 0.1)';
                status.style.borderColor = 'rgba(255, 0, 0, 0.3)';
            };

            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
                status.textContent = '🔴 Connection Error';
            };
        }

        function addMessage(sender, message) {
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message ' + (sender === 'ULTRON' ? 'assistant-message' : 'user-message');
            msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
            messages.appendChild(msgDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function sendMessage() {
            const message = messageInput.value.trim();
            if (message && socket.readyState === WebSocket.OPEN) {
                addMessage('You', message);
                socket.send(JSON.stringify({message: message}));
                messageInput.value = '';
            }
        }

        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Connect on page load
        connect();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ULTRON AI Chat Server",
        "version": "1.0.0",
        "websocket_endpoint": "ws://localhost:8000/ws"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    session_id = f"session_{id(websocket)}"
    await chat_server.connect(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if "message" in message_data:
                response = await chat_server.process_message(
                    message_data["message"],
                    session_id
                )

                await websocket.send_json({
                    "response": response,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        chat_server.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    print("🤖 Starting ULTRON AI Chat Server...")
    print("🌐 Web interface: http://localhost:8000")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("🔗 Health check: http://localhost:8000/health")
    print("-" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
