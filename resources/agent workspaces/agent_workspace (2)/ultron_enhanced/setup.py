"""
ULTRON Enhanced AI System Setup Script
Handles installation, configuration, and initialization
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

class UltronSetup:
    def __init__(self):
        self.base_dir = Path("D:/ULTRON")
        self.current_dir = Path(__file__).parent
        self.config = {}
        
    def run_setup(self):
        """Main setup process"""
        print("=" * 60)
        print("ULTRON ENHANCED AI SYSTEM - SETUP")
        print("=" * 60)
        print()
        
        try:
            self.check_requirements()
            self.create_directory_structure()
            self.install_dependencies()
            self.copy_files()
            self.create_config()
            self.download_assets()
            self.setup_shortcuts()
            self.final_configuration()
            
            print()
            print("=" * 60)
            print("SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Installation Directory: {self.base_dir}")
            print("To start ULTRON, run: python ultron_main.py")
            print("Or use the desktop shortcut if created.")
            print()
            
        except Exception as e:
            print(f"Setup failed: {e}")
            sys.exit(1)
    
    def check_requirements(self):
        """Check system requirements"""
        print("Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 or higher is required")
        
        # Check if running on Windows (for full functionality)
        if os.name != 'nt':
            print("Warning: Full functionality requires Windows OS")
        
        # Check admin privileges
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Warning: Admin privileges recommended for full functionality")
        except:
            pass
        
        print("✓ System requirements check completed")
    
    def create_directory_structure(self):
        """Create ULTRON directory structure"""
        print("Creating directory structure...")
        
        directories = [
            self.base_dir,
            self.base_dir / "core",
            self.base_dir / "models",
            self.base_dir / "assets",
            self.base_dir / "logs",
            self.base_dir / "web",
            self.base_dir / "core" / "plugins",
            self.base_dir / "assets" / "sounds",
            self.base_dir / "assets" / "images",
            self.base_dir / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {directory}")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("Installing Python dependencies...")
        
        requirements_file = self.current_dir / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ])
                print("✓ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Some dependencies failed to install: {e}")
                print("You may need to install them manually")
        else:
            print("Warning: requirements.txt not found")
    
    def copy_files(self):
        """Copy ULTRON files to installation directory"""
        print("Copying ULTRON files...")
        
        # Copy main script
        source_main = self.current_dir / "ultron_main.py"
        dest_main = self.base_dir / "ultron_main.py"
        if source_main.exists():
            shutil.copy2(source_main, dest_main)
            print(f"✓ Copied: {dest_main}")
        
        # Copy web files
        web_source = self.current_dir / "web"
        web_dest = self.base_dir / "web"
        if web_source.exists():
            if web_dest.exists():
                shutil.rmtree(web_dest)
            shutil.copytree(web_source, web_dest)
            print(f"✓ Copied web interface to: {web_dest}")
        
        # Copy any additional files
        additional_files = [
            "requirements.txt",
            "README.md"
        ]
        
        for file_name in additional_files:
            source_file = self.current_dir / file_name
            dest_file = self.base_dir / file_name
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                print(f"✓ Copied: {dest_file}")
    
    def create_config(self):
        """Create initial configuration"""
        print("Creating configuration...")
        
        config_path = self.base_dir / "config.json"
        
        # Get OpenAI API key from user
        api_key = input("Enter your OpenAI API key (optional, press Enter to skip): ").strip()
        
        # Get voice preference
        print("Voice preference:")
        print("1. Male")
        print("2. Female")
        voice_choice = input("Select voice (1 or 2, default: 1): ").strip() or "1"
        voice_gender = "female" if voice_choice == "2" else "male"
        
        # Get theme preference
        print("Theme preference:")
        print("1. Red (Classic)")
        print("2. Blue (Advanced)")
        theme_choice = input("Select theme (1 or 2, default: 1): ").strip() or "1"
        theme = "blue" if theme_choice == "2" else "red"
        
        # Create configuration
        config = {
            "openai_api_key": api_key,
            "voice": voice_gender,
            "theme": theme,
            "hotkeys": {
                "wake": "ctrl+shift+u",
                "toggle_listening": "ctrl+shift+l",
                "emergency_stop": "ctrl+shift+x"
            },
            "offline_mode": not bool(api_key),
            "vision_enabled": True,
            "web_port": 3000,
            "auto_launch_web": True,
            "pokedex_mode": True,
            "version": "2.0.0",
            "setup_date": str(Path().cwd())
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuration saved to: {config_path}")
        self.config = config
    
    def download_assets(self):
        """Download or create necessary assets"""
        print("Setting up assets...")
        
        # Create placeholder sound files
        sounds_dir = self.base_dir / "assets" / "sounds"
        sound_files = [
            "wake.wav",
            "confirm.wav",
            "error.wav",
            "pokedex_open.wav",
            "button_press.wav"
        ]
        
        for sound_file in sound_files:
            sound_path = sounds_dir / sound_file
            if not sound_path.exists():
                # Create empty placeholder
                sound_path.touch()
                print(f"✓ Created placeholder: {sound_path}")
        
        # Create placeholder icon
        icon_path = self.base_dir / "assets" / "images" / "ultron_icon.png"
        if not icon_path.exists():
            icon_path.touch()
            print(f"✓ Created placeholder icon: {icon_path}")
    
    def setup_shortcuts(self):
        """Create desktop shortcuts"""
        print("Creating shortcuts...")
        
        try:
            # Create batch file for easy launching
            batch_content = f"""@echo off
cd /d "{self.base_dir}"
python ultron_main.py
pause
"""
            batch_path = self.base_dir / "start_ultron.bat"
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            print(f"✓ Created launcher: {batch_path}")
            
            # Try to create desktop shortcut
            try:
                import winshell
                from win32com.client import Dispatch
                
                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, "ULTRON AI.lnk")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = str(batch_path)
                shortcut.WorkingDirectory = str(self.base_dir)
                shortcut.IconLocation = str(self.base_dir / "assets" / "images" / "ultron_icon.png")
                shortcut.save()
                
                print(f"✓ Desktop shortcut created: {shortcut_path}")
            except ImportError:
                print("Note: Desktop shortcut creation requires winshell package")
            except Exception as e:
                print(f"Note: Could not create desktop shortcut: {e}")
                
        except Exception as e:
            print(f"Warning: Shortcut creation failed: {e}")
    
    def final_configuration(self):
        """Final setup steps"""
        print("Finalizing configuration...")
        
        # Create initial log entry
        log_path = self.base_dir / "logs" / "ultron.log"
        with open(log_path, 'w') as f:
            f.write(f"ULTRON Enhanced AI System - Setup completed on {Path().cwd()}\n")
        
        # Create startup info
        info_path = self.base_dir / "STARTUP_INFO.txt"
        with open(info_path, 'w') as f:
            f.write("""ULTRON ENHANCED AI SYSTEM - STARTUP INFORMATION

1. LAUNCHING ULTRON:
   - Double-click "start_ultron.bat" or desktop shortcut
   - Or run: python ultron_main.py from the ULTRON directory
   - Admin privileges recommended for full functionality

2. FIRST TIME SETUP:
   - Configure OpenAI API key in settings if not done during setup
   - Test voice recognition by saying wake words: "Ultron", "Jarvis"
   - Explore the Pokedex-style interface using navigation controls

3. MAIN FEATURES:
   - Voice control with wake word detection
   - Pokedex-style interface with multiple sections
   - System automation and control
   - Screen capture and analysis
   - Task management and file operations

4. CONTROLS:
   - D-Pad: Navigation
   - A Button: Execute/Confirm
   - B Button: Back/Cancel
   - Voice: Say wake words to activate
   - Web Interface: Automatic launch at http://localhost:3000

5. TROUBLESHOOTING:
   - Check logs in: logs/ultron.log
   - Ensure microphone permissions are granted
   - Run as administrator for system control features
   - Check network connection for AI features

6. CONFIGURATION:
   - Main config: config.json
   - Settings accessible through Pokedex interface
   - Themes: Red (Classic) or Blue (Advanced)

For support and updates, check the documentation.
""")
        
        print(f"✓ Created startup guide: {info_path}")
        print("✓ Setup finalization completed")

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ULTRON Enhanced AI System Setup

Usage:
    python setup.py          - Run full setup
    python setup.py --help   - Show this help

This script will:
1. Check system requirements
2. Create directory structure in D:/ULTRON
3. Install Python dependencies
4. Copy ULTRON files
5. Create configuration
6. Set up assets and shortcuts

Requirements:
- Python 3.8 or higher
- Windows OS (recommended for full features)
- Admin privileges (recommended)
- Internet connection (for dependencies)
""")
        return
    
    setup = UltronSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
