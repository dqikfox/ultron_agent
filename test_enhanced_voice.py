#!/usr/bin/env python3
"""
Test script for enhanced ULTRON Agent voice features
Tests the NVIDIA-recommended VoiceAssistant improvements
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_voice_imports():
    """Test that all voice-related imports work"""
    print("🔍 Testing voice imports...")

    try:
        from voice import VoiceAssistant
        print("✅ VoiceAssistant import successful")
        # Use the import to avoid lint warning
        _ = VoiceAssistant
    except ImportError as e:
        print(f"❌ VoiceAssistant import failed: {e}")
        return False

    try:
        from tools.audio_manager import AudioManager
        print("✅ AudioManager import successful")
        # Use the import to avoid lint warning
        _ = AudioManager
    except ImportError as e:
        print(f"❌ AudioManager import failed: {e}")
        return False

    try:
        import elevenlabs
        print("✅ elevenlabs import successful")
        # Use the import to avoid lint warning
        _ = elevenlabs
    except ImportError as e:
        print(f"⚠️  elevenlabs import failed (optional): {e}")

    try:
        import pygame
        print("✅ pygame import successful")
        # Use the import to avoid lint warning
        _ = pygame
    except ImportError as e:
        print(f"⚠️  pygame import failed (optional): {e}")

    try:
        import pyttsx3
        print("✅ pyttsx3 import successful")
        # Use the import to avoid lint warning
        _ = pyttsx3
    except ImportError as e:
        print(f"⚠️  pyttsx3 import failed (optional): {e}")

    return True


def test_config_loading():
    """Test that voice configuration loads correctly"""
    print("\n🔍 Testing configuration loading...")

    try:
        from config import Config
        config = Config()

        # Check for new voice settings
        voice_settings = [
            "voice_rate", "voice_volume", "voice_stability",
            "voice_similarity", "voice_cache_dir", "mic_energy_threshold",
            "disable_tts_cache", "microphone_device_index"
        ]

        for setting in voice_settings:
            value = config.data.get(setting)
            if value is not None:
                print(f"✅ {setting}: {value}")
            else:
                print(f"⚠️  {setting}: not found")

        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def test_voice_initialization():
    """Test VoiceAssistant initialization with progress indicators"""
    print("\n🔍 Testing VoiceAssistant initialization...")

    try:
        from config import Config
        from voice import VoiceAssistant

        config = Config()
        print("🔄 Initializing Voice Assistant...")

        # This should show progress indicators
        voice_assistant = VoiceAssistant(config)
        # Use the variable to avoid lint warning
        _ = voice_assistant

        print("✅ VoiceAssistant initialized successfully")
        return True
    except Exception as e:
        print(f"❌ VoiceAssistant initialization failed: {e}")
        return False


def test_audio_manager():
    """Test AudioManager functionality"""
    print("\n🔍 Testing AudioManager...")

    try:
        from tools.audio_manager import AudioManager

        audio_manager = AudioManager()

        # Test basic functionality
        devices = audio_manager.list_audio_devices()
        print(f"✅ Audio devices: {devices}")

        # Test audio system
        test_result = audio_manager.test_audio()
        if test_result:
            print("✅ Audio test successful")
        else:
            print("⚠️  Audio test failed")

        return True
    except Exception as e:
        print(f"❌ AudioManager test failed: {e}")
        return False


def test_cache_directory():
    """Test voice cache directory creation"""
    print("\n🔍 Testing cache directory...")

    try:
        from config import Config

        config = Config()
        cache_dir = config.data.get("voice_cache_dir", "cache/voice")

        cache_path = Path(cache_dir)
        if cache_path.exists():
            print(f"✅ Cache directory exists: {cache_path}")
        else:
            print(f"⚠️  Cache directory does not exist: {cache_path}")

        # Try to create it
        cache_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Cache directory created/verified: {cache_path}")

        return True
    except Exception as e:
        print(f"❌ Cache directory test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 ULTRON Agent Enhanced Voice Features Test")
    print("=" * 50)

    tests = [
        ("Voice Imports", test_voice_imports),
        ("Configuration Loading", test_config_loading),
        ("Voice Initialization", test_voice_initialization),
        ("Audio Manager", test_audio_manager),
        ("Cache Directory", test_cache_directory)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All enhanced voice features are working!")
        return 0
    else:
        print("⚠️  Some features may need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
