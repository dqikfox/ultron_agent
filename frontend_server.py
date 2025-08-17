#!/usr/bin/env python3
"""
ULTRON Frontend Server - Serves the Pokédex GUI
Runs on localhost:5173 to match your requirements
"""

import http.server
import socketserver
import os
import sys
import threading
import time
from pathlib import Path

class UltronFrontendServer:
    def __init__(self, port=5173):
        self.port = port
        self.gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
        self.server = None
        self.running = False

    def start(self):
        """Start the frontend server"""
        try:
            if not self.gui_dir.exists():
                print(f"❌ GUI directory not found: {self.gui_dir}")
                return False

            # Change to GUI directory
            original_dir = os.getcwd()
            os.chdir(self.gui_dir)

            # Create server
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            print(f"🎮 ULTRON Frontend Server starting...")
            print(f"📁 Serving from: {self.gui_dir}")
            print(f"🌐 Frontend URL: http://localhost:{self.port}")
            print("=" * 60)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f"❌ Frontend server failed: {e}")
            return False
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)

    def stop(self):
        """Stop the frontend server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("🛑 Frontend server stopped")

if __name__ == "__main__":
    server = UltronFrontendServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down frontend server...")
        server.stop()
