#!/usr/bin/env python3
"""
Quick start script for UltronSysAgent
Provides easy launch with environment checks
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if critical dependencies are available"""
    critical_deps = [
        'asyncio',
        'psutil', 
        'tkinter'
    ]
    
    missing_deps = []
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing critical dependencies: {missing_deps}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def check_config():
    """Check if configuration exists"""
    config_file = project_root / "config" / "config.json"
    if not config_file.exists():
        print("⚠️ Configuration file not found!")
        print("Creating default configuration...")
        
        # Create config directory
        config_file.parent.mkdir(exist_ok=True)
        
        # Copy default config
        default_config = project_root / "config" / "config.json"
        if default_config.exists():
            return True
        else:
            print("❌ Default configuration not found")
            return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 Starting UltronSysAgent...")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Import and run main application
    try:
        from main import main as run_main
        run_main()
    except KeyboardInterrupt:
        print("\n🔴 UltronSysAgent stopped by user")
    except Exception as e:
        print(f"❌ Error starting UltronSysAgent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
