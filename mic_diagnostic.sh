#!/bin/bash

echo "🎤 MICROPHONE DIAGNOSTIC TOOL"
echo "============================="

# Check audio devices
echo "1. Audio Hardware Detection:"
lsusb | grep -i audio
lspci | grep -i audio
echo ""

# Check ALSA devices
echo "2. ALSA Recording Devices:"
arecord -l
echo ""

# Check PulseAudio/PipeWire sources
echo "3. Audio Sources:"
if command -v pactl >/dev/null; then
    pactl list sources short
elif command -v pw-cli >/dev/null; then
    pw-cli list-objects | grep -A5 "Audio/Source"
fi
echo ""

# Test microphone
echo "4. Microphone Test (5 seconds):"
echo "Speak now..."
arecord -f cd -t wav -d 5 /tmp/mic_test.wav 2>/dev/null
if [ -s /tmp/mic_test.wav ]; then
    echo "✅ Recording successful"
    aplay /tmp/mic_test.wav 2>/dev/null
    rm /tmp/mic_test.wav
else
    echo "❌ Recording failed"
fi
echo ""

# Check permissions
echo "5. Audio Permissions:"
groups | grep audio && echo "✅ In audio group" || echo "❌ Not in audio group"
ls -la /dev/snd/
echo ""

# Check processes using audio
echo "6. Audio Device Usage:"
lsof /dev/snd/* 2>/dev/null | head -10
echo ""

echo "🔧 QUICK FIXES:"
echo "sudo usermod -a -G audio $USER"
echo "sudo chmod 666 /dev/snd/*"
echo "alsamixer  # Unmute microphone"
echo "pavucontrol  # GUI audio control"