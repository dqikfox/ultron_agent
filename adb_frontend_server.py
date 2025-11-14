#!/usr/bin/env python3
"""
ADB Frontend Server - Serves ADB Console on port 8081
Provides the web interface for ADB Manager

PURPOSE:
    - Serves gui/ultron_enhanced/web/adb.html on http://localhost:8081
    - Bridges frontend (JavaScript) with backend (Socket.IO) communication
    - Handles CORS for cross-origin Socket.IO connections
    - SEPARATE from main GUI (which uses web_gui_server.py on port 8080)

INTEGRATION:
    - Started manually OR via separate terminal
    - Works with adb_backend_enhanced.py (port 5003)
    - Frontend connects via Socket.IO to localhost:5003
    - All requests to port 8081 routed to adb.html

CRITICAL: Port 8081 reserved for ADB console
         Port 8080 reserved for main ULTRON GUI (web_gui_server.py)
         Do NOT change port without updating documentation
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP handler with CORS headers for cross-origin requests

    CORS Handling:
        - Allows all origins (*) for Socket.IO client connections
        - Enables real-time communication between frontend and backend
        - Prevents 'No Access-Control-Allow-Origin header' errors
    """

    def end_headers(self):
        """
        Add CORS headers to all HTTP responses

        Headers Added:
            - Access-Control-Allow-Origin: * (allow all origins)
            - Access-Control-Allow-Methods: * (allow all HTTP methods)
            - Access-Control-Allow-Headers: * (allow all headers)
            - Cache-Control: no-store (prevent browser caching)
            - Content-Type: text/html (specify content type)

        Reference:
            https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
        """
        # Allow frontend (on any origin) to communicate with backend
        self.send_header('Access-Control-Allow-Origin', '*')
        # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
        self.send_header('Access-Control-Allow-Methods', '*')
        # Allow all custom headers from client
        self.send_header('Access-Control-Allow-Headers', '*')
        # Prevent browser caching to ensure fresh content
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        # Explicitly set content type as HTML
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        # Call parent class method to finish headers
        super().end_headers()

    def do_GET(self):
        """
        Handle HTTP GET requests

        Routing:
            GET / → serve gui/ultron_enhanced/web/adb.html
            GET /adb.html → serve gui/ultron_enhanced/web/adb.html
            GET /* → default HTTP server behavior

        Purpose:
            - Route all requests to adb.html (Single Page Application)
            - Ensure Socket.IO client loads correctly
            - Prevent 404 errors on frontend navigation
        """
        # Route root path and /adb.html to the HTML file
        # This allows:
        #   - http://localhost:8080/ → loads adb.html
        #   - http://localhost:8080/adb.html → loads adb.html
        if self.path == '/' or self.path == '/adb.html':
            # Construct full path to HTML file in project directory
            # __file__ = current script location
            # Relative path: gui/ultron_enhanced/web/adb.html
            html_path = os.path.join(
                os.path.dirname(__file__),
                'gui/ultron_enhanced/web/adb.html'
            )

            # Check if file exists before attempting to serve
            if os.path.exists(html_path):
                try:
                    # Read HTML file content with UTF-8 encoding
                    with open(html_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Send HTTP 200 OK response
                    self.send_response(200)
                    # Specify HTML content type for browser rendering
                    self.send_header('Content-Type',
                                     'text/html; charset=utf-8')
                    # Add CORS header for Socket.IO communication
                    self.send_header('Access-Control-Allow-Origin', '*')
                    # Send all headers to client
                    self.end_headers()
                    # Write HTML content to response body
                    self.wfile.write(content.encode('utf-8'))
                    return
                except Exception as e:
                    # Log error if file read fails
                    # Common causes: permission denied, encoding error
                    print(f"[ERROR] Failed to read HTML file: {e}")
                    # Send HTTP 500 Internal Server Error
                    self.send_response(500)
                    self.end_headers()
                    return
            else:
                # Log error if HTML file not found
                # Debug: Check if path is correct in project structure
                print(f"[ERROR] HTML file not found at {html_path}")
                # Send HTTP 404 Not Found response
                self.send_response(404)
                self.end_headers()
                # Send error message to client
                self.wfile.write(b"HTML file not found")
                return

        # For other paths, use parent class default behavior
        # This allows serving static files if needed
        # Example: /js/app.js, /css/styles.css (if in current dir)
        super().do_GET()

    def do_OPTIONS(self):
        """
        Handle HTTP OPTIONS requests (CORS preflight)

        CORS Preflight:
            - Browser sends OPTIONS before POST requests
            - Used to verify CORS headers before actual request
            - Must return 200 with CORS headers

        Socket.IO Usage:
            - Socket.IO uses OPTIONS during connection negotiation
            - Must respond with proper CORS headers
            - Required for successful WebSocket upgrade
        """
        # Send HTTP 200 OK for preflight request
        self.send_response(200)
        # Allow all origins to connect
        # This enables frontend to connect from any domain
        self.send_header('Access-Control-Allow-Origin', '*')
        # Allow GET, POST, OPTIONS methods
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, OPTIONS')
        # Allow all custom headers in requests
        self.send_header('Access-Control-Allow-Headers', '*')
        # Send headers to complete response
        self.end_headers()

    def log_message(self, format, *args):
        """
        Override default HTTP logging

        Standard logging format: [IP] GET /path HTTP/1.1
        Custom format: Shows client IP address and request details

        Helps with:
            - Debugging connection issues
            - Monitoring server access
            - Identifying frontend requests
        """
        # Format: [IP] log message
        # Example: [127.0.0.1] GET /adb.html HTTP/1.1 200 -
        print(f"[{self.client_address[0]}] {format % args}")


if __name__ == '__main__':
    """
    Main entry point for ADB Frontend Server

    EXECUTION:
        - Can be run manually: python adb_frontend_server.py
        - NOT integrated into run.bat (serves on separate port)
        - Start manually if ADB console needed

    PORTS & CONNECTIVITY:
        - Listens on: http://127.0.0.1:8081
        - Backend on: http://127.0.0.1:5003
        - Socket.IO connects frontend to backend

    ERROR HANDLING:
        - KeyboardInterrupt (Ctrl+C): Graceful shutdown
        - Exception: Log error and exit with code 1

    DEPENDENCIES:
        - gui/ultron_enhanced/web/adb.html must exist
        - adb_backend_enhanced.py must be running on port 5003
        - Port 8081 must be available (not in use)

    TROUBLESHOOTING:
        - Port 8081 in use: Kill process with:
          netstat -ano | findstr 8081
        - HTML not found: Verify file path is correct
        - CORS errors: Check CORS headers in do_GET()
        - Socket.IO disconnect: Verify backend is running
    """
    try:
        # Server configuration - ADB Console on separate port
        HOST = '127.0.0.1'  # Localhost only (change to '0.0.0.0' for LAN)
        PORT = 8081         # ADB console port (separate from main GUI on 8080)

        # Startup messages for troubleshooting
        print("[+] ADB Frontend Server Starting...")
        print(f"[+] Serving on: http://{HOST}:{PORT}")
        print("[+] Backend: http://localhost:5003")  # Reference for debugging
        print("[+] Press Ctrl+C to stop\n")

        # Create HTTP server with custom request handler
        # - HTTPServer: Standard Python HTTP server
        # - CORSRequestHandler: Our custom handler with CORS support
        server = HTTPServer((HOST, PORT), CORSRequestHandler)

        # Start server and listen for incoming connections
        # - serve_forever(): Blocks until KeyboardInterrupt or error
        # - Handles one request at a time (sufficient for our use)
        server.serve_forever()

    except KeyboardInterrupt:
        # User pressed Ctrl+C to stop server
        # Normal shutdown behavior
        print("\n[!] Server shutdown by user")
        sys.exit(0)
    except Exception as e:
        # Catch any other errors (port in use, permission denied, etc.)
        # Log error and exit with non-zero code (indicates error)
        print(f"[!] Error: {e}")
        sys.exit(1)
