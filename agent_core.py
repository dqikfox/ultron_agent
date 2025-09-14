"""
ULTRON Agent Core System
Main agent initialization and core functionality
Following copilot instructions architecture patterns.
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

# MANDATORY: Use centralized logging system per copilot instructions
from utils.ultron_logger import log_info, log_error, log_ai_decision, log_file_operation
from utils.model_awareness import should_modify_file, check_file_context

class UltronAgent:
    """Core ULTRON agent with essential functionality"""

    def __init__(self):
        # Initialize using centralized logging per copilot instructions
        log_info("agent_core", "ULTRON Agent Core initializing...")

        # NVIDIA API Configuration
        self.nvidia_api_keys = [
            "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",
            "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"
        ]
        self.current_api_key = self.nvidia_api_keys[0]
        log_info("agent_core", f"NVIDIA API configured with {len(self.nvidia_api_keys)} keys")

        # NVIDIA Model Configuration
        self.nvidia_models = {
            "llama-4-maverick": "meta/llama-4-maverick-17b-128e-instruct",
            "gpt-oss-120b": "openai/gpt-oss-120b",
            "llama-3.3-70b": "meta/llama-3.3-70b-instruct"
        }
        self.current_model = "llama-4-maverick"
        log_info("agent_core", f"Models available: {list(self.nvidia_models.keys())}")

        # FastAPI + Socket.IO Setup
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
        self.app = FastAPI(title="ULTRON Agent Core")
        log_info("agent_core", "FastAPI and Socket.IO initialized")

        # Setup routes and Socket.IO events
        self.setup_routes()
        self.setup_socketio_events()

        # Core agent state
        self.conversations: Dict[str, List[Dict]] = {}
        self.status = "initialized"
        self.is_running = False
        self.click_counts = {}  # Track UI interactions
        self.error_counts = {}  # Track error frequency

        # Combine with Socket.IO
        self.app = socketio.ASGIApp(self.sio, other_asgi_app=self.app)
        log_info("agent_core", "ULTRON Agent Core initialization complete")

    async def initialize(self):
        """Initialize agent - required by web_bridge.py"""
        log_info("agent_core", "ULTRON Agent initialize() called by web bridge")
        try:
            self.is_running = True
            self.status = "running"
            log_info("agent_core", "ULTRON Agent fully initialized and ready")
            return True
        except Exception as e:
            log_error("agent_core", f"Agent initialization failed: {e}", error=e)
            return False

    def setup_routes(self):
        """Setup FastAPI routes for the core agent"""
        log_info("agent_core", "Setting up FastAPI routes...")

        @self.app.get("/")
        async def get_home():
            log_info("agent_core", "Home route accessed")
            return await self.get_core_ui()

        @self.app.get("/health")
        async def health_check():
            log_info("agent_core", "Health check requested")
            health_data = {
                "status": "operational",
                "current_model": self.current_model,
                "nvidia_models": list(self.nvidia_models.keys()),
                "api_status": "active",
                "conversations": len(self.conversations),
                "uptime": datetime.now().isoformat()
            }
            log_info("agent_core", f"Health data generated with {len(self.conversations)} conversations")
            return health_data

        @self.app.get("/status")
        async def get_status():
            log_info("agent_core", "Status endpoint accessed")
            status_data = self.get_status()
            return status_data

        # Add click tracking endpoint
        @self.app.post("/track-click")
        async def track_click(request: Request):
            data = await request.json()
            element = data.get('element', 'unknown')
            self.click_counts[element] = self.click_counts.get(element, 0) + 1
            log_info("agent_core", f"Click tracked: {element} (count: {self.click_counts[element]})")
            return {"success": True, "count": self.click_counts[element]}

        # Add GUI logging endpoint per copilot instructions
        @self.app.post("/api/log")
        async def gui_log(request: Request):
            """Handle GUI logging requests and integrate with centralized logging"""
            try:
                data = await request.json()
                event_type = data.get('eventType', 'gui_event')
                element_id = data.get('elementId', 'unknown')
                element_class = data.get('elementClass', 'unknown')
                details = data.get('details', {})
                timestamp = data.get('timestamp', datetime.now().isoformat())
                
                # Log GUI interaction using centralized system
                log_info("gui", f"GUI Event: {event_type} on {element_id}", 
                        event_type=event_type, element_id=element_id, 
                        element_class=element_class, details=details, timestamp=timestamp)
                
                return {"success": True, "logged": True}
            except Exception as e:
                log_error("gui", f"Failed to process GUI log: {e}", error=e)
                return {"success": False, "error": str(e)}

        log_info("agent_core", "FastAPI routes configured")

    def setup_socketio_events(self):
        """Setup Socket.IO event handlers for real-time communication"""
        log_info("agent_core", "Setting up Socket.IO events...")

        @self.sio.event
        async def connect(sid, environ):
            log_info("agent_core", f"Client connected: {sid}")
            await self.sio.emit('connection_established', {
                'session_id': sid,
                'status': 'connected',
                'server_time': datetime.now().isoformat()
            }, to=sid)

        @self.sio.event
        async def disconnect(sid):
            log_info("agent_core", f"Client disconnected: {sid}")

        @self.sio.event
        async def user_message(sid, data):
            """Handle user messages and route to appropriate model"""
            log_info("agent_core", f"Message from {sid}: {data}")
            try:
                user_text = data.get('text', '').strip()
                model_preference = data.get('model', self.current_model)

                if not user_text:
                    log_error("agent_core", f"Empty message received from {sid}")
                    return

                # Initialize conversation history
                if sid not in self.conversations:
                    self.conversations[sid] = []
                    log_info("agent_core", f"New conversation started for {sid}")

                # Add user message to history
                self.conversations[sid].append({
                    "role": "user",
                    "content": user_text,
                    "timestamp": datetime.now().isoformat()
                })

                log_ai_decision("agent_core", f"Processing with model: {model_preference}", 
                               ai_model=model_preference, confidence_score=0.9)

                # Process with selected model
                await self.process_user_message(sid, user_text, model_preference)

            except Exception as e:
                self.error_counts['user_message'] = self.error_counts.get('user_message', 0) + 1
                log_error("agent_core", f"Error processing user message (error #{self.error_counts['user_message']}): {e}", 
                         error=e)
                await self.sio.emit('error', {
                    'message': f"Error processing request: {str(e)}",
                    'error_count': self.error_counts['user_message']
                }, to=sid)

        # Add ping/pong for connection health
        @self.sio.event
        async def ping(sid, data):
            log_info("agent_core", f"Ping from {sid}", session_id=sid)
            await self.sio.emit('pong', {'timestamp': datetime.now().isoformat()}, to=sid)

        log_info("agent_core", "Socket.IO events configured")

    async def process_user_message(self, session_id: str, user_text: str, model: str):
        """Process user message with NVIDIA models"""
        self.logger.info(f"🔄 Processing message for {session_id} with model {model}")
        try:
            # Performance tracking
            start_time = datetime.now()

            # Get conversation history
            messages = self.conversations.get(session_id, [])
            self.logger.info(f"📚 Conversation history: {len(messages)} messages")

            # Prepare NVIDIA API request
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.current_api_key
            )

            model_id = self.nvidia_models.get(model, self.nvidia_models[self.current_model])
            self.logger.info(f"🎯 Using model ID: {model_id}")

            # Enhanced prompt with context awareness
            enhanced_messages = await self.enhance_messages_with_context(messages, session_id)
            self.logger.info(f"💭 Enhanced messages prepared: {len(enhanced_messages)} total")

            # Stream response
            self.logger.info("📡 Starting NVIDIA API stream...")
            completion = client.chat.completions.create(
                model=model_id,
                messages=enhanced_messages,
                temperature=0.7,
                top_p=0.9,
                max_tokens=2048,
                stream=True
            )

            assistant_response = ""
            chunk_count = 0
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_response += content
                    chunk_count += 1

                    # Stream chunk to client
                    await self.sio.emit('assistant_chunk', {
                        'chunk': content,
                        'model': model,
                        'session_id': session_id,
                        'chunk_number': chunk_count
                    }, to=session_id)

            self.logger.info(f"✅ Streaming complete: {chunk_count} chunks, {len(assistant_response)} characters")

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

            self.logger.info(f"⏱️ Response time: {response_time:.2f}s")

            await self.sio.emit('assistant_done', {
                'response_time': response_time,
                'model_used': model,
                'message_length': len(assistant_response),
                'chunk_count': chunk_count
            }, to=session_id)

        except Exception as e:
            self.error_counts['nvidia_api'] = self.error_counts.get('nvidia_api', 0) + 1
            self.logger.error(f"❌ NVIDIA API error (error #{self.error_counts['nvidia_api']}): {e}")
            self.logger.error(traceback.format_exc())
            await self.sio.emit('error', {
                'message': f"NVIDIA API error: {str(e)}",
                'model': model,
                'error_count': self.error_counts['nvidia_api']
            }, to=session_id)

    async def enhance_messages_with_context(self, messages: List[Dict], session_id: str) -> List[Dict]:
        """Enhance messages with context and ULTRON personality"""
        self.logger.debug(f"🔧 Enhancing messages for session {session_id}")

        # ULTRON system prompt
        system_prompt = {
            "role": "system",
            "content": """You are ULTRON, an advanced AI assistant with the following capabilities:

1. **Multi-Model Intelligence**: You can utilize different NVIDIA models based on the task.
2. **Context Awareness**: You remember previous conversations and build upon them.
3. **Technical Expertise**: You can help with coding, system automation, and technical problem-solving.
4. **Pokédx Interface**: You are connected through an advanced Pokédx-style interface.

Personality: Professional yet approachable, focusing on practical solutions. You have access to powerful computational resources through NVIDIA's API.

Current session: """ + session_id
        }

        # Prepare enhanced message list
        enhanced_messages = [system_prompt]

        # Add conversation history (last 10 messages to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        enhanced_messages.extend(recent_messages)

        self.logger.debug(f"💭 Enhanced prompt: {len(enhanced_messages)} messages")
        return enhanced_messages

    async def get_core_ui(self) -> str:
        """Generate basic ULTRON UI with click tracking"""
        self.logger.info("🖥️ Generating core UI")
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

        .status-panel {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--nvidia-green);
            animation: pulse 2s infinite;
        }

        .nav-buttons {
            display: flex;
            gap: 10px;
        }

        .nav-btn {
            padding: 8px 16px;
            background: var(--ultron-panel);
            border: 1px solid var(--ultron-accent);
            color: var(--ultron-text);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .nav-btn:hover {
            background: var(--ultron-accent);
            transform: translateY(-2px);
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
            transition: transform 0.2s ease;
        }

        .send-btn:hover {
            transform: scale(1.1);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .debug-info {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            color: #0f0;
        }
    </style>
</head>
<body>
    <div class="debug-info" id="debugInfo">
        Connection: Initializing...<br>
        Clicks: <span id="clickCount">0</span><br>
        Messages: <span id="messageCount">0</span>
    </div>

    <div class="container">
        <header class="header">
            <div class="logo">🤖 ULTRON Agent Core</div>
            <div class="status-panel">
                <div class="nav-buttons">
                    <button class="nav-btn" onclick="trackClick('pokedex-gui')" data-action="pokedex">🎮 Pokédx GUI</button>
                    <button class="nav-btn" onclick="trackClick('health-check')" data-action="health">❤️ Health</button>
                    <button class="nav-btn" onclick="trackClick('bridge-test')" data-action="bridge">🌉 Bridge</button>
                </div>
                <div class="status-indicator" id="statusIndicator"></div>
            </div>
        </header>

        <div class="messages" id="messages">
            <div class="message assistant">
                🤖 ULTRON Agent Core is online and ready.<br>
                📡 Connected to NVIDIA API with multiple model support.<br>
                🎮 <strong>For the full Pokédex interface, use the web bridge.</strong><br>
                🔗 <strong>Bridge should be running at: <a href="/bridge" style="color: #76b900;">Web Bridge</a></strong>
            </div>
        </div>

        <div class="input-area">
            <input type="text" class="input-field" id="messageInput"
                   placeholder="Ask ULTRON anything..." maxlength="2000">
            <button class="send-btn" id="sendBtn" onclick="trackClick('send-message')">➤</button>
        </div>
    </div>

    <script>
        // Socket.IO connection with detailed logging
        const socket = io();
        let clickCount = 0;
        let messageCount = 0;

        // DOM elements
        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const debugInfo = document.getElementById('debugInfo');
        const statusIndicator = document.getElementById('statusIndicator');

        // Click tracking function
        function trackClick(element) {
            clickCount++;
            document.getElementById('clickCount').textContent = clickCount;

            fetch('/track-click', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({element: element})
            }).then(response => response.json())
            .then(data => {
                console.log(`Click tracked: ${element} (total: ${data.count})`);
            }).catch(error => {
                console.error('Click tracking failed:', error);
            });

            // Handle specific actions
            if (element === 'pokedex-gui') {
                window.open('/gui/ultron_enhanced/web/', '_blank');
            } else if (element === 'health-check') {
                fetch('/health').then(r => r.json()).then(data => {
                    addMessage(`Health: ${JSON.stringify(data, null, 2)}`, 'assistant');
                });
            } else if (element === 'bridge-test') {
                addMessage('Testing bridge connection...', 'assistant');
                // Test bridge functionality
            }
        }

        // Socket.IO events with logging
        socket.on('connect', () => {
            console.log('🔗 Connected to ULTRON');
            updateDebugInfo('Connected');
            statusIndicator.style.background = '#76b900';
        });

        socket.on('disconnect', () => {
            console.log('🔌 Disconnected from ULTRON');
            updateDebugInfo('Disconnected');
            statusIndicator.style.background = '#ff4444';
        });

        socket.on('connection_established', (data) => {
            console.log('✅ Connection established:', data);
            updateDebugInfo('Established');
        });

        socket.on('assistant_chunk', (data) => {
            appendToLastMessage(data.chunk);
            console.log(`📦 Chunk ${data.chunk_number} received`);
        });

        socket.on('assistant_done', (data) => {
            console.log('✅ Message complete:', data);
        });

        socket.on('error', (data) => {
            console.error('❌ Server error:', data);
            addMessage(`Error (${data.error_count}): ${data.message}`, 'assistant');
        });

        socket.on('pong', (data) => {
            console.log('🏓 Pong received:', data.timestamp);
        });

        function updateDebugInfo(status) {
            debugInfo.innerHTML = `
                Connection: ${status}<br>
                Clicks: <span id="clickCount">${clickCount}</span><br>
                Messages: <span id="messageCount">${messageCount}</span>
            `;
        }

        // Message handling with tracking
        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            messageCount++;
            trackClick('send-message');

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
                messageDiv.innerHTML = '<em>🤔 ULTRON is thinking...</em>';
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

        // Health check ping every 30 seconds
        setInterval(() => {
            socket.emit('ping', {timestamp: new Date().toISOString()});
        }, 30000);

        // Update debug info
        setInterval(() => {
            document.getElementById('clickCount').textContent = clickCount;
            document.getElementById('messageCount').textContent = messageCount;
        }, 1000);
    </script>
</body>
</html>
        """

    async def start(self):
        """Start the agent server"""
        self.status = "running"
        self.logger.info("🚀 Starting ULTRON Agent Core server...")

        try:
            # Start the server
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
            server = uvicorn.Server(config)
            self.logger.info("🌐 Server starting on http://localhost:8000")
            await server.serve()
        except Exception as e:
            self.logger.error(f"❌ Server start failed: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def get_status(self):
        """Get agent status - compatible with web_bridge.py"""
        status = {
            'running': self.is_running,
            'status': self.status,
            'current_model': self.current_model,
            'nvidia_models': list(self.nvidia_models.keys()),
            'conversations': len(self.conversations),
            'click_counts': self.click_counts,
            'error_counts': self.error_counts,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.debug(f"📊 Status requested: {status}")
        return status

    async def shutdown(self):
        """Shutdown agent gracefully"""
        self.logger.info("🛑 Shutting down ULTRON Agent...")
        self.is_running = False
        self.status = "shutdown"
        self.logger.info("✅ ULTRON Agent shutdown complete")

# Create global instance
agent = UltronAgent()

if __name__ == "__main__":
    # Run the agent
    asyncio.run(agent.start())
