#!/usr/bin/env python3
"""
Headless testing solution for GUI components in environments without tkinter/display
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_availability():
    """Test GUI availability and provide setup guidance"""
    print("🧪 Testing GUI Availability...")
    
    # Test display
    display_available = bool(os.environ.get('DISPLAY'))
    print(f"📺 Display available: {display_available}")
    
    # Test tkinter
    try:
        import tkinter
        tkinter_available = True
        print("✅ tkinter module available")
    except ImportError:
        tkinter_available = False
        print("❌ tkinter module not available")
    
    # Test PIL
    try:
        from PIL import Image
        pil_available = True
        print("✅ PIL/Pillow available")
    except ImportError:
        pil_available = False
        print("❌ PIL/Pillow not available")
    
    # Overall GUI status
    gui_possible = tkinter_available and (display_available or "CI" in os.environ)
    
    if gui_possible:
        print("✅ GUI testing is possible")
    else:
        print("⚠️  GUI testing not possible - headless mode required")
        print("\n💡 To enable GUI testing:")
        if not tkinter_available:
            print("   • Install tkinter (usually included with Python)")
            print("   • On Ubuntu: sudo apt-get install python3-tk")
        if not pil_available:
            print("   • Install Pillow: pip install pillow")
        if not display_available and "CI" not in os.environ:
            print("   • Set up X11 forwarding or virtual display")
            print("   • For CI: set DISPLAY=:99 and use xvfb")
    
    return {
        'display': display_available,
        'tkinter': tkinter_available,
        'pil': pil_available,
        'gui_possible': gui_possible
    }

def test_stable_diffusion_integration_headless():
    """Test Stable Diffusion integration without GUI dependencies"""
    print("\n🧪 Testing Stable Diffusion Integration (Headless Mode)...")
    
    results = {
        'tool_import': False,
        'gui_import': False,
        'pokedex_integration': False,
        'files_exist': False
    }
    
    # Test tool import
    try:
        from tools.image_generation_tool import ImageGenerationTool
        print("✅ Image generation tool imported successfully")
        results['tool_import'] = True
    except Exception as e:
        print(f"❌ Tool import failed: {e}")
    
    # Test GUI import (should work even without tkinter due to fallbacks)
    try:
        from stable_diffusion_gui import StableDiffusionGUI
        print("✅ Stable Diffusion GUI imported successfully")
        results['gui_import'] = True
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
    
    # Test Pokedex integration
    try:
        from pokedex_ultron_gui import PokedexUltronGUI
        if hasattr(PokedexUltronGUI, '_launch_stable_diffusion_gui'):
            print("✅ Pokedex GUI has Stable Diffusion integration")
            results['pokedex_integration'] = True
        else:
            print("❌ Pokedex GUI missing Stable Diffusion integration")
    except Exception as e:
        print(f"❌ Pokedex GUI test failed: {e}")
    
    # Test file existence
    required_files = [
        'stable_diffusion_colab.ipynb',
        'stable_diffusion_gui.py',
        'tools/image_generation_tool.py',
        'STABLE_DIFFUSION_GUIDE.md'
    ]
    
    all_files_exist = True
    for file_path in required_files:
        file_exists = (project_root / file_path).exists()
        status = "✅" if file_exists else "❌"
        print(f"{status} {file_path}: {'exists' if file_exists else 'missing'}")
        if not file_exists:
            all_files_exist = False
    
    results['files_exist'] = all_files_exist
    
    return results

def create_test_environment_guide():
    """Create a guide for testing in different environments"""
    guide = """
# GUI Testing Environment Setup Guide

## For Developers

### Local Development (with GUI)
```bash
# Install required packages
pip install pillow tkinter

# Run with GUI
python stable_diffusion_gui.py
```

### Headless Environments (CI/Docker)
```bash
# Install headless testing dependencies
pip install pillow

# For virtual display (if needed)
sudo apt-get install xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# Run headless tests
python test_gui_headless.py
```

### Testing Strategy
1. **Full GUI Testing**: Available when tkinter and display are present
2. **Import Testing**: Verify modules can be imported without GUI
3. **Mock Testing**: Use mocks for GUI components in unit tests
4. **Integration Testing**: Test API endpoints and business logic

### Environment Detection
The system automatically detects:
- Display availability (DISPLAY environment variable)
- tkinter module availability  
- PIL/Pillow availability
- CI environment markers

### Fallback Behavior
- GUI components gracefully fallback to headless mode
- Critical functionality remains testable
- Clear error messages guide users to solutions
"""
    
    with open(project_root / "GUI_TESTING_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("📝 Created GUI_TESTING_GUIDE.md")

def main():
    """Run all headless tests and create guidance"""
    print("🚀 ULTRON Stable Diffusion - Headless Testing Suite")
    print("=" * 60)
    
    # Test GUI availability
    gui_status = test_gui_availability()
    
    # Test integration
    integration_results = test_stable_diffusion_integration_headless()
    
    # Create guidance
    create_test_environment_guide()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"GUI Environment: {'✅ Available' if gui_status['gui_possible'] else '⚠️  Headless'}")
    print(f"Tool Integration: {'✅ Working' if integration_results['tool_import'] else '❌ Failed'}")
    print(f"GUI Import: {'✅ Working' if integration_results['gui_import'] else '❌ Failed'}")
    print(f"Pokedex Integration: {'✅ Working' if integration_results['pokedex_integration'] else '❌ Failed'}")
    print(f"Required Files: {'✅ Complete' if integration_results['files_exist'] else '❌ Missing'}")
    
    # Overall status
    critical_tests = [
        integration_results['tool_import'],
        integration_results['gui_import'],
        integration_results['files_exist']
    ]
    
    if all(critical_tests):
        print("\n🎯 Status: ✅ READY - All critical components working")
        print("💡 GUI features will work when tkinter/display are available")
    else:
        print("\n🎯 Status: ⚠️  ISSUES - Some components need attention")
    
    return all(critical_tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)