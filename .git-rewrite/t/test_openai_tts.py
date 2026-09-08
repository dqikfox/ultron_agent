
import openai

# Replace with your actual OpenAI API key
api_key = "your_openai_api_key"
client = openai.OpenAI(api_key=api_key)

try:
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello, this is a test."
)

with open("test.mp3", "wb") as f:
    f.write(response.content)

    print("Audio file generated successfully: test.mp3 - test_openai_tts.py:18")
except Exception as e:

    print(f"Error generating audio file: {str(e)} - test_openai_tts.py:21")
```
This code will attempt to generate an audio file using the specified model and voice. If successful, it will save the audio file as `test.mp3` in the current directory. If an error occurs during the process, it will print an error message with details about the issue.

Please note that you need to replace `"your_openai_api_key"` with your actual OpenAI API key before running this code.

