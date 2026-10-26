"""
Enhanced GUI Test for ULTRON Agent 2 with Voice and Logging Integration
Tests the GUI with working voice system and comprehensive logging
"""

import tkinter as tk
import threading
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from gui_ultimate import UltimateAgentGUI
except ImportError:
    print("❌ Could not import UltimateAgentGUI")
    UltimateAgentGUI = None

try:
    from voice_manager import UltronVoiceManager
except ImportError:
    print("❌ Could not import UltronVoiceManager")
    UltronVoiceManager = None

try:
    from action_logger import ActionLogger
except ImportError:
    print("❌ Could not import ActionLogger")
    ActionLogger = None

class MockAgentWithVoice:
    """Enhanced mock agent with working voice and logging"""
    
    def __init__(self):
        self.config = MockConfig()
        self.voice_manager = None
        self.action_logger = None
        
        # Initialize real voice manager
        try:
            if UltronVoiceManager:
                self.voice_manager = UltronVoiceManager()
                print("✅ Voice Manager initialized in mock agent")
        except Exception as e:
            print(f"❌ Voice Manager failed: {e}")
        
        # Initialize real action logger
        try:
            if ActionLogger:
                self.action_logger = ActionLogger("gui_test.log")
                self.action_logger.log_action("GUI_TEST_START", "Starting GUI test with voice and logging")
                print("✅ Action Logger initialized in mock agent")
        except Exception as e:
            print(f"❌ Action Logger failed: {e}")
        
        # Mock other components
        self.brain = MockBrain()
        self.tools = [MockTool("screenshot_tool", "Take accessibility screenshot")]
        self.memory = MockMemory()
    
    def handle_text(self, text):
        """Handle user text input with voice response and logging"""
        try:
            # Log user input
            if self.action_logger:
                self.action_logger.log_user_input(text, "gui")
            
            # Generate response based on accessibility context
            if "screenshot" in text.lower():
                response = "I'll take a screenshot for you. This helps users with cognitive disabilities save information they need to remember."
            elif "help" in text.lower():
                response = "ULTRON Agent 2 is ready to assist you. I can help with mouse control, keyboard input, taking screenshots, and more accessibility features."
            elif "voice" in text.lower():
                response = "Voice system is active. I can provide audio feedback for all actions to help users with visual impairments."
            else:
                response = f"I understand you said: {text}. How can I help you with computer accessibility today?"
            
            # Log AI response
            if self.action_logger:
                self.action_logger.log_ai_response(response, "gui-mock", 0.5)
            
            # Speak response if voice manager available
            if self.voice_manager and hasattr(self.voice_manager, 'speak'):
                try:
                    self.voice_manager.speak(response)
                    if self.action_logger:
                        self.action_logger.log_voice_action("TTS_RESPONSE", response, "voice_manager")
                except Exception as e:
                    print(f"Voice response failed: {e}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error handling text: {e}"
            print(error_msg)
            if self.action_logger:
                self.action_logger.log_error("GUI_TEXT_HANDLING", error_msg)
            return "I encountered an error, but I'm still here to help you."
    
    def simulate_accessibility_actions(self):
        """Simulate accessibility-focused actions"""
        actions = [
            ("MOUSE_CLICK", "Helping user with motor impairment click button"),
            ("SCREEN_READ", "Reading screen content for visually impaired user"),
            ("VOICE_COMMAND", "Processing voice command for hands-free operation"),
            ("TEXT_INPUT", "Typing text for user with limited mobility"),
            ("SCREENSHOT", "Taking screenshot for cognitive accessibility support")
        ]
        
        for action_type, description in actions:
            if self.action_logger:
                self.action_logger.log_accessibility_action(
                    action_type.lower().replace('_', '_'),
                    description,
                    "GUI simulation test"
                )
            
            if self.voice_manager:
                try:
                    self.voice_manager.speak(f"Completed {description}")
                except:
                    pass
            
            time.sleep(1)  # Small delay between actions

class MockConfig:
    def __init__(self):
        self.data = {
            'llm_model': 'qwen2.5-coder:1.5b',  # Memory optimized
            'voice_engine': 'voice_manager',
            'use_voice': True,
            'use_gui': True,
            'use_vision': True,
            'accessibility_mode': True
        }
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        print(f"Config updated: {key} = {value}")
    
    def save_config(self):
        print("Config saved (mock)")

class MockBrain:
    def __init__(self):
        self.context = "ULTRON Agent 2 - Accessibility-focused AI assistant"
    
    def think(self, input_text):
        return f"Processing accessibility request: {input_text}"

class MockTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def execute(self, *args):
        return f"Executed {self.name} for accessibility support"

class MockMemory:
    def __init__(self):
        self.memories = []
    
    def add(self, memory):
        self.memories.append(memory)

def test_gui_with_voice_and_logging():
    """Test the GUI with integrated voice and logging"""
    print("🚀 Starting ULTRON Agent 2 GUI Test with Voice & Logging")
    print("♿ Focus: Testing accessibility features and user experience")
    print("=" * 60)
    
    # Create mock agent with real voice and logging
    agent = MockAgentWithVoice()
    
    if not UltimateAgentGUI:
        print("❌ GUI not available - cannot run test")
        return
    
    try:
        # Create GUI
        print("🖥️ Initializing GUI...")
        gui = UltimateAgentGUI(agent, test_mode=False)
        
        # Start accessibility simulation in background
        def simulate_actions():
            time.sleep(3)  # Wait for GUI to load
            print("🎭 Starting accessibility action simulation...")
            agent.simulate_accessibility_actions()
        
        simulation_thread = threading.Thread(target=simulate_actions, daemon=True)
        simulation_thread.start()
        
        # Announce GUI ready with voice
        if agent.voice_manager:
            try:
                agent.voice_manager.speak("ULTRON Agent 2 GUI loaded. Accessibility features active. Ready to assist.")
            except Exception as e:
                print(f"Initial voice announcement failed: {e}")
        
        print("🎮 GUI running! Try the following:")
        print("  - Type messages in the input field")
        print("  - Test voice commands (if available)")
        print("  - Check accessibility features")
        print("  - Voice feedback should be active")
        print("  - All actions are being logged")
        print("\n💡 Sample messages to try:")
        print("  - 'take a screenshot'")
        print("  - 'help me with voice commands'")
        print("  - 'I need accessibility assistance'")
        
        # Run GUI (blocking)
        gui.run()
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        if agent.action_logger:
            agent.action_logger.log_error("GUI_TEST_FAILED", str(e))
    
    finally:
        # Cleanup
        print("\n🔄 Cleaning up GUI test...")
        if agent.action_logger:
            agent.action_logger.log_action("GUI_TEST_END", "GUI test completed")
            print("📄 Check gui_test.log for detailed action logs")

def main():
    """Main test function"""
    test_gui_with_voice_and_logging()

if __name__ == "__main__":
    main()
