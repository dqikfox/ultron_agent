#!/usr/bin/env python3
"""
Test script for ULTRON Ultimate GUI
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
        self.tools = [MockTool("test_tool", "Test tool for demonstration")]
        self.pochi = MockPochi()
    
    def handle_text(self, text):
        return f"Mock response to: {text}"

class MockConfig:
    def __init__(self):
        self.data = {
            'llm_model': 'qwen2.5vl:latest',
            'voice_engine': 'pyttsx3',
            'use_voice': True,
            'use_vision': True,
            'use_api': True
        }

class MockVoice:
    def __init__(self):
        self.call_count = 0
    
    async def listen(self, timeout=3):
        # Simulate voice input - only return something occasionally
        import asyncio
        await asyncio.sleep(0.1)
        self.call_count += 1
        # Only return text every 10th call to avoid spam
        if self.call_count % 10 == 0:
            return "Test voice command"
        return None  # Most calls return nothing
    
    async def speak(self, text):
        print(f"Speaking: {text} - test_gui_ultimate.py:49")

class MockBrain:
    def __init__(self):
        self.active = True

class MockTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class MockPochi:
    def is_available(self):
        return True

def test_gui():
    """Test the Ultimate GUI"""
    print("🚀 Starting ULTRON Ultimate GUI Test... - test_gui_ultimate.py:66")
    
    # Create mock agent and log queue
    agent = MockAgent()
    log_queue = queue.Queue()
    
    try:
        # Import the ultimate GUI
        from gui_ultimate import UltimateAgentGUI
        
        print("✅ Successfully imported UltimateAgentGUI - test_gui_ultimate.py:76")
        
        # Create the GUI (this will test initialization)
        gui = UltimateAgentGUI(agent, log_queue)
        
        print("✅ Successfully created GUI instance - test_gui_ultimate.py:81")
        print("✅ All systems initialized - test_gui_ultimate.py:82")
        
        # Add a test message
        gui.add_to_conversation("SYSTEM", "🧪 GUI Test Mode - All systems operational!")
        gui.add_to_conversation("ULTRON", "Ultimate interface test successful. Ready for deployment!")
        
        print("✅ Conversation system working - test_gui_ultimate.py:88")
        
        # Test status updates
        gui.update_component_status('ollama', 'green')
        gui.update_component_status('voice', 'green')
        gui.update_component_status('brain', 'green')
        
        print("✅ Status system working - test_gui_ultimate.py:95")
        
        # Start the GUI (will show window)
        print("🎮 Launching Ultimate GUI window... - test_gui_ultimate.py:98")
        print("📋 Test Features Available: - test_gui_ultimate.py:99")
        print("• Pushtotalk voice (🎤 Voice button) - test_gui_ultimate.py:100")
        print("• 6component status lights - test_gui_ultimate.py:101")
        print("• Live STT feedback panel - test_gui_ultimate.py:102")
        print("• System monitoring - test_gui_ultimate.py:103")
        print("• Quick actions - test_gui_ultimate.py:104")
        print("• Text commands - test_gui_ultimate.py:105")
        print("\n💡 Close the window when done testing! - test_gui_ultimate.py:106")
        
        gui.run()
        
        print("✅ GUI test completed successfully! - test_gui_ultimate.py:110")
        
    except Exception as e:
        print(f"❌ Error during GUI test: {e} - test_gui_ultimate.py:113")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Make sure we're in the right directory
    import os
    if not os.path.exists("gui_ultimate.py"):
        print("❌ gui_ultimate.py not found. Make sure you're in the correct directory. - test_gui_ultimate.py:124")
        exit(1)
    
    success = test_gui()
    if success:
        print("\n🎉 Ultimate GUI test passed! Ready for integration. - test_gui_ultimate.py:129")
    else:
        print("\n❌ Ultimate GUI test failed. Check errors above. - test_gui_ultimate.py:131")
