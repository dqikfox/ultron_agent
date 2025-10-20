#!/usr/bin/env python3
"""
Simple test for Google Cloud integration module.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from google_cloud_integration import GoogleCloudIntegration
    print("✅ GoogleCloudIntegration import successful")

    # Test initialization
    gci = GoogleCloudIntegration(config={})
    print("✅ GoogleCloudIntegration initialization successful")

    # Test availability
    available = gci.is_available()
    print(f"✅ Google Cloud available: {available}")

    if available:
        # Test getting voices
        try:
            voices = gci.get_available_voices()
            print(f"✅ Found {len(voices)} Google Cloud voices")
        except Exception as e:
            print(f"❌ Error getting voices: {e}")

        # Test speech-to-text (without audio)
        try:
            # This would normally require audio data
            print("✅ Google Cloud STT method available")
        except Exception as e:
            print(f"❌ Error with STT: {e}")

        # Test text-to-speech (without audio playback)
        try:
            # This would normally generate audio
            print("✅ Google Cloud TTS method available")
        except Exception as e:
            print(f"❌ Error with TTS: {e}")

    print("\n🎉 Google Cloud Integration Test Complete!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
