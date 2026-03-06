#!/bin/bash
# System Speaker Hardware Diagnostic

echo "🔧 LAPTOP SPEAKER HARDWARE DIAGNOSTIC"
echo "======================================"

# Check hardware detection
echo "🔍 Hardware Detection:"
lspci | grep -i audio
lsusb | grep -i audio

# Check ALSA cards
echo -e "\n🎵 ALSA Sound Cards:"
cat /proc/asound/cards

# Check if speakers are detected
echo -e "\n🔊 Speaker Detection:"
aplay -l | grep -E "(card|device)"

# Check mixer controls
echo -e "\n🎛️ Mixer Controls:"
amixer scontrols

# Check current volumes
echo -e "\n🔊 Current Volumes:"
amixer get Master
amixer get Speaker 2>/dev/null || echo "No Speaker control"
amixer get Headphone 2>/dev/null || echo "No Headphone control"

# Check if anything is muted
echo -e "\n🔇 Mute Status:"
amixer get Master | grep -o '\[on\]\|\[off\]'

# Test with direct ALSA
echo -e "\n🎵 Testing Direct ALSA Output:"
echo "Testing card 1, device 0 (laptop speakers)..."
timeout 3 speaker-test -D hw:1,0 -c 2 -t sine -f 1000 2>/dev/null || echo "Direct ALSA test failed"

# Check PulseAudio/PipeWire status
echo -e "\n🔄 Audio System Status:"
systemctl --user status pipewire 2>/dev/null | head -3
systemctl --user status pulseaudio 2>/dev/null | head -3 || echo "PulseAudio not running"

# Hardware volume controls
echo -e "\n🔧 Hardware Controls:"
echo "Try these commands to fix hardware issues:"
echo "1. Unmute everything: sudo alsactl restore"
echo "2. Reset audio: pulseaudio -k && pulseaudio --start"
echo "3. Check physical volume keys on laptop"
echo "4. Try headphones to test if audio system works"