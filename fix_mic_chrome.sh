#!/bin/bash
# Fix Chrome microphone detection

# 1. Add user to audio group
sudo usermod -a -G audio $USER

# 2. Set PipeWire permissions
mkdir -p ~/.config/pipewire
cat > ~/.config/pipewire/pipewire.conf << 'EOF'
context.properties = {
    default.clock.allowed-rates = [ 48000 ]
}
EOF

# 3. Restart audio
systemctl --user restart pipewire pipewire-pulse wireplumber

# 4. Set default source
pactl set-default-source alsa_input.pci-0000_00_1f.3.analog-stereo

echo "✅ Done. Now:"
echo "1. REBOOT your computer (required for group change)"
echo "2. After reboot, Chrome will see the microphone"
echo ""
echo "OR skip microphone - use text chat at http://localhost:8080"
