#!/usr/bin/env python3
"""
Test launching an app on connected device
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from adb_socket_integration import get_installed_apps, launch_app, get_devices

def main():
    # Get device
    devices = get_devices()
    if not devices:
        print('❌ No devices found')
        return

    device = devices[0]['serial']
    print(f'\n📱 Device: {device}\n')

    # Get installed apps
    apps = get_installed_apps(device)
    print(f'📦 Found {len(apps)} installed apps\n')

    # Find a common app to launch
    target_apps = [
        'com.sec.android.app.sbrowser',  # Samsung Internet
        'com.android.chrome',             # Chrome
        'com.android.settings'            # Settings
    ]

    app_to_launch = None
    for target in target_apps:
        for app in apps:
            if app['package'] == target:
                app_to_launch = app
                break
        if app_to_launch:
            break

    if not app_to_launch:
        app_to_launch = apps[0]

    package = app_to_launch['package']
    name = app_to_launch.get('name', 'Unknown')

    print(f'🚀 Launching: {name} ({package})\n')

    # Launch the app
    result = launch_app(device, package)

    print('📊 Launch Result:')
    print(f'   ✓ Success: {result.get("success")}')
    if result.get('output'):
        print(f'   ℹ Output: {result.get("output")}')
    if result.get('error'):
        print(f'   ⚠ Error: {result.get("error")}')

    print()

if __name__ == '__main__':
    main()
