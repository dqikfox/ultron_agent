    def _speak_openai(self, text):
        """OpenAI TTS implementation"""
        try:
            # Log the input text
            info(f"[OpenAI TTS] Input text: {text}")

            import openai

            api_key = self.voice_engines['openai']['api_key']
            client = openai.OpenAI(api_key=api_key)

            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )

        # Log the TTS output
        info(f"[OpenAI TTS] Response content length: {len(response.content)}")
            # Save and play audio
            with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(response.content)
                audio_file = f.name

            try:
            # Log the audio file path
            info(f"[OpenAI TTS] Audio file saved to: {audio_file}")

            # Play audio file
                if os_name == 'nt':
                    import winsound
                    winsound.PlaySound(audio_file, winsound.SND_FILENAME)
                else:
                    subprocess_run(['mpg123', audio_file], check=True, stdout=DEVNULL, stderr=DEVNULL)

                return True
            finally:
                try:
                    unlink(audio_file)
                except OSError:
                    pass

        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"OpenAI TTS error: {sanitize_log_input(str(e))}")
            return False
```
This code block does the same as the original code, but with additional logging to help diagnose any issues that may arise during speech synthesization.
    print("Testing ULTRON Voice Manager... - voice_manager.py:49")
    test_voice_system()

    # Test the system
    print("Testing ULTRON Voice Manager... - voice_manager.py:53")
    test_voice_system()
