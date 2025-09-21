"""
ULTRON Agent 3.0 - Enhanced API Server
Provides comprehensive system status, health monitoring, and control endpoints
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Enhanced imports
from utils.ultron_logger import log_info, log_error, get_recent_logs
from utils.model_awareness import get_system_stability_score, check_file_context
from utils.system_health import get_health_monitor, quick_health_check

# Try to import agent components
try:
    from agent_core_enhanced import UltronAgentEnhanced
except ImportError:
    try:
        from agent_core import UltronAgent as UltronAgentEnhanced
    except ImportError:
        UltronAgentEnhanced = None

# Pydantic models
class SystemStatus(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float
    version: str
    components: Dict[str, bool]
    performance: Optional[Dict[str, Any]] = None

class HealthCheck(BaseModel):
    overall_status: str
    score: float
    timestamp: str
    checks: Dict[str, Any]

class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    success: bool
    response: str
    timestamp: str
    tools: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class LogEntry(BaseModel):
    timestamp: str
    component: str
    level: str
    message: str

# Global agent instance
agent_instance: Optional[UltronAgentEnhanced] = None

# FastAPI app
app = FastAPI(
    title="ULTRON Agent 3.0 Enhanced API",
    description="Comprehensive API for ULTRON Agent system management and control",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced API server"""
    global agent_instance
    
    log_info("api_enhanced", "Starting Enhanced API Server...")
    
    try:
        if UltronAgentEnhanced:
            agent_instance = UltronAgentEnhanced()
            await agent_instance.initialize()
            log_info("api_enhanced", "Enhanced agent initialized successfully")
        else:
            log_error("api_enhanced", "Enhanced agent not available")
    except Exception as e:
        log_error("api_enhanced", f"Failed to initialize agent: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent_instance
    
    log_info("api_enhanced", "Shutting down Enhanced API Server...")
    
    if agent_instance and hasattr(agent_instance, 'shutdown_enhanced'):
        try:
            await agent_instance.shutdown_enhanced()
            log_info("api_enhanced", "Enhanced agent shutdown complete")
        except Exception as e:
            log_error("api_enhanced", f"Error during agent shutdown: {e}")

# Dependency to get agent instance
async def get_agent() -> UltronAgentEnhanced:
    """Get the current agent instance"""
    if agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return agent_instance

# Health and Status Endpoints
@app.get("/health", response_model=HealthCheck)
async def get_health():
    """Get comprehensive system health status"""
    try:
        health_data = quick_health_check()
        return HealthCheck(**health_data)
    except Exception as e:
        log_error("api_enhanced", f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/status", response_model=SystemStatus)
async def get_status(agent: UltronAgentEnhanced = Depends(get_agent)):
    """Get current system status"""
    try:
        status_data = agent.get_system_status()
        return SystemStatus(**status_data)
    except Exception as e:
        log_error("api_enhanced", f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/status/simple")
async def get_simple_status():
    """Get simple status for quick checks"""
    try:
        stability_score = get_system_stability_score()
        
        return {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "stability_score": stability_score,
            "agent_available": agent_instance is not None,
            "version": "3.0_enhanced"
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "3.0_enhanced"
        }

# Agent Control Endpoints
@app.post("/command", response_model=CommandResponse)
async def execute_command(
    request: CommandRequest,
    agent: UltronAgentEnhanced = Depends(get_agent)
):
    """Execute a command through the agent"""
    try:
        log_info("api_enhanced", f"Executing command via API: {request.command}")
        
        response = await agent.process_command_enhanced(request.command, request.context)
        
        return CommandResponse(
            success=response.get("success", False),
            response=response.get("response", ""),
            timestamp=response.get("timestamp", datetime.now().isoformat()),
            tools=response.get("tools"),
            error=response.get("error")
        )
    except Exception as e:
        log_error("api_enhanced", f"Command execution failed: {e}")
        return CommandResponse(
            success=False,
            response="",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

@app.get("/tools")
async def get_tools(agent: UltronAgentEnhanced = Depends(get_agent)):
    """Get list of available tools"""
    try:
        if hasattr(agent, 'list_tools_enhanced'):
            tools = agent.list_tools_enhanced()
        else:
            tools = [{"name": name, "available": True} for name in agent.list_tools()]
        
        return {
            "tools": tools,
            "count": len(tools),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error("api_enhanced", f"Failed to get tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")

# Voice Control Endpoints
@app.post("/voice/speak")
async def speak_text(
    text: str,
    async_mode: bool = True,
    agent: UltronAgentEnhanced = Depends(get_agent)
):
    """Make the agent speak text"""
    try:
        if hasattr(agent, 'speak_enhanced'):
            success = await agent.speak_enhanced(text, async_mode)
        elif hasattr(agent, 'speak'):
            success = await agent.speak(text, async_mode)
        else:
            success = False
        
        return {
            "success": success,
            "text": text,
            "async_mode": async_mode,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error("api_enhanced", f"Speech failed: {e}")
        raise HTTPException(status_code=500, detail=f"Speech failed: {str(e)}")

@app.get("/voice/status")
async def get_voice_status(agent: UltronAgentEnhanced = Depends(get_agent)):
    """Get voice system status"""
    try:
        voice_available = agent.voice is not None
        
        status = {
            "available": voice_available,
            "timestamp": datetime.now().isoformat()
        }
        
        if voice_available and hasattr(agent.voice, 'check_tts_health'):
            try:
                tts_health = agent.voice.check_tts_health()
                stt_health = agent.voice.check_stt_health()
                status["tts_engines"] = tts_health
                status["stt_engines"] = stt_health
            except Exception as e:
                status["health_check_error"] = str(e)
        
        return status
    except Exception as e:
        log_error("api_enhanced", f"Voice status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice status check failed: {str(e)}")

# Logging and Monitoring Endpoints
@app.get("/logs", response_model=List[LogEntry])
async def get_logs(
    component: Optional[str] = None,
    limit: int = 100,
    level: Optional[str] = None
):
    """Get recent log entries"""
    try:
        logs = get_recent_logs(component, limit)
        
        # Filter by level if specified
        if level:
            logs = [log for log in logs if log.get("level", "").upper() == level.upper()]
        
        return [
            LogEntry(
                timestamp=log.get("timestamp", ""),
                component=log.get("component", "unknown"),
                level=log.get("level", "INFO"),
                message=log.get("message", "")
            )
            for log in logs
        ]
    except Exception as e:
        log_error("api_enhanced", f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@app.get("/logs/components")
async def get_log_components():
    """Get list of components that have logs"""
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"components": [], "count": 0}
        
        components = []
        for log_file in logs_dir.glob("*.log"):
            if log_file.stem not in ["ultron_master", "activities"]:
                components.append(log_file.stem)
        
        return {
            "components": sorted(components),
            "count": len(components),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error("api_enhanced", f"Failed to get log components: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get log components: {str(e)}")

# System Information Endpoints
@app.get("/system/info")
async def get_system_info():
    """Get detailed system information"""
    try:
        import platform
        import psutil
        
        info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            },
            "resources": {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return info
    except Exception as e:
        log_error("api_enhanced", f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

@app.get("/system/processes")
async def get_system_processes():
    """Get running processes information"""
    try:
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 1:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        return {
            "processes": processes[:20],  # Top 20 processes
            "total_count": len(processes),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error("api_enhanced", f"Failed to get processes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get processes: {str(e)}")

# File System Endpoints
@app.get("/files/context")
async def get_file_context(file_path: str):
    """Get context information about a file"""
    try:
        context = check_file_context(file_path)
        return {
            "file_path": file_path,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error("api_enhanced", f"Failed to get file context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file context: {str(e)}")

# Configuration Endpoints
@app.get("/config")
async def get_config():
    """Get current configuration (sanitized)"""
    try:
        config_path = Path("ultron_config.json")
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Sanitize sensitive information
        sanitized_config = config.copy()
        for key in sanitized_config:
            if "key" in key.lower() or "secret" in key.lower() or "password" in key.lower():
                if sanitized_config[key]:
                    sanitized_config[key] = "***HIDDEN***"
        
        return {
            "config": sanitized_config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error("api_enhanced", f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time system updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send periodic status updates
            try:
                status_data = {
                    "type": "status_update",
                    "timestamp": datetime.now().isoformat(),
                    "stability_score": get_system_stability_score(),
                    "agent_available": agent_instance is not None
                }
                
                if agent_instance:
                    status_data["agent_status"] = agent_instance.get_system_status()
                
                await websocket.send_json(status_data)
                
            except Exception as e:
                log_error("api_enhanced", f"WebSocket update error: {e}")
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        log_error("api_enhanced", f"WebSocket connection error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    log_error("api_enhanced", f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc) if hasattr(exc, 'detail') else "Unknown error"
        }
    )

# Main server function
def start_enhanced_api_server(host: str = "127.0.0.1", port: int = 8001):
    """Start the enhanced API server"""
    log_info("api_enhanced", f"Starting Enhanced API Server on {host}:{port}")
    
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    return server

if __name__ == "__main__":
    # Start the server
    server = start_enhanced_api_server()
    server.run()