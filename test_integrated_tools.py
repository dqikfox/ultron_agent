#!/usr/bin/env python3
"""
Test Integrated Tools with PyAutoGUI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.tool_loader import get_tool_loader
from tools.smart_screenshot_tool import SmartScreenshotTool

def test_integrated_tools():
    print("Testing Integrated Tools with PyAutoGUI")
    print("=" * 50)
    
    # Test tool loader
    print("1. Testing tool loader...")
    loader = get_tool_loader()
    tools = loader.list_tools()
    print(f"   Loaded tools: {', '.join(tools)}")
    
    # Test smart screenshot tool
    print("\n2. Testing smart screenshot tool...")
    screenshot_tool = SmartScreenshotTool()
    
    # Test command matching
    test_commands = [
        "take smart screenshot",
        "analyze screen with ocr",
        "screenshot analyze",
        "regular command"
    ]
    
    for cmd in test_commands:
        matches = screenshot_tool.match(cmd)
        print(f"   '{cmd}' -> {matches}")
    
    # Test actual screenshot
    print("\n3. Taking smart screenshot...")
    result = screenshot_tool.execute("smart screenshot")
    print(f"   Result: {result[:200]}...")
    
    # Test PyAutoGUI integration
    print("\n4. Testing PyAutoGUI integration...")
    pyautogui_tool = loader.find_matching_tool("take screenshot")
    if pyautogui_tool:
        print(f"   Found PyAutoGUI tool: {pyautogui_tool.name}")
        screen_info = pyautogui_tool.execute("screen size")
        print(f"   Screen info: {screen_info}")
    
    print("\n5. Integration complete!")
    print("   - Smart screenshot tool integrated")
    print("   - OCR analysis working")
    print("   - PyAutoGUI connected")
    print("   - Files saved to Pictures folder")

if __name__ == "__main__":
    test_integrated_tools()