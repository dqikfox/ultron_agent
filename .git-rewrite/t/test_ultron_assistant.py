"""
Test Prompts for Ultron Assistant - Continue.dev Configuration
Use these prompts to verify your assistant is working correctly
"""

# Test prompts to verify your Ultron Assistant configuration
TEST_PROMPTS = {
    "project_awareness": [
        "What are the main components of the ULTRON Agent 2 project?",
        "How does the tools system work in this project?",
        "Explain the voice_manager.py integration patterns",
        "What's the difference between agent_core.py and brain.py?",
    ],
    
    "automation_expertise": [
        "How do I safely move the mouse to coordinates 250,300 using PyAutoGUI?",
        "Create a function that clicks on an image with proper error handling",
        "Show me how to implement fail-safe mechanisms for automation scripts",
        "What's the best way to handle image recognition timeouts?",
    ],
    
    "voice_integration": [
        "How do I convert voice commands to automation actions?",
        "Create a voice command handler for mouse movement",
        "Show me how to provide audio feedback for automation completion",
        "Integrate TTS confirmation with PyAutoGUI operations",
    ],
    
    "coding_standards": [
        "Create a new tool for the tools/ system with proper error handling",
        "Show me the proper logging pattern for this project",
        "How should I structure a test for PyAutoGUI functionality?",
        "What's the correct way to use the event system for automation?",
    ],
    
    "safety_and_testing": [
        "Create a safe automation script that validates coordinates before clicking",
        "How do I test image recognition without actual GUI interaction?",
        "Show me proper exception handling for automation failures",
        "Create a mock test for voice command processing",
    ],
    
    "integration_scenarios": [
        "Create an end-to-end automation that uses voice, mouse, and image recognition",
        "How do I integrate a new PyAutoGUI feature with the existing architecture?",
        "Show me how to add logging to all automation actions",
        "Create a tool that combines screenshot, image recognition, and clicking",
    ]
}

# Expected response indicators - your assistant should mention these
EXPECTED_RESPONSES = {
    "project_knowledge": [
        "agent_core.py",
        "voice_manager.py", 
        "tools/ package",
        "event system",
        "ActionLogger",
        "ultron_config.json"
    ],
    
    "automation_safety": [
        "pyautogui.FAILSAFE = True",
        "pyautogui.PAUSE = 0.1",
        "confidence threshold",
        "coordinate validation",
        "try/except blocks",
        "timeout handling"
    ],
    
    "voice_patterns": [
        "voice_manager.py",
        "TTS feedback",
        "natural language parsing",
        "audio confirmation",
        "fallback engines"
    ],
    
    "coding_quality": [
        "type hints",
        "docstrings",
        "error handling",
        "logging",
        "testing",
        "async/await"
    ]
}

def print_test_prompts():
    """Print organized test prompts for manual testing"""
    
    print("🧪 ULTRON ASSISTANT - TEST PROMPTS")
    print("=" * 50)
    print()
    
    for category, prompts in TEST_PROMPTS.items():
        print(f"📋 {category.replace('_', ' ').title()}:")
        print("-" * 30)
        
        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. {prompt}")
        
        print()
    
    print("🎯 TESTING INSTRUCTIONS:")
    print("-" * 30)
    print("1. Open Continue panel in VS Code")
    print("2. Select 'Ultron Assistant' from model dropdown")
    print("3. Try the prompts above in different categories")
    print("4. Verify responses include expected keywords")
    print("5. Test different assistant modes (Dev/Prod)")
    print()
    
    print("✅ EXPECTED RESPONSE INDICATORS:")
    print("-" * 30)
    for category, indicators in EXPECTED_RESPONSES.items():
        print(f"• {category.replace('_', ' ').title()}: {', '.join(indicators[:3])}...")
    print()

def create_test_conversation():
    """Create a sample test conversation"""
    
    conversation = """
🤖 SAMPLE TEST CONVERSATION
===========================

👤 User: "How do I safely move the mouse to coordinates using PyAutoGUI in this project?"

🤖 Expected Ultron Assistant Response:
"I'll help you create a safe mouse movement function for the ULTRON Agent 2 project.

Here's the recommended approach following our safety guidelines:

```python
import pyautogui
from action_logger import get_action_logger

def safe_move_mouse(x: int, y: int) -> bool:
    \"\"\"
    Safely move mouse to coordinates with validation and logging
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
    
    Returns:
        bool: True if successful, False otherwise
    \"\"\"
    # Safety setup (as per project standards)
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    # Get screen dimensions for validation
    screen_width, screen_height = pyautogui.size()
    logger = get_action_logger()
    
    try:
        # Validate coordinates
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            logger.log_error("ValidationError", f"Coordinates ({x}, {y}) out of screen bounds")
            return False
        
        # Log the action
        logger.log_action("MOUSE_MOVE", f"Moving mouse to ({x}, {y})")
        
        # Perform the movement
        pyautogui.moveTo(x, y)
        
        # Verify position (optional safety check)
        actual_x, actual_y = pyautogui.position()
        if abs(actual_x - x) > 5 or abs(actual_y - y) > 5:
            logger.log_error("MovementError", f"Mouse position verification failed")
            return False
        
        logger.log_action("MOUSE_MOVE_SUCCESS", f"Mouse moved to ({actual_x}, {actual_y})")
        return True
        
    except Exception as e:
        logger.log_error("PyAutoGUIError", f"Mouse movement failed: {str(e)}")
        return False
```

Key safety features implemented:
• **Fail-safe enabled**: Move mouse to corner to emergency stop
• **Coordinate validation**: Ensures target is within screen bounds  
• **Error handling**: Comprehensive try/catch with logging
• **Action logging**: Integrates with project's ActionLogger system
• **Position verification**: Confirms movement was successful
• **Type hints & docstrings**: Follows project coding standards

You can integrate this with voice commands or use it in automation tools."

✅ This response demonstrates:
- Project architecture knowledge (ActionLogger)
- Safety best practices (FAILSAFE, validation)
- Coding standards (type hints, docstrings, error handling)
- Integration patterns (logging system)
- ULTRON-specific patterns and conventions
"""
    
    return conversation

if __name__ == "__main__":
    print_test_prompts()
    print()
    print(create_test_conversation())
