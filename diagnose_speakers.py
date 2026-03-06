#!/usr/bin/env python3
"""Speaker Diagnostic Tool for ULTRON Agent"""

import subprocess
import os
import sys
import json
from pathlib import Path

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_audio_devices():
    """Check available audio devices"""
    print("🔊 AUDIO DEVICES:")
    
    # Check ALSA devices
    stdout, stderr, code = run_command("aplay -l")
    if code == 0:
        print("  ✅ ALSA devices found:")
        for line in stdout.split('\n'):
            if 'card' in line:
                print(f"    {line}")
    else:
        print("  ❌ No ALSA devices found")
    
    # Check PulseAudio
    stdout, stderr, code = run_command("pactl list sinks short")
    if code == 0:
        print("  ✅ PulseAudio sinks:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"    {line}")
    else:
        print("  ❌ PulseAudio not available")

def test_audio_playback():
    """Test audio playback with different methods"""
    print("\n🎵 AUDIO PLAYBACK TESTS:")
    
    # Test speaker-test
    print("  Testing with speaker-test...")
    stdout, stderr, code = run_command("timeout 3 speaker-test -t sine -f 1000 -c 2 -l 1")
    if code == 0:
        print("    ✅ speaker-test works")
    else:
        print(f"    ❌ speaker-test failed: {stderr}")
    
    # Test aplay with /dev/urandom
    print("  Testing with aplay...")
    stdout, stderr, code = run_command("timeout 2 aplay -f cd /dev/urandom 2>/dev/null")
    if code == 0 or code == 124:  # 124 is timeout exit code
        print("    ✅ aplay works")
    else:
        print(f"    ❌ aplay failed")

def check_volume_levels():
    """Check system volume levels"""
    print("\n🔊 VOLUME LEVELS:")
    
    # Check ALSA mixer
    stdout, stderr, code = run_command("amixer get Master")
    if code == 0:
        for line in stdout.split('\n'):
            if '[' in line and '%' in line:
                print(f"  Master: {line.strip()}")
    
    # Check PulseAudio volume
    stdout, stderr, code = run_command("pactl get-sink-volume @DEFAULT_SINK@")
    if code == 0:
        print(f"  PulseAudio: {stdout}")

def check_audio_processes():
    """Check what processes are using audio"""
    print("\n🎧 AUDIO PROCESSES:")
    
    stdout, stderr, code = run_command("lsof /dev/snd/* 2>/dev/null")
    if stdout:
        print("  Processes using audio:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"    {line}")
    else:
        print("  No processes using audio devices")

def test_python_audio():
    """Test Python audio libraries"""
    print("\n🐍 PYTHON AUDIO LIBRARIES:")
    
    # Test pygame
    try:
        import pygame
        pygame.mixer.init()
        print("  ✅ pygame.mixer available")
        pygame.mixer.quit()
    except Exception as e:
        print(f"  ❌ pygame.mixer failed: {e}")
    
    # Test playsound
    try:
        import playsound
        print("  ✅ playsound available")
    except Exception as e:
        print(f"  ❌ playsound not available: {e}")
    
    # Test pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("  ✅ pyttsx3 available")
    except Exception as e:
        print(f"  ❌ pyttsx3 failed: {e}")

def main():
    """Run complete speaker diagnostics"""
    print("🔧 ULTRON SPEAKER DIAGNOSTICS")
    print("=" * 50)
    
    check_audio_devices()
    check_volume_levels()
    check_audio_processes()
    test_audio_playback()
    test_python_audio()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    
    # Check if audio is muted
    stdout, stderr, code = run_command("amixer get Master | grep -o '\\[off\\]'")
    if stdout:
        print("  ⚠️  Audio appears to be MUTED - run: amixer set Master unmute")
    
    # Check volume level
    stdout, stderr, code = run_command("amixer get Master | grep -o '[0-9]*%' | head -1")
    if stdout:
        volume = int(stdout.replace('%', ''))
        if volume < 20:
            print(f"  ⚠️  Volume is low ({volume}%) - run: amixer set Master 50%")
    
    print("  💡 To test TTS: python3 test_tts.py")
    print("  💡 To fix audio: sudo apt install pulseaudio alsa-utils")

if __name__ == "__main__":
    main()