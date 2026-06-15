#!/usr/bin/env python3
"""
ULTRON ADB Manager - Android Device Control Tool
Provides comprehensive ADB integration with web interface
"""

import os
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ADBManager:
    """Manages ADB commands and Android device interactions"""

    def __init__(self):
        """Initialize ADB Manager"""
        self.adb_path = self._find_adb()
        self.connected_devices: Dict[str, Dict[str, Any]] = {}
        self.logger = logger

    def _find_adb(self) -> str:
        """Find ADB executable path"""
        # Check Android SDK
        android_home = os.environ.get('ANDROID_HOME', '')
        if android_home:
            adb_candidate = os.path.join(android_home, 'platform-tools', 'adb')
            if platform.system() == 'Windows':
                adb_candidate += '.exe'
            if os.path.exists(adb_candidate):
                return adb_candidate

        # Check PATH
        try:
            result = subprocess.run(['where' if platform.system() == 'Windows' else 'which', 'adb'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception as e:
            logger.warning(f"Could not find adb in PATH: {e}")

        # Default fallback
        return 'adb'

    def _run_adb_command(self, *args, device: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run ADB command and return (returncode, stdout, stderr)

        Args:
            *args: Command arguments
            device: Target device serial (optional)

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        cmd = [self.adb_path]

        if device:
            cmd.extend(['-s', device])

        cmd.extend(args)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, '', 'Command timeout'
        except Exception as e:
            return 1, '', str(e)

    def get_devices(self) -> Dict[str, Dict[str, str]]:
        """Get list of connected ADB devices"""
        returncode, stdout, stderr = self._run_adb_command('devices', '-l')

        if returncode != 0:
            logger.error(f"Failed to list devices: {stderr}")
            return {}

        devices = {}
        lines = stdout.strip().split('\n')[1:]  # Skip header

        for line in lines:
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                status = parts[1]

                device_info = {'serial': serial, 'status': status}

                # Parse additional info if available
                if len(parts) > 2:
                    for part in parts[2:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            device_info[key] = value

                devices[serial] = device_info
                self.connected_devices[serial] = device_info

        return devices

    def get_device_properties(self, device: str) -> Dict[str, str]:
        """Get device properties"""
        properties = {}
        property_names = [
            'ro.build.version.release',      # Android version
            'ro.build.version.sdk',          # API level
            'ro.product.model',              # Model
            'ro.product.brand',              # Brand
            'ro.serialno',                   # Serial number
            'ro.build.fingerprint',          # Fingerprint
            'ro.product.cpu.abi',            # CPU ABI
            'ro.build.version.security_patch',  # Security patch
            'ro.setupwizard.mode',           # Setup wizard mode
            'ro.board.platform',             # Platform
        ]

        for prop_name in property_names:
            returncode, stdout, stderr = self._run_adb_command(
                'shell', f'getprop {prop_name}',
                device=device
            )
            if returncode == 0:
                properties[prop_name] = stdout.strip()

        return properties

    def get_battery_info(self, device: str) -> Dict[str, str]:
        """Get battery information"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', 'dumpsys battery',
            device=device
        )

        battery_info = {}
        if returncode == 0:
            for line in stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    battery_info[key.strip()] = value.strip()

        return battery_info

    def get_storage_info(self, device: str) -> Dict[str, str]:
        """Get storage information"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', 'df /data /cache /sdcard',
            device=device
        )

        storage_info = {}
        if returncode == 0:
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                # Parse df output
                storage_info['raw_output'] = stdout
        else:
            storage_info['error'] = stderr

        return storage_info

    def list_apps(self, device: str, system: bool = False) -> List[Dict[str, str]]:
        """List installed applications"""
        cmd = 'shell', 'pm list packages -3'  # -3 = third-party only
        if system:
            cmd = 'shell', 'pm list packages'

        returncode, stdout, stderr = self._run_adb_command(*cmd, device=device)

        apps = []
        if returncode == 0:
            for package in stdout.strip().split('\n'):
                if package.startswith('package:'):
                    app_name = package.replace('package:', '')
                    # Try to get app info
                    ret, out, err = self._run_adb_command(
                        'shell', f'dumpsys package {app_name} | grep versionName',
                        device=device
                    )
                    version = out.strip() if ret == 0 else 'Unknown'
                    apps.append({
                        'package': app_name,
                        'version': version
                    })

        return apps

    def install_app(self, device: str, apk_path: str) -> Tuple[bool, str]:
        """Install application on device"""
        if not os.path.exists(apk_path):
            return False, f"APK file not found: {apk_path}"

        returncode, stdout, stderr = self._run_adb_command(
            'install', '-r', apk_path,
            device=device
        )

        if returncode == 0 and 'Success' in stdout:
            return True, f"App installed successfully: {os.path.basename(apk_path)}"
        else:
            return False, f"Installation failed: {stdout} {stderr}"

    def uninstall_app(self, device: str, package_name: str) -> Tuple[bool, str]:
        """Uninstall application from device"""
        returncode, stdout, stderr = self._run_adb_command(
            'uninstall', package_name,
            device=device
        )

        if returncode == 0 and 'Success' in stdout:
            return True, f"App uninstalled: {package_name}"
        else:
            return False, f"Uninstall failed: {stdout} {stderr}"

    def push_file(self, device: str, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Push file to device"""
        if not os.path.exists(local_path):
            return False, f"Local file not found: {local_path}"

        returncode, stdout, stderr = self._run_adb_command(
            'push', local_path, remote_path,
            device=device
        )

        if returncode == 0:
            return True, f"File pushed: {remote_path}"
        else:
            return False, f"Push failed: {stderr}"

    def pull_file(self, device: str, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """Pull file from device"""
        returncode, stdout, stderr = self._run_adb_command(
            'pull', remote_path, local_path,
            device=device
        )

        if returncode == 0:
            return True, f"File pulled: {local_path}"
        else:
            return False, f"Pull failed: {stderr}"

    def shell_command(self, device: str, command: str) -> Tuple[bool, str]:
        """Execute shell command on device"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', command,
            device=device
        )

        result = stdout if returncode == 0 else stderr
        return returncode == 0, result

    def take_screenshot(self, device: str, output_path: str = None) -> Tuple[bool, str]:
        """Take screenshot from device"""
        if output_path is None:
            output_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        remote_path = '/sdcard/screenshot.png'
        returncode, stdout, stderr = self._run_adb_command(
            'shell', 'screencap -p',
            device=device
        )

        if returncode == 0:
            with open(output_path, 'wb') as f:
                f.write(stdout.encode('latin-1'))
            return True, f"Screenshot saved: {output_path}"
        else:
            return False, f"Screenshot failed: {stderr}"

    def start_screen_record(self, device: str, duration: int = 300) -> Tuple[bool, str]:
        """Start screen recording"""
        remote_path = f'/sdcard/record_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
        returncode, stdout, stderr = self._run_adb_command(
            'shell', f'screenrecord --time-limit {duration} {remote_path}',
            device=device
        )

        if returncode == 0:
            return True, f"Recording started: {remote_path}"
        else:
            return False, f"Recording failed: {stderr}"

    def reboot_device(self, device: str, bootloader: bool = False) -> Tuple[bool, str]:
        """Reboot device"""
        arg = 'bootloader' if bootloader else ''
        returncode, stdout, stderr = self._run_adb_command(
            'reboot', arg,
            device=device
        )

        if returncode == 0:
            return True, "Device rebooting..."
        else:
            return False, f"Reboot failed: {stderr}"

    def forward_port(self, device: str, local_port: int, remote_port: int) -> Tuple[bool, str]:
        """Forward local port to device port"""
        returncode, stdout, stderr = self._run_adb_command(
            'forward',
            f'tcp:{local_port}',
            f'tcp:{remote_port}',
            device=device
        )

        if returncode == 0:
            return True, f"Port forward set: {local_port} -> {remote_port}"
        else:
            return False, f"Forward failed: {stderr}"

    def list_files(self, device: str, path: str = '/sdcard/') -> Tuple[bool, str]:
        """List files in directory"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', f'ls -la {path}',
            device=device
        )

        if returncode == 0:
            return True, stdout
        else:
            return False, f"List failed: {stderr}"

    def grant_permissions(self, device: str, package: str) -> Tuple[bool, str]:
        """Grant all permissions to app"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', f'pm grant {package} android.permission.INTERNET',
            device=device
        )

        if returncode == 0:
            return True, f"Permissions granted to {package}"
        else:
            return False, f"Grant failed: {stderr}"

    def enable_debug_mode(self, device: str) -> Tuple[bool, str]:
        """Enable USB debugging mode"""
        # This is a notification, actual enabling is done on device
        returncode, stdout, stderr = self._run_adb_command(
            'shell', 'settings put global adb_enabled 1',
            device=device
        )

        if returncode == 0:
            return True, "Debug mode enabled"
        else:
            return False, f"Enable failed: {stderr}"

    def tap_screen(self, device: str, x: int, y: int) -> Tuple[bool, str]:
        """Tap screen at coordinates"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', f'input tap {x} {y}',
            device=device
        )

        if returncode == 0:
            return True, f"Tapped at ({x}, {y})"
        else:
            return False, f"Tap failed: {stderr}"

    def input_text(self, device: str, text: str) -> Tuple[bool, str]:
        """Input text on device"""
        # Escape special characters
        text = text.replace("'", "\\'").replace('"', '\\"')
        returncode, stdout, stderr = self._run_adb_command(
            'shell', f"input text '{text}'",
            device=device
        )

        if returncode == 0:
            return True, f"Text inputted: {text}"
        else:
            return False, f"Input failed: {stderr}"

    def factory_reset(self, device: str) -> Tuple[bool, str]:
        """Factory reset device (WARNING)"""
        returncode, stdout, stderr = self._run_adb_command(
            'shell', 'am broadcast -a android.intent.action.MASTER_CLEAR',
            device=device
        )

        if returncode == 0:
            return True, "Factory reset initiated"
        else:
            return False, f"Reset failed: {stderr}"

    def disconnect_device(self, device: str) -> Tuple[bool, str]:
        """Disconnect from device"""
        returncode, stdout, stderr = self._run_adb_command('disconnect', device)

        if returncode == 0:
            return True, f"Disconnected from {device}"
        else:
            return False, f"Disconnect failed: {stderr}"


# Global ADB Manager instance
adb_manager = ADBManager()


def execute_adb_action(action: str, device: str, **kwargs) -> Dict[str, Any]:
    """Execute ADB action and return result"""
    try:
        if action == 'devices':
            devices = adb_manager.get_devices()
            return {'success': True, 'data': devices}

        elif action == 'device_info':
            props = adb_manager.get_device_properties(device)
            battery = adb_manager.get_battery_info(device)
            storage = adb_manager.get_storage_info(device)
            return {
                'success': True,
                'data': {
                    'properties': props,
                    'battery': battery,
                    'storage': storage
                }
            }

        elif action == 'list_apps':
            apps = adb_manager.list_apps(device)
            return {'success': True, 'data': apps}

        elif action == 'install_app':
            success, msg = adb_manager.install_app(device, kwargs.get('path'))
            return {'success': success, 'message': msg}

        elif action == 'uninstall_app':
            success, msg = adb_manager.uninstall_app(device, kwargs.get('package'))
            return {'success': success, 'message': msg}

        elif action == 'push':
            success, msg = adb_manager.push_file(
                device, kwargs.get('local'), kwargs.get('remote')
            )
            return {'success': success, 'message': msg}

        elif action == 'pull':
            success, msg = adb_manager.pull_file(
                device, kwargs.get('remote'), kwargs.get('local')
            )
            return {'success': success, 'message': msg}

        elif action == 'shell':
            success, output = adb_manager.shell_command(device, kwargs.get('args'))
            return {'success': success, 'output': output}

        elif action == 'screenshot':
            success, msg = adb_manager.take_screenshot(device, kwargs.get('output'))
            return {'success': success, 'message': msg}

        elif action == 'record':
            success, msg = adb_manager.start_screen_record(
                device, kwargs.get('duration', 300)
            )
            return {'success': success, 'message': msg}

        elif action == 'reboot':
            success, msg = adb_manager.reboot_device(device)
            return {'success': success, 'message': msg}

        elif action == 'forward':
            success, msg = adb_manager.forward_port(
                device, kwargs.get('local_port'), kwargs.get('remote_port')
            )
            return {'success': success, 'message': msg}

        elif action == 'list_files':
            success, output = adb_manager.list_files(device, kwargs.get('path', '/sdcard/'))
            return {'success': success, 'output': output}

        elif action == 'grant_permissions':
            success, msg = adb_manager.grant_permissions(device, kwargs.get('package'))
            return {'success': success, 'message': msg}

        elif action == 'enable_debugging':
            success, msg = adb_manager.enable_debug_mode(device)
            return {'success': success, 'message': msg}

        elif action == 'tap_screen':
            success, msg = adb_manager.tap_screen(device, kwargs.get('x', 500), kwargs.get('y', 500))
            return {'success': success, 'message': msg}

        elif action == 'shell_input_text':
            success, msg = adb_manager.input_text(device, kwargs.get('text', ''))
            return {'success': success, 'message': msg}

        elif action == 'factory_reset':
            success, msg = adb_manager.factory_reset(device)
            return {'success': success, 'message': msg}

        elif action == 'disconnect':
            success, msg = adb_manager.disconnect_device(device)
            return {'success': success, 'message': msg}

        else:
            return {'success': False, 'message': f'Unknown action: {action}'}

    except Exception as e:
        logger.error(f"Error executing ADB action {action}: {e}")
        return {'success': False, 'message': str(e)}


if __name__ == '__main__':
    # Test ADB Manager
    manager = ADBManager()
    devices = manager.get_devices()
    print("Connected devices:", devices)
