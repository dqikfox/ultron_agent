#!/usr/bin/env python3
"""
ULTRON Voice Chat Demo
Interactive voice chat with your AI models directly from the command line.

This demo allows you to:
- Speak with your local Ollama models
- Test voice recognition and synthesis
- Experience the complete voice interaction workflow
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from voice import VoiceAssistant
from brain import UltronBrain

# Mock tools and memory for brain initialization
mock_tools = {}
mock_memory = type('MockMemory', (), {
    'get_context': lambda: {},
    'store_interaction': lambda *args: None
})()


class VoiceChatDemo:
    """Interactive voice chat demo"""

    def __init__(self):
        self.config = None
        self.voice_assistant = None
        self.brain = None

    async def initialize(self):
        """Initialize all components"""
        print("🚀 ULTRON Voice Chat Demo")
        print("=" * 50)

        try:
            # Load configuration
            print("📋 Loading configuration...")
            self.config = Config()
            print("✅ Configuration loaded")

            # Initialize voice assistant
            print("🎤 Initializing voice system...")
            self.voice_assistant = VoiceAssistant(self.config)
            print("✅ Voice system ready")

            # Initialize AI brain
            print("🧠 Initializing AI brain...")
            self.brain = UltronBrain(self.config, mock_tools, mock_memory)
            print("✅ AI brain ready")

            print("\n🎉 All systems initialized successfully!")
            print("You can now speak with your AI models using voice.")

        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            return False

        return True

    async def voice_chat_loop(self):
        """Main voice chat interaction loop"""
        print("\n🎯 VOICE CHAT MODE")
        print("Commands:")
        print("• Say anything to chat with AI")
        print("• Say 'quit' or 'exit' to end")
        print("• Say 'help' for commands")
        print()

        while True:
            try:
                # Listen for user input
                print("🎤 Listening... (speak now)")
                user_input = await self.voice_assistant.listen_async(
                    timeout=10, phrase_time_limit=10
                )

                if not user_input or not user_input.strip():
                    print("❌ No speech detected, trying again...")
                    continue

                print(f"📝 You said: '{user_input}'")

                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'stop', 'bye']:
                    print("👋 Goodbye!")
                    await self.voice_assistant.speak(
                        "Goodbye! Have a great day!")
                    break

                # Check for help
                if user_input.lower() in ['help', 'commands',
                                        'what can you do']:
                    help_text = ("I can chat with you using voice! "
                                 "Just speak naturally. Say 'quit' to exit.")
                    print(f"💬 {help_text}")
                    await self.voice_assistant.speak(help_text)
                    continue

                # Process with AI
                print("🤖 Thinking...")
                ai_response = await self.brain.direct_chat(user_input)

                if ai_response:
                    response_preview = ai_response[:100]
                    ellipsis = '...' if len(ai_response) > 100 else ''
                    print(f"💭 AI: {response_preview}{ellipsis}")

                    # Speak the response
                    print("🔊 Speaking response...")
                    await self.voice_assistant.speak(ai_response)
                else:
                    error_msg = "Sorry, I couldn't get a response from the AI."
                    print(f"❌ {error_msg}")
                    await self.voice_assistant.speak(error_msg)

            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                await self.voice_assistant.speak("Chat ended by user.")
                break
            except Exception as e:
                error_msg = f"Sorry, there was an error: {str(e)}"
                print(f"❌ {error_msg}")
                try:
                    await self.voice_assistant.speak(
                        "Sorry, there was an error.")
                except Exception as e:
                    print(f"❌ Speech error: {str(e)}")

    async def run_demo(self):
        """Run the complete demo"""
        if not await self.initialize():
            return

        print("\n" + "=" * 50)
        print("🎯 Ready for voice chat!")
        print("Make sure your microphone is working and Ollama is running.")
        print("Press Enter to start voice chat, or 'q' to quit:")

        choice = input().strip().lower()
        if choice == 'q':
            print("👋 Demo ended")
            return

        await self.voice_chat_loop()


async def main():
    """Main entry point"""
    demo = VoiceChatDemo()
    await demo.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

