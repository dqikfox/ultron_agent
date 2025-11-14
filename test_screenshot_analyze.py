"""
Test Screenshot & Analyze Functionality
"""
import requests
import time

BASE_URL = "http://localhost:8080"

print("Testing Screenshot & Analyze")
print("=" * 60)

# Test 1: Screenshot
print("\n[TEST 1] Screenshot with 3-second delay")
print("Starting capture in 3 seconds...")

response = requests.post(f"{BASE_URL}/api/vision/capture")
data = response.json()

if data.get('success'):
    print(f"  [OK] Screenshot saved: {data['image_path']}")
    print(f"  [OK] Timestamp: {data['timestamp']}")
else:
    print(f"  [FAIL] {data.get('error')}")

# Wait a moment
time.sleep(2)

# Test 2: Analyze
print("\n[TEST 2] Analyze screenshot")
print("Running AI description + OCR...")

response = requests.post(f"{BASE_URL}/api/vision/analyze")
data = response.json()

if data.get('success'):
    print(f"  [OK] Image: {data['image_path']}")
    print(f"  [OK] AI Description: {data['ai_description'][:100]}...")
    print(f"  [OK] OCR Text: {data['ocr_text'][:100] if data['ocr_text'] else 'No text'}...")
    print(f"  [OK] Confidence: {data['ocr_confidence']}%")
else:
    print(f"  [FAIL] {data.get('error')}")

print("\n" + "=" * 60)
print("Test complete!")
