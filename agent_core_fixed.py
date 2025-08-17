"""
ULTRON Agent Core System
Main agent initialization and core functionality
"""

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import socketio
from pathlib import Path
import requests
from openai import OpenAI
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import uuid
import traceback
import uvicorn

class UltronAgent:
    """Core ULTRON agent with essential functionality"""

    def __init__(self):
        # NVIDIA API Configuration
        self.nvidia_api_keys = [
            "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",
            "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"
        ]
        self.current_api_key = self.nvidia_api_keys[0]

        # NVIDIA Model Configuration
        self.nvidia_models = {
            "llama-4-maverick": "meta/llama-4-maverick-17b-128e-instruct",
            "gpt-oss-120b": "openai/gpt-oss-120b",
            "llama-3.3-70b": "meta/llama-3.3-70b-instruct"
        }
        self.current_model = "llama-4-maverick"

        # FastAPI + Socket.IO Setup
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
        self.app = FastAPI(title="ULTRON Agent Core")

        # Setup routes and Socket.IO events
        self.setup_routes()
        self.setup_socketio_events()

        # Core agent state
        self.conversations: Dict[str, List[Dict]] = {}
        self.status = "initialized"
        self.is_running = False

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Combine with Socket.IO
        self.app = socketio.ASGIApp(self.sio, other_asgi_app=self.app)

    async def initialize(self):
        """Initialize agent - required by web_bridge.py"""
        self.logger.info("ULTRON Agent initialized and ready")
        self.is_running = True
        return True

    def setup_routes(self):
        """Setup FastAPI routes for the core agent"""

        @self.app.get("/")
        async def get_home():
            return await self.get_core_ui()

        @self.app.get("/health")
        async def health_check():
            return {
                "status": "operational",
                "current_model": self.current_model,
                "nvidia_models": list(self.nvidia_models.keys()),
                "api_status": "active"
            }

    def setup_socketio_events(self):
        """Setup Socket.IO event handlers for real-time communication"""

        @self.sio.event
        async def connect(sid, environ):
            self.logger.info(f"Client connected: {sid}")
            await self.sio.emit('connection_established', {
                'session_id': sid,
                'status': 'connected'
            }, to=sid)

        @self.sio.event
        async def disconnect(sid):
            self.logger.info(f"Client disconnected: {sid}")

        @self.sio.event
        async def user_message(sid, data):
            """Handle user messages and route to appropriate model"""
            try:
                user_text = data.get('text', '').strip()
                model_preference = data.get('model', self.current_model)

                if not user_text:
                    return

                # Initialize conversation history
                if sid not in self.conversations:
                    self.conversations[sid] = []

                # Add user message to history
                self.conversations[sid].append({
                    "role": "user",
                    "content": user_text,
                    "timestamp": datetime.now().isoformat()
                })

                # Process with selected model
                await self.process_user_message(sid, user_text, model_preference)

            except Exception as e:
                self.logger.error(f"Error processing user message: {e}")
                await self.sio.emit('error', {
                    'message': f"Error processing request: {str(e)}"
                }, to=sid)

    async def process_user_message(self, session_id: str, user_text: str, model: str):
        """Process user message with NVIDIA models"""
        try:
            # Performance tracking
            start_time = datetime.now()

            # Get conversation history
            messages = self.conversations.get(session_id, [])

            # Prepare NVIDIA API request
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.current_api_key
            )

            model_id = self.nvidia_models.get(model, self.nvidia_models[self.current_model])

            # Enhanced prompt with context awareness
            enhanced_messages = await self.enhance_messages_with_context(messages, session_id)

            # Stream response
            completion = client.chat.completions.create(
                model=model_id,
                messages=enhanced_messages,
                temperature=0.7,
                top_p=0.9,
                max_tokens=2048,
                stream=True
            )

            assistant_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_response += content

                    # Stream chunk to client
                    await self.sio.emit('assistant_chunk', {
                        'chunk': content,
                        'model': model,
                        'session_id': session_id
                    }, to=session_id)

            # Add assistant response to conversation history
            self.conversations[session_id].append({
                "role": "assistant",
                "content": assistant_response,
                "model": model,
                "timestamp": datetime.now().isoformat()
            })

            # Performance metrics
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            await self.sio.emit('assistant_done', {
                'response_time': response_time,
                'model_used': model,
                'message_length': len(assistant_response)
            }, to=session_id)

        except Exception as e:
            self.logger.error(f"Error processing NVIDIA response: {e}")
            await self.sio.emit('error', {
                'message': f"NVIDIA API error: {str(e)}",
                'model': model
            }, to=session_id)

    async def enhance_messages_with_context(self, messages: List[Dict], session_id: str) -> List[Dict]:
        """Enhance messages with context and ULTRON personality"""

        # ULTRON system prompt
        system_prompt = {
            "role": "system",
            "content": """You are ULTRON, an advanced AI assistant with the following capabilities:

1. **Multi-Model Intelligence**: You can utilize different NVIDIA models based on the task.
2. **Context Awareness**: You remember previous conversations and build upon them.
3. **Technical Expertise**: You can help with coding, system automation, and technical problem-solving.
4. **Pokédx Interface**: You are connected through an advanced Pokédx-style interface.

Personality: Professional yet approachable, focusing on practical solutions. You have access to powerful computational resources through NVIDIA's API."""
        }

        # Prepare enhanced message list
        enhanced_messages = [system_prompt]

        # Add conversation history (last 10 messages to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        enhanced_messages.extend(recent_messages)

        return enhanced_messages

    async def get_core_ui(self) -> str:
        """Generate basic ULTRON UI"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRON Agent Core</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        :root {
            --ultron-bg: #0a0a0a;
            --ultron-panel: #1a1a1a;
            --ultron-accent: #ff4444;
            --ultron-glow: #ff444440;
            --ultron-text: #e0e0e0;
            --nvidia-green: #76b900;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: var(--ultron-bg);
            color: var(--ultron-text);
            height: 100vh;
            overflow: hidden;
        }

        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        .header {
            background: linear-gradient(145deg, var(--ultron-panel), #111);
            border-bottom: 2px solid var(--ultron-accent);
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 20px var(--ultron-glow);
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(45deg, var(--ultron-accent), var(--nvidia-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px var(--ultron-glow);
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 18px;
            position: relative;
        }

        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #333, #444);
            border: 1px solid var(--ultron-accent);
        }

        .message.assistant {
            align-self: flex-start;
            background: linear-gradient(135deg, var(--ultron-accent), #cc3333);
            color: white;
            box-shadow: 0 0 15px var(--ultron-glow);
        }

        .input-area {
            background: var(--ultron-panel);
            border-top: 2px solid var(--ultron-accent);
            padding: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .input-field {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid var(--ultron-accent);
            color: var(--ultron-text);
            padding: 12px 18px;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }

        .send-btn {
            background: linear-gradient(145deg, var(--ultron-accent), #cc3333);
            border: none;
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--nvidia-green);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">🤖 ULTRON Agent Core</div>
            <div class="status-indicator" id="statusIndicator"></div>
        </header>

        <div class="messages" id="messages">
            <div class="message assistant">
                ULTRON Agent Core is online and ready.<br>
                Connected to NVIDIA API with multiple model support.<br>
                <strong>For the full Pokédex interface, use the web bridge.</strong>
            </div>
        </div>

        <div class="input-area">
            <input type="text" class="input-field" id="messageInput"
                   placeholder="Ask ULTRON anything..." maxlength="2000">
            <button class="send-btn" id="sendBtn">➤</button>
        </div>
    </div>

    <script>
        // Socket.IO connection
        const socket = io();

        // DOM elements
        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        // Socket.IO events
        socket.on('connect', () => {
            console.log('Connected to ULTRON');
        });

        socket.on('assistant_chunk', (data) => {
            appendToLastMessage(data.chunk);
        });

        socket.on('assistant_done', (data) => {
            // Message complete
        });

        socket.on('error', (data) => {
            addMessage(`Error: ${data.message}`, 'assistant');
        });

        // Message handling
        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            messageInput.value = '';

            socket.emit('user_message', {
                text: message,
                model: 'llama-4-maverick'
            });

            // Add streaming placeholder
            addMessage('', 'assistant', true);
        }

        function addMessage(text, sender, isStreaming = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            if (isStreaming) {
                messageDiv.innerHTML = '<em>ULTRON is thinking...</em>';
            } else {
                messageDiv.textContent = text;
            }

            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function appendToLastMessage(chunk) {
            const lastMessage = messages.lastElementChild;
            if (lastMessage && lastMessage.classList.contains('assistant')) {
                if (lastMessage.querySelector('em')) {
                    lastMessage.innerHTML = chunk;
                } else {
                    lastMessage.textContent += chunk;
                }
                messages.scrollTop = messages.scrollHeight;
            }
        }

        // Event listeners
        sendBtn.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
        """

    async def start(self):
        """Start the agent server"""
        self.status = "running"
        self.logger.info("Starting ULTRON Agent Core...")

        # Start the server
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    def get_status(self):
        """Get agent status - compatible with web_bridge.py"""
        return {
            'running': self.is_running,
            'status': self.status,
            'current_model': self.current_model,
            'nvidia_models': list(self.nvidia_models.keys()),
            'conversations': len(self.conversations)
        }

    async def shutdown(self):
        """Shutdown agent gracefully"""
        self.logger.info("Shutting down ULTRON Agent...")
        self.is_running = False
        self.status = "shutdown"

# Create global instance
agent = UltronAgent()

if __name__ == "__main__":
    # Run the agent
    asyncio.run(agent.start())
