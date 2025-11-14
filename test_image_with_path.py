#!/usr/bin/env python3
"""
Test Image Description with Specific Path
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.image_description_tool import ImageDescriptionTool

def test_with_specific_image():
    print("Testing Image Description with Latest Screenshot")
    print("=" * 60)
    
    tool = ImageDescriptionTool()
    
    # Use latest screenshot
    image_path = r"C:\Users\ultro\OneDrive\Pictures\Screenshots\screenshot_1761359994.png"
    
    if os.path.exists(image_path):
        print(f"Analyzing: {image_path}")
        print("Requesting detailed visual analysis...")
        
        result = tool.execute("describe image", image_path=image_path)
        print(f"\nDetailed Image Analysis:\n{result}")
    else:
        print(f"Image not found: {image_path}")

if __name__ == "__main__":
    test_with_specific_image()