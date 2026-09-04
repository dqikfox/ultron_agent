#!/usr/bin/env python3
"""
ULTRON Agent System Test - Single Run Diagnostic
Tests all components once and provides a clear report
"""

import requests
import json
import time
import subprocess
import sys

def test_endpoint(url, name):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            return True, data
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_chat(url, message):
    """Test chat functionality"""
    try:
        payload = {"message": message}
        response = requests.post(url, json=payload, timeout=30)
        if response.ok:
            data = response.json()
            return True, data.get('response', 'No response field')
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def check_port(port):
    """Check if a port is in use"""
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        return f":{port}" in result.stdout
    except:
        return False

def main():
    print("🔍 ULTRON Agent System Test")
    print("=" * 50)

    base_url = "http://localhost:8080"

    # Test services
    print("\n📡 Service Status:")
    print("-" * 20)

    services = {
        "Ollama (11434)": check_port(11434),
        "Web GUI (8080)": check_port(8080),
        "API Server (5001)": check_port(5001)
    }

    for service, status in services.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}: {'Running' if status else 'Stopped'}")

    # Test API endpoints
    print("\n🌐 API Endpoints:")
    print("-" * 20)

    endpoints = [
        ("/api/status", "System Status"),
        ("/api/llm/status", "LLM Status"),
        ("/api/voice/status", "Voice Status"),
        ("/api/brain/status", "Brain Status"),
        ("/api/llm/models", "Available Models")
    ]

    working_endpoints = 0
    for endpoint, name in endpoints:
        success, result = test_endpoint(f"{base_url}{endpoint}", name)
        icon = "✅" if success else "❌"
        print(f"{icon} {name}: {'OK' if success else result}")
        if success:
            working_endpoints += 1
            # Show key info for important endpoints
            if endpoint == "/api/llm/status" and isinstance(result, dict):
                print(f"   Current Model: {result.get('model', 'Unknown')}")
                print(f"   Available Models: {len(result.get('available_models', []))}")

    # Test chat functionality
    print("\n💬 Chat Functionality:")
    print("-" * 20)

    if working_endpoints >= 3:  # If most endpoints work, try chat
        print("Testing chat with AI...")
        success, result = test_chat(f"{base_url}/api/llm/chat", "Hello! Can you say hi back?")

        if success:
            print("✅ Chat working!")
            print(f"AI Response: {result[:100]}{'...' if len(str(result)) > 100 else ''}")
        else:
            print(f"❌ Chat failed: {result}")
    else:
        print("❌ Skipping chat test - too many API failures")

    # Summary
    print("\n📊 Summary:")
    print("-" * 20)

    total_services = len(services)
    running_services = sum(services.values())

    total_endpoints = len(endpoints)

    print(f"Services Running: {running_services}/{total_services}")
    print(f"API Endpoints Working: {working_endpoints}/{total_endpoints}")

    if running_services >= 2 and working_endpoints >= 3:
        print("🎉 System Status: READY FOR USE!")
        print("✅ Users can interact with the AI through the web interface")
        print(f"🌐 Access GUI at: {base_url}")
    elif running_services >= 1:
        print("⚠️  System Status: PARTIALLY WORKING")
        print("Some components need attention")
    else:
        print("❌ System Status: NOT READY")
        print("Services need to be started")

    print("\n🔧 Quick Start Commands:")
    print("-" * 20)
    print("1. Start Ollama: ollama serve")
    print("2. Start Web GUI: python web_gui_server.py")
    print("3. Open browser: http://localhost:8080")

if __name__ == "__main__":
    main()
