#!/usr/bin/env python3
"""Test Unity 6000.2.9f1 Setup"""

import requests
import subprocess
import time
from pathlib import Path

def test_unity_installation():
    """Test Unity 6000.2.9f1 installation"""
    unity_path = Path("C:/Program Files/Unity/Hub/Editor/6000.2.9f1/Editor/Unity.exe")
    
    print("🎮 Testing Unity Installation")
    print("=" * 40)
    
    if unity_path.exists():
        print("✅ Unity 6000.2.9f1 found")
        print(f"📍 Path: {unity_path}")
        return True
    else:
        print("❌ Unity 6000.2.9f1 not found")
        return False

def test_ultron_server():
    """Test ULTRON integration server"""
    print("\n🤖 Testing ULTRON Integration Server")
    print("=" * 40)
    
    try:
        # Start server in background
        print("🚀 Starting server...")
        server_process = subprocess.Popen(
            ["python", "unity_integration.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test connection
        response = requests.get("http://localhost:9000/unity/connect", timeout=5)
        if response.status_code == 405:  # Method not allowed (expects POST)
            print("✅ Server is running")
            
            # Test chat endpoint
            chat_response = requests.post(
                "http://localhost:9000/unity/chat",
                json={"message": "Hello from test", "session_id": "test"}
            )
            
            if chat_response.status_code == 200:
                print("✅ Chat endpoint working")
                data = chat_response.json()
                print(f"📝 Response: {data.get('response', 'No response')}")
            else:
                print("❌ Chat endpoint failed")
        
        server_process.terminate()
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def test_unity_files():
    """Test Unity integration files"""
    print("\n📁 Testing Unity Integration Files")
    print("=" * 40)
    
    files_to_check = [
        "UnityUltronClient.cs",
        "UnityExampleUsage.cs",
        "unity_integration.py",
        "setup_unity_6000.bat"
    ]
    
    all_found = True
    for file_name in files_to_check:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - Missing")
            all_found = False
    
    return all_found

def main():
    """Run all tests"""
    print("🧪 ULTRON Unity 6000.2.9f1 Setup Test")
    print("=" * 50)
    
    tests = [
        ("Unity Installation", test_unity_installation),
        ("Integration Files", test_unity_files),
        ("ULTRON Server", test_ultron_server)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 20)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Score: {passed}/{total}")
    
    if passed == total:
        print("\n🚀 All tests passed! Unity setup is ready.")
        print("\nNext steps:")
        print("1. Run: setup_unity_6000.bat")
        print("2. Create your Unity project")
        print("3. Add ULTRON integration components")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()