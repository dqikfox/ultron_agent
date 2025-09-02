"""
Test suite for ULTRON Agent 3.0 enhancements
Tests PyAutoGUI integration, service management, and continuous improvement
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class TestPyAutoGUIIntegration(unittest.TestCase):
    """Test PyAutoGUI automation tool"""
    
    def setUp(self):
        # Mock display for headless testing
        os.environ['DISPLAY'] = ':99'
        
    def test_tool_creation(self):
        """Test that PyAutoGUI tool can be created"""
        try:
            # Import with exception handling for headless environment
            from tools.pyautogui_automation_tool import PyAutoGUIAutomationTool
            
            # This should work even in headless environment
            tool = PyAutoGUIAutomationTool()
            
            self.assertEqual(tool.name, "pyautogui_automation")
            self.assertIn("automation", tool.description.lower())
            self.assertIn("action", tool.parameters["properties"])
            
            # Test schema method
            schema = tool.schema()
            self.assertIn("function", schema)
            self.assertEqual(schema["function"]["name"], "pyautogui_automation")
            
            print("✅ PyAutoGUI tool creation test passed")
            
        except ImportError as e:
            print(f"⚠️  PyAutoGUI not available in headless environment: {e}")
            self.skipTest("PyAutoGUI requires display")
    
    def test_match_functionality(self):
        """Test that the tool correctly matches user input"""
        try:
            from tools.pyautogui_automation_tool import PyAutoGUIAutomationTool
            tool = PyAutoGUIAutomationTool()
            
            # Test positive matches
            self.assertTrue(tool.match("click on the button"))
            self.assertTrue(tool.match("take a screenshot"))
            self.assertTrue(tool.match("automate mouse movement"))
            self.assertTrue(tool.match("type some text"))
            
            # Test negative matches
            self.assertFalse(tool.match("calculate 2+2"))
            self.assertFalse(tool.match("weather forecast"))
            
            print("✅ PyAutoGUI match functionality test passed")
            
        except ImportError:
            self.skipTest("PyAutoGUI requires display")

class TestServiceManager(unittest.TestCase):
    """Test service management functionality"""
    
    def test_service_manager_creation(self):
        """Test service manager can be created"""
        try:
            from service_manager import UltronServiceManager
            
            manager = UltronServiceManager()
            
            # Check that default services are configured
            self.assertIn("ollama", manager.services)
            self.assertIn("agent_core", manager.services)
            
            # Check service properties
            ollama_service = manager.services["ollama"]
            self.assertEqual(ollama_service.port, 11434)
            self.assertTrue(ollama_service.required)
            
            print("✅ Service Manager creation test passed")
            
        except ImportError as e:
            print(f"❌ Service Manager import failed: {e}")
            self.fail(f"Service Manager should be importable: {e}")
    
    def test_service_configuration(self):
        """Test service configuration loading"""
        try:
            from service_manager import UltronServiceManager
            
            # Create temporary config
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                test_config = {
                    "version": "3.0",
                    "test_setting": True
                }
                json.dump(test_config, f)
                temp_config_path = f.name
            
            try:
                manager = UltronServiceManager(config_path=temp_config_path)
                self.assertEqual(manager.config["version"], "3.0")
                self.assertTrue(manager.config["test_setting"])
                
                print("✅ Service configuration test passed")
                
            finally:
                Path(temp_config_path).unlink()
                
        except Exception as e:
            self.fail(f"Service configuration test failed: {e}")

class TestContinuousImprovement(unittest.TestCase):
    """Test continuous improvement system"""
    
    def test_improvement_system_creation(self):
        """Test improvement system can be created"""
        try:
            from continuous_improvement_system import ContinuousImprovementSystem
            
            system = ContinuousImprovementSystem()
            
            self.assertIsInstance(system.suggestions, list)
            self.assertIsInstance(system.diagnostics, list)
            self.assertFalse(system.active)  # Should start inactive
            
            print("✅ Continuous Improvement system creation test passed")
            
        except Exception as e:
            self.fail(f"Continuous Improvement system creation failed: {e}")
    
    def test_suggestion_creation(self):
        """Test improvement suggestion creation"""
        try:
            from continuous_improvement_system import ImprovementSuggestion
            
            suggestion = ImprovementSuggestion(
                id="test_suggestion",
                category="functionality",
                priority="medium",
                title="Test suggestion",
                description="Test description",
                suggested_action="Test action",
                confidence=0.8,
                auto_applicable=False
            )
            
            self.assertEqual(suggestion.id, "test_suggestion")
            self.assertEqual(suggestion.priority, "medium")
            self.assertEqual(suggestion.confidence, 0.8)
            self.assertIsNotNone(suggestion.timestamp)
            
            print("✅ Improvement suggestion creation test passed")
            
        except Exception as e:
            self.fail(f"Suggestion creation test failed: {e}")

class TestSystemIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def test_config_file_exists(self):
        """Test that main configuration file exists"""
        config_file = Path("ultron_config.json")
        self.assertTrue(config_file.exists(), "ultron_config.json should exist")
        
        # Test that it's valid JSON
        try:
            with open(config_file) as f:
                config = json.load(f)
            self.assertIn("version", config)
            print("✅ Configuration file test passed")
        except json.JSONDecodeError:
            self.fail("ultron_config.json should be valid JSON")
    
    def test_tools_directory_structure(self):
        """Test tools directory structure"""
        tools_dir = Path("tools")
        self.assertTrue(tools_dir.exists(), "tools directory should exist")
        self.assertTrue((tools_dir / "__init__.py").exists(), "tools should be a Python package")
        
        # Check for our new PyAutoGUI tool
        pyautogui_tool = tools_dir / "pyautogui_automation_tool.py"
        self.assertTrue(pyautogui_tool.exists(), "PyAutoGUI tool should exist")
        
        print("✅ Tools directory structure test passed")

class TestEnhancementFeatures(unittest.TestCase):
    """Test specific enhancement features"""
    
    def test_pyautogui_feature_coverage(self):
        """Test that PyAutoGUI tool covers all required features"""
        try:
            from tools.pyautogui_automation_tool import PyAutoGUIAutomationTool
            
            tool = PyAutoGUIAutomationTool()
            actions = tool.parameters["properties"]["action"]["enum"]
            
            # Check for key PyAutoGUI features mentioned in specification
            required_features = [
                "click", "screenshot", "type_text", "press_key", "hotkey",
                "move_to", "drag", "scroll", "locate_image"
            ]
            
            for feature in required_features:
                self.assertIn(feature, actions, f"Feature {feature} should be available")
            
            print(f"✅ PyAutoGUI feature coverage test passed ({len(actions)} actions available)")
            
        except ImportError:
            self.skipTest("PyAutoGUI requires display")
    
    def test_service_health_checking(self):
        """Test service health checking functionality"""
        try:
            from service_manager import UltronServiceManager
            
            manager = UltronServiceManager()
            
            # Test health check method exists and is callable
            self.assertTrue(callable(manager.check_service_health))
            
            # Test with non-existent service
            result = manager.check_service_health("nonexistent_service")
            self.assertFalse(result)
            
            print("✅ Service health checking test passed")
            
        except Exception as e:
            self.fail(f"Service health checking test failed: {e}")

def run_comprehensive_tests():
    """Run all tests and provide summary"""
    
    print("🧪 ULTRON Agent 3.0 Enhancement Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPyAutoGUIIntegration,
        TestServiceManager, 
        TestContinuousImprovement,
        TestSystemIntegration,
        TestEnhancementFeatures
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Test Results Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    if result.errors:
        print("\n🚨 Errors:")  
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    if result.skipped:
        print("\n⚠️  Skipped:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n🎉 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)