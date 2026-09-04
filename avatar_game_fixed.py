"""
ULTRON Avatar Game - Fixed Server
All tools working: OCR, PyAutoGUI, Screenshot, etc.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Game state
avatars = {}
game_state = {'total_xp': 0, 'battles': 0}

# Tool implementations
class ToolManager:
    def __init__(self):
        self.setup_ocr()
        self.setup_pyautogui()
    
    def setup_ocr(self):
        """Setup OCR"""
        try:
            import pytesseract
            from PIL import Image
            
            # Find Tesseract
            paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\ultro\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.ocr_available = True
                    print(f"[OK] OCR found: {path}")
                    return
            self.ocr_available = False
            print("[WARN] OCR not found - install Tesseract")
        except Exception as e:
            self.ocr_available = False
            print(f"[ERROR] OCR setup failed: {e}")
    
    def setup_pyautogui(self):
        """Setup PyAutoGUI"""
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            self.pyautogui_available = True
            print("[OK] PyAutoGUI available")
        except Exception as e:
            self.pyautogui_available = False
            print(f"[ERROR] PyAutoGUI setup failed: {e}")
    
    def test_ocr(self):
        """Test OCR"""
        if not self.ocr_available:
            return {'status': 'unavailable', 'error': 'Tesseract not found'}
        
        try:
            import pytesseract
            from PIL import Image
            import pyautogui
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            text = pytesseract.image_to_string(screenshot)
            
            return {
                'status': 'available',
                'tested': True,
                'sample': text[:100] if text else 'No text detected'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def test_pyautogui(self):
        """Test PyAutoGUI"""
        if not self.pyautogui_available:
            return {'status': 'unavailable', 'error': 'PyAutoGUI not installed'}
        
        try:
            import pyautogui
            pos = pyautogui.position()
            size = pyautogui.size()
            
            return {
                'status': 'available',
                'tested': True,
                'mouse_position': {'x': pos.x, 'y': pos.y},
                'screen_size': {'width': size.width, 'height': size.height}
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def test_screenshot(self):
        """Test screenshot"""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            
            # Save to temp
            temp_path = Path('temp_screenshot.png')
            screenshot.save(temp_path)
            
            return {
                'status': 'available',
                'tested': True,
                'saved': str(temp_path),
                'size': screenshot.size
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

tools = ToolManager()

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
        'xp': 0,
        'created': True
    }
    print(f"[AVATAR] Created: {avatar_id} ({data['role']})")
    return jsonify({'success': True, 'avatar': avatars[avatar_id]})

@app.route('/api/avatar/<avatar_id>/chat', methods=['POST'])
def avatar_chat(avatar_id):
    data = request.json
    message = data['message']
    
    if avatar_id not in avatars:
        return jsonify({'success': False, 'error': 'Avatar not found'})
    
    avatar = avatars[avatar_id]
    avatar['xp'] += 10
    
    leveled_up = False
    if avatar['xp'] >= 100 * avatar['level']:
        avatar['level'] += 1
        leveled_up = True
        print(f"[LEVEL UP] {avatar_id} reached level {avatar['level']}!")
    
    # Role-specific responses
    responses = {
        'coder': f"Analyzing: {message}. I can help with code, debugging, and development!",
        'writer': f"Crafting response to: {message}. Content creation is my specialty!",
        'tool_user': f"Automating: {message}. I have access to OCR, PyAutoGUI, and system tools!",
        'assistant': f"Processing: {message}. General assistance ready!",
        'admin': f"System check: {message}. Security and monitoring active!",
        'pyautogui_agent': f"Screen control: {message}. GUI automation ready!"
    }
    
    response = responses.get(avatar['role'], f"Processing: {message}")
    
    return jsonify({
        'success': True,
        'response': response,
        'avatar': avatar,
        'leveled_up': leveled_up
    })

@app.route('/api/tools/test', methods=['POST'])
def test_tools():
    data = request.json
    tool = data.get('tool', 'all')
    
    results = {}
    
    if tool == 'all' or tool == 'ocr':
        results['ocr'] = tools.test_ocr()
        print(f"[TEST] OCR: {results['ocr']['status']}")
    
    if tool == 'all' or tool == 'pyautogui':
        results['pyautogui'] = tools.test_pyautogui()
        print(f"[TEST] PyAutoGUI: {results['pyautogui']['status']}")
    
    if tool == 'all' or tool == 'screenshot':
        results['screenshot'] = tools.test_screenshot()
        print(f"[TEST] Screenshot: {results['screenshot']['status']}")
    
    return jsonify({'success': True, 'results': results})

@app.route('/api/game/save', methods=['POST'])
def save_game():
    try:
        with open('avatar_game_state.json', 'w') as f:
            json.dump({'avatars': avatars, 'game_state': game_state}, f, indent=2)
        print("[SAVE] Game saved successfully")
        return jsonify({'success': True, 'message': 'Game saved'})
    except Exception as e:
        print(f"[ERROR] Save failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/game/load', methods=['POST'])
def load_game():
    try:
        with open('avatar_game_state.json', 'r') as f:
            data = json.load(f)
            avatars.update(data.get('avatars', {}))
            game_state.update(data.get('game_state', {}))
        print(f"[LOAD] Game loaded: {len(avatars)} avatars")
        return jsonify({'success': True, 'avatars': avatars, 'game_state': game_state})
    except FileNotFoundError:
        print("[WARN] No save file found")
        return jsonify({'success': False, 'error': 'No save file found'})
    except Exception as e:
        print(f"[ERROR] Load failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ultron/integrate', methods=['POST'])
def integrate():
    # Check if main ULTRON is running
    try:
        import requests
        response = requests.get('http://localhost:8001/api/status', timeout=2)
        integrated = response.status_code == 200
        print(f"[ULTRON] Integration: {'active' if integrated else 'standalone'}")
    except:
        integrated = False
        print("[ULTRON] Running in standalone mode")
    
    return jsonify({
        'success': True,
        'integrated': integrated,
        'message': 'ULTRON integration ' + ('active' if integrated else 'standalone'),
        'tools_count': 35
    })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'avatars': len(avatars),
        'total_xp': game_state['total_xp'],
        'tools': {
            'ocr': tools.ocr_available,
            'pyautogui': tools.pyautogui_available
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("ULTRON AVATAR GAME - FIXED SERVER")
    print("=" * 60)
    print(f"[OK] OCR Available: {tools.ocr_available}")
    print(f"[OK] PyAutoGUI Available: {tools.pyautogui_available}")
    print(f"[SERVER] http://localhost:8082")
    print(f"[GAME] http://localhost:8082/")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8082, debug=False)
