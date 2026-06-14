#!/usr/bin/env python3
"""
ULTRON Complete AI Agent Setup Script
Sets up full PC control capabilities including automation, file management, and system control
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ULTRON_ROOT = r"D:\ULTRON"

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_automation_dependencies():
    """Install critical automation dependencies"""
    print("🤖 Installing AI agent automation dependencies...")
    
    critical_packages = [
        "pyautogui",     # GUI automation
        "pyperclip",     # Clipboard access
        "sounddevice",   # Real-time audio
        "webrtcvad",     # Voice activity detection
        "speechrecognition",  # Speech to text
        "pyttsx3",       # Text to speech
        "psutil",        # System monitoring
        "pillow",        # Image processing
        "numpy"          # Numeric processing
    ]
    
    for package in critical_packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    # Install all requirements
    try:
        print("Installing full requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Some optional dependencies may have failed")
        return True

def test_automation_capabilities():
    """Test if automation capabilities are working"""
    print("\n🔧 Testing automation capabilities...")
    
    try:
        # Test PyAutoGUI
        import pyautogui
        screen_size = pyautogui.size()
        print(f"✅ Screen automation ready - Screen size: {screen_size}")
        
        # Test clipboard
        import pyperclip
        pyperclip.copy("ULTRON test")
        clipboard_content = pyperclip.paste()
        if clipboard_content == "ULTRON test":
            print("✅ Clipboard access working")
        else:
            print("⚠️ Clipboard access issue")
        
        # Test file operations
        import pathlib
        test_file = pathlib.Path(ULTRON_ROOT) / "test_agent.txt"
        test_file.write_text("ULTRON agent test")
        if test_file.exists():
            print("✅ File operations working")
            test_file.unlink()  # Clean up
        else:
            print("❌ File operations failed")
        
        # Test system monitoring
        import psutil
        cpu_percent = psutil.cpu_percent()
        print(f"✅ System monitoring working - CPU: {cpu_percent}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Automation test failed: {e}")
        return False

def create_agent_config():
    """Create configuration optimized for AI agent operations"""
    config_path = os.path.join(ULTRON_ROOT, "config.json")
    
    agent_config = {
        "voice": {
            "enabled": True,
            "rate": 180,
            "volume": 0.9
        },
        "audio": {
            "real_time": True,
            "sample_rate": 16000,
            "chunk_duration_ms": 30,
            "sensitivity": 0.5,
            "auto_respond": True,
            "voice_activity_detection": True
        },
        "automation": {
            "enabled": True,
            "safe_mode": True,
            "confirm_destructive_actions": True,
            "screenshot_on_action": False,
            "action_delay": 0.1,
            "failsafe": True
        },
        "ai": {
            "local_mode": True,
            "context_memory": 15,
            "response_speed": "fast",
            "api_key": "",
            "advanced_commands": True
        },
        "interface": {
            "theme": "agent",
            "animations": True,
            "audio_visualization": True,
            "live_updates": True,
            "show_advanced_controls": True
        },
        "system": {
            "auto_screenshot": False,
            "log_conversations": True,
            "log_actions": True,
            "backup_frequency": "daily",
            "performance_mode": "agent"
        },
        "file_operations": {
            "default_directory": ULTRON_ROOT,
            "auto_backup": True,
            "confirm_delete": True,
            "show_hidden_files": False
        },
        "wake_words": [
            "ultron",
            "hello ultron", 
            "hey ultron",
            "speak",
            "ultra",
            "computer"
        ],
        "keyboard_shortcuts": {
            "emergency_stop": "ctrl+shift+q",
            "toggle_listening": "ctrl+shift+l",
            "quick_screenshot": "ctrl+shift+s"
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    print(f"✅ AI agent config created: {config_path}")

def create_agent_directories():
    """Create directory structure for AI agent"""
    directories = [
        ULTRON_ROOT,
        os.path.join(ULTRON_ROOT, "core"),
        os.path.join(ULTRON_ROOT, "models"),
        os.path.join(ULTRON_ROOT, "assets"),
        os.path.join(ULTRON_ROOT, "logs"),
        os.path.join(ULTRON_ROOT, "web"),
        os.path.join(ULTRON_ROOT, "screenshots"),
        os.path.join(ULTRON_ROOT, "audio_recordings"),
        os.path.join(ULTRON_ROOT, "scripts"),
        os.path.join(ULTRON_ROOT, "automations"),
        os.path.join(ULTRON_ROOT, "managed_files"),
        os.path.join(ULTRON_ROOT, "backups"),
        os.path.join(ULTRON_ROOT, "temp")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_automation_scripts():
    """Create sample automation scripts"""
    scripts_dir = os.path.join(ULTRON_ROOT, "scripts")
    
    # Sample automation script
    automation_script = '''#!/usr/bin/env python3
"""
Sample ULTRON Automation Script
Demonstrates how to create custom automation tasks
"""

import pyautogui
import time
import pyperclip

def open_notepad_and_type():
    """Open Notepad and type a message"""
    # Open Run dialog
    pyautogui.hotkey('win', 'r')
    time.sleep(0.5)
    
    # Type notepad
    pyautogui.write('notepad')
    pyautogui.press('enter')
    time.sleep(1)
    
    # Type message
    message = "Hello from ULTRON AI Agent!"
    pyautogui.write(message)
    
    return f"Opened Notepad and typed: {message}"

def take_screenshot_and_save():
    """Take a screenshot and save it"""
    screenshot = pyautogui.screenshot()
    filename = f"ultron_screenshot_{int(time.time())}.png"
    screenshot.save(filename)
    return f"Screenshot saved as: {filename}"

def copy_system_info():
    """Copy system information to clipboard"""
    import platform
    import psutil
    
    info = f"""
ULTRON System Information:
OS: {platform.system()} {platform.release()}
Processor: {platform.processor()}
Architecture: {platform.architecture()[0]}
CPU Usage: {psutil.cpu_percent()}%
Memory Usage: {psutil.virtual_memory().percent}%
Disk Usage: {psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent}%
"""
    
    pyperclip.copy(info)
    return "System information copied to clipboard"

if __name__ == "__main__":
    print("ULTRON Automation Script")
    print("Available functions:")
    print("1. open_notepad_and_type()")
    print("2. take_screenshot_and_save()")
    print("3. copy_system_info()")
'''
    
    script_path = os.path.join(scripts_dir, "sample_automation.py")
    with open(script_path, 'w') as f:
        f.write(automation_script)
    
    print(f"✅ Sample automation script created: {script_path}")

def create_agent_test_script():
    """Create comprehensive agent test script"""
    test_script = '''#!/usr/bin/env python3
"""
ULTRON Complete AI Agent Test
Tests all automation and control capabilities
"""

import os
import sys
import time
import tempfile
from pathlib import Path

def test_all_capabilities():
    print("🤖 ULTRON Complete AI Agent Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: PyAutoGUI
    print("1️⃣ Testing GUI automation...")
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        screen_size = pyautogui.size()
        mouse_pos = pyautogui.position()
        print(f"   Screen: {screen_size}, Mouse: {mouse_pos}")
        results.append(("GUI Automation", True))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("GUI Automation", False))
    
    # Test 2: Clipboard
    print("2️⃣ Testing clipboard access...")
    try:
        import pyperclip
        test_text = "ULTRON clipboard test"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        if result == test_text:
            print("   Clipboard working")
            results.append(("Clipboard", True))
        else:
            print("   Clipboard not working properly")
            results.append(("Clipboard", False))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Clipboard", False))
    
    # Test 3: File operations
    print("3️⃣ Testing file operations...")
    try:
        test_dir = Path.home() / "ultron_test"
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / "test.txt"
        test_file.write_text("ULTRON file test")
        
        if test_file.exists() and test_file.read_text() == "ULTRON file test":
            print("   File operations working")
            results.append(("File Operations", True))
            # Cleanup
            test_file.unlink()
            test_dir.rmdir()
        else:
            print("   File operations failed")
            results.append(("File Operations", False))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("File Operations", False))
    
    # Test 4: System monitoring
    print("4️⃣ Testing system monitoring...")
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        print(f"   CPU: {cpu}%, Memory: {memory}%")
        results.append(("System Monitoring", True))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("System Monitoring", False))
    
    # Test 5: Audio system
    print("5️⃣ Testing audio system...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = len([d for d in devices if d['max_input_channels'] > 0])
        output_devices = len([d for d in devices if d['max_output_channels'] > 0])
        print(f"   Input devices: {input_devices}, Output devices: {output_devices}")
        if input_devices > 0 and output_devices > 0:
            results.append(("Audio System", True))
        else:
            results.append(("Audio System", False))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Audio System", False))
    
    # Test 6: Speech recognition
    print("6️⃣ Testing speech recognition...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        print("   Speech recognition library loaded")
        results.append(("Speech Recognition", True))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Speech Recognition", False))
    
    # Test 7: Text-to-speech
    print("7️⃣ Testing text-to-speech...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"   Text-to-speech ready ({len(voices)} voices)")
        results.append(("Text-to-Speech", True))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Text-to-Speech", False))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\\n🎉 ALL TESTS PASSED!")
        print("🤖 ULTRON Complete AI Agent is ready!")
        print("\\nCapabilities available:")
        print("  • Real-time voice control")
        print("  • GUI automation (keyboard/mouse)")
        print("  • File and folder management")
        print("  • Application launching")
        print("  • System monitoring")
        print("  • Clipboard operations")
        print("  • Screenshot capture")
        print("  • Text typing automation")
    else:
        print(f"\\n⚠️ {total - passed} tests failed")
        print("Some AI agent features may not work properly.")
        print("Check the error messages above for troubleshooting.")

if __name__ == "__main__":
    test_all_capabilities()
'''
    
    test_path = os.path.join(ULTRON_ROOT, "test_agent_capabilities.py")
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    print(f"✅ Agent test script created: {test_path}")

def copy_main_files():
    """Copy main files to ULTRON directory"""
    files_to_copy = [
        ("main.py", "main.py"),
        ("requirements.txt", "requirements_agent.txt")
    ]
    
    for source, dest in files_to_copy:
        if os.path.exists(source):
            dest_path = os.path.join(ULTRON_ROOT, dest)
            shutil.copy2(source, dest_path)
            print(f"✅ Copied {source} → {dest_path}")
        else:
            print(f"⚠️ {source} not found")

def create_startup_scripts():
    """Create startup scripts for complete AI agent"""
    
    # Windows batch file
    bat_content = f'''@echo off
title ULTRON Complete AI Agent
echo Starting ULTRON Complete AI Agent...
echo.
echo Capabilities:
echo  - Real-time voice control
echo  - GUI automation (keyboard/mouse)
echo  - File and application management
echo  - System monitoring and control
echo.
cd /d "{ULTRON_ROOT}"
python main.py
pause
'''
    
    bat_path = os.path.join(ULTRON_ROOT, "start_ultron_agent.bat")
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    
    # Python launcher with capability check
    py_content = f'''#!/usr/bin/env python3
import os
import sys
import subprocess

print("🤖 ULTRON Complete AI Agent")
print("=" * 50)

# Change to ULTRON directory
os.chdir(r"{ULTRON_ROOT}")
sys.path.insert(0, r"{ULTRON_ROOT}")

# Check critical dependencies
missing_deps = []
try:
    import pyautogui
    print("✅ GUI automation ready")
except ImportError:
    missing_deps.append("pyautogui")
    print("❌ Missing: pyautogui")

try:
    import pyperclip
    print("✅ Clipboard access ready")
except ImportError:
    missing_deps.append("pyperclip")
    print("❌ Missing: pyperclip")

try:
    import sounddevice
    import webrtcvad
    print("✅ Audio processing ready")
except ImportError:
    missing_deps.append("sounddevice webrtcvad")
    print("❌ Missing: audio dependencies")

if missing_deps:
    print(f"\\n⚠️ Missing dependencies: {{' '.join(missing_deps)}}")
    print("Run: pip install " + " ".join(missing_deps))
    input("Press Enter to continue anyway...")

# Run capability test
try:
    print("\\n🔧 Running capability test...")
    exec(open("test_agent_capabilities.py").read())
except:
    print("⚠️ Capability test failed - continuing anyway")

# Start ULTRON
print("\\n🚀 Starting ULTRON Complete AI Agent...")
from main import main
main()
'''
    
    py_path = os.path.join(ULTRON_ROOT, "start_ultron_agent.py")
    with open(py_path, 'w') as f:
        f.write(py_content)
    
    print(f"✅ Created startup scripts:")
    print(f"   - {bat_path}")
    print(f"   - {py_path}")

def main():
    """Main setup function"""
    print("🤖 ULTRON Complete AI Agent Setup")
    print("=" * 60)
    print(f"Setting up complete AI agent in: {ULTRON_ROOT}")
    print()
    
    # Check admin privileges
    if check_admin_privileges():
        print("✅ Running with administrator privileges")
    else:
        print("⚠️ Not running as administrator - some features may be limited")
    
    try:
        # Step 1: Create directories
        print("1️⃣ Creating AI agent directory structure...")
        create_agent_directories()
        print()
        
        # Step 2: Install dependencies
        print("2️⃣ Installing AI agent dependencies...")
        if not install_automation_dependencies():
            print("❌ Failed to install dependencies - please install manually")
            return
        print()
        
        # Step 3: Test automation
        print("3️⃣ Testing automation capabilities...")
        if test_automation_capabilities():
            print("✅ Automation capabilities working!")
        else:
            print("⚠️ Some automation features may not work")
        print()
        
        # Step 4: Create config
        print("4️⃣ Creating AI agent configuration...")
        create_agent_config()
        print()
        
        # Step 5: Copy files
        print("5️⃣ Copying main files...")
        copy_main_files()
        print()
        
        # Step 6: Create automation scripts
        print("6️⃣ Creating automation scripts...")
        create_automation_scripts()
        print()
        
        # Step 7: Create test script
        print("7️⃣ Creating capability test script...")
        create_agent_test_script()
        print()
        
        # Step 8: Create startup scripts
        print("8️⃣ Creating startup scripts...")
        create_startup_scripts()
        print()
        
        print("🎉 ULTRON Complete AI Agent Setup Complete!")
        print()
        print("🤖 AI Agent Capabilities:")
        print("  ✅ Real-time voice control with wake words")
        print("  ✅ GUI automation (keyboard & mouse control)")
        print("  ✅ File and folder management (create, edit, delete)")
        print("  ✅ Application launching and control")
        print("  ✅ System monitoring and screenshots")
        print("  ✅ Clipboard operations and text automation")
        print("  ✅ Advanced system commands")
        print()
        print("📋 Quick Start:")
        print(f"  1. Test capabilities: python {os.path.join(ULTRON_ROOT, 'test_agent_capabilities.py')}")
        print(f"  2. Start AI agent: python {os.path.join(ULTRON_ROOT, 'main.py')}")
        print(f"  3. Or use launcher: {os.path.join(ULTRON_ROOT, 'start_ultron_agent.bat')}")
        print()
        print("🗣️ Voice Commands:")
        print('  "Hey ULTRON, open notepad"')
        print('  "ULTRON, create file test.txt"')
        print('  "Hello ULTRON, type hello world"')
        print('  "ULTRON, take screenshot"')
        print('  "Hey ULTRON, press enter"')
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
