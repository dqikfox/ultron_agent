"""
ULTRON Agent 2 - Proper GUI Launcher using Pokedex Interface
Launches the working Pokedex GUI with voice and logging integration
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from pokedex_ultron_gui import PokedexUltronGUI
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import PokedexUltronGUI: {e}")
    GUI_AVAILABLE = False

try:
    from agent_core import UltronAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import UltronAgent: {e}")
    AGENT_AVAILABLE = False

try:
    from voice_manager import UltronVoiceManager
except ImportError:
    UltronVoiceManager = None

try:
    from action_logger import ActionLogger
except ImportError:
    ActionLogger = None

class EnhancedUltronAgent:
    """Enhanced ULTRON Agent with proper GUI integration"""
    
    def __init__(self):
        self.config = self.load_config()
        self.voice_manager = None
        self.action_logger = None
        
        # Initialize voice system
        if UltronVoiceManager:
            try:
                self.voice_manager = UltronVoiceManager()
                print("✅ Voice Manager initialized")
            except Exception as e:
                print(f"⚠️ Voice Manager failed: {e}")
        
        # Initialize action logger
        if ActionLogger:
            try:
                self.action_logger = ActionLogger("ultron_gui_session.log")
                self.action_logger.log_action("GUI_SESSION_START", "ULTRON GUI session starting")
                print("✅ Action Logger initialized")
            except Exception as e:
                print(f"⚠️ Action Logger failed: {e}")
    
    def load_config(self):
        """Load configuration"""
        try:
            import json
            config_file = Path("ultron_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Config loading failed: {e}")
        
        # Default config
        return {
            'llm_model': 'qwen2.5-coder:1.5b',  # Memory optimized for 4GB systems
            'voice_engine': 'voice_manager',
            'use_voice': True,
            'use_gui': True,
            'accessibility_mode': True
        }
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def handle_text(self, text):
        """Handle user text input with accessibility focus"""
        try:
            # Log user input
            if self.action_logger:
                self.action_logger.log_user_input(text, "gui")
            
            # Process accessibility commands
            response = self.process_accessibility_command(text)
            
            # Log AI response
            if self.action_logger:
                self.action_logger.log_ai_response(response, self.config.get('llm_model', 'local'), 0.5)
            
            # Provide voice feedback
            if self.voice_manager and self.config.get('use_voice', True):
                try:
                    self.voice_manager.speak(response)
                    if self.action_logger:
                        self.action_logger.log_voice_action("TTS_RESPONSE", response, "voice_manager")
                except Exception as e:
                    print(f"Voice response failed: {e}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            print(error_msg)
            if self.action_logger:
                self.action_logger.log_error("COMMAND_PROCESSING", error_msg)
            return "I encountered an error, but I'm still here to help you with accessibility features."
    
    def process_accessibility_command(self, text):
        """Process commands with accessibility focus"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["screenshot", "capture", "snap"]):
            return "I'll take an accessibility screenshot for you. This helps users with cognitive disabilities save important information they need to remember."
        
        elif any(word in text_lower for word in ["click", "mouse", "button"]):
            return "I can help you click on elements using voice commands. This assists users with motor impairments who cannot use traditional mouse input."
        
        elif any(word in text_lower for word in ["type", "write", "text"]):
            return "I can type text for you using voice commands. This helps users with limited mobility or repetitive strain injuries."
        
        elif any(word in text_lower for word in ["read", "describe", "see"]):
            return "I can read and describe screen content for you. This assists users with visual impairments by providing audio descriptions of visual elements."
        
        elif any(word in text_lower for word in ["help", "assistance", "support"]):
            return "I'm ULTRON Agent 2, your accessibility assistant. I can help with mouse control, keyboard input, screen reading, and more. My goal is to make your computer fully accessible."
        
        elif any(word in text_lower for word in ["voice", "speak", "say"]):
            return "Voice system is active and ready. I provide audio feedback for all actions to ensure you're always informed about what's happening."
        
        else:
            return f"I understand: '{text}'. I'm here to help with accessibility. I can assist with clicking, typing, reading screens, taking screenshots, and voice control. What would you like me to help you with?"

def main():
    """Main launcher function"""
    print("🚀 ULTRON Agent 2 - Enhanced GUI Launcher")
    print("♿ Accessibility-focused interface with voice and logging")
    print("=" * 60)
    
    if not GUI_AVAILABLE:
        print("❌ Pokedex GUI not available")
        return
    
    try:
        # Create enhanced agent
        print("🤖 Initializing ULTRON Agent...")
        agent = EnhancedUltronAgent()
        
        # Announce startup
        if agent.voice_manager:
            agent.voice_manager.speak("ULTRON Agent 2 starting. Accessibility interface loading.")
        
        # Launch Pokedex GUI
        print("🎮 Launching Pokedex GUI interface...")
        gui = PokedexUltronGUI(agent, test_mode=False)
        
        print("✅ GUI launched successfully!")
        print("💡 Features available:")
        print("  - Text input field for commands")
        print("  - Voice feedback system")
        print("  - Accessibility logging")
        print("  - Real-time system monitoring")
        print("  - Pokedex-style interface")
        
        print("\n🗣️ Try these accessibility commands:")
        print("  - 'take a screenshot'")
        print("  - 'help me click something'")  
        print("  - 'read the screen for me'")
        print("  - 'type some text'")
        
        # Run GUI
        gui.run()
        
    except Exception as e:
        print(f"❌ GUI launch failed: {e}")
        if 'agent' in locals() and agent.action_logger:
            agent.action_logger.log_error("GUI_LAUNCH_FAILED", str(e))

if __name__ == "__main__":
    main()
