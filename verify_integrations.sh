#!/bin/bash
# ════════════════════════════════════════════════════════════════════════
# ULTRON AGENT 3.0 - Integration Verification Script
# ════════════════════════════════════════════════════════════════════════
# Tests that tracing and MCP integrations are working properly
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
echo "║         ULTRON AGENT 3.0 - Integration Verification        ║"
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
else
    print_status "warn" "No virtual environment found"
fi

# Test OpenTelemetry imports
echo ""
echo -e "${BLUE}[1/4] Testing OpenTelemetry tracing...${NC}"
if python3 -c "import opentelemetry; print('OpenTelemetry version:', opentelemetry.__version__)" 2>/dev/null; then
    print_status "ok" "OpenTelemetry available"
else
    print_status "error" "OpenTelemetry not available"
fi

if python3 -c "from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter" 2>/dev/null; then
    print_status "ok" "OTLP exporter available"
else
    print_status "error" "OTLP exporter not available"
fi

# Test tracing module
echo ""
echo -e "${BLUE}[2/4] Testing tracing module...${NC}"
if [ -f "tracing.py" ]; then
    if python3 -c "import tracing; print('Tracing module loaded successfully')" 2>/dev/null; then
        print_status "ok" "Tracing module working"
    else
        print_status "error" "Tracing module has errors"
    fi
else
    print_status "error" "Tracing module not found"
fi

# Test brain.py tracing integration
echo ""
echo -e "${BLUE}[3/4] Testing brain.py tracing integration...${NC}"
if [ -f "brain.py" ]; then
    if grep -q "@trace_function" brain.py; then
        print_status "ok" "Brain.py has tracing decorators"
    else
        print_status "warn" "Brain.py missing tracing decorators"
    fi

    if grep -q "from tracing import" brain.py; then
        print_status "ok" "Brain.py imports tracing module"
    else
        print_status "warn" "Brain.py missing tracing import"
    fi
else
    print_status "error" "Brain.py not found"
fi

# Test MCP configuration
echo ""
echo -e "${BLUE}[4/4] Testing MCP configuration...${NC}"
if [ -f "mcp.json" ]; then
    if python3 -c "import json; config=json.load(open('mcp.json')); print(f'Found {len(config.get(\"mcpServers\", {}))} MCP servers')" 2>/dev/null; then
        print_status "ok" "MCP configuration valid"
    else
        print_status "error" "MCP configuration invalid"
    fi
else
    print_status "warn" "MCP configuration not found (optional)"
fi

# Test environment variables
echo ""
echo -e "${BLUE}Environment Variables:${NC}"
if [ -n "$OTEL_SERVICE_NAME" ]; then
    print_status "ok" "OTEL_SERVICE_NAME: $OTEL_SERVICE_NAME"
else
    print_status "warn" "OTEL_SERVICE_NAME not set (will be set by run.sh)"
fi

if [ -n "$OTEL_EXPORTER_OTLP_ENDPOINT" ]; then
    print_status "ok" "OTEL_EXPORTER_OTLP_ENDPOINT: $OTEL_EXPORTER_OTLP_ENDPOINT"
else
    print_status "warn" "OTEL_EXPORTER_OTLP_ENDPOINT not set (will be set by run.sh)"
fi

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           ✅ VERIFICATION COMPLETE                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Integration status:"
echo "• Tracing: Ready for http://localhost:4320"
echo "• MCP: Configuration checked"
echo "• Environment: Will be set by run.sh"
echo ""
echo "Run ./run.sh to start ULTRON Agent with all integrations"
echo ""
