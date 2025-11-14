#!/usr/bin/env python3
"""
ADB Socket.IO Integration Module
Provides Socket.IO event handlers for ADB operations
Integrates with existing web_gui_server.py Flask app
"""

import subprocess
import os
import base64
from pathlib import Path
from utils.ultron_logger import log_info, log_error, log_ai_decision

# ADB path
ADB_PATH = r"C:\Users\ultro\platform-tools\adb.exe"

# ============================================================
# ADB COMMAND EXECUTION
# ============================================================

def run_adb_command(args, device=None):
    """Execute ADB command and return output"""
    try:
        cmd = [ADB_PATH]
        if device:
            cmd.extend(['-s', device])
        cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip() if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Command timeout (30s)'
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e)
        }


# ============================================================
# DEVICE MANAGEMENT
# ============================================================

def get_devices():
    """Get list of connected devices"""
    result = run_adb_command(['devices', '-l'])
    if not result['success']:
        return []

    devices = []
    for line in result['output'].split('\n')[1:]:
        if not line.strip() or line.startswith('*'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            serial = parts[0]
            status = parts[1]
            devices.append({
                'serial': serial,
                'status': status,
                'model': parts[3] if len(parts) > 3 else 'Unknown',
                'device': parts[5] if len(parts) > 5 else 'Unknown'
            })

    return devices


def get_device_info(device):
    """Get detailed device information"""
    info = {'serial': device}

    # Get device model
    result = run_adb_command(['shell', 'getprop', 'ro.product.model'], device)
    if result['success']:
        info['model'] = result['output']

    # Get Android version
    result = run_adb_command(
        ['shell', 'getprop', 'ro.build.version.release'],
        device
    )
    if result['success']:
        info['version'] = result['output']

    # Get API level
    result = run_adb_command(['shell', 'getprop', 'ro.build.version.sdk'], device)
    if result['success']:
        info['api_level'] = result['output']

    # Get battery
    battery_result = run_adb_command(['shell', 'dumpsys', 'battery'], device)
    if battery_result['success']:
        for line in battery_result['output'].split('\n'):
            if 'level:' in line:
                info['battery'] = line.split(':')[1].strip() + '%'
                break

    # Get storage
    storage_result = run_adb_command(
        ['shell', 'df', '/storage/emulated/0'],
        device
    )
    if storage_result['success']:
        lines = storage_result['output'].split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 3:
                info['storage'] = f"{parts[2]}B / {parts[1]}B"

    return info


# ============================================================
# SHELL COMMANDS
# ============================================================

def execute_shell_command(device, command):
    """Execute shell command on device"""
    result = run_adb_command(['shell', command], device)
    return result


def get_logcat(device, lines=100):
    """Get logcat output"""
    result = run_adb_command(['logcat', '-d', '-t', str(lines)], device)
    return result


def clear_logcat(device):
    """Clear logcat"""
    result = run_adb_command(['logcat', '-c'], device)
    return result


def get_process_list(device):
    """Get running processes"""
    result = run_adb_command(['shell', 'ps'], device)
    return result


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
            apps.append({
                'package': package_name,
                'name': package_name.split('.')[-1]
            })

    return apps


def launch_app(device, package_name):
    """Launch application - auto-detects main activity"""
    # First try to get the main activity for this package
    activity_result = run_adb_command(
        ['shell', 'cmd', 'package', 'resolve-activity', '--brief',
         package_name],
        device
    )

    main_activity = None
    if activity_result['success'] and activity_result['output']:
        # Parse the output to get the activity
        # Format: priority=... packageName/.ActivityName
        lines = activity_result['output'].split('\n')
        for line in lines:
            if '/' in line:
                parts = line.split()
                for part in parts:
                    if '/' in part:
                        main_activity = part.strip()
                        break
                if main_activity:
                    break

    # If we found the activity, use it; otherwise try common names
    if not main_activity:
        # Try common activity names
        common_activities = [
            f"{package_name}/.MainActivity",
            f"{package_name}/.MainActivityAlias",
            f"{package_name}/.LauncherActivity"
        ]
        main_activity = common_activities[0]

    # Launch with the activity name
    result = run_adb_command(
        ['shell', 'am', 'start', '-a',
         'android.intent.action.MAIN', '-n', main_activity],
        device
    )
    return result


def uninstall_app(device, package_name):
    """Uninstall application"""
    result = run_adb_command(['uninstall', package_name], device)
    return result


# ============================================================
# SCREEN INTERACTION
# ============================================================

def tap_screen(device, x, y):
    """Tap screen at coordinates"""
    result = run_adb_command(['shell', 'input', 'tap', str(x), str(y)], device)
    return result


def swipe_screen(device, x1, y1, x2, y2, duration=500):
    """Swipe on screen"""
    result = run_adb_command(
        ['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)],
        device
    )
    return result


def input_text(device, text):
    """Type text on device"""
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    result = run_adb_command(
        ['shell', 'input', 'text', escaped_text],
        device
    )
    return result


def press_key(device, key_code):
    """Press hardware key"""
    result = run_adb_command(['shell', 'input', 'keyevent', str(key_code)], device)
    return result


def take_screenshot(device):
    """Take device screenshot"""
    temp_path = '/sdcard/screenshot.png'
    result = run_adb_command(['shell', 'screencap', '-p', temp_path], device)

    if result['success']:
        local_path = '/tmp/adb_screenshot.png'
        pull_result = run_adb_command(['pull', temp_path, local_path], device)

        if pull_result['success']:
            try:
                with open(local_path, 'rb') as f:
                    img_data = f.read()
                    img_base64 = base64.b64encode(img_data).decode()
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    return {'success': True, 'image': img_base64}
            except Exception as e:
                return {'success': False, 'error': str(e)}

    return result


# ============================================================
# FILE OPERATIONS
# ============================================================

def list_files(device, path='/sdcard/'):
    """List files in directory"""
    result = run_adb_command(['shell', 'ls', '-la', path], device)
    if not result['success']:
        return []

    files = []
    for line in result['output'].split('\n')[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 9:
            files.append({
                'name': parts[-1],
                'size': parts[4],
                'type': 'd' if line.startswith('d') else 'f',
                'perms': parts[0]
            })

    return files


def pull_file(device, remote_path, local_path=None):
    """Download file from device"""
    if not local_path:
        local_path = f"/tmp/{os.path.basename(remote_path)}"

    result = run_adb_command(['pull', remote_path, local_path], device)
    return {**result, 'local_path': local_path}


def push_file(device, local_path, remote_path):
    """Upload file to device"""
    result = run_adb_command(['push', local_path, remote_path], device)
    return result


# ============================================================
# PORT FORWARDING
# ============================================================

def forward_port(device, local_port, remote_port):
    """Setup port forwarding"""
    result = run_adb_command(
        ['forward', f'tcp:{local_port}', f'tcp:{remote_port}'],
        device
    )
    return result


def reverse_forward(device, remote_port, local_port):
    """Setup reverse port forwarding"""
    result = run_adb_command(
        ['reverse', f'tcp:{remote_port}', f'tcp:{local_port}'],
        device
    )
    return result


# ============================================================
# SOCKET.IO EVENT HANDLER FACTORY
# ============================================================

def create_socket_handlers(socketio):
    """Create Socket.IO event handlers for ADB operations"""

    connected_clients = set()

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        client_id = request.sid
        connected_clients.add(client_id)
        log_info("adb_socket_integration", f"ADB Client connected: {client_id}")
        emit('adb_response', {
            'status': 'connected',
            'message': 'Connected to ADB server'
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnect"""
        client_id = request.sid
        connected_clients.discard(client_id)
        log_info("adb_socket_integration", f"ADB Client disconnected: {client_id}")

    @socketio.on('adb_command')
    def handle_adb_command(data):
        """Handle ADB command from client"""
        try:
            from flask import request
            from flask_socketio import emit

            command = data.get('command')
            device = data.get('device')
            args = data.get('args', '')

            log_info(
                "adb_socket_integration",
                f"ADB Command: {command}, Device: {device}"
            )

            response = {'device': device, 'command': command}

            # DEVICE MANAGEMENT
            if command == 'devices':
                devices = get_devices()
                response['devices'] = devices
                response['output'] = f"Found {len(devices)} device(s)"
                response['success'] = True

            elif command == 'device_info':
                info = get_device_info(device)
                response['device_info'] = info
                response['output'] = "Device info retrieved"
                response['success'] = True

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
                response['success'] = True

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
                result = swipe_screen(
                    device,
                    int(coords[0]), int(coords[1]),
                    int(coords[2]), int(coords[3])
                )
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
                response['success'] = True

            elif command == 'pull':
                result = pull_file(device, args)
                response.update(result)

            elif command == 'push':
                paths = args.split(',')
                result = push_file(device, paths[0], paths[1])
                response.update(result)

            # NETWORKING
            elif command == 'forward':
                ports = args.split(',')
                result = forward_port(device, ports[0], ports[1])
                response.update(result)

            elif command == 'reverse':
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

            else:
                response['error'] = f"Unknown command: {command}"
                response['success'] = False

            emit('adb_response', response)
            log_ai_decision(
                "adb_socket_integration",
                f"Executed: {command}",
                confidence_score=0.95 if response.get('success') else 0.1
            )

        except Exception as e:
            log_error("adb_socket_integration", f"Error: {str(e)}")
            emit('adb_error', {'message': str(e), 'command': command})

    return {
        'connect': handle_connect,
        'disconnect': handle_disconnect,
        'adb_command': handle_adb_command
    }
