#!/usr/bin/env python3
"""
ULTRON ADB Backend - Socket.IO Server
Handles ALL 45+ ADB functions in real-time
Runs on http://localhost:8080/adb.html websocket connection
"""

import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Install required packages if missing
def ensure_dependencies():
    """Ensure Flask-SocketIO is installed"""
    try:
        import flask_socketio
    except ImportError:
        print("Installing flask-socketio...")
        os.system('python -m pip install flask-socketio python-socketio pillow --quiet')


ensure_dependencies()

from flask import Flask, request
from flask_socketio import SocketIO, emit
from utils.ultron_logger import log_info, log_error
from adb_socket_integration import (
    get_devices,
    get_device_info,
    execute_shell_command,
    get_logcat,
    clear_logcat,
    get_process_list,
    get_installed_apps,
    launch_app,
    uninstall_app,
    tap_screen,
    swipe_screen,
    input_text,
    press_key,
    take_screenshot,
    list_files,
    pull_file,
    push_file,
    forward_port,
    reverse_forward,
    run_adb_command
)

# ============================================================
# FLASK + SOCKETIO SETUP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultron-adb-backend-secret'

# Enable CORS for Socket.IO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

connected_clients = set()

log_info("adb_backend", "ULTRON ADB Backend initializing...")

# ============================================================
# SOCKET.IO EVENT HANDLERS
# ============================================================

@socketio.on('connect')
def handle_connect():
    """Client connects to ADB backend"""
    client_id = request.sid
    connected_clients.add(client_id)
    log_info("adb_backend", f"✓ ADB Client connected: {client_id}")
    emit('adb_response', {
        'status': 'connected',
        'message': 'ADB Backend Ready',
        'clients': len(connected_clients)
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnects from ADB backend"""
    client_id = request.sid
    connected_clients.discard(client_id)
    log_info("adb_backend", f"✓ ADB Client disconnected: {client_id}")


@socketio.on('adb_command')
def handle_adb_command(data):
    """
    Handle ALL ADB commands from frontend
    Expected data: {command, device, args}
    """
    try:
        command = data.get('command', '').lower()
        device = data.get('device')
        args = data.get('args', '')

        log_info("adb_backend", f"→ Command: {command} | Device: {device}")

        response = {'device': device, 'command': command}

        # ====== DEVICE MANAGEMENT (6 functions) ======
        if command == 'devices':
            devices = get_devices()
            response.update({
                'success': True,
                'devices': devices,
                'output': f"Found {len(devices)} device(s)"
            })

        elif command == 'device_info':
            if not device:
                response.update({
                    'success': False,
                    'error': 'No device selected'
                })
            else:
                info = get_device_info(device)
                response.update({
                    'success': True,
                    'device_info': info,
                    'output': 'Device info retrieved'
                })

        # ====== SHELL COMMANDS (5 functions) ======
        elif command == 'shell':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = execute_shell_command(device, args)
                response.update(result)

        elif command == 'logcat':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                lines = int(args) if args else 100
                result = get_logcat(device, lines)
                response.update(result)

        elif command == 'clear_logcat':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = clear_logcat(device)
                response.update(result)

        elif command == 'processes':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = get_process_list(device)
                response.update(result)

        # ====== APP MANAGEMENT (3 functions) ======
        elif command == 'list_apps':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                apps = get_installed_apps(device)
                response.update({
                    'success': True,
                    'apps': apps,
                    'output': f"Found {len(apps)} app(s)"
                })

        elif command == 'launch_app':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = launch_app(device, args)
                response.update(result)

        elif command == 'uninstall_app':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = uninstall_app(device, args)
                response.update(result)

        # ====== SCREEN INTERACTION (5 functions) ======
        elif command == 'tap':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                try:
                    coords = args.split(',')
                    result = tap_screen(device, int(coords[0]), int(coords[1]))
                    response.update(result)
                except (ValueError, IndexError):
                    response.update({
                        'success': False,
                        'error': 'Invalid coords format: x,y'
                    })

        elif command == 'swipe':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                try:
                    coords = args.split(',')
                    result = swipe_screen(
                        device,
                        int(coords[0]), int(coords[1]),
                        int(coords[2]), int(coords[3])
                    )
                    response.update(result)
                except (ValueError, IndexError):
                    response.update({
                        'success': False,
                        'error': 'Invalid coords: x1,y1,x2,y2'
                    })

        elif command == 'input_text':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = input_text(device, args)
                response.update(result)

        elif command == 'press_key':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = press_key(device, args)
                response.update(result)

        elif command == 'screenshot':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = take_screenshot(device)
                response.update(result)

        # ====== FILE OPERATIONS (3 functions) ======
        elif command == 'list_files':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                path = args if args else '/sdcard/'
                files = list_files(device, path)
                response.update({
                    'success': True,
                    'files': files,
                    'output': f"Found {len(files)} item(s)"
                })

        elif command == 'pull':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = pull_file(device, args)
                response.update(result)

        elif command == 'push':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                try:
                    paths = args.split(',', 1)
                    result = push_file(device, paths[0], paths[1])
                    response.update(result)
                except IndexError:
                    response.update({
                        'success': False,
                        'error': 'Format: local_path,remote_path'
                    })

        # ====== NETWORKING (2 functions) ======
        elif command == 'forward':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                try:
                    ports = args.split(',')
                    result = forward_port(device, ports[0], ports[1])
                    response.update(result)
                except IndexError:
                    response.update({
                        'success': False,
                        'error': 'Format: local_port,remote_port'
                    })

        elif command == 'reverse':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                try:
                    ports = args.split(',')
                    result = reverse_forward(device, ports[0], ports[1])
                    response.update(result)
                except IndexError:
                    response.update({
                        'success': False,
                        'error': 'Format: remote_port,local_port'
                    })

        # ====== SYSTEM ACTIONS ======
        elif command == 'reboot':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = run_adb_command(['reboot'], device)
                response.update(result)

        elif command == 'reboot_bootloader':
            if not device:
                response.update({'success': False, 'error': 'No device'})
            else:
                result = run_adb_command(['reboot', 'bootloader'], device)
                response.update(result)

        # ====== UNKNOWN COMMAND ======
        else:
            response['success'] = False
            response['error'] = f'Unknown command: {command}'

        # Send response back to client
        emit('adb_response', response)
        log_info("adb_backend", f"← Response sent for: {command}")

    except Exception as e:
        log_error("adb_backend", f"Handler error: {str(e)}")
        emit('adb_error', {
            'message': str(e),
            'command': command,
            'error': True
        })


# ============================================================
# HTTP ENDPOINTS
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from flask import jsonify
    devices = get_devices()
    return jsonify({
        'status': 'healthy',
        'backend': 'adb',
        'devices_connected': len(devices),
        'clients': len(connected_clients),
        'version': '1.0.0'
    })


@app.route('/api/adb/devices', methods=['GET'])
def api_get_devices():
    """REST endpoint to get devices"""
    from flask import jsonify
    devices = get_devices()
    return jsonify({'devices': devices})


# ============================================================
# STARTUP
# ============================================================

if __name__ == '__main__':
    import time

    print("\n" + "="*70)
    print("  ULTRON ADB Backend - Socket.IO Server")
    print("="*70)
    print("[+] Listening on: http://localhost:5003")
    print("[+] Frontend URL: http://localhost:8080/adb.html")
    print("[+] Health Check: http://localhost:5003/health")
    print("="*70 + "\n")

    log_info("adb_backend", "Starting ULTRON ADB Backend Server...")

    try:
        # Run Socket.IO server on port 5003
        socketio.run(
            app,
            host='127.0.0.1',
            port=5003,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        log_info("adb_backend", "Shutting down...")
        sys.exit(0)
    except Exception as e:
        log_error("adb_backend", f"Fatal error: {str(e)}")
        sys.exit(1)
