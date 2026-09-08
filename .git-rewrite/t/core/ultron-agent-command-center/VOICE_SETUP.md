# Voice Setup Guide

## ElevenLabs Configuration

### 1. Get Your API Key
1. Go to [ElevenLabs](https://elevenlabs.io)
2. Sign up or log in
3. Go to Profile → API Keys
4. Copy your API key

### 2. Configure the Application
1. Open `.env` file in the project root
2. Replace `your_elevenlabs_api_key_here` with your actual API key:
   ```
   ELEVENLABS_API_KEY=sk-your-actual-api-key-here
   ```

### 3. Voice Selection
- **System Voices**: Always available (uses browser TTS)
- **ElevenLabs Voices**: Available when API key is configured
- **Default**: System voices are used as fallback

### 4. Troubleshooting

#### No Voices Available
- Check if `.env` file exists
- Verify API key is correct
- Check internet connection
- System voices should always work as fallback

#### ElevenLabs Voices Not Loading
- Verify API key in `.env` file
- Check ElevenLabs account status
- Ensure you have character credits remaining
- Check browser console for error messages

#### Voice Not Playing
- Check system audio settings
- Try different voice (system vs ElevenLabs)
- Verify browser permissions for audio
- Check if audio is muted

### 5. Voice Settings (ElevenLabs Only)
- **Stability**: Controls voice consistency (0-1)
- **Similarity**: Controls voice similarity to original (0-1)
- **Style**: Controls speaking style variation (0-1)
- **Speaker Boost**: Enhances voice clarity

### 6. Usage Limits
- Free tier: 10,000 characters/month
- Check usage in ElevenLabs dashboard
- Monitor character count in app status

## Quick Fix Commands

```bash
# Rebuild with fixes
npm run build

# Start development server
npm run dev

# Check voice service status
# Look for "ELEVENLABS" status indicator in app
```