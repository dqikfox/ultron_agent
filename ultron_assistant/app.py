# app.py
import asyncio
import json
import sys
import os
from pathlib import Path
import threading
import webbrowser
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import uvicorn
from pydantic import BaseModel

# Add parent directory to path to import from main project
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import local modules first
from ollama_client import ollama_chat, check_ollama_status
from automation import run_command

# Import voice from local directory to avoid conflicts with main project
sys.path.insert(0, str(Path(__file__).parent))
from voice import listen_once, Speaker
import speech_recognition as sr

# Try to import from main project if available
try:
    from config import Config
    from agent_core import UltronAgent
    from brain import UltronBrain
    MAIN_PROJECT_AVAILABLE = True
except ImportError:
    MAIN_PROJECT_AVAILABLE = False
    print("Warning: Main Ultron project not available, running in standalone mode - app.py:37")

# -------------------------------------------------
# FastAPI + Socket.IO Setup
# -------------------------------------------------
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
fastapi_app = FastAPI(title="Ultron Assistant", description="Advanced AI Assistant with Voice and Automation")

# Mount static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

fastapi_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Wrap with Socket.IO
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

# -------------------------------------------------
# Global objects
# -------------------------------------------------
speaker = Speaker()
recognizer = sr.Recognizer()
try:
    mic = sr.Microphone()
except OSError:
    print("Warning: No microphone detected, voice input disabled - app.py:65")
    mic = None

# Main project integration
ultron_agent = None
if MAIN_PROJECT_AVAILABLE:
    try:
        # Initialize without arguments as UltronAgent doesn't require them
        ultron_agent = UltronAgent()
    except Exception as e:
        print(f"Warning: Could not initialize main Ultron agent: {e} - app.py:75")

# Conversation history (in production, use Redis or database)
conversations = {}

# -------------------------------------------------
# Pydantic Models
# -------------------------------------------------
class UserMessage(BaseModel):
    text: str
    conversation_id: str = "default"

class VoiceRequest(BaseModel):
    timeout: int = 10

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
async def stream_response(messages, sid, conversation_id="default"):
    """Stream Ollama response to client."""
    try:
        # Store conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add system prompt to identify the model if not already present
        if not messages or messages[0].get("role") != "system":
            system_message = {
                "role": "system",
                "content": "You are Qwen2.5-VL, a multimodal AI assistant created by Alibaba Cloud. You can process both text and images. You are part of the Ultron Assistant system, providing intelligent responses with voice interaction capabilities. Always identify yourself as Qwen2.5-VL when asked about your identity."
            }
            messages = [system_message] + messages
        
        full_response = ""
        async for chunk in ollama_chat(messages):
            full_response += chunk
            await sio.emit('assistant_chunk', {'chunk': chunk}, to=sid)
        
        # Speak the response aloud
        if full_response.strip():
            speaker.say(full_response)
        
        # Store the complete response
        conversations[conversation_id].append({
            "role": "assistant", 
            "content": full_response
        })
        
        await sio.emit('assistant_done', {}, to=sid)
    except Exception as e:
        await sio.emit('error', {'message': f"Error: {str(e)}"}, to=sid)

def is_automation_command(text: str) -> bool:
    """Check if text is an automation command."""
    automation_triggers = [
        "open ", "type ", "search for ", "take screenshot", "screenshot",
        "volume up", "volume down", "click", "scroll", "press key"
    ]
    return any(text.lower().strip().startswith(trigger) for trigger in automation_triggers)

# -------------------------------------------------
# Socket.IO Events
# -------------------------------------------------
@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid} - app.py:130")
    await sio.emit('status', {'message': 'Connected to Ultron Assistant'}, to=sid)

@sio.event
async def user_message(sid, data):
    """Handle user message from WebSocket."""
    try:
        user_text = data.get('text', '').strip()
        conversation_id = data.get('conversation_id', 'default')
        
        if not user_text:
            return

        # Store user message in conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        conversations[conversation_id].append({"role": "user", "content": user_text})

        # Special commands
        if user_text.lower() in ["stop listening", "stop", "quit", "exit"]:
            await sio.emit('assistant_chunk', {'chunk': "Stopping voice listening."}, to=sid)
            await sio.emit('assistant_done', {}, to=sid)
            return

        # Check if it's an automation command
        if is_automation_command(user_text):
            try:
                result = run_command(user_text)
                speaker.say(result)
                await sio.emit('assistant_chunk', {'chunk': result}, to=sid)
                await sio.emit('assistant_done', {}, to=sid)
                
                # Store automation result
                conversations[conversation_id].append({"role": "assistant", "content": result})
                return
            except Exception as e:
                error_msg = f"Automation error: {str(e)}"
                await sio.emit('assistant_chunk', {'chunk': error_msg}, to=sid)
                await sio.emit('assistant_done', {}, to=sid)
                return

        # Use main project brain if available
        if ultron_agent and hasattr(ultron_agent, 'brain'):
            try:
                # Use the think method from UltronBrain
                response = ultron_agent.brain.think(user_text)
                speaker.say(response)
                await sio.emit('assistant_chunk', {'chunk': response}, to=sid)
                await sio.emit('assistant_done', {}, to=sid)
                conversations[conversation_id].append({"role": "assistant", "content": response})
                return
            except Exception as e:
                print(f"Main brain error: {e}, falling back to Ollama - app.py:186")

        # Fallback to Ollama
        messages = conversations[conversation_id][-10:]  # Keep last 10 messages for context
        await stream_response(messages, sid, conversation_id)

    except Exception as e:
        await sio.emit('error', {'message': f"Error processing message: {str(e)}"}, to=sid)

@sio.event
async def get_conversation_history(sid, data):
    """Return conversation history."""
    conversation_id = data.get('conversation_id', 'default')
    history = conversations.get(conversation_id, [])
    await sio.emit('conversation_history', {'history': history}, to=sid)

# Global variables for continuous voice mode
continuous_voice_sessions = {}
voice_stop_events = {}

@sio.event
async def start_continuous_voice(sid, data):
    """Start continuous voice interaction mode."""
    try:
        if not mic:
            await sio.emit('error', {'message': 'No microphone available'}, to=sid)
            return
        
        conversation_id = data.get('conversation_id', 'default')
        
        # Stop existing session if any
        if sid in continuous_voice_sessions:
            await stop_continuous_voice(sid, {})
        
        # Create stop event
        stop_event = threading.Event()
        voice_stop_events[sid] = stop_event
        
        # Start continuous listening in background thread
        def voice_handler(text):
            """Handle recognized voice input."""
            asyncio.create_task(process_voice_message(sid, text, conversation_id))
        
        def continuous_listen():
            """Continuous listening loop."""
            from voice import recognizer_instance
            recognizer_instance.listen_continuously(voice_handler, stop_event)
        
        voice_thread = threading.Thread(target=continuous_listen, daemon=True)
        continuous_voice_sessions[sid] = voice_thread
        voice_thread.start()
        
        await sio.emit('continuous_voice_started', {
            'message': 'Continuous voice mode started. Speak naturally and I will respond.',
            'conversation_id': conversation_id
        }, to=sid)
        
    except Exception as e:
        await sio.emit('error', {'message': f"Error starting continuous voice: {str(e)}"}, to=sid)

@sio.event
async def stop_continuous_voice(sid, data):
    """Stop continuous voice interaction mode."""
    try:
        # Stop the voice thread
        if sid in voice_stop_events:
            voice_stop_events[sid].set()
            del voice_stop_events[sid]
        
        if sid in continuous_voice_sessions:
            del continuous_voice_sessions[sid]
        
        await sio.emit('continuous_voice_stopped', {
            'message': 'Continuous voice mode stopped.'
        }, to=sid)
        
    except Exception as e:
        await sio.emit('error', {'message': f"Error stopping continuous voice: {str(e)}"}, to=sid)

async def process_voice_message(sid, text, conversation_id):
    """Process voice input in continuous mode."""
    try:
        # Emit what was heard
        await sio.emit('voice_recognized', {
            'text': text,
            'conversation_id': conversation_id
        }, to=sid)
        
        # Process like a regular message
        await user_message(sid, {'text': text, 'conversation_id': conversation_id})
        
    except Exception as e:
        await sio.emit('error', {'message': f"Error processing voice message: {str(e)}"}, to=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnect - cleanup voice sessions."""
    print(f"❌ Client disconnected: {sid} - app.py:135")
    
    # Cleanup continuous voice session
    if sid in voice_stop_events:
        voice_stop_events[sid].set()
        del voice_stop_events[sid]
    
    if sid in continuous_voice_sessions:
        del continuous_voice_sessions[sid]

# -------------------------------------------------
# HTTP Routes
# -------------------------------------------------
@fastapi_app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@fastapi_app.post("/voice")
async def voice_input():
    """Handle voice input via HTTP."""
    if not mic:
        return JSONResponse({"error": "No microphone available"}, status_code=400)
    
    try:
        text = listen_once(recognizer, mic)
        if text:
            return JSONResponse({"text": text, "success": True})
        else:
            return JSONResponse({"error": "Could not understand audio", "success": False})
    except Exception as e:
        return JSONResponse({"error": str(e), "success": False})

@fastapi_app.get("/status")
async def get_status():
    """Get system status."""
    status = {
        "server_running": True,
        "microphone_available": mic is not None,
        "main_agent_available": ultron_agent is not None,
        "conversations": len(conversations)
    }
    
    if ultron_agent:
        status["agent_status"] = getattr(ultron_agent, 'status', 'unknown')
    
    return JSONResponse(status)

@fastapi_app.get("/conversations")
async def list_conversations():
    """List all conversation IDs."""
    return JSONResponse({"conversations": list(conversations.keys())})

@fastapi_app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation history."""
    history = conversations.get(conversation_id, [])
    return JSONResponse({"conversation_id": conversation_id, "history": history})

@fastapi_app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear specific conversation."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return JSONResponse({"message": f"Conversation {conversation_id} cleared"})
    return JSONResponse({"error": "Conversation not found"}, status_code=404)

# -------------------------------------------------
# Desktop GUI Integration
# -------------------------------------------------
def launch_desktop_gui():
    """Launch the desktop GUI version."""
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtCore import QUrl
        import sys
        
        class UltronDesktopApp(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Ultron Assistant")
                self.setGeometry(100, 100, 1200, 800)
                
                # Create web engine view
                self.browser = QWebEngineView()
                self.browser.setUrl(QUrl("http://127.0.0.1:8000"))
                self.setCentralWidget(self.browser)
        
        app = QApplication(sys.argv)
        window = UltronDesktopApp()
        window.show()
        app.exec()
        
    except ImportError:
        print("PySide6 not available, opening in browser instead - app.py:287")
        webbrowser.open("http://127.0.0.1:8000")

# -------------------------------------------------
# Main Application Runner
# -------------------------------------------------
def run_server(host="127.0.0.1", port=8000, use_gui=True):
    """Run the FastAPI server and optionally launch GUI."""
    
    # Start server in background thread
    def start_server():
        uvicorn.run(app, host=host, port=port, log_level="info")
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    import time
    time.sleep(2)
    
    if use_gui:
        # Try desktop GUI first, fallback to browser
        try:
            launch_desktop_gui()
        except Exception as e:
            print(f"Desktop GUI failed: {e} - app.py:312")
            print("Opening in browser instead... - app.py:313")
            webbrowser.open(f"http://{host}:{port}")
    else:
        print(f"Server running at http://{host}:{port} - app.py:316")
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Server stopped - app.py:322")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultron Assistant Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-gui", action="store_true", help="Run without GUI")
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, use_gui=not args.no_gui)
