#!/bin/bash
# ════════════════════════════════════════════════════════════════════════
# ULTRON AGENT 3.0 - Integration Setup Script
# ════════════════════════════════════════════════════════════════════════
# Sets up OpenTelemetry tracing and MCP server configurations
# ════════════════════════════════════════════════════════════════════════

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "ok" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}✗${NC} $message"
    fi
}

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         ULTRON AGENT 3.0 - Integration Setup              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Activate virtual environment if available
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_status "ok" "Virtual environment activated"
elif [ -d "env" ] && [ -f "env/bin/activate" ]; then
    source env/bin/activate
    print_status "ok" "Virtual environment activated"
fi

# Install OpenTelemetry tracing dependencies
echo ""
echo -e "${BLUE}[1/3] Installing OpenTelemetry tracing...${NC}"
if [ -f "install_tracing.sh" ]; then
    bash install_tracing.sh
    print_status "ok" "Tracing dependencies installed"
else
    print_status "warn" "install_tracing.sh not found - creating it"
    cat > install_tracing.sh << 'EOF'
#!/bin/bash
echo "Installing OpenTelemetry tracing dependencies..."

. venv/bin/activate

pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp-proto-http \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-flask

echo "✅ OpenTelemetry dependencies installed"
echo "Start ULTRON Agent to see traces at http://localhost:4320"
EOF
    chmod +x install_tracing.sh
    bash install_tracing.sh
    print_status "ok" "Tracing setup created and installed"
fi

# Verify tracing module exists
echo ""
echo -e "${BLUE}[2/3] Verifying tracing module...${NC}"
if [ -f "tracing.py" ]; then
    print_status "ok" "Tracing module found"
else
    print_status "warn" "Creating tracing module"
    cat > tracing.py << 'EOF'
"""
OpenTelemetry Tracing Setup for ULTRON Agent
Visualizes agent operations at http://localhost:4320
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import functools

# Configure tracing
resource = Resource.create({"service.name": "ultron-agent"})
trace.set_tracer_provider(TracerProvider(resource=resource))

# OTLP exporter to localhost:4320
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4320/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Get tracer
tracer = trace.get_tracer(__name__)

# Auto-instrument HTTP requests and Flask
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument()

def trace_function(name=None):
    """Decorator to trace function calls"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.result", str(type(result)))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator

def trace_agent_operation(operation_type, details=None):
    """Create a span for agent operations"""
    span = tracer.start_span(f"agent.{operation_type}")
    if details:
        for key, value in details.items():
            span.set_attribute(f"agent.{key}", str(value))
    return span
EOF
    print_status "ok" "Tracing module created"
fi

# Verify MCP configuration
echo ""
echo -e "${BLUE}[3/3] Verifying MCP configuration...${NC}"
if [ -f "mcp.json" ]; then
    if python3 -c "import json; json.load(open('mcp.json'))" 2>/dev/null; then
        print_status "ok" "MCP configuration valid"
    else
        print_status "error" "MCP configuration invalid"
    fi
else
    print_status "warn" "No MCP configuration found (optional)"
fi

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           ✅ INTEGRATION SETUP COMPLETE                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Integration features enabled:"
echo "• OpenTelemetry tracing → http://localhost:4320"
echo "• MCP server support (if configured)"
echo ""
echo "Run ./run.sh to start ULTRON Agent with all integrations"
echo ""
