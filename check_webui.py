import requests

def check_webui():
    """Check if Automatic1111 WebUI is running and get models"""
    try:
        # First check if main page is accessible
        main_response = requests.get('http://127.0.0.1:7860/', timeout=5)
        if main_response.status_code != 200:
            print(f"❌ WebUI main page not accessible (status: {main_response.status_code}) - check_webui.py:9")
            return False

        print("✅ WebUI main page accessible - check_webui.py:12")

        # Try API endpoints
        api_endpoints = [
            'http://127.0.0.1:7860/sdapi/v1/sd-models',
            'http://127.0.0.1:7860/sdapi/v1/options',
            'http://127.0.0.1:7860/api/predict'
        ]

        for endpoint in api_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    print(f"✅ API endpoint working: {endpoint} - check_webui.py:25")
                    if 'sd-models' in endpoint:
                        models = response.json()
                        print(f"📄 Found {len(models)} models: - check_webui.py:28")
                        for model in models[:3]:  # Show first 3
                            model_name = model.get('model_name', 'Unknown')
                            print(f"📄 {model_name} - check_webui.py:31")
                    return True
                else:
                    print(f"⚠️  API endpoint {endpoint} returned status {response.status_code} - check_webui.py:34")
            except Exception as e:
                print(f"⚠️  API endpoint {endpoint} failed: {e} - check_webui.py:36")

        print("❌ API not enabled. Make sure to start WebUI with api flag - check_webui.py:38")
        print("💡 Stop WebUI (Ctrl+C) and restart with: webuiuser.bat api - check_webui.py:39")
        return False

    except Exception as e:
        print(f"❌ Cannot connect to WebUI: {e} - check_webui.py:43")
        print("💡 Make sure Automatic1111 WebUI is running on port 7860 - check_webui.py:44")
        return False

if __name__ == "__main__":
    check_webui()
