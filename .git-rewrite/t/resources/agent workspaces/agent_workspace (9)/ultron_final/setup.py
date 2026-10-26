#!/usr/bin/env python3
"""
ULTRON Setup Script
Installs dependencies and prepares the system
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a system command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check operating system
    os_name = platform.system()
    print(f"✅ Operating System: {os_name}")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "logs",
        "screenshots",
        "managed_files",
        "managed_files/documents",
        "managed_files/images",
        "managed_files/videos",
        "managed_files/audio",
        "managed_files/archives",
        "managed_files/code",
        "managed_files/executables",
        "managed_files/other",
        "managed_files/backup"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")
            return False
    
    return True

def check_optional_dependencies():
    """Check optional system dependencies"""
    print("🔍 Checking optional dependencies...")
    
    # Check Tesseract OCR
    if run_command("tesseract --version", "Checking Tesseract OCR"):
        print("✅ Tesseract OCR is available")
    else:
        print("⚠️ Tesseract OCR not found - Vision system will be limited")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux: sudo apt-get install tesseract-ocr")
        print("   macOS: brew install tesseract")
    
    return True

def display_installation_info():
    """Display post-installation information"""
    print("\n" + "=" * 60)
    print("🎉 ULTRON Setup Complete!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("1. Edit config.json to add your OpenAI API key (optional)")
    print("2. Run tests: python test_ultron.py")
    print("3. Start ULTRON:")
    print("   - GUI Mode: python main.py --mode gui")
    print("   - Console Mode: python main.py --mode console")
    print("   - Async Mode: python main.py --mode async")
    
    print("\n🔧 Configuration:")
    print("- Edit config.json for custom settings")
    print("- Logs will be saved in the 'logs' directory")
    print("- Screenshots will be saved in 'screenshots' directory")
    print("- Sorted files will be organized in 'managed_files' directory")
    
    print("\n🌐 Web Interface:")
    print("- Access at http://localhost:3000 when running")
    print("- REST API available for integration")
    
    print("\n⚠️ Important Notes:")
    print("- Some features require admin privileges")
    print("- Voice recognition needs a microphone")
    print("- OCR requires Tesseract installation")
    print("- AI features need OpenAI API key")

def main():
    """Main setup function"""
    print("🔴 ULTRON AI Assistant Setup")
    print("=" * 40)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met")
        return 1
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        return 1
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        return 1
    
    # Check optional dependencies
    check_optional_dependencies()
    
    # Display installation info
    display_installation_info()
    
    print(f"\n✅ Setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
