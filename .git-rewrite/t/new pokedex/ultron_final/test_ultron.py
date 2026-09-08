#!/usr/bin/env python3
"""
ULTRON System Testing Suite
Comprehensive tests for all components
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all module imports"""
    print("🔧 Testing module imports...")
    
    try:
        from main import UltronCore
        print("✅ Main module imported successfully")
    except Exception as e:
        print(f"❌ Main module import failed: {e}")
        return False
    
    try:
        from core.voice_engine import VoiceEngine
        print("✅ Voice engine imported successfully")
    except Exception as e:
        print(f"❌ Voice engine import failed: {e}")
        return False
    
    try:
        from core.vision_system import VisionSystem
        print("✅ Vision system imported successfully")
    except Exception as e:
        print(f"❌ Vision system import failed: {e}")
        return False
    
    try:
        from core.ai_brain import AIBrain
        print("✅ AI brain imported successfully")
    except Exception as e:
        print(f"❌ AI brain import failed: {e}")
        return False
    
    try:
        from core.system_control import SystemControl
        print("✅ System control imported successfully")
    except Exception as e:
        print(f"❌ System control import failed: {e}")
        return False
    
    try:
        from core.file_manager import FileManager
        print("✅ File manager imported successfully")
    except Exception as e:
        print(f"❌ File manager import failed: {e}")
        return False
    
    try:
        from core.web_interface import WebInterface
        print("✅ Web interface imported successfully")
    except Exception as e:
        print(f"❌ Web interface import failed: {e}")
        return False
    
    try:
        from gui.ultron_gui import UltronGUI
        print("✅ GUI imported successfully")
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    
    dependencies = [
        'speech_recognition',
        'pyttsx3',
        'cv2',
        'pytesseract',
        'PIL',
        'numpy',
        'psutil',
        'pyautogui',
        'flask',
        'tkinter'
    ]
    
    missing = []
    
    for dep in dependencies:
        try:
            if dep == 'cv2':
                import cv2
            elif dep == 'PIL':
                from PIL import Image
            elif dep == 'tkinter':
                import tkinter as tk
            else:
                __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

async def test_ultron_core():
    """Test ULTRON core functionality"""
    print("\n🤖 Testing ULTRON core...")
    
    try:
        from main import UltronCore
        
        # Initialize ULTRON
        ultron = UltronCore()
        print("✅ ULTRON core initialized")
        
        # Test configuration loading
        config = ultron.config
        if config:
            print("✅ Configuration loaded")
        else:
            print("❌ Configuration loading failed")
            return False
        
        # Test component availability
        status = ultron.get_status()
        print(f"✅ Status retrieved: {status['running']}")
        
        # Test basic command processing
        result = await ultron.process_command("time", source="test")
        if result['success']:
            print(f"✅ Command processed: {result['response'][:50]}...")
        else:
            print(f"❌ Command processing failed: {result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ULTRON core test failed: {e}")
        return False

def test_voice_engine():
    """Test voice engine functionality"""
    print("\n🎤 Testing voice engine...")
    
    try:
        from core.voice_engine import VoiceEngine
        
        # Mock config
        config = {
            'voice': {
                'enabled': True,
                'tts_rate': 150,
                'recognition_timeout': 5
            }
        }
        
        voice = VoiceEngine(config)
        
        if voice.is_available():
            print("✅ Voice engine available")
            
            # Test TTS (without actually speaking)
            try:
                voice.speak("Test message")
                print("✅ TTS functionality working")
            except Exception as e:
                print(f"⚠️ TTS test failed: {e}")
        else:
            print("⚠️ Voice engine not available (may need microphone)")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice engine test failed: {e}")
        return False

async def test_vision_system():
    """Test vision system functionality"""
    print("\n👁️ Testing vision system...")
    
    try:
        from core.vision_system import VisionSystem
        
        # Mock config
        config = {
            'vision': {
                'enabled': True,
                'auto_enhance': True,
                'ocr_language': 'eng'
            }
        }
        
        vision = VisionSystem(config)
        
        if vision.is_available():
            print("✅ Vision system available")
            
            # Test screenshot
            result = await vision.take_screenshot()
            if result['success']:
                print(f"✅ Screenshot taken: {result['path']}")
            else:
                print(f"❌ Screenshot failed: {result['error']}")
                return False
        else:
            print("❌ Vision system not available (Tesseract missing?)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Vision system test failed: {e}")
        return False

async def test_system_control():
    """Test system control functionality"""
    print("\n⚙️ Testing system control...")
    
    try:
        from core.system_control import SystemControl
        
        # Mock config
        config = {
            'system': {
                'admin_required': True,
                'safe_commands_only': True
            }
        }
        
        system = SystemControl(config)
        
        if system.is_available():
            print("✅ System control available")
            
            # Test system status
            status = await system.get_status()
            if 'cpu' in status:
                print(f"✅ System status: CPU {status['cpu']:.1f}%")
            else:
                print(f"❌ System status failed: {status}")
                return False
        else:
            print("❌ System control not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ System control test failed: {e}")
        return False

async def test_file_manager():
    """Test file manager functionality"""
    print("\n📁 Testing file manager...")
    
    try:
        from core.file_manager import FileManager
        
        # Mock config
        config = {
            'files': {
                'auto_sort': True,
                'backup_before_sort': True
            }
        }
        
        file_manager = FileManager(config)
        
        if file_manager.is_available():
            print("✅ File manager available")
            
            # Test file classification
            test_file = "test.txt"
            category = file_manager.classify_file(test_file)
            print(f"✅ File classification: {test_file} -> {category}")
            
            # Test statistics
            stats = file_manager.get_statistics()
            if 'total_files' in stats:
                print(f"✅ Statistics: {stats['total_files']} files managed")
            else:
                print(f"❌ Statistics failed: {stats}")
                return False
        else:
            print("❌ File manager not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ File manager test failed: {e}")
        return False

def test_gui():
    """Test GUI functionality (without displaying)"""
    print("\n🖥️ Testing GUI...")
    
    try:
        from gui.ultron_gui import UltronGUI
        print("✅ GUI classes imported successfully")
        
        # Don't actually create GUI window in test
        print("✅ GUI test passed (import only)")
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_web_interface():
    """Test web interface functionality"""
    print("\n🌐 Testing web interface...")
    
    try:
        from core.web_interface import WebInterface
        print("✅ Web interface imported successfully")
        
        # Check if HTML file exists
        html_file = Path("web/index.html")
        if html_file.exists():
            print("✅ Web HTML file found")
        else:
            print("❌ Web HTML file missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🔴 ULTRON System Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Voice Engine", test_voice_engine),
        ("GUI", test_gui),
        ("Web Interface", test_web_interface)
    ]
    
    async_tests = [
        ("ULTRON Core", test_ultron_core),
        ("Vision System", test_vision_system),
        ("System Control", test_system_control),
        ("File Manager", test_file_manager)
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} - PASSED")
            else:
                print(f"❌ {name} - FAILED")
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")
    
    # Run asynchronous tests
    for name, test_func in async_tests:
        try:
            if await test_func():
                passed += 1
                print(f"✅ {name} - PASSED")
            else:
                print(f"❌ {name} - FAILED")
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ULTRON is ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

def main():
    """Main test runner"""
    # Suppress logging for tests
    logging.basicConfig(level=logging.ERROR)
    
    try:
        result = asyncio.run(run_all_tests())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
