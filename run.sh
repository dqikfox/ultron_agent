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
FRONTEND_PORT=5175
NVIDIA_PORT=8000

# AI MODEL CONFIGURATION
# PRIMARY: dolphin3:latest (uncensored, fast, multimodal) - RECOMMENDED
# FALLBACK: llava:7b (stable, fast, multimodal)
OLLAMA_MODEL="dolphin3:latest"
FALLBACK_MODEL="llava:7b"

# OPTIONAL SERVICES (set to "yes" to enable)
# Frontend Server (Alternative UI on port 5175)
ENABLE_FRONTEND_SERVER=yes
# NVIDIA Enhanced Server (Enhanced AI chat on port 8000)
ENABLE_NVIDIA_SERVER=yes
# Consciousness Mode (Enable consciousness-driven NPC behavior)
ENABLE_CONSCIOUSNESS=yes

# Process IDs for cleanup
WEB_GUI_PID=""
API_SERVER_PID=""
OLLAMA_PID=""
FRONTEND_PID=""
NVIDIA_PID=""

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

    # Kill Frontend Server (if enabled)
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
        print_status "ok" "Frontend Server stopped"
    fi

    # Kill NVIDIA Server (if enabled)
    if [ -n "$NVIDIA_PID" ] && kill -0 "$NVIDIA_PID" 2>/dev/null; then
        kill -TERM "$NVIDIA_PID" 2>/dev/null || true
        print_status "ok" "NVIDIA Server stopped"
    fi

    # Optionally kill Ollama (commented out - keeps running for other apps)
    # if [ -n "$OLLAMA_PID" ] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
    #     kill -TERM "$OLLAMA_PID" 2>/dev/null || true
    #     print_status "ok" "Ollama stopped"
    # fi

    # Kill any stray Python processes related to ULTRON
    pkill -f "web_gui_server.py" 2>/dev/null || true
    pkill -f "api_server.py" 2>/dev/null || true
    pkill -f "frontend_server.py" 2>/dev/null || true
    pkill -f "nvidia_enhanced_ultron.py" 2>/dev/null || true

    echo -e "${GREEN}✓ All services terminated${NC}"
    exit 0
}

check_port() {
    local port=$1
    if ss -tuln 2>/dev/null | grep -q ":$port " || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        return 0
    else
        return 1
    fi
}

wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=8
    local attempt=0

    echo -ne "      ${YELLOW}⏳${NC} $name starting"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -m 1 "$url" >/dev/null 2>&1; then
            echo -e "\r      ${GREEN}✓${NC} $name ${GREEN}READY${NC}                    "
            return 0
        fi
        echo -ne "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e "\r      ${YELLOW}⚠${NC} $name ${YELLOW}TIMEOUT${NC} (continuing...)    "
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

if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    # Always activate venv, even if already in a venv shell
    VENV_PATH="$(pwd)/venv"
    if [ "$VIRTUAL_ENV" != "$VENV_PATH" ]; then
        source venv/bin/activate
        print_status "ok" "Virtual environment activated"
    else
        print_status "ok" "Virtual environment already active"
    fi
elif [ -d "env" ] && [ -f "env/bin/activate" ]; then
    VENV_PATH="$(pwd)/env"
    if [ "$VIRTUAL_ENV" != "$VENV_PATH" ]; then
        source env/bin/activate
        print_status "ok" "Virtual environment activated"
    else
        print_status "ok" "Virtual environment already active"
    fi
else
    print_status "warn" "No virtual environment found (venv/ or env/)"
fi
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

echo -e "${BLUE}[6/6] 🚀 Service startup...${NC}"

# Ensure logs directory exists
mkdir -p logs

# Start Web GUI Server (CRITICAL)
echo -ne "      ${CYAN}►${NC} Launching Web GUI (port $WEB_GUI_PORT)..."
$PYTHON_CMD web_gui_server.py > logs/web_gui.log 2>&1 &
WEB_GUI_PID=$!
sleep 2
if kill -0 "$WEB_GUI_PID" 2>/dev/null; then
    echo -e "\r      ${GREEN}✓${NC} Web GUI launched [PID: $WEB_GUI_PID]         "
else
    echo -e "\r      ${RED}✗${NC} Web GUI FAILED to start                "
fi

# Start API Server (CRITICAL)
echo -ne "      ${CYAN}►${NC} Launching API Server (port $API_SERVER_PORT)..."
$PYTHON_CMD api_server.py > logs/api_server.log 2>&1 &
API_SERVER_PID=$!
sleep 2
if kill -0 "$API_SERVER_PID" 2>/dev/null; then
    echo -e "\r      ${GREEN}✓${NC} API Server launched [PID: $API_SERVER_PID]     "
else
    echo -e "\r      ${RED}✗${NC} API Server FAILED to start             "
fi

# Start optional services
if [ "$ENABLE_FRONTEND_SERVER" = "yes" ] && [ -f "frontend_server.py" ]; then
    echo -ne "      ${CYAN}►${NC} Launching Frontend (port $FRONTEND_PORT)..."
    $PYTHON_CMD frontend_server.py > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    sleep 1
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "\r      ${GREEN}✓${NC} Frontend launched [PID: $FRONTEND_PID]        "
    else
        echo -e "\r      ${RED}✗${NC} Frontend FAILED to start               "
    fi
fi

if [ "$ENABLE_NVIDIA_SERVER" = "yes" ] && [ -f "nvidia_enhanced_ultron.py" ]; then
    echo -ne "      ${CYAN}►${NC} Launching NVIDIA (port $NVIDIA_PORT)..."
    $PYTHON_CMD nvidia_enhanced_ultron.py > logs/nvidia.log 2>&1 &
    NVIDIA_PID=$!
    sleep 1
    if kill -0 "$NVIDIA_PID" 2>/dev/null; then
        echo -e "\r      ${GREEN}✓${NC} NVIDIA launched [PID: $NVIDIA_PID]           "
    else
        echo -e "\r      ${RED}✗${NC} NVIDIA FAILED to start                 "
    fi
fi

echo ""

# ──────────────────────────────────────────────────────────────────────
# STARTUP COMPLETE
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
echo " ${CYAN}════ SERVICES ════${NC}"
echo " 🌐 WEB GUI:      http://localhost:$WEB_GUI_PORT/"
echo " 📡 API SERVER:   http://localhost:$API_SERVER_PORT/"
echo " 🤖 OLLAMA:       http://localhost:$OLLAMA_PORT/"

if [ "$ENABLE_FRONTEND_SERVER" = "yes" ]; then
    echo " 🎨 FRONTEND:     http://localhost:$FRONTEND_PORT/"
fi
if [ "$ENABLE_NVIDIA_SERVER" = "yes" ]; then
    echo " 🚀 NVIDIA:       http://localhost:$NVIDIA_PORT/"
fi

echo ""
echo " ${YELLOW}⏸️  Press Ctrl+C to stop all services${NC}"
echo ""

log "Startup complete in ${DURATION}s"

# Launch browser
echo "🌐 Opening Web GUI..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$WEB_GUI_PORT/" 2>/dev/null &
elif command -v gnome-open &> /dev/null; then
    gnome-open "http://localhost:$WEB_GUI_PORT/" 2>/dev/null &
fi

# Keep alive
while true; do
    sleep 60
    # Monitor services
    if [ -n "$WEB_GUI_PID" ] && ! kill -0 "$WEB_GUI_PID" 2>/dev/null; then
        log "⚠️  Web GUI died unexpectedly"
    fi
    if [ -n "$API_SERVER_PID" ] && ! kill -0 "$API_SERVER_PID" 2>/dev/null; then
        log "⚠️  API Server died unexpectedly"
    fi
done

echo -e "${BLUE}[6/6] 🚀 Service startup and health check...${NC}"

# Ensure logs directory exists
mkdir -p logs

# Start Web GUI (CRITICAL - includes consciousness endpoints)
echo -ne "      ${CYAN}►${NC} Launching Web GUI (port $WEB_GUI_PORT)..."
$PYTHON_CMD web_gui_server.py > logs/web_gui.log 2>&1 &
WEB_GUI_PID=$!
sleep 0.5
if kill -0 "$WEB_GUI_PID" 2>/dev/null; then
    echo -e "\r      ${GREEN}✓${NC} Web GUI launched ${GREEN}successfully${NC} [PID: $WEB_GUI_PID]         "
else
    echo -e "\r      ${RED}✗${NC} Web GUI ${RED}FAILED${NC} to start                       "
fi

# Start API Server (CRITICAL)
echo -ne "      ${CYAN}►${NC} Launching API Server (port $API_SERVER_PORT)..."
$PYTHON_CMD api_server.py > logs/api_server.log 2>&1 &
API_SERVER_PID=$!
sleep 0.5
if kill -0 "$API_SERVER_PID" 2>/dev/null; then
    echo -e "\r      ${GREEN}✓${NC} API Server launched ${GREEN}successfully${NC} [PID: $API_SERVER_PID]     "
else
    echo -e "\r      ${RED}✗${NC} API Server ${RED}FAILED${NC} to start                   "
fi

# Start optional Frontend Server (alternative UI)
if [ "$ENABLE_FRONTEND_SERVER" = "yes" ] && [ -f "frontend_server.py" ]; then
    echo -ne "      ${CYAN}►${NC} Launching Frontend Server (port $FRONTEND_PORT)..."
    $PYTHON_CMD frontend_server.py > logs/frontend_server.log 2>&1 &
    FRONTEND_PID=$!
    sleep 0.5
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "\r      ${GREEN}✓${NC} Frontend Server launched ${GREEN}successfully${NC} [PID: $FRONTEND_PID]"
    else
        echo -e "\r      ${RED}✗${NC} Frontend Server ${RED}FAILED${NC} to start              "
    fi
fi

# Start optional NVIDIA Enhanced Server
if [ "$ENABLE_NVIDIA_SERVER" = "yes" ] && [ -f "nvidia_enhanced_ultron.py" ]; then
    echo -ne "      ${CYAN}►${NC} Launching NVIDIA Server (port $NVIDIA_PORT)..."
    $PYTHON_CMD nvidia_enhanced_ultron.py > logs/nvidia_server.log 2>&1 &
    NVIDIA_PID=$!
    sleep 0.5
    if kill -0 "$NVIDIA_PID" 2>/dev/null; then
        echo -e "\r      ${GREEN}✓${NC} NVIDIA Server launched ${GREEN}successfully${NC} [PID: $NVIDIA_PID]   "
    else
        echo -e "\r      ${RED}✗${NC} NVIDIA Server ${RED}FAILED${NC} to start                 "
    fi
fi

echo ""

# Wait for services to initialize with visual progress
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "  ${YELLOW}⏳ Waiting for services to initialize...${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

sleep 2


# Check Web GUI health
wait_for_service "http://localhost:$WEB_GUI_PORT/" "Web GUI Root"
wait_for_service "http://localhost:$WEB_GUI_PORT/api/status" "Web GUI /api/status"

# Check API Server health
wait_for_service "http://localhost:$API_SERVER_PORT/health" "API Server /health"
wait_for_service "http://localhost:$API_SERVER_PORT/api/status" "API Server /api/status"
wait_for_service "http://localhost:$API_SERVER_PORT/api/llm/chat" "API Server /api/llm/chat"

# Check consciousness system if enabled
if [ "$ENABLE_CONSCIOUSNESS" = "yes" ]; then
    echo -ne "      ${YELLOW}⏳${NC} Consciousness System checking"
    if curl -s -m 2 "http://localhost:$WEB_GUI_PORT/api/consciousness/status" >/dev/null 2>&1; then
        CONSCIOUSNESS_STATUS=$(curl -s -m 2 "http://localhost:$WEB_GUI_PORT/api/consciousness/status" | grep -o '"available":[^,]*' | cut -d':' -f2 || echo "unknown")
        if [ "$CONSCIOUSNESS_STATUS" = "true" ]; then
            echo -e "\r      ${GREEN}✓${NC} Consciousness System ${GREEN}AVAILABLE${NC}              "
        else
            echo -e "\r      ${YELLOW}⚠${NC} Consciousness System ${YELLOW}INITIALIZING${NC}...       "
        fi
    else
        echo -e "\r      ${YELLOW}⚠${NC} Consciousness System ${YELLOW}INITIALIZING${NC}...           "
    fi
fi

# Check optional services
if [ "$ENABLE_FRONTEND_SERVER" = "yes" ]; then
    wait_for_service "http://localhost:$FRONTEND_PORT/" "Frontend Server"
fi

if [ "$ENABLE_NVIDIA_SERVER" = "yes" ]; then
    wait_for_service "http://localhost:$NVIDIA_PORT/" "NVIDIA Server"
fi


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
if [ "$ENABLE_CONSCIOUSNESS" = "yes" ]; then
    echo " 🧠 CONSCIOUSNESS: ENABLED (NPC-ready)"
fi
echo ""
echo " ${CYAN}════ CORE SERVICES ════${NC}"
echo " 🌐 WEB GUI:      http://localhost:$WEB_GUI_PORT/  (Pokédex UI + Consciousness API)"
echo " 📡 API SERVER:   http://localhost:$API_SERVER_PORT/  (REST API + WebSocket)"
echo " 🤖 OLLAMA:       http://localhost:$OLLAMA_PORT/  (LLM Backend)"

if [ "$ENABLE_FRONTEND_SERVER" = "yes" ] || [ "$ENABLE_NVIDIA_SERVER" = "yes" ]; then
    echo ""
    echo " ${CYAN}════ OPTIONAL SERVICES ════${NC}"
    if [ "$ENABLE_FRONTEND_SERVER" = "yes" ]; then
        echo " 🎨 FRONTEND:     http://localhost:$FRONTEND_PORT/  (Alternative UI)"
    fi
    if [ "$ENABLE_NVIDIA_SERVER" = "yes" ]; then
        echo " 🚀 NVIDIA:       http://localhost:$NVIDIA_PORT/  (Enhanced AI Chat)"
    fi
fi

echo ""
echo " ${CYAN}════ LOGS & MONITORING ════${NC}"
echo " 📝 MASTER LOG:   $LOG_FILE"
echo " 📊 WEB GUI:      logs/web_gui.log"
echo " 📊 API SERVER:   logs/api_server.log"
if [ "$ENABLE_FRONTEND_SERVER" = "yes" ]; then
    echo " 📊 FRONTEND:     logs/frontend_server.log"
fi
if [ "$ENABLE_NVIDIA_SERVER" = "yes" ]; then
    echo " 📊 NVIDIA:       logs/nvidia_server.log"
fi
echo ""
echo " ${YELLOW}⏸️  Press Ctrl+C to stop all services${NC}"
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

    # Monitor all services and log if any die unexpectedly
    if [ -n "$WEB_GUI_PID" ] && ! kill -0 "$WEB_GUI_PID" 2>/dev/null; then
        log "⚠️  WARNING: Web GUI process died unexpectedly (PID: $WEB_GUI_PID)"
        echo -e "${YELLOW}⚠️  Web GUI service stopped - check logs/web_gui.log${NC}"
    fi

    if [ -n "$API_SERVER_PID" ] && ! kill -0 "$API_SERVER_PID" 2>/dev/null; then
        log "⚠️  WARNING: API Server process died unexpectedly (PID: $API_SERVER_PID)"
        echo -e "${YELLOW}⚠️  API Server stopped - check logs/api_server.log${NC}"
    fi

    if [ "$ENABLE_FRONTEND_SERVER" = "yes" ] && [ -n "$FRONTEND_PID" ] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        log "⚠️  WARNING: Frontend Server died unexpectedly (PID: $FRONTEND_PID)"
    fi

    if [ "$ENABLE_NVIDIA_SERVER" = "yes" ] && [ -n "$NVIDIA_PID" ] && ! kill -0 "$NVIDIA_PID" 2>/dev/null; then
        log "⚠️  WARNING: NVIDIA Server died unexpectedly (PID: $NVIDIA_PID)"
    fi

    # Optional: Auto-restart critical services (commented out by default)
    # Uncomment the lines below to enable automatic service restart
    # if [ -n "$WEB_GUI_PID" ] && ! kill -0 "$WEB_GUI_PID" 2>/dev/null; then
    #     log "🔄 Auto-restarting Web GUI..."
    #     $PYTHON_CMD web_gui_server.py > logs/web_gui.log 2>&1 &
    #     WEB_GUI_PID=$!
    #     print_status "ok" "Web GUI restarted [PID: $WEB_GUI_PID]"
    # fi
    #
    # if [ -n "$API_SERVER_PID" ] && ! kill -0 "$API_SERVER_PID" 2>/dev/null; then
    #     log "🔄 Auto-restarting API Server..."
    #     $PYTHON_CMD api_server.py > logs/api_server.log 2>&1 &
    #     API_SERVER_PID=$!
    #     print_status "ok" "API Server restarted [PID: $API_SERVER_PID]"
    # fi
done
