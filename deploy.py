#!/usr/bin/env python3
"""
ULTRON Enhanced - Deployment Script
===================================

Automated deployment script for setting up ULTRON Enhanced
in the target directory (D:/ULTRON or user-specified).
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

def print_banner():
    """Display deployment banner."""
    print("=" * 70)
    print("   🚀 ULTRON Enhanced v3.0 - Deployment Script 🚀")
    print("=" * 70)
    print()

def get_default_install_path():
    """Get default installation path based on OS."""
    if os.name == 'nt':  # Windows
        return Path("D:/ULTRON")
    else:  # Unix-like
        return Path.home() / "ULTRON"

def create_directory_structure(base_path):
    """Create complete directory structure."""
    directories = [
        # Core directories
        'core',
        'web',
        'web/assets',
        'tools',
        'tools/automation',
        'tools/ai_tools',
        'tools/web_tools',
        'utils',
        'tests',
        
        # Runtime directories
        'logs',
        'screenshots',
        'models',
        'temp',
        'assets',
        
        # Data directories
        'config',
        'cache',
        'backups'
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True

def copy_source_files(source_path, target_path):
    """Copy all source files to target directory."""
    print("📋 Copying source files...")
    
    # Files to copy
    files_to_copy = [
        # Main application files
        'main.py',
        'agent_core.py',
        'brain.py',
        'voice_manager.py',
        'vision.py',
        'memory.py',
        'config.py',
        'ollama_manager.py',
        'security_utils.py',
        
        # Launchers
        'launch_ultron.py',
        'run.bat',
        'run.sh',
        
        # Configuration
        'ultron_config.json.example',
        'requirements.txt',
        'setup.py',
        
        # Documentation
        'README.md',
        'LICENSE',
        'Contributing.md',
        
        # GUI files
        'pokedex_ultron_gui.py',
        'gui_ultimate.py',
    ]
    
    # Directories to copy recursively
    dirs_to_copy = [
        'core',
        'web',
        'tools',
        'utils',
        'tests',
        'gui'
    ]
    
    # Copy individual files
    for file_name in files_to_copy:
        source_file = source_path / file_name
        target_file = target_path / file_name
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"   ✅ {file_name}")
        else:
            print(f"   ⚠️  {file_name} (not found)")
    
    # Copy directories
    for dir_name in dirs_to_copy:
        source_dir = source_path / dir_name
        target_dir = target_path / dir_name
        
        if source_dir.exists():
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(source_dir, target_dir)
            print(f"   ✅ {dir_name}/ (directory)")
        else:
            print(f"   ⚠️  {dir_name}/ (not found)")
    
    return True

def create_configuration(target_path):
    """Create initial configuration files."""
    print("⚙️  Creating configuration...")
    
    # Main configuration
    config_file = target_path / "ultron_config.json"
    
    if not config_file.exists():
        config_data = {
            "ai": {
                "primary_model": "ollama:qwen2.5-coder",
                "fallback_models": ["openai:gpt-4", "anthropic:claude-3"],
                "local_models": ["ollama:llama3.2"],
                "vision_model": "openai:gpt-4-vision",
                "openai_api_key": "",
                "anthropic_api_key": "",
                "google_api_key": ""
            },
            "voice": {
                "tts_engine": "pyttsx3",
                "stt_engine": "whisper",
                "wake_word": "ultron",
                "tts_rate": 150,
                "tts_volume": 0.9,
                "wake_word_feedback": True
            },
            "vision": {
                "tesseract_config": "--psm 6",
                "auto_save_screenshots": True,
                "vision_analysis_model": "gpt-4-vision"
            },
            "automation": {
                "safety_enabled": True,
                "confirmation_required": True,
                "screen_capture_interval": 5,
                "mouse_movement_speed": 1.0,
                "automation_pause": 0.1
            },
            "web": {
                "host": "localhost",
                "port": 8080,
                "enable_cors": True,
                "auto_open_browser": True
            },
            "gui": {
                "theme": "pokedex",
                "window_size": [1200, 800],
                "always_on_top": False,
                "enable_animations": True
            },
            "system": {
                "log_level": "INFO",
                "max_log_size": "10MB",
                "backup_logs": True,
                "performance_monitoring": True
            }
        }
        
        config_file.write_text(json.dumps(config_data, indent=2))
        print("   ✅ ultron_config.json")
    else:
        print("   ⚠️  ultron_config.json (already exists)")
    
    # Environment template
    env_file = target_path / ".env.example"
    env_content = """# ULTRON Enhanced Environment Variables
# Copy this to .env and fill in your values

# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Porcupine Wake Word Detection
PORCUPINE_ACCESS_KEY=your_porcupine_key_here

# Optional: Custom Model Endpoints
CUSTOM_AI_ENDPOINT=http://localhost:11434
CUSTOM_AI_MODEL=custom_model_name

# System Configuration
ULTRON_LOG_LEVEL=INFO
ULTRON_DEBUG=false
ULTRON_SAFE_MODE=true
"""
    
    env_file.write_text(env_content)
    print("   ✅ .env.example")
    
    return True

def install_dependencies(target_path):
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    
    requirements_file = target_path / "requirements.txt"
    if not requirements_file.exists():
        # Create basic requirements
        requirements = [
            "flask>=2.0.0",
            "flask-socketio>=5.0.0",
            "flask-cors>=4.0.0",
            "eventlet>=0.33.0",
            "psutil>=5.8.0",
            "opencv-python>=4.5.0",
            "pillow>=8.0.0",
            "pyautogui>=0.9.50",
            "numpy>=1.21.0",
            "requests>=2.25.0",
            "speechrecognition>=3.8.0",
            "pyttsx3>=2.90",
            "pyaudio>=0.2.11",
            "pytesseract>=0.3.8",
            "openai>=1.0.0",
            "anthropic>=0.3.0",
            "google-generativeai>=0.3.0",
            "mss>=6.1.0",
            "pydub>=0.25.0",
            "pygame>=2.1.0"
        ]
        
        requirements_file.write_text("\n".join(requirements))
    
    # Install dependencies
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 
            str(requirements_file)
        ], cwd=target_path)
        print("   ✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        return False

def create_shortcuts(target_path):
    """Create desktop shortcuts and launchers."""
    print("🔗 Creating shortcuts...")
    
    if os.name == 'nt':  # Windows
        # Create batch file launcher
        launcher_bat = target_path / "ULTRON_Enhanced.bat"
        launcher_content = f"""@echo off
cd /d "{target_path}"
call run.bat
pause
"""
        launcher_bat.write_text(launcher_content)
        print("   ✅ ULTRON_Enhanced.bat")
        
        # Try to create desktop shortcut
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "ULTRON Enhanced.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(launcher_bat)
            shortcut.WorkingDirectory = str(target_path)
            shortcut.IconLocation = str(target_path / "assets" / "ultron_icon.ico")
            shortcut.Description = "ULTRON Enhanced AI Agent"
            shortcut.save()
            
            print("   ✅ Desktop shortcut created")
        except ImportError:
            print("   ⚠️  Desktop shortcut requires pywin32")
    
    else:  # Unix-like
        # Create shell script launcher
        launcher_sh = target_path / "ultron_enhanced.sh"
        launcher_content = f"""#!/bin/bash
cd "{target_path}"
./run.sh
"""
        launcher_sh.write_text(launcher_content)
        launcher_sh.chmod(0o755)
        print("   ✅ ultron_enhanced.sh")
        
        # Create .desktop file
        desktop_file = target_path / "ultron_enhanced.desktop"
        desktop_content = f"""[Desktop Entry]
Name=ULTRON Enhanced
Comment=Advanced AI Agent System
Exec={launcher_sh}
Icon={target_path}/assets/ultron_icon.png
Terminal=false
Type=Application
Categories=Development;Utility;
"""
        desktop_file.write_text(desktop_content)
        print("   ✅ ultron_enhanced.desktop")
    
    return True

def create_documentation(target_path):
    """Create comprehensive documentation."""
    print("📚 Creating documentation...")
    
    # Quick start guide
    quickstart = target_path / "QUICKSTART.md"
    quickstart_content = """# ULTRON Enhanced - Quick Start Guide

## 🚀 Getting Started

### 1. First Time Setup
- Run `launch_ultron.py` for automatic setup
- Configure `ultron_config.json` with your API keys
- Test voice and automation features

### 2. Launch Options
- **GUI Mode**: `python main.py` (default)
- **Web Mode**: `python main.py --web`
- **CLI Mode**: `python main.py --cli`

### 3. Web Interface
- Open browser to: http://localhost:8080
- Use Pokédx-style interface
- Real-time system monitoring

### 4. Voice Commands
- "ULTRON, take a screenshot"
- "Analyze this screen"
- "Open Chrome and navigate to GitHub"
- "What processes are running?"

### 5. Configuration
- AI Models: Configure in `ultron_config.json`
- Voice Settings: Adjust TTS rate and volume
- Automation: Enable/disable safety features

## 🔧 Troubleshooting

### Common Issues
1. **No Voice Recognition**: Check microphone permissions
2. **Screenshot Failed**: Verify screen capture permissions
3. **AI Not Responding**: Check API keys and model availability
4. **GUI Won't Start**: Try `python main.py --cli`

### Getting Help
- Check `logs/error.log` for detailed errors
- Run diagnostics: `python -c "import agent_core; print('OK')"`
- Report issues on GitHub

## 📖 Documentation
- Main README: Complete feature documentation
- API Reference: `/docs/API.md`
- Architecture: `/docs/ARCHITECTURE.md`
"""
    
    quickstart.write_text(quickstart_content)
    print("   ✅ QUICKSTART.md")
    
    # Installation summary
    install_log = target_path / "INSTALLATION.log"
    install_content = f"""ULTRON Enhanced v3.0 - Installation Log
================================================

Installation Date: {datetime.now().isoformat()}
Installation Path: {target_path}
Python Version: {sys.version}
Platform: {sys.platform}

Components Installed:
✅ Core ULTRON Agent System
✅ Pokédx-Style GUI Interface
✅ Web Server & API Endpoints
✅ Voice Recognition & TTS
✅ Computer Vision & OCR
✅ System Automation Tools
✅ Multi-AI Integration
✅ Configuration Templates

Next Steps:
1. Configure ultron_config.json with your API keys
2. Run launch_ultron.py to start the system
3. Access web interface at http://localhost:8080
4. Check QUICKSTART.md for usage guide

Support:
- Documentation: README.md
- Issues: GitHub Issues
- Logs: logs/ directory
"""
    
    install_log.write_text(install_content)
    print("   ✅ INSTALLATION.log")
    
    return True

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy ULTRON Enhanced")
    parser.add_argument("--path", help="Installation path", 
                       default=str(get_default_install_path()))
    parser.add_argument("--skip-deps", action="store_true",
                       help="Skip dependency installation")
    parser.add_argument("--skip-shortcuts", action="store_true",
                       help="Skip shortcut creation")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Get paths
    source_path = Path(__file__).parent
    target_path = Path(args.path)
    
    print(f"🎯 Source: {source_path}")
    print(f"🎯 Target: {target_path}")
    print()
    
    # Confirm deployment
    if target_path.exists() and any(target_path.iterdir()):
        print("⚠️  Target directory exists and is not empty!")
        response = input("Continue? This may overwrite files [y/N]: ").lower()
        if response not in ['y', 'yes']:
            print("Deployment cancelled.")
            return 1
    
    # Deployment steps
    steps = [
        ("Directory Structure", lambda: create_directory_structure(target_path)),
        ("Source Files", lambda: copy_source_files(source_path, target_path)),
        ("Configuration", lambda: create_configuration(target_path)),
        ("Documentation", lambda: create_documentation(target_path)),
    ]
    
    if not args.skip_deps:
        steps.append(("Dependencies", lambda: install_dependencies(target_path)))
    
    if not args.skip_shortcuts:
        steps.append(("Shortcuts", lambda: create_shortcuts(target_path)))
    
    # Execute deployment steps
    failed_steps = []
    for step_name, step_func in steps:
        print(f"🔄 {step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed")
            else:
                print(f"✅ {step_name} completed")
        except Exception as e:
            print(f"❌ {step_name} error: {e}")
            failed_steps.append(step_name)
        print()
    
    # Summary
    if failed_steps:
        print(f"⚠️  Deployment completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print()
        print("You may need to complete these steps manually.")
        return_code = 1
    else:
        print("🎉 ULTRON Enhanced deployed successfully!")
        return_code = 0
    
    print()
    print("=" * 70)
    print("   🤖 ULTRON Enhanced v3.0 - Deployment Complete 🤖")
    print("=" * 70)
    print()
    print(f"📍 Installation Location: {target_path}")
    print()
    print("🚀 Next Steps:")
    print("1. Configure ultron_config.json with your API keys")
    print("2. Run launch_ultron.py to start the system")
    print("3. Access web interface at http://localhost:8080")
    print("4. Check QUICKSTART.md for detailed usage")
    print()
    
    return return_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)