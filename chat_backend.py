#!/usr/bin/env python3
"""
Minimal ULTRON Chat Backend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Load config
try:
    with open('ultron_config.json', 'r') as f:
        config = json.load(f)
except:
    config = {}

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "ultron-chat"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        # Try Claude first
        claude_key = config.get('anthropic_api_key', '')
        if claude_key:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': claude_key,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 1000,
                    'messages': [{'role': 'user', 'content': message}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return jsonify({
                    'response': result['content'][0]['text'],
                    'model': 'claude-3-haiku'
                })
        
        # Fallback to Ollama
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen2.5-coder:7b',
                'prompt': message,
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'response': result.get('response', 'No response'),
                'model': 'qwen2.5-coder:7b'
            })
        
        return jsonify({'error': 'No AI backend available'}), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Starting ULTRON Chat Backend on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=False)