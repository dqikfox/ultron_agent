#!/usr/bin/env python3
import requests
import os

os.environ["OPENAI_API_KEY"] = "REDACTED_OPENAI_KEY_3"

url = "https://ultron-agent-ai-assistant-dkgcuzmbr-dqikfoxs-projects.vercel.app"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    "Content-Type": "application/json"
}

try:
    r = requests.post(f"{url}/api/chat", json={"message": "hello"}, headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Response: {r.json()}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Error: {e}")