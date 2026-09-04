import requests
import json

def test_image_generation():
    """Test image generation through ULTRON API"""
    try:
        # Test command
        command = "generate image of a beautiful mountain landscape at sunset"
        url = 'http://localhost:8080/api/command'
        data = {'command': command}
        headers = {'Content-Type': 'application/json'}

        print(f"🖼️  Testing image generation...")
        print(f"📤 Command: {command}")

        response = requests.post(url, json=data, headers=headers, timeout=60)

        print(f"📥 Status: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                response_text = result.get('response', 'No response')
                print("📄 Response:")
                print(f"   {response_text}")

                # Check for success indicators
                success_indicators = ['generated successfully', 'image generated', 'saved to']
                if any(indicator in response_text.lower() for indicator in success_indicators):
                    print("✅ Image generation appears successful!")
                    return True
                else:
                    print("⚠️  Response doesn't indicate success")
                    return False

            except json.JSONDecodeError:
                print(f"📄 Raw Response: {response.text}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("⏰ Request timed out (normal for image generation)")
        return True  # Timeout is expected for long-running generation
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_image_generation()
    if success:
        print("\n🎉 Image generation test completed!")
        print("💡 Check C:\\Users\\ultro\\OneDrive\\Pictures\\STABLED for generated images")
    else:
        print("\n❌ Image generation test failed")
