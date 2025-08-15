#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Web API Server
Powers the beautiful web-based GUI with full agent integration
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psutil

# Import ULTRON components
try:
    from agent_core import UltronAgent
    from security_utils import sanitize_log_input
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent components not available: {e} - ultron_web_api.py:29")
    AGENT_AVAILABLE = False

# GPU monitoring
try:
    import pynvml
    GPU_AVAILABLE = True
    pynvml.nvmlInit()
except ImportError:
    GPU_AVAILABLE = False

class UltronWebAPI:
    """
    Complete Web API for ULTRON Agent with WebSocket support
    """

    def __init__(self):
        # Setup logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.app = FastAPI(title="ULTRON Agent 3.0 API", version="3.0.0")
        self.agent = None
        self.connected_clients = set()
        self.system_monitor_active = False
        self.setup_cors()
        self.setup_routes()
        self.setup_static_files()
        self.initialize_agent()

    def setup_cors(self):
        """Setup CORS for web interface"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_static_files(self):
        """Setup static file serving for web GUI"""
        web_gui_path = Path("web_gui")
        if web_gui_path.exists():
            self.app.mount("/", StaticFiles(directory="web_gui", html=True), name="static")

    def initialize_agent(self):
        """Initialize ULTRON Agent if available"""
        if AGENT_AVAILABLE:
            try:
                # Set use_gui to False temporarily for web API
                import os
                os.environ["ULTRON_USE_GUI"] = "false"
                
                # Initialize agent
                self.agent = UltronAgent()
                
                # Make sure GUI is disabled
                if hasattr(self.agent, 'gui'):
                    self.agent.gui = None
                if hasattr(self.agent, 'gui_thread'):
                    self.agent.gui_thread = None
                
                self.logger.info("ULTRON Agent initialized successfully for web API")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent: {e}")
                self.agent = None
        else:
            self.logger.warning("Agent components not available - running in demo mode")

    def setup_routes(self):
        """Setup all API routes"""

        # WebSocket endpoint for real-time communication
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.connected_clients.add(websocket)
            self.logger.info(f"Client connected. Total: {len(self.connected_clients)}")

            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    response = await self.handle_websocket_message(message)
                    await websocket.send_text(json.dumps(response))
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
                self.logger.info(f"Client disconnected. Total: {len(self.connected_clients)}")

    async def handle_websocket_message(self, message):
        """Handle WebSocket messages from clients"""
        msg_type = message.get('type', 'unknown')
        
        if msg_type == 'command':
            command = message.get('data', {}).get('command', '').strip()
            if not command:
                return {"type": "error", "message": "Command is required"}

            if not self.agent:
                return {
                    "type": "response",
                    "data": {
                        "success": False,
                        "response": "🤖 Agent not available - running in demo mode",
                        "command": command
                    }
                }

            try:
                # Execute command through agent
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.agent.process_command, command
                )

                return {
                    "type": "response",
                    "data": {
                        "success": True,
                        "response": response,
                        "command": command
                    }
                }

            except Exception as e:
                self.logger.error(f"WebSocket command execution failed: {e}")
                return {
                    "type": "response",
                    "data": {
                        "success": False,
                        "response": f"Error executing command: {str(e)}",
                        "command": command
                    }
                }
        
        elif msg_type == 'system_stats':
            stats = await self.get_system_stats()
            return {"type": "system_stats", "data": stats}
            
        else:
            return {"type": "error", "message": f"Unknown message type: {msg_type}"}
        @self.app.get("/api/status")
        async def get_status():
            """Get system and agent status"""
            return {
                "status": "online",
                "agent_available": self.agent is not None,
                "agent_status": getattr(self.agent, 'status', 'unknown') if self.agent else 'unavailable',
                "system": await self.get_system_stats(),
                "timestamp": time.time()
            }

        @self.app.post("/api/command")
        async def execute_command(request: dict):
            """Execute a command through the agent"""
            command = request.get('command', '').strip()
            if not command:
                raise HTTPException(status_code=400, detail="Command is required")

            if not self.agent:
                return {
                    "success": False,
                    "response": "Agent not available - running in demo mode",
                    "command": command,
                    "timestamp": time.time()
                }

            try:
                # Execute command through agent
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.agent.process_command, command
                )

                return {
                    "success": True,
                    "response": response,
                    "command": command,
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Command execution failed: {e}")
                return {
                    "success": False,
                    "response": f"Error executing command: {str(e)}",
                    "command": command,
                    "timestamp": time.time()
                }

        @self.app.get("/api/system")
        async def get_system_info():
            """Get detailed system information"""
            return await self.get_system_stats()

        @self.app.get("/api/tools")
        async def get_tools():
            """Get available agent tools"""
            if not self.agent:
                return {"tools": [], "count": 0}

            try:
                tools = self.agent.list_tools() if hasattr(self.agent, 'list_tools') else []
                return {
                    "tools": tools,
                    "count": len(tools),
                    "timestamp": time.time()
                }
            except Exception as e:
                self.logger.error(f"Error getting tools: {e}")
                return {"tools": [], "count": 0, "error": str(e)}

        @self.app.post("/api/voice/toggle")
        async def toggle_voice():
            """Toggle voice listening mode"""
            if not self.agent or not hasattr(self.agent, 'voice'):
                return {"success": False, "message": "Voice system not available"}

            # This would integrate with the voice system
            return {
                "success": True,
                "listening": False,  # Would be actual state
                "message": "Voice toggle functionality ready"
            }

        @self.app.get("/api/memory")
        async def get_memory():
            """Get agent memory information"""
            if not self.agent or not hasattr(self.agent, 'memory'):
                return {"short_term": [], "long_term": [], "count": 0}

            try:
                memory = self.agent.memory
                return {
                    "short_term": getattr(memory, 'short_term', []),
                    "long_term": getattr(memory, 'long_term', []),
                    "count": len(getattr(memory, 'short_term', [])),
                    "timestamp": time.time()
                }
            except Exception as e:
                return {"error": str(e), "short_term": [], "long_term": [], "count": 0}

    async def handle_websocket_message(self, message: dict) -> dict:
        """Handle incoming WebSocket messages"""
        msg_type = message.get('type', 'unknown')

        if msg_type == 'command':
            command = message.get('data', {}).get('command', '')
            if self.agent:
                try:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, self.agent.process_command, command
                    )
                    return {
                        "type": "command_response",
                        "success": True,
                        "data": {"response": response, "command": command},
                        "timestamp": time.time()
                    }
                except Exception as e:
                    return {
                        "type": "command_response",
                        "success": False,
                        "data": {"error": str(e), "command": command},
                        "timestamp": time.time()
                    }
            else:
                return {
                    "type": "command_response",
                    "success": False,
                    "data": {"error": "Agent not available", "command": command},
                    "timestamp": time.time()
                }

        elif msg_type == 'system_request':
            stats = await self.get_system_stats()
            return {
                "type": "system_data",
                "data": stats,
                "timestamp": time.time()
            }

        elif msg_type == 'ping':
            return {
                "type": "pong",
                "timestamp": time.time()
            }

        else:
            return {
                "type": "error",
                "data": {"message": f"Unknown message type: {msg_type}"},
                "timestamp": time.time()
            }

    async def get_system_stats(self) -> dict:
        """Get comprehensive system statistics"""
        stats = {
            "cpu": {
                "usage": psutil.cpu_percent(interval=0.1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "usage": psutil.virtual_memory().percent,
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                "total": psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total,
                "free": psutil.disk_usage('/').free if os.name != 'nt' else psutil.disk_usage('C:').free
            },
            "network": {
                "status": "connected",
                "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
            },
            "agent": {
                "status": getattr(self.agent, 'status', 'unknown') if self.agent else 'unavailable',
                "components": self.get_agent_component_status(),
                "tools_count": len(self.agent.tools) if self.agent and hasattr(self.agent, 'tools') else 0
            }
        }

        # Add GPU stats if available
        if GPU_AVAILABLE:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                gpu_stats = []

                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')

                    gpu_stats.append({
                        "id": i,
                        "name": name,
                        "memory_usage": (mem_info.used / mem_info.total) * 100,
                        "memory_total": mem_info.total,
                        "memory_used": mem_info.used,
                        "temperature": temp
                    })

                stats["gpu"] = gpu_stats

            except Exception as e:
                stats["gpu"] = {"error": str(e)}
        else:
            stats["gpu"] = {"available": False}

        return stats

    def get_agent_component_status(self) -> dict:
        """Get status of agent components"""
        if not self.agent:
            return {}

        components = {}

        # Check each component
        for component_name in ['brain', 'voice', 'memory', 'vision', 'tools']:
            if hasattr(self.agent, component_name):
                component = getattr(self.agent, component_name)
                components[component_name] = {
                    "available": component is not None,
                    "status": "online" if component else "offline"
                }

                # Additional component-specific info
                if component_name == 'tools' and component:
                    components[component_name]["count"] = len(component)
                elif component_name == 'memory' and component:
                    components[component_name]["short_term_count"] = len(getattr(component, 'short_term', []))
            else:
                components[component_name] = {"available": False, "status": "not_loaded"}

        return components

    async def broadcast_to_clients(self, message: dict):
        """Broadcast message to all connected WebSocket clients"""
        if not self.connected_clients:
            return

        disconnected = []
        for client in self.connected_clients:
            try:
                await client.send_text(json.dumps(message))
            except Exception:
                disconnected.append(client)

        # Remove disconnected clients
        for client in disconnected:
            self.connected_clients.discard(client)

    def start_system_monitoring(self):
        """Start background system monitoring"""
        if self.system_monitor_active:
            return

        self.system_monitor_active = True

        async def monitor_loop():
            while self.system_monitor_active:
                try:
                    stats = await self.get_system_stats()
                    await self.broadcast_to_clients({
                        "type": "system_update",
                        "data": stats,
                        "timestamp": time.time()
                    })
                    await asyncio.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    self.logger.error(f"System monitoring error: {e}")
                    await asyncio.sleep(5)

        # Start monitoring in background
        asyncio.create_task(monitor_loop())
        self.logger.info("System monitoring started")

    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the web API server"""
        self.logger.info(f"🚀 Starting ULTRON Web API server on {host}:{port}")
        self.logger.info(f"🌐 Web interface available at: http://{host}:{port}")

        # Start system monitoring
        self.start_system_monitoring()

        # Run the server
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )


# Factory function
def create_ultron_web_api() -> UltronWebAPI:
    """Create and return UltronWebAPI instance"""
    return UltronWebAPI()


# Main entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON Agent 3.0 Web API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")

    args = parser.parse_args()

    # Create and run the API server
    api = create_ultron_web_api()
    api.run(host=args.host, port=args.port)
