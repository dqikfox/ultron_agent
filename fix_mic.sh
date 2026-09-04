#!/bin/bash

echo "🔧 FIXING MICROPHONE PERMISSIONS..."

# Add user to audio group
echo "Adding user to audio group..."
sudo usermod -a -G audio $USER

# Set audio device permissions
echo "Setting audio device permissions..."
sudo chmod 666 /dev/snd/*

# Check microphone levels with alsamixer
echo "Opening audio mixer to check microphone levels..."
echo "In alsamixer:"
echo "- Press F4 to show capture devices"
echo "- Use arrow keys to select microphone"
echo "- Press SPACE to unmute (remove 'MM')"
echo "- Use UP arrow to increase volume"
echo "- Press ESC to exit"
echo ""
read -p "Press Enter to open alsamixer..."
alsamixer

echo ""
echo "✅ Microphone fix complete!"
echo "🔄 You may need to logout/login or reboot for group changes to take effect"
echo ""
echo "🧪 Test microphone:"
echo "arecord -f cd -t wav -d 3 test.wav && aplay test.wav"