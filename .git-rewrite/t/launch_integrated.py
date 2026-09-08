#!/usr/bin/env python3
"""
Integrated Launcher for Ultron GUI + Assistant
Starts both the GUI system and the assistant web app
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def start_gui():
    """Start the GUI system"""
    gui_path = Path("gui/ultron_enhanced")
    if gui_path.exists():
        print("🔴 Starting Ultron GUI...")
        try:
            subprocess.run([sys.executable, "ultron_main.py"], cwd=str(gui_path))
        except Exception as e:
            print(f"❌ GUI Error: {e}")
    else:
        print("❌ GUI path not found")

def start_assistant():
    """Start the assistant development server"""
    assistant_path = Path("assistant/ai-assistant")
    if assistant_path.exists():
        print("🤖 Starting AI Assistant...")
        try:
            subprocess.run(["npm", "run", "dev"], cwd=str(assistant_path), shell=True)
        except Exception as e:
            print(f"❌ Assistant Error: {e}")
    else:
        print("❌ Assistant path not found")

def start_bridge():
    """Start the bridge server"""
    print("🌉 Starting Bridge Server...")
    try:
        subprocess.run([sys.executable, "gui_assistant_bridge.py"])
    except Exception as e:
        print(f"❌ Bridge Error: {e}")

def main():
    print("🔴 ULTRON Integrated Launcher")
    print("=" * 40)
    
    choice = input("""
Choose launch option:
1. GUI Only
2. Assistant Only  
3. Bridge Only
4. All Components
5. Exit

Enter choice (1-5): """).strip()
    
    if choice == "1":
        start_gui()
    elif choice == "2":
        start_assistant()
    elif choice == "3":
        start_bridge()
    elif choice == "4":
        print("🚀 Starting all components...")
        
        # Start bridge in background
        bridge_thread = threading.Thread(target=start_bridge, daemon=True)
        bridge_thread.start()
        
        time.sleep(2)  # Give bridge time to start
        
        # Start assistant in background
        assistant_thread = threading.Thread(target=start_assistant, daemon=True)
        assistant_thread.start()
        
        time.sleep(3)  # Give assistant time to start
        
        # Start GUI (main thread)
        start_gui()
        
    elif choice == "5":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🔴 Shutdown requested")
        sys.exit(0)