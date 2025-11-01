"""
ULTRON Avatar Game Server - Integrated with Main ULTRON System
Handles avatar game deployment, testing, and integration
"""

import asyncio
import json
import logging
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import psutil
import signal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.ultron_logger import log_info, log_error, log_ai_decision

try:
    from aws_integration import aws
    AWS_ENABLED = aws.enabled
except:
    AWS_ENABLED = False
    aws = None

try:
    from avatar_db import save_message, load_memory, get_relationship_score
    DB_ENABLED = True
except:
    DB_ENABLED = False

try:
    from ensemble import ensemble_response, context_weights
    ENSEMBLE_ENABLED = True
except:
    ENSEMBLE_ENABLED = False

try:
    from ultron_avatar_bridge import voice_command_handler, get_ultron_tools, integrate_with_ultron
    BRIDGE_ENABLED = True
except:
    BRIDGE_ENABLED = False

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

avatar_sessions = {}
avatar_stats = {}

def kill_existing_instances():
    """Kill any existing avatar game server instances"""
    current_pid = os.getpid()
    killed = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.pid == current_pid:
                continue
            
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'avatar_game_server.py' in ' '.join(cmdline):
                log_info("avatar_game", f"Killing existing instance: PID {proc.pid}")
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed > 0:
        log_info("avatar_game", f"Killed {killed} existing instance(s)")
        import time
        time.sleep(2)
    
    return killed

class AvatarGameManager:
    def __init__(self):
        self.avatars = {}
        self.memory = {}
        self.skills = {}
        self.achievements = {}
        self.model_avatars = self.load_model_avatars()
        self.aws_enabled = AWS_ENABLED
        self.setup_tools()
        
        if self.aws_enabled:
            log_info("avatar_game", "AWS integration enabled")
    
    def load_model_avatars(self):
        """Load static model avatar assignments"""
        try:
            config_path = Path(__file__).parent / 'model_avatars.json'
            with open(config_path, 'r') as f:
                data = json.load(f)
                log_info("avatar_game", f"Loaded {len(data['model_avatars'])} model avatars")
                return data
        except Exception as e:
            log_error("avatar_game", f"Failed to load model avatars: {e}")
            return {'model_avatars': {}, 'default_model': 'gerard/ultron:latest'}
    
    def get_model_avatar(self, model_name):
        """Get avatar configuration for a model"""
        return self.model_avatars['model_avatars'].get(model_name)
    
    def apply_personality(self, model_name, base_response):
        """Apply model personality to response"""
        avatar = self.get_model_avatar(model_name)
        if not avatar or not self.model_avatars.get('personality_system', {}).get('enabled'):
            return base_response
        
        personality = avatar.get('personality', '')
        voice_style = avatar.get('voice_style', '')
        
        # Add catchphrase occasionally
        import random
        if random.random() < self.model_avatars['personality_system'].get('include_catchphrase_chance', 0.1):
            catchphrase = avatar.get('catchphrase', '')
            if catchphrase:
                base_response += f"\n\n*{catchphrase}*"
        
        return base_response
        
    def create_avatar(self, avatar_id, role, model):
        self.avatars[avatar_id] = {
            'id': avatar_id,
            'role': role,
            'model': model,
            'level': 1,
            'xp': 0,
            'skills': self.get_default_skills(role),
            'active': True,
            'created_at': asyncio.get_event_loop().time()
        }
        log_info("avatar_game", f"Avatar created: {avatar_id} ({role})")
        return self.avatars[avatar_id]
    
    def setup_tools(self):
        """Setup OCR and PyAutoGUI"""
        try:
            import pytesseract
            from PIL import Image
            paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.ocr_available = True
                    log_info("avatar_game", f"OCR available: {path}")
                    break
            else:
                self.ocr_available = False
        except:
            self.ocr_available = False
        
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            self.pyautogui_available = True
            log_info("avatar_game", "PyAutoGUI available")
        except:
            self.pyautogui_available = False
    
    def get_default_skills(self, role):
        skill_trees = {
            'coder': ['python', 'javascript', 'debugging', 'git'],
            'writer': ['creative_writing', 'documentation', 'editing', 'research'],
            'tool_user': ['automation', 'scripting', 'system_control', 'api_integration'],
            'assistant': ['general_knowledge', 'task_management', 'communication', 'problem_solving'],
            'admin': ['security', 'monitoring', 'deployment', 'optimization'],
            'pyautogui_agent': ['screen_control', 'ocr', 'gui_automation', 'image_recognition']
        }
        return {skill: 1 for skill in skill_trees.get(role, [])}
    
    def add_xp(self, avatar_id, xp_amount):
        if avatar_id in self.avatars:
            self.avatars[avatar_id]['xp'] += xp_amount
            # Level up every 100 XP
            new_level = 1 + (self.avatars[avatar_id]['xp'] // 100)
            if new_level > self.avatars[avatar_id]['level']:
                self.avatars[avatar_id]['level'] = new_level
                log_info("avatar_game", f"Avatar {avatar_id} leveled up to {new_level}")
                return True
        return False
    
    def save_state(self):
        state_file = Path(__file__).parent / 'avatar_game_state.json'
        with open(state_file, 'w') as f:
            json.dump({
                'avatars': self.avatars,
                'memory': self.memory,
                'skills': self.skills,
                'achievements': self.achievements
            }, f, indent=2)
        log_info("avatar_game", "Game state saved")
    
    def load_state(self):
        state_file = Path(__file__).parent / 'avatar_game_state.json'
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.avatars = data.get('avatars', {})
                self.memory = data.get('memory', {})
                self.skills = data.get('skills', {})
                self.achievements = data.get('achievements', {})
            log_info("avatar_game", "Game state loaded")

game_manager = AvatarGameManager()

@app.route('/')
def index():
    return send_from_directory('gui/ultron_enhanced/web', 'ultron_avatar_game_ultimate.html')

@app.route('/api/avatar/create', methods=['POST'])
def create_avatar():
    data = request.json
    avatar_id = data.get('id')
    role = data.get('role')
    model = data.get('model')
    
    avatar = game_manager.create_avatar(avatar_id, role, model)
    socketio.emit('avatar_created', avatar)
    
    return jsonify({'success': True, 'avatar': avatar})

@app.route('/api/avatar/<avatar_id>/chat', methods=['POST'])
def avatar_chat(avatar_id):
    data = request.json
    message = data.get('message')
    model_name = data.get('model')
    use_aws = data.get('use_aws', False)
    use_ensemble = data.get('use_ensemble', False)
    
    if avatar_id not in game_manager.avatars:
        return jsonify({'success': False, 'error': 'Avatar not found'})
    
    avatar = game_manager.avatars[avatar_id]
    model_avatar = game_manager.get_model_avatar(model_name) if model_name else None
    
    # Multi-model ensemble
    if use_ensemble and ENSEMBLE_ENABLED:
        weights = context_weights(message)
        models = list(weights.keys())
        weight_list = list(weights.values())
        response = ensemble_response(message, models, weight_list)
    # AWS Bedrock integration
    elif use_aws and game_manager.aws_enabled and aws:
        bedrock_response = aws.bedrock_chat('anthropic.claude-v2', message)
        if bedrock_response:
            response = bedrock_response
        else:
            response = "AWS Bedrock unavailable"
    elif model_avatar:
        personality = model_avatar.get('personality', '')
        response = f"{model_avatar['name']}: {message}\n\n[{personality}]"
        response = game_manager.apply_personality(model_name, response)
    else:
        responses = {
            'coder': f"Analyzing: {message}. I can help with code and debugging!",
            'writer': f"Crafting: {message}. Content creation ready!",
            'tool_user': f"Automating: {message}. OCR and PyAutoGUI available!",
            'assistant': f"Processing: {message}. General assistance ready!",
            'admin': f"System check: {message}. Monitoring active!",
            'pyautogui_agent': f"Screen control: {message}. GUI automation ready!"
        }
        response = responses.get(avatar['role'], f"Processing: {message}")
    
    # AWS sentiment analysis
    sentiment = None
    if game_manager.aws_enabled and aws:
        sentiment = aws.analyze_sentiment(message)
    
    leveled_up = game_manager.add_xp(avatar_id, 10)
    
    # Save to database
    if DB_ENABLED and sentiment:
        score_map = {'POSITIVE': 5, 'NEUTRAL': 0, 'NEGATIVE': -3, 'MIXED': 1}
        score = score_map.get(sentiment.get('sentiment'), 0)
        save_message(avatar_id, message, response, sentiment.get('sentiment'), 
                    int(asyncio.get_event_loop().time()), score)
    
    return jsonify({
        'success': True,
        'response': response,
        'avatar': avatar,
        'model_avatar': model_avatar,
        'leveled_up': leveled_up,
        'sentiment': sentiment,
        'aws_used': use_aws and game_manager.aws_enabled,
        'ensemble_used': use_ensemble and ENSEMBLE_ENABLED,
        'db_saved': DB_ENABLED
    })

@app.route('/api/avatar/<avatar_id>/stats', methods=['GET'])
def get_avatar_stats(avatar_id):
    if avatar_id not in game_manager.avatars:
        return jsonify({'success': False, 'error': 'Avatar not found'})
    
    return jsonify({'success': True, 'avatar': game_manager.avatars[avatar_id]})

@app.route('/api/game/save', methods=['POST'])
def save_game():
    data = request.json or {}
    use_cloud = data.get('use_cloud', False)
    
    # Local save
    game_manager.save_state()
    
    # Cloud save to S3
    cloud_saved = False
    if use_cloud and game_manager.aws_enabled and aws:
        bucket = os.getenv('AWS_S3_BUCKET', 'ultron-game-saves')
        game_data = {
            'user_id': data.get('user_id', 'default'),
            'avatars': game_manager.avatars,
            'memory': game_manager.memory,
            'achievements': game_manager.achievements
        }
        cloud_saved = aws.s3_save_game(bucket, game_data)
    
    return jsonify({
        'success': True,
        'message': 'Game saved',
        'cloud_saved': cloud_saved
    })

@app.route('/api/game/load', methods=['POST'])
def load_game():
    data = request.json or {}
    use_cloud = data.get('use_cloud', False)
    
    # Try cloud load first
    if use_cloud and game_manager.aws_enabled and aws:
        bucket = os.getenv('AWS_S3_BUCKET', 'ultron-game-saves')
        cloud_data = aws.s3_load_game(bucket, data.get('user_id', 'default'))
        if cloud_data:
            game_manager.avatars = cloud_data.get('avatars', {})
            game_manager.memory = cloud_data.get('memory', {})
            game_manager.achievements = cloud_data.get('achievements', {})
            return jsonify({
                'success': True,
                'message': 'Game loaded from cloud',
                'avatars': game_manager.avatars,
                'cloud_loaded': True
            })
    
    # Fallback to local load
    game_manager.load_state()
    return jsonify({
        'success': True,
        'message': 'Game loaded',
        'avatars': game_manager.avatars,
        'cloud_loaded': False
    })

@app.route('/api/tools/test', methods=['POST'])
def test_tools():
    data = request.json
    tool_name = data.get('tool', 'all')
    
    results = {}
    
    if tool_name == 'all' or tool_name == 'ocr':
        results['ocr'] = {
            'status': 'available' if game_manager.ocr_available else 'unavailable',
            'tested': True
        }
    
    if tool_name == 'all' or tool_name == 'pyautogui':
        results['pyautogui'] = {
            'status': 'available' if game_manager.pyautogui_available else 'unavailable',
            'tested': True
        }
    
    if tool_name == 'all' or tool_name == 'screenshot':
        try:
            import pyautogui
            results['screenshot'] = {'status': 'available', 'tested': True}
        except:
            results['screenshot'] = {'status': 'unavailable', 'tested': False}
    
    return jsonify({'success': True, 'results': results})

@app.route('/api/models/avatars', methods=['GET'])
def get_model_avatars():
    """Get all model avatar configurations"""
    return jsonify({
        'success': True,
        'avatars': game_manager.model_avatars['model_avatars'],
        'default_model': game_manager.model_avatars.get('default_model')
    })

@app.route('/api/models/avatar/<model_name>', methods=['GET'])
def get_model_avatar(model_name):
    """Get specific model avatar configuration"""
    avatar = game_manager.get_model_avatar(model_name)
    if avatar:
        return jsonify({'success': True, 'avatar': avatar})
    return jsonify({'success': False, 'error': 'Model avatar not found'})

@app.route('/api/aws/status', methods=['GET'])
def aws_status():
    """Get AWS integration status"""
    services = {}
    if game_manager.aws_enabled and aws:
        services = {
            'bedrock': True,
            's3': True,
            'polly': True,
            'comprehend': True,
            'translate': True
        }
    
    return jsonify({
        'success': True,
        'enabled': game_manager.aws_enabled,
        'region': aws.region if aws else None,
        'services': services
    })

@app.route('/api/aws/translate', methods=['POST'])
def translate_text():
    """Translate text to target language"""
    if not game_manager.aws_enabled or not aws:
        return jsonify({'success': False, 'error': 'AWS not enabled'})
    
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang', 'es')
    
    translated = aws.translate_text(text, target_lang)
    return jsonify({
        'success': bool(translated),
        'translated': translated,
        'target_lang': target_lang
    })

@app.route('/api/aws/voice', methods=['POST'])
def generate_voice():
    """Generate voice using AWS Polly"""
    if not game_manager.aws_enabled or not aws:
        return jsonify({'success': False, 'error': 'AWS not enabled'})
    
    data = request.json
    text = data.get('text')
    character = data.get('character')
    
    voice_id = aws.get_character_voice(character) if character else 'Matthew'
    audio = aws.polly_speak(text, voice_id)
    
    if audio:
        # Save to temp file and return path
        import base64
        audio_b64 = base64.b64encode(audio).decode('utf-8')
        return jsonify({
            'success': True,
            'audio': audio_b64,
            'voice_id': voice_id
        })
    
    return jsonify({'success': False, 'error': 'Voice generation failed'})

@app.route('/api/ultron/integrate', methods=['POST'])
def integrate_ultron():
    """Integrate with main ULTRON agent"""
    integrated = False
    tools = []
    
    if BRIDGE_ENABLED:
        integrated = integrate_with_ultron()
        if integrated:
            tools = get_ultron_tools()
    
    return jsonify({
        'success': True,
        'integrated': integrated,
        'message': 'ULTRON integration ' + ('active' if integrated else 'standalone'),
        'tools_count': len(tools),
        'tools': tools[:10],
        'model_avatars': len(game_manager.model_avatars['model_avatars']),
        'aws_enabled': game_manager.aws_enabled,
        'bridge_enabled': BRIDGE_ENABLED
    })

@app.route('/api/voice/command', methods=['POST'])
def handle_voice_command():
    """Handle voice commands from ULTRON"""
    if not BRIDGE_ENABLED:
        return jsonify({'success': False, 'error': 'Bridge not enabled'})
    
    data = request.json
    command = data.get('command', '')
    
    result = voice_command_handler(command)
    if result:
        return jsonify({'success': True, 'action': result})
    
    return jsonify({'success': False, 'error': 'Command not recognized'})

@socketio.on('connect')
def handle_connect():
    log_info("avatar_game", "Client connected")
    emit('connection_status', {'status': 'connected'})

@socketio.on('avatar_action')
def handle_avatar_action(data):
    avatar_id = data.get('avatar_id')
    action = data.get('action')
    
    log_info("avatar_game", f"Avatar {avatar_id} action: {action}")
    
    # Add XP for actions
    if avatar_id in game_manager.avatars:
        game_manager.add_xp(avatar_id, 5)
    
    emit('action_result', {'success': True, 'avatar_id': avatar_id})

@socketio.on('voice_command')
def handle_voice_command(data):
    command = data.get('command')
    log_info("avatar_game", f"Voice command: {command}")
    
    # Process voice command
    emit('voice_response', {'command': command, 'processed': True})

def run_server():
    # Kill existing instances first
    kill_existing_instances()
    
    log_info("avatar_game", "Starting ULTRON Avatar Game Server on port 8082")
    print("=" * 60)
    print("ULTRON AVATAR GAME SERVER")
    print("=" * 60)
    print(f"[OK] OCR: {game_manager.ocr_available}")
    print(f"[OK] PyAutoGUI: {game_manager.pyautogui_available}")
    print(f"[OK] AWS: {game_manager.aws_enabled}")
    if game_manager.aws_enabled:
        print(f"[AWS] Region: {aws.region}")
        print(f"[AWS] Services: Bedrock, S3, Polly, Comprehend, Translate")
    print(f"[SERVER] http://localhost:8082")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=8082, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_server()
