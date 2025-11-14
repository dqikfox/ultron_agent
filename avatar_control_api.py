#!/usr/bin/env python3
"""Avatar Control API for PyAutoGUI and Screen Capture"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pyautogui
import time
import os
from datetime import datetime
from utils.ultron_logger import log_info, log_error

app = Flask(__name__)
CORS(app)

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

@app.route('/api/pyautogui/mouse', methods=['POST'])
def mouse_control():
    """Control mouse via PyAutoGUI"""
    try:
        data = request.get_json()
        action = data.get('action', 'click')
        x = data.get('x', 0)
        y = data.get('y', 0)
        
        log_info("avatar_control", f"Mouse {action} at ({x}, {y})")
        
        if action == 'click':
            pyautogui.click(x, y)
        elif action == 'rightclick':
            pyautogui.rightClick(x, y)
        elif action == 'doubleclick':
            pyautogui.doubleClick(x, y)
        elif action == 'drag':
            to_x = data.get('to_x', x + 100)
            to_y = data.get('to_y', y + 100)
            pyautogui.drag(x, y, to_x, to_y, duration=0.5)
        elif action == 'scroll':
            clicks = data.get('clicks', 3)
            pyautogui.scroll(clicks, x, y)
        elif action == 'move':
            pyautogui.moveTo(x, y)
        
        return jsonify({'success': True, 'action': action, 'x': x, 'y': y})
        
    except Exception as e:
        log_error("avatar_control", f"Mouse control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pyautogui/keyboard', methods=['POST'])
def keyboard_control():
    """Control keyboard via PyAutoGUI"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        keys = data.get('keys', '')
        
        if text:
            log_info("avatar_control", f"Typing text: {text[:50]}...")
            pyautogui.typewrite(text, interval=0.05)
        
        if keys:
            log_info("avatar_control", f"Pressing keys: {keys}")
            if ',' in keys:
                # Multiple keys combination
                key_list = [k.strip() for k in keys.split(',')]
                pyautogui.hotkey(*key_list)
            else:
                # Single key
                pyautogui.press(keys)
        
        return jsonify({'success': True, 'text': text, 'keys': keys})
        
    except Exception as e:
        log_error("avatar_control", f"Keyboard control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pyautogui/screen', methods=['GET'])
def get_screen_info():
    """Get screen information"""
    try:
        size = pyautogui.size()
        position = pyautogui.position()
        
        return jsonify({
            'screen_width': size.width,
            'screen_height': size.height,
            'mouse_x': position.x,
            'mouse_y': position.y
        })
        
    except Exception as e:
        log_error("avatar_control", f"Screen info error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pyautogui/locate', methods=['POST'])
def locate_on_screen():
    """Locate image or text on screen"""
    try:
        data = request.get_json()
        image_path = data.get('image_path', '')
        confidence = data.get('confidence', 0.8)
        
        if image_path and os.path.exists(image_path):
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return jsonify({
                    'found': True,
                    'x': center.x,
                    'y': center.y,
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height
                })
            else:
                return jsonify({'found': False})
        
        return jsonify({'error': 'Invalid image path'}), 400
        
    except Exception as e:
        log_error("avatar_control", f"Locate error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vision/live_capture', methods=['POST'])
def live_capture():
    """Capture screenshot for live viewing"""
    try:
        screenshot = pyautogui.screenshot()
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"live_screenshot_{timestamp}.png"
        filepath = os.path.join("screenshots", filename)
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        
        screenshot.save(filepath)
        
        log_info("avatar_control", f"Live screenshot saved: {filepath}")
        
        return jsonify({
            'success': True,
            'image_path': filepath,
            'image_url': f'/screenshots/{filename}',
            'timestamp': time.time(),
            'width': screenshot.width,
            'height': screenshot.height
        })
        
    except Exception as e:
        log_error("avatar_control", f"Live capture error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    log_info("avatar_control", "Starting Avatar Control API server on port 8081")
    app.run(host='0.0.0.0', port=8081, debug=False)