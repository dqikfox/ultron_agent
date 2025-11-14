#!/usr/bin/env python3
"""
Enhanced ADB Commands - Implements additional features from official Android documentation
Based on: https://developer.android.com/tools/adb
Updated: November 1, 2025
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from adb_socket_integration import run_adb_command
from utils.ultron_logger import log_info, log_error

# ============================================================
# PERMISSION MANAGEMENT (Android 6.0+ / API 23+)
# ============================================================

def grant_permission(device: str, package: str, permission: str) -> dict:
    """
    Grant runtime permission to app (requires Android 6.0+)

    Args:
        device: Device serial
        package: Package name (e.g., 'com.example.app')
        permission: Permission name (e.g., 'android.permission.CAMERA')

    Returns:
        Command result dictionary
    """
    log_info("adb_enhanced", f"Granting {permission} to {package}")
    result = run_adb_command(
        ['shell', 'pm', 'grant', package, permission],
        device
    )
    return result


def revoke_permission(device: str, package: str, permission: str) -> dict:
    """
    Revoke runtime permission from app (requires Android 6.0+)

    Args:
        device: Device serial
        package: Package name
        permission: Permission name

    Returns:
        Command result dictionary
    """
    log_info("adb_enhanced", f"Revoking {permission} from {package}")
    result = run_adb_command(
        ['shell', 'pm', 'revoke', package, permission],
        device
    )
    return result


def list_permissions(device: str, group: str = None) -> dict:
    """
    List all system permissions

    Args:
        device: Device serial
        group: Optional permission group filter

    Returns:
        Dictionary with permission list
    """
    cmd = ['shell', 'pm', 'list', 'permissions']
    if group:
        cmd.extend(['-g', group])
    else:
        cmd.append('-d')  # Show dangerous permissions

    result = run_adb_command(cmd, device)
    return result


def get_app_permissions(device: str, package: str) -> dict:
    """
    Get permissions granted to specific app

    Args:
        device: Device serial
        package: Package name

    Returns:
        Dictionary with granted permissions
    """
    result = run_adb_command(
        ['shell', 'dumpsys', 'package', package],
        device
    )
    return result


# ============================================================
# APP DATA & STATE MANAGEMENT
# ============================================================

def clear_app_data(device: str, package: str) -> dict:
    """
    Clear all data associated with app (cache, databases, etc.)

    Args:
        device: Device serial
        package: Package name

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Clearing data for {package}")
    result = run_adb_command(
        ['shell', 'pm', 'clear', package],
        device
    )
    return result


def enable_app(device: str, package: str) -> dict:
    """
    Enable disabled app package

    Args:
        device: Device serial
        package: Package name

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Enabling {package}")
    result = run_adb_command(
        ['shell', 'pm', 'enable', package],
        device
    )
    return result


def disable_app(device: str, package: str) -> dict:
    """
    Disable app package without uninstalling

    Args:
        device: Device serial
        package: Package name

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Disabling {package}")
    result = run_adb_command(
        ['shell', 'pm', 'disable-user', package],
        device
    )
    return result


def get_app_path(device: str, package: str) -> dict:
    """
    Get file path to app APK

    Args:
        device: Device serial
        package: Package name

    Returns:
        Dictionary with APK path
    """
    result = run_adb_command(
        ['shell', 'pm', 'path', package],
        device
    )
    return result


# ============================================================
# FORCE STOP & CRASH MANAGEMENT
# ============================================================

def force_stop_app(device: str, package: str) -> dict:
    """
    Force stop all processes in package

    Args:
        device: Device serial
        package: Package name

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Force stopping {package}")
    result = run_adb_command(
        ['shell', 'am', 'force-stop', package],
        device
    )
    return result


def monitor_crashes(device: str) -> dict:
    """
    Monitor app crashes and ANRs in real-time

    Args:
        device: Device serial

    Returns:
        Command result (streaming)
    """
    log_info("adb_enhanced", "Starting crash monitoring")
    result = run_adb_command(
        ['shell', 'am', 'monitor'],
        device
    )
    return result


# ============================================================
# SERVICE MANAGEMENT
# ============================================================

def start_service(device: str, service_name: str) -> dict:
    """
    Start a background service

    Args:
        device: Device serial
        service_name: Service name (e.g., 'com.example/.MyService')

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Starting service {service_name}")
    result = run_adb_command(
        ['shell', 'am', 'startservice', service_name],
        device
    )
    return result


def stop_service(device: str, service_name: str) -> dict:
    """
    Stop a background service

    Args:
        device: Device serial
        service_name: Service name

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Stopping service {service_name}")
    result = run_adb_command(
        ['shell', 'am', 'stopservice', service_name],
        device
    )
    return result


# ============================================================
# DEVICE FEATURES & CAPABILITIES
# ============================================================

def list_device_features(device: str) -> dict:
    """
    List all device features (camera, NFC, GPS, etc.)

    Args:
        device: Device serial

    Returns:
        Dictionary with feature list
    """
    log_info("adb_enhanced", "Retrieving device features")
    result = run_adb_command(
        ['shell', 'pm', 'list', 'features'],
        device
    )
    return result


def list_libraries(device: str) -> dict:
    """
    List all supported libraries

    Args:
        device: Device serial

    Returns:
        Dictionary with library list
    """
    result = run_adb_command(
        ['shell', 'pm', 'list', 'libraries'],
        device
    )
    return result


def has_feature(device: str, feature_name: str) -> dict:
    """
    Check if device has specific feature

    Args:
        device: Device serial
        feature_name: Feature name

    Returns:
        Boolean result
    """
    result = run_adb_command(
        ['shell', 'pm', 'has-feature', feature_name],
        device
    )
    return result


# ============================================================
# SYSTEM INFORMATION & DIAGNOSTICS
# ============================================================

def get_battery_info(device: str) -> dict:
    """
    Get detailed battery information

    Args:
        device: Device serial

    Returns:
        Dictionary with battery status
    """
    log_info("adb_enhanced", "Retrieving battery info")
    result = run_adb_command(
        ['shell', 'dumpsys', 'battery'],
        device
    )
    return result


def get_memory_info(device: str) -> dict:
    """
    Get memory usage information

    Args:
        device: Device serial

    Returns:
        Dictionary with memory stats
    """
    log_info("adb_enhanced", "Retrieving memory info")
    result = run_adb_command(
        ['shell', 'dumpsys', 'meminfo'],
        device
    )
    return result


def get_cpu_info(device: str) -> dict:
    """
    Get CPU information

    Args:
        device: Device serial

    Returns:
        Dictionary with CPU details
    """
    result = run_adb_command(
        ['shell', 'cat', '/proc/cpuinfo'],
        device
    )
    return result


def get_thermal_info(device: str) -> dict:
    """
    Get device temperature information

    Args:
        device: Device serial

    Returns:
        Dictionary with thermal data
    """
    result = run_adb_command(
        ['shell', 'cat', '/sys/class/thermal/thermal_zone0/temp'],
        device
    )
    return result


def get_network_info(device: str) -> dict:
    """
    Get network connectivity information

    Args:
        device: Device serial

    Returns:
        Dictionary with network status
    """
    result = run_adb_command(
        ['shell', 'dumpsys', 'connectivity'],
        device
    )
    return result


def get_all_system_properties(device: str) -> dict:
    """
    Get all system properties

    Args:
        device: Device serial

    Returns:
        Dictionary with all properties
    """
    log_info("adb_enhanced", "Retrieving all system properties")
    result = run_adb_command(
        ['shell', 'getprop'],
        device
    )
    return result


# ============================================================
# BROADCAST INTENTS
# ============================================================

def broadcast_intent(device: str, action: str, extras: dict = None) -> dict:
    """
    Broadcast system intent

    Args:
        device: Device serial
        action: Intent action (e.g., 'android.intent.action.SCREEN_ON')
        extras: Optional intent extras

    Returns:
        Command result
    """
    cmd = ['shell', 'am', 'broadcast', '-a', action]

    if extras:
        for key, value in extras.items():
            cmd.extend(['-e', key, str(value)])

    log_info("adb_enhanced", f"Broadcasting intent: {action}")
    result = run_adb_command(cmd, device)
    return result


# ============================================================
# SCREENSHOT & VIDEO ENHANCEMENTS
# ============================================================

def take_screenshot_raw(device: str) -> bytes:
    """
    Take raw screenshot (PNG format, no overhead)

    Args:
        device: Device serial

    Returns:
        Raw PNG bytes
    """
    log_info("adb_enhanced", "Taking screenshot")
    result = run_adb_command(
        ['exec-out', 'screencap', '-p'],
        device
    )
    return result


def record_screen(
    device: str,
    filename: str = '/sdcard/video.mp4',
    duration: int = 180,
    bitrate: int = 20,
    size: str = None,
    rotate: bool = False
) -> dict:
    """
    Record device screen to MP4 video

    Args:
        device: Device serial
        filename: Output file path on device
        duration: Max duration in seconds
        bitrate: Video bitrate in Mbps
        size: Resolution (e.g., '1280x720')
        rotate: Enable 90° rotation

    Returns:
        Command result
    """
    cmd = ['shell', 'screenrecord']

    if size:
        cmd.extend(['--size', size])

    cmd.extend(['--bit-rate', str(bitrate * 1000000)])
    cmd.extend(['--time-limit', str(duration)])

    if rotate:
        cmd.append('--rotate')

    cmd.append(filename)

    log_info("adb_enhanced", f"Starting video recording: {filename}")
    result = run_adb_command(cmd, device)
    return result


# ============================================================
# DISPLAY SETTINGS
# ============================================================

def set_display_size(device: str, width: int, height: int) -> dict:
    """
    Override device display size (for testing)

    Args:
        device: Device serial
        width: Screen width in pixels
        height: Screen height in pixels

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Setting display size: {width}x{height}")
    result = run_adb_command(
        ['shell', 'am', 'display-size', f"{width}x{height}"],
        device
    )
    return result


def reset_display_size(device: str) -> dict:
    """
    Reset display size to default

    Args:
        device: Device serial

    Returns:
        Command result
    """
    result = run_adb_command(
        ['shell', 'am', 'display-size', 'reset'],
        device
    )
    return result


def set_display_density(device: str, dpi: int) -> dict:
    """
    Override device display density (for testing)

    Args:
        device: Device serial
        dpi: Display density in DPI

    Returns:
        Command result
    """
    log_info("adb_enhanced", f"Setting display density: {dpi} DPI")
    result = run_adb_command(
        ['shell', 'am', 'display-density', str(dpi)],
        device
    )
    return result


def reset_display_density(device: str) -> dict:
    """
    Reset display density to default

    Args:
        device: Device serial

    Returns:
        Command result
    """
    result = run_adb_command(
        ['shell', 'am', 'display-density', 'reset'],
        device
    )
    return result


# ============================================================
# APP INSTALLATION OPTIONS
# ============================================================

def install_app_with_options(
    device: str,
    apk_path: str,
    replace: bool = False,
    test_package: bool = False,
    allow_downgrade: bool = False,
    grant_permissions: bool = False
) -> dict:
    """
    Install APK with advanced options

    Args:
        device: Device serial
        apk_path: Path to APK file
        replace: Replace existing app (-r flag)
        test_package: Install as test package (-t flag)
        allow_downgrade: Allow downgrade (-d flag)
        grant_permissions: Grant all permissions (-g flag)

    Returns:
        Installation result
    """
    cmd = ['install']

    if replace:
        cmd.append('-r')
    if test_package:
        cmd.append('-t')
    if allow_downgrade:
        cmd.append('-d')
    if grant_permissions:
        cmd.append('-g')

    cmd.append(apk_path)

    log_info("adb_enhanced", f"Installing APK: {apk_path}")
    result = run_adb_command(cmd, device)
    return result


# ============================================================
# LOGCAT ADVANCED
# ============================================================

def get_logcat_verbose(device: str, lines: int = 100, package: str = None) -> dict:
    """
    Get verbose logcat output

    Args:
        device: Device serial
        lines: Number of lines
        package: Optional package filter

    Returns:
        Logcat output
    """
    cmd = ['logcat', '-v', 'verbose', '-m', str(lines)]
    if package:
        cmd.append(f"{package}:*")

    result = run_adb_command(cmd, device)
    return result


def get_logcat_by_level(device: str, level: str = 'E', lines: int = 100) -> dict:
    """
    Get logcat filtered by level (V/D/I/W/E/F)

    Args:
        device: Device serial
        level: Log level (V=verbose, D=debug, I=info, W=warning, E=error, F=fatal)
        lines: Number of lines

    Returns:
        Filtered logcat
    """
    result = run_adb_command(
        ['logcat', f"*:{level}", '-m', str(lines)],
        device
    )
    return result


def clear_logcat(device: str) -> dict:
    """
    Clear all logcat buffers

    Args:
        device: Device serial

    Returns:
        Command result
    """
    result = run_adb_command(['logcat', '-c'], device)
    return result


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_battery_output(output: str) -> dict:
    """Parse battery info output"""
    data = {}
    for line in output.split('\n'):
        if ':' in line:
            key, value = line.strip().split(':', 1)
            data[key.strip()] = value.strip()
    return data


def parse_memory_output(output: str) -> dict:
    """Parse memory info output"""
    data = {}
    for line in output.split('\n'):
        if line.strip() and not line.startswith('Process'):
            parts = line.split()
            if len(parts) >= 2:
                data[parts[0]] = ' '.join(parts[1:])
    return data


def parse_logcat_output(output: str) -> list:
    """Parse logcat output into structured format"""
    logs = []
    for line in output.split('\n'):
        if line.strip():
            logs.append(line.strip())
    return logs
