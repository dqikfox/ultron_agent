#!/bin/bash
# Permanent audio device fix for ULTRON Agent

echo "🔧 Setting up permanent audio device configuration..."

# Set laptop speakers as default (not NVIDIA HDMI)
pactl set-default-sink alsa_output.pci-0000_00_1f.3-platform-skl_hda_dsp_generic.HiFi__hw_sofhdadsp__sink

# Set volume to 80%
pactl set-sink-volume @DEFAULT_SINK@ 80%

# Unmute
pactl set-sink-mute @DEFAULT_SINK@ 0

echo "✅ Audio configured for laptop speakers"
echo "🔊 Volume set to 80%"
echo "🎵 TTS will now use laptop speakers by default"