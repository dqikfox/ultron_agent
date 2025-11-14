"""Test Unity AI Integration"""

import asyncio
import requests
import subprocess
import time
from pathlib import Path


def test_ollama():
    """Test Ollama availability"""
    print("[1/5] Testing Ollama...")
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            print("[OK] Ollama running")
            return True
    except:
        pass
    print("[FAIL] Ollama not running - start with: ollama serve")
    return False


def test_unity_bridge():
    """Test Unity Bridge"""
    print("[2/5] Testing Unity Bridge...")
    try:
        r = requests.post(
            "http://localhost:8765/api/assistant",
            json={"query": "test"},
            timeout=5
        )
        if r.status_code == 200:
            print("[OK] Unity Bridge running")
            return True
    except:
        pass
    print("[FAIL] Unity Bridge not running - start with: start_unity_bridge.bat")
    return False


def test_unity_tool():
    """Test Unity Tool discovery"""
    print("[3/5] Testing Unity Tool...")
    tool_path = Path("tools/unity_ai_tool.py")
    if tool_path.exists():
        print("[OK] Unity Tool installed")
        return True
    print("[FAIL] Unity Tool not found")
    return False


def test_assistant_query():
    """Test Unity Assistant"""
    print("[4/5] Testing Assistant query...")
    try:
        r = requests.post(
            "http://localhost:8765/api/assistant",
            json={"query": "Create a simple Unity player controller"},
            timeout=30
        )
        if r.status_code == 200:
            response = r.json().get("response", "")
            print(f"[OK] Assistant response: {response[:100]}...")
            return True
    except Exception as e:
        print(f"[FAIL] Assistant failed: {str(e)}")
    return False


def test_game_generation():
    """Test game code generation"""
    print("[5/5] Testing game generation...")
    try:
        r = requests.post(
            "http://localhost:8765/api/generate",
            json={"prompt": "Create a simple 2D platformer player script with jump and movement"},
            timeout=30
        )
        if r.status_code == 200:
            result = r.json()
            code = result.get("code", "")
            print(f"[OK] Generated {len(code)} characters of code")
            
            # Save generated code
            output = Path("generated_player.cs")
            output.write_text(code)
            print(f"[OK] Saved to: {output}")
            return True
    except Exception as e:
        print(f"[FAIL] Generation failed: {str(e)}")
    return False


def main():
    print("=== Unity AI Integration Test ===\n")
    
    results = [
        test_ollama(),
        test_unity_bridge(),
        test_unity_tool(),
        test_assistant_query(),
        test_game_generation()
    ]
    
    passed = sum(results)
    print(f"\n=== Results: {passed}/5 tests passed ===")
    
    if passed == 5:
        print("\n[SUCCESS] All systems operational!")
        print("\nNext steps:")
        print("1. Install Unity Hub: https://unity.com/download")
        print("2. Install Unity 2022.3 LTS or later")
        print("3. Create new Unity project")
        print("4. Use ULTRON to generate game code:")
        print('   "unity create a 2D platformer game"')
    else:
        print("\n[WARNING] Some tests failed. Fix issues above.")


if __name__ == '__main__':
    main()
