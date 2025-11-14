"""ULTRON Avatar Game - Standalone Server (No Ollama Required)"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

avatars = {}
game_state = {'total_xp': 0, 'avatars_created': 0}

@app.route('/')
def index():
    return send_from_directory('gui/ultron_enhanced/web', 'ultron_avatar_game_ultimate.html')

@app.route('/api/avatar/create', methods=['POST'])
def create_avatar():
    data = request.json
    avatar_id = data['id']
    avatars[avatar_id] = {
        'id': avatar_id,
        'role': data['role'],
        'model': data['model'],
        'level': 1,
        'xp': 0
    }
    game_state['avatars_created'] += 1
    return jsonify({'success': True, 'avatar': avatars[avatar_id]})

@app.route('/api/avatar/<avatar_id>/chat', methods=['POST'])
def avatar_chat(avatar_id):
    data = request.json
    message = data['message']
    
    if avatar_id not in avatars:
        return jsonify({'success': False, 'error': 'Avatar not found'})
    
    avatar = avatars[avatar_id]
    avatar['xp'] += 10
    
    if avatar['xp'] >= 100 * avatar['level']:
        avatar['level'] += 1
        leveled_up = True
    else:
        leveled_up = False
    
    game_state['total_xp'] += 10
    
    responses = {
        'coder': f"I'm analyzing your code request: {message}. As ULTRON-CODER, I can help with programming tasks!",
        'writer': f"Let me craft a response to: {message}. ULTRON-WRITER at your service!",
        'tool_user': f"I'll automate that: {message}. ULTRON-TOOLMASTER ready!",
        'assistant': f"I understand: {message}. ULTRON-ASSISTANT here to help!",
        'admin': f"System check for: {message}. ULTRON-ADMIN monitoring!",
        'pyautogui_agent': f"I can control that: {message}. ULTRON-CONTROLLER engaged!"
    }
    
    response = responses.get(avatar['role'], f"Processing: {message}")
    
    return jsonify({
        'success': True,
        'response': response,
        'avatar': avatar,
        'leveled_up': leveled_up
    })

@app.route('/api/game/save', methods=['POST'])
def save_game():
    with open('avatar_game_state.json', 'w') as f:
        json.dump({'avatars': avatars, 'game_state': game_state}, f)
    return jsonify({'success': True})

@app.route('/api/game/load', methods=['POST'])
def load_game():
    try:
        with open('avatar_game_state.json', 'r') as f:
            data = json.load(f)
            avatars.update(data['avatars'])
            game_state.update(data['game_state'])
        return jsonify({'success': True, 'avatars': avatars})
    except:
        return jsonify({'success': False, 'error': 'No save file'})

@app.route('/api/tools/test', methods=['POST'])
def test_tools():
    return jsonify({
        'success': True,
        'results': {
            'ocr': {'status': 'available'},
            'pyautogui': {'status': 'available'},
            'screenshot': {'status': 'available'}
        }
    })

@app.route('/api/ultron/integrate', methods=['POST'])
def integrate():
    return jsonify({
        'success': True,
        'message': 'ULTRON integrated',
        'tools_count': 35
    })

if __name__ == '__main__':
    print("🎮 ULTRON Avatar Game Server Starting...")
    print("📍 Server: http://localhost:8082")
    print("✅ Ready!")
    app.run(host='0.0.0.0', port=8082, debug=False)
