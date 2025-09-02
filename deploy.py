#!/usr/bin/env python3
"""
ULTRON Enhanced - Deployment Script
Automated deployment for D:/ULTRON directory structure
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Deployment configuration
DEPLOY_TARGET = r"D:\ULTRON"
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(DEPLOY_TARGET, "backups")

def print_banner():
    """Print deployment banner"""
    print("=" * 60)
    print("  ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗")
    print("  ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║")
    print("  ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║")
    print("  ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║")
    print("  ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║")
    print("   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝")
    print()
    print("         ENHANCED AI SYSTEM - DEPLOYMENT SCRIPT")
    print("                     Version 2.0.0")
    print("=" * 60)
    print()

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_backup():
    """Create backup of existing installation"""
    if not os.path.exists(DEPLOY_TARGET):
        print("📁 No existing installation found")
        return True
    
    print("📦 Creating backup of existing installation...")
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"ultron_backup_{timestamp}")
    
    try:
        # Backup critical files
        critical_files = ['config.json', 'logs', 'models']
        
        for item in critical_files:
            source_path = os.path.join(DEPLOY_TARGET, item)
            if os.path.exists(source_path):
                dest_path = os.path.join(backup_path, item)
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                print(f"  ✅ Backed up: {item}")
        
        print(f"✅ Backup created: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def deploy_files():
    """Deploy ULTRON Enhanced files"""
    print("🚀 Deploying ULTRON Enhanced files...")
    
    try:
        # Create target directory structure
        directories = [
            DEPLOY_TARGET,
            os.path.join(DEPLOY_TARGET, "core"),
            os.path.join(DEPLOY_TARGET, "web"),
            os.path.join(DEPLOY_TARGET, "web", "assets"),
            os.path.join(DEPLOY_TARGET, "assets"),
            os.path.join(DEPLOY_TARGET, "logs"),
            os.path.join(DEPLOY_TARGET, "models"),
            os.path.join(DEPLOY_TARGET, "screenshots"),
            os.path.join(DEPLOY_TARGET, "temp")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"  📁 Created: {os.path.basename(directory)}")
        
        # File deployment mapping
        file_mappings = {
            # Main files
            "ultron_main.py": "ultron_main.py",
            "launch_ultron.py": "launch_ultron.py",
            "setup.py": "setup.py",
            "requirements.txt": "requirements.txt",
            "demo_ultron.py": "demo_ultron.py",
            "README.md": "README.md",
            
            # Core modules
            "core/__init__.py": "core/__init__.py",
            "core/voice_processor.py": "core/voice_processor.py",
            "core/system_automation.py": "core/system_automation.py",
            "core/vision_system.py": "core/vision_system.py",
            "core/web_server.py": "core/web_server.py",
            
            # Web interface
            "web/index.html": "web/index.html",
            "web/styles.css": "web/styles.css",
            "web/app.js": "web/app.js",
            "web/assets/sounds.js": "web/assets/sounds.js",
        }
        
        # Deploy files
        for source_file, target_file in file_mappings.items():
            source_path = os.path.join(SOURCE_DIR, source_file)
            target_path = os.path.join(DEPLOY_TARGET, target_file)
            
            if os.path.exists(source_path):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(source_path, target_path)
                print(f"  ✅ Deployed: {source_file}")
            else:
                print(f"  ⚠️  Missing: {source_file}")
        
        # Deploy config if not exists
        config_path = os.path.join(DEPLOY_TARGET, "config.json")
        if not os.path.exists(config_path):
            source_config = os.path.join(SOURCE_DIR, "config.json")
            if os.path.exists(source_config):
                shutil.copy2(source_config, config_path)
                print(f"  ✅ Deployed: config.json")
        else:
            print(f"  📋 Preserved existing config.json")
        
        print("✅ File deployment completed")
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        requirements_path = os.path.join(DEPLOY_TARGET, "requirements.txt")
        if not os.path.exists(requirements_path):
            print("❌ requirements.txt not found")
            return False
        
        # Install using pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_path, "--upgrade"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Dependency installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Dependency installation error: {e}")
        return False

def setup_shortcuts():
    """Create desktop shortcuts"""
    print("🔗 Creating desktop shortcuts...")
    
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Main launcher shortcut
        launcher_path = os.path.join(DEPLOY_TARGET, "launch_ultron.py")
        shortcut_content = f'@echo off\ncd /d "{DEPLOY_TARGET}"\npython "{launcher_path}"\npause'
        
        shortcut_path = os.path.join(desktop, "ULTRON Enhanced.bat")
        with open(shortcut_path, 'w') as f:
            f.write(shortcut_content)
        
        print(f"  ✅ Created: ULTRON Enhanced.bat")
        
        # Demo shortcut
        demo_path = os.path.join(DEPLOY_TARGET, "demo_ultron.py")
        demo_content = f'@echo off\ncd /d "{DEPLOY_TARGET}"\npython "{demo_path}"\npause'
        
        demo_shortcut_path = os.path.join(desktop, "ULTRON Demo.bat")
        with open(demo_shortcut_path, 'w') as f:
            f.write(demo_content)
        
        print(f"  ✅ Created: ULTRON Demo.bat")
        
        return True
        
    except Exception as e:
        print(f"❌ Shortcut creation failed: {e}")
        return False

def verify_deployment():
    """Verify deployment integrity"""
    print("🔍 Verifying deployment...")
    
    critical_files = [
        "ultron_main.py",
        "launch_ultron.py",
        "config.json",
        "core/__init__.py",
        "web/index.html"
    ]
    
    missing_files = []
    for file_path in critical_files:
        full_path = os.path.join(DEPLOY_TARGET, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Deployment verification failed:")
        for missing in missing_files:
            print(f"  Missing: {missing}")
        return False
    
    print("✅ Deployment verification passed")
    return True

def update_config():
    """Update configuration for deployment"""
    print("⚙️ Updating configuration...")
    
    try:
        config_path = os.path.join(DEPLOY_TARGET, "config.json")
        
        # Load existing config or create new one
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update paths and settings
        config.update({
            "ultron_root": DEPLOY_TARGET,
            "web_dir": os.path.join(DEPLOY_TARGET, "web"),
            "assets_dir": os.path.join(DEPLOY_TARGET, "assets"),
            "logs_dir": os.path.join(DEPLOY_TARGET, "logs"),
            "models_dir": os.path.join(DEPLOY_TARGET, "models"),
            "screenshots_dir": os.path.join(DEPLOY_TARGET, "screenshots"),
            "deployment_date": datetime.now().isoformat(),
            "version": "2.0.0"
        })
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration updated")
        return True
        
    except Exception as e:
        print(f"❌ Configuration update failed: {e}")
        return False

def main():
    """Main deployment function"""
    print_banner()
    
    print(f"📍 Source: {SOURCE_DIR}")
    print(f"📍 Target: {DEPLOY_TARGET}")
    print()
    
    # Check admin privileges
    if not check_admin_privileges():
        print("⚠️  Warning: Not running as administrator")
        print("Some features may require admin privileges")
        print()
    
    # Confirm deployment
    response = input(f"Deploy ULTRON Enhanced to {DEPLOY_TARGET}? (y/N): ").lower()
    if response != 'y':
        print("❌ Deployment cancelled")
        sys.exit(0)
    
    print("\n🚀 Starting deployment...\n")
    
    # Deployment steps
    steps = [
        ("Creating backup", create_backup),
        ("Deploying files", deploy_files),
        ("Installing dependencies", install_dependencies),
        ("Updating configuration", update_config),
        ("Creating shortcuts", setup_shortcuts),
        ("Verifying deployment", verify_deployment)
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            success = False
            break
    
    print("\n" + "=" * 60)
    if success:
        print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📁 Installation directory: {DEPLOY_TARGET}")
        print("🚀 Launch ULTRON: Use desktop shortcut or run launch_ultron.py")
        print("🎮 Try demo: Run demo_ultron.py for feature demonstration")
        print("📖 Documentation: See README.md for full usage guide")
        print("⚙️ Configuration: Edit config.json to customize settings")
    else:
        print("❌ DEPLOYMENT FAILED")
        print("=" * 60)
        print("Check error messages above and try again")
        print("Manual installation may be required")
    
    print("=" * 60)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
