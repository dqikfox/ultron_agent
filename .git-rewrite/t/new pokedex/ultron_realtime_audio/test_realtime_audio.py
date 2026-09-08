#!/usr/bin/env python3
"""
ULTRON Real-Time Audio Test
Quick test to verify audio system is working
"""

import sys
import time
import threading

def test_dependencies():
    """Test if all audio dependencies are available"""
    print("🔍 Testing Dependencies...")
    
    missing = []
    
    try:
        import sounddevice as sd
        print("✅ sounddevice - Real-time audio streaming")
    except ImportError:
        missing.append("sounddevice")
        print("❌ sounddevice - MISSING")
    
    try:
        import webrtcvad
        print("✅ webrtcvad - Voice activity detection")
    except ImportError:
        missing.append("webrtcvad")
        print("❌ webrtcvad - MISSING")
    
    try:
        import speech_recognition as sr
        print("✅ speech_recognition - Speech-to-text")
    except ImportError:
        missing.append("speech_recognition")
        print("❌ speech_recognition - MISSING")
    
    try:
        import pyttsx3
        print("✅ pyttsx3 - Text-to-speech")
    except ImportError:
        missing.append("pyttsx3")
        print("❌ pyttsx3 - MISSING")
    
    try:
        import numpy as np
        print("✅ numpy - Audio processing")
    except ImportError:
        missing.append("numpy")
        print("❌ numpy - MISSING")
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    else:
        print("\n✅ All dependencies available!")
        return True

def test_audio_devices():
    """Test audio device availability"""
    print("\n🎧 Testing Audio Devices...")
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device['name']))
            if device['max_output_channels'] > 0:
                output_devices.append((i, device['name']))
        
        print(f"🎤 Input devices found: {len(input_devices)}")
        for i, name in input_devices[:3]:  # Show first 3
            print(f"   {i}: {name}")
        
        print(f"🔊 Output devices found: {len(output_devices)}")
        for i, name in output_devices[:3]:  # Show first 3
            print(f"   {i}: {name}")
        
        if len(input_devices) == 0:
            print("❌ No microphones found!")
            return False
        
        if len(output_devices) == 0:
            print("❌ No speakers found!")
            return False
        
        print("✅ Audio devices available!")
        return True
        
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")
        return False

def test_microphone():
    """Test microphone recording"""
    print("\n🎤 Testing Microphone...")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        sample_rate = 16000
        duration = 2  # 2 seconds
        
        print("Recording 2 seconds... Speak now!")
        
        # Record audio
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1,
                          dtype=np.float32)
        
        # Show countdown
        for i in range(duration, 0, -1):
            print(f"Recording: {i} seconds remaining...")
            time.sleep(1)
        
        sd.wait()  # Wait for recording to finish
        
        # Analyze recording
        max_volume = np.max(np.abs(recording))
        avg_volume = np.mean(np.abs(recording))
        
        print(f"Max volume: {max_volume:.4f}")
        print(f"Average volume: {avg_volume:.4f}")
        
        if max_volume > 0.01:
            print("✅ Microphone working! Audio detected.")
            
            # Test playback
            try:
                print("Playing back recording...")
                sd.play(recording, sample_rate)
                sd.wait()
                print("✅ Playback complete!")
                return True
            except Exception as e:
                print(f"⚠️ Playback failed: {e}")
                return True  # Mic still works
                
        else:
            print("❌ No audio detected. Check microphone connection and permissions.")
            return False
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_voice_activity_detection():
    """Test voice activity detection"""
    print("\n🗣️ Testing Voice Activity Detection...")
    
    try:
        import sounddevice as sd
        import webrtcvad
        import numpy as np
        
        vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        sample_rate = 16000
        frame_duration = 30  # ms
        frame_size = int(sample_rate * frame_duration / 1000)
        
        print("Testing VAD for 5 seconds... Try speaking and staying quiet!")
        
        def audio_callback(indata, frames, time, status):
            # Convert to int16 for VAD
            audio_data = (indata[:, 0] * 32767).astype(np.int16)
            audio_bytes = audio_data.tobytes()
            
            # Check voice activity
            is_speech = vad.is_speech(audio_bytes, sample_rate)
            
            if is_speech:
                print("🗣️ VOICE DETECTED!")
            else:
                print("🔇 Silence...")
        
        # Start stream
        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=frame_size,
            callback=audio_callback
        )
        
        with stream:
            time.sleep(5)
        
        print("✅ Voice Activity Detection working!")
        return True
        
    except Exception as e:
        print(f"❌ VAD test failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition"""
    print("\n🧠 Testing Speech Recognition...")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        print("Testing with built-in microphone...")
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("Say something! (5 seconds)")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Processing speech...")
                
                # Try to recognize
                text = recognizer.recognize_google(audio)
                print(f"✅ Recognized: '{text}'")
                return True
                
            except sr.WaitTimeoutError:
                print("⚠️ No speech detected in time limit")
                return False
            except sr.UnknownValueError:
                print("⚠️ Speech was detected but not understood")
                return False
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Speech recognition test failed: {e}")
        return False

def test_text_to_speech():
    """Test text-to-speech"""
    print("\n🔊 Testing Text-to-Speech...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices)}")
        
        if voices:
            for i, voice in enumerate(voices[:2]):  # Show first 2
                print(f"   {i}: {voice.name}")
        
        # Test speech
        test_text = "ULTRON real-time audio test successful!"
        print(f"Speaking: '{test_text}'")
        
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ Text-to-speech working!")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech test failed: {e}")
        return False

def main():
    """Run all audio tests"""
    print("🤖 ULTRON Real-Time Audio Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Dependencies
    test_results.append(("Dependencies", test_dependencies()))
    
    if not test_results[-1][1]:
        print("\n❌ Cannot continue without required dependencies")
        return
    
    # Test 2: Audio devices
    test_results.append(("Audio Devices", test_audio_devices()))
    
    # Test 3: Microphone
    test_results.append(("Microphone", test_microphone()))
    
    # Test 4: Voice Activity Detection
    test_results.append(("Voice Activity Detection", test_voice_activity_detection()))
    
    # Test 5: Speech Recognition
    test_results.append(("Speech Recognition", test_speech_recognition()))
    
    # Test 6: Text-to-Speech
    test_results.append(("Text-to-Speech", test_text_to_speech()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 ULTRON Real-Time Audio is ready!")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Click '🎤 START REAL-TIME'")
        print("  3. Say 'Hey ULTRON' to test!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Some features may not work properly.")
        print("Check the error messages above for troubleshooting.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
