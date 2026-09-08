#!/usr/bin/env python3
"""
ULTRON Real-Time Audio Setup Script
Sets up everything needed for live audio processing
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ULTRON_ROOT = r"D:\ULTRON"

def install_audio_dependencies():
    """Install critical real-time audio dependencies"""
    print("🎵 Installing real-time audio dependencies...")
    
    critical_packages = [
        "sounddevice",
        "webrtcvad", 
        "numpy",
        "scipy"
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
        return True  # Continue anyway

def test_audio_system():
    """Test if audio system is working"""
    print("\n🔊 Testing audio system...")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        # Test audio devices
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        
        print(f"✅ Found {len(input_devices)} input devices")
        print(f"✅ Found {len(output_devices)} output devices")
        
        if len(input_devices) == 0:
            print("❌ No microphones found!")
            return False
        
        if len(output_devices) == 0:
            print("❌ No speakers found!")
            return False
        
        # Test basic recording
        print("Testing microphone...")
        try:
            sample_rate = 16000
            duration = 0.5  # Half second test
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()
            
            if recording is not None and len(recording) > 0:
                print("✅ Microphone test successful")
            else:
                print("❌ Microphone test failed")
                return False
                
        except Exception as e:
            print(f"❌ Microphone test error: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Audio system import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Audio system error: {e}")
        return False

def create_realtime_config():
    """Create configuration optimized for real-time audio"""
    config_path = os.path.join(ULTRON_ROOT, "config.json")
    
    realtime_config = {
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
            "voice_activity_detection": True,
            "noise_reduction": True
        },
        "ai": {
            "local_mode": True,
            "context_memory": 10,
            "response_speed": "fast",
            "api_key": ""
        },
        "interface": {
            "theme": "realtime",
            "animations": True,
            "audio_visualization": True,
            "live_updates": True
        },
        "system": {
            "auto_screenshot": False,
            "log_conversations": True,
            "backup_frequency": "daily",
            "performance_mode": "realtime"
        },
        "wake_words": [
            "ultron",
            "hello ultron", 
            "hey ultron",
            "speak",
            "ultra"
        ]
    }
    
    with open(config_path, 'w') as f:
        json.dump(realtime_config, f, indent=2)
    
    print(f"✅ Real-time config created: {config_path}")

def create_audio_test_script():
    """Create audio test utility"""
    test_script = """#!/usr/bin/env python3
import sounddevice as sd
import numpy as np
import time

def test_audio():
    print("🔊 ULTRON Audio System Test")
    print("=" * 40)
    
    # List devices
    print("Available audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        marker = "→" if device['name'] == sd.default.device[0] or device['name'] == sd.default.device[1] else " "
        print(f"{marker} {i}: {device['name']} ({device['max_input_channels']} in, {device['max_output_channels']} out)")
    
    print()
    
    # Test recording
    print("Testing microphone (3 seconds)...")
    try:
        sample_rate = 16000
        duration = 3
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        
        print("Recording... Speak now!")
        for i in range(duration):
            print(f"Recording: {i+1}/{duration}")
            time.sleep(1)
        
        sd.wait()
        
        # Check if we got audio
        max_vol = np.max(np.abs(recording))
        if max_vol > 0.01:
            print(f"✅ Audio captured! Max volume: {max_vol:.3f}")
            
            # Play back
            print("Playing back...")
            sd.play(recording, sample_rate)
            sd.wait()
            print("✅ Playback complete")
        else:
            print("❌ No audio detected - check microphone")
            
    except Exception as e:
        print(f"❌ Audio test failed: {e}")

if __name__ == "__main__":
    test_audio()
"""
    
    test_path = os.path.join(ULTRON_ROOT, "test_audio.py")
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    print(f"✅ Audio test script created: {test_path}")

def create_directory_structure():
    """Create ULTRON directory structure"""
    directories = [
        ULTRON_ROOT,
        os.path.join(ULTRON_ROOT, "core"),
        os.path.join(ULTRON_ROOT, "models"),
        os.path.join(ULTRON_ROOT, "assets"),
        os.path.join(ULTRON_ROOT, "logs"),
        os.path.join(ULTRON_ROOT, "web"),
        os.path.join(ULTRON_ROOT, "screenshots"),
        os.path.join(ULTRON_ROOT, "audio_recordings"),
        os.path.join(ULTRON_ROOT, "backups")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def copy_main_files():
    """Copy main files to ULTRON directory"""
    files_to_copy = [
        ("main.py", "main.py"),
        ("requirements.txt", "requirements_realtime.txt")
    ]
    
    for source, dest in files_to_copy:
        if os.path.exists(source):
            dest_path = os.path.join(ULTRON_ROOT, dest)
            shutil.copy2(source, dest_path)
            print(f"✅ Copied {source} → {dest_path}")
        else:
            print(f"⚠️ {source} not found")

def create_startup_scripts():
    """Create startup scripts for real-time ULTRON"""
    
    # Windows batch file
    bat_content = f"""@echo off
title ULTRON Real-Time AI Assistant
echo Starting ULTRON Real-Time Audio System...
cd /d "{ULTRON_ROOT}"
python main.py
pause
"""
    
    bat_path = os.path.join(ULTRON_ROOT, "start_ultron_realtime.bat")
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    
    # Python launcher with audio check
    py_content = f"""#!/usr/bin/env python3
import os
import sys
import subprocess

print("🤖 ULTRON Real-Time Audio System")
print("=" * 40)

# Change to ULTRON directory
os.chdir(r"{ULTRON_ROOT}")
sys.path.insert(0, r"{ULTRON_ROOT}")

# Check audio dependencies
try:
    import sounddevice
    import webrtcvad
    print("✅ Audio dependencies ready")
except ImportError as e:
    print(f"❌ Missing audio dependency: {{e}}")
    print("Run: pip install sounddevice webrtcvad")
    input("Press Enter to continue anyway...")

# Run audio test
try:
    print("\\nTesting audio system...")
    exec(open("test_audio.py").read())
except:
    print("⚠️ Audio test failed - continuing anyway")

# Start ULTRON
print("\\n🚀 Starting ULTRON Real-Time...")
from main import main
main()
"""
    
    py_path = os.path.join(ULTRON_ROOT, "start_ultron_realtime.py")
    with open(py_path, 'w') as f:
        f.write(py_content)
    
    print(f"✅ Created startup scripts:")
    print(f"   - {bat_path}")
    print(f"   - {py_path}")

def main():
    """Main setup function"""
    print("🤖 ULTRON Real-Time Audio Setup")
    print("=" * 50)
    print(f"Setting up real-time ULTRON in: {ULTRON_ROOT}")
    print()
    
    try:
        # Step 1: Create directories
        print("1️⃣ Creating directory structure...")
        create_directory_structure()
        print()
        
        # Step 2: Install audio dependencies
        print("2️⃣ Installing real-time audio dependencies...")
        if not install_audio_dependencies():
            print("❌ Failed to install dependencies - please install manually")
            return
        print()
        
        # Step 3: Test audio system
        print("3️⃣ Testing audio system...")
        if test_audio_system():
            print("✅ Audio system working!")
        else:
            print("⚠️ Audio system issues detected - may need troubleshooting")
        print()
        
        # Step 4: Create real-time config
        print("4️⃣ Creating real-time configuration...")
        create_realtime_config()
        print()
        
        # Step 5: Copy files
        print("5️⃣ Copying main files...")
        copy_main_files()
        print()
        
        # Step 6: Create utilities
        print("6️⃣ Creating audio utilities...")
        create_audio_test_script()
        print()
        
        # Step 7: Create startup scripts
        print("7️⃣ Creating startup scripts...")
        create_startup_scripts()
        print()
        
        print("🎉 ULTRON Real-Time Audio Setup Complete!")
        print()
        print("📋 Quick Start Guide:")
        print(f"  1. Test audio: python {os.path.join(ULTRON_ROOT, 'test_audio.py')}")
        print(f"  2. Start ULTRON: python {os.path.join(ULTRON_ROOT, 'main.py')}")
        print(f"  3. Or use launcher: {os.path.join(ULTRON_ROOT, 'start_ultron_realtime.bat')}")
        print()
        print("🎤 Real-Time Features:")
        print("  • Continuous voice activity detection")
        print("  • Instant speech recognition")
        print("  • Live audio visualization")  
        print("  • Real-time response generation")
        print("  • Voice wake word detection")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
