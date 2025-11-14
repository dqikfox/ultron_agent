#!/usr/bin/env python3
"""
Try launching app with am start using proper activity name
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from adb_socket_integration import get_devices, run_adb_command

def main():
    devices = get_devices()
    if not devices:
        print('No devices found')
        return

    device = devices[0]['serial']
    print(f'Device: {device}\n')

    # Method 1: Get main activity of the app
    print('Method 1: Using cmd package manager\n')
    result = run_adb_command(
        ['shell', 'cmd', 'package', 'resolve-activity',
         '--brief', 'com.sec.android.app.sbrowser'],
        device
    )

    if result.get('success'):
        print(f'Activity: {result.get("output")}')
    else:
        print(f'Error: {result.get("error")}')

    print()

    # Method 2: Launch using monkey (simpler)
    print('Method 2: Using monkey (force app to foreground)\n')
    result = run_adb_command(
        ['shell', 'monkey', '-p', 'com.sec.android.app.sbrowser',
         '-c', 'android.intent.category.LAUNCHER', '1'],
        device
    )

    print(f'Success: {result.get("success")}')
    if result.get('output'):
        print(f'Output: {result.get("output")[:100]}')
    if result.get('error'):
        print(f'Error: {result.get("error")[:100]}')

    print()

    # Method 3: Direct intent launch
    print('Method 3: Direct intent with MAIN action\n')
    result = run_adb_command(
        ['shell', 'am', 'start', '-a',
         'android.intent.action.MAIN', '-n',
         'com.sec.android.app.sbrowser/com.sec.android.app.sbrowser.SBrowserMainActivity'],
        device
    )

    print(f'Success: {result.get("success")}')
    print(f'Output: {result.get("output")}')
    if result.get('error'):
        print(f'Error: {result.get("error")}')

    print()

if __name__ == '__main__':
    main()
