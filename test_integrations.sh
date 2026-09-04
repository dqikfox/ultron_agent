#!/bin/bash

echo "🧪 Testing ULTRON AI Integrations"
echo "================================="

echo "1. Testing MiniMax AI..."
python3 -c "
import requests
import json

api_key = 'REDACTED_CURSOR_KEY'
try:
    response = requests.post(
        'https://api.minimax.chat/v1/text/chatcompletion_v2',
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        json={'model': 'abab6.5s-chat', 'messages': [{'sender_type': 'USER', 'text': 'Hello'}]}
    )
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:100]}...')
except Exception as e:
    print(f'Error: {e}')
"

echo ""
echo "2. Testing Claude Desktop..."
if snap list | grep -q claudeai-desktop; then
    echo "✅ Claude Desktop installed"
    echo "⚠️  Launch manually: snap run claudeai-desktop"
else
    echo "❌ Claude Desktop not found"
fi

echo ""
echo "3. Testing Continue integration..."
if [ -f ".continue/config.yaml" ]; then
    echo "✅ Continue config found"
    grep -A 2 "MiniMax" .continue/config.yaml || echo "⚠️  MiniMax not in config"
else
    echo "❌ Continue config missing"
fi