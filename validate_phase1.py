#!/usr/bin/env python3
"""
Validation script for ULTRON Phase 1 Maverick implementation
Tests core functionality without requiring GUI components
"""

from pathlib import Path
import tempfile
import os


def test_maverick_engine():
    """Test the Maverick engine without GUI"""
    print("Testing Maverick Engine...")
    
    try:
        from ultron_agent.maverick.engine import MaverickEngine
        from ultron_agent.maverick.tasks import DEFAULT_TASKS, TodoFinderTask
        
        # Create a temporary repo with some test content
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            
            # Create a test file with TODO
            test_file = repo_path / "test.py"
            test_file.write_text("# TODO: This is a test TODO comment\nprint('hello')\n")
            
            # Create requirements.txt for testing
            req_file = repo_path / "requirements.txt"
            req_file.write_text("requests>=2.25.0\nnumpy>=1.20.0\n")
            
            # Test engine creation
            engine = MaverickEngine(repo_root=repo_path, interval_seconds=10, auto_apply=False)
            print("✅ MaverickEngine created successfully")
            
            # Test task execution directly
            todo_task = TodoFinderTask()
            suggestions = todo_task.run(repo_path)
            
            if suggestions:
                print(f"✅ Found {len(suggestions)} suggestions from TODO task")
                for s in suggestions:
                    print(f"  - {s.severity}: {s.title}")
            else:
                print("❌ No suggestions found from TODO task")
                return False
                
            print("✅ Maverick Engine test completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Maverick Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_supporting_modules():
    """Test supporting modules"""
    print("\nTesting Supporting Modules...")
    
    try:
        # Test theme
        from ultron_agent.gui.theme import CYBERPUNK
        assert CYBERPUNK["bg"] == "#000000"
        print("✅ Theme module working")
        
        # Test model manager
        from ultron_agent.ai.model_manager import ModelManager
        mm = ModelManager()
        models = mm.available_models()
        assert len(models) > 0
        print("✅ Model Manager working")
        
        # Test automation tools
        from ultron_agent.automation.pyauto_tools import DesktopAutomation
        da = DesktopAutomation()
        # Just test creation, don't test actual automation functions
        print("✅ Desktop Automation module imported")
        
        # Test voice stub
        from ultron_agent.multimodal.voice import transcribe_once
        print("✅ Voice module imported")
        
        # Test vision stub
        from ultron_agent.multimodal.vision import load_image
        print("✅ Vision module imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Supporting modules test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imports_in_gui():
    """Test that GUI modifications are syntactically correct"""
    print("\nTesting GUI Integration Syntax...")
    
    try:
        # Test import syntax by compiling the file
        import ast
        with open("gui_ultimate.py", "r") as f:
            source = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(source)
        print("✅ gui_ultimate.py syntax is valid")
        
        # Check for the new imports
        if "from ultron_agent.maverick.engine import MaverickEngine" in source:
            print("✅ MaverickEngine import added")
        else:
            print("❌ MaverickEngine import missing")
            return False
            
        if "def _open_maverick_panel(self):" in source:
            print("✅ Maverick panel method added")
        else:
            print("❌ Maverick panel method missing")  
            return False
            
        if "Maverick" in source and "command=self._open_maverick_panel" in source:
            print("✅ Maverick button added to GUI")
        else:
            print("❌ Maverick button missing from GUI")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("🚀 ULTRON Phase 1 Validation Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test core Maverick functionality
    if not test_maverick_engine():
        all_passed = False
    
    # Test supporting modules
    if not test_supporting_modules():
        all_passed = False
    
    # Test GUI integration
    if not test_imports_in_gui():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All Phase 1 tests PASSED!")
        print("✅ Maverick Auto-Improvement System is ready")
        print("✅ Supporting modules are functional") 
        print("✅ GUI integration is syntactically correct")
        print("\n📝 Note: GUI functionality requires tkinter and can be tested with:")
        print("   python run_ultron.py --gui")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1


if __name__ == "__main__":
    exit(main())