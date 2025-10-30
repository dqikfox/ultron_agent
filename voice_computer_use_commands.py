#!/usr/bin/env python3
"""Voice Commands for OpenAI Computer Use Integration"""

from openai_computer_use_integration import ultron_computer_use
from utils.ultron_logger import log_info

class VoiceComputerUseCommands:
    """Voice command processor for computer use"""
    
    def __init__(self):
        self.computer_use = ultron_computer_use
        
    def process_voice_command(self, voice_input: str) -> str:
        """Process voice command for computer control"""
        
        voice_lower = voice_input.lower()
        
        # Computer use wake phrases
        computer_phrases = ["computer", "screen", "click", "type", "mouse", "keyboard"]
        
        if not any(phrase in voice_lower for phrase in computer_phrases):
            return None  # Not a computer use command
        
        log_info("voice_computer_use", f"Processing computer command: {voice_input}")
        
        # Route to computer use system
        result = self.computer_use.handle_voice_command(voice_input)
        
        return result

# Voice command mappings for ULTRON
COMPUTER_USE_VOICE_COMMANDS = {
    # Click commands
    "click desktop": "click on the desktop",
    "click screen": "click on the screen", 
    "click center": "click on the center",
    "click button": "click on the button",
    "left click": "click with left button",
    "right click": "click with right button",
    
    # Type commands
    "type hello": "type hello world",
    "type name": "type my name",
    "type text": "type some text",
    
    # Scroll commands
    "scroll up": "scroll up",
    "scroll down": "scroll down",
    "page up": "scroll up",
    "page down": "scroll down",
    
    # Key commands
    "press enter": "press enter key",
    "press escape": "press escape key",
    "press tab": "press tab key",
    
    # Screenshot commands
    "take screenshot": "take a screenshot",
    "capture screen": "capture the screen",
    "screenshot": "take a screenshot"
}

def get_computer_use_voice_processor():
    """Get voice processor for computer use commands"""
    return VoiceComputerUseCommands()

if __name__ == "__main__":
    processor = VoiceComputerUseCommands()
    
    # Test voice commands
    test_commands = [
        "computer click desktop",
        "type hello world", 
        "scroll down the page",
        "take a screenshot"
    ]
    
    for cmd in test_commands:
        result = processor.process_voice_command(cmd)
        print(f"'{cmd}' -> {result}")