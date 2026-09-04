#!/bin/bash

echo "🎤 ULTRON Microphone Fix"
echo "========================"
echo ""

# Check current groups
echo "Current groups: $(groups)"
echo ""

# Add user to audio group
echo "Adding user to audio group..."
sudo usermod -a -G audio $USER

if [ $? -eq 0 ]; then
    echo "✅ Successfully added $USER to audio group"
else
    echo "❌ Failed to add user to audio group"
    exit 1
fi

# Set proper permissions on audio devices
echo ""
echo "Setting audio device permissions..."
sudo chmod 666 /dev/snd/* 2>/dev/null || true

echo ""
echo "🎤 MICROPHONE FIX COMPLETE"
echo "=========================="
echo ""
echo "⚠️  IMPORTANT: You must LOGOUT and LOGIN again (or reboot)"
echo "   for the audio group changes to take effect."
echo ""
echo "After logout/login, test with:"
echo "  arecord -f cd -t wav -d 5 test.wav"
echo ""