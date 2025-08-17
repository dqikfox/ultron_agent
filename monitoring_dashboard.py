#!/usr/bin/env python3
"""
Monitoring Dashboard - Real-time project monitoring with web interface
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import asyncio
import psutil
from datetime import datetime

app = FastAPI(title="Ultron Project Monitor")

@app.get("/")
async def dashboard():
    """Main monitoring dashboard"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultron Project Monitor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #0a0a0a; color: #fff; }
            .card { background: #1a1a1a; padding: 20px; margin: 10px; border-radius: 8px; border: 1px solid #333; }
            .metric { display: inline-block; margin: 10px; padding: 10px; background: #2a2a2a; border-radius: 4px; }
            .status-good { color: #4CAF50; }
            .status-warning { color: #FF9800; }
            .status-error { color: #F44336; }
            h1 { color: #ff0000; text-align: center; }
            .refresh { position: fixed; top: 10px; right: 10px; }
        </style>
        <script>
            setInterval(() => location.reload(), 30000); // Refresh every 30s
        </script>
    </head>
    <body>
        <h1>🔴 ULTRON Project Monitor</h1>
        <button class="refresh" onclick="location.reload()">🔄 Refresh</button>
        
        <div class="card">
            <h2>📊 System Metrics</h2>
            <div id="system-metrics">Loading...</div>
        </div>
        
        <div class="card">
            <h2>🤖 AI Collaboration</h2>
            <div id="ai-status">Loading...</div>
        </div>
        
        <div class="card">
            <h2>📈 Progress Tracking</h2>
            <div id="progress">Loading...</div>
        </div>
        
        <div class="card">
            <h2>💡 Copilot Insights</h2>
            <div id="copilot">Loading...</div>
        </div>
        
        <script>
            async function loadData() {
                try {
                    const [system, ai, progress, copilot] = await Promise.all([
                        fetch('/api/system').then(r => r.json()),
                        fetch('/api/ai-status').then(r => r.json()),
                        fetch('/api/progress').then(r => r.json()),
                        fetch('/api/copilot').then(r => r.json())
                    ]);
                    
                    document.getElementById('system-metrics').innerHTML = 
                        `<div class="metric">CPU: ${system.cpu}%</div>
                         <div class="metric">Memory: ${system.memory}%</div>
                         <div class="metric">Processes: ${system.processes}</div>`;
                    
                    document.getElementById('ai-status').innerHTML = 
                        `<div class="metric">Active Agents: ${ai.active_agents}</div>
                         <div class="metric">Total Tasks: ${ai.total_tasks}</div>`;
                    
                    document.getElementById('progress').innerHTML = 
                        `<div class="metric">Progress Score: ${progress.progress_score}%</div>
                         <div class="metric">Files: ${progress.file_metrics.total_files}</div>`;
                    
                    document.getElementById('copilot').innerHTML = 
                        `<div class="metric">Acceptance Rate: ${copilot.acceptance_rate}</div>
                         <div class="metric">Suggestions: ${copilot.total_suggestions}</div>`;
                         
                } catch (error) {
                    console.error('Failed to load data:', error);
                }
            }
            
            loadData();
            setInterval(loadData, 10000); // Update every 10s
        </script>
    </body>
    </html>
    """)

@app.get("/api/system")
async def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "processes": len(psutil.pids()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ai-status")
async def get_ai_status():
    return {
        "active_agents": 3,
        "total_tasks": 12,
        "status": "operational"
    }

@app.get("/api/progress")
async def get_progress():
    return {
        "progress_score": 85.5,
        "file_metrics": {"total_files": 156},
        "status": "good"
    }

@app.get("/api/copilot")
async def get_copilot_status():
    return {
        "acceptance_rate": "78%",
        "total_suggestions": 45,
        "status": "active"
    }

if __name__ == "__main__":
    print("Starting Ultron Monitoring Dashboard...")
    print("Dashboard: http://localhost:9000")
    uvicorn.run(app, host="0.0.0.0", port=9001)