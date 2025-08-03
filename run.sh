#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PYTHON_CMD="python3" # or "python"
VENV_DIR="venv"

# --- Functions ---

# Function to print colored messages
print_msg() {
    color_code=$1
    shift
    echo -e "\033[${color_code}m$@\033[0m"
}

info() { print_msg "34" "[INFO] $@"; }
warn() { print_msg "33" "[WARN] $@"; }
error() { print_msg "31" "[ERROR] $@"; exit 1; }
success() { print_msg "32" "[SUCCESS] $@"; }

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# --- Main Script ---

info "Starting Ultron Agent 2.0..."

# 1. Check for Python
if ! command_exists $PYTHON_CMD; then
    error "$PYTHON_CMD is not installed or not in PATH. Please install Python 3.8+."
fi
info "Python check passed."

# 2. Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    info "Virtual environment not found. Creating one at '$VENV_DIR'..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    success "Virtual environment created."
fi

info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Install/Upgrade Dependencies
info "Checking and installing dependencies from requirements.txt..."
if pip install -r requirements.txt; then
    success "Dependencies are up to date."
else
    error "Failed to install dependencies. Please check requirements.txt and your network connection."
fi

# 4. Check for .env file
if [ ! -f ".env" ]; then
    warn ".env file not found. Copying from .env.example..."
    warn "Please update .env with your API keys for full functionality."
    cp .env.example .env
fi

# 5. Run the Agent
info "Launching Ultron Agent..."

# Add any command-line arguments here if needed
# For example: python main.py --mode cli
exec $PYTHON_CMD main.py "$@"

