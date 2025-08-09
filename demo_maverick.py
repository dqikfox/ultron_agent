#!/usr/bin/env python3
"""
Demo script showing ULTRON Phase 1 Maverick functionality
Creates test files to demonstrate different suggestion types
"""

import os
import time
from pathlib import Path


def create_demo_files():
    """Create test files to demonstrate Maverick suggestions"""
    print("Creating demo files to test Maverick suggestions...")
    
    # Create a Python file with TODO
    demo_py = Path("demo_todo_example.py")
    demo_py.write_text("""#!/usr/bin/env python3
# TODO: This is a test TODO that Maverick should detect
# TODO: Another TODO item for testing

def hello_world():
    # TODO: Implement error handling here
    print("Hello from demo file!")
    
if __name__ == "__main__":
    hello_world()
""")
    
    # Create a Python file that references a missing image
    demo_gui = Path("demo_gui_with_missing_image.py") 
    demo_gui.write_text("""
import tkinter as tk
from PIL import Image

# This will be detected by ImagePathValidatorTask
image_path = "resources/images/missing_demo_image.png"
background_image = "resources/images/another_missing_image.jpg"

def load_demo_images():
    # Maverick will suggest adding these missing assets
    img = Image.open(image_path)
    bg = Image.open(background_image)
""")
    
    # Create a markdown file with TODO
    demo_md = Path("demo_notes.md")
    demo_md.write_text("""# Demo Notes

This is a demo markdown file.

## Tasks

- TODO: Review the Maverick implementation
- TODO: Add more test cases
- Complete other items

## Notes

The Maverick system should find the TODO items above.
""")
    
    print("✅ Demo files created:")
    print(f"  - {demo_py}")
    print(f"  - {demo_gui}")  
    print(f"  - {demo_md}")
    

def run_maverick_demo():
    """Run a quick Maverick scan demo"""
    print("\n🚀 Starting Maverick Demo...")
    
    from ultron_agent.maverick.engine import MaverickEngine
    
    # Create engine with short interval for demo
    engine = MaverickEngine(repo_root=Path("."), interval_seconds=5, auto_apply=False)
    
    # Add observer to print results
    def print_suggestions(suggestions):
        print(f"\n📋 Maverick found {len(suggestions)} suggestions:")
        for i, s in enumerate(suggestions, 1):
            print(f"{i:2}. [{s.severity.upper()}] {s.title}")
            if s.file:
                location = f"{s.file}"
                if s.line:
                    location += f":{s.line}"
                print(f"     File: {location}")
            if s.action:
                print(f"     Action: {s.action}")
            print()
    
    engine.observe(print_suggestions)
    
    # Start engine
    engine.start()
    print("⚡ Maverick engine started, scanning repository...")
    
    # Let it run for a bit
    try:
        time.sleep(8)  # Wait for at least one scan
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()
        print("\n✅ Maverick demo completed")
    

def cleanup_demo_files():
    """Clean up demo files"""
    print("\n🧹 Cleaning up demo files...")
    demo_files = [
        "demo_todo_example.py",
        "demo_gui_with_missing_image.py", 
        "demo_notes.md"
    ]
    
    for file in demo_files:
        try:
            Path(file).unlink()
            print(f"  Removed {file}")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    print("🎭 ULTRON Phase 1 Maverick Demo")
    print("=" * 40)
    
    try:
        create_demo_files()
        run_maverick_demo()
        
        print("\n" + "=" * 40)
        print("🎉 Demo completed successfully!")
        print("\nTo run Maverick manually:")
        print("  python run_ultron.py --maverick --interval 30")
        print("\nTo open the GUI (requires tkinter):")
        print("  python run_ultron.py --gui")
        
    finally:
        cleanup_demo_files()