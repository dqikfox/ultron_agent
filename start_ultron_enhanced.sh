#!/bin/bash
# Enhanced ULTRON Service Startup Script
# Fixes connection issues and starts all services in correct order

echo "🚀 ULTRON Enhanced Service Startup"
echo "=================================="

# Fix connection configurations first
echo "🔧 Fixing connection configurations..."
python -c "
from connection_config_fixer import ConnectionConfigurationFixer
fixer = ConnectionConfigurationFixer()
results = fixer.apply_automatic_fixes()
print(f'Applied {results["fixes_applied"]} fixes')
"

# Start Ollama first (critical dependency)
echo "🤖 Starting Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    ollama serve &
    echo "  Ollama server starting..."
    sleep 5
else
    echo "  Ollama already running"
fi

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "  ✅ Ollama is ready!"
        break
    fi
    sleep 1
done

# Start web GUI server
echo "🌐 Starting Web GUI server..."
if ! pgrep -f "web_gui_server.py" > /dev/null; then
    python web_gui_server.py &
    echo "  Web GUI server starting..."
    sleep 2
else
    echo "  Web GUI server already running"
fi

# Start agent core
echo "🧠 Starting ULTRON Agent Core..."
if ! pgrep -f "main.py" > /dev/null; then
    python main.py &
    echo "  Agent core starting..."
    sleep 3
else
    echo "  Agent core already running"
fi

# Start monitoring
echo "📊 Starting monitoring dashboard..."
if ! pgrep -f "monitoring_dashboard.py" > /dev/null; then
    python monitoring_dashboard.py &
    echo "  Monitoring dashboard starting..."
    sleep 2
else
    echo "  Monitoring dashboard already running"
fi

echo ""
echo "✅ ULTRON Services Startup Complete!"
echo ""
echo "🌐 Access Points:"
echo "  📊 Dashboard:     http://localhost:9000"  
echo "  🤖 Web GUI:       http://localhost:8080"
echo "  📡 Ollama API:    http://localhost:11434"
echo ""
echo "🔍 Check service status:"
echo "  python -c \"from service_manager import get_service_manager; print(get_service_manager().get_service_status_report())\"
