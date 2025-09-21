#!/usr/bin/env python3
"""
ULTRON Main Server - Serves the Pokédex GUI with automatic port fallback
"""

import http.server
import socketserver
import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

class UltronMainServer:
    def __init__(self, port=None):
        # Port configuration with fallback
        self.port = port or int(os.getenv('ULTRON_GUI_PORT', '5000'))
        self.gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
        self.server = None
        self.running = False

        # Setup debug logging
        self.setup_debug_logging()

    def setup_debug_logging(self):
        """Setup comprehensive debug logging"""
        debug_mode = os.getenv('ULTRON_DEBUG', '0') == '1'
        log_level = logging.DEBUG if debug_mode else logging.INFO

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('debug_logs/main_gui_debug.log', mode='a')
            ]
        )
        self.logger = logging.getLogger('MainGUIServer')

        if debug_mode:
            self.logger.debug("DEBUG MODE ENABLED for Main GUI Server")

        self.logger.info(f"Main GUI Server initializing on port {self.port}")
        self.logger.info(f"Target GUI directory: {self.gui_dir}")

    def find_available_port(self, start_port):
        """Find an available port starting from the given port"""
        import socket

        port = start_port
        max_attempts = 10  # Try up to 10 ports

        for attempt in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                self.logger.warning(f"Port {port} is in use, trying next port...")
                port += 1

        raise OSError(f"No available ports found starting from {start_port}")

    def start(self):
        """Start the main server serving the GUI directory"""
        try:
            self.logger.info("Starting Main GUI Server...")

            if not self.gui_dir.exists():
                error_msg = f"GUI directory not found: {self.gui_dir}"
                self.logger.error(error_msg)
                print(f"❌ {error_msg}")
                return False

            self.logger.info(f"GUI directory found: {self.gui_dir}")
            self.logger.debug(f"GUI directory contents: {list(self.gui_dir.iterdir())}")

            # Change to GUI directory to serve it properly
            original_dir = os.getcwd()
            self.logger.debug(f"Original directory: {original_dir}")
            os.chdir(self.gui_dir)
            self.logger.debug(f"Changed to GUI directory: {self.gui_dir}")

            # Try to find an available port
            try:
                available_port = self.find_available_port(self.port)
                if available_port != self.port:
                    self.logger.warning(f"Port {self.port} in use, using port {available_port} instead")
                    self.port = available_port
            except OSError as port_error:
                error_msg = f"Could not find available port: {port_error}"
                self.logger.error(error_msg)
                print(f"❌ {error_msg}")
                return False

            # Create server with available port
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            self.logger.info(f"Server created successfully on port {self.port}")
            print(f"✅ ULTRON Main Interface Server starting...")
            print(f"✅ Serving Pokédex GUI from: {self.gui_dir}")
            print(f"✅ Main URL: http://localhost:{self.port}")
            print(f"✅ This serves the sophisticated Pokédex interface directly!")
            print("=" * 60)

            self.logger.info("Server bound to port successfully")
            self.logger.info("Starting to serve requests...")

            self.running = True
            self.server.serve_forever()

        except OSError as e:
            if e.errno == 10048:  # Port already in use
                error_msg = f"Port {self.port} is already in use"
                self.logger.error(error_msg)
                print(f"❌ {error_msg}")
            else:
                error_msg = f"OS Error: {e}"
                self.logger.error(error_msg)
                print(f"❌ {error_msg}")
            return False
        except Exception as e:
            error_msg = f"Main server failed: {e}"
            self.logger.error(error_msg, exc_info=True)
            print(f"❌ {error_msg}")
            return False
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)
                self.logger.debug(f"Restored original directory: {original_dir}")

    def stop(self):
        """Stop the main server"""
        if self.server:
            self.logger.info("Shutting down Main GUI Server...")
            self.server.shutdown()
            self.running = False
            self.logger.info("Main GUI Server stopped")
            print("✅ Main server stopped")

if __name__ == "__main__":
    # Create debug_logs directory if it doesn't exist
    os.makedirs('debug_logs', exist_ok=True)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ULTRON Main GUI Server')
    parser.add_argument('--port', type=int, help='Port to run the server on')
    args = parser.parse_args()

    server = UltronMainServer(port=args.port)
    try:
        print(f"🚀 Starting ULTRON Main GUI Server on port {server.port}...")
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down main server...")
        server.stop()
