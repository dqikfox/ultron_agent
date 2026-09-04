#!/usr/bin/env python3
"""
Simple HTTP server for Pokédex GUI on port 8081
"""

import http.server
import socketserver
import os
import sys

# Change to the web directory
web_dir = os.path.join(os.path.dirname(__file__), 'gui', 'ultron_enhanced', 'web')
if os.path.exists(web_dir):
    os.chdir(web_dir)
    print(f"Serving from: {web_dir}")
else:
    print(f"Web directory not found: {web_dir}")
    sys.exit(1)

# Set up the server
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", 8081), Handler) as httpd:
    print("Pokédex GUI server running on port 8081")
    print("Open: http://localhost:8081")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.shutdown()
