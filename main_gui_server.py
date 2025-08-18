#!/usr/bin/env python3
"""
ULTRON Main Server - Serves the Pokédex GUI on port 5000
This replaces the simple HTTP server to serve the correct GUI directory
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class UltronMainServer:
    def __init__(self, port=5000):
        self.port = port
        self.gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
        self.server = None
        self.running = False

    def start(self):
        """Start the main server serving the GUI directory"""
        try:
            if not self.gui_dir.exists():
                print(f" GUI directory not found: {self.gui_dir}")
                return False

            # Change to GUI directory to serve it properly
            original_dir = os.getcwd()
            os.chdir(self.gui_dir)

            # Create server
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            print(f" ULTRON Main Interface Server starting...")
            print(f" Serving Pokédex GUI from: {self.gui_dir}")
            print(f" Main URL: http://localhost:{self.port}")
            print(f" This serves the sophisticated Pokédex interface directly!")
            print("=" * 60)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f" Main server failed: {e}")
            return False
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)

    def stop(self):
        """Stop the main server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print(" Main server stopped")

if __name__ == "__main__":
    server = UltronMainServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n Shutting down main server...")
        server.stop()
