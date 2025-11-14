"""Test all Unity integration components"""

from pathlib import Path
import sys


def test_files():
    """Test generated files exist"""
    print("[1/5] Testing Files...")
    
    files = [
        "UnityGame/Assets/Scripts/PlayerController.cs",
        "UnityGame/Assets/Scripts/CameraFollow.cs",
        "UnityGame/Assets/Scripts/GameManager.cs",
        "UnityGame/Assets/Scripts/Sentis/AIEnemy.cs",
        "UnityGame/Assets/Scripts/Sentis/PlayerPredictor.cs",
        "UnityGame/Assets/Scripts/Sentis/DifficultyAI.cs",
        "UnityGame/Assets/Models/EnemyAI.onnx",
        "UnityGame/Assets/Models/DifficultyAI.onnx"
    ]
    
    missing = []
    for f in files:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print(f"  [FAIL] Missing: {missing}")
        return False
    
    print(f"  [OK] All 8 files exist")
    return True


def test_scripts():
    """Test scripts are valid C#"""
    print("[2/5] Testing Scripts...")
    
    scripts = [
        "UnityGame/Assets/Scripts/PlayerController.cs",
        "UnityGame/Assets/Scripts/Sentis/AIEnemy.cs"
    ]
    
    for script in scripts:
        content = Path(script).read_text()
        if "using Unity" not in content or "class" not in content:
            print(f"  [FAIL] Invalid C#: {script}")
            return False
    
    print("  [OK] Scripts valid")
    return True


def test_onnx():
    """Test ONNX models"""
    print("[3/5] Testing ONNX Models...")
    
    models = [
        "UnityGame/Assets/Models/EnemyAI.onnx",
        "UnityGame/Assets/Models/DifficultyAI.onnx"
    ]
    
    for model in models:
        size = Path(model).stat().st_size
        if size < 500:
            print(f"  [FAIL] Model too small: {model}")
            return False
    
    print("  [OK] Models valid")
    return True


def test_tools():
    """Test ULTRON tools"""
    print("[4/5] Testing Tools...")
    
    tools = [
        "tools/unity_ai_tool.py",
        "tools/unity_inference_tool.py",
        "tools/unity_sentis_tool.py"
    ]
    
    for tool in tools:
        if not Path(tool).exists():
            print(f"  [FAIL] Missing: {tool}")
            return False
    
    print("  [OK] All 3 tools exist")
    return True


def test_docs():
    """Test documentation"""
    print("[5/5] Testing Documentation...")
    
    docs = [
        "UNITY_INTEGRATION.md",
        "UNITY_SENTIS_GAME_COMPLETE.md",
        "UNITY_IMPORT_GUIDE.md",
        "UNITY_VSCODE_COMPATIBILITY.md"
    ]
    
    for doc in docs:
        if not Path(doc).exists():
            print(f"  [FAIL] Missing: {doc}")
            return False
    
    print("  [OK] All 4 docs exist")
    return True


def main():
    print("=== Unity Integration Test Suite ===\n")
    
    tests = [
        test_files,
        test_scripts,
        test_onnx,
        test_tools,
        test_docs
    ]
    
    results = [test() for test in tests]
    passed = sum(results)
    
    print(f"\n=== Results: {passed}/5 Passed ===\n")
    
    if passed == 5:
        print("[SUCCESS] All tests passed!")
        print("\nReady to import to Unity:")
        print("1. Run: .\\open_unity_folder.bat")
        print("2. Copy files to Unity project")
        print("3. Follow UNITY_IMPORT_GUIDE.md")
        return 0
    else:
        print("[FAIL] Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
