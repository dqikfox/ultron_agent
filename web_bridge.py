"""
ULTRON Web Bridge - Connects Pokédex GUI to Agent Core
Follows project architecture from copilot instructions
"""

import os
import sys
import asyncio
import json
import threading
import time
import traceback
from pathlib import Path

# Add project root (per copilot instructions)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class UltronWebBridge:
    """Bridges web GUI to agent_core.py following project patterns"""

    def __init__(self):
        self.gui_dir = project_root / "gui" / "ultron_enhanced" / "web"
        self.agent_instance = None
        self.server_running = False

    def verify_gui_exists(self):
        """Verify Pokédex GUI exists at specified location"""
        index_file = self.gui_dir / "index.html"

        if not self.gui_dir.exists():
            print(f"❌ GUI directory not found: {self.gui_dir} - web_bridge.py:32")
            return False

        if not index_file.exists():
            print(f"❌ index.html not found: {index_file} - web_bridge.py:36")
            return False

        print(f"✅ Pokédx GUI verified at: {index_file} - web_bridge.py:39")
        return True

    async def initialize_agent(self):
        """Initialize agent_core.py following copilot instructions"""
        try:
            from agent_core import UltronAgent

            print("🤖 Initializing ULTRON Agent Core... - web_bridge.py:47")
            self.agent_instance = UltronAgent()

            # Initialize following project patterns
            await self.agent_instance.initialize()

            status = self.agent_instance.get_status()

            print("✅ Agent core initialized: - web_bridge.py:55")
            print(f"• Status: {status.get('running', 'unknown')} - web_bridge.py:56")
            print(f"• Current Model: {status.get('current_model', 'unknown')} - web_bridge.py:57")
            print(f"• NVIDIA Models: {len(status.get('nvidia_models', []))} - web_bridge.py:58")
            print(f"• Conversations: {status.get('conversations', 0)} - web_bridge.py:59")

            return True

        except Exception as e:
            print(f"❌ Agent initialization failed: {e} - web_bridge.py:64")
            print(f"❌ Full traceback: {traceback.format_exc()} - web_bridge.py:65")
            return False

    def start_web_server(self, port=5000):
        """Start simple web server for GUI"""
        import http.server
        import socketserver

        # Change to GUI directory
        os.chdir(self.gui_dir)

        try:
            handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", port), handler)

            def run_server():
                print(f"🌐 Web server running on http://localhost:{port} - web_bridge.py:81")
                httpd.serve_forever()

            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()

            self.server_running = True
            return f"http://localhost:{port}"

        except Exception as e:
            print(f"❌ Failed to start web server: {e} - web_bridge.py:91")
            return None

    async def bridge_connection(self):
        """Main bridge method - connects GUI to agent"""
        print("🌟 ULTRON Web Bridge  Connecting GUI to Agent - web_bridge.py:96")
        print("= - web_bridge.py:97" * 60)

        # Step 1: Verify GUI files
        if not self.verify_gui_exists():
            return False

        # Step 2: Initialize agent core
        if not await self.initialize_agent():
            return False

        # Step 3: Start web server
        url = self.start_web_server()
        if not url:
            return False

        # Step 4: Open browser
        import webbrowser
        time.sleep(1)
        webbrowser.open(url)

        print(f"\n🎮 ULTRON POKÉDEX GUI BRIDGE ACTIVE - web_bridge.py:117")
        print("= - web_bridge.py:118" * 60)
        print(f"🌐 GUI URL: {url} - web_bridge.py:119")
        print(f"📁 GUI Path: {self.gui_dir} - web_bridge.py:120")
        print(f"🤖 Agent Core: Running - web_bridge.py:121")
        print(f"🔧 Tools: {len(self.agent_instance.get_available_tools())} loaded - web_bridge.py:122")
        print("" * 60)
        print("Press Ctrl+C to disconnect - web_bridge.py:124")
        print("= - web_bridge.py:125" * 60)

        # Keep bridge active
        try:
            while self.server_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Disconnecting web bridge... - web_bridge.py:132")
            if self.agent_instance:
                await self.agent_instance.shutdown()
            print("✅ Bridge disconnected - web_bridge.py:135")

        return True

# Quick bridge connection
async def quick_bridge():
    """Quick bridge connection"""
    bridge = UltronWebBridge()
    await bridge.bridge_connection()

def main():
    """Main entry point"""
    try:
        asyncio.run(quick_bridge())
    except KeyboardInterrupt:
        print("\n👋 Bridge cancelled - web_bridge.py:150")
    except Exception as e:
        print(f"💥 Bridge failed: {e} - web_bridge.py:152")

if __name__ == "__main__":
    main()
