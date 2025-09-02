#!/usr/bin/env python3
"""
ULTRON Enhanced - Demo Launcher
==============================

This script demonstrates the key features of ULTRON Enhanced v3.0
including the Pokédx-style web interface and modular architecture.
"""

import asyncio
import sys
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print ULTRON Enhanced banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         🤖 ULTRON Enhanced v3.0 🤖                           ║
║                                                                              ║
║        Transform your system into a comprehensive AI automation platform     ║
║                       with beautiful Pokédx interface                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎮 Features Demonstrated:
   • Pokédx-Style Web Interface with retro-futuristic design
   • Modular Architecture with Voice, Vision, System Automation
   • Real-time System Monitoring with animated indicators  
   • Multi-AI Integration (OpenAI, Anthropic, Ollama, NVIDIA)
   • Advanced Computer Vision and OCR capabilities
   • Voice Control with wake word detection
   • Complete Process Management and File Organization
   • Beautiful LED indicators and authentic sound effects

═══════════════════════════════════════════════════════════════════════════════
""")

async def demo_system():
    """Run ULTRON Enhanced demonstration"""
    print_banner()
    
    # Import here to show loading
    print("🔄 Loading ULTRON Enhanced core modules...")
    try:
        from ultron_main import UltronCore
        print("✓ Core modules loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load core modules: {e}")
        return False
    
    print("\n🔄 Initializing ULTRON Enhanced system...")
    try:
        ultron = UltronCore()
        print("✓ System initialized successfully")
        print(f"✓ Configuration: {ultron.config.theme} theme, Port {ultron.config.web_port}")
    except Exception as e:
        print(f"✗ Failed to initialize system: {e}")
        return False
    
    print("\n🔄 Starting web server and components...")
    try:
        # Start web server
        if ultron.web_server.start_server():
            print("✓ Web server started successfully")
            web_url = f"http://localhost:{ultron.config.web_port}"
            print(f"🌐 Pokédx Interface: {web_url}")
            
            # Try to open web browser
            try:
                print("🔄 Opening Pokédx interface in browser...")
                webbrowser.open(web_url)
                print("✓ Browser opened to Pokédx interface")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"   Please manually open: {web_url}")
            
        else:
            print("✗ Failed to start web server")
            return False
            
    except Exception as e:
        print(f"✗ Failed to start web server: {e}")
        return False
    
    print(f"""
🎉 ULTRON Enhanced Demo is now running!

┌─────────────────────────────────────────────────────────────────┐
│                        🎮 Demo Instructions                     │
├─────────────────────────────────────────────────────────────────┤
│  1. Open your browser to: http://localhost:{ultron.config.web_port}              │
│  2. Explore the beautiful Pokédx-style interface              │  
│  3. Try the different tabs: CONSOLE, SYSTEM, VISION, etc.      │
│  4. Watch real-time system monitoring with animated bars       │
│  5. Click the 🎤 button to test voice interface (if available) │
│  6. Enjoy the authentic LED indicators and sound effects       │
│  7. Press Ctrl+C to stop the demo                              │
└─────────────────────────────────────────────────────────────────┘

💡 System Status:
   • Web Interface: ✓ Running on port {ultron.config.web_port}
   • Voice Processing: {"✓ Available" if ultron.voice_processor.tts_engine else "⚠️  Limited (headless mode)"}
   • Vision System: {"✓ Available" if ultron.vision_system else "⚠️  Limited (headless mode)"}  
   • System Automation: {"✓ Available" if ultron.system_automation else "✗ Not available"}
   • File Organization: {"✓ Available" if hasattr(ultron, 'file_sorter') else "⚠️  Disabled for demo"}

🎯 This demo showcases the complete ULTRON Enhanced transformation with
   professional architecture, beautiful interface, and enterprise features!

   Press Ctrl+C to stop the demo...
""")
    
    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🔴 Demo stopped by user")
        
        # Clean shutdown
        print("🔄 Shutting down ULTRON Enhanced...")
        try:
            ultron.web_server.stop_server()
            print("✓ Web server stopped")
        except Exception as e:
            print(f"⚠️  Error stopping web server: {e}")
        
        print("✅ Demo completed successfully!")
        print("\nThank you for trying ULTRON Enhanced v3.0! 🤖✨")
        return True

def main():
    """Main demo entry point"""
    try:
        # Run the async demo
        return asyncio.run(demo_system())
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)