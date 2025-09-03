#!/usr/bin/env python3
"""
ULTRON Enhanced v3.0 - Advanced Feature Launcher
===============================================

Comprehensive launcher demonstrating all next-generation features:
• NVIDIA NIM Integration & Multi-LLM Router
• Enhanced Voice System with Wake Word Detection  
• Desktop Application with PySide6
• Real-time Performance Analytics & Optimization
• Beautiful Pokédx Web Interface
"""

import sys
import asyncio
import time
import webbrowser
import subprocess
from pathlib import Path
import logging

def print_enhanced_banner():
    """Print enhanced ULTRON banner with new features"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                     🚀 ULTRON Enhanced v3.0 - Advanced Launch 🚀                 ║
║                                                                                   ║
║                   Next-Generation AI Automation Platform                         ║
║                        with Enterprise-Grade Features                            ║
╚═══════════════════════════════════════════════════════════════════════════════════╝

✨ NEW ADVANCED FEATURES IMPLEMENTED:

🤖 AI & Machine Learning:
   • NVIDIA NIM Integration - Enterprise AI models (Llama 3.1 70B, Nemotron 4 340B)
   • Multi-LLM Router - Intelligent routing between OpenAI, Anthropic, Google, Ollama
   • Task-Optimized Model Selection - Automatic provider selection based on task type
   • Advanced Conversation Memory - Context-aware AI interactions

🎤 Enhanced Voice System:
   • Wake Word Detection - "ULTRON" activation with Porcupine engine
   • Noise Reduction & Speech Enhancement - Crystal clear voice processing
   • Voice-to-AI Pipeline - Direct voice commands to enterprise AI models
   • Multi-Engine TTS Support - pyttsx3, Azure, Google, OpenAI voices

🖥️ Desktop Application:
   • Professional PySide6 GUI - Native desktop app with system tray
   • Embedded Web Interface - Pokédx interface in desktop wrapper
   • Real-time Monitoring - Live system stats and AI performance
   • Configuration Management - Easy settings with visual interface

📊 Performance & Analytics:
   • Real-time Performance Monitoring - CPU, memory, disk, network metrics
   • Intelligent Optimization - Automatic performance tuning and suggestions
   • Predictive Analytics - Performance trend analysis and anomaly detection
   • Health Scoring - System health grading (A+ to F scale)

🌐 Web Interface Enhancements:
   • Beautiful Pokédx Design - Authentic retro-futuristic interface
   • Real-time System Analytics - Live performance dashboards
   • Voice Integration - Web-based voice controls with visual feedback
   • WebSocket Communications - Real-time updates and interactions

═══════════════════════════════════════════════════════════════════════════════════
""")

def check_dependencies():
    """Check for enhanced dependencies"""
    print("🔍 Checking Enhanced Dependencies...")
    
    deps_status = {}
    
    # Core dependencies
    try:
        import psutil
        deps_status['psutil'] = "✅ Available"
    except ImportError:
        deps_status['psutil'] = "❌ Missing - pip install psutil"
    
    try:
        import flask
        deps_status['flask'] = "✅ Available"
    except ImportError:
        deps_status['flask'] = "❌ Missing - pip install flask flask-socketio"
    
    # Enhanced voice dependencies
    try:
        import speech_recognition
        deps_status['speech_recognition'] = "✅ Available"
    except ImportError:
        deps_status['speech_recognition'] = "❌ Missing - pip install SpeechRecognition"
    
    try:
        import pvporcupine
        deps_status['pvporcupine'] = "✅ Available (Wake Word Detection)"
    except ImportError:
        deps_status['pvporcupine'] = "⚠️  Optional - pip install pvporcupine"
    
    # Desktop GUI dependencies
    try:
        import PySide6
        deps_status['PySide6'] = "✅ Available (Desktop App)"
    except ImportError:
        deps_status['PySide6'] = "⚠️  Optional - pip install PySide6"
    
    # AI provider dependencies
    try:
        import openai
        deps_status['openai'] = "✅ Available"
    except ImportError:
        deps_status['openai'] = "⚠️  Optional - pip install openai"
    
    try:
        import anthropic
        deps_status['anthropic'] = "✅ Available"
    except ImportError:
        deps_status['anthropic'] = "⚠️  Optional - pip install anthropic"
    
    try:
        import ollama
        deps_status['ollama'] = "✅ Available (Local AI)"
    except ImportError:
        deps_status['ollama'] = "⚠️  Optional - pip install ollama"
    
    # Vision dependencies
    try:
        import cv2
        deps_status['opencv'] = "✅ Available"
    except ImportError:
        deps_status['opencv'] = "⚠️  Optional - pip install opencv-python"
    
    # Display status
    for dep, status in deps_status.items():
        print(f"   {dep}: {status}")
    
    # Count missing critical dependencies
    critical_missing = [dep for dep, status in deps_status.items() 
                       if "❌" in status and dep in ['psutil', 'flask', 'speech_recognition']]
    
    if critical_missing:
        print(f"\n❌ Critical dependencies missing: {', '.join(critical_missing)}")
        print("Please install missing dependencies before proceeding.")
        return False
    else:
        print("\n✅ Core dependencies satisfied!")
        return True

async def launch_enhanced_system():
    """Launch ULTRON Enhanced with all features"""
    print("\n🚀 Launching ULTRON Enhanced v3.0...")
    
    try:
        # Import main system
        from ultron_main import UltronCore
        print("✅ Core modules loaded")
        
        # Initialize enhanced system
        print("🔄 Initializing enhanced system...")
        ultron = UltronCore()
        
        print("✅ Enhanced system initialized with:")
        print("   • Multi-LLM Router")
        print("   • Enhanced Voice System") 
        print("   • Performance Monitor")
        print("   • Real-time Analytics")
        
        # Start system
        print("\n🔄 Starting all components...")
        await ultron.start()
        
    except Exception as e:
        print(f"❌ Enhanced system launch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def launch_desktop_app():
    """Launch desktop application"""
    try:
        print("🖥️  Launching Desktop Application...")
        from ultron_desktop_app import main as desktop_main
        return desktop_main()
        
    except ImportError:
        print("❌ PySide6 not available - Desktop app cannot run")
        print("   Install with: pip install PySide6")
        return False
    except Exception as e:
        print(f"❌ Desktop app launch failed: {e}")
        return False

def show_launch_options():
    """Show launch options menu"""
    print("\n📋 ULTRON Enhanced v3.0 Launch Options:")
    print("═" * 50)
    print("1. 🚀 Launch Enhanced Web Mode (Recommended)")
    print("2. 🖥️  Launch Desktop Application (PySide6)")
    print("3. 🌐 Launch Web Interface Only")
    print("4. 💻 Launch CLI Mode")
    print("5. 🎤 Test Enhanced Voice System")
    print("6. 📊 Performance Analytics Demo")
    print("7. 🤖 Multi-LLM Router Test")
    print("8. ❓ System Diagnostics")
    print("0. ❌ Exit")
    print("═" * 50)
    
    choice = input("\n👆 Select option (0-8): ").strip()
    return choice

async def test_enhanced_voice():
    """Test enhanced voice system"""
    print("\n🎤 Testing Enhanced Voice System...")
    
    try:
        from core.enhanced_voice_system import EnhancedVoiceSystem, VoiceConfig
        
        voice_config = VoiceConfig(
            wake_words=["ultron", "computer"],
            continuous_listening=False,  # For testing
            noise_reduction=True,
            voice_feedback=True
        )
        
        voice_system = EnhancedVoiceSystem(voice_config)
        
        # Test components
        test_results = await voice_system.test_voice_system()
        
        print("🔍 Voice System Test Results:")
        for component, status in test_results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {component}: {status_icon}")
        
        if test_results.get("tts", False):
            await voice_system.speak("Enhanced voice system test completed successfully!")
        
        voice_system.cleanup()
        
    except Exception as e:
        print(f"❌ Voice system test failed: {e}")

async def test_multi_llm_router():
    """Test Multi-LLM Router"""
    print("\n🤖 Testing Multi-LLM Router...")
    
    try:
        from core.nvidia_nim_integration import MultiLLMRouter
        
        # Test configuration (you would need actual API keys)
        config = {
            'openai_api_key': '',  # Add your keys for testing
            'nvidia_api_key': '',
            'anthropic_api_key': '',
            'google_api_key': ''
        }
        
        router = MultiLLMRouter(config)
        
        print("🔍 Multi-LLM Router Status:")
        status = router.get_status()
        print(f"   Available Providers: {status['providers']}")
        print(f"   Fallback Chain: {' → '.join(status['fallback_chain'])}")
        
        # Test health check
        print("\n🏥 Running Health Check...")
        health_results = await router.health_check_all()
        
        for provider, health in health_results.items():
            status_icon = "✅" if health.get('status') == 'healthy' else "❌"
            print(f"   {provider}: {status_icon} {health.get('status', 'unknown')}")
        
        if status['providers']:
            # Test completion
            print("\n🧠 Testing AI Completion...")
            test_messages = [{"role": "user", "content": "Hello! Please respond with a brief greeting."}]
            result = await router.route_completion(test_messages)
            
            if "content" in result:
                print(f"✅ Test Response: {result['content']}")
                print(f"   Provider: {result.get('provider', 'unknown')}")
            else:
                print(f"❌ Test failed: {result}")
        
    except Exception as e:
        print(f"❌ Multi-LLM Router test failed: {e}")

async def show_performance_demo():
    """Show performance analytics demo"""
    print("\n📊 Performance Analytics Demo...")
    
    try:
        from core.performance_optimizer import SystemResourceMonitor
        
        monitor = SystemResourceMonitor()
        
        print("🔄 Starting performance monitoring...")
        monitor.start_monitoring(interval=1.0)
        
        # Let it collect data for a few seconds
        await asyncio.sleep(5)
        
        # Get real-time data
        dashboard_data = monitor.get_real_time_data()
        
        print("\n📈 Current System Performance:")
        current = dashboard_data.get('current_metrics', {})
        print(f"   CPU Usage: {current.get('cpu_percent', 0):.1f}%")
        print(f"   Memory Usage: {current.get('memory_percent', 0):.1f}%")
        print(f"   Disk Usage: {current.get('disk_usage', 0):.1f}%")
        print(f"   Health Score: {dashboard_data.get('health_score', 0)}/100")
        print(f"   Performance Grade: {dashboard_data.get('performance_grade', 'N/A')}")
        
        # Show suggestions if any
        suggestions = dashboard_data.get('suggestions', [])
        if suggestions:
            print(f"\n💡 Optimization Suggestions ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3
                print(f"   {i}. {suggestion.get('title', 'Unknown')}")
                print(f"      {suggestion.get('description', '')}")
        
        # Show anomalies if any
        anomalies = dashboard_data.get('anomalies', [])
        if anomalies:
            print(f"\n⚠️  Performance Anomalies ({len(anomalies)}):")
            for anomaly in anomalies:
                print(f"   • {anomaly.get('description', 'Unknown anomaly')}")
        
        monitor.stop_monitoring()
        
    except Exception as e:
        print(f"❌ Performance demo failed: {e}")

async def run_diagnostics():
    """Run comprehensive system diagnostics"""
    print("\n🔧 Running System Diagnostics...")
    
    print("\n1. 🐍 Python Environment:")
    print(f"   Version: {sys.version}")
    print(f"   Executable: {sys.executable}")
    
    print("\n2. 📁 Project Structure:")
    project_files = ['ultron_main.py', 'core/', 'web/', 'config_enhanced.json']
    for file_path in project_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
    
    print("\n3. 🔌 Core Components:")
    try:
        # Test core imports
        from ultron_main import UltronCore
        print("   ✅ UltronCore")
        
        from core.nvidia_nim_integration import MultiLLMRouter
        print("   ✅ MultiLLMRouter")
        
        from core.enhanced_voice_system import EnhancedVoiceSystem
        print("   ✅ EnhancedVoiceSystem")
        
        from core.performance_optimizer import SystemResourceMonitor
        print("   ✅ SystemResourceMonitor")
        
    except Exception as e:
        print(f"   ❌ Component import failed: {e}")
    
    print("\n4. 🌐 Web Interface:")
    web_files = ['web/index.html', 'web/styles.css', 'web/app.js']
    for web_file in web_files:
        if Path(web_file).exists():
            print(f"   ✅ {web_file}")
        else:
            print(f"   ❌ {web_file} - Missing")
    
    print("\n✅ Diagnostics completed!")

async def main():
    """Main enhanced launcher"""
    print_enhanced_banner()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    while True:
        choice = show_launch_options()
        
        if choice == "0":
            print("\n👋 Goodbye! Thank you for using ULTRON Enhanced v3.0")
            return 0
            
        elif choice == "1":
            print("\n🚀 Starting Enhanced Web Mode...")
            try:
                await launch_enhanced_system()
            except KeyboardInterrupt:
                print("\n\n🛑 Enhanced system stopped by user")
            return 0
            
        elif choice == "2":
            return launch_desktop_app()
            
        elif choice == "3":
            print("\n🌐 Opening Web Interface...")
            webbrowser.open("http://localhost:8080")
            
        elif choice == "4":
            print("\n💻 Starting CLI Mode...")
            subprocess.run([sys.executable, "ultron_main.py", "--cli"])
            
        elif choice == "5":
            await test_enhanced_voice()
            
        elif choice == "6":
            await show_performance_demo()
            
        elif choice == "7":
            await test_multi_llm_router()
            
        elif choice == "8":
            await run_diagnostics()
            
        else:
            print("❌ Invalid option. Please try again.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Launcher interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        sys.exit(1)