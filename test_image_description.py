#!/usr/bin/env python3
"""
Test Image Description Tool
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.image_description_tool import ImageDescriptionTool

def test_image_description():
    print("Testing Image Description Tool")
    print("=" * 50)
    
    tool = ImageDescriptionTool()
    
    # Test with latest screenshot
    screenshots_dir = os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures", "Screenshots")
    
    # Find latest screenshot
    if os.path.exists(screenshots_dir):
        screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
        if screenshots:
            latest_screenshot = max(screenshots, key=lambda x: os.path.getctime(os.path.join(screenshots_dir, x)))
            screenshot_path = os.path.join(screenshots_dir, latest_screenshot)
            
            print(f"Analyzing latest screenshot: {latest_screenshot}")
            print("This will provide detailed visual analysis...")
            
            result = tool.execute(f"describe image {screenshot_path}")
            print(f"\nResult:\n{result}")
        else:
            print("No screenshots found to analyze")
    else:
        print("Screenshots directory not found")
    
    # Test command matching
    print("\nTesting command matching:")
    test_commands = [
        "describe image test.png",
        "analyze image screenshot.jpg", 
        "what's in image photo.png",
        "visual analysis picture.jpeg",
        "regular command"
    ]
    
    for cmd in test_commands:
        matches = tool.match(cmd)
        print(f"  '{cmd}' -> {matches}")

if __name__ == "__main__":
    test_image_description()