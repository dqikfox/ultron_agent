#!/bin/bash
# ULTRON 3.0 Shell Script Test
# This script demonstrates shellcheck functionality

echo "ULTRON 3.0 System Check"

# Check if python is available
if command -v python &> /dev/null; then
    echo "✅ Python is available"
    python --version
else
    echo "❌ Python not found"
fi

# Check for main.py
if [ -f "main.py" ]; then
    echo "✅ main.py found"
else
    echo "❌ main.py not found"
fi

# Check system resources
echo "System Information:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"

echo "ULTRON 3.0 system check complete!"
