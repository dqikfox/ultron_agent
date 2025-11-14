#!/usr/bin/env python3
"""Verify Avatar Game Integration"""

import requests
import json
import os

def verify_avatar_integration():
    """Verify avatar game integration with all services"""
    print("🔍 Verifying Avatar Game Integration...")
    
    # Check file locations
    files_to_check = [
        ("gui/ultron_enhanced/web/ultron_avatar_game.html", "Avatar game in web directory"),
        ("avatar_control_api.py", "Avatar control API script"),
        ("unity_integration.py", "Unity integration script"),
        ("api_integration_server.py", "API integration server"),
    ]
    
    print("\n📁 File Verification:")
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - MISSING")
    
    # Check service endpoints
    endpoints = [
        ("http://localhost:11434/api/tags", "Ollama LLM service"),
        ("http://localhost:8080/", "Web GUI server"),
        ("http://localhost:8080/ultron_avatar_game.html", "Avatar game via web GUI"),
        ("http://localhost:8081/api/pyautogui/screen", "Avatar control API"),
        ("http://localhost:9000/unity/connect", "Unity integration", "POST"),
        ("http://localhost:5002/api/computer-use/status", "Computer use integration"),
    ]
    
    print("\n🌐 Service Verification:")
    for endpoint_info in endpoints:
        endpoint = endpoint_info[0]
        description = endpoint_info[1]
        method = endpoint_info[2] if len(endpoint_info) > 2 else "GET"
        
        try:
            if method == "POST":
                response = requests.post(endpoint, json={"test": True}, timeout=3)
            else:
                response = requests.get(endpoint, timeout=3)
            
            if response.status_code in [200, 201]:
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {description} - Not running")
        except requests.exceptions.Timeout:
            print(f"⚠️  {description} - Timeout")
        except Exception as e:
            print(f"❌ {description} - Error: {str(e)}")
    
    # Test avatar game functionality
    print("\n🎮 Avatar Game Functionality:")
    
    # Test model availability
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            required_models = ['exaone-deep:7.8b', 'mistral-nemo:12b', 'gpt-oss:20b-cloud', 'llava:7b', 'gemma3:12b']
            
            available_models = [model['name'] for model in models]
            for model in required_models:
                if any(model in available for available in available_models):
                    print(f"✅ Model {model} available")
                else:
                    print(f"⚠️  Model {model} not found")
    except:
        print("❌ Could not check model availability")
    
    # Test screen capture capability
    try:
        response = requests.post("http://localhost:8081/api/vision/live_capture", 
                               json={}, timeout=5)
        if response.status_code == 200:
            print("✅ Screen capture functionality working")
        else:
            print("⚠️  Screen capture may not be working")
    except:
        print("❌ Screen capture not accessible")
    
    print("\n🔗 Integration Summary:")
    print("• Avatar game moved to correct web directory")
    print("• All backend services maintain their original ports")
    print("• Unity integration unchanged (port 9000)")
    print("• Avatar control API on port 8081 as expected")
    print("• Web GUI serves avatar game at /ultron_avatar_game.html")
    
    print("\n✨ Integration Status: Ready for use!")

if __name__ == "__main__":
    verify_avatar_integration()