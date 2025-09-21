"""
ULTRON Enhanced - Interactive Demonstration
Shows system capabilities and provides testing interface
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def setup_demo_environment():
    """Setup demonstration environment"""
    print("=" * 60)
    print("  ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗")
    print("  ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║")
    print("  ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║")
    print("  ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║")
    print("  ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║")
    print("   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝")
    print()
    print("         ENHANCED AI SYSTEM - DEMONSTRATION MODE")
    print("                     Version 2.0.0")
    print("=" * 60)
    print()

def check_system_readiness():
    """Check if system is ready for demonstration"""
    print("🔍 Checking system readiness...")
    
    # Check core modules
    try:
        from core import get_system_capabilities, check_dependencies, check_compatibility
        capabilities = get_system_capabilities()
        dependencies = check_dependencies()
        compatibility = check_compatibility()
        
        print(f"✅ ULTRON Core Version: {capabilities['version']}")
        print(f"✅ Platform: {compatibility['platform']}")
        print(f"✅ Python: {compatibility['python_version'].split()[0]}")
        
        # Check module availability
        modules = capabilities['modules']
        for module_name, available in modules.items():
            status = "✅" if available else "❌"
            print(f"{status} {module_name.replace('_', ' ').title()}: {'Available' if available else 'Not Available'}")
        
        # Check dependencies
        if not dependencies['all_required_available']:
            print("❌ Missing required dependencies:")
            for dep in dependencies['missing_required']:
                print(f"   - {dep}")
            return False
        
        if dependencies['missing_optional']:
            print("⚠️  Optional dependencies missing (limited functionality):")
            for dep in dependencies['missing_optional']:
                print(f"   - {dep}")
        
        # Check compatibility issues
        if not compatibility['compatible']:
            print("❌ Compatibility issues:")
            for issue in compatibility['issues']:
                print(f"   - {issue}")
            return False
        
        if compatibility['warnings']:
            print("⚠️  Compatibility warnings:")
            for warning in compatibility['warnings']:
                print(f"   - {warning}")
        
        print("✅ System ready for demonstration")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import core modules: {e}")
        return False
    except Exception as e:
        print(f"❌ System check failed: {e}")
        return False

def demonstrate_voice_system():
    """Demonstrate voice processing capabilities"""
    print("\n🎤 VOICE SYSTEM DEMONSTRATION")
    print("-" * 40)
    
    try:
        from core.voice_processor import VoiceProcessor
        
        # Create test configuration
        config = {
            "voice": "male",
            "wake_words": ["ultron", "demo"],
            "voice_settings": {"rate": 150, "volume": 0.8}
        }
        
        voice_processor = VoiceProcessor(config)
        
        if voice_processor.tts_engine:
            print("✅ Text-to-Speech system initialized")
            
            # Get voice information
            voice_info = voice_processor.get_voice_info()
            if voice_info:
                print(f"📊 Available voices: {len(voice_info.get('available_voices', []))}")
                print(f"📊 Current rate: {voice_info.get('current_rate', 'Unknown')}")
                print(f"📊 Current volume: {voice_info.get('current_volume', 'Unknown')}")
            
            # Test speech
            test_response = input("\n🔊 Test speech synthesis? (y/n): ").lower()
            if test_response == 'y':
                print("🔊 Speaking test message...")
                voice_processor.speak("ULTRON Enhanced demonstration mode activated. All systems operational.")
                
        else:
            print("❌ Text-to-Speech not available")
        
        if voice_processor.microphone:
            print("✅ Microphone system initialized")
            
            # Test microphone
            test_mic = input("\n🎤 Test microphone? (y/n): ").lower()
            if test_mic == 'y':
                print("🎤 Testing microphone (speak for 3 seconds)...")
                mic_result = voice_processor.test_microphone()
                print(f"📊 Microphone test result: {mic_result.get('status', 'unknown')}")
                if mic_result.get('recognized_text'):
                    print(f"📝 Recognized: {mic_result['recognized_text']}")
        else:
            print("❌ Microphone not available")
        
        # Cleanup
        voice_processor.cleanup()
        
    except ImportError:
        print("❌ Voice processor not available")
    except Exception as e:
        print(f"❌ Voice demonstration failed: {e}")

def demonstrate_vision_system():
    """Demonstrate computer vision capabilities"""
    print("\n👁️ VISION SYSTEM DEMONSTRATION")
    print("-" * 40)
    
    try:
        from core.vision_system import VisionSystem
        
        # Create test configuration
        config = {
            "vision_enabled": True,
            "screenshot_dir": "./demo_screenshots"
        }
        
        vision_system = VisionSystem(config)
        
        # Get capabilities
        capabilities = vision_system.get_vision_capabilities()
        print(f"📊 OpenCV Available: {capabilities.get('cv2_available', False)}")
        print(f"📊 AI Vision Available: {capabilities.get('ai_vision_available', False)}")
        print(f"📊 Supported Formats: {', '.join(capabilities.get('supported_formats', []))}")
        
        # Test screenshot
        test_screenshot = input("\n📷 Take demonstration screenshot? (y/n): ").lower()
        if test_screenshot == 'y':
            print("📷 Taking screenshot...")
            result = vision_system.capture_screen()
            
            if result.get("success"):
                print(f"✅ Screenshot saved: {result.get('filename', 'unknown')}")
                print(f"📊 Resolution: {result.get('width', 0)}x{result.get('height', 0)}")
                print(f"📊 File size: {result.get('file_size', 0)} bytes")
                
                # Test analysis
                test_analysis = input("\n🔍 Analyze screenshot? (y/n): ").lower()
                if test_analysis == 'y':
                    print("🔍 Analyzing screenshot...")
                    analysis_result = vision_system.analyze_screen("basic")
                    
                    if analysis_result.get("success"):
                        print("✅ Analysis completed")
                        if analysis_result.get("image_info"):
                            info = analysis_result["image_info"]
                            print(f"📊 Image mode: {info.get('mode', 'unknown')}")
                            print(f"📊 Brightness: {info.get('average_brightness', 0):.1f}")
                    else:
                        print(f"❌ Analysis failed: {analysis_result.get('message', 'unknown error')}")
            else:
                print(f"❌ Screenshot failed: {result.get('message', 'unknown error')}")
        
        # Show analysis history
        history = vision_system.get_analysis_history(5)
        if history.get("success") and history.get("history"):
            print(f"\n📈 Recent analyses: {len(history['history'])}")
        
    except ImportError:
        print("❌ Vision system not available")
    except Exception as e:
        print(f"❌ Vision demonstration failed: {e}")

def demonstrate_system_automation():
    """Demonstrate system automation capabilities"""
    print("\n⚙️ SYSTEM AUTOMATION DEMONSTRATION")
    print("-" * 40)
    
    try:
        from core.system_automation import SystemAutomation
        
        # Create test configuration
        config = {}
        
        automation = SystemAutomation(config)
        print(f"🔐 Admin privileges: {automation.is_admin}")
        
        # Test system info
        print("\n📊 Getting system information...")
        sys_info = automation.system_monitor.get_system_info("basic")
        
        if sys_info.get("success"):
            info = sys_info["system_info"]
            print(f"💻 CPU Usage: {info.get('cpu_percent', 0):.1f}%")
            print(f"💾 Memory Usage: {info.get('memory_percent', 0):.1f}%")
            print(f"💿 Disk Usage: {info.get('disk_percent', 0):.1f}%")
        
        # Test process management
        print("\n🔍 Getting process information...")
        proc_info = automation.process_manager.execute_command({"action": "list"})
        
        if proc_info.get("success"):
            processes = proc_info.get("processes", [])
            print(f"⚡ Active processes: {len(processes)}")
            
            # Show top 5 processes by CPU
            top_processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5]
            print("🔥 Top CPU processes:")
            for proc in top_processes:
                print(f"   {proc.get('name', 'Unknown')}: {proc.get('cpu_percent', 0):.1f}%")
        
        # Test file operations (safe)
        print("\n📁 Testing file operations...")
        file_info = automation.file_manager.execute_command({
            "action": "list",
            "path": "."
        })
        
        if file_info.get("success"):
            files = file_info.get("files", [])
            print(f"📄 Files in current directory: {len(files)}")
            
            # Show first few files
            for file_item in files[:5]:
                file_type = "📁" if file_item.get('is_dir') else "📄"
                print(f"   {file_type} {file_item.get('name', 'Unknown')}")
        
        # Test automation task creation
        print("\n🤖 Testing automation task creation...")
        task_result = automation.execute_command("automation_task", {
            "action": "create",
            "name": "Demo Task",
            "description": "Demonstration automation task",
            "commands": [
                {"type": "system_info", "data": {"info_type": "basic"}}
            ]
        })
        
        if task_result.get("success"):
            print(f"✅ Created task: {task_result.get('task_id')}")
            
            # List tasks
            list_result = automation.execute_command("automation_task", {"action": "list"})
            if list_result.get("success"):
                tasks = list_result.get("tasks", [])
                print(f"📋 Total automation tasks: {len(tasks)}")
        
    except ImportError:
        print("❌ System automation not available")
    except Exception as e:
        print(f"❌ System automation demonstration failed: {e}")

def demonstrate_web_server():
    """Demonstrate web server capabilities"""
    print("\n🌐 WEB SERVER DEMONSTRATION")
    print("-" * 40)
    
    try:
        from core.web_server import UltronWebServer, WebServerUtils
        
        # Check port availability
        test_port = 3001  # Use different port for demo
        port_available = WebServerUtils.is_port_available(test_port)
        print(f"🔌 Port {test_port} available: {port_available}")
        
        if not port_available:
            test_port = WebServerUtils.find_available_port(3001)
            print(f"🔌 Using alternative port: {test_port}")
        
        # Create test configuration
        config = {
            "web_port": test_port,
            "web_dir": "./web"
        }
        
        web_server = UltronWebServer(config)
        
        # Test server start (but don't actually start to avoid conflicts)
        print("📊 Web server configuration:")
        print(f"   Port: {web_server.port}")
        print(f"   Web directory: {web_server.web_dir}")
        print(f"   API endpoints: {len(web_server.api_endpoints)}")
        
        # Test API endpoint handling (without starting server)
        print("\n🔌 Testing API endpoints...")
        
        # Test status endpoint
        status_result = web_server.handle_api_request("/api/status", "GET", {})
        if status_result.get("success"):
            print("✅ Status API endpoint functional")
            status_data = status_result.get("status", {})
            print(f"   Server configured: {status_data.get('server_running', 'unknown')}")
        
        # Test command endpoint
        command_result = web_server.handle_api_request("/api/command", "POST", {
            "command": "test command",
            "type": "demo"
        })
        if command_result.get("success"):
            print("✅ Command API endpoint functional")
        
        print(f"🌐 Web interface would be available at: http://localhost:{test_port}")
        
    except ImportError:
        print("❌ Web server not available")
    except Exception as e:
        print(f"❌ Web server demonstration failed: {e}")

def demonstrate_integration():
    """Demonstrate system integration"""
    print("\n🔗 INTEGRATION DEMONSTRATION")
    print("-" * 40)
    
    try:
        # Import main ULTRON core
        sys.path.append(os.path.dirname(__file__))
        from ultron_main import UltronCore, load_config
        
        # Load configuration
        config = load_config()
        
        # Create ULTRON core instance
        print("🚀 Initializing ULTRON core...")
        ultron_core = UltronCore(config)
        
        # Test core status
        status = ultron_core.get_status()
        print(f"✅ ULTRON core initialized")
        print(f"📊 Mode: {status.get('current_mode', 'unknown')}")
        print(f"📊 Voice available: {status.get('voice_available', False)}")
        print(f"📊 Vision available: {status.get('vision_available', False)}")
        
        # Test command processing
        print("\n💬 Testing command processing...")
        test_commands = [
            "hello",
            "status", 
            "time",
            "help"
        ]
        
        for command in test_commands:
            print(f"   Command: {command}")
            result = ultron_core.process_command(command)
            if result.get("success"):
                print(f"   Response: {result.get('response', 'No response')[:50]}...")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Test system info
        print("\n📊 Testing system information...")
        sys_info = ultron_core.get_system_info("basic")
        if sys_info.get("success"):
            info = sys_info.get("system_info", {})
            print(f"   CPU: {info.get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {info.get('memory_percent', 0):.1f}%")
        
        # Cleanup
        ultron_core.stop()
        print("✅ Integration test completed")
        
    except ImportError as e:
        print(f"❌ Integration test failed - import error: {e}")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

def interactive_menu():
    """Interactive demonstration menu"""
    while True:
        print("\n" + "=" * 50)
        print("ULTRON ENHANCED - DEMONSTRATION MENU")
        print("=" * 50)
        print("1. 🎤 Voice System Demo")
        print("2. 👁️  Vision System Demo") 
        print("3. ⚙️  System Automation Demo")
        print("4. 🌐 Web Server Demo")
        print("5. 🔗 Integration Demo")
        print("6. 📊 System Status")
        print("7. 🔧 Quick System Check")
        print("0. ❌ Exit Demo")
        print("-" * 50)
        
        try:
            choice = input("Select option (0-7): ").strip()
            
            if choice == "0":
                print("\n👋 Exiting ULTRON demonstration...")
                break
            elif choice == "1":
                demonstrate_voice_system()
            elif choice == "2":
                demonstrate_vision_system()
            elif choice == "3":
                demonstrate_system_automation()
            elif choice == "4":
                demonstrate_web_server()
            elif choice == "5":
                demonstrate_integration()
            elif choice == "6":
                show_system_status()
            elif choice == "7":
                check_system_readiness()
            else:
                print("❌ Invalid option. Please try again.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            input("Press Enter to continue...")

def show_system_status():
    """Show comprehensive system status"""
    print("\n📊 COMPREHENSIVE SYSTEM STATUS")
    print("-" * 40)
    
    try:
        # System information
        import platform
        import sys
        print(f"🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📁 Working Directory: {os.getcwd()}")
        print(f"⏰ Current Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check core modules
        try:
            from core import get_system_capabilities
            capabilities = get_system_capabilities()
            print(f"\n🔧 ULTRON Core Version: {capabilities['version']}")
            print("📦 Module Status:")
            for module, available in capabilities['modules'].items():
                status = "✅" if available else "❌"
                print(f"   {status} {module.replace('_', ' ').title()}")
        except ImportError:
            print("\n❌ ULTRON core modules not available")
        
        # System resources
        try:
            import psutil
            print(f"\n💻 System Resources:")
            print(f"   CPU: {psutil.cpu_percent():.1f}%")
            print(f"   Memory: {psutil.virtual_memory().percent:.1f}%")
            print(f"   Disk: {psutil.disk_usage('/').percent:.1f}%")
        except ImportError:
            print("\n❌ System resource monitoring not available")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def main():
    """Main demonstration function"""
    setup_demo_environment()
    
    if not check_system_readiness():
        print("\n❌ System not ready for demonstration")
        print("Please run setup.py first or install missing dependencies")
        sys.exit(1)
    
    print("\n🎯 ULTRON Enhanced is ready for demonstration!")
    print("This demo will showcase the key features and capabilities.")
    
    # Ask user preference
    demo_mode = input("\nChoose demo mode:\n1. Interactive Menu\n2. Full Auto Demo\n3. Quick Test\nEnter choice (1-3): ").strip()
    
    if demo_mode == "1":
        interactive_menu()
    elif demo_mode == "2":
        print("\n🚀 Running full automated demonstration...")
        demonstrate_voice_system()
        demonstrate_vision_system() 
        demonstrate_system_automation()
        demonstrate_web_server()
        demonstrate_integration()
        print("\n✅ Full demonstration completed!")
    elif demo_mode == "3":
        print("\n⚡ Running quick test...")
        check_system_readiness()
        show_system_status()
        print("\n✅ Quick test completed!")
    else:
        print("❌ Invalid choice, running interactive menu...")
        interactive_menu()
    
    print("\n" + "=" * 60)
    print("✨ ULTRON ENHANCED DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("Thank you for trying ULTRON Enhanced!")
    print("To start the full system, run: python ultron_main.py")
    print("Or use the launcher: python launch_ultron.py")
    print("For installation help: python setup.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
