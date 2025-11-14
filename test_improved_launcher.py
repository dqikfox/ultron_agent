#!/usr/bin/env python3
"""
Test improved app launcher with auto-detection
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from adb_socket_integration import get_devices, launch_app

def main():
    devices = get_devices()
    if not devices:
        print('No device found')
        return

    device = devices[0]['serial']
    print(f'Device: {device}\n')

    print('Launching Samsung Internet Browser')
    print('(with auto-detected activity)...\n')

    result = launch_app(device, 'com.sec.android.app.sbrowser')

    print(f'✓ Success: {result.get("success")}')
    print(f'✓ Output: {result.get("output")}')

    if result.get('error'):
        print(f'⚠ Error: {result.get("error")}')

    print()

if __name__ == '__main__':
    main()
