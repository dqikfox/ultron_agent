#!/usr/bin/env python3
"""Test TTS functionality with the updated configuration"""

import json
import asyncio
from voice import VoiceAssistant

def load_config():
    """Load configuration from ultron_config.json"""
    with open('ultron_config.json', 'r') as f:
        return json.load(f)

async def test_tts():
    """Test TTS functionality"""
    print("Loading configuration...")
    config = load_config()
    
    print("Initializing Voice Assistant...")
    voice_assistant = VoiceAssistant(config)
    
    print("Testing TTS with default message...")
    test_message = "Hello! TTS is now enabled by default in ULTRON Agent. This is a test of the voice system."
    
    success = await voice_assistant.speak_async(test_message)
    
    if success:
        print("✅ TTS test successful!")
    else:
        print("❌ TTS test failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(test_tts())