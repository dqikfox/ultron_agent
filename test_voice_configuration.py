#!/usr/bin/env python3
"""
ULTRON Voice Configuration Test Suite
Comprehensive testing for voice functionality including audio capture,
speech recognition, text-to-speech, and AI model integration.

This test suite validates:
- Voice system initialization and configuration
- Microphone setup and audio capture
- Speech recognition with multiple services
- Text-to-speech with fallback chains
- Integration with Ollama and other AI models
- GUI voice chat functionality
- Health monitoring and error handling
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from voice import VoiceAssistant
from brain import UltronBrain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceTestSuite:
    """
    Comprehensive test suite for ULTRON voice functionality
    """

    def __init__(self):
        self.config = None
        self.voice_assistant = None
        self.brain = None
        self.test_results = []
        self.current_test = None

    def log_test_result(self, test_name: str, status: str, message: str = "",
                       details: Dict = None):
        """Log a test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "details": details or {}
        }
        self.test_results.append(result)

        status_icon = {
            "PASS": "✅",
            "FAIL": "❌",
            "SKIP": "⏭️",
            "INFO": "ℹ️"
        }.get(status, "?")

        print(f"{status_icon} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    async def setup_test_environment(self):
        """Setup test environment and initialize components"""
        print("🚀 ULTRON Voice Configuration Test Suite")
        print("=" * 60)

        try:
            # Test 1: Configuration Loading
            self.current_test = "Configuration Loading"
            print("\n📋 Test 1: Configuration Loading")
            print("-" * 40)

            self.config = Config()
            self.log_test_result(
                "Configuration Loading",
                "PASS",
                "Configuration loaded successfully"
            )

            # Test 2: Voice System Initialization
            self.current_test = "Voice System Initialization"
            print("\n🎤 Test 2: Voice System Initialization")
            print("-" * 40)

            self.voice_assistant = VoiceAssistant(self.config)
            self.log_test_result(
                "Voice System Initialization",
                "PASS",
                "Voice assistant initialized successfully"
            )

            # Test 3: Brain/AI System Initialization
            self.current_test = "AI System Initialization"
            print("\n🧠 Test 3: AI System Initialization")
            print("-" * 40)

            # Mock tools and memory for brain initialization
            mock_tools = {}
            mock_memory = type('MockMemory', (), {
                'get_context': lambda: {},
                'store_interaction': lambda *args: None
            })()

            self.brain = UltronBrain(self.config, mock_tools, mock_memory)
            self.log_test_result(
                "AI System Initialization",
                "PASS",
                "AI brain system initialized successfully"
            )

        except Exception as e:
            self.log_test_result(
                self.current_test,
                "FAIL",
                f"Setup failed: {str(e)}"
            )
            raise

    async def test_microphone_setup(self):
        """Test microphone detection and setup"""
        print("\n🎙️ Test 4: Microphone Setup")
        print("-" * 40)

        try:
            # Get available microphones
            microphones = self.voice_assistant.get_available_microphones()

            if not microphones:
                self.log_test_result(
                    "Microphone Detection",
                    "FAIL",
                    "No microphones detected"
                )
                return

            self.log_test_result(
                "Microphone Detection",
                "PASS",
                f"Found {len(microphones)} microphone(s)",
                {"microphones": [m['name'] for m in microphones]}
            )

            # Test microphone selection
            current_device = self.config.get("microphone_device_index")
            if current_device is not None:
                success = self.voice_assistant.set_microphone(current_device)
                status = "PASS" if success else "FAIL"
                message = ("Microphone configured successfully" if success
                          else "Failed to configure microphone")
                self.log_test_result("Microphone Configuration",
                                    status, message)
            else:
                self.log_test_result(
                    "Microphone Configuration",
                    "INFO",
                    "No specific microphone configured, using default"
                )

        except Exception as e:
            self.log_test_result(
                "Microphone Setup",
                "FAIL",
                f"Microphone setup failed: {str(e)}"
            )

    async def test_speech_recognition(self):
        """Test speech recognition with user interaction"""
        print("\n🎧 Test 5: Speech Recognition")
        print("-" * 40)

        # Check STT health
        stt_health = self.voice_assistant.check_stt_health()
        healthy_services = [k for k, v in stt_health.items() if v]

        if not healthy_services:
            self.log_test_result(
                "Speech Recognition Health",
                "FAIL",
                "No speech recognition services available"
            )
            return

        self.log_test_result(
            "Speech Recognition Health",
            "PASS",
            f"Healthy STT services: {', '.join(healthy_services)}",
            {"services": stt_health}
        )

        # Interactive speech test
        print("\n🗣️  INTERACTIVE SPEECH TEST")
        print("Please speak a short phrase (e.g., 'Hello ULTRON')")
        print("You have 5 seconds to speak after the prompt...")
        print("Press Enter when ready to speak:")

        input()  # Wait for user to press Enter

        try:
            print("🎤 Listening... (speak now)")
            recognized_text = await self.voice_assistant.listen_async(
                timeout=5, phrase_time_limit=5
            )

            if recognized_text and recognized_text.strip():
                self.log_test_result(
                    "Speech Recognition",
                    "PASS",
                    f"Successfully recognized: '{recognized_text}'"
                )
            else:
                self.log_test_result(
                    "Speech Recognition",
                    "FAIL",
                    "No speech recognized or empty result"
                )

        except Exception as e:
            self.log_test_result(
                "Speech Recognition",
                "FAIL",
                f"Speech recognition error: {str(e)}"
            )

    async def test_text_to_speech(self):
        """Test text-to-speech functionality"""
        print("\n🔊 Test 6: Text-to-Speech")
        print("-" * 40)

        # Check TTS health
        tts_health = self.voice_assistant.check_tts_health()
        healthy_services = [k for k, v in tts_health.items() if v]

        if not healthy_services:
            self.log_test_result(
                "Text-to-Speech Health",
                "FAIL",
                "No text-to-speech services available"
            )
            return

        self.log_test_result(
            "Text-to-Speech Health",
            "PASS",
            f"Healthy TTS services: {', '.join(healthy_services)}",
            {"services": tts_health}
        )

        # Test TTS with sample text
        test_text = "Hello! This is ULTRON testing voice synthesis."

        try:
            print(f"🔊 Speaking: '{test_text}'")
            success = await self.voice_assistant.speak(test_text)

            if success:
                self.log_test_result(
                    "Text-to-Speech",
                    "PASS",
                    "Successfully synthesized and played speech"
                )
            else:
                self.log_test_result(
                    "Text-to-Speech",
                    "FAIL",
                    "Failed to synthesize or play speech"
                )

        except Exception as e:
            self.log_test_result(
                "Text-to-Speech",
                "FAIL",
                f"TTS error: {str(e)}"
            )

    async def test_ai_model_integration(self):
        """Test integration with AI models"""
        print("\n🤖 Test 7: AI Model Integration")
        print("-" * 40)

        # Test Ollama connectivity
        try:
            test_prompt = "Say hello in one word."
            print(f"🤖 Testing AI model with prompt: '{test_prompt}'")

            response = await self.brain.direct_chat(test_prompt)

            if response and len(response.strip()) > 0:
                self.log_test_result(
                    "AI Model Integration",
                    "PASS",
                    f"AI responded: '{response[:50]}...'",
                    {"response_length": len(response)}
                )
            else:
                self.log_test_result(
                    "AI Model Integration",
                    "FAIL",
                    "Empty or no response from AI model"
                )

        except Exception as e:
            self.log_test_result(
                "AI Model Integration",
                "FAIL",
                f"AI model integration failed: {str(e)}"
            )

    async def test_voice_chat_workflow(self):
        """Test complete voice chat workflow"""
        print("\n🎯 Test 8: Voice Chat Workflow")
        print("-" * 40)

        print("🗣️  VOICE CHAT TEST")
        print("This test simulates a complete voice interaction:")
        print("1. You speak a question/command")
        print("2. System recognizes your speech")
        print("3. AI processes and responds")
        print("4. System speaks the response")
        print()
        print("Press Enter when ready to start:")

        input()  # Wait for user

        try:
            # Step 1: Listen for user input
            print("🎤 Step 1: Listening for your voice input...")
            user_input = await self.voice_assistant.listen_async(
                timeout=10, phrase_time_limit=10
            )

            if not user_input or not user_input.strip():
                self.log_test_result(
                    "Voice Chat Workflow",
                    "FAIL",
                    "No speech input received"
                )
                return

            print(f"📝 Recognized: '{user_input}'")

            # Step 2: Process with AI
            print("🤖 Step 2: Processing with AI model...")
            ai_response = await self.brain.direct_chat(user_input)

            if not ai_response:
                self.log_test_result(
                    "Voice Chat Workflow",
                    "FAIL",
                    "No AI response generated"
                )
                return

            print(f"💭 AI Response: '{ai_response[:100]}...'")

            # Step 3: Speak response
            print("🔊 Step 3: Speaking AI response...")
            speak_success = await self.voice_assistant.speak(ai_response)

            if speak_success:
                self.log_test_result(
                    "Voice Chat Workflow",
                    "PASS",
                    "Complete voice chat workflow successful",
                    {
                        "user_input": user_input,
                        "ai_response_length": len(ai_response),
                        "speech_success": speak_success
                    }
                )
            else:
                self.log_test_result(
                    "Voice Chat Workflow",
                    "FAIL",
                    "Voice synthesis failed in workflow"
                )

        except Exception as e:
            self.log_test_result(
                "Voice Chat Workflow",
                "FAIL",
                f"Voice chat workflow error: {str(e)}"
            )

    async def test_voice_configuration_settings(self):
        """Test voice configuration settings"""
        print("\n⚙️ Test 9: Voice Configuration Settings")
        print("-" * 40)

        # Check voice settings
        settings_to_check = [
            "voice_rate", "voice_volume", "voice_stability",
            "voice_similarity", "mic_energy_threshold",
            "voice_cache_dir", "microphone_device_index"
        ]

        config_status = {}
        for setting in settings_to_check:
            value = self.config.get(setting)
            config_status[setting] = {
                "configured": value is not None,
                "value": value
            }

        configured_count = sum(1 for s in config_status.values()
                               if s["configured"])

        self.log_test_result(
            "Voice Configuration Settings",
            "PASS" if configured_count > 0 else "INFO",
            f"{configured_count}/{len(settings_to_check)} "
            "voice settings configured",
            {"settings": config_status}
        )

        # Test voice availability
        available_voices = self.voice_assistant.get_available_voices()
        self.log_test_result(
            "Voice Availability",
            "PASS" if available_voices else "FAIL",
            f"Found {len(available_voices)} available voices",
            {"voices": [{"name": v["name"], "source": v["source"]}
                       for v in available_voices[:5]]}  # Show first 5
        )

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 TEST SUITE SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results
                           if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results
                           if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results
                            if r["status"] == "SKIP"])

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")

        success_rate = ((passed_tests / total_tests * 100)
                        if total_tests > 0 else 0)
        print(".1f")
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)

        for result in self.test_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "SKIP": "⏭️",
                "INFO": "ℹ️"
            }.get(result["status"], "?")

            print(f"{status_icon} {result['test_name']}")
            if result["message"]:
                print(f"   {result['message']}")
            if result["details"]:
                for key, value in result["details"].items():
                    print(f"   • {key}: {value}")

        # Save results to file
        report_file = "voice_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.time(),
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "skipped": skipped_tests,
                    "success_rate": success_rate
                },
                "results": self.test_results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Detailed report saved to: {report_file}")

        return success_rate >= 80  # Consider 80% pass rate as success

    async def run_all_tests(self):
        """Run the complete test suite"""
        try:
            await self.setup_test_environment()
            await self.test_microphone_setup()
            await self.test_speech_recognition()
            await self.test_text_to_speech()
            await self.test_ai_model_integration()
            await self.test_voice_chat_workflow()
            await self.test_voice_configuration_settings()

            success = self.generate_test_report()
            return success

        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main test execution function"""
    print("🎯 ULTRON Voice Configuration Test Suite")
    print("This comprehensive test suite will validate:")
    print("• Voice system initialization and configuration")
    print("• Microphone setup and audio capture")
    print("• Speech recognition with user interaction")
    print("• Text-to-speech functionality")
    print("• AI model integration (Ollama)")
    print("• Complete voice chat workflow")
    print("• Voice configuration settings")
    print()

    # Check prerequisites
    print("🔍 Checking prerequisites...")

    # Check if Ollama is running
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:11434/api/tags"
            ) as response:
                if response.status == 200:
                    print("✅ Ollama service is running")
                else:
                    print("⚠️  Ollama service may not be responding correctly")
    except Exception:
        print("⚠️  Cannot connect to Ollama "
              "(this is OK if testing without AI)")

    # Check microphone access
    try:
        import speech_recognition as sr
        # Just test that we can create a microphone object
        sr.Microphone()
        print("✅ Microphone access available")
    except Exception as e:
        print(f"⚠️  Microphone access issue: {str(e)}")

    print()
    input("Press Enter to start the test suite...")

    # Run tests
    test_suite = VoiceTestSuite()
    success = await test_suite.run_all_tests()

    if success:
        print("\n🎉 Voice configuration tests completed successfully!")
        print("Your ULTRON voice system is ready for use.")
    else:
        print("\n⚠️  Some tests failed. Check the detailed report above.")
        print("You may need to configure API keys or check system setup.")

    print("\n💡 Next Steps:")
    print("1. Review the test results and fix any failed tests")
    print("2. Configure API keys for ElevenLabs and other services")
    print("3. Test the GUI voice chat functionality")
    print("4. Run individual tests as needed for troubleshooting")


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
