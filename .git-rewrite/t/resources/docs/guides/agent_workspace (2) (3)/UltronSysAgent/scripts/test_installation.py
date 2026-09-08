#!/usr/bin/env python3
"""
Installation Test Script for UltronSysAgent
Verifies that all components are properly installed and configured
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    tests = {
        # Core Python modules
        'asyncio': lambda: __import__('asyncio'),
        'sqlite3': lambda: __import__('sqlite3'),
        'json': lambda: __import__('json'),
        'pathlib': lambda: __import__('pathlib'),
        'logging': lambda: __import__('logging'),
        
        # Third-party dependencies
        'numpy': lambda: __import__('numpy'),
        'psutil': lambda: __import__('psutil'),
        'httpx': lambda: __import__('httpx'),
        
        # Optional dependencies
        'sounddevice': lambda: __import__('sounddevice'),
        'webrtcvad': lambda: __import__('webrtcvad'),
        'pyttsx3': lambda: __import__('pyttsx3'),
        'cv2': lambda: __import__('cv2'),
        'PIL': lambda: __import__('PIL'),
        'PyPDF2': lambda: __import__('PyPDF2'),
        'docx': lambda: __import__('docx'),
        
        # AI dependencies
        'openai': lambda: __import__('openai'),
        
        # GUI
        'tkinter': lambda: __import__('tkinter'),
    }
    
    results = {}
    for name, import_func in tests.items():
        try:
            import_func()
            print(f"  ✅ {name}")
            results[name] = True
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            results[name] = False
        except Exception as e:
            print(f"  ⚠️ {name}: {e}")
            results[name] = False
    
    return results

def test_project_structure():
    """Test that project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_paths = [
        'src',
        'src/core',
        'src/modules',
        'src/gui',
        'config',
        'logs',
        'data',
        'plugins',
        'scripts',
        'main.py',
        'requirements.txt',
        'README.md'
    ]
    
    results = {}
    for path in required_paths:
        full_path = project_root / path
        exists = full_path.exists()
        
        if exists:
            print(f"  ✅ {path}")
        else:
            print(f"  ❌ {path}")
        
        results[path] = exists
    
    return results

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.core.config import ConfigManager
        
        config = ConfigManager()
        config.load()
        
        # Test basic config access
        admin_mode = config.get('system.admin_mode')
        voice_enabled = config.get('voice.always_listening')
        
        print(f"  ✅ Configuration loaded successfully")
        print(f"  ✅ Admin mode: {admin_mode}")
        print(f"  ✅ Voice listening: {voice_enabled}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_core_modules():
    """Test that core modules can be imported"""
    print("\n🧠 Testing core modules...")
    
    core_modules = [
        'src.core.config',
        'src.core.event_bus',
        'src.core.logger',
        'src.core.application'
    ]
    
    results = {}
    for module in core_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
            results[module] = True
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            results[module] = False
    
    return results

def test_feature_modules():
    """Test that feature modules can be imported"""
    print("\n🔧 Testing feature modules...")
    
    feature_modules = [
        'src.modules.voice_engine.voice_engine',
        'src.modules.ai_brain.ai_brain',
        'src.modules.system_automation.system_automation',
        'src.modules.memory_manager.memory_manager',
        'src.modules.file_manager.file_manager',
        'src.modules.vision_system.vision_system',
        'src.modules.scheduler.scheduler'
    ]
    
    results = {}
    for module in feature_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
            results[module] = True
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            results[module] = False
    
    return results

def test_gui():
    """Test GUI components"""
    print("\n🖥️ Testing GUI components...")
    
    try:
        import tkinter as tk
        
        # Test basic tkinter functionality
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Test GUI module import
        from src.gui.main_window import MainWindow
        
        print("  ✅ Tkinter available")
        print("  ✅ GUI module imports successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ❌ GUI test failed: {e}")
        return False

def test_plugin_system():
    """Test plugin system"""
    print("\n🔌 Testing plugin system...")
    
    try:
        # Test example plugin
        plugin_path = project_root / "plugins" / "example_plugin.py"
        
        if plugin_path.exists():
            print("  ✅ Example plugin file exists")
            
            # Try to import plugin
            sys.path.insert(0, str(plugin_path.parent))
            import example_plugin
            
            print("  ✅ Example plugin imports successfully")
            print(f"  ✅ Plugin class: {example_plugin.PLUGIN_CLASS}")
            print(f"  ✅ Plugin name: {example_plugin.PLUGIN_NAME}")
            
            return True
        else:
            print("  ❌ Example plugin file not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Plugin system test failed: {e}")
        return False

async def test_async_functionality():
    """Test async functionality"""
    print("\n⚡ Testing async functionality...")
    
    try:
        # Test event bus
        from src.core.event_bus import EventBus
        
        event_bus = EventBus()
        
        # Test event publishing
        await event_bus.publish("test_event", {"test": True}, source="test")
        
        print("  ✅ Event bus functionality")
        print("  ✅ Async operations")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Async test failed: {e}")
        return False

def test_dependencies():
    """Test specific dependency functionality"""
    print("\n🔬 Testing dependency functionality...")
    
    tests = {}
    
    # Test numpy
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        tests['numpy'] = True
        print("  ✅ NumPy operations")
    except Exception as e:
        tests['numpy'] = False
        print(f"  ❌ NumPy: {e}")
    
    # Test psutil
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        tests['psutil'] = True
        print(f"  ✅ psutil (CPU: {cpu_percent}%)")
    except Exception as e:
        tests['psutil'] = False
        print(f"  ❌ psutil: {e}")
    
    # Test OpenAI (if API key available)
    try:
        import openai
        tests['openai'] = True
        print("  ✅ OpenAI library")
    except Exception as e:
        tests['openai'] = False
        print(f"  ❌ OpenAI: {e}")
    
    return tests

def generate_report(results):
    """Generate test report"""
    print("\n" + "=" * 60)
    print("🤖 ULTRON SYSAGENT INSTALLATION TEST REPORT")
    print("=" * 60)
    
    # Calculate overall score
    total_tests = 0
    passed_tests = 0
    
    for category, category_results in results.items():
        if isinstance(category_results, dict):
            for test, result in category_results.items():
                total_tests += 1
                if result:
                    passed_tests += 1
        else:
            total_tests += 1
            if category_results:
                passed_tests += 1
    
    score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Overall Score: {score:.1f}% ({passed_tests}/{total_tests} tests passed)")
    print()
    
    # Status determination
    if score >= 90:
        status = "🟢 EXCELLENT - Ready for full operation"
    elif score >= 75:
        status = "🟡 GOOD - Some optional features may be limited"
    elif score >= 60:
        status = "🟠 FAIR - Basic functionality available"
    else:
        status = "🔴 POOR - Significant issues found"
    
    print(f"Status: {status}")
    print()
    
    # Recommendations
    print("Recommendations:")
    
    if results.get('imports', {}).get('sounddevice', True) == False:
        print("  • Install sounddevice for voice functionality: pip install sounddevice")
    
    if results.get('imports', {}).get('cv2', True) == False:
        print("  • Install OpenCV for vision features: pip install opencv-python")
    
    if results.get('imports', {}).get('webrtcvad', True) == False:
        print("  • Install webrtcvad for voice activity detection: pip install webrtcvad")
    
    if results.get('configuration', True) == False:
        print("  • Check configuration file: config/config.json")
    
    if score < 75:
        print("  • Consider running setup script: python scripts/setup_windows.py")
        print("  • Install missing dependencies: pip install -r requirements.txt")
    
    print()
    print("For detailed installation instructions, see README.md")
    print("=" * 60)

async def main():
    """Main test function"""
    print("🤖 UltronSysAgent Installation Test")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['structure'] = test_project_structure()
    results['configuration'] = test_configuration()
    results['core_modules'] = test_core_modules()
    results['feature_modules'] = test_feature_modules()
    results['gui'] = test_gui()
    results['plugins'] = test_plugin_system()
    results['async'] = await test_async_functionality()
    results['dependencies'] = test_dependencies()
    
    # Generate report
    generate_report(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
