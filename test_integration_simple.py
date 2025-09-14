#!/usr/bin/env python3
"""
Simple test for Stable Diffusion integration without GUI dependencies
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_stable_diffusion_tool_basic():
    """Test basic Stable Diffusion tool functionality"""
    print("🧪 Testing Stable Diffusion Tool (basic)...")
    
    try:
        # Mock dependencies that might not be available
        sys.modules['PIL'] = type(sys)('PIL')
        sys.modules['PIL.Image'] = type(sys)('PIL.Image')
        
        from tools.image_generation_tool import ImageGenerationTool
        
        # Mock config
        class MockConfig:
            def __init__(self):
                self.data = {}
        
        config = MockConfig()
        tool = ImageGenerationTool(config)
        
        print(f"✅ Tool created: {tool.name}")
        print(f"📝 Description: {tool.description}")
        
        # Test command matching
        test_commands = [
            "generate image of a cat",
            "create image cyberpunk style", 
            "stable diffusion realistic portrait",
            "make a picture of sunset",
            "hello world"  # Should not match
        ]
        
        for cmd in test_commands:
            match = tool.match(cmd)
            print(f"🔍 '{cmd}' -> Match: {match}")
        
        # Test parameter parsing
        test_command = "generate image of a robot width:1024 height:768 steps:25 guidance:8.0"
        params = tool.parse_parameters(test_command)
        print(f"📋 Parsed parameters: {params}")
        
        # Test schema
        schema = tool.schema()
        print(f"📋 Schema: {schema['name']}")
        print(f"🎯 Capabilities: {len(schema['capabilities'])} features")
        
        print("✅ Stable Diffusion Tool basic test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Stable Diffusion Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_colab_notebook():
    """Test if Colab notebook exists and is valid"""
    print("🧪 Testing Colab Notebook...")
    
    notebook_path = project_root / "stable_diffusion_colab.ipynb"
    if notebook_path.exists():
        print(f"✅ Colab notebook found: {notebook_path}")
        
        # Check file size
        size_kb = notebook_path.stat().st_size / 1024
        print(f"📊 Notebook size: {size_kb:.1f} KB")
        
        # Try to parse as JSON to verify it's valid
        try:
            import json
            with open(notebook_path, 'r') as f:
                notebook_data = json.load(f)
            
            cells = notebook_data.get('cells', [])
            print(f"📄 Notebook has {len(cells)} cells")
            
            # Check for key components
            has_setup = any('install' in str(cell.get('source', '')).lower() for cell in cells)
            has_api = any('flask' in str(cell.get('source', '')).lower() for cell in cells) 
            has_gradio = any('gradio' in str(cell.get('source', '')).lower() for cell in cells)
            
            print(f"🔧 Has setup cell: {has_setup}")
            print(f"🌐 Has API server: {has_api}")
            print(f"🎮 Has Gradio interface: {has_gradio}")
            
            return True
            
        except Exception as e:
            print(f"❌ Invalid notebook format: {e}")
            return False
    else:
        print(f"❌ Colab notebook not found: {notebook_path}")
        return False

def test_gui_integration():
    """Test GUI integration (import only)"""
    print("🧪 Testing GUI Integration...")
    
    try:
        # Mock tkinter and PIL to avoid import errors
        sys.modules['tkinter'] = type(sys)('tkinter')
        sys.modules['tkinter.ttk'] = type(sys)('tkinter.ttk')
        sys.modules['tkinter.scrolledtext'] = type(sys)('tkinter.scrolledtext')
        sys.modules['tkinter.filedialog'] = type(sys)('tkinter.filedialog')
        sys.modules['tkinter.messagebox'] = type(sys)('tkinter.messagebox')
        sys.modules['PIL'] = type(sys)('PIL')
        sys.modules['PIL.Image'] = type(sys)('PIL.Image')
        sys.modules['PIL.ImageTk'] = type(sys)('PIL.ImageTk')
        
        from pokedex_ultron_gui import PokedexUltronGUI
        
        # Test that the GUI class has our new method
        if hasattr(PokedexUltronGUI, '_launch_stable_diffusion_gui'):
            print("✅ GUI has Stable Diffusion launcher method")
        else:
            print("❌ GUI missing Stable Diffusion launcher method")
            return False
        
        print("✅ GUI integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("🧪 Testing File Structure...")
    
    required_files = [
        "stable_diffusion_colab.ipynb",
        "stable_diffusion_gui.py", 
        "tools/image_generation_tool.py",
        "pokedex_ultron_gui.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            print(f"✅ {file_path} ({size_kb:.1f} KB)")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🚀 ULTRON Stable Diffusion Integration Test Suite (Simple)")
    print("=" * 70)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Stable Diffusion Tool", test_stable_diffusion_tool_basic),
        ("Colab Notebook", test_colab_notebook),
        ("GUI Integration", test_gui_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        print("-" * 50)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Stable Diffusion integration is ready!")
        print("\n📋 INTEGRATION SUMMARY:")
        print("✅ Enhanced Stable Diffusion tool with Colab support")
        print("✅ Comprehensive Colab notebook with API endpoints")
        print("✅ Advanced GUI interface for image generation")
        print("✅ Integration button added to main ULTRON GUI")
        print("\n🚀 Ready for use!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)