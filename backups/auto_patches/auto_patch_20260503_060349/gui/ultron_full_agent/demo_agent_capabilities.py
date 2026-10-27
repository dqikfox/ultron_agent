#!/usr/bin/env python3
"""
ULTRON AI Agent Capabilities Demo
Demonstrates the full PC control capabilities
"""

import os
import sys
import time
import tempfile
from pathlib import Path

def demo_introduction():
    """Introduction to ULTRON AI Agent"""
    print("🤖 ULTRON AI Agent Capabilities Demo")
    print("=" * 50)
    print("This demo shows what ULTRON can do on your PC:")
    print("✅ Open applications")
    print("✅ Create and manage files") 
    print("✅ Control keyboard and mouse")
    print("✅ Take screenshots")
    print("✅ Monitor system")
    print("✅ Respond to voice commands")
    print()
    input("Press Enter to start demo...")

def demo_file_operations():
    """Demonstrate file operations"""
    print("\n📁 DEMO: File Operations")
    print("-" * 30)
    
    try:
        # Create a demo directory
        demo_dir = Path.home() / "ULTRON_Demo"
        demo_dir.mkdir(exist_ok=True)
        print(f"✅ Created directory: {demo_dir}")
        
        # Create files
        files_to_create = [
            ("demo.txt", "Hello from ULTRON AI Agent!"),
            ("system_info.txt", f"Demo created at: {time.strftime('%Y-%m-%d %H:%M:%S')}"),
            ("commands.txt", "Voice commands:\n- Hey ULTRON, open notepad\n- ULTRON, create file\n- Take screenshot")
        ]
        
        for filename, content in files_to_create:
            file_path = demo_dir / filename
            file_path.write_text(content)
            print(f"✅ Created file: {filename}")
        
        # List files
        files = list(demo_dir.glob("*"))
        print(f"✅ Files in demo directory: {len(files)}")
        for file_path in files:
            print(f"   📄 {file_path.name}")
        
        # Read a file
        demo_file = demo_dir / "demo.txt"
        content = demo_file.read_text()
        print(f"✅ Read file content: '{content}'")
        
        print("✅ File operations demo complete!")
        
    except Exception as e:
        print(f"❌ File operations demo failed: {e}")

def demo_system_monitoring():
    """Demonstrate system monitoring"""
    print("\n💻 DEMO: System Monitoring")
    print("-" * 30)
    
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"✅ CPU Usage: {cpu_percent}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        print(f"✅ Memory Usage: {memory.percent}% ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)")
        
        # Disk usage
        disk = psutil.disk_usage('/')
        print(f"✅ Disk Usage: {disk.percent}% ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)")
        
        # Running processes (top 5)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        print("✅ Top 5 processes by CPU usage:")
        for proc in processes[:5]:
            print(f"   🔹 {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%")
        
        print("✅ System monitoring demo complete!")
        
    except Exception as e:
        print(f"❌ System monitoring demo failed: {e}")

def demo_automation_capabilities():
    """Demonstrate automation capabilities (simulation)"""
    print("\n🤖 DEMO: Automation Capabilities")
    print("-" * 30)
    
    try:
        # Import automation libraries
        import pyautogui
        import pyperclip
        
        # Screen size and mouse position
        screen_size = pyautogui.size()
        mouse_pos = pyautogui.position()
        print(f"✅ Screen size: {screen_size}")
        print(f"✅ Current mouse position: {mouse_pos}")
        
        # Clipboard operations
        original_clipboard = pyperclip.paste()
        test_text = "ULTRON AI Agent clipboard test"
        pyperclip.copy(test_text)
        copied_text = pyperclip.paste()
        
        if copied_text == test_text:
            print(f"✅ Clipboard test successful: '{copied_text}'")
        else:
            print("❌ Clipboard test failed")
        
        # Restore original clipboard
        pyperclip.copy(original_clipboard)
        
        # Demonstrate text typing (simulated)
        print("✅ Text typing capabilities ready")
        print("   - Can type any text automatically")
        print("   - Can press any key combination")
        print("   - Can execute keyboard shortcuts")
        
        # Demonstrate mouse control (simulated)
        print("✅ Mouse control capabilities ready")
        print("   - Can click at any position")
        print("   - Can drag and drop")
        print("   - Can get mouse coordinates")
        
        print("✅ Automation capabilities demo complete!")
        
    except Exception as e:
        print(f"❌ Automation demo failed: {e}")

def demo_voice_commands():
    """Demonstrate voice command capabilities"""
    print("\n🎤 DEMO: Voice Command Capabilities")
    print("-" * 30)
    
    try:
        import speech_recognition as sr
        import pyttsx3
        
        # Speech recognition
        recognizer = sr.Recognizer()
        print("✅ Speech recognition engine loaded")
        
        # Text-to-speech
        tts_engine = pyttsx3.init()
        voices = tts_engine.getProperty('voices')
        print(f"✅ Text-to-speech engine loaded ({len(voices)} voices available)")
        
        # Real-time audio
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            output_devices = [d for d in devices if d['max_output_channels'] > 0]
            print(f"✅ Audio devices: {len(input_devices)} input, {len(output_devices)} output")
        except:
            print("⚠️ Real-time audio not available")
        
        # Voice activity detection
        try:
            import webrtcvad
            vad = webrtcvad.Vad()
            print("✅ Voice activity detection ready")
        except:
            print("⚠️ Voice activity detection not available")
        
        print("✅ Voice command system ready!")
        print("\nSupported wake words:")
        print("   🗣️ 'Hey ULTRON'")
        print("   🗣️ 'Hello ULTRON'")
        print("   🗣️ 'ULTRON'")
        print("   🗣️ 'Computer'")
        
        print("\nExample voice commands:")
        print("   🎤 'Hey ULTRON, open notepad'")
        print("   🎤 'ULTRON, create file test.txt'")
        print("   🎤 'Take a screenshot'")
        print("   🎤 'Type hello world'")
        print("   🎤 'Press enter'")
        
        print("✅ Voice command demo complete!")
        
    except Exception as e:
        print(f"❌ Voice command demo failed: {e}")

def demo_application_control():
    """Demonstrate application control capabilities"""
    print("\n🚀 DEMO: Application Control")
    print("-" * 30)
    
    # Simulate application launching
    apps_that_can_be_opened = [
        "Notepad (notepad.exe)",
        "Calculator (calc.exe)",
        "Paint (mspaint.exe)",
        "Command Prompt (cmd.exe)",
        "PowerShell (powershell.exe)",
        "File Explorer (explorer.exe)",
        "Chrome Browser",
        "Firefox Browser",
        "VS Code",
        "Microsoft Word",
        "Microsoft Excel",
        "Any installed application"
    ]
    
    print("✅ Applications that can be controlled:")
    for app in apps_that_can_be_opened:
        print(f"   🔹 {app}")
    
    print("\n✅ Application control examples:")
    print("   🎤 'Hey ULTRON, open notepad'")
    print("   🎤 'Launch chrome'")
    print("   🎤 'Start calculator'")
    print("   🎤 'Open file explorer'")
    print("   🎤 'Run command prompt'")
    
    print("✅ Application control demo complete!")

def demo_conclusion():
    """Demo conclusion"""
    print("\n🎉 ULTRON AI Agent Demo Complete!")
    print("=" * 50)
    print("ULTRON can now:")
    print("✅ Control your PC with voice commands")
    print("✅ Open any application instantly")
    print("✅ Create, edit, and manage files")
    print("✅ Automate keyboard and mouse actions")
    print("✅ Monitor system performance")
    print("✅ Take screenshots and manage clipboard")
    print("✅ Respond in real-time to natural speech")
    print()
    print("🚀 Ready to start? Run:")
    print("   python main.py")
    print()
    print("🎤 Then say: 'Hey ULTRON' and give any command!")

def main():
    """Run the complete demo"""
    demo_introduction()
    demo_file_operations()
    demo_system_monitoring() 
    demo_automation_capabilities()
    demo_voice_commands()
    demo_application_control()
    demo_conclusion()

if __name__ == "__main__":
    main()
