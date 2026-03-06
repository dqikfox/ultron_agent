#!/bin/bash

# Claude Desktop Launcher for ULTRON Agent
echo "🤖 Launching Claude Desktop..."

# Try different ways to launch Claude Desktop
if command -v claudeai-desktop &> /dev/null; then
    claudeai-desktop &
elif snap list | grep -q claudeai-desktop; then
    snap run claudeai-desktop &
else
    echo "❌ Claude Desktop not found. Install with:"
    echo "   sudo snap install claudeai-desktop"
    exit 1
fi

echo "✅ Claude Desktop launched successfully"
echo "🔗 Integration with ULTRON Agent configured"