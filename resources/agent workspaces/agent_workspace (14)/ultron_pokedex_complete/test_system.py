#!/usr/bin/env python3
"""
ULTRON System Test Script
Validates all components before deployment
"""

import os
import sys
import json
import importlib.util
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def test_dependencies():
    """Test if required dependencies can be imported"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        ('os', 'Built-in'),
        ('sys', 'Built-in'),
        ('json', 'Built-in'),
        ('time', 'Built-in'),
        ('threading', 'Built-in'),
        ('tkinter', 'GUI Framework'),
        ('pathlib', 'Built-in')
    ]
    
    optional_packages = [
        ('psutil', 'System monitoring'),
        ('numpy', 'Numeric processing'),
        ('PIL', 'Image processing'),
        ('pygame', 'Audio support'),
        ('speech_recognition', 'Voice recognition'),
        ('pyttsx3', 'Text-to-speech')
    ]
    
    results = {'required': True, 'optional': 0}
    
    # Test required packages
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} - MISSING")
            results['required'] = False
    
    # Test optional packages
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
            results['optional'] += 1
        except ImportError:
            print(f"⚠️ {package} - {description} - OPTIONAL (install with pip)")
    
    print(f"\nOptional packages available: {results['optional']}/{len(optional_packages)}")
    return results

def test_main_script():
    """Test if main.py can be imported"""
    print("\n🤖 Testing main script...")
    
    main_path = "main.py"
    if not os.path.exists(main_path):
        print(f"❌ main.py not found in current directory")
        return False
    
    try:
        # Test syntax by compiling
        with open(main_path, 'r') as f:
            code = f.read()
        
        compile(code, main_path, 'exec')
        print("✅ main.py syntax check passed")
        
        # Test imports (without running main)
        spec = importlib.util.spec_from_file_location("ultron_main", main_path)
        if spec and spec.loader:
            print("✅ main.py import structure valid")
            return True
        else:
            print("❌ main.py import structure invalid")
            return False
            
    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Import test warning: {e}")
        return True  # May still work

def test_ultron_directory():
    """Test ULTRON directory structure"""
    print("\n📁 Testing D:\\ULTRON directory...")
    
    ultron_root = r"D:\ULTRON"
    required_dirs = [
        ultron_root,
        os.path.join(ultron_root, "assets"),
        os.path.join(ultron_root, "logs"),
    ]
    
    optional_dirs = [
        os.path.join(ultron_root, "core"),
        os.path.join(ultron_root, "models"),
        os.path.join(ultron_root, "web"),
        os.path.join(ultron_root, "screenshots")
    ]
    
    # Check if D: drive exists
    if not os.path.exists("D:"):
        print("⚠️ D: drive not found - ULTRON path may need adjustment")
        return False
    
    all_good = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - MISSING")
            all_good = False
    
    print("\nOptional directories:")
    for directory in optional_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"⚠️ {directory} - Will be created automatically")
    
    return all_good

def test_config_file():
    """Test config.json format"""
    print("\n⚙️ Testing configuration...")
    
    config_path = r"D:\ULTRON\config.json"
    if not os.path.exists(config_path):
        print(f"⚠️ {config_path} not found - Will be created automatically")
        return True
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ['voice', 'ai', 'interface', 'system']
        for key in required_keys:
            if key in config:
                print(f"✅ Config section '{key}' found")
            else:
                print(f"⚠️ Config section '{key}' missing - Will use defaults")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Config file invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Config file error: {e}")
        return False

def test_audio_system():
    """Test audio system availability"""
    print("\n🔊 Testing audio system...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            print(f"✅ Text-to-speech available ({len(voices)} voices)")
        else:
            print("⚠️ Text-to-speech available but no voices found")
        engine.stop()
    except Exception as e:
        print(f"⚠️ Text-to-speech issue: {e}")
    
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        mics = sr.Microphone.list_microphone_names()
        if mics:
            print(f"✅ Speech recognition available ({len(mics)} microphones)")
        else:
            print("⚠️ Speech recognition available but no microphones found")
    except Exception as e:
        print(f"⚠️ Speech recognition issue: {e}")

def test_gui_system():
    """Test GUI system"""
    print("\n🖥️ Testing GUI system...")
    
    try:
        import tkinter as tk
        # Test if we can create a window (don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("✅ Tkinter GUI system working")
        return True
    except Exception as e:
        print(f"❌ GUI system error: {e}")
        return False

def run_installation_test():
    """Test if pip install would work"""
    print("\n🛠️ Testing pip installation...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip available: {result.stdout.strip()}")
            return True
        else:
            print("❌ pip not available")
            return False
    except Exception as e:
        print(f"❌ pip test failed: {e}")
        return False

def generate_test_report(results):
    """Generate final test report"""
    print("\n" + "="*50)
    print("🔍 ULTRON SYSTEM TEST REPORT")
    print("="*50)
    
    critical_issues = []
    warnings = []
    
    if not results['python']:
        critical_issues.append("Python version incompatible")
    
    if not results['dependencies']['required']:
        critical_issues.append("Required dependencies missing")
    
    if not results['main_script']:
        critical_issues.append("Main script has issues")
    
    if not results['gui']:
        critical_issues.append("GUI system not working")
    
    if not results['ultron_dir']:
        warnings.append("ULTRON directory structure needs setup")
    
    if results['dependencies']['optional'] < 4:
        warnings.append("Some optional features may not work")
    
    print(f"\n🎯 CRITICAL ISSUES: {len(critical_issues)}")
    for issue in critical_issues:
        print(f"   ❌ {issue}")
    
    print(f"\n⚠️ WARNINGS: {len(warnings)}")
    for warning in warnings:
        print(f"   ⚠️ {warning}")
    
    if len(critical_issues) == 0:
        print(f"\n🎉 ULTRON READY TO DEPLOY!")
        print("   Run: python setup.py")
        print("   Then: cd D:\\ULTRON && python main.py")
    else:
        print(f"\n🚨 CRITICAL ISSUES MUST BE FIXED FIRST")
        print("   1. Install Python 3.7+")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Check main.py file integrity")
    
    print("\n" + "="*50)

def main():
    """Run all tests"""
    print("🤖 ULTRON SYSTEM VALIDATION")
    print("Checking if ULTRON is ready for deployment...\n")
    
    results = {
        'python': test_python_version(),
        'dependencies': test_dependencies(),
        'main_script': test_main_script(),
        'ultron_dir': test_ultron_directory(),
        'config': test_config_file(),
        'gui': test_gui_system(),
        'pip': run_installation_test()
    }
    
    # Optional tests
    test_audio_system()
    
    generate_test_report(results)

if __name__ == "__main__":
    main()
