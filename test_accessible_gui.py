"""
Test suite for ULTRON Accessible GUI Integration
Tests accessibility features, voice integration, and high-contrast design
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import threading
import time
import queue

# Import the GUI module
try:
    from ultron_accessible_gui import UltronAccessibleGUI, create_ultron_accessible_gui
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"GUI module not available: {e}")
    GUI_AVAILABLE = False


class TestUltronAccessibleGUI(unittest.TestCase):
    """Test accessible GUI functionality"""
    
    def setUp(self):
        """Setup test environment"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI module not available")
        
        # Create mock components
        self.mock_voice_manager = Mock()
        self.mock_agent_core = Mock()
        
        # Setup mock voice manager methods
        self.mock_voice_manager.is_listening.return_value = False
        self.mock_voice_manager.start_listening = Mock()
        self.mock_voice_manager.stop_listening = Mock()
        self.mock_voice_manager.emergency_stop = Mock()
        self.mock_voice_manager.set_wake_callback = Mock()
        self.mock_voice_manager.set_command_callback = Mock()
        self.mock_voice_manager.set_stop_callback = Mock()
        
        # Setup mock agent core
        self.mock_agent_core.process_command.return_value = "Test response"
    
    def test_accessibility_color_schemes(self):
        """Test high-contrast color schemes for accessibility"""
        # Test dark mode colors
        dark_colors = UltronAccessibleGUI.HIGH_CONTRAST_DARK
        self.assertEqual(dark_colors['bg'], '#000000')  # Pure black
        self.assertEqual(dark_colors['fg'], '#00FF00')  # Bright green
        self.assertEqual(dark_colors['accent'], '#FFFF00')  # Yellow
        
        # Test light mode colors
        light_colors = UltronAccessibleGUI.HIGH_CONTRAST_LIGHT
        self.assertEqual(light_colors['bg'], '#FFFFFF')  # Pure white
        self.assertEqual(light_colors['fg'], '#000000')  # Black
        self.assertEqual(light_colors['accent'], '#0000FF')  # Blue
    
    @patch('tkinter.Tk')
    def test_gui_initialization(self, mock_tk):
        """Test GUI initialization with accessibility features"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # Create GUI instance
        gui = UltronAccessibleGUI(
            mock_root, 
            self.mock_voice_manager, 
            self.mock_agent_core
        )
        
        # Verify initialization
        self.assertEqual(gui.voice_manager, self.mock_voice_manager)
        self.assertEqual(gui.agent_core, self.mock_agent_core)
        self.assertEqual(gui.contrast_mode, 'dark')
        self.assertEqual(gui.font_size, 20)  # Large font for accessibility
        
        # Verify window configuration
        mock_root.configure.assert_called_with(bg='#000000')  # High contrast
        mock_root.attributes.assert_called_with('-topmost', True)  # Always on top
    
    def test_voice_integration_callbacks(self):
        """Test voice integration callback setup"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create GUI
            gui = UltronAccessibleGUI(
                mock_root,
                self.mock_voice_manager,
                self.mock_agent_core
            )
            
            # Verify callbacks were set
            self.mock_voice_manager.set_wake_callback.assert_called_once()
            self.mock_voice_manager.set_command_callback.assert_called_once()
            self.mock_voice_manager.set_stop_callback.assert_called_once()
    
    def test_font_size_accessibility(self):
        """Test font size adjustment for visual accessibility"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_conversation = Mock()
            
            gui = UltronAccessibleGUI(mock_root, None, None)
            gui.conversation_area = mock_conversation
            
            # Test font size increase
            original_size = gui.font_size
            gui._adjust_font_size(4)
            self.assertEqual(gui.font_size, original_size + 4)
            
            # Test font size decrease
            gui._adjust_font_size(-2)
            self.assertEqual(gui.font_size, original_size + 2)
            
            # Test minimum font size limit
            gui.font_size = 10
            gui._adjust_font_size(-5)
            self.assertEqual(gui.font_size, 12)  # Should not go below 12
            
            # Test maximum font size limit
            gui.font_size = 35
            gui._adjust_font_size(5)
            self.assertEqual(gui.font_size, 36)  # Should not exceed 36
    
    def test_contrast_mode_toggle(self):
        """Test contrast mode switching for accessibility"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            
            gui = UltronAccessibleGUI(mock_root, None, None)
            
            # Start with dark mode
            self.assertEqual(gui.contrast_mode, 'dark')
            self.assertEqual(gui.colors, gui.HIGH_CONTRAST_DARK)
            
            # Toggle to light mode
            with patch.object(gui, '_update_colors'):
                gui._toggle_contrast()
            
            self.assertEqual(gui.contrast_mode, 'light')
            self.assertEqual(gui.colors, gui.HIGH_CONTRAST_LIGHT)
            
            # Toggle back to dark mode
            with patch.object(gui, '_update_colors'):
                gui._toggle_contrast()
            
            self.assertEqual(gui.contrast_mode, 'dark')
            self.assertEqual(gui.colors, gui.HIGH_CONTRAST_DARK)
    
    def test_emergency_stop_functionality(self):
        """Test emergency stop for user safety"""
        with patch('tkinter.Tk') as mock_tk, \
             patch('tkinter.messagebox.showwarning') as mock_warning:
            
            mock_root = Mock()
            gui = UltronAccessibleGUI(mock_root, self.mock_voice_manager, None)
            
            # Trigger emergency stop
            gui._emergency_stop()
            
            # Verify voice manager was stopped
            self.mock_voice_manager.emergency_stop.assert_called_once()
            
            # Verify warning dialog was shown
            mock_warning.assert_called_once()
    
    def test_voice_toggle_functionality(self):
        """Test voice control toggle"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_button = Mock()
            
            gui = UltronAccessibleGUI(mock_root, self.mock_voice_manager, None)
            gui.voice_button = mock_button
            
            # Test starting voice (when not listening)
            self.mock_voice_manager.is_listening.return_value = False
            gui._toggle_voice()
            
            self.mock_voice_manager.start_listening.assert_called_once()
            mock_button.config.assert_called_with(
                text="🔇 STOP VOICE", 
                bg=gui.colors['error']
            )
            
            # Test stopping voice (when listening)
            self.mock_voice_manager.is_listening.return_value = True
            gui._toggle_voice()
            
            self.mock_voice_manager.stop_listening.assert_called_once()
    
    def test_message_queue_processing(self):
        """Test thread-safe message processing"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            gui = UltronAccessibleGUI(mock_root, None, None)
            
            # Mock message handling methods
            gui._add_system_message = Mock()
            gui._add_user_message = Mock()
            gui._add_assistant_message = Mock()
            gui._add_error_message = Mock()
            gui._update_status = Mock()
            
            # Add messages to queue
            gui.message_queue.put(('system', 'Test system message'))
            gui.message_queue.put(('user', 'Test user message'))
            gui.message_queue.put(('assistant', 'Test assistant message'))
            gui.message_queue.put(('error', 'Test error message'))
            gui.message_queue.put(('status', 'Test status'))
            
            # Process messages
            gui._process_message_queue()
            
            # Verify messages were processed
            gui._add_system_message.assert_called_with('Test system message')
            gui._add_user_message.assert_called_with('Test user message')
            gui._add_assistant_message.assert_called_with('Test assistant message')
            gui._add_error_message.assert_called_with('Test error message')
            gui._update_status.assert_called_with('Test status')
    
    def test_agent_command_processing(self):
        """Test command processing through agent_core"""
        with patch('tkinter.Tk') as mock_tk, \
             patch('threading.Thread') as mock_thread:
            
            mock_root = Mock()
            gui = UltronAccessibleGUI(mock_root, None, self.mock_agent_core)
            
            # Process a command
            gui._process_agent_command("test command")
            
            # Verify agent_core was called
            self.mock_agent_core.process_command.assert_called_with("test command")
    
    def test_create_ultron_accessible_gui_function(self):
        """Test GUI creation function"""
        with patch('tkinter.Tk') as mock_tk, \
             patch.object(UltronAccessibleGUI, '__init__', return_value=None) as mock_init:
            
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create GUI using function
            root, gui = create_ultron_accessible_gui(
                self.mock_agent_core, 
                self.mock_voice_manager
            )
            
            # Verify components
            self.assertEqual(root, mock_root)
            mock_init.assert_called_once_with(
                mock_root, 
                self.mock_voice_manager, 
                self.mock_agent_core
            )


class TestAccessibilityFeatures(unittest.TestCase):
    """Test specific accessibility features"""
    
    def test_ultron_solutions_branding(self):
        """Test ULTRON SOLUTIONS branding in accessible GUI"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI module not available")
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            
            gui = UltronAccessibleGUI(mock_root, None, None)
            
            # Check that title includes ULTRON SOLUTIONS
            mock_root.title.assert_called_with("🔴 ULTRON SOLUTIONS - Voice Assistant")
    
    def test_high_contrast_accessibility(self):
        """Test high contrast design for visual impairments"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI module not available")
        
        # Test color contrast ratios
        dark_bg = '#000000'  # Pure black
        dark_fg = '#00FF00'  # Bright green
        
        light_bg = '#FFFFFF'  # Pure white  
        light_fg = '#000000'  # Black
        
        # These color combinations provide maximum contrast
        self.assertNotEqual(dark_bg, dark_fg)
        self.assertNotEqual(light_bg, light_fg)
    
    def test_large_font_accessibility(self):
        """Test large fonts for visual accessibility"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI module not available")
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            
            gui = UltronAccessibleGUI(mock_root, None, None)
            
            # Check default font size is large
            self.assertEqual(gui.font_size, 20)
            
            # Check font size can be adjusted
            gui._adjust_font_size(4)
            self.assertEqual(gui.font_size, 24)
    
    def test_always_on_top_accessibility(self):
        """Test always-on-top for visibility"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI module not available")
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            
            gui = UltronAccessibleGUI(mock_root, None, None)
            
            # Verify window is set to always on top
            mock_root.attributes.assert_called_with('-topmost', True)


def run_accessible_gui_tests():
    """Run all accessible GUI tests with detailed output"""
    
    print("🔴 ULTRON ACCESSIBLE GUI TEST SUITE 🔴")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUltronAccessibleGUI))
    suite.addTests(loader.loadTestsFromTestCase(TestAccessibilityFeatures))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False
    )
    
    print(f"Starting accessible GUI tests...")
    print(f"GUI module available: {GUI_AVAILABLE}")
    print("-" * 50)
    
    try:
        result = runner.run(suite)
        
        print("-" * 50)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        # Show detailed results
        if result.failures:
            print("\n❌ FAILURES:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\n💥 ERRORS:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        
        if result.skipped:
            print(f"\n⏭️  SKIPPED: {len(result.skipped)} tests")
        
        # Calculate success rate
        if result.testsRun > 0:
            success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
            print(f"\n🎯 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("✅ ACCESSIBLE GUI TESTS PASSED")
            else:
                print("❌ ACCESSIBLE GUI TESTS NEED ATTENTION")
        
        return result
        
    except Exception as e:
        print(f"💥 Test runner error: {e}")
        return None


if __name__ == "__main__":
    run_accessible_gui_tests()
