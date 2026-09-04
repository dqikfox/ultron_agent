#!/usr/bin/env python3
"""
Microphone Diagnostic Tool for ULTRON Agent
Tests different audio input methods and provides fixes
"""

import os
import sys
import subprocess
import json

def test_system_microphone():
    """Test system-level microphone access"""
    print("🎤 Testing System Microphone Access...")
    
    try:
        # Test ALSA (Linux)
        if os.name == 'posix':
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ALSA audio devices found:")
                print(result.stdout)
                return True
            else:
                print("❌ No ALSA audio devices found")
                
        # Test PulseAudio (Linux)
        try:
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ PulseAudio sources found:")
                print(result.stdout)
                return True
        except FileNotFoundError:
            print("⚠️ PulseAudio not available")
            
    except Exception as e:
        print(f"❌ System microphone test failed: {e}")
    
    return False

def test_python_microphone():
    """Test Python speech recognition microphone access"""
    print("\n🐍 Testing Python Microphone Access...")
    
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        # List available microphones
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {index}: {name}")
        
        # Test default microphone
        try:
            with sr.Microphone() as source:
                print("✅ Default microphone accessible")
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("✅ Ambient noise adjustment successful")
                return True
        except Exception as e:
            print(f"❌ Default microphone failed: {e}")
            
            # Try specific device indices
            for device_index in [0, 1, 2]:
                try:
                    with sr.Microphone(device_index=device_index) as source:
                        print(f"✅ Microphone device {device_index} accessible")
                        return True
                except:
                    continue
                    
    except ImportError:
        print("❌ speech_recognition package not installed")
        print("Install with: pip install SpeechRecognition")
    except Exception as e:
        print(f"❌ Python microphone test failed: {e}")
    
    return False

def test_browser_microphone():
    """Test browser microphone permissions"""
    print("\n🌐 Browser Microphone Permissions...")
    
    print("Manual checks needed:")
    print("1. Open Chrome/Firefox")
    print("2. Go to: chrome://settings/content/microphone")
    print("3. Ensure 'Sites can ask to use your microphone' is ON")
    print("4. Check if localhost:8080 is blocked - remove from block list")
    print("5. Add localhost:8080 to allow list if needed")
    
    return True

def generate_fixes():
    """Generate specific fixes based on detected issues"""
    print("\n🔧 Recommended Fixes:")
    
    print("\n**Browser Fixes:**")
    print("1. Chrome: chrome://settings/content/microphone")
    print("2. Firefox: about:preferences#privacy → Microphone")
    print("3. Clear browser data and refresh")
    print("4. Try incognito/private mode")
    
    print("\n**System Fixes (Linux):**")
    print("1. Check audio group membership:")
    print("   groups $USER | grep audio")
    print("2. Add user to audio group:")
    print("   sudo usermod -a -G audio $USER")
    print("3. Restart browser after group change")
    
    print("\n**ULTRON-Specific Fixes:**")
    print("1. Use voice fallback chain:")
    print("   - ElevenLabs API (if configured)")
    print("   - pyttsx3 (offline TTS)")
    print("   - Console input/output")
    print("2. Test with: python3 test_microphone.py")
    
    print("\n**Alternative Input Methods:**")
    print("1. Text-based chat in web GUI")
    print("2. API endpoints for programmatic access")
    print("3. CLI interface: python3 main.py")

def create_browser_test_page():
    """Create a simple HTML page to test browser microphone access"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>ULTRON Microphone Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        button { padding: 10px 20px; margin: 10px; font-size: 16px; }
        #status { margin: 20px 0; padding: 10px; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🎤 ULTRON Microphone Test</h1>
    <button onclick="testMicrophone()">Test Microphone Access</button>
    <button onclick="testRecording()">Test Recording</button>
    <div id="status"></div>
    
    <script>
        function updateStatus(message, isError = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = isError ? 'error' : 'success';
        }
        
        async function testMicrophone() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                updateStatus('✅ Microphone access granted!');
                stream.getTracks().forEach(track => track.stop());
            } catch (error) {
                updateStatus(`❌ Microphone access denied: ${error.message}`, true);
                console.error('Microphone error:', error);
            }
        }
        
        async function testRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                updateStatus('✅ Recording test successful!');
                
                setTimeout(() => {
                    mediaRecorder.stop();
                    stream.getTracks().forEach(track => track.stop());
                }, 1000);
            } catch (error) {
                updateStatus(`❌ Recording test failed: ${error.message}`, true);
            }
        }
    </script>
</body>
</html>"""
    
    with open('/tmp/microphone_test.html', 'w') as f:
        f.write(html_content)
    
    print(f"\n📄 Browser test page created: file:///tmp/microphone_test.html")
    print("Open this file in your browser to test microphone access")

def main():
    print("🚀 ULTRON Microphone Diagnostic Tool")
    print("=" * 50)
    
    system_ok = test_system_microphone()
    python_ok = test_python_microphone()
    browser_ok = test_browser_microphone()
    
    print("\n📊 Summary:")
    print(f"System Microphone: {'✅' if system_ok else '❌'}")
    print(f"Python Access: {'✅' if python_ok else '❌'}")
    print(f"Browser Setup: {'✅' if browser_ok else '❌'}")
    
    generate_fixes()
    create_browser_test_page()
    
    print("\n🎯 Next Steps:")
    print("1. Fix any failed tests above")
    print("2. Open the browser test page")
    print("3. Grant microphone permissions when prompted")
    print("4. Restart ULTRON services: ./run.sh")

if __name__ == "__main__":
    main()