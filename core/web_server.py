"""
ULTRON Web Server
================

Built-in web server with real-time API endpoints, Pokédx-style interface,
and WebSocket support for live system monitoring and control.
"""

import os
import sys
import asyncio
import threading
import logging
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Web server imports
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_socketio import SocketIO, emit, join_room, leave_room
    import eventlet
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Web server not available. Install with: pip install flask flask-socketio eventlet")

# CORS support
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False


class UltronWebServer:
    """Advanced web server with Pokédx-style interface and real-time APIs."""
    
    def __init__(self, agent_ref=None, host: str = "localhost", port: int = 8080):
        """Initialize web server."""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask and related dependencies required for web server")
        
        self.agent_ref = agent_ref
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # Flask app setup
        self.app = Flask(__name__, 
                        template_folder='web',
                        static_folder='web/assets')
        self.app.secret_key = os.urandom(24)
        
        # Enable CORS if available
        if CORS_AVAILABLE:
            CORS(self.app)
        
        # SocketIO for real-time communication
        self.socketio = SocketIO(self.app, 
                               cors_allowed_origins="*",
                               async_mode='eventlet')
        
        # Server state
        self.running = False
        self.server_thread = None
        self.connected_clients = set()
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
        
        self.logger.info(f"Web server initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Serve main Pokédx interface."""
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status."""
            try:
                if self.agent_ref:
                    status = {
                        'agent_status': self.agent_ref.status,
                        'timestamp': datetime.now().isoformat(),
                        'connected_clients': len(self.connected_clients)
                    }
                    
                    # Get additional system info if available
                    if hasattr(self.agent_ref, 'get_system_status'):
                        status.update(self.agent_ref.get_system_status())
                else:
                    status = {
                        'agent_status': 'disconnected',
                        'timestamp': datetime.now().isoformat(),
                        'connected_clients': len(self.connected_clients)
                    }
                
                return jsonify(status)
                
            except Exception as e:
                self.logger.error(f"Status API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chat', methods=['POST'])
        def api_chat():
            """Handle chat messages."""
            try:
                data = request.get_json()
                if not data or 'message' not in data:
                    return jsonify({'error': 'Message required'}), 400
                
                message = data['message']
                model = data.get('model', 'default')
                
                # Process message through agent if available
                if self.agent_ref and hasattr(self.agent_ref, 'process_message'):
                    response = self.agent_ref.process_message(message, model=model)
                else:
                    response = {
                        'response': f"Echo: {message}",
                        'model': model,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Broadcast to connected clients
                self.socketio.emit('chat_response', response, broadcast=True)
                
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Chat API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/screenshot', methods=['POST'])
        def api_screenshot():
            """Take screenshot."""
            try:
                data = request.get_json() or {}
                region = data.get('region')  # [x, y, width, height]
                save_file = data.get('save_file')
                
                if self.agent_ref and hasattr(self.agent_ref, 'vision'):
                    screenshot_path = self.agent_ref.vision.capture_screen(
                        region=tuple(region) if region else None,
                        save_file=save_file
                    )
                    
                    if screenshot_path:
                        return jsonify({
                            'success': True,
                            'screenshot_path': screenshot_path,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        return jsonify({'error': 'Screenshot failed'}), 500
                else:
                    return jsonify({'error': 'Vision system not available'}), 503
                
            except Exception as e:
                self.logger.error(f"Screenshot API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ocr', methods=['POST'])
        def api_ocr():
            """Perform OCR on screen or image."""
            try:
                data = request.get_json() or {}
                region = data.get('region')
                image_path = data.get('image_path')
                language = data.get('language', 'eng')
                
                if self.agent_ref and hasattr(self.agent_ref, 'vision'):
                    if image_path:
                        text = self.agent_ref.vision.extract_text(image_path, language=language)
                    else:
                        text = self.agent_ref.vision.extract_text_from_screen(
                            region=tuple(region) if region else None,
                            language=language
                        )
                    
                    return jsonify({
                        'text': text,
                        'success': text is not None,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({'error': 'Vision system not available'}), 503
                
            except Exception as e:
                self.logger.error(f"OCR API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automation', methods=['POST'])
        def api_automation():
            """Execute automation commands."""
            try:
                data = request.get_json()
                if not data or 'action' not in data:
                    return jsonify({'error': 'Action required'}), 400
                
                action = data['action']
                params = data.get('params', {})
                
                if self.agent_ref and hasattr(self.agent_ref, 'automation'):
                    result = self._execute_automation_action(action, params)
                    return jsonify(result)
                else:
                    return jsonify({'error': 'Automation system not available'}), 503
                
            except Exception as e:
                self.logger.error(f"Automation API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/voice', methods=['POST'])
        def api_voice():
            """Voice control endpoints."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Request data required'}), 400
                
                command = data.get('command')
                text = data.get('text')
                
                if self.agent_ref and hasattr(self.agent_ref, 'voice'):
                    if command == 'speak' and text:
                        self.agent_ref.voice.speak(text)
                        return jsonify({'success': True, 'action': 'speak'})
                    
                    elif command == 'listen':
                        result = self.agent_ref.voice.listen_once(
                            timeout=data.get('timeout', 5)
                        )
                        return jsonify({
                            'text': result,
                            'success': result is not None
                        })
                    
                    elif command == 'status':
                        status = self.agent_ref.voice.get_status()
                        return jsonify(status)
                    
                    else:
                        return jsonify({'error': 'Unknown voice command'}), 400
                else:
                    return jsonify({'error': 'Voice system not available'}), 503
                
            except Exception as e:
                self.logger.error(f"Voice API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """Serve static assets."""
            return send_from_directory('web/assets', filename)
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            client_id = request.sid
            self.connected_clients.add(client_id)
            self.logger.info(f"Client connected: {client_id}")
            
            # Send initial status
            if self.agent_ref:
                status = {
                    'type': 'status_update',
                    'data': self.agent_ref.status if hasattr(self.agent_ref, 'status') else 'connected'
                }
                emit('status_update', status)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            client_id = request.sid
            self.connected_clients.discard(client_id)
            self.logger.info(f"Client disconnected: {client_id}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle room joining."""
            room = data.get('room', 'default')
            join_room(room)
            emit('room_status', {'joined': room})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle room leaving."""
            room = data.get('room', 'default')
            leave_room(room)
            emit('room_status', {'left': room})
        
        @self.socketio.on('live_chat')
        def handle_live_chat(data):
            """Handle live chat messages."""
            try:
                message = data.get('message', '')
                if message and self.agent_ref:
                    # Process through agent
                    response = self._process_live_message(message)
                    emit('live_response', response, broadcast=True)
                    
            except Exception as e:
                self.logger.error(f"Live chat error: {e}")
                emit('error', {'message': str(e)})
        
        @self.socketio.on('system_command')
        def handle_system_command(data):
            """Handle system commands via WebSocket."""
            try:
                command = data.get('command')
                params = data.get('params', {})
                
                if command and self.agent_ref:
                    result = self._execute_system_command(command, params)
                    emit('command_result', result)
                    
            except Exception as e:
                self.logger.error(f"System command error: {e}")
                emit('error', {'message': str(e)})
    
    def _execute_automation_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automation action."""
        try:
            automation = self.agent_ref.automation
            
            if action == 'click':
                x, y = params.get('x', 0), params.get('y', 0)
                button = params.get('button', 'left')
                result = automation.click_at(x, y, button=button)
                
            elif action == 'type':
                text = params.get('text', '')
                result = automation.type_text(text)
                
            elif action == 'key_press':
                key = params.get('key', '')
                result = automation.press_key(key)
                
            elif action == 'screenshot':
                filename = params.get('filename')
                result = automation.take_screenshot(filename)
                
            elif action == 'get_processes':
                filter_name = params.get('filter')
                result = automation.get_running_processes(filter_name)
                
            elif action == 'system_stats':
                result = automation.get_system_stats()
                
            else:
                return {'error': f'Unknown action: {action}', 'success': False}
            
            return {'success': True, 'result': result, 'action': action}
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _process_live_message(self, message: str) -> Dict[str, Any]:
        """Process live chat message."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Simple echo for now - replace with actual agent processing
            response = f"Received: {message}"
            
            if hasattr(self.agent_ref, 'process_command'):
                response = self.agent_ref.process_command(message)
            
            return {
                'response': response,
                'timestamp': timestamp,
                'type': 'chat_response'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'type': 'error'
            }
    
    def _execute_system_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system command."""
        try:
            if command == 'get_status':
                if hasattr(self.agent_ref, 'get_system_status'):
                    result = self.agent_ref.get_system_status()
                else:
                    result = {'status': 'unknown'}
            
            elif command == 'restart_service':
                service = params.get('service')
                # Implement service restart logic
                result = {'restarted': service}
            
            else:
                result = {'error': f'Unknown command: {command}'}
            
            return {'success': True, 'result': result, 'command': command}
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def start_server(self) -> bool:
        """Start the web server."""
        if self.running:
            self.logger.warning("Web server already running")
            return False
        
        try:
            self.running = True
            
            # Start server in separate thread
            def run_server():
                try:
                    self.logger.info(f"Starting web server on http://{self.host}:{self.port}")
                    self.socketio.run(self.app, 
                                    host=self.host, 
                                    port=self.port,
                                    debug=False,
                                    use_reloader=False)
                except Exception as e:
                    self.logger.error(f"Web server error: {e}")
                finally:
                    self.running = False
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(1)
            
            self.logger.info("Web server started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            self.running = False
            return False
    
    def stop_server(self):
        """Stop the web server."""
        if not self.running:
            return
        
        self.running = False
        
        # Disconnect all clients
        if self.connected_clients:
            self.socketio.emit('server_shutdown', {'message': 'Server shutting down'}, 
                             broadcast=True)
        
        self.logger.info("Web server stopped")
    
    def broadcast_message(self, message_type: str, data: Dict[str, Any], room: str = None):
        """Broadcast message to connected clients."""
        if self.running:
            self.socketio.emit(message_type, data, room=room, broadcast=room is None)
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            'running': self.running,
            'host': self.host,
            'port': self.port,
            'connected_clients': len(self.connected_clients),
            'flask_available': FLASK_AVAILABLE,
            'cors_available': CORS_AVAILABLE
        }
    
    def wait_for_shutdown(self):
        """Wait for server shutdown."""
        if self.server_thread and self.server_thread.is_alive():
            try:
                self.server_thread.join()
            except KeyboardInterrupt:
                self.stop_server()


def create_default_web_files():
    """Create default web interface files."""
    web_dir = Path("web")
    web_dir.mkdir(exist_ok=True)
    
    # Create assets directory
    assets_dir = web_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create placeholder for assets
    (assets_dir / "placeholder.txt").write_text(
        "This directory contains web assets (CSS, JS, images, sounds)\n"
        "Generated by ULTRON Web Server"
    )
    
    print(f"Created web directory structure at {web_dir}")


if __name__ == "__main__":
    # Create default web files and test server
    create_default_web_files()
    
    print("Testing ULTRON Web Server...")
    server = UltronWebServer(host="localhost", port=8080)
    
    if server.start_server():
        print("Web server started successfully!")
        print("Visit: http://localhost:8080")
        
        try:
            server.wait_for_shutdown()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            server.stop_server()
    else:
        print("Failed to start web server")