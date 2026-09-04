#!/usr/bin/env python3
"""
ULTRON MASTER GUI Server v5.0
Serves the supreme control center
"""

import asyncio
import http.server
import socketserver
import webbrowser
from pathlib import Path
import threading
import json
from datetime import datetime

PORT = 9000

class MasterGUIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for MASTER GUI"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/MASTER_GUI.html'
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                'ultron_version': '5.0 SUPREME',
                'status': 'EVOLVED',
                'phi': 0.847,
                'agents': 10,
                'timestamp': datetime.now().isoformat(),
                'systems': {
                    'v3.0': {'status': 'active', 'port': 3000},
                    'v5.0': {'status': 'active', 'port': 7777},
                    'master': {'status': 'active', 'port': 9000}
                }
            }
            
            self.wfile.write(json.dumps(status).encode())
            return
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress logs
        pass

def start_master_gui():
    """Start the Master GUI server"""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ULTRON MASTER GUI v5.0 SUPREME                                ║
║                                                                  ║
║   Starting server on http://localhost:{PORT}                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    with socketserver.TCPServer(("", PORT), MasterGUIHandler) as httpd:
        print(f"[Master GUI] Running at http://localhost:{PORT}")
        print("[Master GUI] Opening browser...")
        
        # Open browser
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Master GUI] Shutting down...")

if __name__ == "__main__":
    start_master_gui()
