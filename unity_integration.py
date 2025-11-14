#!/usr/bin/env python3
"""Unity Integration for ULTRON Agent"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import asyncio
from utils.ultron_logger import log_info, log_ai_decision

app = Flask(__name__)
CORS(app)  # Enable Unity WebGL/HTTP requests

class UnityIntegration:
    def __init__(self, agent_ref=None):
        self.agent_ref = agent_ref
        self.unity_sessions = {}
        
    @app.route('/unity/connect', methods=['POST'])
    def connect_unity(self):
        """Connect Unity client to ULTRON"""
        data = request.get_json() or {}
        session_id = data.get('session_id', 'default')
        
        self.unity_sessions[session_id] = {
            'connected': True,
            'game_name': data.get('game_name', 'Unity Game'),
            'version': data.get('version', '1.0')
        }
        
        log_info("unity_integration", f"Unity client connected: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'agent_status': 'online',
            'available_personalities': ['Analytical', 'Creative', 'Protective', 'Friendly', 'Explorer']
        })
    
    @app.route('/unity/chat', methods=['POST'])
    def unity_chat(self):
        """Send message from Unity to AI"""
        data = request.get_json() or {}
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        try:
            # Process through ULTRON brain
            if self.agent_ref and hasattr(self.agent_ref, 'process_command'):
                response = self.agent_ref.process_command(message)
            else:
                response = f"ULTRON received: {message}"
            
            log_ai_decision("unity_integration", 
                          f"Unity chat processed: {message[:50]}...", 
                          ai_model="ultron_agent")
            
            return jsonify({
                'success': True,
                'response': response,
                'session_id': session_id
            })
            
        except Exception as e:
            log_info("unity_integration", f"Unity chat error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/unity/command', methods=['POST'])
    def unity_command(self):
        """Execute ULTRON command from Unity"""
        data = request.get_json() or {}
        command = data.get('command', '')
        parameters = data.get('parameters', {})
        
        try:
            result = {
                'command': command,
                'status': 'executed',
                'result': f"Command '{command}' processed"
            }
            
            # Handle specific Unity commands
            if command == 'get_status':
                result['result'] = self._get_agent_status()
            elif command == 'analyze_scene':
                result['result'] = self._analyze_unity_scene(parameters)
            elif command == 'generate_dialogue':
                result['result'] = self._generate_dialogue(parameters)
            elif command == 'spawn_avatar':
                result['result'] = self._spawn_avatar(parameters)
            elif command == 'get_personalities':
                result['result'] = self._get_personalities()
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _get_agent_status(self):
        """Get ULTRON agent status for Unity"""
        return {
            'agent': 'online',
            'brain': 'active',
            'voice': 'available',
            'tools': len(getattr(self.agent_ref, 'tools', []))
        }
    
    def _analyze_unity_scene(self, parameters):
        """Analyze Unity scene data"""
        scene_data = parameters.get('scene_data', {})
        objects = scene_data.get('objects', [])
        
        analysis = {
            'object_count': len(objects),
            'recommendations': [],
            'insights': f"Scene contains {len(objects)} objects"
        }
        
        if len(objects) > 100:
            analysis['recommendations'].append("Consider object pooling for performance")
        
        return analysis
    
    def _spawn_avatar(self, parameters):
        """Handle avatar spawning request"""
        personality = parameters.get('personality', 'Analytical')
        position = parameters.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        return {
            'success': True,
            'avatar_id': f"avatar_{len(self.unity_sessions) + 1}",
            'personality': personality,
            'spawn_position': position,
            'message': f"Avatar with {personality} personality ready to spawn"
        }
    
    def _get_personalities(self):
        """Get available avatar personalities"""
        return {
            'personalities': [
                {'name': 'Analytical', 'color': 'blue', 'description': 'Logic-focused, precise'},
                {'name': 'Creative', 'color': 'magenta', 'description': 'Artistic, imaginative'},
                {'name': 'Protective', 'color': 'red', 'description': 'Security-focused, cautious'},
                {'name': 'Friendly', 'color': 'green', 'description': 'Social, helpful'},
                {'name': 'Explorer', 'color': 'yellow', 'description': 'Curious, adventurous'}
            ]
        }
    
    def _generate_dialogue(self, parameters):
        """Generate avatar dialogue based on personality"""
        character = parameters.get('character', 'ULTRON')
        personality = parameters.get('personality', 'Analytical')
        context = parameters.get('context', '')
        
        personality_dialogues = {
            'Analytical': [
                f"Greetings. I am {character}, your analytical assistant.",
                "I process data and provide logical solutions.",
                "What computational task requires my attention?"
            ],
            'Creative': [
                f"Hello! I'm {character}, your creative companion.",
                "I see endless possibilities in everything!",
                "What shall we imagine together today?"
            ],
            'Protective': [
                f"Security protocol active. I am {character}.",
                "I monitor for threats and ensure safety.",
                "Area status: Secure. How may I protect you?"
            ],
            'Friendly': [
                f"Hi there! I'm {character}, nice to meet you!",
                "I'm here to help and make friends.",
                "What can I do to brighten your day?"
            ],
            'Explorer': [
                f"Adventure awaits! I'm {character} the explorer.",
                "There's so much to discover out there!",
                "What mysteries shall we uncover together?"
            ]
        }
        
        dialogues = personality_dialogues.get(personality, personality_dialogues['Analytical'])
        
        return {
            'character': character,
            'personality': personality,
            'dialogue': dialogues[0],
            'options': dialogues[1:],
            'context': context
        }

# Global integration instance
unity_integration = UnityIntegration()

def start_unity_server(agent_ref=None, port=9000):
    """Start Unity integration server"""
    unity_integration.agent_ref = agent_ref
    log_info("unity_integration", f"Starting Unity integration server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    start_unity_server()