#!/bin/bash
# ════════════════════════════════════════════════════════════════════════
# ULTRON AGENT 3.0 - Ubuntu Setup Script
# ════════════════════════════════════════════════════════════════════════
# This script sets up the ULTRON Agent environment on Ubuntu/Debian systems
# ════════════════════════════════════════════════════════════════════════

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         ULTRON AGENT 3.0 - Ubuntu Setup Script            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "ok" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}✗${NC} $message"
    else
        echo -e "$message"
    fi
}

print_header

echo ""
echo "This script will install and configure ULTRON Agent 3.0"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# ──────────────────────────────────────────────────────────────────────
# STEP 1: System Updates
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[1/6] Updating system packages...${NC}"
sudo apt-get update -qq
print_status "ok" "System packages updated"

# ──────────────────────────────────────────────────────────────────────
# STEP 2: Install Python and Dependencies
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[2/6] Installing Python and build dependencies...${NC}"

# Install Python and essential tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    curl \
    wget \
    git \
    lsof \
    portaudio19-dev \
    > /dev/null 2>&1

print_status "ok" "Python $(python3 --version | awk '{print $2}') installed"

# ──────────────────────────────────────────────────────────────────────
# STEP 3: Install Ollama
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[3/6] Installing Ollama AI backend...${NC}"

if command -v ollama &> /dev/null; then
    print_status "ok" "Ollama already installed ($(ollama --version))"
else
    curl -fsSL https://ollama.com/install.sh | sh
    print_status "ok" "Ollama installed successfully"
fi

# Start Ollama service
sudo systemctl enable ollama 2>/dev/null || true
sudo systemctl start ollama 2>/dev/null || true

# If systemctl not available, start manually
if ! systemctl is-active --quiet ollama 2>/dev/null; then
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

print_status "ok" "Ollama service running"

# ──────────────────────────────────────────────────────────────────────
# STEP 4: Install AI Models
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[4/6] Installing AI models (this may take a while)...${NC}"

# Pull primary model
if ollama list 2>/dev/null | grep -q "llava:7b"; then
    print_status "ok" "Model llava:7b already installed"
else
    echo "   Downloading llava:7b (4.7GB)..."
    ollama pull llava:7b
    print_status "ok" "Model llava:7b installed"
fi

# ──────────────────────────────────────────────────────────────────────
# STEP 5: Create Virtual Environment
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[5/6] Setting up Python virtual environment...${NC}"

if [ -d "venv" ]; then
    print_status "warn" "Virtual environment already exists"
else
    python3 -m venv venv
    print_status "ok" "Virtual environment created"
fi

# Activate and install dependencies
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1
print_status "ok" "pip upgraded"

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "   Installing Python packages (this may take a few minutes)..."
    pip install -r requirements.txt > /dev/null 2>&1
    print_status "ok" "Python dependencies installed"
else
    print_status "warn" "requirements.txt not found - skipping package installation"
fi

# ──────────────────────────────────────────────────────────────────────
# STEP 6: Create Necessary Directories
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[6/6] Creating directories and configuration...${NC}"

# Create log directories
mkdir -p logs cache/voice cache/web_search screenshots
print_status "ok" "Directories created"

# Check config file
if [ ! -f "ultron_config.json" ]; then
    print_status "warn" "ultron_config.json not found - will use defaults"
else
    print_status "ok" "Configuration file found"
fi

# Make run script executable
chmod +x run.sh 2>/dev/null || true
chmod +x setup_integrations.sh 2>/dev/null || true
print_status "ok" "Scripts made executable"

# Run integration setup
if [ -f "setup_integrations.sh" ]; then
    echo "   Setting up integrations (tracing, MCP)..."
    ./setup_integrations.sh > /dev/null 2>&1
    print_status "ok" "Integrations configured"
fi

# ──────────────────────────────────────────────────────────────────────
# Setup Complete
# ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           ✅ ULTRON AGENT 3.0 - SETUP COMPLETE              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "2. Start ULTRON Agent:"
echo "   ${YELLOW}./run.sh${NC}"
echo ""
echo "   Or for development mode:"
echo "   ${YELLOW}python3 main.py${NC}"
echo ""
echo "3. Access Web GUI at:"
echo "   ${YELLOW}http://localhost:8080${NC}"
echo ""
echo "Additional configuration:"
echo "- Edit ultron_config.json for API keys and settings"
echo "- Check logs/ directory for troubleshooting"
echo ""
