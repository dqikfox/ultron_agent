#!/usr/bin/env python3
"""
Debug app launch issue
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from adb_socket_integration import get_devices, execute_shell_command

def main():
    devices = get_devices()
    if not devices:
        print('No devices found')
        return

    device = devices[0]['serial']
    print(f'Device: {device}\n')

    # Get list of running packages
    print('Checking running apps...\n')
    result = execute_shell_command(device, 'pm list packages | grep -i sbrowser')

    if result.get('success'):
        if result.get('output'):
            print(f'✓ Browser package found: {result.get("output")}')
        else:
            print('✗ Browser package not in list')

    # Try alternative: get dumpsys
    print('\nChecking if app is in foreground...')
    result = execute_shell_command(device, 'dumpsys window windows | grep mCurrentFocus')

    if result.get('success'):
        output = result.get('output', '')
        if output:
            print(f'Current focus: {output[:100]}')
            if 'sbrowser' in output.lower():
                print('✓ Browser is in foreground!')
            else:
                print('✗ Browser not in foreground')
        else:
            print('Could not determine foreground app')

    print()

if __name__ == '__main__':
    main()
