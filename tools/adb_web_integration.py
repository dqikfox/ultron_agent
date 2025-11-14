#!/usr/bin/env python3
"""
ADB Web Server Integration
Handles ADB endpoints for the web GUI
"""

import json
import logging
from tools.adb_manager import adb_manager, execute_adb_action

logger = logging.getLogger(__name__)


class ADBWebHandler:
    """Handles ADB web requests"""

    @staticmethod
    def handle_adb_get(path: str) -> dict:
        """Handle ADB GET requests"""
        try:
            if path == '/api/adb/devices':
                devices = adb_manager.get_devices()
                return {'success': True, 'devices': devices}

            elif path.startswith('/api/adb/device/'):
                device = path.split('/')[-1]
                from tools.adb_manager import execute_adb_action
                result = execute_adb_action('device_info', device)
                return result

            elif path.startswith('/api/adb/apps/'):
                device = path.split('/')[-1]
                result = execute_adb_action('list_apps', device)
                return result

            elif path.startswith('/api/adb/battery/'):
                device = path.split('/')[-1]
                battery = adb_manager.get_battery_info(device)
                return {'success': True, 'battery': battery}

            elif path.startswith('/api/adb/storage/'):
                device = path.split('/')[-1]
                storage = adb_manager.get_storage_info(device)
                return {'success': True, 'storage': storage}

            else:
                return {'success': False, 'message': 'Unknown ADB endpoint'}

        except Exception as e:
            logger.error(f"ADB GET error: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def handle_adb_post(path: str, data: dict) -> dict:
        """Handle ADB POST requests"""
        try:
            if path == '/api/adb/command':
                command = data.get('command')
                device = data.get('device')
                args = data.get('args', {})
                result = execute_adb_action(command, device, **args)
                return result

            elif path == '/api/adb/shell':
                device = data.get('device')
                command = data.get('command')
                result = execute_adb_action('shell', device, args=command)
                return result

            elif path == '/api/adb/install':
                device = data.get('device')
                apk_path = data.get('path')
                result = execute_adb_action('install_app', device, path=apk_path)
                return result

            elif path == '/api/adb/uninstall':
                device = data.get('device')
                package = data.get('package')
                result = execute_adb_action('uninstall_app', device, package=package)
                return result

            elif path == '/api/adb/push':
                device = data.get('device')
                local = data.get('local')
                remote = data.get('remote')
                result = execute_adb_action('push', device, local=local, remote=remote)
                return result

            elif path == '/api/adb/pull':
                device = data.get('device')
                remote = data.get('remote')
                local = data.get('local')
                result = execute_adb_action('pull', device, remote=remote, local=local)
                return result

            elif path == '/api/adb/screenshot':
                device = data.get('device')
                output = data.get('output')
                result = execute_adb_action('screenshot', device, output=output)
                return result

            elif path == '/api/adb/reboot':
                device = data.get('device')
                result = execute_adb_action('reboot', device)
                return result

            elif path == '/api/adb/forward':
                device = data.get('device')
                local_port = data.get('local_port')
                remote_port = data.get('remote_port')
                result = execute_adb_action(
                    'forward', device,
                    local_port=local_port,
                    remote_port=remote_port
                )
                return result

            elif path == '/api/adb/list-files':
                device = data.get('device')
                file_path = data.get('path', '/sdcard/')
                result = execute_adb_action('list_files', device, path=file_path)
                return result

            else:
                return {'success': False, 'message': 'Unknown ADB endpoint'}

        except Exception as e:
            logger.error(f"ADB POST error: {e}")
            return {'success': False, 'error': str(e)}


def register_adb_handlers(handler_class):
    """Register ADB handlers into web server"""

    # Monkey-patch the handler class with ADB support
    original_handle_api_get = handler_class._handle_api_get
    original_handle_api_post = handler_class._handle_api_post

    def new_handle_api_get(self):
        """Enhanced API GET with ADB support"""
        if self.path.startswith('/api/adb/'):
            try:
                response = ADBWebHandler.handle_adb_get(self.path)
                self._send_json_response(response)
            except Exception as e:
                logger.error(f"ADB API error: {e}")
                self._send_json_response(
                    {'success': False, 'error': str(e)}, 500
                )
        else:
            original_handle_api_get(self)

    def new_handle_api_post(self):
        """Enhanced API POST with ADB support"""
        if self.path.startswith('/api/adb/'):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    data = {}
                else:
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))

                response = ADBWebHandler.handle_adb_post(self.path, data)
                self._send_json_response(response)
            except Exception as e:
                logger.error(f"ADB API POST error: {e}")
                self._send_json_response(
                    {'success': False, 'error': str(e)}, 500
                )
        else:
            original_handle_api_post(self)

    handler_class._handle_api_get = new_handle_api_get
    handler_class._handle_api_post = new_handle_api_post
