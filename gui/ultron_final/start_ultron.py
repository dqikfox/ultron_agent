#!/usr/bin/env python3
"""
ULTRON Quick Start Launcher
Easy launcher for ULTRON with different modes
"""

import os
import sys
import subprocess
from pathlib import Path

def check_setup():
    """Check if ULTRON is properly set up"""
    print("🔍 Checking ULTRON setup...")
    
    # Check if directories exist
    required_dirs = ["logs", "screenshots", "managed_files"]
    for directory in required_dirs:
        if not Path(directory).exists():
            print(f"❌ Missing directory: {directory}")
            print("Run 'python setup.py' first")
            return False
    
    # Check if main files exist
    required_files = ["main.py", "config.json", "requirements.txt"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing file: {file}")
            return False
    
    print("✅ ULTRON setup verified")
    return True

def display_menu():
    """Display startup menu"""
    print("\n🔴 ULTRON AI Assistant Launcher")
    print("=" * 40)
    print("1. GUI Mode (Recommended)")
    print("2. Console Mode")
    print("3. Async Mode (Advanced)")
    print("4. Web Interface Only")
    print("5. Run Tests")
    print("6. Setup/Install")
    print("0. Exit")
    print("=" * 40)

def launch_mode(mode):
    """Launch ULTRON in specified mode"""
    commands = {
        "gui": [sys.executable, "main.py", "--mode", "gui"],
        "console": [sys.executable, "main.py", "--mode", "console"],
        "async": [sys.executable, "main.py", "--mode", "async"],
        "test": [sys.executable, "test_ultron.py"],
        "setup": [sys.executable, "setup.py"]
    }
    
    if mode not in commands:
        print(f"❌ Unknown mode: {mode}")
        return False
    
    try:
        print(f"🚀 Starting ULTRON in {mode} mode...")
        subprocess.run(commands[mode])
        return True
    except KeyboardInterrupt:
        print("\n⚠️ ULTRON stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start ULTRON: {e}")
        return False

def main():
    """Main launcher function"""
    print("🔴 ULTRON AI Assistant")
    
    # Check setup first
    if not check_setup():
        print("\n🔧 Running setup first...")
        if not launch_mode("setup"):
            return 1
    
    while True:
        display_menu()
        
        try:
            choice = input("\nSelect option (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                launch_mode("gui")
            elif choice == "2":
                launch_mode("console")
            elif choice == "3":
                launch_mode("async")
            elif choice == "4":
                print("🌐 Web interface will be available at http://localhost:3000")
                launch_mode("async")
            elif choice == "5":
                launch_mode("test")
            elif choice == "6":
                launch_mode("setup")
            else:
                print("❌ Invalid choice. Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
