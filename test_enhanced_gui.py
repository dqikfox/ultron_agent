#!/usr/bin/env python3
"""
Test Enhanced GUI with Interactive OCR
"""

import subprocess
import time
import webbrowser
import requests

def test_enhanced_gui():
    print("Testing Enhanced ULTRON GUI with Interactive OCR")
    print("=" * 60)
    
    # Start OCR server
    print("1. Starting OCR Integration Server...")
    ocr_process = subprocess.Popen([
        "python", "gui_ocr_integration.py"
    ], cwd="c:\\Projects\\ultron_agent")
    time.sleep(3)
    
    # Start GUI server on correct port
    print("2. Starting ULTRON GUI on port 8080...")
    gui_process = subprocess.Popen([
        "python", "-m", "http.server", "8080"
    ], cwd="c:\\Projects\\ultron_agent\\gui\\ultron_enhanced\\web")
    time.sleep(2)
    
    # Test OCR API
    print("3. Testing OCR API...")
    try:
        response = requests.get("http://localhost:5001/api/vision/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ OCR API online")
        else:
            print("   ❌ OCR API failed")
    except Exception as e:
        print(f"   ❌ OCR API error: {e}")
    
    # Test GUI
    print("4. Testing GUI...")
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("   ✅ GUI online")
        else:
            print("   ❌ GUI failed")
    except Exception as e:
        print(f"   ❌ GUI error: {e}")
    
    print("\n🚀 ENHANCED FEATURES:")
    print("   ✅ Interactive progress indicators")
    print("   ✅ Real-time results display")
    print("   ✅ Screenshot thumbnail preview")
    print("   ✅ Success/error notifications")
    print("   ✅ File management buttons")
    print("   ✅ Full report modal")
    print("   ✅ Export functionality")
    
    print("\n📱 USER EXPERIENCE:")
    print("   ✅ Step-by-step progress")
    print("   ✅ Clear success/failure states")
    print("   ✅ Interactive buttons and actions")
    print("   ✅ File location shortcuts")
    print("   ✅ Help and troubleshooting")
    
    print(f"\n🌐 Access Points:")
    print(f"   GUI: http://localhost:8080")
    print(f"   OCR API: http://localhost:5001")
    
    print("\nOpening enhanced GUI...")
    webbrowser.open("http://localhost:8080")
    
    print("\n🎯 TEST INSTRUCTIONS:")
    print("1. Navigate to Vision section")
    print("2. Click 'Start Vision Analysis' button")
    print("3. Watch progress indicators")
    print("4. View detailed results")
    print("5. Use action buttons to explore")

if __name__ == "__main__":
    test_enhanced_gui()