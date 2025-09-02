#!/usr/bin/env python3
"""
ULTRON Enhanced - Easy Launcher
===============================

Simple launcher with system checks and diagnostics.
This provides an easy way to start ULTRON with comprehensive checks.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def print_banner():
    """Display startup banner."""
    print("=" * 60)
    print("   🤖 ULTRON Enhanced v3.0 - Launcher 🤖")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version compatibility."""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  ULTRON Enhanced requires Python 3.8 or higher")
        print("   Please upgrade your Python installation")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_dependencies():
    """Check and install required dependencies."""
    print("📦 Checking dependencies...")
    
    # Core dependencies
    required_packages = [
        'flask', 'flask-socketio', 'eventlet',
        'psutil', 'opencv-python', 'pillow',
        'pyautogui', 'requests', 'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').split('.')[0])
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n📥 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade'
            ] + missing)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    print("✅ All dependencies satisfied")
    return True

def check_system_permissions():
    """Check system permissions and capabilities."""
    print("🔐 Checking system permissions...")
    
    # Check write permissions
    try:
        test_file = Path("test_write.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Write permissions")
    except Exception:
        print("   ⚠️  Limited write permissions")
    
    # Check if we can import GUI libraries
    try:
        import tkinter
        print("   ✅ GUI capabilities available")
    except ImportError:
        print("   ⚠️  GUI not available (headless mode)")
    
    # Check system info
    print(f"   ℹ️  OS: {platform.system()} {platform.release()}")
    print(f"   ℹ️  Architecture: {platform.machine()}")
    
    return True

def setup_directories():
    """Create necessary directories."""
    print("📁 Setting up directories...")
    
    directories = [
        'logs', 'screenshots', 'models', 'temp',
        'web/assets', 'core'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True

def check_configuration():
    """Check configuration files."""
    print("⚙️  Checking configuration...")
    
    config_file = Path("ultron_config.json")
    example_config = Path("ultron_config.json.example")
    
    if not config_file.exists():
        if example_config.exists():
            print("   📋 Copying example configuration...")
            shutil.copy(example_config, config_file)
        else:
            print("   ⚠️  Creating basic configuration...")
            basic_config = {
                "ai": {
                    "primary_model": "ollama:qwen2.5-coder",
                    "fallback_models": ["openai:gpt-4"],
                    "openai_api_key": ""
                },
                "voice": {
                    "tts_engine": "pyttsx3",
                    "tts_rate": 150,
                    "wake_word": "ultron"
                },
                "automation": {
                    "safety_enabled": True,
                    "confirmation_required": True
                },
                "web": {
                    "host": "localhost",
                    "port": 8080
                }
            }
            config_file.write_text(json.dumps(basic_config, indent=2))
    
    print("   ✅ Configuration ready")
    return True

def check_optional_services():
    """Check optional services like Ollama."""
    print("🔌 Checking optional services...")
    
    # Check for Ollama
    if shutil.which("ollama"):
        print("   ✅ Ollama available")
        
        # Try to start Ollama if not running
        try:
            subprocess.run(['ollama', 'list'], 
                         capture_output=True, timeout=5)
            print("   ✅ Ollama server running")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            print("   ⚠️  Ollama server not responding")
    else:
        print("   ⚠️  Ollama not found (local AI unavailable)")
    
    return True

def run_diagnostics():
    """Run comprehensive system diagnostics."""
    print("🔧 Running diagnostics...")
    
    try:
        # Test core imports
        core_modules = [
            'agent_core', 'brain', 'voice_manager', 
            'config', 'memory'
        ]
        
        for module in core_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError as e:
                print(f"   ⚠️  {module}: {e}")
        
        print("✅ Diagnostics complete")
        return True
        
    except Exception as e:
        print(f"❌ Diagnostics failed: {e}")
        return False

def launch_ultron(mode='auto'):
    """Launch ULTRON Enhanced."""
    print(f"🚀 Launching ULTRON Enhanced ({mode} mode)...")
    print()
    
    # Import and start main application
    try:
        from agent_core import UltronAgent
        
        print("🤖 Initializing ULTRON Agent...")
        agent = UltronAgent()
        
        if mode == 'web':
            print("🌐 Starting in Web mode...")
            print("   Access: http://localhost:8080")
            from core.web_server import UltronWebServer
            server = UltronWebServer(agent_ref=agent)
            server.start_server()
            server.wait_for_shutdown()
            
        elif mode == 'cli':
            print("💻 Starting in CLI mode...")
            agent.start()
            
        else:
            print("🖥️  Starting in Auto mode...")
            if hasattr(agent, 'start_gui'):
                agent.start_gui()
            else:
                agent.start()
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import ULTRON components: {e}")
        return False
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main launcher function."""
    print_banner()
    
    # Parse command line arguments
    mode = 'auto'
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--web', '--cli', '--gui']:
            mode = arg[2:]  # Remove --
    
    print(f"🎯 Launch Mode: {mode.upper()}")
    print()
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("System Permissions", check_system_permissions),
        ("Directory Setup", setup_directories),
        ("Configuration", check_configuration),
        ("Optional Services", check_optional_services),
        ("System Diagnostics", run_diagnostics)
    ]
    
    failed_checks = []
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            failed_checks.append(check_name)
        print()
    
    # Summary
    if failed_checks:
        print("⚠️  Some checks failed:")
        for check in failed_checks:
            print(f"   - {check}")
        print()
        
        response = input("Continue anyway? [y/N]: ").lower()
        if response not in ['y', 'yes']:
            print("Exiting...")
            return 1
    
    print("✅ All systems ready!")
    print()
    print("=" * 60)
    print("   🤖 ULTRON Enhanced - Starting... 🤖")
    print("=" * 60)
    print()
    
    # Launch application
    success = launch_ultron(mode)
    
    if success:
        print()
        print("✅ ULTRON Enhanced shut down normally")
        return 0
    else:
        print()
        print("❌ ULTRON Enhanced encountered errors")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)