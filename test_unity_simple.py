#!/usr/bin/env python3
"""Simple Unity Setup Test"""

from pathlib import Path

def test_unity_installation():
    """Test Unity 6000.2.9f1 installation"""
    unity_path = Path("C:/Program Files/Unity/Hub/Editor/6000.2.9f1/Editor/Unity.exe")
    
    print("Testing Unity Installation")
    print("=" * 30)
    
    if unity_path.exists():
        print("SUCCESS: Unity 6000.2.9f1 found")
        print(f"Path: {unity_path}")
        return True
    else:
        print("ERROR: Unity 6000.2.9f1 not found")
        return False

def test_unity_files():
    """Test Unity integration files"""
    print("\nTesting Unity Integration Files")
    print("=" * 35)
    
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
            print(f"SUCCESS: {file_name}")
        else:
            print(f"ERROR: {file_name} - Missing")
            all_found = False
    
    return all_found

def main():
    """Run tests"""
    print("ULTRON Unity 6000.2.9f1 Setup Test")
    print("=" * 40)
    
    unity_ok = test_unity_installation()
    files_ok = test_unity_files()
    
    print("\nTest Results")
    print("=" * 15)
    print(f"Unity Installation: {'PASS' if unity_ok else 'FAIL'}")
    print(f"Integration Files: {'PASS' if files_ok else 'FAIL'}")
    
    if unity_ok and files_ok:
        print("\nSUCCESS: Unity setup is ready!")
        print("\nNext steps:")
        print("1. Run: setup_unity_6000.bat")
        print("2. Create your Unity project")
        print("3. Add ULTRON components")
    else:
        print("\nERROR: Some components missing")

if __name__ == "__main__":
    main()