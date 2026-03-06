#!/usr/bin/env python3
"""Simple test without external dependencies"""

import requests
import os

def test_vercel_assistant():
    print("🌐 Testing Vercel Assistant...")
    url = "https://ultron-agent-ai-assistant-dkgcuzmbr-dqikfoxs-projects.vercel.app"
    
    try:
        response = requests.post(
            f"{url}/api/chat",
            json={"message": "Hello, what is Python?"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_openai_key():
    print("🔑 Testing OpenAI API Key...")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print(f"✅ API Key found: {api_key[:10]}...")
        return True
    else:
        print("❌ No API key found")
        return False

if __name__ == "__main__":
    print("Simple Assistant Tests\n")
    
    key_ok = test_openai_key()
    vercel_ok = test_vercel_assistant()
    
    print(f"\nResults:")
    print(f"API Key: {'✅' if key_ok else '❌'}")
    print(f"Vercel: {'✅' if vercel_ok else '❌'}")