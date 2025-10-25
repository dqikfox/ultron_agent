#!/usr/bin/env python3
"""ULTRON Agent Development Dashboard - Real-time status and controls"""
#!/usr/bin/env python3
"""ULTRON Agent Development Dashboard - Real-time status and controls"""

# Your code here

config_results = test_config_updated()

# Rest of your code here

import json
import time
from pathlib import Path
from datetime import datetime
import requests

def get_system_status():
    """Get comprehensive system status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "services": {},
        "aws": {},
        "tools": {},
        "ai_models": {}
    }

    # Check core services
    services = [
        ("Ollama", "http://localhost:11434"),
        ("Web GUI", "http://localhost:8080"),
        ("API Server", "http://localhost:5000"),
        ("Mobile Interface", "http://localhost:8001")
    ]

    for name, url in services:
        try:
            response = requests.get(url, timeout=2)
            status["services"][name] = "✅ Online"
        except:
            status["services"][name] = "❌ Offline"

    # Check AWS integration
    config_path = Path("ultron_config.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

        aws_config = config.get("aws_bedrock", {})
        status["aws"]["enabled"] = aws_config.get("enabled", False)
        status["aws"]["endpoint"] = aws_config.get("api_endpoint", "Not configured")

    # Check available tools
    tools_dir = Path("tools")
    if tools_dir.exists():
        tool_files = list(tools_dir.glob("*_tool.py"))
        status["tools"]["count"] = len(tool_files)
        status["tools"]["latest"] = [f.stem for f in tool_files[-5:]]

    return status

def display_dashboard():
    """Display real-time dashboard"""
    while True:
        status = get_system_status()

        print("\n - development_dashboard.py:67" + "="*60)
        print("🤖 ULTRON Agent 3.0  Development Dashboard - development_dashboard.py:68")
        print("= - development_dashboard.py:69"*60)
        print(f"⏰ Last Update: {status['timestamp']} - development_dashboard.py:70")

        print("\n📊 Services Status: - development_dashboard.py:72")
        for service, state in status["services"].items():
            print(f"{service}: {state} - development_dashboard.py:74")

        print("\n☁️ AWS Integration: - development_dashboard.py:76")
        print(f"Enabled: {'✅' if status['aws']['enabled'] else '❌'} - development_dashboard.py:77")
        print(f"Endpoint: {status['aws']['endpoint']} - development_dashboard.py:78")

        print(f"\n🔧 Tools: {status['tools']['count']} available - development_dashboard.py:80")
        print(f"Latest: {', '.join(status['tools']['latest'])} - development_dashboard.py:81")

        print("\n🎯 Quick Actions: - development_dashboard.py:83")
        print("1. Deploy AWS Infrastructure - development_dashboard.py:84")
        print("2. Test Amazon Q Integration - development_dashboard.py:85")
        print("3. Run Health Checks - development_dashboard.py:86")
        print("4. View Logs - development_dashboard.py:87")
        print("5. Exit Dashboard - development_dashboard.py:88")

        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Dashboard closed - development_dashboard.py:93")
            break

if __name__ == "__main__":
    display_dashboard()
