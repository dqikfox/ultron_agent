#!/usr/bin/env python3
"""
ULTRON Frontend Server - Serves the Pokédex GUI
Runs on localhost:5175 by default (override with --port or ULTRON_FRONTEND_PORT)
"""

import http.server
import socketserver
import os
import sys
import threading
import time
from pathlib import Path
import argparse

class UltronFrontendServer:
    def __init__(self, port=5175):
        self.port = port
        self.gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
        self.server = None
        self.running = False

    def start(self):
        """Start the frontend server"""
        try:
            if not self.gui_dir.exists():
                print(f"[ERROR] GUI directory not found: {self.gui_dir} - frontend_server.py:26")
                return False

            # Change to GUI directory
            original_dir = os.getcwd()
            os.chdir(self.gui_dir)

            # Create server
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            print(f"[FRONTEND] ULTRON Frontend Server starting... - frontend_server.py:37")
            print(f"[FRONTEND] Serving from: {self.gui_dir} - frontend_server.py:38")
            print(f"[FRONTEND] Frontend URL: http://localhost:{self.port} - frontend_server.py:39")
            print("[FRONTEND] - frontend_server.py:40" + "=" * 50)

            self.running = True
            self.server.serve_forever()

        except Exception as e:
            print(f"[ERROR] Frontend server failed: {e} - frontend_server.py:46")
            return False
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)

    def stop(self):
        """Stop the frontend server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[FRONTEND] Frontend server stopped - frontend_server.py:57")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the ULTRON frontend static server")
    default_port = int(os.getenv("ULTRON_FRONTEND_PORT", 5175))
    parser.add_argument("--port", type=int, default=default_port, help="Port to serve the frontend on")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = UltronFrontendServer(port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[FRONTEND] Shutting down frontend server... - frontend_server.py:64")
        server.stop()
