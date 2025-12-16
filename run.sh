#!/bin/bash
# ════════════════════════════════════════════════════════════════════════
# ULTRON AGENT 3.0 - UBUNTU LAUNCHER
# ════════════════════════════════════════════════════════════════════════
# This script:
#   - Starts Ollama AI backend
#   - Launches Web GUI and API servers
#   - Monitors service health
#   - Opens browser to Web GUI
#
# FEATURES:
#   ✓ Automatic service startup
#   ✓ Health checking before completion
#   ✓ Startup time tracking
#   ✓ Clean shutdown on exit
# ════════════════════════════════════════════════════════════════════════

set -e  # Exit on error
trap cleanup EXIT INT TERM

# ──────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────

PYTHON_CMD="python3"
OLLAMA_CMD="ollama"
LOG_FILE="ultron.log"

# CRITICAL PORTS (must match API server configuration)
OLLAMA_PORT=11434
WEB_GUI_PORT=8080
API_SERVER_PORT=5000

# AI MODEL CONFIGURATION
# PRIMARY: llava:7b (stable, fast, multimodal) - RECOMMENDED
# FALLBACK: deepseek-r1:14b (advanced reasoning, may timeout)
OLLAMA_MODEL="llava:7b"
FALLBACK_MODEL="deepseek-r1:14b"

# Process IDs for cleanup
WEB_GUI_PID=""
API_SERVER_PID=""
OLLAMA_PID=""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ──────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              ULTRON AGENT 3.0 - LAUNCHER                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "ok" ]; then
        echo -e "      ${GREEN}✓${NC} $message"
    elif [ "$status" = "warn" ]; then
        echo -e "      ${YELLOW}⚠${NC} $message"
    elif [ "$status" = "error" ]; then
        echo -e "      ${RED}✗${NC} $message"
    else
        echo -e "      $message"
    fi
}

cleanup() {
    echo ""
    log "🛑 Shutting down ULTRON services..."

    # Kill Web GUI
    if [ -n "$WEB_GUI_PID" ] && kill -0 "$WEB_GUI_PID" 2>/dev/null; then
        kill -TERM "$WEB_GUI_PID" 2>/dev/null || true
        print_status "ok" "Web GUI stopped"
    fi

    # Kill API Server
    if [ -n "$API_SERVER_PID" ] && kill -0 "$API_SERVER_PID" 2>/dev/null; then
        kill -TERM "$API_SERVER_PID" 2>/dev/null || true
        print_status "ok" "API Server stopped"
    fi

    # Optionally kill Ollama (comment out if you want it to keep running)
    # if [ -n "$OLLAMA_PID" ] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
    #     kill -TERM "$OLLAMA_PID" 2>/dev/null || true
    #     print_status "ok" "Ollama stopped"
    # fi

    # Kill any stray Python processes related to ULTRON
    pkill -f "web_gui_server.py" 2>/dev/null || true
    pkill -f "api_server.py" 2>/dev/null || true

    echo -e "${GREEN}✓ All services terminated${NC}"
    exit 0
}

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s -m 1 "$url" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    return 1
}

# ──────────────────────────────────────────────────────────────────────
# INITIALIZATION
# ──────────────────────────────────────────────────────────────────────

clear
print_header
log "ULTRON Launcher starting..."
echo "[INFO] Startup sequence initiated..."
echo ""

START_TIME=$(date +%s)

# ──────────────────────────────────────────────────────────────────────
# STEP 1: CLEANUP - Kill existing processes
# ──────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[1/6] 🧹 Cleanup existing processes...${NC}"
pkill -f "web_gui_server.py" 2>/dev/null || true
pkill -f "api_server.py" 2>/dev/null || true
sleep 1
print_status "ok" "Cleaned up stale processes"
echo ""

# ──────────────────────────────────────────────────────────────────────
# STEP 2: PREFLIGHT CHECKS
# ──────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[2/6] ✓ Preflight checks...${NC}"
PREFLIGHT_FAIL=0

if [ ! -f "web_gui_server.py" ]; then
    print_status "error" "web_gui_server.py missing"
    PREFLIGHT_FAIL=1
fi

if [ ! -f "main.py" ]; then
    print_status "error" "main.py missing"
    PREFLIGHT_FAIL=1
fi

if [ ! -f "ultron_config.json" ]; then
    print_status "warn" "Config missing (using defaults)"
fi

if [ $PREFLIGHT_FAIL -eq 1 ]; then
    echo -e "${RED}✗ CRITICAL FILES MISSING${NC}"
    exit 1
fi

print_status "ok" "All critical files present"
echo ""

# ──────────────────────────────────────────────────────────────────────
# STEP 3: PYTHON VERIFICATION
# ──────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[3/6] 🐍 Python verification...${NC}"
if ! command -v $PYTHON_CMD &> /dev/null; then
    print_status "error" "Python3 not found in PATH"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_status "ok" "Python $PYTHON_VERSION available"
echo ""

# ──────────────────────────────────────────────────────────────────────
# STEP 4: OLLAMA STARTUP (CRITICAL)
# ──────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[4/6] 🤖 Ollama AI backend startup...${NC}"

# Check if Ollama is installed
if ! command -v $OLLAMA_CMD &> /dev/null; then
    print_status "error" "Ollama not installed"
    echo ""
    echo "Please install Ollama:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    exit 1
fi

# Check if Ollama is already running
if curl -s -m 1 "http://localhost:$OLLAMA_PORT/api/tags" >/dev/null 2>&1; then
    print_status "ok" "Already running"
else
    # Start Ollama in background
    $OLLAMA_CMD serve > /dev/null 2>&1 &
    OLLAMA_PID=$!

    # Wait for Ollama to be ready
    if wait_for_service "http://localhost:$OLLAMA_PORT/api/tags" "Ollama"; then
        print_status "ok" "Started successfully"
    else
        print_status "warn" "Ollama timeout - continuing anyway"
    fi
fi

print_status "ok" "Ollama responsive at http://localhost:$OLLAMA_PORT"
echo ""

# ──────────────────────────────────────────────────────────────────────
# STEP 5: MODEL VERIFICATION
# ──────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[5/6] 🧠 AI model verification...${NC}"

if $OLLAMA_CMD list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
    print_status "ok" "Model: $OLLAMA_MODEL"
elif $OLLAMA_CMD list 2>/dev/null | grep -q "$FALLBACK_MODEL"; then
    OLLAMA_MODEL="$FALLBACK_MODEL"
    print_status "ok" "Using fallback: $FALLBACK_MODEL"
else
    print_status "warn" "No models available - please install: ollama pull llava:7b"
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# STEP 6: SERVICE STARTUP
# ──────────────────────────────────────────────────────────────────────

echo -e "${BLUE}[6/6] 🚀 Service startup and health check...${NC}"

# Start Web GUI
$PYTHON_CMD web_gui_server.py > logs/web_gui.log 2>&1 &
WEB_GUI_PID=$!
sleep 1

# Start API Server
$PYTHON_CMD api_server.py > logs/api_server.log 2>&1 &
API_SERVER_PID=$!

print_status "ok" "Web GUI (port $WEB_GUI_PORT) launched"
print_status "ok" "API Server (port $API_SERVER_PORT) launched"
echo ""

# Wait for services to initialize
sleep 3
echo "      Checking service health..."

if curl -s -m 1 "http://localhost:$WEB_GUI_PORT/" >/dev/null 2>&1; then
    print_status "ok" "Web GUI HEALTHY"
else
    print_status "warn" "Web GUI initializing..."
fi

if curl -s -m 1 "http://localhost:$API_SERVER_PORT/health" >/dev/null 2>&1; then
    print_status "ok" "API Server HEALTHY"
else
    print_status "warn" "API Server initializing..."
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# STARTUP COMPLETE - DISPLAY STATUS
# ──────────────────────────────────────────────────────────────────────

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           ✅ ULTRON AGENT 3.0 - STARTUP COMPLETE            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo " 🚀 STARTUP TIME: ${DURATION} seconds"
echo " 🤖 AI MODEL: $OLLAMA_MODEL"
echo ""
echo " 🌐 WEB GUI:      http://localhost:$WEB_GUI_PORT/"
echo " API SERVER:      http://localhost:$API_SERVER_PORT/"
echo " 🤖 OLLAMA:       http://localhost:$OLLAMA_PORT/"
echo ""
echo " 📝 LOGS:         $LOG_FILE"
echo "                  logs/web_gui.log"
echo "                  logs/api_server.log"
echo " ⏸️  Press Ctrl+C to stop all services"
echo ""
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

log "Startup complete in ${DURATION}s"

# ──────────────────────────────────────────────────────────────────────
# LAUNCH BROWSER TO WEB GUI
# ──────────────────────────────────────────────────────────────────────

echo "🌐 Launching Web GUI in default browser..."
GUI_URL="http://localhost:$WEB_GUI_PORT/"

if command -v xdg-open &> /dev/null; then
    xdg-open "$GUI_URL" 2>/dev/null &
    print_status "ok" "Opened in default browser"
elif command -v gnome-open &> /dev/null; then
    gnome-open "$GUI_URL" 2>/dev/null &
    print_status "ok" "Opened in default browser"
else
    print_status "warn" "Could not open browser automatically"
    echo "      Please open: $GUI_URL"
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# END OF STARTUP - KEEP ALIVE
# ──────────────────────────────────────────────────────────────────────

sleep 2
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ULTRON services are running. Press Ctrl+C to stop."
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Keep the script running and wait for SIGINT/SIGTERM
while true; do
    sleep 60
    # Optionally check if services are still running
    if [ -n "$WEB_GUI_PID" ] && ! kill -0 "$WEB_GUI_PID" 2>/dev/null; then
        log "WARNING: Web GUI process died unexpectedly"
    fi
    if [ -n "$API_SERVER_PID" ] && ! kill -0 "$API_SERVER_PID" 2>/dev/null; then
        log "WARNING: API Server process died unexpectedly"
    fi
done
