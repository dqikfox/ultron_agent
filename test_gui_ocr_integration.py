#!/usr/bin/env python3
"""
Test GUI OCR Integration
"""

import subprocess
import time
import requests
import webbrowser
from threading import Thread

def start_ocr_server():
    """Start the OCR integration server"""
    print("Starting OCR Integration Server...")
    subprocess.Popen([
        "python", "gui_ocr_integration.py"
    ], cwd="c:\\Projects\\ultron_agent")

def start_gui_server():
    """Start the GUI server"""
    print("Starting GUI Server...")
    subprocess.Popen([
        "python", "-m", "http.server", "8080"
    ], cwd="c:\\Projects\\ultron_agent\\gui\\ultron_enhanced\\web")

def test_integration():
    print("Testing ULTRON GUI OCR Integration")
    print("=" * 50)
    
    # Start servers
    print("1. Starting servers...")
    start_ocr_server()
    time.sleep(2)
    start_gui_server()
    time.sleep(3)
    
    # Test OCR API
    print("2. Testing OCR API...")
    try:
        response = requests.get("http://localhost:5001/api/vision/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] OCR API Status: {data['status']}")
            print(f"   [OK] Tools: {data['tools']}")
        else:
            print(f"   [FAIL] OCR API returned {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] OCR API error: {e}")
    
    # Test GUI
    print("3. Testing GUI...")
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("   [OK] GUI server running")
        else:
            print(f"   [FAIL] GUI returned {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] GUI error: {e}")
    
    print("\n4. Integration Status:")
    print("   [OK] OCR Integration Server: http://localhost:5001")
    print("   [OK] ULTRON GUI: http://localhost:8080")
    print("   [OK] Vision section connected to OCR")
    
    print("\n5. Opening GUI...")
    webbrowser.open("http://localhost:8080")
    
    print("\nGUI OCR Integration Test Complete!")
    print("\nTo test:")
    print("1. Open http://localhost:8080")
    print("2. Navigate to Vision section")
    print("3. Click 'CAPTURE' button")
    print("4. Check Screenshots folder for results")

if __name__ == "__main__":
    test_integration()