#!/bin/bash

# Manual .NET installation script for ULTRON Agent
# Fixes VS Code extension timeout issues

set -e

DOTNET_VERSION="9.0.11"
DOTNET_DIR="$HOME/.config/Code/User/globalStorage/ms-dotnettools.vscode-dotnet-runtime/.dotnet/${DOTNET_VERSION}~x64~aspnetcore"

echo "Installing .NET ${DOTNET_VERSION} manually..."

# Create directory
mkdir -p "$DOTNET_DIR"

# Download official installer
wget -O /tmp/dotnet-install.sh https://dot.net/v1/dotnet-install.sh
chmod +x /tmp/dotnet-install.sh

# Install with extended timeout
/tmp/dotnet-install.sh --install-dir "$DOTNET_DIR" --version "$DOTNET_VERSION" --runtime aspnetcore --architecture x64 --verbose

# Cleanup
rm /tmp/dotnet-install.sh

echo "✓ .NET ${DOTNET_VERSION} installed to: $DOTNET_DIR"
echo "✓ Restart VS Code to use the new runtime"