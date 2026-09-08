from config import Config
from voice import VoiceAssistant
import asyncio

async def main():
    config = Config()
    config.data["use_voice"] = True
    va = VoiceAssistant(config)
    print("Testing voice.speak()...")
    try:
        await va.speak("Theres No Strings On Me")
        print("Speech completed successfully.")
    except Exception as e:
        print(f"VoiceAssistant.speak() failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
