#!/usr/bin/env python3
"""Test Avatar Game Dependencies"""

import requests
import json
import time
import os

def test_avatar_game_dependencies():
    """Test all avatar game dependencies"""
    print("🧪 Testing Avatar Game Dependencies...")
    
    tests = []
    
    # Test 1: Avatar game file exists in web directory
    avatar_file = "gui/ultron_enhanced/web/ultron_avatar_game.html"
    if os.path.exists(avatar_file):
        tests.append(("✅", "Avatar game file in web directory"))
    else:
        tests.append(("❌", "Avatar game file missing from web directory"))
    
    # Test 2: Ollama service (port 11434)
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            tests.append(("✅", "Ollama service running"))
        else:
            tests.append(("❌", "Ollama service not responding"))
    except:
        tests.append(("❌", "Ollama service not accessible"))
    
    # Test 3: Web GUI server (port 8080)
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            tests.append(("✅", "Web GUI server running"))
        else:
            tests.append(("❌", "Web GUI server not responding"))
    except:
        tests.append(("❌", "Web GUI server not accessible"))
    
    # Test 4: Avatar control API (port 8081)
    try:
        response = requests.get("http://localhost:8081/api/pyautogui/screen", timeout=5)
        if response.status_code == 200:
            tests.append(("✅", "Avatar control API running"))
        else:
            tests.append(("❌", "Avatar control API not responding"))
    except:
        tests.append(("❌", "Avatar control API not accessible"))
    
    # Test 5: Unity integration (port 9000)
    try:
        response = requests.post("http://localhost:9000/unity/connect", 
                               json={"session_id": "test", "game_name": "Test"}, 
                               timeout=5)
        if response.status_code == 200:
            tests.append(("✅", "Unity integration running"))
        else:
            tests.append(("❌", "Unity integration not responding"))
    except:
        tests.append(("❌", "Unity integration not accessible"))
    
    # Test 6: API integration server (port 5002)
    try:
        response = requests.get("http://localhost:5002/api/computer-use/status", timeout=5)
        if response.status_code == 200:
            tests.append(("✅", "API integration server running"))
        else:
            tests.append(("❌", "API integration server not responding"))
    except:
        tests.append(("❌", "API integration server not accessible"))
    
    # Test 7: Avatar game accessibility via web GUI
    try:
        response = requests.get("http://localhost:8080/ultron_avatar_game.html", timeout=5)
        if response.status_code == 200:
            tests.append(("✅", "Avatar game accessible via web GUI"))
        else:
            tests.append(("❌", "Avatar game not accessible via web GUI"))
    except:
        tests.append(("❌", "Avatar game not accessible via web GUI"))
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for status, description in tests:
        print(f"{status} {description}")
        if status == "✅":
            passed += 1
    
    print("=" * 50)
    print(f"📈 Summary: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All dependencies working correctly!")
        return True
    else:
        print("⚠️  Some dependencies need attention")
        return False

if __name__ == "__main__":
    test_avatar_game_dependencies()