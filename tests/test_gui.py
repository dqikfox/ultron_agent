import pytest
import tkinter as tk
import queue
from unittest.mock import patch

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
    async def listen(self, timeout=3):
        return "Test voice command"
    
    async def speak(self, text):
        print(f"Speaking: {text} - test_gui.py:33")

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

@pytest.fixture
def mock_agent():
    return MockAgent()

@pytest.fixture
def log_queue():
    return queue.Queue()

# We need to patch the main loop so the GUI doesn't block tests.
@patch('tkinter.Tk.mainloop')
def test_gui_initialization(mock_mainloop, mock_agent, log_queue):
    """Tests if the UltimateAgentGUI initializes without errors."""
    from gui_ultimate import UltimateAgentGUI
    
    # The GUI will be created, but `run()` will not block.
    gui = UltimateAgentGUI(mock_agent, log_queue)
    
    assert gui is not None
    assert isinstance(gui.root, tk.Tk)
    assert gui.agent == mock_agent
    
    # Test if a welcome message was added
    assert len(gui.conversation_history) > 0
    assert gui.conversation_history[0]['speaker'] == "ULTRON"
    
    # Since the mainloop is mocked, we need to manually destroy the window
    # to avoid it hanging around.
    gui.root.destroy()

@patch('tkinter.Tk.mainloop')
def test_add_to_conversation(mock_mainloop, mock_agent, log_queue):
    """Tests the add_to_conversation method."""
    from gui_ultimate import UltimateAgentGUI
    
    gui = UltimateAgentGUI(mock_agent, log_queue)
    
    initial_history_len = len(gui.conversation_history)
    
    gui.add_to_conversation("SYSTEM", "Test message")
    
    assert len(gui.conversation_history) == initial_history_len + 1
    last_message = gui.conversation_history[-1]
    assert last_message['speaker'] == "SYSTEM"
    assert last_message['message'] == "Test message"
    
    gui.root.destroy()

