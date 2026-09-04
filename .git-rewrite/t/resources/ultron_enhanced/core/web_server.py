"""
ULTRON Enhanced - Web Server Module
Built-in web server for Pokedex interface with WebSocket support
"""

import os
import sys
import json
import time
import logging
import threading
import socketserver
import http.server
from pathlib import Path
from typing import Dict, List, Optional, Any
import urllib.parse
import mimetypes

try:
    import websockets
    import asyncio
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logging.warning("WebSockets not available - real-time features disabled")

class UltronWebServer:
    """Enhanced web server for ULTRON Pokedex interface"""
    
    def __init__(self, config: Dict, ultron_core=None):
        self.config = config
        self.ultron_core = ultron_core
        self.port = config.get('web_port', 3000)
        self.web_dir = Path(config.get('web_dir', './web'))
        self.server = None
        self.server_thread = None
        self.websocket_server = None
        self.websocket_clients = set()
        self.is_running = False
        
        # API endpoints
        self.api_endpoints = {
            '/api/status': self._handle_status,
            '/api/command': self._handle_command,
            '/api/system': self._handle_system,
            '/api/vision': self._handle_vision,
            '/api/voice': self._handle_voice,
            '/api/config': self._handle_config,
            '/api/tasks': self._handle_tasks,
            '/api/files': self._handle_files
        }
        
        logging.info(f"Web server initialized on port {self.port}")
    
    def start(self) -> bool:
        """Start the web server"""
        try:
            if self.is_running:
                logging.warning("Web server already running")
                return True
            
            # Start HTTP server
            self._start_http_server()
            
            # Start WebSocket server if available
            if WEBSOCKETS_AVAILABLE:
                self._start_websocket_server()
            
            self.is_running = True
            logging.info(f"Web server started on http://localhost:{self.port}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start web server: {e}")
            return False
    
    def stop(self):
        """Stop the web server"""
        try:
            self.is_running = False
            
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.websocket_server:
                self.websocket_server.close()
            
            logging.info("Web server stopped")
            
        except Exception as e:
            logging.error(f"Error stopping web server: {e}")
    
    def _start_http_server(self):
        """Start HTTP server thread"""
        handler = UltronHTTPHandler
        handler.web_server = self
        
        self.server = socketserver.TCPServer(("", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
    
    def _start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        if not WEBSOCKETS_AVAILABLE:
            return
        
        async def websocket_handler(websocket, path):
            """Handle WebSocket connections"""
            self.websocket_clients.add(websocket)
            logging.info(f"WebSocket client connected: {websocket.remote_address}")
            
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_clients.remove(websocket)
                logging.info(f"WebSocket client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server in separate thread
        def start_ws_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            start_server = websockets.serve(
                websocket_handler, 
                "localhost", 
                self.port + 1
            )
            
            self.websocket_server = loop.run_until_complete(start_server)
            loop.run_forever()
        
        ws_thread = threading.Thread(target=start_ws_server, daemon=True)
        ws_thread.start()
        
        logging.info(f"WebSocket server started on ws://localhost:{self.port + 1}")
    
    def broadcast_message(self, message: Dict):
        """Broadcast message to all WebSocket clients"""
        if not WEBSOCKETS_AVAILABLE or not self.websocket_clients:
            return
        
        message_str = json.dumps(message)
        
        async def send_to_clients():
            if self.websocket_clients:
                await asyncio.gather(
                    *[client.send(message_str) for client in self.websocket_clients],
                    return_exceptions=True
                )
        
        # Schedule the coroutine
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(send_to_clients())
        except:
            pass  # No loop running
    
    def handle_api_request(self, path: str, method: str, data: Dict = None) -> Dict:
        """Handle API requests"""
        try:
            if path in self.api_endpoints:
                return self.api_endpoints[path](method, data or {})
            else:
                return {
                    "success": False,
                    "error": "API endpoint not found",
                    "code": 404
                }
        except Exception as e:
            logging.error(f"API request error: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": 500
            }
    
    def _handle_status(self, method: str, data: Dict) -> Dict:
        """Handle status API requests"""
        if method == "GET":
            status = {
                "server_running": self.is_running,
                "websocket_available": WEBSOCKETS_AVAILABLE,
                "connected_clients": len(self.websocket_clients),
                "ultron_core_available": self.ultron_core is not None,
                "timestamp": time.time()
            }
            
            if self.ultron_core and hasattr(self.ultron_core, 'get_status'):
                status.update(self.ultron_core.get_status())
            
            return {
                "success": True,
                "status": status
            }
        else:
            return {"success": False, "error": "Method not allowed", "code": 405}
    
    def _handle_command(self, method: str, data: Dict) -> Dict:
        """Handle command API requests"""
        if method == "POST":
            command = data.get('command', '')
            command_type = data.get('type', 'text')
            
            if not command:
                return {"success": False, "error": "Command required"}
            
            # Process command through ULTRON core
            if self.ultron_core and hasattr(self.ultron_core, 'process_command'):
                result = self.ultron_core.process_command(command, command_type)
            else:
                # Fallback response
                result = {
                    "success": True,
                    "response": f"Command received: {command}",
                    "command": command,
                    "type": command_type
                }
            
            # Broadcast to WebSocket clients
            self.broadcast_message({
                "type": "command_result",
                "data": result
            })
            
            return result
        else:
            return {"success": False, "error": "Method not allowed", "code": 405}
    
    def _handle_system(self, method: str, data: Dict) -> Dict:
        """Handle system API requests"""
        if method == "GET":
            action = data.get('action', 'info')
            
            if self.ultron_core and hasattr(self.ultron_core, 'get_system_info'):
                return self.ultron_core.get_system_info(action)
            else:
                # Fallback system info
                import psutil
                return {
                    "success": True,
                    "system_info": {
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
                    }
                }
        elif method == "POST":
            action = data.get('action')
            
            if self.ultron_core and hasattr(self.ultron_core, 'execute_system_action'):
                return self.ultron_core.execute_system_action(action, data)
            else:
                return {"success": False, "error": "System control not available"}
        else:
            return {"success": False, "error": "Method not allowed", "code": 405}
    
    def _handle_vision(self, method: str, data: Dict) -> Dict:
        """Handle vision API requests"""
        if method == "POST":
            action = data.get('action', 'capture')
            
            if self.ultron_core and hasattr(self.ultron_core, 'vision_system'):
                vision = self.ultron_core.vision_system
                
                if action == 'capture':
                    return vision.capture_screen()
                elif action == 'analyze':
                    analysis_type = data.get('analysis_type', 'full')
                    return vision.analyze_screen(analysis_type)
                elif action == 'history':
                    limit = data.get('limit', 10)
                    return vision.get_analysis_history(limit)
                else:
                    return {"success": False, "error": "Unknown vision action"}
            else:
                return {"success": False, "error": "Vision system not available"}
        else:
            return {"success": False, "error": "Method not allowed", "code": 405}
    
    def _handle_voice(self, method: str, data: Dict) -> Dict:
        """Handle voice API requests"""
        if method == "POST":
            action = data.get('action')
            
            if self.ultron_core and hasattr(self.ultron_core, 'voice_processor'):
                voice = self.ultron_core.voice_processor
                
                if action == 'start_listening':
                    voice.start_listening()
                    return {"success": True, "message": "Voice recognition started"}
                elif action == 'stop_listening':
                    voice.stop_listening()
                    return {"success": True, "message": "Voice recognition stopped"}
                elif action == 'speak':
                    text = data.get('text', '')
                    if text:
                        voice.speak(text)
                        return {"success": True, "message": "Speech initiated"}
                    else:
                        return {"success": False, "error": "Text required"}
                elif action == 'test_microphone':
                    return voice.test_microphone()
                elif action == 'get_voices':
                    return voice.get_voice_info()
                else:
                    return {"success": False, "error": "Unknown voice action"}
            else:
                return {"success": False, "error": "Voice system not available"}
        else:
            return {"success": False, "error": "Method not allowed", "code": 405}
    
    def _handle_config(self, method: str, data: Dict) -> Dict:
        """Handle configuration API requests"""
        if method == "GET":
            # Return safe configuration (no sensitive data)
            safe_config = {
                "theme": self.config.get("theme", "red"),
                "voice": self.config.get("voice", "male"),
                "web_port": self.config.get("web_port", 3000),
                "vision_enabled": self.config.get("vision_enabled", True),
                "pokedex_mode": self.config.get("pokedex_mode", True)
            }
            return {"success": True, "config": safe_config}
        
        elif method == "POST":
            # Update configuration
            updates = data.get('updates', {})
            
            # Apply safe updates
            safe_keys = ["theme", "voice", "vision_enabled", "pokedex_mode"]
            for key in safe_keys:
                if key in updates:
                    self.config[key] = updates[key]
            
            # Save configuration if possible
            if self.ultron_core and hasattr(self.ultron_core, 'save_config'):
                self.ultron_core.save_config()
            
            return {"success": True, "message": "Configuration updated"}
        else:
            return {"success": False, "error": "Method not allowed", "code": 405}
    
    def _handle_tasks(self, method: str, data: Dict) -> Dict:
        """Handle task management API requests"""
        if self.ultron_core and hasattr(self.ultron_core, 'task_manager'):
            task_manager = self.ultron_core.task_manager
            
            if method == "GET":
                return task_manager.get_tasks()
            elif method == "POST":
                action = data.get('action')
                if action == 'create':
                    return task_manager.create_task(data)
                elif action == 'execute':
                    return task_manager.execute_task(data.get('task_id'))
                elif action == 'delete':
                    return task_manager.delete_task(data.get('task_id'))
                else:
                    return {"success": False, "error": "Unknown task action"}
            else:
                return {"success": False, "error": "Method not allowed", "code": 405}
        else:
            return {"success": False, "error": "Task manager not available"}
    
    def _handle_files(self, method: str, data: Dict) -> Dict:
        """Handle file management API requests"""
        if self.ultron_core and hasattr(self.ultron_core, 'file_manager'):
            file_manager = self.ultron_core.file_manager
            
            if method == "GET":
                path = data.get('path', '.')
                return file_manager.list_files(path)
            elif method == "POST":
                action = data.get('action')
                return file_manager.execute_command({
                    "action": action,
                    **data
                })
            else:
                return {"success": False, "error": "Method not allowed", "code": 405}
        else:
            return {"success": False, "error": "File manager not available"}

class UltronHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for ULTRON web interface"""
    
    web_server = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(self.web_server.web_dir), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle API requests
        if path.startswith('/api/'):
            self._handle_api_request('GET', path, parsed_path.query)
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle API requests
        if path.startswith('/api/'):
            # Read POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
            
            self._handle_api_request('POST', path, data)
        else:
            self._send_error(404, "Not Found")
    
    def _handle_api_request(self, method: str, path: str, data):
        """Handle API requests"""
        try:
            # Parse query parameters for GET requests
            if method == 'GET' and isinstance(data, str):
                query_params = urllib.parse.parse_qs(data)
                data = {k: v[0] if v else '' for k, v in query_params.items()}
            
            # Process through web server
            result = self.web_server.handle_api_request(path, method, data)
            
            # Send response
            self._send_json_response(result)
            
        except Exception as e:
            logging.error(f"API request error: {e}")
            self._send_json_response({
                "success": False,
                "error": str(e),
                "code": 500
            })
    
    def _send_json_response(self, data: Dict):
        """Send JSON response"""
        try:
            response_data = json.dumps(data, indent=2)
            
            self.send_response(data.get('code', 200))
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            logging.error(f"Error sending JSON response: {e}")
    
    def _send_error(self, code: int, message: str):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        error_data = {
            "success": False,
            "error": message,
            "code": code
        }
        
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use Python logging"""
        logging.info(f"Web request: {format % args}")

class WebServerUtils:
    """Utility functions for web server"""
    
    @staticmethod
    def get_local_ip():
        """Get local IP address"""
        import socket
        try:
            # Connect to a remote server to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def is_port_available(port: int) -> bool:
        """Check if port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except socket.error:
                return False
    
    @staticmethod
    def find_available_port(start_port: int = 3000, max_attempts: int = 100) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            if WebServerUtils.is_port_available(port):
                return port
        return None
    
    @staticmethod
    def create_ssl_context(cert_file: str, key_file: str):
        """Create SSL context for HTTPS"""
        try:
            import ssl
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file, key_file)
            return context
        except Exception as e:
            logging.error(f"SSL context creation failed: {e}")
            return None
    
    @staticmethod
    def generate_self_signed_cert(cert_file: str, key_file: str):
        """Generate self-signed certificate for HTTPS"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            # Generate private key
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ULTRON"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                ]),
                critical=False,
            ).sign(key, hashes.SHA256(), default_backend())
            
            # Write certificate and key to files
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(key_file, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            return True
            
        except ImportError:
            logging.error("Cryptography library not available for SSL certificate generation")
            return False
        except Exception as e:
            logging.error(f"Certificate generation failed: {e}")
            return False
