#!/bin/bash

echo "🤖 → 😊 Restarting ULTRON with Human Personality..."

# Kill existing processes
echo "Stopping ULTRON processes..."
pkill -f "web_gui_server.py" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true
pkill -f "brain.py" 2>/dev/null || true
sleep 3

echo "✅ Processes stopped"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start ULTRON with new personality
echo "🚀 Starting ULTRON with human-like personality..."
python main.py &
MAIN_PID=$!

sleep 2

if kill -0 "$MAIN_PID" 2>/dev/null; then
    echo "✅ ULTRON started successfully [PID: $MAIN_PID]"
    echo ""
    echo "🎉 PERSONALITY CHANGES APPLIED!"
    echo "💬 ULTRON should now be:"
    echo "   • More conversational and friendly"
    echo "   • Less robotic and technical"
    echo "   • Using casual language"
    echo ""
    echo "🎤 MICROPHONE FIX NEEDED:"
    echo "   Run: sudo usermod -a -G audio $USER"
    echo "   Then logout/login or reboot"
else
    echo "❌ Failed to start ULTRON"
    echo "Try: python main.py"
fi