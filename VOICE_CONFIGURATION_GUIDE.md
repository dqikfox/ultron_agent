# ULTRON Agent Voice System Configuration Guide

## Overview
The ULTRON Agent now includes full voice integration with automatic fallback support. This guide explains how to configure and use the voice system.

## Voice System Architecture

### Available Voice Implementations
1. **Primary**: `voice.py` - Full ElevenLabs integration with STT/TTS
2. **Fallback**: `voice_manager.py` - Simple pyttsx3 TTS only
3. **Auto-Fallback Chain**: ElevenLabs → pyttsx3 → Console output

### Configuration Options

#### Basic Voice Configuration
```json
{
  "use_voice": true,
  "voice_engine": "elevenlabs",
  "elevenlabs_api_key": "your_api_key_here",
  "elevenlabs_agent_id": "voice_agent_id_here",
  "stt_engine": "whisper",
  "tts_engine": "elevenlabs"
}
```

#### Voice Settings
- `use_voice`: Enable/disable voice system (default: false)
- `voice_engine`: Primary voice engine ("elevenlabs" or "pyttsx3")
- `elevenlabs_api_key`: Your ElevenLabs API key
- `elevenlabs_agent_id`: ElevenLabs voice agent ID
- `stt_engine`: Speech-to-text engine ("whisper", "google", etc.)
- `tts_engine`: Text-to-speech engine ("elevenlabs", "pyttsx3", etc.)

## Setup Instructions

### 1. Configure API Keys

#### ElevenLabs Setup
1. Go to [ElevenLabs](https://elevenlabs.io)
2. Sign up for an account
3. Get your API key from the dashboard
4. Create a voice agent or use a pre-made voice
5. Update `ultron_config.json`:
```json
{
  "elevenlabs_api_key": "sk_your_api_key_here",
  "elevenlabs_agent_id": "your_voice_agent_id"
}
```

#### Alternative: Use Environment Variables
```bash
# Set environment variables instead of config file
export ELEVENLABS_API_KEY="sk_your_api_key_here"
export ELEVENLABS_AGENT_ID="your_voice_agent_id"
```

### 2. Test Voice Integration

#### Run Voice Integration Test
```bash
python test_voice_integration.py
```

#### Run Voice Command Simulator
```bash
python voice_command_simulator.py
```

### 3. Start ULTRON with Voice

#### Standard Startup
```bash
python main.py
```

#### Force Web GUI Mode
```bash
python main.py --web
```

## Voice Commands

### Basic Commands
- "hello ultron" - Basic greeting
- "what time is it" - Get current time
- "tell me a joke" - Get a joke
- "open browser" - Open web browser
- "show system status" - Display system information
- "list available tools" - Show available tools
- "goodbye" - Exit voice mode

### Tool Integration
The voice system automatically integrates with all loaded tools. Any tool that has a `match()` method can be triggered by voice commands.

## Troubleshooting

### Common Issues

#### 1. Voice System Not Initializing
**Symptoms**: Voice commands not working, no audio output
**Solutions**:
- Check `ultron_config.json` for correct `use_voice: true`
- Verify API keys are properly configured
- Check logs for initialization errors

#### 2. ElevenLabs Not Working
**Symptoms**: Falls back to pyttsx3, poor voice quality
**Solutions**:
- Verify ElevenLabs API key is correct
- Check ElevenLabs account has credits
- Ensure `elevenlabs_agent_id` is valid

#### 3. No Audio Output
**Symptoms**: Commands processed but no voice response
**Solutions**:
- Check system audio settings
- Verify microphone permissions (if using STT)
- Test with `voice_command_simulator.py`

#### 4. Import Errors
**Symptoms**: "ImportError: No module named 'voice'"
**Solutions**:
- Ensure `voice.py` exists in project root
- Check Python path includes project directory
- Install missing dependencies

### Log Files
Check these log files for detailed error information:
- `logs/agent_core.log` - Main agent logs
- `logs/voice.log` - Voice system specific logs
- `logs/error.log` - Error details

### Debug Mode
Enable debug logging in `ultron_config.json`:
```json
{
  "logging": {
    "level": "DEBUG",
    "file": "logs/debug.log"
  }
}
```

## Advanced Configuration

### Custom Voice Settings
```json
{
  "voice_settings": {
    "speech_rate": 180,
    "voice_volume": 0.8,
    "voice_gender": "female",
    "language": "en-US"
  }
}
```

### Multiple Voice Engines
The system supports multiple voice engines simultaneously:
```json
{
  "voice_engines": {
    "primary": "elevenlabs",
    "fallback": "pyttsx3",
    "offline": "console"
  }
}
```

## API Reference

### Voice Methods
- `agent.speak(text, async_mode=True)` - Speak text
- `agent.handle_voice_command(command)` - Process voice command
- `agent.start_voice_listening()` - Start continuous listening

### Voice System Classes
- `VoiceAssistant` - Full ElevenLabs integration
- `UltronVoiceManager` - Simple pyttsx3 fallback

## Performance Tips

### Optimization Settings
```json
{
  "performance": {
    "voice_cache_enabled": true,
    "voice_cache_size": 100,
    "async_voice_processing": true
  }
}
```

### System Requirements
- **Minimum**: Python 3.8+, Windows/Linux/MacOS
- **Recommended**: Python 3.10+, 4GB RAM, microphone
- **Optimal**: Python 3.11+, 8GB RAM, quality microphone

## Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables for production
- Rotate keys regularly
- Monitor API usage

### Voice Data Privacy
- Voice commands are processed locally when possible
- ElevenLabs processes audio server-side (check their privacy policy)
- Logs may contain voice command transcripts

## Support

### Getting Help
1. Check the logs in `logs/` directory
2. Run the test scripts to isolate issues
3. Verify configuration matches this guide
4. Check GitHub issues for similar problems

### Test Scripts
- `test_voice_integration.py` - Basic voice system test
- `voice_command_simulator.py` - Simulate voice commands
- `run.bat` - Full system startup with diagnostics

---

*Voice system configuration complete. The ULTRON Agent now supports full voice interaction with automatic fallbacks and comprehensive error handling.*
