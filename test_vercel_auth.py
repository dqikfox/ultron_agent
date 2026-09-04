#!/usr/bin/env python3
import requests
import os

url = "https://ultron-agent-ai-assistant-dkgcuzmbr-dqikfoxs-projects.vercel.app"
headers = {
    "Authorization": "Bearer REDACTED_VERCEL_TOKEN_2",
    "Content-Type": "application/json"
}

try:
    r = requests.post(f"{url}/api/chat", json={"message": "What is Python?"}, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"✅ Success: {r.json()}")
    else:
        print(f"❌ Error: {r.text}")
except Exception as e:
    print(f"❌ Exception: {e}")