import requests
import json
import time

def test_stable_diffusion_via_api():
    """Test Stable Diffusion through ULTRON API"""

    print("🖼️  Testing Stable Diffusion via ULTRON API")
    print("=" * 60)

    # Check if ULTRON is running
    try:
        response = requests.get('http://localhost:8080/api/agent/info', timeout=5)
        if response.status_code == 200:
            agent_info = response.json()
            print("✅ ULTRON Agent Status:")
            print(f"   Status: {agent_info.get('status', 'unknown')}")
            print(f"   Tools: {agent_info.get('tools_count', 0)}")
        else:
            print("❌ ULTRON Agent not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to ULTRON: {e}")
        return

    # Check available tools
    try:
        response = requests.get('http://localhost:8080/api/tools', timeout=5)
        if response.status_code == 200:
            tools_data = response.json()
            tools = tools_data.get('tools', [])
            tool_names = [tool['name'] for tool in tools]
            print(f"✅ Available Tools: {len(tools)}")
            if 'Stable Diffusion Image Generator' in tool_names:
                print("   ✅ Stable Diffusion tool found!")
            else:
                print("   ❌ Stable Diffusion tool not found")
                print(f"   Available tools: {tool_names}")
                return
        else:
            print("❌ Cannot get tools list")
            return
    except Exception as e:
        print(f"❌ Error checking tools: {e}")
        return

    # Test image generation command
    print("\n🎨 Testing Image Generation...")
    command = "generate image of a beautiful sunset over mountains with vibrant colors"

    try:
        url = 'http://localhost:8080/api/command'
        data = {'command': command}
        headers = {'Content-Type': 'application/json'}

        print(f"📤 Sending command: {command}")
        response = requests.post(url, json=data, headers=headers, timeout=120)

        print(f"📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                response_text = result.get('response', 'No response')
                print("📄 Response:")
                print(f"   {response_text}")

                # Check if image was generated
                if 'generated successfully' in response_text.lower() or 'image generated' in response_text.lower():
                    print("✅ Image generation appears successful!")
                elif 'failed' in response_text.lower():
                    print("❌ Image generation failed")
                else:
                    print("⚠️  Unexpected response format")

            except json.JSONDecodeError:
                print(f"📄 Raw Response: {response.text}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   {response.text}")

    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this is normal for image generation)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "=" * 60)
    print("🏁 Test completed")

if __name__ == "__main__":
    test_stable_diffusion_via_api()
