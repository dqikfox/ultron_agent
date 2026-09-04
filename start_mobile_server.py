#!/usr/bin/env python3
"""
ULTRON Agent Mobile Web Interface Server
Run this script to start the mobile web interface server persistently.
"""

from tools.mobile_web_interface_tool import MobileWebInterfaceTool
import logging
import sys
import time

def main():
    """Start the mobile web interface server"""
    try:
        print("🚀 Starting ULTRON Agent Mobile Web Interface Server...")
        print("=" * 60)

        # Create and initialize the tool
        tool = MobileWebInterfaceTool()
        print("✅ Web interface initialized")

        # Start the server using the tool's method
        result = tool.start_interface()
        print(result)

        # Keep the script running
        print("\n🔄 Server is running in background thread...")
        print("Press Ctrl+C to stop the server")

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            tool.stop_interface()

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        tool.stop_interface()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
