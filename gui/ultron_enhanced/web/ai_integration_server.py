#!/usr/bin/env python3
"""
ULTRON AI SIMULATOR - Real AI Integration Example
================================================

This script demonstrates how to connect the ULTRON AI SIMULATOR to real AI models
via Ollama or LM Studio. It provides a simple API server that the web interface
can call to get real AI responses instead of simulated ones.

Requirements:
- Ollama running locally (http://localhost:11434)
- Python 3.7+
- Flask or FastAPI

Installation:
    pip install flask requests asyncio aiohttp

Usage:
    python ai_integration_server.py
    
Then modify the HTML file to use the AI API endpoints instead of simulated responses.
"""

from flask import Flask, request, jsonify
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional

app = Flask(__name__)

# Global state storage for NPC contexts
npc_contexts = {}

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"

class AINPCManager:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_response(self, npc_id: str, model: str, persona_data: Dict, 
                              user_message: Optional[str] = None) -> str:
        """Generate AI response for an NPC"""
        
        # Build context for the AI
        context = self._build_context(npc_id, persona_data, user_message)
        
        try:
            # Call Ollama API
            async with self.session.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": context,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get('response', '')
                    
                    # Store in context memory
                    self._store_interaction(npc_id, user_message, ai_response)
                    
                    return ai_response.strip()
                else:
                    return f"Error: AI model {model} is not responding (Status: {response.status})"
                    
        except Exception as e:
            return f"AI service unavailable: {str(e)}"
    
    def _build_context(self, npc_id: str, persona_data: Dict, user_message: Optional[str]) -> str:
        """Build the full context prompt for the AI"""
        
        # Get existing context
        if npc_id not in npc_contexts:
            npc_contexts[npc_id] = {
                'persona': persona_data,
                'recent_interactions': [],
                'current_state': {},
                'memories': []
            }
        
        context = npc_contexts[npc_id]
        
        # Build the persona prompt
        prompt = f"""You are {persona_data['name']}, {persona_data['description']}.

Your current state:
- Hunger: {persona_data.get('hunger', 50)}/100
- Thirst: {persona_data.get('thirst', 50)}/100  
- Happiness: {persona_data.get('happiness', 75)}/100
- HP: {persona_data.get('hp', 100)}/100
- Current Goal: {persona_data.get('goal', 'wander')}

Your personality traits: {', '.join(persona_data.get('traits', []))}

"""
        
        # Add recent interactions for context
        if context['recent_interactions']:
            prompt += "Recent interactions:\n"
            for interaction in context['recent_interactions'][-3:]:  # Last 3 interactions
                prompt += f"- {interaction}\n"
            prompt += "\n"
        
        # Add personality-based behavior guidelines
        prompt += "Guidelines:\n"
        prompt += "- Always stay in character\n"
        prompt += "- Your responses should reflect your current physical and emotional state\n"
        prompt += "- Remember past interactions when relevant\n"
        prompt += "- Be natural and engaging in your responses\n"
        prompt += "- Keep responses under 100 words\n"
        
        # Add user message if provided
        if user_message:
            prompt += f"\nSomeone says to you: \"{user_message}\"\n"
            prompt += "Respond as your character would:"
        else:
            prompt += "\nYou are free to think or speak your thoughts:"
        
        return prompt
    
    def _store_interaction(self, npc_id: str, user_message: Optional[str], ai_response: str):
        """Store interaction in NPC memory"""
        if npc_id not in npc_contexts:
            return
            
        interaction = {
            'timestamp': time.time(),
            'user_message': user_message,
            'npc_response': ai_response,
            'context': npc_contexts[npc_id]['current_state']
        }
        
        npc_contexts[npc_id]['recent_interactions'].append(interaction)
        
        # Keep only last 10 interactions
        if len(npc_contexts[npc_id]['recent_interactions']) > 10:
            npc_contexts[npc_id]['recent_interactions'].pop(0)

@app.route('/api/ai/response', methods=['POST'])
async def generate_ai_response():
    """Main endpoint for generating NPC responses"""
    data = request.get_json()
    
    npc_id = data.get('npc_id')
    model = data.get('model', DEFAULT_MODEL)
    persona_data = data.get('persona_data', {})
    user_message = data.get('message')
    
    if not npc_id or not persona_data:
        return jsonify({'error': 'npc_id and persona_data are required'}), 400
    
    async with AINPCManager() as manager:
        response = await manager.generate_response(npc_id, model, persona_data, user_message)
    
    return jsonify({
        'response': response,
        'npc_id': npc_id,
        'model_used': model
    })

@app.route('/api/ai/model-status', methods=['GET'])
async def check_model_status():
    """Check if Ollama is running and what models are available"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{OLLAMA_URL}/api/tags") as response:
                if response.status == 200:
                    models_data = await response.json()
                    models = [model['name'] for model in models_data.get('models', [])]
                    return jsonify({
                        'status': 'connected',
                        'available_models': models,
                        'default_model': DEFAULT_MODEL
                    })
                else:
                    return jsonify({
                        'status': 'disconnected',
                        'error': 'Ollama service not responding'
                    }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 503

@app.route('/api/ai/update-state', methods=['POST'])
def update_npc_state():
    """Update NPC's current state"""
    data = request.get_json()
    npc_id = data.get('npc_id')
    state_update = data.get('state', {})
    
    if npc_id:
        if npc_id not in npc_contexts:
            npc_contexts[npc_id] = {'recent_interactions': [], 'current_state': {}}
        
        npc_contexts[npc_id]['current_state'].update(state_update)
        npc_contexts[npc_id]['current_state']['updated_at'] = time.time()
        
        return jsonify({'status': 'success', 'npc_id': npc_id})
    
    return jsonify({'error': 'npc_id required'}), 400

@app.route('/api/ai/npc-context/<npc_id>', methods=['GET'])
def get_npc_context(npc_id):
    """Get current NPC context and memory"""
    context = npc_contexts.get(npc_id, {
        'recent_interactions': [],
        'current_state': {},
        'memories': []
    })
    
    return jsonify({
        'npc_id': npc_id,
        'context': context
    })

@app.route('/api/ai/clear-memory/<npc_id>', methods=['POST'])
def clear_npc_memory(npc_id):
    """Clear NPC's memory and context"""
    if npc_id in npc_contexts:
        npc_contexts[npc_id] = {
            'recent_interactions': [],
            'current_state': npc_contexts[npc_id].get('current_state', {}),
            'memories': []
        }
    
    return jsonify({'status': 'success', 'npc_id': npc_id})

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'ULTRON AI Simulator Integration',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("🤖 ULTRON AI SIMULATOR - Real AI Integration Server")
    print("=" * 50)
    print(f"Starting server on http://localhost:5000")
    print(f"Connecting to Ollama at {OLLAMA_URL}")
    print("\nMake sure Ollama is running:")
    print("  1. Install Ollama: https://ollama.ai")
    print("  2. Pull a model: ollama pull llama3")
    print("  3. Start server: ollama serve")
    print("\nTo integrate with the web interface:")
    print("  1. Open ultron-ai-simulator.html")
    print("  2. Modify the sendMessage() function to call /api/ai/response")
    print("  3. Update the getResponse() functions to use real AI")
    print("\n" + "=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)