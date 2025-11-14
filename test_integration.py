#!/usr/bin/env python3
"""Integration test for ULTRON Agent complete system"""

import asyncio
import requests
import json
from utils.ultron_logger import log_info, log_error

async def test_system_integration():
    """Test all major system components"""
    
    tests = []
    
    # Test 1: Ollama backend
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        tests.append(("Ollama Backend", response.status_code == 200))
    except:
        tests.append(("Ollama Backend", False))
    
    # Test 2: Web GUI
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        tests.append(("Web GUI", response.status_code == 200))
    except:
        tests.append(("Web GUI", False))
    
    # Test 3: Amazon Q Auto-run
    try:
        with open("ultron_config.json", "r") as f:
            config = json.load(f)
        auto_run_enabled = config.get("auto_run", {}).get("enabled", False)
        tests.append(("Amazon Q Auto-run Config", auto_run_enabled))
    except:
        tests.append(("Amazon Q Auto-run Config", False))
    
    # Test 4: AI News Search
    try:
        import subprocess
        result = subprocess.run(["python", "get_ai_news.py"], 
                              capture_output=True, text=True, timeout=10)
        tests.append(("AI News Search", result.returncode == 0))
    except:
        tests.append(("AI News Search", False))
    
    # Results
    passed = sum(1 for _, status in tests if status)
    total = len(tests)
    
    print(f"\n=== ULTRON Agent Integration Test Results ===")
    for test_name, status in tests:
        status_str = "PASS" if status else "FAIL"
        print(f"{test_name}: {status_str}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All systems operational!")
        return True
    else:
        print("Some systems need attention")
        return False

if __name__ == "__main__":
    asyncio.run(test_system_integration())