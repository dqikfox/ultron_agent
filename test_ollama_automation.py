#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.pyautogui_tool import PyAutoGUITool
from tools.ollama_pyautogui_bridge import OllamaPyAutoGUIBridge

def test_automation_setup():
    print("Testing ULTRON Agent Automation Setup")
    print("=" * 50)
    
    # Test PyAutoGUI
    print("1. Testing PyAutoGUI Tool...")
    pyautogui_tool = PyAutoGUITool()
    
    try:
        screen_info = pyautogui_tool.execute("screen size")
        mouse_pos = pyautogui_tool.execute("mouse position")
        print(f"   [OK] {screen_info}")
        print(f"   [OK] {mouse_pos}")
    except Exception as e:
        print(f"   [FAIL] PyAutoGUI error: {e}")
        return False
    
    # Test Ollama Bridge
    print("\n2. Testing Ollama PyAutoGUI Bridge...")
    bridge = OllamaPyAutoGUIBridge()
    
    try:
        functions = bridge.execute("functions")
        print(f"   [OK] {functions}")
        
        # Test function call
        result = bridge.call_function("get_screen_info")
        print(f"   [OK] Function call result: {result}")
    except Exception as e:
        print(f"   [FAIL] Bridge error: {e}")
        return False
    
    # Test function schema
    print("\n3. Testing Function Schema for Ollama...")
    try:
        schema = bridge.execute("schema")
        print(f"   [OK] Schema generated ({len(schema)} characters)")
    except Exception as e:
        print(f"   [FAIL] Schema error: {e}")
    
    print("\n4. Available Automation Functions:")
    for func_name in bridge.function_registry.keys():
        print(f"   - {func_name}")
    
    print("\n[SUCCESS] Automation setup test completed successfully!")
    print("\nNext Steps:")
    print("1. Start Ollama: ollama serve")
    print("2. Load model: ollama run qwen3-coder:480b-cloud")
    print("3. Use automation functions in AI conversations")
    
    return True

if __name__ == "__main__":
    test_automation_setup()