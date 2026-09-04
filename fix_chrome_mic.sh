#!/bin/bash
# Fix Chrome Microphone Access on Linux

echo "🔧 Fixing Chrome Microphone Access..."

# 1. Restart PulseAudio/PipeWire
echo "1. Restarting audio system..."
systemctl --user restart pipewire pipewire-pulse 2>/dev/null || pulseaudio -k && pulseaudio --start

# 2. Set default source
echo "2. Setting default microphone..."
pactl set-default-source alsa_input.platform-snd_aloop.0.analog-stereo

# 3. Unmute and set volume
echo "3. Unmuting microphone..."
pactl set-source-mute @DEFAULT_SOURCE@ 0
pactl set-source-volume @DEFAULT_SOURCE@ 80%

# 4. Test microphone
echo "4. Testing microphone (3 seconds)..."
arecord -d 3 -f cd /tmp/test.wav 2>/dev/null && echo "✅ Microphone working!" || echo "❌ Microphone test failed"

echo ""
echo "✅ Audio system restarted"
echo ""
echo "Now do this:"
echo "1. Close ALL Chrome windows completely"
echo "2. Restart Chrome"
echo "3. Go to localhost:8080"
echo "4. Click 'Allow' when prompted"
