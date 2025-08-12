#!/usr/bin/env python3
"""
Ultron Assistant Setup Script
============================

This script helps set up the Ultron Assistant environment by:
1. Checking Python version compatibility
2. Installing required dependencies
3. Verifying Ollama installation
4. Testing the complete system

Usage:
    python setup_ultron_assistant.py [options]

Options:
    --check-only        Only check system requirements
    --install-deps      Install missing Python dependencies
    --install-ollama    Guide through Ollama installation
    --test-system       Run system tests after setup
"""

import subprocess
import sys
import os
import platform
import urllib.request
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("           ULTRON ASSISTANT SETUP")
    print("=" * 60)
    print()

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    required = (3, 8)
    
    if version[:2] >= required:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (requires {required[0]}.{required[1]}+)")
        print("  Please upgrade Python from https://python.org")
        return False

def check_package_installed(package: str) -> bool:
    """Check if a Python package is installed."""
    try:
        package_name = package.split('>=')[0].split('==')[0].split('[')[0]
        # Handle packages with hyphens
        package_name = package_name.replace('-', '_')
        __import__(package_name)
        return True
    except ImportError:
        return False

def get_required_packages() -> List[str]:
    """Get list of required packages."""
    return [
        'fastapi>=0.110.0',
        'uvicorn[standard]>=0.29.0',
        'python-socketio[asyncio_client]>=5.11.2',
        'python-socketio[asyncio_server]>=5.11.2',
        'pydantic>=2.7.0',
        'httpx>=0.27.0',
        'PySide6>=6.7.0',
        'SpeechRecognition>=3.10.4',
        'pyttsx3>=2.90',
        'pyautogui>=0.9.54',
        'Pillow>=10.3.0',
        'Jinja2>=3.1.2'
    ]

def check_dependencies() -> Tuple[List[str], List[str]]:
    """Check which dependencies are installed/missing."""
    required = get_required_packages()
    installed = []
    missing = []
    
    for package in required:
        if check_package_installed(package):
            installed.append(package)
        else:
            missing.append(package)
    
    return installed, missing

def install_dependencies(packages: List[str]) -> bool:
    """Install missing dependencies."""
    if not packages:
        print("✓ All dependencies already installed")
        return True
    
    print(f"Installing {len(packages)} missing packages...")
    print("Packages:", ', '.join([p.split('>=')[0] for p in packages]))
    print()
    
    # Special handling for system-specific packages
    if platform.system() == "Windows":
        print("Note: On Windows, some packages may require additional setup:")
        if any('pyaudio' in pkg.lower() for pkg in packages):
            print("  - pyaudio: May need pre-built wheel from")
            print("    https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        if any('pyside6' in pkg.lower() for pkg in packages):
            print("  - PySide6: May require Visual C++ Redistributable")
    
    try:
        # Use pip to install packages
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade'] + packages
        print(f"Running: {' '.join(cmd[:4])} [packages...]")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print("✗ Installation failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Installation error: {e}")
        return False

def check_ollama() -> Dict[str, any]:
    """Check Ollama installation and status."""
    status = {
        "installed": False,
        "running": False,
        "models": [],
        "version": None,
        "error": None
    }
    
    try:
        # Check if ollama command exists
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            status["installed"] = True
            status["version"] = result.stdout.strip()
        
    except (FileNotFoundError, subprocess.TimeoutExpired):
        status["error"] = "Ollama command not found"
        return status
    
    if status["installed"]:
        try:
            # Check if Ollama server is running
            import httpx
            response = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5)
            if response.status_code == 200:
                status["running"] = True
                data = response.json()
                status["models"] = [model["name"] for model in data.get("models", [])]
        except Exception as e:
            status["error"] = f"Server check failed: {e}"
    
    return status

def install_ollama_guide():
    """Provide Ollama installation guidance."""
    print("\n" + "=" * 40)
    print("        OLLAMA INSTALLATION GUIDE")
    print("=" * 40)
    
    system = platform.system()
    
    if system == "Windows":
        print("For Windows:")
        print("1. Download Ollama from: https://ollama.ai/download")
        print("2. Run the installer (.exe file)")
        print("3. Restart your terminal/command prompt")
        print("4. Verify installation: ollama --version")
        
    elif system == "Darwin":  # macOS
        print("For macOS:")
        print("1. Download Ollama from: https://ollama.ai/download")
        print("2. Drag to Applications folder")
        print("3. Or use Homebrew: brew install ollama")
        
    else:  # Linux
        print("For Linux:")
        print("1. Run: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Or download from: https://ollama.ai/download")
    
    print("\nAfter installation:")
    print("1. Start Ollama: ollama serve")
    print("2. Pull a model: ollama pull llama3.2")
    print("3. Test: ollama run llama3.2")
    print()

def test_system() -> bool:
    """Test the complete system."""
    print("\n" + "=" * 40)
    print("         SYSTEM TESTING")
    print("=" * 40)
    
    all_good = True
    
    # Test Python imports
    print("Testing Python imports...")
    try:
        import fastapi
        import uvicorn
        import socketio
        import httpx
        print("✓ Core web frameworks")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        all_good = False
    
    try:
        import speech_recognition
        import pyttsx3
        print("✓ Voice processing libraries")
    except ImportError as e:
        print(f"✗ Voice libraries missing: {e}")
        print("  (Voice features will be disabled)")
    
    try:
        import pyautogui
        print("✓ Automation library")
    except ImportError:
        print("✗ pyautogui missing (automation disabled)")
    
    # Test Ollama connection
    print("\nTesting Ollama connection...")
    ollama_status = check_ollama()
    if ollama_status["running"]:
        print(f"✓ Ollama running with {len(ollama_status['models'])} models")
    else:
        print("✗ Ollama not running")
        print("  Start with: ollama serve")
        all_good = False
    
    # Test file structure
    print("\nChecking file structure...")
    script_dir = Path(__file__).parent
    required_files = [
        "app.py",
        "ollama_client.py", 
        "automation.py",
        "voice.py",
        "static/css/ultron.css",
        "static/js/chat.js",
        "templates/index.html"
    ]
    
    for file_path in required_files:
        full_path = script_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("✓ ALL TESTS PASSED - Ready to launch!")
    else:
        print("✗ Some tests failed - Check errors above")
    print("=" * 40)
    
    return all_good

def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultron Assistant Setup")
    parser.add_argument("--check-only", action="store_true", 
                       help="Only check requirements")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install missing dependencies")
    parser.add_argument("--install-ollama", action="store_true",
                       help="Show Ollama installation guide")
    parser.add_argument("--test-system", action="store_true",
                       help="Run system tests")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\nChecking Python dependencies...")
    installed, missing = check_dependencies()
    print(f"✓ {len(installed)} packages installed")
    
    if missing:
        print(f"⚠ {len(missing)} packages missing:")
        for pkg in missing:
            print(f"  - {pkg}")
        
        if args.install_deps:
            if not install_dependencies(missing):
                sys.exit(1)
        elif not args.check_only:
            print("\nRun with --install-deps to install missing packages")
    else:
        print("✓ All Python dependencies installed")
    
    # Check Ollama
    print("\nChecking Ollama...")
    ollama_status = check_ollama()
    
    if not ollama_status["installed"]:
        print("✗ Ollama not installed")
        if args.install_ollama:
            install_ollama_guide()
        else:
            print("Run with --install-ollama for installation guide")
            if not args.check_only:
                sys.exit(1)
    else:
        print(f"✓ Ollama installed ({ollama_status['version']})")
        
        if ollama_status["running"]:
            print(f"✓ Ollama running with {len(ollama_status['models'])} models")
            if not ollama_status["models"]:
                print("⚠ No models available. Run: ollama pull llama3.2")
        else:
            print("⚠ Ollama not running. Start with: ollama serve")
    
    # Run tests if requested
    if args.test_system:
        if not test_system():
            sys.exit(1)
    
    # Final summary
    if not args.check_only and not args.install_ollama:
        print("\n" + "=" * 60)
        print("Setup complete! To start Ultron Assistant:")
        print("  python run_ultron_assistant.py")
        print("\nOr use the batch file on Windows:")
        print("  run_ultron.bat")
        print("=" * 60)

if __name__ == "__main__":
    main()
