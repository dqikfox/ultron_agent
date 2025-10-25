#!/usr/bin/env python3
"""ULTRON Agent Development Dashboard - Real-time status and controls"""

import json
import time
from pathlib import Path
from datetime import datetime

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
            import requests
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
        
        print("\n" + "="*60)
        print("🤖 ULTRON Agent 3.0 - Development Dashboard")
        print("="*60)
        print(f"⏰ Last Update: {status['timestamp']}")
        
        print("\n📊 Services Status:")
        for service, state in status["services"].items():
            print(f"   {service}: {state}")
        
        print("\n☁️ AWS Integration:")
        print(f"   Enabled: {'✅' if status['aws']['enabled'] else '❌'}")
        print(f"   Endpoint: {status['aws']['endpoint']}")
        
        print(f"\n🔧 Tools: {status['tools']['count']} available")
        print(f"   Latest: {', '.join(status['tools']['latest'])}")
        
        print("\n🎯 Quick Actions:")
        print("   1. Deploy AWS Infrastructure")
        print("   2. Test Amazon Q Integration") 
        print("   3. Run Health Checks")
        print("   4. View Logs")
        print("   5. Exit Dashboard")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Dashboard closed")
            break

if __name__ == "__main__":
    display_dashboard()