#!/usr/bin/env python3
"""
ULTRON Main Server - Serves the Pokéde            # Create server
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            self.logger.info(f"Server created successfully on port {self.port}")
            print(f"✅ ULTRON Main Interface Server starting...")
            print(f"✅ Serving Pokédx GUI from: {self.gui_dir}")
            print(f"✅ Main URL: http://localhost:{self.port}")
            print(f"✅ This serves the sophisticated Pokédx interface directly!")
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
                self.logger.debug(f"Restored original directory: {original_dir}")This replaces the simple HTTP server to serve the correct GUI directory
"""

import http.server
import socketserver
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

class UltronMainServer:
    def __init__(self, port=5000):
        self.port = port
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
            self.logger.info("Shutting down Main GUI Server...")
            self.server.shutdown()
            self.running = False
            self.logger.info("Main GUI Server stopped")
            print("✅ Main server stopped")

if __name__ == "__main__":
    # Create debug_logs directory if it doesn't exist
    os.makedirs('debug_logs', exist_ok=True)

    server = UltronMainServer()
    try:
        print(f"🚀 Starting ULTRON Main GUI Server on port {server.port}...")
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down main server...")
        server.stop()
