"""
ULTRON Agent 3.0 - Modernized Agent Core
Main agent integration and orchestration using the new modular structure
"""
from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import socketio
import uvicorn

from . import (
    UltronConfig, get_config, setup_logging, get_logger,
    UltronError, ErrorCategory, ErrorSeverity
)
from .ai import UltronBrain, OllamaManager
from .interfaces import VoiceManager, VisionManager 
from .storage import Memory

logger = get_logger("ultron.agent_core", source="agent")


class ModernUltronAgent:
    """
    Modernized ULTRON Agent using the new modular architecture.
    
    This class orchestrates all components using the new package structure
    with proper type safety and error handling.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize the modern ULTRON agent with enhanced modularity."""
        # Load configuration
        self.config = get_config() if not config_path else UltronConfig.from_file(config_path)
        
        # Setup logging
        setup_logging(self.config.log_level.value)
        logger.info("🤖 Modern ULTRON Agent initializing...")

        # Initialize core components
        self.brain: Optional[UltronBrain] = None
        self.ollama_manager: Optional[OllamaManager] = None
        self.voice_manager: Optional[VoiceManager] = None
        self.vision_manager: Optional[VisionManager] = None
        self.memory: Optional[Memory] = None
        
        # Agent state
        self.status = "initializing"
        self.is_running = False
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.error_counts: Dict[str, int] = {}
        self.click_counts: Dict[str, int] = {}
        
        # Web components
        self.app: Optional[FastAPI] = None
        self.sio: Optional[socketio.AsyncServer] = None
        
        # Initialize all components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize all agent components with error handling."""
        try:
            # Initialize storage components
            logger.info("🧠 Initializing memory...")
            self.memory = Memory(
                short_term_limit=self.config.memory_short_term_limit if hasattr(self.config, 'memory_short_term_limit') else 10
            )
            
            # Initialize AI components
            logger.info("🤖 Initializing AI components...")
            self.ollama_manager = OllamaManager(self.config)
            
            # Initialize brain with tools and memory
            self.brain = UltronBrain(self.config, tools=None, memory=self.memory)
            
            # Initialize interface components
            if self.config.use_voice:
                logger.info("🔊 Initializing voice manager...")
                self.voice_manager = VoiceManager(self.config)
            
            if self.config.use_vision:
                logger.info("👁️ Initializing vision manager...")
                self.vision_manager = VisionManager(self.config)
            
            # Initialize web components if API is enabled
            if self.config.use_api:
                logger.info("🌐 Initializing web components...")
                self._setup_web_components()
            
            self.status = "ready"
            logger.info("✅ Modern ULTRON Agent initialization complete")
            
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ Agent initialization failed: {e}")
            logger.error(traceback.format_exc())
            raise UltronError(
                f"Agent initialization failed: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                recovery_suggestion="Check configuration and dependencies",
                original_error=e
            )

    def _setup_web_components(self) -> None:
        """Setup FastAPI and Socket.IO components."""
        # Initialize Socket.IO
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins="*"
        )
        
        # Initialize FastAPI
        self.app = FastAPI(
            title="ULTRON Agent 3.0",
            description="Modern AI Agent with Enhanced Modularity",
            version="3.0.0"
        )
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio_events()
        
        # Combine with Socket.IO
        self.app = socketio.ASGIApp(self.sio, other_asgi_app=self.app)

    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        if not self.app:
            return

        @self.app.get("/", response_class=HTMLResponse)
        async def get_home() -> str:
            """Home route with agent interface."""
            logger.info("🏠 Home route accessed")
            return await self._get_agent_ui()

        @self.app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """Health check endpoint."""
            logger.info("❤️ Health check requested")
            try:
                health_data: Dict[str, Any] = {
                    "status": self.status,
                    "timestamp": datetime.now().isoformat(),
                    "version": "3.0.0",
                    "components": {
                        "brain": self.brain is not None,
                        "ollama": self.ollama_manager is not None and self.ollama_manager.is_connected,
                        "voice": self.voice_manager is not None,
                        "vision": self.vision_manager is not None,
                        "memory": self.memory is not None
                    },
                    "conversations": len(self.conversations),
                    "memory_stats": self.memory.get_memory_stats() if self.memory else {}
                }
                
                if self.ollama_manager:
                    health_data["ollama"] = self.ollama_manager.get_status()
                
                logger.info("📊 Health check completed")
                return health_data
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return {"status": "error", "message": str(e)}

        @self.app.get("/status")
        async def get_status() -> Dict[str, Any]:
            """Detailed status endpoint."""
            logger.info("📈 Status endpoint accessed")
            return await self._get_detailed_status()

        @self.app.post("/chat")
        async def chat_endpoint(request: Request) -> Dict[str, Any]:
            """Chat with the agent."""
            try:
                data = await request.json()
                message = data.get("message", "")
                
                if not message:
                    return {"error": "No message provided"}
                
                response = await self.process_message(message)
                return {"response": response}
                
            except Exception as e:
                logger.error(f"Chat endpoint error: {e}")
                return {"error": str(e)}

        @self.app.post("/track-click")
        async def track_click(request: Request) -> Dict[str, Any]:
            """Track UI interactions for analytics."""
            try:
                data = await request.json()
                element = data.get('element', 'unknown')
                self.click_counts[element] = self.click_counts.get(element, 0) + 1
                logger.info(f"🖱️ Click tracked: {element} (count: {self.click_counts[element]})")
                return {"success": True, "count": self.click_counts[element]}
            except Exception as e:
                logger.error(f"Click tracking failed: {e}")
                return {"success": False, "error": str(e)}

    def _setup_socketio_events(self) -> None:
        """Setup Socket.IO event handlers."""
        if not self.sio:
            return

        @self.sio.event
        async def connect(sid: str, environ: Dict[str, Any]) -> None:
            """Handle client connection."""
            logger.info(f"🔗 Client connected: {sid}")

        @self.sio.event
        async def disconnect(sid: str) -> None:
            """Handle client disconnection."""
            logger.info(f"📡 Client disconnected: {sid}")

        @self.sio.event
        async def message(sid: str, data: Dict[str, Any]) -> None:
            """Handle incoming messages."""
            try:
                user_message = data.get('message', '')
                if user_message:
                    response = await self.process_message(user_message)
                    await self.sio.emit('response', {'message': response}, room=sid)
            except Exception as e:
                logger.error(f"Socket.IO message error: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)

    async def process_message(self, message: str, session_id: Optional[str] = None) -> str:
        """
        Process a user message through the agent pipeline.
        
        Args:
            message: User input message
            session_id: Optional session identifier
            
        Returns:
            Agent response
        """
        try:
            logger.info(f"💬 Processing message: {message[:50]}...")
            
            # Store in memory
            if self.memory:
                self.memory.add_to_short_term({
                    "type": "user_input",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Store conversation
            if session_id:
                if session_id not in self.conversations:
                    self.conversations[session_id] = []
                self.conversations[session_id].append({
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Process through brain
            if self.brain:
                response = await self.brain.think(message)
            else:
                response = "Agent brain not initialized"
            
            # Store response in memory and conversation
            if self.memory:
                self.memory.add_to_short_term({
                    "type": "agent_response",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
            
            if session_id and session_id in self.conversations:
                self.conversations[session_id].append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Speak response if voice is enabled
            if self.voice_manager and self.config.use_voice:
                try:
                    await self.voice_manager.speak(response)
                except Exception as e:
                    logger.warning(f"Voice output failed: {e}")
            
            logger.info("✅ Message processed successfully")
            return response
            
        except UltronError:
            raise  # Re-raise UltronErrors
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(traceback.format_exc())
            raise UltronError(
                f"Message processing failed: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                original_error=e
            )

    async def _get_agent_ui(self) -> str:
        """Generate the agent UI HTML."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ULTRON Agent 3.0</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { background: #333; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .chat { background: #222; padding: 20px; border-radius: 10px; }
                input, button { padding: 10px; margin: 10px 0; font-size: 16px; }
                button { background: #007acc; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #005aa7; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 ULTRON Agent 3.0</h1>
                <div class="status">
                    <h3>Status: """ + self.status + """</h3>
                    <p>Modern AI Agent with Enhanced Modularity</p>
                </div>
                <div class="chat">
                    <h3>Chat Interface</h3>
                    <div id="messages"></div>
                    <input type="text" id="messageInput" placeholder="Type your message..." style="width: 70%;">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            <script src="/socket.io/socket.io.js"></script>
            <script>
                const socket = io();
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    if (input.value.trim()) {
                        socket.emit('message', {message: input.value});
                        addMessage('You: ' + input.value);
                        input.value = '';
                    }
                }
                socket.on('response', function(data) {
                    addMessage('ULTRON: ' + data.message);
                });
                function addMessage(message) {
                    const messages = document.getElementById('messages');
                    const div = document.createElement('div');
                    div.innerHTML = message;
                    div.style.margin = '10px 0';
                    messages.appendChild(div);
                    messages.scrollTop = messages.scrollHeight;
                }
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendMessage();
                });
            </script>
        </body>
        </html>
        """

    async def _get_detailed_status(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        status_data = {
            "agent": {
                "status": self.status,
                "version": "3.0.0",
                "uptime": datetime.now().isoformat(),
                "is_running": self.is_running
            },
            "components": {},
            "statistics": {
                "conversations": len(self.conversations),
                "total_messages": sum(len(conv) for conv in self.conversations.values()),
                "click_counts": self.click_counts,
                "error_counts": self.error_counts
            }
        }
        
        # Component status
        if self.ollama_manager:
            status_data["components"]["ollama"] = self.ollama_manager.get_status()
        
        if self.voice_manager:
            status_data["components"]["voice"] = self.voice_manager.get_status()
        
        if self.vision_manager:
            status_data["components"]["vision"] = self.vision_manager.get_status()
        
        if self.memory:
            status_data["components"]["memory"] = self.memory.get_memory_stats()
        
        if self.brain:
            status_data["components"]["brain"] = self.brain.get_cache_stats()
        
        return status_data

    async def run_server(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the agent server."""
        if not self.app:
            raise UltronError(
                "Web components not initialized",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Enable API in configuration"
            )
        
        logger.info(f"🚀 Starting ULTRON Agent server on {host}:{port}")
        self.is_running = True
        
        try:
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
        except Exception as e:
            logger.error(f"Server error: {e}")
            self.is_running = False
            raise

    def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        logger.info("🛑 Shutting down ULTRON Agent...")
        
        try:
            if self.voice_manager:
                self.voice_manager.stop_voice()
            
            if self.memory:
                self.memory.save_long_term_memory()
            
            self.is_running = False
            self.status = "shutdown"
            logger.info("✅ ULTRON Agent shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Backward compatibility - expose the old class name
UltronAgent = ModernUltronAgent