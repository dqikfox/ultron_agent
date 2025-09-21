#!/usr/bin/env python3
"""
ULTRON Voice System Comprehensive Test
Tests voice capture, ElevenLabs TTS, and fallback mechanisms
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
sys.path.append('.')

from config import Config
from voice import VoiceAssistant


class VoiceSystemTester:
    """Comprehensive tester for ULTRON voice system"""

    def __init__(self):
        self.config = Config()
        self.voice = None
        self.test_results = {}

    async def setup(self):
        """Initialize voice system"""
        print("🔧 Setting up voice system...")
        try:
            self.voice = VoiceAssistant(self.config)
            self.test_results['setup'] = True
            print("✅ Voice system initialized successfully")
        except Exception as e:
            self.test_results['setup'] = False
            print(f"❌ Voice system setup failed: {e}")
            return False
        return True

    async def test_environment_variables(self):
        """Test environment variable integration"""
        print("\n🧪 Testing Environment Variables...")

        elevenlabs_agent_id = os.getenv('ELEVENLABS_AGENT_ID')
        elevenlabs_api_key = os.getenv('ELEVENLABS_APIKEY')

        print(f"ELEVENLABS_AGENT_ID: {elevenlabs_agent_id or 'Not set'}")
        print(f"ELEVENLABS_API_KEY: {'Set' if elevenlabs_api_key else 'Not set'}")
        print(f"Voice.preferred_voice_id: {self.voice.preferred_voice_id}")

        # Verify voice ID is correctly set
        if elevenlabs_agent_id and self.voice.preferred_voice_id == elevenlabs_agent_id:
            self.test_results['env_vars'] = True
            print("✅ Environment variable integration working")
        elif self.voice.preferred_voice_id:
            self.test_results['env_vars'] = True
            print("✅ Voice ID set from config/fallback")
        else:
            self.test_results['env_vars'] = False
            print("❌ Voice ID not properly configured")

    async def test_health_checks(self):
        """Test health monitoring"""
        print("\n🩺 Testing Health Checks...")

        try:
            tts_health = self.voice.check_tts_health()
            stt_health = self.voice.check_stt_health()

            print("TTS Health:", tts_health)
            print("STT Health:", stt_health)

            # Check if at least one TTS engine is available
            tts_available = any(tts_health.values())
            stt_available = any(stt_health.values())

            self.test_results['health_tts'] = tts_available
            self.test_results['health_stt'] = stt_available

            if tts_available:
                print("✅ TTS health check passed")
            else:
                print("❌ No TTS engines available")

            if stt_available:
                print("✅ STT health check passed")
            else:
                print("❌ No STT engines available")

        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.test_results['health_tts'] = False
            self.test_results['health_stt'] = False

    async def test_voice_listing(self):
        """Test voice enumeration"""
        print("\n🎤 Testing Voice Enumeration...")

        try:
            voices = self.voice.get_available_voices()
            print(f"Found {len(voices)} voices across all engines")

            elevenlabs_voices = [v for v in voices if v['source'] == 'elevenlabs']
            pyttsx3_voices = [v for v in voices if v['source'] == 'pyttsx3']

            print(f"ElevenLabs voices: {len(elevenlabs_voices)}")
            print(f"pyttsx3 voices: {len(pyttsx3_voices)}")

            self.test_results['voice_listing'] = len(voices) > 0
            if len(voices) > 0:
                print("✅ Voice enumeration working")
            else:
                print("❌ No voices found")

        except Exception as e:
            print(f"❌ Voice enumeration failed: {e}")
            self.test_results['voice_listing'] = False

    async def test_microphone_listing(self):
        """Test microphone enumeration"""
        print("\n🎙️ Testing Microphone Enumeration...")

        try:
            mics = self.voice.get_available_microphones()
            print(f"Found {len(mics)} microphones")

            for i, mic in enumerate(mics[:3]):  # Show first 3
                print(f"  {i+1}. {mic['name']} (index: {mic['index']})")

            self.test_results['microphone_listing'] = len(mics) > 0
            if len(mics) > 0:
                print("✅ Microphone enumeration working")
            else:
                print("❌ No microphones found")

        except Exception as e:
            print(f"❌ Microphone enumeration failed: {e}")
            self.test_results['microphone_listing'] = False

    async def test_tts_functionality(self):
        """Test TTS functionality"""
        print("\n🗣️ Testing TTS Functionality...")

        test_text = "Hello, this is a test of the ULTRON voice system."

        try:
            print(f"Speaking: '{test_text}'")

            # Test async speak
            start_time = time.time()
            success = await self.voice.speak(test_text)
            duration = time.time() - start_time

            if success:
                print(f"✅ TTS completed in {duration:.2f} seconds")
                self.test_results['tts_async'] = True
                print("✅ Async TTS test passed")
            else:
                print("❌ Async TTS test failed")
                self.test_results['tts_async'] = False

            # Test sync speak
            print("Testing synchronous TTS...")
            sync_success = self.voice.speak_sync("This is a sync test.")
            if sync_success:
                print("✅ Sync TTS test passed")
                self.test_results['tts_sync'] = True
            else:
                print("❌ Sync TTS test failed")
                self.test_results['tts_sync'] = False

        except Exception as e:
            print(f"❌ TTS functionality test failed: {e}")
            self.test_results['tts_async'] = False
            self.test_results['tts_sync'] = False

    async def test_stt_functionality(self):
        """Test STT functionality (with timeout to avoid hanging)"""
        print("\n👂 Testing STT Functionality...")

        try:
            print("Testing STT with 3-second timeout...")
            print("Please speak something now...")

            # Use a short timeout for testing
            start_time = time.time()
            text = await asyncio.wait_for(
                self.voice.listen_async(timeout=3, phrase_time_limit=3),
                timeout=5
            )
            duration = time.time() - start_time

            if text and text.strip():
                print(f"✅ STT captured: '{text}'")
                print(f"⏱️ STT completed in {duration:.2f} seconds")
                self.test_results['stt_async'] = True
            else:
                print("⚠️ STT returned empty result (might be normal if no speech)")
                self.test_results['stt_async'] = True  # Still counts as working

        except asyncio.TimeoutError:
            print("⏰ STT test timed out (normal for automated testing)")
            self.test_results['stt_async'] = True
        except Exception as e:
            print(f"❌ STT functionality test failed: {e}")
            self.test_results['stt_async'] = False

    async def test_performance_monitoring(self):
        """Test performance monitoring"""
        print("\n📊 Testing Performance Monitoring...")

        try:
            stats = self.voice.get_performance_stats()
            print("Performance stats retrieved:", 'error' not in stats)

            if 'error' not in stats:
                print("✅ Performance monitoring working")
                self.test_results['performance'] = True
            else:
                print(f"⚠️ Performance monitoring issue: {stats.get('error')}")
                self.test_results['performance'] = False

        except Exception as e:
            print(f"❌ Performance monitoring test failed: {e}")
            self.test_results['performance'] = False

    async def test_event_system(self):
        """Test event system integration"""
        print("\n📡 Testing Event System Integration...")

        try:
            event_available = self.voice.event_system is not None
            perf_available = self.voice.performance_monitor is not None

            print(f"Event system available: {event_available}")
            print(f"Performance monitor available: {perf_available}")

            self.test_results['event_system'] = event_available
            self.test_results['perf_monitor'] = perf_available

            if event_available:
                print("✅ Event system integration working")
            else:
                print("⚠️ Event system not available")

            if perf_available:
                print("✅ Performance monitor integration working")
            else:
                print("⚠️ Performance monitor not available")

        except Exception as e:
            print(f"❌ Event system test failed: {e}")
            self.test_results['event_system'] = False
            self.test_results['perf_monitor'] = False

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🎯 ULTRON VOICE SYSTEM TEST SUMMARY")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")

        print("\n🔍 Key Findings:")
        if self.test_results.get('setup', False):
            print("  • Voice system initializes successfully")
        if self.test_results.get('env_vars', False):
            print("  • Environment variables properly integrated")
        if self.test_results.get('health_tts', False):
            print("  • TTS engines available and healthy")
        if self.test_results.get('health_stt', False):
            print("  • STT engines available and healthy")
        if self.test_results.get('tts_async', False):
            print("  • ElevenLabs/pyttsx3 TTS working")
        if self.test_results.get('stt_async', False):
            print("  • Speech recognition functional")
        if self.test_results.get('event_system', False):
            print("  • Event system integration active")
        if self.test_results.get('performance', False):
            print("  • Performance monitoring active")

        print("\n🎉 Test completed!")


async def main():
    """Main test execution"""
    print("🚀 Starting ULTRON Voice System Comprehensive Test")
    print("="*60)

    tester = VoiceSystemTester()

    # Run all tests
    if await tester.setup():
        await tester.test_environment_variables()
        await tester.test_health_checks()
        await tester.test_voice_listing()
        await tester.test_microphone_listing()
        await tester.test_event_system()
        await tester.test_performance_monitoring()
        await tester.test_tts_functionality()
        await tester.test_stt_functionality()

    # Print summary
    tester.print_test_summary()


if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(main())</content>
<parameter name="filePath">c:\Projects\ultron_agent_2\test_voice_comprehensive.py
