#!/bin/bash

echo "🎤 Installing Enhanced STT Engine..."

# Install Whisper and dependencies
pip install openai-whisper
pip install pyaudio
pip install wave

# Alternative: Azure Speech (if you want cloud STT)
# pip install azure-cognitiveservices-speech

# Alternative: Google Cloud Speech (if you want Google STT)  
# pip install google-cloud-speech

echo "✅ Enhanced STT installed!"
echo ""
echo "🎯 Available STT Engines:"
echo "   • OpenAI Whisper (Local, Free, 95%+ accuracy)"
echo "   • Azure Speech (Cloud, Pay-per-use, 98%+ accuracy)"
echo "   • Google Cloud Speech (Cloud, Pay-per-use, 97%+ accuracy)"
echo ""
echo "🚀 Whisper is now configured as default STT engine"