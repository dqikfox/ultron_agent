#!/bin/bash
echo "🔧 Hardware Microphone Fix"
echo "=========================="

# Force reload audio drivers
echo "2580" | sudo -S modprobe -r snd_hda_intel
echo "2580" | sudo -S modprobe snd_hda_intel

# Restart audio services
systemctl --user restart wireplumber pipewire pipewire-pulse 2>/dev/null || true

# Check if mic appears
sleep 2
echo "Checking for microphone..."
wpctl status | grep -A5 "Sources:"