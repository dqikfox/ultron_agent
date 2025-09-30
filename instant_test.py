import requests
import json
import time

def test_endpoint(url, timeout=3):
    """Test a single endpoint with short timeout"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start_time

        if response.ok:
            return f"✅ OK ({elapsed:.2f}s)"
        else:
            return f"❌ HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return f"⏰ TIMEOUT (>{timeout}s)"
    except requests.exceptions.ConnectionError:
        return f"🔌 CONNECTION REFUSED"
    except Exception as e:
        return f"❌ ERROR: {str(e)[:50]}"

def test_chat_quick():
    """Test chat with very short timeout"""
    try:
        data = {"message": "Hi"}
        response = requests.post("http://localhost:8080/api/llm/chat",
                               json=data, timeout=5)  # Only 5 second timeout
        if response.ok:
            result = response.json()
            return f"✅ CHAT WORKS - Response: {str(result)[:100]}..."
        else:
            return f"❌ CHAT FAILED - HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return "⏰ CHAT TIMEOUT (>5s) - Server responding slowly"
    except Exception as e:
        return f"❌ CHAT ERROR: {str(e)[:50]}"

print("🚀 QUICK ULTRON SYSTEM TEST")
print("=" * 40)

# Test basic endpoints with short timeouts
endpoints = [
    ("Status", "http://localhost:8080/api/status"),
    ("LLM Status", "http://localhost:8080/api/llm/status"),
    ("Voice Status", "http://localhost:8080/api/voice/status"),
    ("Brain Status", "http://localhost:8080/api/brain/status")
]

all_good = True
for name, url in endpoints:
    result = test_endpoint(url)
    print(f"{name:12}: {result}")
    if not result.startswith("✅"):
        all_good = False

print("\n🧠 CHAT TEST:")
chat_result = test_chat_quick()
print(f"Chat Test: {chat_result}")

if all_good and chat_result.startswith("✅"):
    print("\n🎉 SYSTEM FULLY OPERATIONAL!")
else:
    print("\n⚠️  Some issues detected - check above")

print("\n✅ Test completed - no infinite loops!")
