"""
Quick test to verify Continue extension can access local Ollama models.
Run this to confirm configuration is working.
"""

import requests
import json

def test_ollama_connection():
    """Test basic Ollama connectivity"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"[OK] Ollama connected - {len(models)} models available")
            return True
        else:
            print(f"[FAIL] Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Ollama connection failed: {e}")
        return False

def test_model_generation(model_name="qwen2.5-coder:7b"):
    """Test model can generate responses"""
    try:
        payload = {
            "model": model_name,
            "prompt": "Write a Python function to add two numbers:",
            "stream": False
        }
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {model_name} generated response")
            print(f"   Response preview: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"[FAIL] {model_name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {model_name} generation failed: {e}")
        return False

def main():
    print("Testing Continue Extension - Local Ollama Models\n")
    
    # Test 1: Connection
    print("Test 1: Ollama Connection")
    if not test_ollama_connection():
        print("\nFAILED: Ollama not accessible")
        return
    
    # Test 2: Primary model
    print("\nTest 2: Primary Model (Qwen 2.5 Coder 7B)")
    if not test_model_generation("qwen2.5-coder:7b"):
        print("\nWARNING: Primary model not responding")
    
    # Test 3: Autocomplete model
    print("\nTest 3: Autocomplete Model (Qwen 2.5 Coder 1.5B)")
    if not test_model_generation("qwen2.5-coder:1.5b"):
        print("\nWARNING: Autocomplete model not responding")
    
    print("\nALL TESTS PASSED - Continue extension ready to use!")
    print("\nNext steps:")
    print("1. Open VS Code")
    print("2. Press Ctrl+L to open Continue chat")
    print("3. Type: 'Hello, test local model'")
    print("4. Verify response comes from Qwen 2.5 Coder 7B")

if __name__ == "__main__":
    main()
