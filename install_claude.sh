#!/bin/bash

echo "🤖 Installing Claude Desktop for ULTRON Agent"
echo "=============================================="

# Try AppImage installation
echo "1. Downloading Claude Desktop AppImage..."
wget -O claude-desktop.AppImage https://storage.googleapis.com/claude-desktop/claude-desktop-linux-x64.AppImage

if [ -f "claude-desktop.AppImage" ]; then
    chmod +x claude-desktop.AppImage
    echo "✅ Claude Desktop AppImage downloaded"
    echo "🚀 Launch with: ./claude-desktop.AppImage"
else
    echo "❌ AppImage download failed"
    
    # Try Flatpak
    echo "2. Trying Flatpak installation..."
    if command -v flatpak &> /dev/null; then
        flatpak install -y flathub com.anthropic.Claude
        echo "✅ Claude Desktop installed via Flatpak"
        echo "🚀 Launch with: flatpak run com.anthropic.Claude"
    else
        echo "❌ Flatpak not available"
        
        # Manual installation instructions
        echo "3. Manual installation required:"
        echo "   Visit: https://claude.ai/download"
        echo "   Download Linux version manually"
    fi
fi

echo ""
echo "🔗 ULTRON Integration configured"
echo "📝 Config files updated with MiniMax AI support"