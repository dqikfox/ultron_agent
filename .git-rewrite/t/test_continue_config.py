#!/usr/bin/env python3
"""
Test script to verify Continue extension configuration with local Qwen2.5 Coder model
"""

import requests
import json
import sys
from datetime import datetime

def test_ollama_connection():
    """Test if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Ollama server is running")
            print(f"📋 Available models: {len(models)}")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Ollama server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server at localhost:11434")
        print("💡 Make sure Ollama is running: 'ollama serve'")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def test_qwen_model():
    """Test if qwen2.5-coder model is available"""
    try:
        # Test model generation
        payload = {
            "model": "qwen2.5-coder:1.5b",
            "prompt": "def hello_world():",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 50
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Qwen2.5 Coder model is working")
            print(f"📝 Test response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Model test failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Qwen model: {e}")
        return False

def test_continue_config():
    """Test Continue configuration file"""
    config_path = r"C:\Users\ultro\.continue\config.yaml"
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            
        print("✅ Continue config file found")
        print(f"📍 Location: {config_path}")
        
        # Check for key components
        checks = [
            ("qwen2.5-coder", "Model name"),
            ("localhost:11434", "Local server URL"),
            ("continue-proxy", "Provider type"),
            ("context:", "Context providers")
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description} configured")
            else:
                print(f"❌ {description} missing")
                
        return True
        
    except FileNotFoundError:
        print(f"❌ Continue config file not found at {config_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 ULTRON CONTINUE EXTENSION TEST")
    print("=" * 50)
    print(f"🕐 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Continue Config", test_continue_config),
        ("Qwen2.5 Coder Model", test_qwen_model)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("📊 TEST RESULTS")
    print("-" * 20)
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Your Continue extension should work perfectly with the local Qwen2.5 Coder model.")
        print()
        print("💡 Next steps:")
        print("1. Open VS Code")
        print("2. Press Ctrl+Shift+P")
        print("3. Type 'Continue: Open Chat'")
        print("4. Ask: 'Explain my Ultron automation code'")
    else:
        print("⚠️  Some tests failed. Check the output above for issues.")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
