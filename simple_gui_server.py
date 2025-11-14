#!/usr/bin/env python3
"""Simple HTTP server to serve the ULTRON GUI for testing"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

# Change to the GUI directory
gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
os.chdir(gui_dir)

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Serving ULTRON GUI at http://localhost:{PORT}")
        print(f"📁 Directory: {gui_dir}")
        print("Press Ctrl+C to stop")

        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")
