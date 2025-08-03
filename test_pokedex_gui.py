#!/usr/bin/env python3
"""
Test script for ULTRON Pokedex GUI
"""

import tkinter as tk
import queue
import threading
import time
from pathlib import Path

# Mock agent class for testing
class MockAgent:
    def __init__(self):
        self.config = MockConfig()
        self.voice = MockVoice()
        self.brain = MockBrain()
        self.tools = [MockTool("pokedex_scanner", "Scan for Pokemon data")]
    
    def handle_text(self, text):
        return f"Pokedex response: {text}"

class MockConfig:
    def __init__(self):
        self.data = {
            'llm_model': 'qwen2.5:latest',
            'voice_engine': 'pyttsx3',
            'use_voice': True,
            'use_vision': True,
            'use_api': True
        }

class MockVoice:
    async def listen(self, timeout=3):
        # Simulate voice input
        import asyncio
        await asyncio.sleep(0.2)
        return None  # No constant voice input
    
    async def speak(self, text):
        print(f"Pokedex Speaking: {text}")

class MockBrain:
    def __init__(self):
        self.active = True

class MockTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

def test_pokedex_gui():
    """Test the Pokedex GUI"""
    print("🎮 Starting ULTRON Pokedex GUI Test...")
    
    # Create mock agent and log queue
    agent = MockAgent()
    log_queue = queue.Queue()
    
    try:
        # Import the Pokedex GUI
        from gui import AgentGUI
        
        print("✅ Successfully imported Pokedex AgentGUI")
        
        # Create the GUI (this will test initialization)
        gui = AgentGUI(agent, log_queue)
        
        print("✅ Successfully created Pokedex GUI instance")
        print("✅ All systems initialized")
        
        # Add a test message
        gui.add_to_conversation("SYSTEM", "🎮 Pokedex Mode - ULTRON interface initialized!")
        gui.add_to_conversation("ULTRON", "Welcome to the ULTRON Pokedex interface! Classic retro styling activated.")
        gui.add_to_conversation("USER", "Show me the Pokedex interface")
        gui.add_to_conversation("ULTRON", "This is the classic Pokedex-style interface with red header, organized panels, and retro gaming aesthetics!")
        
        print("✅ Conversation system working")
        
        # Start the GUI (will show window)
        print("🎮 Launching Pokedex GUI window...")
        print("📋 Pokedex Features Available:")
        print("   • Classic red Pokedex header")
        print("   • Three-panel layout (Status | Conversation | Controls)")
        print("   • System monitoring panel")
        print("   • Voice controls")
        print("   • Retro gaming aesthetics")
        print("   • Text commands")
        print("\n💡 Close the window when done testing!")
        
        gui.run()
        
        print("✅ Pokedex GUI test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during Pokedex GUI test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Make sure we're in the right directory
    import os
    if not os.path.exists("gui.py"):
        print("❌ gui.py not found. Make sure you're in the correct directory.")
        exit(1)
    
    success = test_pokedex_gui()
    if success:
        print("\n🎮 Pokedex GUI test passed! Classic interface ready.")
    else:
        print("\n❌ Pokedex GUI test failed. Check errors above.")
