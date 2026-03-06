#!/usr/bin/env python3
"""
Enhanced STT Engine with OpenAI Whisper
Better accuracy and natural voice processing
"""

import whisper
import pyaudio
import wave
import tempfile
import os
from typing import Optional

class EnhancedSTT:
    def __init__(self):
        # Load Whisper model (base is good balance of speed/accuracy)
        self.model = whisper.load_model("base")
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        
    def listen_and_transcribe(self, duration: int = 5) -> Optional[str]:
        """Record audio and transcribe with Whisper"""
        try:
            # Record audio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎤 Listening...")
            frames = []
            for _ in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                wf = wave.open(tmp_file.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Transcribe with Whisper
                result = self.model.transcribe(tmp_file.name)
                text = result["text"].strip()
                
                # Cleanup
                os.unlink(tmp_file.name)
                
                return text if text else None
                
        except Exception as e:
            print(f"STT Error: {e}")
            return None

# Quick test
if __name__ == "__main__":
    stt = EnhancedSTT()
    print("Say something...")
    text = stt.listen_and_transcribe(3)
    print(f"You said: {text}")