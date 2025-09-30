import requests
import json

# Test all API endpoints
base_url = "http://localhost:8080"

endpoints = [
    "/api/status",
    "/api/llm/status",
    "/api/voice/status",
    "/api/brain/status",
    "/api/llm/models"
]

print("🧪 Testing ULTRON Agent API Endpoints")
print("=" * 50)

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=5)
        if response.ok:
            print(f"✅ {endpoint}: {response.status_code}")
            data = response.json()
            print(f"   {json.dumps(data, indent=2)[:100]}...")
        else:
            print(f"❌ {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint}: Error - {str(e)}")
    print()

# Test chat endpoint
print("🧪 Testing Chat Functionality")
print("=" * 50)

try:
    chat_data = {"message": "Hello! Can you introduce yourself?"}
    response = requests.post(f"{base_url}/api/llm/chat",
                           json=chat_data,
                           headers={"Content-Type": "application/json"},
                           timeout=30)

    if response.ok:
        print("✅ Chat endpoint working!")
        data = response.json()
        print(f"AI Response: {data.get('response', 'No response')}")
    else:
        print(f"❌ Chat failed: {response.status_code}")
        print(f"Error: {response.text}")

except Exception as e:
    print(f"❌ Chat error: {str(e)}")
