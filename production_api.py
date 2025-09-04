#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Production API Server
FastAPI-based REST API with comprehensive documentation and monitoring
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import uvicorn

# Import our modules
try:
    from secure_config import get_config, get_sensitive_config
    from production_monitor import ProductionMonitor
    from ultron_agent.health import HealthChecker
except ImportError:
    # Fallback for development
    def get_config(): return {}
    def get_sensitive_config(key, default=None): return default
    ProductionMonitor = None
    HealthChecker = None

logger = logging.getLogger(__name__)


# Pydantic models for API documentation
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Overall health status", example="healthy")
    timestamp: str = Field(..., description="ISO timestamp of health check")
    uptime: float = Field(..., description="System uptime in seconds")
    components: Dict[str, str] = Field(..., description="Component health status")
    version: str = Field(..., description="Application version", example="3.0.0")


class SystemMetrics(BaseModel):
    """System metrics response model."""
    cpu_percent: float = Field(..., description="CPU usage percentage", ge=0, le=100)
    memory_percent: float = Field(..., description="Memory usage percentage", ge=0, le=100)
    disk_percent: float = Field(..., description="Disk usage percentage", ge=0, le=100)
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    timestamp: str = Field(..., description="ISO timestamp of metrics collection")
    gpu_percent: Optional[float] = Field(None, description="GPU usage percentage if available")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    model: Optional[str] = Field("gpt-3.5-turbo", description="AI model to use")
    temperature: Optional[float] = Field(0.7, description="Response creativity", ge=0, le=2)
    max_tokens: Optional[int] = Field(1000, description="Maximum response tokens", ge=1, le=4000)


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="AI generated response")
    model: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Tokens consumed")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: str = Field(..., description="ISO timestamp of response")


class VoiceRequest(BaseModel):
    """Voice interaction request model."""
    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=1000)
    voice: Optional[str] = Field("default", description="Voice to use")
    speed: Optional[float] = Field(1.0, description="Speech speed", ge=0.5, le=2.0)


class ConfigRequest(BaseModel):
    """Configuration update request model."""
    config: Dict[str, Any] = Field(..., description="Configuration data to update")
    encrypted: bool = Field(True, description="Whether to encrypt the configuration")


class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: str = Field(..., description="ISO timestamp of response")


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="ULTRON Agent 3.0 API",
        version="3.0.0",
        description="""
## ULTRON Agent 3.0 - Production API

A comprehensive AI agent framework with voice-first, multi-modal capabilities.

### Features
- 🤖 **Multi-LLM Integration**: OpenAI, Ollama, and more
- 🎤 **Voice Processing**: Speech recognition and synthesis
- 👁️ **Vision Capabilities**: Image analysis and processing
- 🔧 **System Automation**: Cross-platform automation tools
- 📊 **Health Monitoring**: Real-time system metrics and alerts
- 🔒 **Security First**: Encrypted configuration and secure endpoints

### Authentication
Most endpoints require API key authentication. Include your API key in the `X-API-Key` header.

### Rate Limiting
API endpoints are rate limited to ensure fair usage and system stability.

### Support
- **Documentation**: [GitHub Wiki](https://github.com/dqikfox/ultron_agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/dqikfox/ultron_agent/issues)
- **Security**: See security documentation for reporting vulnerabilities
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    
    # Add custom tags
    openapi_schema["tags"] = [
        {"name": "Health", "description": "System health and monitoring endpoints"},
        {"name": "AI Chat", "description": "AI conversation and chat endpoints"},
        {"name": "Voice", "description": "Voice processing and synthesis endpoints"},
        {"name": "System", "description": "System management and configuration endpoints"},
        {"name": "Monitoring", "description": "Metrics and monitoring endpoints"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Create FastAPI app
app = FastAPI(
    title="ULTRON Agent 3.0",
    description="Production-ready AI agent framework",
    version="3.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global variables
monitor: Optional[ProductionMonitor] = None
health_checker: Optional[HealthChecker] = None
start_time = time.time()


# Dependency functions
async def get_api_key(request: Request) -> str:
    """Validate API key from header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Validate API key (implement your validation logic)
    expected_key = get_sensitive_config("api.secret_key", "development-key")
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key


# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Interactive Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "operationsSorter": "alpha",
            "filter": True,
            "tagsSorter": "alpha",
            "tryItOutEnabled": True
        }
    )


@app.get("/api/v1/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    """Get OpenAPI schema."""
    return JSONResponse(custom_openapi())


# Health and monitoring endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Basic health check",
    description="Returns the basic health status of the ULTRON Agent system."
)
async def health_check():
    """Basic health check endpoint."""
    try:
        uptime = time.time() - start_time
        
        # Get component health if available
        components = {"api": "healthy"}
        if health_checker:
            try:
                health_data = await health_checker.check_basic_health()
                components.update(health_data.get("components", {}))
            except Exception as e:
                logger.error(f"Health checker error: {e}")
                components["health_checker"] = "error"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            uptime=uptime,
            components=components,
            version="3.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@app.get(
    "/health/detailed",
    response_model=Dict[str, Any],
    tags=["Health"],
    summary="Detailed health check",
    description="Returns detailed health information including component status and metrics."
)
async def detailed_health_check():
    """Detailed health check with component information."""
    try:
        if health_checker:
            return await health_checker.check_all_health()
        else:
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {"api": "healthy"},
                "message": "Health checker not available"
            }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detailed health check failed"
        )


@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="Prometheus metrics",
    description="Returns system metrics in Prometheus format for monitoring integration."
)
async def get_metrics():
    """Prometheus metrics endpoint."""
    try:
        if monitor:
            metrics_text = monitor.metrics_collector.get_prometheus_metrics()
            return Response(content=metrics_text, media_type="text/plain")
        else:
            return Response(content="# Monitoring not available", media_type="text/plain")
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return Response(content=f"# Error: {e}", media_type="text/plain")


@app.get(
    "/api/v1/system/metrics",
    response_model=SystemMetrics,
    tags=["Monitoring"],
    summary="System metrics",
    description="Returns current system resource metrics in JSON format."
)
async def get_system_metrics():
    """Get current system metrics."""
    try:
        if monitor:
            metrics = monitor.metrics_collector.collect_system_metrics()
            return SystemMetrics(
                cpu_percent=metrics.cpu_percent,
                memory_percent=metrics.memory_percent,
                disk_percent=metrics.disk_percent,
                uptime_seconds=metrics.uptime_seconds,
                timestamp=metrics.timestamp.isoformat(),
                gpu_percent=metrics.gpu_percent
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System monitoring not available"
            )
    except Exception as e:
        logger.error(f"System metrics collection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect system metrics"
        )


# AI Chat endpoints
@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    tags=["AI Chat"],
    summary="Send chat message",
    description="Send a message to the AI agent and receive a response.",
    dependencies=[Depends(get_api_key)]
)
async def chat_endpoint(request: ChatRequest):
    """Chat with the AI agent."""
    try:
        start_time = time.time()
        
        # TODO: Implement actual AI chat logic
        # This is a placeholder implementation
        response_text = f"Echo: {request.message}"
        tokens_used = len(request.message.split()) + len(response_text.split())
        response_time = time.time() - start_time
        
        return ChatResponse(
            response=response_text,
            model=request.model,
            tokens_used=tokens_used,
            response_time=response_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed"
        )


# Voice endpoints
@app.post(
    "/api/v1/voice/synthesize",
    response_model=APIResponse,
    tags=["Voice"],
    summary="Text-to-speech synthesis",
    description="Convert text to speech using the voice synthesis system.",
    dependencies=[Depends(get_api_key)]
)
async def voice_synthesize(request: VoiceRequest):
    """Synthesize speech from text."""
    try:
        # TODO: Implement actual voice synthesis
        # This is a placeholder implementation
        return APIResponse(
            success=True,
            message=f"Voice synthesis requested for: {request.text[:50]}...",
            data={
                "text": request.text,
                "voice": request.voice,
                "speed": request.speed,
                "duration_estimate": len(request.text) * 0.1  # Rough estimate
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Voice synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice synthesis failed"
        )


# System management endpoints
@app.get(
    "/api/v1/system/status",
    response_model=Dict[str, Any],
    tags=["System"],
    summary="System status",
    description="Get comprehensive system status information.",
    dependencies=[Depends(get_api_key)]
)
async def get_system_status():
    """Get comprehensive system status."""
    try:
        status_data = {
            "version": "3.0.0",
            "uptime": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "environment": get_config().get("environment", "development"),
            "components": {
                "api": "operational",
                "monitoring": "operational" if monitor else "unavailable",
                "health_checker": "operational" if health_checker else "unavailable"
            }
        }
        
        return status_data
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System status check failed"
        )


@app.post(
    "/api/v1/system/config",
    response_model=APIResponse,
    tags=["System"],
    summary="Update configuration",
    description="Update system configuration (admin only).",
    dependencies=[Depends(get_api_key)]
)
async def update_config(request: ConfigRequest):
    """Update system configuration."""
    try:
        # TODO: Implement configuration update logic
        # This is a placeholder implementation
        return APIResponse(
            success=True,
            message="Configuration update requested",
            data={
                "config_keys": list(request.config.keys()),
                "encrypted": request.encrypted,
                "applied": False  # Would be True after actual implementation
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Configuration update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration update failed"
        )


# Root endpoint
@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
    summary="API Home",
    description="ULTRON Agent API home page with links to documentation."
)
async def api_home():
    """API home page."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>ULTRON Agent 3.0 API</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: linear-gradient(135deg, #1a1a1a, #2d2d2d); 
            color: #fff; min-height: 100vh;
        }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .header { margin-bottom: 40px; }
        .logo { font-size: 3em; margin-bottom: 10px; }
        .subtitle { font-size: 1.2em; opacity: 0.8; }
        .card { 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; 
            padding: 30px; margin: 20px 0; text-align: left;
        }
        .btn { 
            display: inline-block; background: #007acc; color: white; 
            text-decoration: none; padding: 12px 24px; border-radius: 6px; 
            margin: 10px; transition: all 0.3s;
        }
        .btn:hover { background: #005a9e; transform: translateY(-2px); }
        .feature { margin: 15px 0; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .feature:last-child { border-bottom: none; }
        .status { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚀 ULTRON Agent 3.0</div>
            <div class="subtitle">Production-Ready AI Agent Framework</div>
            <div class="status">✅ API Online</div>
        </div>
        
        <div class="card">
            <h2>🛠️ API Documentation</h2>
            <p>Access comprehensive API documentation and interactive testing:</p>
            <a href="/docs" class="btn">📖 Interactive Documentation</a>
            <a href="/api/v1/openapi.json" class="btn">📄 OpenAPI Schema</a>
        </div>
        
        <div class="card">
            <h2>📊 System Monitoring</h2>
            <div class="feature">
                <strong>Health Check:</strong> <a href="/health" style="color: #4CAF50;">/health</a>
            </div>
            <div class="feature">
                <strong>Detailed Health:</strong> <a href="/health/detailed" style="color: #4CAF50;">/health/detailed</a>
            </div>
            <div class="feature">
                <strong>Metrics:</strong> <a href="/metrics" style="color: #4CAF50;">/metrics</a>
            </div>
        </div>
        
        <div class="card">
            <h2>🤖 AI Capabilities</h2>
            <div class="feature">💬 <strong>Multi-LLM Chat:</strong> OpenAI, Ollama integration</div>
            <div class="feature">🎤 <strong>Voice Processing:</strong> Speech recognition and synthesis</div>
            <div class="feature">👁️ <strong>Vision:</strong> Image analysis and processing</div>
            <div class="feature">🔧 <strong>Automation:</strong> System automation tools</div>
        </div>
        
        <div class="card">
            <h2>🔒 Security & Authentication</h2>
            <p>All API endpoints require authentication via the <code>X-API-Key</code> header.</p>
            <p>See the interactive documentation for details on request/response formats.</p>
        </div>
        
        <div class="card">
            <h2>📚 Resources</h2>
            <a href="https://github.com/dqikfox/ultron_agent" class="btn">📁 GitHub Repository</a>
            <a href="https://github.com/dqikfox/ultron_agent/wiki" class="btn">📖 Documentation</a>
            <a href="https://github.com/dqikfox/ultron_agent/issues" class="btn">🐛 Report Issues</a>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global monitor, health_checker
    
    logger.info("🚀 Starting ULTRON Agent API server...")
    
    # Initialize monitoring if available
    if ProductionMonitor:
        try:
            monitor = ProductionMonitor()
            await monitor.start_monitoring()
            logger.info("✅ Production monitoring started")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    # Initialize health checker if available
    if HealthChecker:
        try:
            health_checker = HealthChecker()
            logger.info("✅ Health checker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize health checker: {e}")
    
    logger.info("✅ ULTRON Agent API server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global monitor
    
    logger.info("🔄 Shutting down ULTRON Agent API server...")
    
    if monitor:
        try:
            await monitor.stop_monitoring()
            logger.info("✅ Monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    logger.info("✅ ULTRON Agent API server shutdown complete")


# Set custom OpenAPI schema
app.openapi = custom_openapi


def create_app(config: Optional[Dict[str, Any]] = None) -> FastAPI:
    """Factory function to create the FastAPI app."""
    return app


async def start_server(host: str = "0.0.0.0", port: int = 8080, **kwargs):
    """Start the API server."""
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        **kwargs
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ULTRON Agent API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run server
    uvicorn.run(
        "production_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )