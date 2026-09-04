"""
ULTRON Enhanced AI System - Launcher
Provides an easy way to start ULTRON with proper checks and initialization
"""

import os
import sys
import json
import time
import ctypes
import subprocess
from pathlib import Path

class UltronLauncher:
    def __init__(self):
        self.base_dir = Path("D:/ULTRON")
        self.script_dir = Path(__file__).parent
        
    def run(self):
        """Main launcher process"""
        self.print_header()
        
        try:
            self.check_installation()
            self.check_admin_privileges()
            self.check_dependencies()
            self.start_ultron()
            
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            input("Press Enter to exit...")
            sys.exit(1)
    
    def print_header(self):
        """Print ULTRON header"""
        print("=" * 60)
        print("  ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗")
        print("  ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║")
        print("  ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║")
        print("  ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║")
        print("  ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║")
        print("   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝")
        print()
        print("         ENHANCED AI SYSTEM - POKEDEX INTERFACE")
        print("                     Version 2.0.0")
        print("=" * 60)
        print()
    
    def check_installation(self):
        """Check if ULTRON is properly installed"""
        print("🔍 Checking ULTRON installation...")
        
        # Check if base directory exists
        if not self.base_dir.exists():
            # Try to find ULTRON in current directory
            current_main = self.script_dir / "ultron_main.py"
            if current_main.exists():
                print(f"⚠️  ULTRON not found in {self.base_dir}")
                print(f"📁 Found ULTRON in current directory: {self.script_dir}")
                
                response = input("Run from current directory? (y/n): ").lower()
                if response == 'y':
                    self.base_dir = self.script_dir
                else:
                    raise Exception(f"ULTRON not installed in {self.base_dir}. Run setup.py first.")
            else:
                raise Exception(f"ULTRON not found. Please run setup.py first.")
        
        # Check main script
        main_script = self.base_dir / "ultron_main.py"
        if not main_script.exists():
            raise Exception(f"Main script not found: {main_script}")
        
        # Check configuration
        config_file = self.base_dir / "config.json"
        if not config_file.exists():
            print("⚠️  Configuration file not found. Creating default configuration...")
            self.create_default_config()
        
        print("✅ Installation check completed")
    
    def check_admin_privileges(self):
        """Check and optionally request admin privileges"""
        print("🔐 Checking administrator privileges...")
        
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("⚠️  Not running as administrator")
                print("   Some features may be limited (system control, automation)")
                
                response = input("Request admin privileges? (y/n): ").lower()
                if response == 'y':
                    print("🔄 Requesting administrator privileges...")
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, " ".join(sys.argv), None, 1
                    )
                    sys.exit(0)
                else:
                    print("⚠️  Continuing without admin privileges")
            else:
                print("✅ Running with administrator privileges")
        except Exception:
            print("⚠️  Could not check admin privileges (non-Windows system?)")
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("📦 Checking dependencies...")
        
        required_modules = [
            'tkinter',
            'psutil',
            'PIL',
            'pygame',
            'speech_recognition',
            'pyttsx3'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print(f"❌ Missing required modules: {', '.join(missing_modules)}")
            response = input("Install missing dependencies? (y/n): ").lower()
            if response == 'y':
                self.install_dependencies()
            else:
                raise Exception("Required dependencies not installed")
        else:
            print("✅ All dependencies available")
    
    def install_dependencies(self):
        """Install missing dependencies"""
        print("📦 Installing dependencies...")
        
        requirements_file = self.base_dir / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ])
                print("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError:
                raise Exception("Failed to install dependencies")
        else:
            # Install basic requirements
            basic_packages = [
                "psutil", "Pillow", "pygame", "SpeechRecognition", "pyttsx3", "openai"
            ]
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install"] + basic_packages
                )
                print("✅ Basic dependencies installed")
            except subprocess.CalledProcessError:
                raise Exception("Failed to install basic dependencies")
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "openai_api_key": "",
            "voice": "male",
            "theme": "red",
            "offline_mode": True,
            "vision_enabled": True,
            "web_port": 3000,
            "auto_launch_web": True,
            "pokedex_mode": True,
            "first_run": True
        }
        
        config_file = self.base_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✅ Default configuration created: {config_file}")
    
    def start_ultron(self):
        """Start the ULTRON system"""
        print("🚀 Starting ULTRON Enhanced AI System...")
        print()
        
        # Change to ULTRON directory
        os.chdir(self.base_dir)
        
        # Start ULTRON
        main_script = self.base_dir / "ultron_main.py"
        
        try:
            # Show loading message
            print("⚡ Initializing AI systems...")
            print("🎮 Loading Pokedex interface...")
            print("🎤 Setting up voice recognition...")
            print("👁️  Activating vision systems...")
            print()
            print("🌟 ULTRON is starting up...")
            print("=" * 60)
            print()
            
            # Execute ULTRON
            subprocess.run([sys.executable, str(main_script)], check=True)
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"ULTRON failed to start: {e}")
        except KeyboardInterrupt:
            print("\\n⚠️  ULTRON startup interrupted by user")
        except Exception as e:
            raise Exception(f"Unexpected error starting ULTRON: {e}")

def main():
    """Main launcher function"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("""
ULTRON Enhanced AI System Launcher

Usage:
    python launch_ultron.py         - Start ULTRON with checks
    python launch_ultron.py --help  - Show this help

This launcher will:
1. Check ULTRON installation
2. Verify administrator privileges
3. Check required dependencies
4. Start ULTRON Enhanced AI System

For first-time setup, run: python setup.py
""")
            return
        elif sys.argv[1] == '--quick':
            # Quick launch without checks (for advanced users)
            os.chdir("D:/ULTRON")
            subprocess.run([sys.executable, "ultron_main.py"])
            return
    
    launcher = UltronLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
