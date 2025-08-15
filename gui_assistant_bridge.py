#!/usr/bin/env python3
"""
GUI-Assistant Bridge
Links the GUI folder with the assistant web application
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Paths
GUI_PATH = Path("gui/ultron_enhanced")
ASSISTANT_PATH = Path("assistant/ai-assistant")
WEB_PATH = GUI_PATH / "web"

app = FastAPI(title="Ultron GUI-Assistant Bridge")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from GUI
if WEB_PATH.exists():
    app.mount("/gui", StaticFiles(directory=str(WEB_PATH)), name="gui")

# Mount assistant build files if they exist
assistant_dist = ASSISTANT_PATH / "dist"
if assistant_dist.exists():
    app.mount("/assistant", StaticFiles(directory=str(assistant_dist)), name="assistant")

@app.get("/")
async def root():
    """Main page with links to both interfaces"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultron Control Center</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0a0a0a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { background: #1a1a1a; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #333; }
            .btn { display: inline-block; padding: 12px 24px; background: #ff0000; color: white; text-decoration: none; border-radius: 4px; margin: 10px 10px 10px 0; }
            .btn:hover { background: #cc0000; }
            h1 { color: #ff0000; text-align: center; }
            .status { padding: 8px; border-radius: 4px; margin: 10px 0; }
            .online { background: #004400; border: 1px solid #008800; }
            .offline { background: #440000; border: 1px solid #880000; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔴 ULTRON Control Center</h1>
            
            <div class="card">
                <h2>GUI Interface</h2>
                <p>Enhanced Ultron GUI with voice control and automation features</p>
                <div class="status online">✅ GUI Available</div>
                <a href="/gui/" class="btn">Launch GUI</a>
                <a href="/gui/index.html" class="btn">Direct Access</a>
            </div>
            
            <div class="card">
                <h2>AI Assistant</h2>
                <p>React-based AI assistant with chat interface and file processing</p>
                <div class="status online">✅ Assistant Available</div>
                <a href="/assistant/" class="btn">Launch Assistant</a>
                <a href="http://localhost:5173" class="btn">Dev Server</a>
            </div>
            
            <div class="card">
                <h2>Quick Actions</h2>
                <a href="/start-assistant" class="btn">Start Assistant Dev</a>
                <a href="/build-assistant" class="btn">Build Assistant</a>
                <a href="/status" class="btn">System Status</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/start-assistant")
async def start_assistant():
    """Start the assistant development server"""
    try:
        if ASSISTANT_PATH.exists():
            # Start the Vite dev server
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(ASSISTANT_PATH),
                shell=True
            )
            return {"status": "started", "message": "Assistant dev server starting on http://localhost:5173"}
        else:
            return {"status": "error", "message": "Assistant path not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/build-assistant")
async def build_assistant():
    """Build the assistant for production"""
    try:
        if ASSISTANT_PATH.exists():
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(ASSISTANT_PATH),
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {"status": "success", "message": "Assistant built successfully"}
            else:
                return {"status": "error", "message": result.stderr}
        else:
            return {"status": "error", "message": "Assistant path not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/status")
async def status():
    """Get system status"""
    return {
        "gui_available": WEB_PATH.exists(),
        "assistant_available": ASSISTANT_PATH.exists(),
        "assistant_built": (ASSISTANT_PATH / "dist").exists(),
        "paths": {
            "gui": str(GUI_PATH),
            "assistant": str(ASSISTANT_PATH),
            "web": str(WEB_PATH)
        }
    }

if __name__ == "__main__":
    print("🔴 Starting Ultron GUI-Assistant Bridge...")
    print(f"GUI Path: {GUI_PATH}")
    print(f"Assistant Path: {ASSISTANT_PATH}")
    print("Bridge available at: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)