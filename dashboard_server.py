#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Main Dashboard Server
Serves the main system dashboard on localhost:5000
"""

import http.server
import socketserver
import json
import subprocess
import os
import threading
import time
from pathlib import Path

class UltronDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_dashboard()
        elif self.path == '/api/gpu-stats':
            self.serve_gpu_stats()
        elif self.path == '/api/system-status':
            self.serve_system_status()
        else:
            super().do_GET()

    def serve_dashboard(self):
        """Serve the main dashboard"""
        try:
            with open('dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, "Dashboard not found")

    def serve_gpu_stats(self):
        """Serve live GPU statistics"""
        try:
            # Get NVIDIA GPU stats
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=utilization.gpu,utilization.memory,temperature.gpu,power.draw,memory.used,memory.total',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                stats = result.stdout.strip().split(', ')
                gpu_data = {
                    'utilization': int(stats[0]),
                    'memory_utilization': int(stats[1]), 
                    'temperature': int(stats[2]),
                    'power_draw': float(stats[3]),
                    'memory_used': int(stats[4]),
                    'memory_total': int(stats[5]),
                    'timestamp': time.time()
                }
            else:
                # Fallback data if nvidia-smi fails
                gpu_data = {
                    'utilization': 36,
                    'memory_utilization': 3,
                    'temperature': 54,
                    'power_draw': 174.0,
                    'memory_used': 377,
                    'memory_total': 4096,
                    'timestamp': time.time(),
                    'error': 'nvidia-smi unavailable'
                }
                
        except Exception as e:
            gpu_data = {
                'error': str(e),
                'timestamp': time.time()
            }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(gpu_data).encode('utf-8'))

    def serve_system_status(self):
        """Serve system status information"""
        status = {
            'services': {
                'dashboard': {'port': 5000, 'status': 'online'},
                'chat_engine': {'port': 5173, 'status': 'unknown'},
                'gui_api': {'port': 3000, 'status': 'unknown'},
                'agent_core': {'port': 8000, 'status': 'unknown'},
                'web_bridge': {'status': 'unknown'}
            },
            'nvidia_models': [
                'llama-4-maverick',
                'gpt-oss-120b', 
                'llama-3.3-70b'
            ],
            'active_model': 'llama-4-maverick',
            'timestamp': time.time()
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"🌐 [{timestamp}] DASHBOARD: {format % args}")

def start_dashboard_server(port=5000):
    """Start the ULTRON dashboard server"""
    print(f"🚀 Starting ULTRON Dashboard Server...")
    print(f"📊 Main Dashboard: http://localhost:{port}")
    print(f"🎮 GPU Stats API: http://localhost:{port}/api/gpu-stats")
    print(f"⚙️ System Status API: http://localhost:{port}/api/system-status")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer(("", port), UltronDashboardHandler) as httpd:
            print(f"✅ ULTRON Dashboard serving at http://localhost:{port}")
            print("🔴 Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 ULTRON Dashboard server stopped")
    except Exception as e:
        print(f"❌ Dashboard server error: {e}")

if __name__ == "__main__":
    start_dashboard_server()
