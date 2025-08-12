"""Enhanced API server with health endpoints and structured logging."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import uvicorn

from ultron_agent.config import get_config, UltronConfig
from ultron_agent.health import get_health_checker, HealthChecker
from ultron_agent.logging_config import get_logger, LogContext

logger = get_logger("ultron.api", source="api")

# Global agent instance (set by main.py)
_agent_instance = None


# Request/Response models
class StatusResponse(BaseModel):
    """Status endpoint response."""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    """Readiness endpoint response."""
    status: str
    timestamp: str
    response_time_ms: float
    components: Dict[str, Any]


class CommandRequest(BaseModel):
    """Command execution request."""
    command: str
    context: Optional[Dict[str, Any]] = None


class CommandResponse(BaseModel):
    """Command execution response."""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: float


# Dependencies
def get_health_checker_dep() -> HealthChecker:
    """Dependency for health checker."""
    return get_health_checker()


def get_config_dep() -> UltronConfig:
    """Dependency for configuration."""
    return get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown."""
    logger.info("Starting Ultron Agent API server")

    # Initialize health checker
    health_checker = get_health_checker()

    # Startup complete
    logger.info("API server startup complete")
    yield

    # Shutdown
    logger.info("Shutting down API server")


# Create FastAPI app
app = FastAPI(
    title="Ultron Agent API",
    description="Local voice-first AI assistant with multi-model support",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests with timing and correlation."""
    with LogContext(f"{request.method} {request.url.path}", logger) as ctx:
        try:
            response = await call_next(request)
            ctx.log(f"Response: {response.status_code}", extra={
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else "unknown"
            })
            return response
        except Exception as e:
            ctx.log(f"Request failed: {e}", level=logging.ERROR)
            raise


# Health endpoints
@app.get("/healthz", response_model=StatusResponse, tags=["Health"])
async def health_check(health_checker: HealthChecker = Depends(get_health_checker_dep)):
    """
    Basic health check endpoint for load balancers.
    Returns quickly with minimal dependency checks.
    """
    result = await health_checker.check_basic_health()
    return StatusResponse(**result)


@app.get("/readyz", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check(health_checker: HealthChecker = Depends(get_health_checker_dep)):
    """
    Comprehensive readiness check including all dependencies.
    Use this to determine if the service is ready to handle requests.
    """
    result = await health_checker.check_readiness()

    if result["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail="Service not ready")
    elif result["status"] == "degraded":
        # Return 200 but log warning
        logger.warning("Service is in degraded state", extra={"components": result["components"]})

    return ReadinessResponse(**result)


@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def metrics(health_checker: HealthChecker = Depends(get_health_checker_dep)):
    """
    Prometheus-compatible metrics endpoint.
    Returns system metrics in Prometheus text format.
    """
    result = await health_checker.get_metrics()
    return Response(
        content=result["body"],
        media_type=result["content_type"]
    )


# Legacy status endpoint for backward compatibility
@app.get("/status", tags=["Legacy"])
async def legacy_status(health_checker: HealthChecker = Depends(get_health_checker_dep)):
    """Legacy status endpoint for backward compatibility."""
    result = await health_checker.check_basic_health()
    return {
        "status": "operational" if result["status"] == "healthy" else "degraded",
        "message": "Ultron Agent is running",
        "timestamp": result["timestamp"],
        "version": result["version"]
    }


# Command execution endpoint
@app.post("/command", response_model=CommandResponse, tags=["Commands"])
async def execute_command(
    request: CommandRequest,
    config: UltronConfig = Depends(get_config_dep)
):
    """
    Execute a command through the integrated ULTRON agent.
    """
    with LogContext(f"Command: {request.command}", logger) as ctx:
        try:
            if _agent_instance is None:
                raise HTTPException(status_code=503, detail="Agent not initialized")

            ctx.log(f"Executing command: {request.command}")
            
            # Execute command through agent
            start_time = asyncio.get_event_loop().time()
            result = _agent_instance.handle_text(request.command)
            end_time = asyncio.get_event_loop().time()
            
            execution_time_ms = (end_time - start_time) * 1000

            return CommandResponse(
                success=True,
                result=result,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            ctx.log(f"Command execution failed: {e}", level=logging.ERROR)
            return CommandResponse(
                success=False,
                error=str(e),
                execution_time_ms=0.0
            )


# Configuration endpoints
@app.get("/config", tags=["Configuration"])
async def get_configuration(config: UltronConfig = Depends(get_config_dep)):
    """Get current configuration (sanitized)."""
    return config.sanitized_dict()


# Agent-specific endpoints
@app.get("/agent/status", tags=["Agent"])
async def get_agent_status():
    """Get detailed agent status including all components."""
    if _agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "status": _agent_instance.status,
        "components": {
            "brain": _agent_instance.brain is not None,
            "voice": _agent_instance.voice is not None,
            "vision": _agent_instance.vision is not None,
            "gui": _agent_instance.gui is not None,
            "maverick": _agent_instance.maverick is not None,
            "tools_count": len(_agent_instance.tools),
            "event_system": _agent_instance.event_system is not None,
            "performance_monitor": _agent_instance.performance_monitor is not None,
            "task_scheduler": _agent_instance.task_scheduler is not None
        }
    }


@app.get("/agent/tools", tags=["Agent"])
async def get_agent_tools():
    """Get list of available tools."""
    if _agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    tools_info = []
    for tool in _agent_instance.tools:
        try:
            schema = tool.__class__.schema() if hasattr(tool.__class__, 'schema') else {}
            tools_info.append({
                "name": schema.get('name', tool.__class__.__name__),
                "description": schema.get('description', 'No description'),
                "parameters": schema.get('parameters', {}),
                "class_name": tool.__class__.__name__
            })
        except Exception as e:
            tools_info.append({
                "name": tool.__class__.__name__,
                "description": f"Error getting tool info: {e}",
                "parameters": {},
                "class_name": tool.__class__.__name__,
                "error": True
            })
    
    return {
        "tools": tools_info,
        "total_count": len(_agent_instance.tools)
    }


@app.get("/agent/maverick", tags=["Agent"])
async def get_maverick_status():
    """Get Maverick auto-improvement engine status."""
    if _agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return _agent_instance.get_maverick_status()


@app.post("/agent/maverick/analyze", tags=["Agent"])
async def trigger_maverick_analysis():
    """Trigger Maverick analysis manually."""
    if _agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if not _agent_instance.maverick:
        raise HTTPException(status_code=404, detail="Maverick engine not available")
    
    try:
        result = await _agent_instance.handle_command("force maverick analysis")
        return {
            "success": True,
            "result": result,
            "message": "Maverick analysis triggered successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to trigger Maverick analysis"
        }


@app.get("/info", tags=["Information"])
async def get_info():
    """Get general service information."""
    return {
        "name": "Ultron Agent",
        "version": "3.0.0",
        "description": "Local voice-first AI assistant",
        "endpoints": {
            "health": "/healthz",
            "readiness": "/readyz",
            "metrics": "/metrics",
            "docs": "/docs",
            "status": "/status (legacy)",
            "command": "/command",
            "config": "/config"
        }
    }


async def run_server(
    host: str = "127.0.0.1",
    port: int = 5000,
    reload: bool = False,
    log_level: str = "info"
) -> None:
    """
    Run the API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        log_level: Uvicorn log level
    """
    config_obj = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower(),
        access_log=True
    )

    server = uvicorn.Server(config_obj)
    logger.info(f"Starting API server on {host}:{port}")
    await server.serve()


if __name__ == "__main__":
    # Development server
    import sys

    # Setup basic logging for development
    logging.basicConfig(level=logging.INFO)

    # Get config
    config = get_config()

    # Run server
    asyncio.run(run_server(
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.value
    ))
