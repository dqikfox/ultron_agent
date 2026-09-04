import requests
import json

# Test the mobile web interface API
url = "http://localhost:5001/api/command"
data = {"command": "hello ultron"}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
