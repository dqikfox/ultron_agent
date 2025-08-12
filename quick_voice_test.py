"""
Quick Live Voice Test for ULTRON Agent 2
Test voice system with accessibility messages
"""

import pyttsx3
import time

def test_live_voice():
    """Test voice system with live accessibility messages"""
    print("🎙️ ULTRON Agent 2 - Live Voice Test")
    print("♿ Testing accessibility-focused voice feedback\n")
    
    try:
        # Initialize voice engine
        engine = pyttsx3.init()
        
        # Configure for accessibility
        voices = engine.getProperty('voices')
        if voices:
            # Find a clear voice (prefer female voices for accessibility)
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            else:
                engine.setProperty('voice', voices[0].id)
        
        # Set accessibility-friendly settings
        engine.setProperty('rate', 180)    # Moderate speed
        engine.setProperty('volume', 0.9)  # High volume
        
        # Test messages for different scenarios
        messages = [
            "Welcome to ULTRON Agent 2. Your digital accessibility assistant is ready.",
            "Voice control activated. How can I help you today?",
            "I can help you navigate, click, type, and control your computer using voice commands.",
            "For users with mobility impairments, I provide hands-free computer control.",
            "For users with visual impairments, I provide detailed screen descriptions.",
            "Say 'help' at any time to learn about available voice commands.",
            "ULTRON is here to transform your disability into a digital advantage."
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"🔊 Speaking message {i}/7: {message[:50]}...")
            engine.say(message)
            engine.runAndWait()
            time.sleep(0.5)  # Brief pause between messages
        
        print("\n✅ Live voice test completed successfully!")
        print("🎯 Voice system is working and accessibility-ready!")
        
    except Exception as e:
        print(f"❌ Voice test failed: {e}")

if __name__ == "__main__":
    test_live_voice()
