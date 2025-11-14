"""
Fix Screenshot with 3-second delay and restore Analyze button
"""

# Add to web_gui_server.py _capture_screen method
CAPTURE_FIX = '''
def _capture_screen(self):
    """Capture screen with 3-second delay"""
    try:
        import time
        import pyautogui
        from pathlib import Path
        
        # 3-second delay for window switching
        time.sleep(3)
        
        # Create screenshots directory
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        # Capture screenshot
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshots_dir / f"screenshot_{timestamp}.png"
        
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        return {
            'success': True,
            'image_path': str(screenshot_path),
            'message': 'Screenshot captured (3s delay)',
            'timestamp': timestamp
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
'''

# Add to web_gui_server.py _analyze_vision method
ANALYZE_FIX = '''
def _analyze_vision(self):
    """Analyze latest screenshot with AI description and OCR"""
    try:
        from pathlib import Path
        import json
        
        # Get latest screenshot
        screenshots_dir = Path("screenshots")
        if not screenshots_dir.exists():
            return {'success': False, 'error': 'No screenshots directory'}
        
        screenshots = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshots:
            return {'success': False, 'error': 'No screenshots found. Take a screenshot first.'}
        
        # Get most recent
        latest = max(screenshots, key=lambda p: p.stat().st_mtime)
        
        # OCR with enhanced_ocr_tool
        from tools.enhanced_ocr_tool import EnhancedOCRTool
        ocr_tool = EnhancedOCRTool()
        ocr_result = ocr_tool.execute("read", image_path=str(latest))
        ocr_data = json.loads(ocr_result)
        
        # AI description via Ollama
        import requests
        ollama_url = "http://localhost:11434"
        
        # Use llava for vision
        prompt = f"Describe this screenshot in detail. What do you see?"
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llava:7b",
                "prompt": prompt,
                "images": [str(latest)],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            ai_description = response.json().get("response", "No description")
        else:
            ai_description = "AI description unavailable"
        
        return {
            'success': True,
            'image_path': str(latest),
            'ai_description': ai_description,
            'ocr_text': ocr_data.get('raw_text', ''),
            'ocr_confidence': ocr_data.get('confidence', 0),
            'analysis': ocr_data.get('analysis', {}),
            'timestamp': latest.stem.replace('screenshot_', '')
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
'''

print("Screenshot & Analyze Fix")
print("=" * 60)
print("\n1. CAPTURE FIX (3-second delay):")
print(CAPTURE_FIX)
print("\n2. ANALYZE FIX (AI + OCR):")
print(ANALYZE_FIX)
print("\n" + "=" * 60)
print("\nTo apply:")
print("1. Replace _capture_screen() in web_gui_server.py")
print("2. Replace _analyze_vision() in web_gui_server.py")
print("3. Restart web server")
