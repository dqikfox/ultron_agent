#!/usr/bin/env python3
"""
Windows Setup Script for UltronSysAgent
Handles installation, auto-start configuration, and system integration
"""

import os
import sys
import subprocess
import winreg
import shutil
from pathlib import Path
import json

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        requirements_file = Path(__file__).parent.parent / "requirements.txt"
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_auto_start():
    """Setup Windows auto-start using Task Scheduler"""
    print("⚙️ Setting up auto-start...")
    
    try:
        # Get paths
        script_dir = Path(__file__).parent.parent
        main_script = script_dir / "main.py"
        python_exe = sys.executable
        
        # Create batch file for startup
        batch_content = f'''@echo off
cd /d "{script_dir}"
"{python_exe}" "{main_script}"
'''
        
        batch_file = script_dir / "start_ultron.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        # Create Task Scheduler task
        task_name = "UltronSysAgent"
        
        # XML task definition
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>"{batch_file}"</Command>
      <WorkingDirectory>"{script_dir}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
        
        # Save task XML
        task_xml_file = script_dir / "ultron_task.xml"
        with open(task_xml_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)
        
        # Create the task
        cmd = f'schtasks /create /tn "{task_name}" /xml "{task_xml_file}" /f'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Auto-start configured successfully")
            return True
        else:
            print(f"❌ Failed to configure auto-start: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up auto-start: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut"""
    print("🖥️ Creating desktop shortcut...")
    
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        script_dir = Path(__file__).parent.parent
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(desktop / "UltronSysAgent.lnk"))
        shortcut.Targetpath = str(script_dir / "start_ultron.bat")
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = str(script_dir / "assets" / "ultron_icon.ico")
        shortcut.Description = "UltronSysAgent - AI Assistant"
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
        
    except ImportError:
        print("⚠️ pywin32 not available, skipping shortcut creation")
        return True
    except Exception as e:
        print(f"❌ Error creating desktop shortcut: {e}")
        return False

def setup_firewall_rules():
    """Setup Windows Firewall rules for UltronSysAgent"""
    print("🔥 Setting up firewall rules...")
    
    try:
        # Allow Python through firewall
        python_exe = sys.executable
        
        # Inbound rule
        cmd_in = f'netsh advfirewall firewall add rule name="UltronSysAgent (Python) - Inbound" dir=in action=allow program="{python_exe}" enable=yes'
        subprocess.run(cmd_in, shell=True, check=True)
        
        # Outbound rule
        cmd_out = f'netsh advfirewall firewall add rule name="UltronSysAgent (Python) - Outbound" dir=out action=allow program="{python_exe}" enable=yes'
        subprocess.run(cmd_out, shell=True, check=True)
        
        print("✅ Firewall rules configured")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to configure firewall: {e}")
        return True  # Non-critical failure
    except Exception as e:
        print(f"❌ Error setting up firewall: {e}")
        return True  # Non-critical failure

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    script_dir = Path(__file__).parent.parent
    directories = [
        "logs",
        "data/memory",
        "data/cache", 
        "data/models",
        "data/screenshots",
        "plugins",
        "assets/sounds",
        "assets/images",
        "assets/themes"
    ]
    
    for directory in directories:
        dir_path = script_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  📂 {directory}")
    
    print("✅ Directories created")

def verify_installation():
    """Verify installation by testing imports"""
    print("🔍 Verifying installation...")
    
    test_imports = [
        "asyncio",
        "numpy", 
        "psutil",
        "openai",
        "httpx",
        "sounddevice",
        "webrtcvad",
        "pyttsx3",
        "PyPDF2",
        "docx",
        "PIL",
        "cv2",
        "sqlite3"
    ]
    
    failed_imports = []
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"⚠️ Some modules failed to import: {failed_imports}")
        print("You may need to install additional dependencies manually")
    else:
        print("✅ All core modules imported successfully")
    
    return len(failed_imports) == 0

def setup_environment_file():
    """Create .env file template"""
    print("🔧 Setting up environment file...")
    
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / "config" / ".env"
    
    env_template = """# UltronSysAgent Environment Configuration
# Copy this file and fill in your API keys

# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek API Key (for DeepSeek models)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# ElevenLabs API Key (for advanced TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# System Configuration
ULTRON_ADMIN_MODE=false
ULTRON_DEBUG=false
ULTRON_OFFLINE_MODE=false
ULTRON_GPU_ENABLED=true
ULTRON_CUDA_ENABLED=true
"""
    
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("✅ Environment file template created")
    else:
        print("⚠️ Environment file already exists")

def main():
    """Main setup function"""
    print("🤖 UltronSysAgent Windows Setup")
    print("================================")
    
    # Check if running as admin
    if not check_admin_privileges():
        print("⚠️ Warning: Not running as administrator")
        print("Some features may require admin privileges")
        print("Consider running 'Run as administrator' for full setup")
        print()
    
    # Create directories
    create_directories()
    
    # Setup environment file
    setup_environment_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return False
    
    # Verify installation
    verify_installation()
    
    # Setup auto-start (requires admin)
    if check_admin_privileges():
        setup_auto_start()
        setup_firewall_rules()
    else:
        print("⚠️ Skipping auto-start and firewall setup (requires admin)")
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print()
    print("🎉 UltronSysAgent setup completed!")
    print()
    print("Next steps:")
    print("1. Edit config/.env file and add your API keys")
    print("2. Run 'python main.py' to start UltronSysAgent")
    print("3. For auto-start, re-run this script as administrator")
    print()
    print("Enjoy your new AI assistant! 🤖")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        sys.exit(1)
