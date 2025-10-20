#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.pyautogui_tool import PyAutoGUITool

def test_pyautogui():
    print("Testing PyAutoGUI Integration")
    print("=" * 40)
    
    tool = PyAutoGUITool()
    
    # Test 1: Screen info
    print("1. Testing screen info...")
    result = tool.execute("screen size")
    print(f"Result: {result}")
    
    # Test 2: Mouse position
    print("\n2. Testing mouse position...")
    result = tool.execute("mouse position")
    print(f"Result: {result}")
    
    # Test 3: Screenshot
    print("\n3. Testing screenshot...")
    result = tool.execute("screenshot")
    print(f"Result: {result}")
    
    # Test 4: Command matching
    print("\n4. Testing command matching...")
    test_commands = [
        "take a screenshot",
        "click at 100,200", 
        "type hello world",
        "move mouse to 500,300",
        "scroll down",
        "press key enter",
        "regular command"
    ]
    
    for cmd in test_commands:
        matches = tool.match(cmd)
        print(f"  '{cmd}' -> {matches}")
    
    # Test 5: Help
    print("\n5. Testing help...")
    result = tool.execute("help")
    print(f"Result: {result}")
    
    print("\nPyAutoGUI integration test completed!")

if __name__ == "__main__":
    test_pyautogui()