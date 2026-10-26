"""Web interface for ULTRON"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
import threading
import logging
from pathlib import Path

class WebInterface:
    def __init__(self, config, ultron_core):
        self.config = config['web']
        self.ultron = ultron_core
        self.app = Flask(__name__, 
                        template_folder='../web/templates',
                        static_folder='../web/static')
        self.running = False
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return send_from_directory('../web', 'index.html')
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            return send_from_directory('../web/static', filename)
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.ultron.get_status())
        
        @self.app.route('/api/command', methods=['POST'])
        def process_command():
            data = request.get_json()
            command = data.get('command', '')
            
            if not command:
                return jsonify({"error": "No command provided"})
            
            try:
                # Run command in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ultron.process_command(command, source="web")
                )
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/system')
        def get_system_info():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.ultron.system.get_status())
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/screenshot', methods=['POST'])
        def take_screenshot():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.ultron.vision.take_screenshot())
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/files/sort', methods=['POST'])
        def sort_files():
            try:
                data = request.get_json() or {}
                source_dir = data.get('source_dir')
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.ultron.files.auto_sort(source_dir))
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)})
        
        @self.app.route('/api/files/stats')
        def get_file_stats():
            try:
                stats = self.ultron.files.get_statistics()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)})
    
    async def start(self):
        """Start web server"""
        if not self.config.get('enabled', True):
            return
        
        def run_server():
            try:
                self.app.run(
                    host=self.config.get('host', 'localhost'),
                    port=self.config.get('port', 3000),
                    debug=False
                )
            except Exception as e:
                logging.error(f"Web server error: {e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        self.running = True
        logging.info("Web interface started")
    
    async def stop(self):
        """Stop web server"""
        self.running = False
        logging.info("Web interface stopped")
    
    def is_running(self):
        return self.running
