#!/usr/bin/env python3
"""
Run the mobile web interface server
"""

from tools.mobile_web_interface_tool import MobileWebInterfaceTool
import time

if __name__ == "__main__":
    tool = MobileWebInterfaceTool()
    result = tool.start_interface()
    print(result)

    # Keep the process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
