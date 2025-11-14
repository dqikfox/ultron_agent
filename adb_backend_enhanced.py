#!/usr/bin/env python3
"""
ADB Backend Integration - Updated with Enhanced Commands
Integrates adb_enhanced_commands.py with Socket.IO server
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect
import json
import asyncio
from adb_socket_integration import run_adb_command
from adb_enhanced_commands import (
    grant_permission,
    revoke_permission,
    list_permissions,
    clear_app_data,
    enable_app,
    disable_app,
    get_app_path,
    force_stop_app,
    list_device_features,
    get_battery_info,
    get_memory_info,
    get_network_info,
    set_display_size,
    reset_display_size,
    set_display_density,
    get_logcat_by_level,
    clear_logcat,
)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

CURRENT_DEVICE = None


def log_info(message):
    """Simple logging"""
    print(f"[INFO] {message} - adb_backend_enhanced.py:48")


def log_error(message):
    """Error logging"""
    print(f"[ERROR] {message} - adb_backend_enhanced.py:53")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'adb_backend'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    log_info("Client connected")
    emit('connection_response', {'data': 'Connected to ADB Backend'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    log_info("Client disconnected")


@socketio.on('select_device')
def handle_device_select(data):
    """Select device for operations"""
    global CURRENT_DEVICE
    CURRENT_DEVICE = data.get('device')
    log_info(f"Device selected: {CURRENT_DEVICE}")
    emit('device_selected', {'device': CURRENT_DEVICE})


# ============================================================
# Permission Management Commands
# ============================================================

@socketio.on('grant_permission')
def handle_grant_permission(data):
    """Grant permission to app"""
    try:
        package = data.get('package')
        permission = data.get('permission')

        result = grant_permission(CURRENT_DEVICE, package, permission)

        emit('grant_permission_response', {
            'success': True,
            'package': package,
            'permission': permission,
            'result': result
        })
    except Exception as e:
        log_error(f"Grant permission error: {e}")
        emit('grant_permission_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('revoke_permission')
def handle_revoke_permission(data):
    """Revoke permission from app"""
    try:
        package = data.get('package')
        permission = data.get('permission')

        result = revoke_permission(CURRENT_DEVICE, package, permission)

        emit('revoke_permission_response', {
            'success': True,
            'package': package,
            'permission': permission,
            'result': result
        })
    except Exception as e:
        log_error(f"Revoke permission error: {e}")
        emit('revoke_permission_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('list_permissions')
def handle_list_permissions(data):
    """List system permissions"""
    try:
        group = data.get('group')
        # Prefer device provided in event, fallback to previously selected device.
        device = data.get('device') or CURRENT_DEVICE
        if device is None:
            raise ValueError("No device specified or selected")
        device = str(device)
        result = list_permissions(device, group)

        emit('list_permissions_response', {
            'success': True,
            'permissions': result
        })
    except Exception as e:
        log_error(f"List permissions error: {e}")
        emit('list_permissions_response', {
            'success': False,
            'error': str(e)
        })


# ============================================================
# App Management Commands
# ============================================================

@socketio.on('clear_app_data')
def handle_clear_app_data(data):
    """Clear app data"""
    try:
        package = data.get('package')
        result = clear_app_data(CURRENT_DEVICE, package)

        emit('clear_app_data_response', {
            'success': True,
            'package': package,
            'result': result
        })
    except Exception as e:
        log_error(f"Clear app data error: {e}")
        emit('clear_app_data_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('enable_app')
def handle_enable_app(data):
    """Enable app"""
    try:
        package = data.get('package')
        result = enable_app(CURRENT_DEVICE, package)

        emit('enable_app_response', {
            'success': True,
            'package': package,
            'result': result
        })
    except Exception as e:
        log_error(f"Enable app error: {e}")
        emit('enable_app_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('disable_app')
def handle_disable_app(data):
    """Disable app"""
    try:
        package = data.get('package')
        result = disable_app(CURRENT_DEVICE, package)

        emit('disable_app_response', {
            'success': True,
            'package': package,
            'result': result
        })
    except Exception as e:
        log_error(f"Disable app error: {e}")
        emit('disable_app_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('force_stop_app')
def handle_force_stop_app(data):
    """Force stop app"""
    try:
        package = data.get('package')
        result = force_stop_app(CURRENT_DEVICE, package)

        emit('force_stop_app_response', {
            'success': True,
            'package': package,
            'result': result
        })
    except Exception as e:
        log_error(f"Force stop app error: {e}")
        emit('force_stop_app_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_app_path')
def handle_get_app_path(data):
    """Get app APK path"""
    try:
        package = data.get('package')
        result = get_app_path(CURRENT_DEVICE, package)

        emit('get_app_path_response', {
            'success': True,
            'package': package,
            'path': result
        })
    except Exception as e:
        log_error(f"Get app path error: {e}")
        emit('get_app_path_response', {
            'success': False,
            'error': str(e)
        })


# ============================================================
# System Information Commands
# ============================================================

@socketio.on('get_battery_info')
def handle_get_battery_info(data):
    """Get battery information"""
    try:
        result = get_battery_info(CURRENT_DEVICE)

        emit('get_battery_info_response', {
            'success': True,
            'battery_info': result
        })
    except Exception as e:
        log_error(f"Get battery info error: {e}")
        emit('get_battery_info_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_memory_info')
def handle_get_memory_info(data):
    """Get memory information"""
    try:
        result = get_memory_info(CURRENT_DEVICE)

        emit('get_memory_info_response', {
            'success': True,
            'memory_info': result
        })
    except Exception as e:
        log_error(f"Get memory info error: {e}")
        emit('get_memory_info_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_network_info')
def handle_get_network_info(data):
    """Get network information"""
    try:
        result = get_network_info(CURRENT_DEVICE)

        emit('get_network_info_response', {
            'success': True,
            'network_info': result
        })
    except Exception as e:
        log_error(f"Get network info error: {e}")
        emit('get_network_info_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_device_features')
def handle_get_device_features(data):
    """Get device features"""
    try:
        result = list_device_features(CURRENT_DEVICE)

        emit('get_device_features_response', {
            'success': True,
            'features': result
        })
    except Exception as e:
        log_error(f"Get device features error: {e}")
        emit('get_device_features_response', {
            'success': False,
            'error': str(e)
        })


# ============================================================
# Display Commands
# ============================================================

@socketio.on('set_display_size')
def handle_set_display_size(data):
    """Set display size"""
    try:
        width = data.get('width')
        height = data.get('height')
        result = set_display_size(CURRENT_DEVICE, width, height)

        emit('set_display_size_response', {
            'success': True,
            'size': f"{width}x{height}",
            'result': result
        })
    except Exception as e:
        log_error(f"Set display size error: {e}")
        emit('set_display_size_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('reset_display_size')
def handle_reset_display_size(data):
    """Reset display size"""
    try:
        result = reset_display_size(CURRENT_DEVICE)

        emit('reset_display_size_response', {
            'success': True,
            'result': result
        })
    except Exception as e:
        log_error(f"Reset display size error: {e}")
        emit('reset_display_size_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('set_display_density')
def handle_set_display_density(data):
    """Set display density"""
    try:
        dpi = data.get('dpi')
        result = set_display_density(CURRENT_DEVICE, dpi)

        emit('set_display_density_response', {
            'success': True,
            'dpi': dpi,
            'result': result
        })
    except Exception as e:
        log_error(f"Set display density error: {e}")
        emit('set_display_density_response', {
            'success': False,
            'error': str(e)
        })


# ============================================================
# Logcat Commands
# ============================================================

@socketio.on('get_logcat_by_level')
def handle_get_logcat_by_level(data):
    """Get logcat filtered by level"""
    try:
        level = data.get('level', 'E')
        lines = data.get('lines', 100)
        result = get_logcat_by_level(CURRENT_DEVICE, level, lines)

        emit('get_logcat_by_level_response', {
            'success': True,
            'level': level,
            'logcat': result
        })
    except Exception as e:
        log_error(f"Get logcat error: {e}")
        emit('get_logcat_by_level_response', {
            'success': False,
            'error': str(e)
        })


@socketio.on('clear_logcat')
def handle_clear_logcat(data):
    """Clear logcat"""
    try:
        result = clear_logcat(CURRENT_DEVICE)

        emit('clear_logcat_response', {
            'success': True,
            'result': result
        })
    except Exception as e:
        log_error(f"Clear logcat error: {e}")
        emit('clear_logcat_response', {
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    try:
        log_info("[+] Starting ULTRON ADB Enhanced Backend")
        print("[+] ULTRON ADB Backend  Socket.IO Server (Enhanced) - adb_backend_enhanced.py:447")
        print("[+] Listening on: http://localhost:5003 - adb_backend_enhanced.py:448")
        print("[+] Frontend URL: http://localhost:8080/adb.html - adb_backend_enhanced.py:449")
        print("[+] Health Check: http://localhost:5003/health - adb_backend_enhanced.py:450")
        print("[DEBUG] Starting socketio.run()... - adb_backend_enhanced.py:451")
        socketio.run(
            app,
            host='0.0.0.0',  # Changed from 127.0.0.1 to accept all interfaces
            port=5003,
            debug=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n[!] Shutdown requested - adb_backend_enhanced.py:460")
        log_info("Backend shutdown by user")
    except Exception as e:
        import traceback
        print(f"[!] Error: {e} - adb_backend_enhanced.py:464")
        traceback.print_exc()
        log_error(f"Backend error: {e}")
