#!/bin/bash

# Unity Tools Integration for ULTRON Agent
# Manages Unity project setup and addressable assets

set -e

UNITY_PROJECT_PATH="/home/ultro/projects/ultron_agent/unity_cloud_code"
UNITY_EDITOR_PATH="/opt/unity/Editor/Unity"

echo "🎮 Unity Tools Operational Setup"

# Check Unity installation
if [ ! -f "$UNITY_EDITOR_PATH" ]; then
    echo "⚠️  Unity Editor not found at $UNITY_EDITOR_PATH"
    echo "Please install Unity Hub and Unity Editor 2023.3 LTS"
    exit 1
fi

# Build UltronModule
echo "🔧 Building UltronModule..."
cd "$UNITY_PROJECT_PATH/UltronModule"
dotnet build --configuration Release

# Generate Unity project files
echo "📁 Generating Unity project files..."
cd "$UNITY_PROJECT_PATH"
"$UNITY_EDITOR_PATH" -batchmode -quit -projectPath . -executeMethod UnityEditor.SyncVS.SyncSolution

# Import addressable assets
echo "📦 Setting up Addressable Assets..."
"$UNITY_EDITOR_PATH" -batchmode -quit -projectPath . -executeMethod AddressableAssetSettings.BuildPlayerContent

echo "✅ Unity tools operational"