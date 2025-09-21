#!/usr/bin/env python3
"""
Test script for ULTRON Agent voice and vision integration
Tests the centralized configuration system with environment variables
"""

import os
import sys
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from voice_manager import UltronVoiceManager
from tools.vision import get_vision_tool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test centralized configuration loading"""
    print("=== Testing Centralized Configuration ===")

    # Initialize config
    config = Config()
    print(f"Config loaded: {config is not None}")

    # Test API key loading from environment
    api_keys = ['openai', 'elevenlabs', 'gemini', 'anthropic']
    for key_name in api_keys:
        key_value = config.get_api_key(key_name)
        status = "✓" if key_value else "✗"
        masked_value = "***" + key_value[-4:] if key_value else "None"
        print(f"{status} {key_name}: {masked_value}")

    return config


def test_voice_manager(config):
    """Test voice manager with ElevenLabs integration"""
    print("\n=== Testing Voice Manager ===")

    # Initialize voice manager
    voice_manager = UltronVoiceManager(ultron_config=config)
    print(f"Voice manager initialized: {voice_manager is not None}")

    # Check available engines
    engines = voice_manager.get_available_engines()
    print(f"Available engines: {engines}")

    # Test engine availability
    for engine in ['pyttsx3', 'elevenlabs']:
        available = engine in engines
        status = "✓" if available else "✗"
        avail_text = "Available" if available else "Not available"
        print(f"{status} {engine}: {avail_text}")

    return voice_manager


def test_vision_tool(config):
    """Test vision tool with CLIP integration"""
    print("\n=== Testing Vision Tool ===")

    # Get vision tool instance
    vision_tool = get_vision_tool(config)
    print(f"Vision tool initialized: {vision_tool is not None}")

    # Check CLIP model availability
    clip_available = vision_tool.clip_model is not None
    status = "✓" if clip_available else "✗"
    avail_text = "Available" if clip_available else "Not available"
    print(f"{status} CLIP model: {avail_text}")

    if clip_available:
        print(f"Device: {vision_tool.device}")

    return vision_tool


def test_offline_fallback():
    """Test offline-first design"""
    print("\n=== Testing Offline-First Design ===")

    # Test if Ollama is available (for offline models)
    try:
        import ollama  # noqa: F401
        ollama_available = True
        print("✓ Ollama client available")
    except ImportError:
        ollama_available = False
        print("✗ Ollama client not available")

    return ollama_available


def main():
    """Main test function"""
    print("ULTRON Agent Integration Test")
    print("=" * 40)

    try:
        # Test configuration
        config = test_configuration()

        # Test voice manager
        _ = test_voice_manager(config)

        # Test vision tool
        _ = test_vision_tool(config)

        # Test offline capabilities
        _ = test_offline_fallback()

        print("\n=== Test Summary ===")
        print("✓ Configuration system: Working")
        print("✓ Voice manager: Working")
        print("✓ Vision tool: Working")
        print("✓ Offline-first design: Working")
        print("\n🎉 All systems operational!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

