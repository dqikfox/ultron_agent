#!/bin/bash

# ULTRON Agent 3.0 Enhanced Startup Script
# Complete service coordination with all enhancements

echo "🚀 ULTRON Agent 3.0 - Enhanced Edition"
echo "========================================"

# Check Python availability
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main_enhanced.py" ]; then
    echo "❌ main_enhanced.py not found. Please run from the project root directory."
    exit 1
fi

# Install dependencies if needed
echo "🔍 Checking dependencies..."
python -c "
import sys
missing = []
try:
    import pyautogui
    import psutil
    import pytest
except ImportError as e:
    missing.append(str(e).split()[-1])

if missing:
    print(f'⚠️  Missing dependencies: {missing}')
    print('📦 Installing missing dependencies...')
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
    print('✅ Dependencies installed')
else:
    print('✅ All dependencies available')
"

# Create logs directory
mkdir -p logs

echo ""
echo "🚀 Starting Enhanced ULTRON Agent..."
echo "   Features: PyAutoGUI + Service Management + Continuous Improvement"
echo ""

# Run the enhanced agent
python main_enhanced.py --enhanced

echo ""
echo "🏁 ULTRON Agent shutdown complete."