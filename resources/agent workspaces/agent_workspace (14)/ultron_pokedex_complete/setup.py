#!/usr/bin/env python3
"""
ULTRON Setup Script
Prepares the D:\ULTRON directory and installs dependencies
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ULTRON_ROOT = r"D:\ULTRON"

def create_directory_structure():
    """Create the ULTRON directory structure"""
    directories = [
        ULTRON_ROOT,
        os.path.join(ULTRON_ROOT, "core"),
        os.path.join(ULTRON_ROOT, "models"),
        os.path.join(ULTRON_ROOT, "assets"),
        os.path.join(ULTRON_ROOT, "logs"),
        os.path.join(ULTRON_ROOT, "web"),
        os.path.join(ULTRON_ROOT, "screenshots"),
        os.path.join(ULTRON_ROOT, "backups")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_default_config():
    """Create default configuration file"""
    config_path = os.path.join(ULTRON_ROOT, "config.json")
    
    if os.path.exists(config_path):
        print(f"✅ Config already exists: {config_path}")
        return
    
    default_config = {
        "voice": {
            "enabled": True,
            "rate": 150,
            "volume": 0.9
        },
        "ai": {
            "local_mode": True,
            "api_key": "",
            "model": "local"
        },
        "interface": {
            "theme": "pokedex",
            "animations": True,
            "startup_sound": True
        },
        "system": {
            "auto_screenshot": False,
            "log_conversations": True,
            "backup_frequency": "daily"
        },
        "wake_words": [
            "ultron",
            "hello",
            "speak",
            "ultra"
        ]
    }
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"✅ Created config: {config_path}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try running: pip install -r requirements.txt manually")

def copy_main_file():
    """Copy main.py to ULTRON directory"""
    source = "main.py"
    destination = os.path.join(ULTRON_ROOT, "main.py")
    
    if os.path.exists(source):
        shutil.copy2(source, destination)
        print(f"✅ Copied main.py to: {destination}")
    else:
        print(f"❌ main.py not found in current directory")

def create_startup_scripts():
    """Create convenient startup scripts"""
    
    # Windows batch file
    bat_content = f"""@echo off
title ULTRON AI Assistant
cd /d "{ULTRON_ROOT}"
python main.py
pause
"""
    
    bat_path = os.path.join(ULTRON_ROOT, "start_ultron.bat")
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    
    # Python launcher
    py_content = f"""#!/usr/bin/env python3
import os
import sys

# Change to ULTRON directory
os.chdir(r"{ULTRON_ROOT}")

# Add to Python path
sys.path.insert(0, r"{ULTRON_ROOT}")

# Import and run
from main import main
main()
"""
    
    py_path = os.path.join(ULTRON_ROOT, "start_ultron.py")
    with open(py_path, 'w') as f:
        f.write(py_content)
    
    print(f"✅ Created startup scripts:")
    print(f"   - {bat_path}")
    print(f"   - {py_path}")

def verify_installation():
    """Verify the installation"""
    print("\n🔍 Verifying installation...")
    
    checks = [
        (os.path.join(ULTRON_ROOT, "main.py"), "Main script"),
        (os.path.join(ULTRON_ROOT, "config.json"), "Configuration"),
        (os.path.join(ULTRON_ROOT, "logs"), "Logs directory"),
        (os.path.join(ULTRON_ROOT, "assets"), "Assets directory"),
    ]
    
    all_good = True
    for path, description in checks:
        if os.path.exists(path):
            print(f"✅ {description}: {path}")
        else:
            print(f"❌ {description}: {path}")
            all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("🤖 ULTRON Setup Script")
    print("=" * 50)
    print(f"Setting up ULTRON in: {ULTRON_ROOT}")
    print()
    
    try:
        # Step 1: Create directories
        print("1️⃣ Creating directory structure...")
        create_directory_structure()
        print()
        
        # Step 2: Create config
        print("2️⃣ Creating configuration...")
        create_default_config()
        print()
        
        # Step 3: Install dependencies
        print("3️⃣ Installing dependencies...")
        install_dependencies()
        print()
        
        # Step 4: Copy files
        print("4️⃣ Copying main files...")
        copy_main_file()
        print()
        
        # Step 5: Create startup scripts
        print("5️⃣ Creating startup scripts...")
        create_startup_scripts()
        print()
        
        # Step 6: Verify
        print("6️⃣ Verifying installation...")
        if verify_installation():
            print("\n🎉 ULTRON setup completed successfully!")
            print(f"\nTo start ULTRON:")
            print(f"  Option 1: Double-click {os.path.join(ULTRON_ROOT, 'start_ultron.bat')}")
            print(f"  Option 2: Run 'python {os.path.join(ULTRON_ROOT, 'main.py')}'")
            print(f"  Option 3: Run 'python {os.path.join(ULTRON_ROOT, 'start_ultron.py')}'")
        else:
            print("\n❌ Some components failed to install properly")
            print("Please check the errors above and try again")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
