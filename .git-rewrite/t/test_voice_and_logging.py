"""
Comprehensive Voice and Logging Test Suite for ULTRON Agent 2
Tests voice system functionality and ensures chat logging works properly
"""

import asyncio
import logging
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from voice_manager import UltronVoiceManager
except ImportError:
    print("❌ Warning: voice_manager not found, testing fallback systems")
    UltronVoiceManager = None

try:
    from action_logger import ActionLogger
except ImportError:
    print("❌ Error: action_logger not found")
    ActionLogger = None

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("❌ pyttsx3 not available")

class UltronSystemTester:
    """Test suite for ULTRON voice and logging systems"""
    
    def __init__(self):
        self.test_results = {}
        self.logger = self.setup_logging()
        self.action_logger = None
        self.voice_manager = None
        
        # Initialize systems
        self.initialize_systems()
    
    def setup_logging(self):
        """Setup test logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='🔧 %(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ultron_test.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def initialize_systems(self):
        """Initialize action logger and voice manager"""
        try:
            if ActionLogger:
                self.action_logger = ActionLogger()
                self.logger.info("✅ ActionLogger initialized successfully")
            else:
                self.logger.error("❌ ActionLogger not available")
        except Exception as e:
            self.logger.error(f"❌ ActionLogger initialization failed: {e}")
        
        try:
            if UltronVoiceManager:
                self.voice_manager = UltronVoiceManager()
                self.logger.info("✅ VoiceManager initialized successfully")
            else:
                self.logger.error("❌ VoiceManager not available")
        except Exception as e:
            self.logger.error(f"❌ VoiceManager initialization failed: {e}")
    
    def test_action_logging(self):
        """Test action logging functionality"""
        print("\n🧪 Testing Action Logging System...")
        
        if not self.action_logger:
            print("❌ ActionLogger not available - skipping tests")
            self.test_results['action_logging'] = False
            return False
        
        try:
            # Test basic logging
            self.action_logger.log_action("TEST_START", "Beginning action logging tests")
            
            # Test user input logging
            test_input = "Hello ULTRON, can you help me take a screenshot?"
            self.action_logger.log_user_input(test_input, "voice")
            
            # Test AI response logging
            test_response = "I'll help you take a screenshot. Let me activate the screenshot tool for you."
            self.action_logger.log_ai_response(test_response, "qwen2.5-coder", 1.2)
            
            # Test error logging
            self.action_logger.log_error("TEST_ERROR", "This is a test error for validation")
            
            # Test automation action logging
            self.action_logger.log_automation_action(
                "screenshot", 
                "Taking screenshot for accessibility user",
                {"filename": "test_screenshot.png", "method": "voice_command"}
            )
            
            # Test voice action logging
            self.action_logger.log_voice_action("TTS_SPEAK", "Screenshot saved successfully", "pyttsx3")
            
            print("✅ Action logging tests completed successfully")
            self.test_results['action_logging'] = True
            return True
            
        except Exception as e:
            print(f"❌ Action logging test failed: {e}")
            self.test_results['action_logging'] = False
            return False
    
    def test_voice_system_basic(self):
        """Test basic voice system functionality"""
        print("\n🗣️ Testing Basic Voice System...")
        
        # Test pyttsx3 directly
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                
                # Configure for accessibility
                voices = engine.getProperty('voices')
                if voices:
                    # Use first available voice
                    engine.setProperty('voice', voices[0].id)
                
                engine.setProperty('rate', 180)  # Moderate speed for accessibility
                engine.setProperty('volume', 0.9)  # High volume for hearing impaired users
                
                test_message = "ULTRON voice system test. Accessibility features active."
                print(f"🔊 Speaking: {test_message}")
                
                engine.say(test_message)
                engine.runAndWait()
                
                print("✅ pyttsx3 voice test successful")
                self.test_results['voice_basic'] = True
                
                # Log the voice test
                if self.action_logger:
                    self.action_logger.log_voice_action("TTS_TEST", test_message, "pyttsx3")
                
                return True
                
            except Exception as e:
                print(f"❌ pyttsx3 voice test failed: {e}")
                self.test_results['voice_basic'] = False
                return False
        else:
            print("❌ pyttsx3 not available")
            self.test_results['voice_basic'] = False
            return False
    
    def test_voice_manager_integration(self):
        """Test voice manager integration"""
        print("\n🎙️ Testing Voice Manager Integration...")
        
        if not self.voice_manager:
            print("❌ VoiceManager not available - skipping tests")
            self.test_results['voice_manager'] = False
            return False
        
        try:
            # Test accessibility-focused voice feedback
            accessibility_messages = [
                "Welcome to ULTRON Agent 2 - Your digital accessibility assistant",
                "Voice system ready. How can I help you today?",
                "Screenshot tool activated. Say 'take screenshot' to capture your screen",
                "Mouse movement completed safely. Coordinates validated.",
                "Task completed successfully. What would you like to do next?"
            ]
            
            for i, message in enumerate(accessibility_messages):
                print(f"🔊 Testing message {i+1}/5: {message[:50]}...")
                
                # Use voice manager speak method
                if hasattr(self.voice_manager, 'speak'):
                    self.voice_manager.speak(message)
                elif hasattr(self.voice_manager, 'say'):
                    self.voice_manager.say(message)
                
                # Log each voice action
                if self.action_logger:
                    self.action_logger.log_voice_action("TTS_ACCESSIBILITY", message, "voice_manager")
                
                # Small delay between messages
                time.sleep(0.5)
            
            print("✅ Voice manager integration test successful")
            self.test_results['voice_manager'] = True
            return True
            
        except Exception as e:
            print(f"❌ Voice manager test failed: {e}")
            self.test_results['voice_manager'] = False
            return False
    
    def test_accessibility_features(self):
        """Test accessibility-specific features"""
        print("\n♿ Testing Accessibility Features...")
        
        try:
            # Test voice feedback for different disability scenarios
            accessibility_scenarios = [
                {
                    "disability_type": "motor_impairment",
                    "message": "Voice command recognized. Executing mouse click for you.",
                    "context": "User with limited hand mobility using voice control"
                },
                {
                    "disability_type": "visual_impairment", 
                    "message": "Screen reader mode active. Button found at coordinates 150, 200.",
                    "context": "Describing screen elements for blind user"
                },
                {
                    "disability_type": "cognitive_disability",
                    "message": "Task completed. Click the green 'OK' button to continue.",
                    "context": "Simple, clear instructions for cognitive accessibility"
                }
            ]
            
            for scenario in accessibility_scenarios:
                print(f"🔊 Testing {scenario['disability_type']}: {scenario['message'][:40]}...")
                
                # Log accessibility action
                if self.action_logger:
                    self.action_logger.log_accessibility_action(
                        scenario['disability_type'],
                        scenario['message'],
                        scenario['context']
                    )
                
                # Speak accessibility message
                if PYTTSX3_AVAILABLE:
                    engine = pyttsx3.init()
                    engine.say(scenario['message'])
                    engine.runAndWait()
                
                time.sleep(0.3)
            
            print("✅ Accessibility features test successful")
            self.test_results['accessibility'] = True
            return True
            
        except Exception as e:
            print(f"❌ Accessibility features test failed: {e}")
            self.test_results['accessibility'] = False
            return False
    
    def test_chat_logging(self):
        """Test comprehensive chat logging"""
        print("\n💬 Testing Chat Logging...")
        
        if not self.action_logger:
            print("❌ ActionLogger not available - skipping chat tests")
            self.test_results['chat_logging'] = False
            return False
        
        try:
            # Simulate a complete chat session
            chat_session = [
                {
                    "user": "Hello ULTRON, I need help clicking on an icon because I can't use my mouse",
                    "ai": "I understand you need assistance with mouse clicking. I'll help you navigate using voice commands. Can you describe the icon you want to click?",
                    "model": "qwen2.5-coder"
                },
                {
                    "user": "It's the blue folder icon on the desktop, near the top left",
                    "ai": "I'll help you click the blue folder icon. Let me locate it using image recognition and perform the click for you.",
                    "model": "qwen2.5-coder"
                },
                {
                    "user": "Thank you, that worked perfectly!",
                    "ai": "You're welcome! I'm here to help make your computer accessible. Is there anything else you'd like me to help you with?",
                    "model": "qwen2.5-coder"
                }
            ]
            
            for i, exchange in enumerate(chat_session):
                print(f"💬 Logging chat exchange {i+1}/3...")
                
                # Log user input
                self.action_logger.log_user_input(exchange["user"], "voice")
                
                # Log AI response
                processing_time = 1.5 + (i * 0.3)  # Simulate varying response times
                self.action_logger.log_ai_response(exchange["ai"], exchange["model"], processing_time)
                
                # Log the accessibility context
                self.action_logger.log_action(
                    "ACCESSIBILITY_ASSISTANCE",
                    f"Providing assistance for user with mobility impairment - Exchange {i+1}",
                    {
                        "user_need": "motor_impairment_assistance",
                        "solution_type": "voice_controlled_automation",
                        "success": True
                    }
                )
            
            print("✅ Chat logging test successful")
            self.test_results['chat_logging'] = True
            return True
            
        except Exception as e:
            print(f"❌ Chat logging test failed: {e}")
            self.test_results['chat_logging'] = False
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("🧪 ULTRON AGENT 2 SYSTEM TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print("\n" + "="*60)
        
        if self.action_logger:
            self.action_logger.log_action(
                "TEST_COMPLETE",
                f"System tests completed - {passed_tests}/{total_tests} passed",
                {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "test_details": self.test_results
                }
            )
        
        # Voice announcement of results
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                result_message = f"ULTRON system tests completed. {passed_tests} out of {total_tests} tests passed."
                engine.say(result_message)
                engine.runAndWait()
            except:
                pass
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting ULTRON Agent 2 System Tests...")
        print("🎯 Testing voice system and chat logging for accessibility features")
        
        # Run all tests
        self.test_action_logging()
        self.test_voice_system_basic()
        self.test_voice_manager_integration()
        self.test_accessibility_features()
        self.test_chat_logging()
        
        # Generate report
        self.generate_test_report()

def main():
    """Main test function"""
    print("🤖 ULTRON Agent 2 - Voice and Logging System Test Suite")
    print("♿ Focus: Accessibility and Digital Inclusion Features")
    print("=" * 60)
    
    tester = UltronSystemTester()
    tester.run_all_tests()
    
    print("\n🔍 Check the following files for detailed logs:")
    print("  - ultron_test.log (test execution log)")
    print("  - ultron_actions.log (action logger output)")
    print("  - actions_[timestamp].json (detailed action log)")

if __name__ == "__main__":
    main()
