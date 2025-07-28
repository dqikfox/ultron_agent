#!/usr/bin/env python3
"""
Create basic audio files for ULTRON interface
Generates simple sine wave audio files for UI sounds
"""

import os
import wave
import struct
import math

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    """Generate a sine wave audio signal"""
    frames = int(duration * sample_rate)
    audio_data = []
    
    for i in range(frames):
        # Generate sine wave
        value = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        audio_data.append(struct.pack('<h', value))
    
    return b''.join(audio_data)

def create_wake_sound():
    """Create wake sound - ascending tone"""
    sample_rate = 44100
    duration = 0.5
    frames = int(duration * sample_rate)
    audio_data = []
    
    start_freq = 220  # A3
    end_freq = 440    # A4
    
    for i in range(frames):
        # Frequency sweep from low to high
        progress = i / frames
        frequency = start_freq + (end_freq - start_freq) * progress
        
        # Add some envelope (fade in/out)
        envelope = math.sin(math.pi * progress) * 0.3
        
        value = int(envelope * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        audio_data.append(struct.pack('<h', value))
    
    return b''.join(audio_data)

def create_button_sound():
    """Create button press sound - short click"""
    return generate_sine_wave(800, 0.1, amplitude=0.2)

def create_confirm_sound():
    """Create confirmation sound - two-tone beep"""
    sample_rate = 44100
    
    # First tone
    tone1 = generate_sine_wave(600, 0.15, sample_rate, 0.3)
    
    # Short pause
    pause_frames = int(0.05 * sample_rate)
    pause = b'\x00\x00' * pause_frames
    
    # Second tone (higher)
    tone2 = generate_sine_wave(800, 0.15, sample_rate, 0.3)
    
    return tone1 + pause + tone2

def save_wav_file(filename, audio_data, sample_rate=44100):
    """Save audio data as WAV file"""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

def main():
    """Generate all audio files"""
    print("Creating ULTRON audio files...")
    
    # Create audio files
    audio_files = {
        'wake.wav': create_wake_sound(),
        'button_press.wav': create_button_sound(),
        'confirm.wav': create_confirm_sound()
    }
    
    for filename, audio_data in audio_files.items():
        filepath = os.path.join(os.path.dirname(__file__), filename)
        save_wav_file(filepath, audio_data)
        print(f"Created: {filename}")
    
    print("Audio files created successfully!")

if __name__ == "__main__":
    main()
