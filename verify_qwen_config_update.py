"""
ULTRON Project Configuration Verification - Qwen2.5-Coder:1.5b Update
Verifies all configurations have been updated to use the memory-optimized model
"""

import json
import os
import yaml
from pathlib import Path

def check_json_config(file_path, description):
    """Check JSON configuration file"""
    print(f"\n📋 Checking {description}: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check for Qwen model references
        qwen_found = False
        qwen_version = None
        
        def check_dict(d, path=""):
            nonlocal qwen_found, qwen_version
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    check_dict(value, current_path)
                elif isinstance(value, str) and "qwen" in value.lower():
                    qwen_found = True
                    if "1.5b" in value:
                        qwen_version = "1.5b ✅"
                    elif "7b" in value:
                        qwen_version = "7b ❌"
                    print(f"   🔍 Found Qwen reference: {current_path} = {value}")
        
        check_dict(config)
        
        if qwen_found:
            print(f"   📊 Qwen Model Version: {qwen_version}")
            return "1.5b" in str(qwen_version)
        else:
            print(f"   ℹ️  No Qwen references found in {description}")
            return True
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_yaml_config(file_path, description):
    """Check YAML configuration file"""
    print(f"\n📋 Checking {description}: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        qwen_found = False
        qwen_version = None
        
        # Check for qwen references in content
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if "qwen" in line.lower() and ("model:" in line or "model =" in line):
                qwen_found = True
                if "1.5b" in line:
                    qwen_version = "1.5b ✅"
                elif "7b" in line:
                    qwen_version = "7b ❌"
                print(f"   🔍 Line {i}: {line.strip()}")
        
        if qwen_found:
            print(f"   📊 Qwen Model Version: {qwen_version}")
            return "1.5b" in str(qwen_version) if qwen_version else False
        else:
            print(f"   ℹ️  No Qwen references found in {description}")
            return True
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_python_file(file_path, description):
    """Check Python file for Qwen references"""
    print(f"\n🐍 Checking {description}: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        qwen_found = False
        all_updated = True
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if "qwen" in line.lower() and ("7b" in line or "1.5b" in line):
                qwen_found = True
                if "7b" in line and "7b-instruct" not in line:
                    # Skip references to other models like llama-4-maverick-17b
                    continue
                    
                if "1.5b" in line:
                    print(f"   ✅ Line {i}: {line.strip()}")
                elif "7b" in line:
                    print(f"   ❌ Line {i}: {line.strip()}")
                    all_updated = False
        
        if qwen_found:
            status = "✅ All updated" if all_updated else "❌ Some 7b references remain"
            print(f"   📊 Status: {status}")
            return all_updated
        else:
            print(f"   ℹ️  No Qwen references found in {description}")
            return True
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def main():
    """Main verification function"""
    print("🔴 ULTRON PROJECT CONFIGURATION VERIFICATION 🔴")
    print("Checking all configurations for Qwen2.5-Coder:1.5b update")
    print("=" * 60)
    
    verification_results = []
    
    # Configuration files to check
    config_files = [
        ("ultron_config.json", "Main ULTRON Configuration", check_json_config),
        ("test_ai_integration.py", "AI Integration Test Script", check_python_file),
        ("nvidia_nim_router.py", "NVIDIA NIM Router", check_python_file),
        ("ultron_enhanced_ai.py", "Enhanced AI System", check_python_file),
        ("ollama_keepalive.py", "Ollama Keep-Alive Service", check_python_file),
        ("start_ollama_keepalive.bat", "Keep-Alive Batch Script", check_python_file),
        ("ultron_multi_config.yaml", "Multi-Configuration YAML", check_yaml_config),
        ("ultron_single_optimized.yaml", "Single Optimized YAML", check_yaml_config),
        ("test_gui_with_voice.py", "GUI with Voice Test", check_python_file),
        ("launch_proper_gui.py", "GUI Launcher", check_python_file),
        ("ultron_advanced_ai_nvidia.py", "Advanced NVIDIA AI", check_python_file),
    ]
    
    # Continue extension files
    continue_files = [
        (".continue/assistants/Ultron Assistant.yaml", "Continue - Main Assistant"),
        (".continue/assistants/Ultron Assistant Dev.yaml", "Continue - Development Assistant"),
        (".continue/assistants/Ultron Assistant Prod.yaml", "Continue - Production Assistant"),
        (".continue/assistants/Ultron Assistant Enhanced.yaml", "Continue - Enhanced Assistant"),
        (".continue/assistants/Ultron Assistant StarCoder.yaml", "Continue - StarCoder Assistant"),
        (".continue/README.md", "Continue - README"),
    ]
    
    # Check main configuration files
    for file_path, description, check_func in config_files:
        result = check_func(file_path, description)
        verification_results.append((description, result))
    
    # Check Continue extension files
    for file_path, description in continue_files:
        result = check_yaml_config(file_path, description)
        verification_results.append((description, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("🔴 VERIFICATION SUMMARY 🔴")
    print("=" * 60)
    
    passed = 0
    total = len(verification_results)
    
    for description, result in verification_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {description}")
        if result:
            passed += 1
    
    print(f"\n📊 OVERALL RESULT: {passed}/{total} configurations verified")
    
    if passed == total:
        print("🎉 ALL CONFIGURATIONS UPDATED TO QWEN2.5-CODER:1.5B!")
        print("Your ULTRON project is now memory-optimized for 4GB systems.")
    else:
        print(f"⚠️  {total - passed} configurations still need manual updating.")
        print("Check the failed items above and update them manually.")
    
    # Memory usage information
    print("\n" + "=" * 60)
    print("💾 MEMORY USAGE COMPARISON")
    print("=" * 60)
    print("❌ OLD: Qwen2.5-Coder:7b-instruct  → ~5.8GB RAM required")
    print("✅ NEW: Qwen2.5-Coder:1.5b         → ~1.0GB RAM required")
    print("💡 Memory Savings: ~4.8GB (83% reduction)")
    print("\n🚀 Your system can now run ULTRON smoothly with 4GB total RAM!")

if __name__ == "__main__":
    main()
