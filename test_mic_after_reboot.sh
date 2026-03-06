#!/bin/bash
echo "🎤 Post-Reboot Microphone Test"
echo "=============================="

# Test 1: Hardware detection
echo "1. Hardware detection:"
arecord -l | grep -i capture

# Test 2: PipeWire sources
echo -e "\n2. PipeWire audio sources:"
wpctl status | grep -A5 "Sources:"

# Test 3: Quick recording test
echo -e "\n3. Recording test (3 seconds):"
arecord -D hw:1,0 -f cd -t wav -d 3 reboot_test.wav 2>/dev/null && echo "✅ Recording successful" || echo "❌ Recording failed"

# Test 4: Python speech recognition
echo -e "\n4. Python microphone test:"
. venv/bin/activate 2>/dev/null || true
python3 -c "
import speech_recognition as sr
try:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print('✅ Python microphone initialized')
except Exception as e:
    print(f'❌ Python microphone failed: {e}')
" 2>/dev/null

echo -e "\n🎤 Test complete. If all tests pass, your microphone is working!"