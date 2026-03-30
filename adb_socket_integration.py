#!/usr/bin/env python3
"""
ADB Socket.IO Integration Module
Provides Socket.IO event handlers for ADB operations
Integrates with existing web_gui_server.py Flask app
"""

import os
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

# ADB path
ADB_PATH = os.environ.get("ADB_PATH", r"C:\Users\ultro\platform-tools\adb.exe")

os.environ.setdefault("ADB_PATH", ADB_PATH)

# ============================================================
# DEVICE MANAGEMENT
# ============================================================
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
