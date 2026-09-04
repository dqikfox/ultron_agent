#!/usr/bin/env python3
"""Simple speaker test using pygame"""

import pygame
import numpy as np
import time

def test_speakers():
    """Test speakers with a simple tone"""
    print("🔊 Testing speakers with pygame...")
    
    # Initialize pygame mixer
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    
    # Generate a simple sine wave tone
    sample_rate = 22050
    duration = 2  # seconds
    frequency = 440  # A4 note
    
    # Create sine wave
    frames = int(duration * sample_rate)
    arr = np.zeros((frames, 2))
    
    for i in range(frames):
        wave = np.sin(2 * np.pi * frequency * i / sample_rate)
        arr[i][0] = wave * 0.3  # Left channel
        arr[i][1] = wave * 0.3  # Right channel
    
    # Convert to pygame sound
    sound = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
    
    print("Playing test tone (440Hz) for 2 seconds...")
    print("You should hear a clear tone from your speakers.")
    
    # Play the sound
    sound.play()
    time.sleep(duration + 0.5)  # Wait for sound to finish
    
    pygame.mixer.quit()
    print("✅ Speaker test complete!")

if __name__ == "__main__":
    test_speakers()