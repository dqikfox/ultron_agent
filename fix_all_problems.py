#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Comprehensive Problem Fixer
This script fixes all identified issues in the ULTRON Agent system
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_status(message, status="INFO"):
    """Print status message with formatting"""
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def fix_missing_dependencies():
    """Install missing Python dependencies"""
    print_status("Installing missing dependencies...", "INFO")
    
    missing_deps = [
        "flask==3.0.0",
        "pydantic==2.5.0", 
        "python-dotenv==1.0.0",
        "pytesseract==0.3.10"
    ]
    
    for dep in missing_deps:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print_status(f"Installed {dep}", "SUCCESS")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to install {dep}: {e}", "ERROR")

def create_missing_files():
    """Create any missing essential files"""
    print_status("Creating missing essential files...", "INFO")
    
    # Create __init__.py files
    init_dirs = [
        "tools",
        "utils", 
        "ultron_agent",
        "ultron_agent/core"
    ]
    
    for dir_path in init_dirs:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text("# ULTRON Agent module\n")
            print_status(f"Created {init_file}", "SUCCESS")

def fix_config_issues():
    """Fix configuration-related issues"""
    print_status("Fixing configuration issues...", "INFO")
    
    config_file = Path("ultron_config.json")
    if not config_file.exists():
        # Create basic config
        basic_config = {
            "use_voice": True,
            "use_vision": True,
            "use_api": True,
            "use_gui": True,
            "llm_model": "qwen3-coder:480b-cloud",
            "ollama_base_url": "http://localhost:11434",
            "log_level": "INFO",
            "debug": False,
            "voice_enabled": True,
            "vision_enabled": True,
            "memory_enabled": True,
            "tools_enabled": True,
            "gui_enabled": True,
            "api_host": "127.0.0.1",
            "api_port": 5000
        }
        
        with open(config_file, 'w') as f:
            json.dump(basic_config, f, indent=2)
        print_status("Created basic ultron_config.json", "SUCCESS")

def fix_import_issues():
    """Fix common import issues"""
    print_status("Fixing import issues...", "INFO")
    
    # Create missing utility files
    utils_dir = Path("utils")
    utils_dir.mkdir(exist_ok=True)
    
    # Create basic event_system.py if missing
    event_system_file = utils_dir / "event_system.py"
    if not event_system_file.exists():
        event_system_content = '''"""
Basic event system for ULTRON Agent
"""
import asyncio
from typing import Dict, List, Callable, Any

class EventSystem:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event: str, callback: Callable):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    async def emit(self, event: str, data: Any = None):
        if event in self.listeners:
            for callback in self.listeners[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Event callback error: {e}")
'''
        event_system_file.write_text(event_system_content)
        print_status("Created basic event_system.py", "SUCCESS")

def fix_directory_structure():
    """Ensure proper directory structure"""
    print_status("Fixing directory structure...", "INFO")
    
    required_dirs = [
        "logs",
        "cache",
        "screenshots", 
        "tools",
        "utils",
        "gui/ultron_enhanced/web"
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print_status(f"Ensured directory exists: {dir_path}", "SUCCESS")

def test_basic_functionality():
    """Test basic system functionality"""
    print_status("Testing basic functionality...", "INFO")
    
    try:
        # Test config loading
        from ultron_agent.config import load_config
        config = load_config()
        print_status("Configuration loading works", "SUCCESS")
        
        # Test logging
        from utils.ultron_logger import log_info
        log_info("test", "System test successful")
        print_status("Logging system works", "SUCCESS")
        
        # Test agent core
        from agent_core import UltronAgent
        agent = UltronAgent()
        print_status("Agent core initialization works", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Basic functionality test failed: {e}", "ERROR")
        return False

def main():
    """Main fix function"""
    print("🔧 ULTRON Agent 3.0 - Comprehensive Problem Fixer")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    try:
        # Run all fixes
        fix_missing_dependencies()
        create_missing_files()
        fix_config_issues()
        fix_import_issues()
        fix_directory_structure()
        
        print("=" * 60)
        print_status("Running basic functionality test...", "INFO")
        
        if test_basic_functionality():
            print("=" * 60)
            print_status("🎉 All problems fixed successfully!", "SUCCESS")
            print_status("ULTRON Agent should now be ready to run", "SUCCESS")
            print_status("Try running: python main.py", "INFO")
        else:
            print_status("Some issues remain. Check the errors above.", "WARNING")
            
    except Exception as e:
        print_status(f"Fix process failed: {e}", "ERROR")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())