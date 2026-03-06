#!/bin/bash

echo "🤖 Installing Claude Code CLI for ULTRON Agent"
echo "=============================================="

# Download bootstrap script manually
echo "1. Downloading Claude Code bootstrap..."
wget -O bootstrap.sh https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/bootstrap.sh

if [ -f "bootstrap.sh" ]; then
    chmod +x bootstrap.sh
    echo "2. Running Claude Code installer..."
    bash bootstrap.sh
    
    if command -v claude &> /dev/null; then
        echo "✅ Claude Code installed successfully"
        echo "🔑 API Key configured in ULTRON"
        claude --version
    else
        echo "❌ Installation failed"
    fi
else
    echo "❌ Bootstrap download failed"
    echo "📝 Manual installation:"
    echo "   1. Visit https://code.claude.com"
    echo "   2. Download for Linux"
    echo "   3. Install manually"
fi

echo ""
echo "🧪 Testing Claude API..."
python3 -c "
import requests
response = requests.post(
    'https://api.anthropic.com/v1/messages',
    headers={
        'x-api-key': 'REDACTED_ANTHROPIC_KEY_1',
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    },
    json={
        'model': 'claude-3-haiku-20240307',
        'max_tokens': 20,
        'messages': [{'role': 'user', 'content': 'Test'}]
    }
)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print('✅ Claude API working')
else:
    print(f'❌ API Error: {response.text[:100]}')
"