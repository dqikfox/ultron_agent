#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - System Verification Script
Verifies that all components are working correctly
"""

import sys
import os
import json
import requests
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_required_files():
    """Check for required files"""
    required_files = [
        "main.py",
        "agent_core.py", 
        "brain.py",
        "memory.py",
        "voice.py",
        "vision.py",
        "config.py",
        "ultron_config.json",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_dependencies():
    """Check Python dependencies"""
    try:
        import flask
        import pydantic
        import aiohttp
        import PIL
        import speech_recognition
        import pyttsx3
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama service running with {len(models)} models")
            return True
        else:
            print(f"❌ Ollama service error: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama service not running")
        return False

def check_configuration():
    """Check configuration validity"""
    try:
        with open("ultron_config.json", 'r') as f:
            config = json.load(f)
        
        required_keys = ["llm_model", "ollama_base_url", "use_voice", "use_gui"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"❌ Missing config keys: {', '.join(missing_keys)}")
            return False
        else:
            print("✅ Configuration valid")
            return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def check_imports():
    """Check critical imports"""
    try:
        from agent_core import UltronAgent
        from brain import UltronBrain
        from memory import UltronMemory
        from utils.ultron_logger import log_info
        print("✅ Core modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 ULTRON Agent 3.0 - System Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Core Imports", check_imports),
        ("Ollama Service", check_ollama_service),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if check_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System verification PASSED!")
        print("✅ ULTRON Agent is ready to run")
        print("💡 Try: python main.py")
        return 0
    else:
        print("⚠️  System verification FAILED")
        print("🔧 Run: python fix_all_problems.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())