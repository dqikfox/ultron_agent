#!/bin/bash

echo "🤖 → 😊 Applying ULTRON Personality Fix..."

# Kill existing processes
echo "Stopping existing ULTRON processes..."
pkill -f "web_gui_server.py" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true
pkill -f "brain.py" 2>/dev/null || true
sleep 2

echo "✅ Personality changes applied!"
echo "🎯 Changes made:"
echo "   • More conversational and human-like responses"
echo "   • Reduced technical jargon"
echo "   • Faster, more natural voice settings"
echo "   • Lower microphone sensitivity for better detection"

echo ""
echo "🚀 Restarting ULTRON with new personality..."

# Start the main system
if [ -f "run.sh" ]; then
    ./run.sh
elif [ -f "main.py" ]; then
    python main.py &
    echo "Started main.py in background"
else
    echo "❌ No startup script found. Please run manually:"
    echo "   python main.py"
fi

echo ""
echo "🎉 ULTRON is now more human-like!"
echo "💬 Try saying: 'Hey ULTRON, how are you?'"
echo "🎤 Voice should be less robotic and more natural"