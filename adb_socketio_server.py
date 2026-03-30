#!/usr/bin/env python3
"""
ULTRON ADB Socket.IO Server
Handles all ADB operations for the web interface
Integrates with existing web_gui_server.py on port 8080
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from utils.ultron_logger import log_info, log_error, log_ai_decision
from adb_common import (
    run_adb_command,
    get_devices,
    execute_shell_command,
    get_logcat,
    clear_logcat,
    get_process_list,
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
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flask import Flask, request, jsonify
    from flask_socketio import SocketIO, emit
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Run: pip install flask flask-socketio python-socketio psutil pillow")
    sys.exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

ADB_PATH = os.environ.get("ADB_PATH", "adb")
SOCKET_PORT = 8080
SOCKET_HOST = "127.0.0.1"
LOG_FILE = "logs/adb_socketio_server.log"

os.environ.setdefault("ADB_PATH", ADB_PATH)

# ============================================================
# FLASK & SOCKETIO SETUP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultron-adb-socket-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active connections
active_devices = {}
connected_clients = set()

log_info("adb_socketio_server", "Server initializing...")

# ============================================================
# DEVICE MANAGEMENT
# ============================================================

def get_device_info(device):
    """Get detailed device information"""
    props = {
        'device_name': ['ro.product.model', 'ro.product.device'],
        'model': ['ro.product.model'],
        'version': ['ro.build.version.release'],
        'api_level': ['ro.build.version.sdk'],
        'serial': ['ro.serialno'],
        'imei': ['persist.sys.usb.config', 'ro.telephony.use_old_mnc_mcc'],
        'battery': ['battery'],
        'storage': ['storage'],
        'memory': ['memory'],
        'cpu': ['cpu_info']
    }

    info = {'serial': device}

    # Get properties
    for key, prop_names in props.items():
        for prop in prop_names:
            result = run_adb_command(['shell', 'getprop', prop], device)
            if result['success'] and result['output']:
                info[key] = result['output']
                break

    # Get battery info
    battery_result = run_adb_command(['shell', 'dumpsys', 'battery'], device)
    if battery_result['success']:
        for line in battery_result['output'].split('\n'):
            if 'level:' in line:
                info['battery'] = line.split(':')[1].strip() + '%'

    # Get storage
    storage_result = run_adb_command(['shell', 'df', '/storage/emulated/0'], device)
    if storage_result['success']:
        lines = storage_result['output'].split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 3:
                info['storage'] = f"{parts[2]}B / {parts[1]}B"

    # Get memory
    memory_result = run_adb_command(['shell', 'cat', '/proc/meminfo'], device)
    if memory_result['success']:
        for line in memory_result['output'].split('\n'):
            if 'MemTotal:' in line:
                total_kb = int(line.split()[1])
                info['memory'] = f"{total_kb // 1024}MB"

    return info

# ============================================================
# APP MANAGEMENT
# ============================================================

def get_installed_apps(device):
    """Get list of installed apps"""
    result = run_adb_command(['shell', 'pm', 'list', 'packages', '-3'], device)
    if not result['success']:
        return []

    apps = []
    for package in result['output'].split('\n'):
        if package.startswith('package:'):
            package_name = package.replace('package:', '').strip()
            # Get app label
            label_result = run_adb_command(
                ['shell', 'dumpsys', 'package', package_name],
                device
            )
            label = package_name
            if label_result['success']:
                for line in label_result['output'].split('\n'):
                    if 'versionName=' in line:
                        version = line.split('=')[1]
                        break

            apps.append({
                'package': package_name,
                'name': label,
                'version': version if 'version' in locals() else '1.0'
            })

    return apps

def launch_app(device, package_name):
    """Launch application"""
    result = run_adb_command(
        ['shell', 'am', 'start', '-n', f"{package_name}/.MainActivity"],
        device
    )
    return result

# ============================================================
# SCREEN INTERACTION
# ============================================================

# ============================================================
# FILE OPERATIONS
# ============================================================

# ============================================================
# PORT FORWARDING
# ============================================================

# ============================================================
# SOCKET.IO EVENT HANDLERS
# ============================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    log_info("adb_socketio_server", f"Client connected: {client_id}")
    emit('adb_response', {
        'status': 'connected',
        'message': 'Connected to ADB server'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    client_id = request.sid
    connected_clients.discard(client_id)
    log_info("adb_socketio_server", f"Client disconnected: {client_id}")

@socketio.on('adb_command')
def handle_adb_command(data):
    """Handle ADB command from client"""
    try:
        command = data.get('command')
        device = data.get('device')
        args = data.get('args', '')

        log_info("adb_socketio_server", f"Command: {command}, Device: {device}, Args: {args}")

        response = {'device': device, 'command': command}

        # DEVICE MANAGEMENT
        if command == 'devices':
            devices = get_devices()
            response['devices'] = devices
            response['output'] = f"Found {len(devices)} device(s)"

        elif command == 'device_info':
            info = get_device_info(device)
            response['device_info'] = info
            response['output'] = "Device info retrieved"

        # SHELL COMMANDS
        elif command == 'shell':
            result = execute_shell_command(device, args)
            response.update(result)

        elif command == 'logcat':
            lines = int(args) if args else 100
            result = get_logcat(device, lines)
            response.update(result)

        elif command == 'clear_logcat':
            result = clear_logcat(device)
            response.update(result)

        elif command == 'processes':
            result = get_process_list(device)
            response.update(result)

        # APPS
        elif command == 'list_apps':
            apps = get_installed_apps(device)
            response['apps'] = apps
            response['output'] = f"Found {len(apps)} app(s)"

        elif command == 'launch_app':
            result = launch_app(device, args)
            response.update(result)

        elif command == 'uninstall_app':
            result = uninstall_app(device, args)
            response.update(result)

        # SCREEN
        elif command == 'tap':
            coords = args.split(',')
            result = tap_screen(device, int(coords[0]), int(coords[1]))
            response.update(result)

        elif command == 'swipe':
            coords = args.split(',')
            result = swipe_screen(device, int(coords[0]), int(coords[1]),
                                int(coords[2]), int(coords[3]))
            response.update(result)

        elif command == 'input_text':
            result = input_text(device, args)
            response.update(result)

        elif command == 'press_key':
            result = press_key(device, args)
            response.update(result)

        elif command == 'screenshot':
            result = take_screenshot(device)
            response.update(result)

        # FILES
        elif command == 'list_files':
            files = list_files(device, args if args else '/sdcard/')
            response['files'] = files
            response['output'] = f"Found {len(files)} item(s)"

        elif command == 'pull':
            result = pull_file(device, args)
            response.update(result)

        elif command == 'push':
            # args = "local_path,remote_path"
            paths = args.split(',')
            result = push_file(device, paths[0], paths[1])
            response.update(result)

        # NETWORKING
        elif command == 'forward':
            # args = "local_port,remote_port"
            ports = args.split(',')
            result = forward_port(device, ports[0], ports[1])
            response.update(result)

        elif command == 'reverse':
            # args = "remote_port,local_port"
            ports = args.split(',')
            result = reverse_forward(device, ports[0], ports[1])
            response.update(result)

        # SYSTEM ACTIONS
        elif command == 'reboot':
            result = run_adb_command(['reboot'], device)
            response.update(result)

        elif command == 'reboot_bootloader':
            result = run_adb_command(['reboot', 'bootloader'], device)
            response.update(result)

        elif command == 'power_on':
            result = press_key(device, '26')  # Power key
            response.update(result)

        elif command == 'power_off':
            result = run_adb_command(['shell', 'am', 'start', '-a',
                                    'android.intent.action.REBOOT'], device)
            response.update(result)

        else:
            response['error'] = f"Unknown command: {command}"
            response['success'] = False

        emit('adb_response', response)
        log_ai_decision("adb_socketio_server", f"Command executed: {command}",
                       confidence_score=0.95 if response.get('success') else 0.1)

    except Exception as e:
        log_error("adb_socketio_server", f"Command error: {str(e)}")
        emit('adb_error', {'message': str(e), 'command': command})

# ============================================================
# HTTP ROUTES
# ============================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    devices = get_devices()
    return jsonify({
        'status': 'healthy',
        'devices': len(devices),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/adb/devices', methods=['GET'])
def api_devices():
    """Get devices via HTTP"""
    devices = get_devices()
    return jsonify({'devices': devices})

@app.route('/api/adb/push', methods=['POST'])
def api_push_file():
    """Upload file to device"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        device = request.form.get('device')
        remote_path = request.form.get('remote_path', '/sdcard/')

        # Save temp file
        temp_path = f'/tmp/{file.filename}'
        file.save(temp_path)

        # Push to device
        result = push_file(device, temp_path, remote_path)
        os.remove(temp_path)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# STARTUP
# ============================================================

if __name__ == '__main__':
    log_info("adb_socketio_server", f"Starting Socket.IO server on {SOCKET_HOST}:{SOCKET_PORT}")

    try:
        socketio.run(app, host=SOCKET_HOST, port=SOCKET_PORT, debug=False,
                    use_reloader=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        log_error("adb_socketio_server", f"Server error: {str(e)}")
        sys.exit(1)
