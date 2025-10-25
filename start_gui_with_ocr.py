#!/usr/bin/env python3
"""
Start ULTRON GUI with OCR Integration
Correct port configuration: GUI on 8080, OCR API on 5001
"""

import subprocess
import time
import webbrowser
import os

def start_ocr_integration():
    """Start OCR integration server on port 5001"""
    print("Starting OCR Integration Server on port 5001...")
    return subprocess.Popen([
        "python", "gui_ocr_integration.py"
    ], cwd="c:\\Projects\\ultron_agent")

def start_gui():
    """Start ULTRON GUI on port 8080"""
    print("Starting ULTRON GUI on port 8080...")
    return subprocess.Popen([
        "python", "-m", "http.server", "8080"
    ], cwd="c:\\Projects\\ultron_agent\\gui\\ultron_enhanced\\web")

def main():
    print("ULTRON Agent - GUI with OCR Integration")
    print("=" * 50)
    
    # Start OCR integration server
    ocr_process = start_ocr_integration()
    time.sleep(2)
    
    # Start GUI server
    gui_process = start_gui()
    time.sleep(3)
    
    print("\nServices Started:")
    print("✓ OCR Integration API: http://localhost:5001")
    print("✓ ULTRON GUI: http://localhost:8080")
    print("\nOpening ULTRON GUI...")
    
    # Open GUI in browser
    webbrowser.open("http://localhost:8080")
    
    print("\nGUI with OCR Integration is now running!")
    print("\nTo use OCR features:")
    print("1. Navigate to the Vision section in the GUI")
    print("2. Click 'CAPTURE' to take screenshot with OCR analysis")
    print("3. Results saved to Pictures/Screenshots/descriptions/")
    
    print("\nPress Ctrl+C to stop servers")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        ocr_process.terminate()
        gui_process.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    main()