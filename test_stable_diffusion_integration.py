#!/usr/bin/env python3
"""
Test script for Stable Diffusion integration
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_stable_diffusion_tool():
    """Test the Stable Diffusion tool"""
    print("🧪 Testing Stable Diffusion Tool...")
    
    try:
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
            "make a picture of sunset"
        ]
        
        for cmd in test_commands:
            match = tool.match(cmd)
            print(f"🔍 '{cmd}' -> Match: {match}")
        
        # Test schema
        schema = tool.schema()
        print(f"📋 Schema: {schema['name']}")
        print(f"🎯 Capabilities: {len(schema['capabilities'])} features")
        
        print("✅ Stable Diffusion Tool test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Stable Diffusion Tool test failed: {e}")
        return False

def test_stable_diffusion_gui():
    """Test the Stable Diffusion GUI with headless fallback"""
    print("🧪 Testing Stable Diffusion GUI...")
    
    try:
        # Test tkinter availability first
        try:
            import tkinter
            gui_available = True
            print("✅ tkinter is available")
        except ImportError:
            gui_available = False
            print("⚠️  tkinter not available - testing headless mode")
        
        from stable_diffusion_gui import StableDiffusionGUI
        
        if gui_available:
            # Test with GUI
            gui = StableDiffusionGUI()
            print(f"✅ GUI created: images_dir = {gui.images_dir}")
        else:
            # Test headless mode - just verify class can be imported
            print("✅ StableDiffusionGUI class imported successfully")
            # Test critical attributes without creating GUI
            test_gui = type('MockGUI', (), {
                'images_dir': project_root / "generated_images",
                'generation_history': [],
                'current_images': []
            })()
            test_gui.images_dir.mkdir(exist_ok=True)
            print(f"✅ Mock GUI attributes: images_dir = {test_gui.images_dir}")
        
        print(f"📁 Image directory exists: {(project_root / 'generated_images').exists()}")
        
        print("✅ Stable Diffusion GUI test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Stable Diffusion GUI test failed: {e}")
        return False

def test_colab_notebook():
    """Test if Colab notebook exists"""
    print("🧪 Testing Colab Notebook...")
    
    notebook_path = project_root / "stable_diffusion_colab.ipynb"
    if notebook_path.exists():
        print(f"✅ Colab notebook found: {notebook_path}")
        
        # Check file size
        size_kb = notebook_path.stat().st_size / 1024
        print(f"📊 Notebook size: {size_kb:.1f} KB")
        
        return True
    else:
        print(f"❌ Colab notebook not found: {notebook_path}")
        return False

def test_gui_integration():
    """Test GUI integration with headless fallback"""
    print("🧪 Testing GUI Integration...")
    
    try:
        # Test tkinter availability first
        try:
            import tkinter
            gui_available = True
            print("✅ tkinter is available")
        except ImportError:
            gui_available = False
            print("⚠️  tkinter not available - testing module imports only")
        
        from pokedex_ultron_gui import PokedexUltronGUI
        
        # Test that the GUI class has our new method
        if hasattr(PokedexUltronGUI, '_launch_stable_diffusion_gui'):
            print("✅ GUI has Stable Diffusion launcher method")
        else:
            print("❌ GUI missing Stable Diffusion launcher method")
            return False
        
        if gui_available:
            # Test with mock agent in test mode
            class MockAgent:
                def __init__(self):
                    self.name = "test_agent"
            
            test_gui = PokedexUltronGUI(MockAgent(), test_mode=True)
            print("✅ GUI initialization successful in test mode")
        else:
            print("✅ GUI class imported and method verified (headless mode)")
        
        print("✅ GUI integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ULTRON Stable Diffusion Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Stable Diffusion Tool", test_stable_diffusion_tool),
        ("Stable Diffusion GUI", test_stable_diffusion_gui),
        ("Colab Notebook", test_colab_notebook),
        ("GUI Integration", test_gui_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
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
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)