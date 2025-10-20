import requests
import json
import time

def test_image_generation():
    try:
        url = 'http://localhost:8080/api/command'
        data = {'command': 'generate image of a beautiful sunset over mountains'}
        headers = {'Content-Type': 'application/json'}

        print("Sending image generation command to ULTRON API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data, headers=headers, timeout=60)

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
        else:
            print(f"Error Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_image_generation()
