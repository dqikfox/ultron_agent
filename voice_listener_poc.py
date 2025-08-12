import speech_recognition as sr

def listen_and_transcribe():
    """
    A proof-of-concept function to capture audio from the microphone,
    transcribe it to text, and print the result.
    """
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait a moment...")
        # Adjust for ambient noise to improve accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("\nListening... Please say something.")
        
        try:
            # Listen for audio input from the user
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing your speech...")
            
            # Use Google's free web speech API to recognize the audio
            text = recognizer.recognize_google(audio_data)
            print(f"\nTranscription: "{text}"")
            
        except sr.WaitTimeoutError:
            print("\nError: Listening timed out. No speech was detected.")
        except sr.UnknownValueError:
            print("\nError: Could not understand the audio. Please try again.")
        except sr.RequestError as e:
            print(f"\nError: Could not request results from the speech recognition service; {e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    print("--- Voice Listener Proof-of-Concept ---")
    print("This script will test the core speech-to-text functionality.")
    print("NOTE: You may need to install required libraries first:")
    print("pip install SpeechRecognition PyAudio")
    print("-" * 40)
    
    listen_and_transcribe()
    
    print("-" * 40)
    print("Script finished.")