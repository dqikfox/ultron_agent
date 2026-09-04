#!/bin/bash
# Quick verification script for ULTRON Agent Ubuntu setup

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         ULTRON Agent - System Verification               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $1 is in use"
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

echo "System Requirements:"
check_command python3
check_command pip3
check_command curl
check_command git
echo ""

echo "ULTRON Dependencies:"
check_command ollama
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not created yet"
fi
echo ""

echo "Port Availability:"
check_port 8080  # Web GUI
check_port 5000  # API Server
check_port 11434 # Ollama
echo ""

echo "Files:"
if [ -f "ultron_config.json" ]; then
    echo -e "${GREEN}✓${NC} ultron_config.json exists"
else
    echo -e "${YELLOW}⚠${NC} ultron_config.json not found (will use defaults)"
fi

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt exists"
else
    echo -e "${RED}✗${NC} requirements.txt missing"
fi
echo ""

echo "Ollama Models:"
if command -v ollama &> /dev/null; then
    if ollama list 2>/dev/null | grep -q "llava:7b"; then
        echo -e "${GREEN}✓${NC} llava:7b model installed"
    else
        echo -e "${YELLOW}⚠${NC} llava:7b model not found - will be downloaded"
    fi
else
    echo -e "${YELLOW}⚠${NC} Ollama not installed - setup script will install it"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "Next steps:"
echo ""
if [ ! -d "venv" ] || ! command -v ollama &> /dev/null; then
    echo "1. Run setup script:"
    echo "   ./setup_ubuntu.sh"
    echo ""
fi
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Start ULTRON:"
echo "   ./run.sh"
echo "═══════════════════════════════════════════════════════════════"
