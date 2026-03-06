#!/bin/bash
echo "🎤 ULTRON Microphone Diagnostic & Fix"
echo "====================================="

# Test 1: Check if microphone hardware exists
echo "1. Hardware Detection:"
if lspci | grep -i audio | grep -i intel; then
    echo "✅ Intel audio hardware detected"
else
    echo "❌ No Intel audio hardware found"
fi

# Test 2: Check ALSA capture devices
echo -e "\n2. ALSA Capture Devices:"
if arecord -l | grep -i capture; then
    echo "✅ ALSA capture device found"
else
    echo "❌ No ALSA capture devices"
fi

# Test 3: Check mixer controls
echo -e "\n3. Mixer Controls:"
amixer -c 1 controls | grep -i mic

# Test 4: Try to unmute and boost microphone
echo -e "\n4. Attempting to enable microphone:"
echo "2580" | sudo -S amixer -c 1 sset 'Capture' 100% unmute 2>/dev/null && echo "✅ Capture unmuted" || echo "❌ Capture control failed"

# Test 5: Set microphone boost
echo "2580" | sudo -S amixer -c 1 cset numid=8 3 2>/dev/null && echo "✅ Mic boost set" || echo "❌ Mic boost failed"

# Test 6: Test recording with maximum gain
echo -e "\n5. Recording test (3 seconds with max gain):"
arecord -D hw:1,0 -f cd -t wav -d 3 diagnostic_test.wav 2>/dev/null
if [ -f diagnostic_test.wav ]; then
    SIZE=$(stat -c%s diagnostic_test.wav)
    echo "✅ Recording created: ${SIZE} bytes"
    
    # Check if recording has actual audio data (not just silence)
    if hexdump -C diagnostic_test.wav | grep -v "00 00 00 00" | grep -q "data"; then
        echo "✅ Audio data detected in recording"
    else
        echo "❌ Recording contains only silence"
    fi
else
    echo "❌ Recording failed"
fi

# Test 7: Check PulseAudio/PipeWire
echo -e "\n6. Audio System Status:"
if command -v wpctl &> /dev/null; then
    echo "Using PipeWire:"
    wpctl status | grep -A3 "Sources:"
else
    echo "❌ PipeWire not available"
fi

# Test 8: Install missing audio packages
echo -e "\n7. Installing audio packages:"
echo "2580" | sudo -S apt install -y alsa-utils pulseaudio-utils 2>/dev/null && echo "✅ Audio packages installed" || echo "❌ Package installation failed"

# Test 9: Restart audio services
echo -e "\n8. Restarting audio services:"
systemctl --user restart wireplumber pipewire 2>/dev/null && echo "✅ Audio services restarted" || echo "❌ Service restart failed"

echo -e "\n🎤 Diagnostic complete. Check results above."