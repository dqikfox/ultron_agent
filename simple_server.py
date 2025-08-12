#!/usr/bin/env python3
"""
Simple ULTRON Agent Web Server
"""

import asyncio
import json
import subprocess
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="ULTRON Agent Web Server")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

manager = ConnectionManager()

async def execute_git_command(command: str) -> str:
    """Execute git command and return output"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=30
        )
        
        if result.returncode == 0:
            return f"✅ {command}\n{result.stdout}" if result.stdout else f"✅ {command} completed successfully"
        else:
            return f"❌ {command}\nError: {result.stderr}"
    except subprocess.TimeoutExpired:
        return f"⏰ {command} timed out"
    except Exception as e:
        return f"❌ {command}\nException: {str(e)}"

async def handle_message(message: str, websocket: WebSocket):
    """Process incoming messages from the web client"""
    try:
        # Try to parse as JSON first (for structured commands)
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'git_command':
                command = data.get('command')
                logger.info(f"Executing git command: {command}")
                result = await execute_git_command(command)
                await manager.send_personal_message(result, websocket)
                return
                
            elif message_type == 'settings':
                settings = data.get('data')
                logger.info(f"Settings updated: {settings}")
                await manager.send_personal_message(f"Settings applied: {json.dumps(settings, indent=2)}", websocket)
                return
                
            elif message_type == 'invoke_tool':
                tool = data.get('tool')
                logger.info(f"Tool invoked: {tool}")
                await manager.send_personal_message(f"Executing tool: {tool}...", websocket)
                return
                
        except json.JSONDecodeError:
            # Not JSON, treat as plain text command
            pass
        
        # Handle plain text commands
        logger.info(f"Processing text command: {message}")
        
        # Try to load and use ULTRON Agent
        try:
            from agent_core import UltronAgent
            from config import Config
            
            # Try to initialize agent for this request
            config = Config()
            agent = UltronAgent(config)
            response = agent.handle_text(message)
            
        except Exception as e:
            logger.warning(f"Could not use ULTRON Agent: {e}")
            # Fallback responses
            if "status" in message.lower():
                response = "🤖 ULTRON Agent Status: Online (Web Interface)\n✅ WebSocket: Connected\n⚠️ Full Agent: Not loaded"
            elif "help" in message.lower():
                response = """🤖 ULTRON Agent Web Interface Help:
• Git operations: Use buttons in left panel
• Chat: Type messages here
• Keyboard shortcuts: Ctrl+Enter (send), Alt+G (git status), Alt+P (push)
• Note: Full AI features require ULTRON Agent to be properly configured"""
            elif "hello" in message.lower():
                response = "🤖 Hello! ULTRON Web Interface is ready. Type 'help' for commands or 'status' for system info."
            else:
                response = f"🤖 Received: '{message}'\n📝 Full ULTRON Agent not available. Basic web interface working."
        
        await manager.send_personal_message(response, websocket)
        
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        logger.error(error_msg)
        await manager.send_personal_message(error_msg, websocket)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await handle_message(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Serve the HTML file
@app.get("/")
async def get_index():
    return FileResponse("index.html", media_type="text/html")

# Serve static files
@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files"""
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ULTRON Agent Web Server"}

if __name__ == "__main__":
    print("🤖 Starting ULTRON Agent Web Server...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("🌐 Web interface: http://localhost:8000")
    print("⚡ Git operations and chat ready!")
    print("🎤 Accessibility features enabled")
    print("-" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
