#!/usr/bin/env python3
"""Test autonomous GUI integration"""

import webbrowser
import time
import subprocess
import sys

def test_autonomous_gui():
    """Test the autonomous GUI features"""
    
    print("🤖 Testing ULTRON Autonomous GUI Integration")
    print("=" * 50)
    
    # Start web GUI server
    print("1. Starting web GUI server...")
    try:
        gui_process = subprocess.Popen(
            ["python", "web_gui_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("2. Waiting for server to initialize...")
        time.sleep(3)
        
        # Open browser to autonomous section
        print("3. Opening autonomous interface...")
        url = "http://localhost:8080/#autonomous"
        webbrowser.open(url)
        
        print("✅ Autonomous GUI test completed!")
        print()
        print("Manual verification steps:")
        print("1. Navigate to the AUTONOMOUS section in the GUI")
        print("2. Click 'Start Autonomous Mode' button")
        print("3. Click 'Run Integration Test' button")
        print("4. Verify buttons respond and show status updates")
        print()
        print("Press Ctrl+C to stop the server...")
        
        # Keep server running for manual testing
        try:
            gui_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            gui_process.terminate()
            gui_process.wait()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_autonomous_gui()
    sys.exit(0 if success else 1)