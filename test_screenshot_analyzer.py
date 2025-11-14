#!/usr/bin/env python3
"""
Test Screenshot Analyzer Tool
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.screenshot_analyzer_tool import ScreenshotAnalyzerTool

def test_screenshot_analyzer():
    print("Testing Screenshot Analyzer Tool")
    print("=" * 50)
    
    tool = ScreenshotAnalyzerTool()
    
    print("Taking screenshot and analyzing with AI...")
    print("This will:")
    print("1. Take a screenshot")
    print("2. Analyze it with AI vision model")
    print("3. Save description to descriptions folder")
    print("4. Return detailed analysis")
    
    result = tool.execute("analyze screen")
    print(f"\nResult:\n{result}")
    
    print("\nCheck the following folders:")
    print("- screenshots/ (for the image)")
    print("- screenshots/descriptions/ (for the text description)")

if __name__ == "__main__":
    test_screenshot_analyzer()