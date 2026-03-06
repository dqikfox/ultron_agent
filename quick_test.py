#!/usr/bin/env python3
import requests
import os

# Set API key directly for testing
os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

print("🔑 API Key:", os.getenv("OPENAI_API_KEY")[:20] + "...")

# Test Vercel endpoint
print("\n🌐 Testing Vercel...")
url = "https://ultron-agent-ai-assistant-dkgcuzmbr-dqikfoxs-projects.vercel.app"

try:
    # Test basic GET
    response = requests.get(url, timeout=5)
    print(f"GET Status: {response.status_code}")
    
    # Test POST to /api/chat
    response = requests.post(f"{url}/api/chat", json={"message": "hello"}, timeout=5)
    print(f"POST /api/chat Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n✅ Test complete")