#!/usr/bin/env python3
"""
Test script for GitHub Models integration tool
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.github_models_tool import GitHubModelsTool

def test_github_models():
    """Test the GitHub Models integration"""
    print("Testing GitHub Models Integration Tool")
    print("=" * 50)
    
    # Initialize the tool
    tool = GitHubModelsTool()
    
    # Test 1: Check if tool initializes
    print("[OK] Tool initialized successfully")
    
    # Test 2: Check command matching
    test_commands = [
        "github model test",
        "ask mistral a question",
        "github ai help",
        "regular command"
    ]
    
    print("\nTesting command matching:")
    for cmd in test_commands:
        matches = tool.match(cmd)
        print(f"  '{cmd}' -> {matches}")
    
    # Test 3: Check available models
    print("\nAvailable models:")
    models = tool.get_available_models()
    for model in models:
        print(f"  - {model}")
    
    # Test 4: Test connection (if possible)
    print("\nTesting connection:")
    try:
        connection_ok = tool.test_connection()
        if connection_ok:
            print("  [OK] Connection successful")
        else:
            print("  [FAIL] Connection failed")
    except Exception as e:
        print(f"  [ERROR] Connection error: {e}")
    
    # Test 5: Test a simple query
    print("\nTesting simple query:")
    try:
        response = tool.execute("ask mistral: What is AI?")
        print(f"  Response: {response[:100]}...")
    except Exception as e:
        print(f"  [ERROR] Query error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_github_models()