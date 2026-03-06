#!/usr/bin/env python3
import requests
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

print("🔑 API Key set:", "✅" if os.getenv("OPENAI_API_KEY") else "❌")

# Test Vercel
print("🌐 Testing Vercel...")
try:
    r = requests.get("https://ultron-agent-ai-assistant-dkgcuzmbr-dqikfoxs-projects.vercel.app", timeout=5)
    print(f"Status: {r.status_code}")
    print("✅ Vercel accessible")
except Exception as e:
    print(f"❌ Vercel error: {e}")

print("✅ Test complete")