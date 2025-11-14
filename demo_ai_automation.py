#!/usr/bin/env python3
"""
Demo: AI-Controlled Screen Automation
Shows ULTRON Agent AI controlling PyAutoGUI functions
"""

import requests
import json
import time
from tools.ollama_pyautogui_bridge import OllamaPyAutoGUIBridge

def demo_ai_automation():
    print("ULTRON Agent - AI-Controlled Screen Automation Demo")
    print("=" * 60)
    
    bridge = OllamaPyAutoGUIBridge()
    
    # Demo 1: AI takes screenshot
    print("1. AI Taking Screenshot...")
    result = bridge.call_function("take_screenshot")
    print(f"   Result: {result}")
    
    # Demo 2: AI gets screen info
    print("\n2. AI Getting Screen Information...")
    result = bridge.call_function("get_screen_info")
    print(f"   Result: {result}")
    
    # Demo 3: AI moves mouse
    print("\n3. AI Moving Mouse to Center...")
    result = bridge.call_function("move_mouse", x=960, y=540)
    print(f"   Result: {result}")
    
    # Demo 4: AI types text
    print("\n4. AI Typing Text...")
    result = bridge.call_function("type_text", text="ULTRON AI is now controlling the screen!")
    print(f"   Result: {result}")
    
    # Demo 5: AI presses key
    print("\n5. AI Pressing Enter Key...")
    result = bridge.call_function("press_key", key="enter")
    print(f"   Result: {result}")
    
    # Demo 6: AI scrolls
    print("\n6. AI Scrolling Down...")
    result = bridge.call_function("scroll", direction="down")
    print(f"   Result: {result}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("\nULTRON Agent AI can now:")
    print("[OK] Take screenshots automatically")
    print("[OK] Move mouse to any coordinates")
    print("[OK] Type text on screen")
    print("[OK] Press keyboard keys")
    print("[OK] Scroll up/down")
    print("[OK] Click at specific locations")
    
    print("\nNext: Ask the AI to perform complex automation tasks!")
    
    return True

def test_ai_conversation():
    """Test AI conversation with automation capabilities"""
    print("\n" + "=" * 60)
    print("Testing AI Conversation with Automation")
    print("=" * 60)
    
    automation_prompt = """You are ULTRON AI with screen automation capabilities. 

Available functions:
- take_screenshot(): Capture screen
- click_at(x, y): Click coordinates
- type_text(text): Type text
- move_mouse(x, y): Move mouse
- scroll(direction): Scroll up/down
- press_key(key): Press keys
- get_screen_info(): Get screen info

Current screen: 1920x1080
Status: All automation systems online

Respond as ULTRON AI ready to control the screen. Be brief and direct."""
    
    try:
        payload = {
            "model": "llava:7b",
            "prompt": automation_prompt,
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            print(f"AI Response: {ai_response}")
            return True
        else:
            print(f"AI query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"AI conversation error: {e}")
        return False

if __name__ == "__main__":
    # Run automation demo
    demo_ai_automation()
    
    # Test AI conversation
    test_ai_conversation()