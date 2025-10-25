"""
ULTRON Avatar Server
Simple HTTP server for serving 3D avatar models and viewers
Bypasses CORS restrictions for local file loading
"""

import http.server
import socketserver
import os
import sys

# Configuration
PORT = 8090
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class AvatarHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with CORS headers for local development"""

    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Custom logging with green color for ULTRON theme
        print(f"[ULTRON Avatar Server] {args[0]} - {args[1]}")

def run_server():
    """Start the avatar server"""
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), AvatarHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🤖 ULTRON AVATAR SERVER")
        print("=" * 60)
        print(f"✅ Server started successfully!")
        print(f"📂 Serving directory: {DIRECTORY}")
        print(f"🌐 URL: http://localhost:{PORT}")
        print("")
        print("📄 Available viewers:")
        print(f"   • ULTRON Model:    http://localhost:{PORT}/ultron_avatar_viewer.html")
        print(f"   • Procedural:      http://localhost:{PORT}/ultron_avatar.html")
        print(f"   • Blender GLB:     http://localhost:{PORT}/ultron_avatar_blender.html")
        print(f"   • Gallery Index:   http://localhost:{PORT}/index.html")
        print("")
        print("⚠️  Press Ctrl+C to stop the server")
        print("=" * 60)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            print("=" * 60)
            sys.exit(0)

if __name__ == "__main__":
    run_server()
