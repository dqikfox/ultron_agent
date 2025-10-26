# ULTRON Agent 3.0 - Voice & Microphone System Documentation

## 🎤 Voice System Architecture

### Overview
The ULTRON Agent voice system provides bidirectional voice communication with three components:
1. **Text-to-Speech (TTS)**: AI speaks responses using ElevenLabs API or browser fallback
2. **Speech-to-Text (STT)**: Microphone captures user voice commands via Web Speech API
3. **Voice Recognition**: Continuous listening with automatic restart

---

## 🔧 System Components

### 1. Frontend Voice Controller
**File**: `gui/ultron_enhanced/web/app.js`

**Key Methods**:
- `toggleVoice()` - Main entry point for enabling/disabling voice
- `toggleVoiceChat(forceState)` - Handles server sync and state management
- `startVoiceRecognition()` - Initializes Web Speech API microphone
- `stopVoiceRecognition()` - Stops microphone and cleanup
- `speakText(text)` - Queues text for TTS playback
- `dequeueSpeech()` - Processes TTS queue with fallback logic

**State Variables**:
```javascript
this.voiceEnabled = false;      // Master voice enable flag
this.isListening = false;       // Microphone is actively listening
this.isSpeaking = false;        // TTS is currently playing
this.shouldRestartRecognition = false; // Auto-restart mic after speech
this.recognition = null;        // Web Speech API instance
this.ttsQueue = [];             // Queued TTS messages
```

---

### 2. Backend Voice Service
**File**: `voice.py`

**Responsibilities**:
- ElevenLabs API integration for premium TTS
- pyttsx3 fallback for offline TTS
- Voice status tracking and event emission
- Audio format conversion and streaming

**Key Classes**:
```python
class VoiceAssistant:
    def __init__(self):
        self.tts_enabled = False
        self.stt_enabled = False
        self.elevenlabs_client = None
        self.pyttsx3_engine = None
        self.voice_model = "e3mik6xHn4Sl51poljxK"  # ElevenLabs voice ID
```

**API Endpoints**:
- `POST /api/voice/toggle` - Enable/disable voice (handled by `web_gui_server.py`)
- `POST /api/voice/speak` - Queue text for TTS playback
- `GET /api/voice/status` - Get current voice service status

---

### 3. Web GUI Server Integration
**File**: `web_gui_server.py`

**Voice Route Handlers**:
```python
# Line ~345: Voice toggle endpoint
def handle_voice_toggle_request(self):
    """Toggle voice assistant on/off"""
    # Syncs with voice.py service
    # Returns: {"voice_enabled": bool, "status": str}

# Line ~417: Voice synthesis endpoint
def handle_voice_speak_request(self):
    """Generate TTS audio for text"""
    # 1. Try ElevenLabs API (premium)
    # 2. Fallback to pyttsx3 (offline)
    # 3. Return audio/mpeg or error
```

---

## 🚀 How to Enable Voice & Microphone

### Step-by-Step User Flow:

1. **Start ULTRON Agent**:
   ```bash
   .\run.bat
   ```

2. **Open Web GUI**:
   - Navigate to: http://localhost:8080
   - Click "INITIATE LINK" on start screen

3. **Enable Voice Button**:
   - Click the **microphone icon** in the top navigation bar
   - Browser will prompt: "Allow microphone access?"
   - Click "Allow"

4. **Voice System Activated**:
   - System message: "Voice chat enabled. I am listening."
   - Microphone starts continuous listening
   - AI will speak responses using TTS

5. **Disable Voice**:
   - Click microphone icon again
   - System message: "Voice chat disabled"
   - Microphone stops, TTS stops

---

## 🔐 Browser Permissions

### Microphone Access Required:
The Web Speech API requires explicit user permission to access the microphone.

**Permission States**:
- ✅ **Granted**: Voice recognition works
- ❌ **Denied**: Error message shown, voice disabled
- ⏳ **Prompt**: Browser asks user on first click

**Debugging Permission Issues**:
```javascript
// Check current permission state (Developer Console)
navigator.permissions.query({name: 'microphone'})
  .then(result => console.log('Mic permission:', result.state));

// States: 'granted', 'denied', or 'prompt'
```

**Reset Permissions**:
1. Click the lock icon in browser address bar
2. Find "Microphone" setting
3. Change to "Ask" or "Allow"
4. Reload page

---

## 📊 Voice System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. User Clicks Voice Button (Microphone Icon)             │
│     - Calls: toggleVoice() → toggleVoiceChat()             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Frontend Sends POST /api/voice/toggle                   │
│     - Body: {"enable": true}                                │
│     - web_gui_server.py receives request                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Backend Updates Voice Service (voice.py)                │
│     - Sets: voice_enabled = true                            │
│     - Emits event: voice_status_changed                     │
│     - Returns: {"voice_enabled": true, "status": "enabled"} │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Frontend Receives Response                              │
│     - Sets: this.voiceEnabled = true                        │
│     - Calls: startVoiceRecognition()                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Web Speech API Initialized                              │
│     - Creates: new SpeechRecognition()                      │
│     - Sets: continuous = true, lang = 'en-US'               │
│     - Starts: recognition.start()                           │
│     - Browser prompts for microphone permission             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. User Grants Microphone Permission                       │
│     - recognition.onstart fires                             │
│     - Sets: this.isListening = true                         │
│     - Message: "Listening for voice commands…"              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  7. User Speaks into Microphone                             │
│     - recognition.onresult fires with transcript            │
│     - Calls: handleVoiceTranscript(transcript)              │
│     - Sends: sendChatMessage(text, {fromVoice: true})       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  8. AI Processes Command & Responds                         │
│     - POST /api/llm/chat with user text                     │
│     - LLM generates response                                │
│     - Backend calls: voice.speak(response_text)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  9. TTS Playback                                            │
│     - Frontend calls: speakText(response)                   │
│     - Queues text in: this.ttsQueue                         │
│     - Calls: dequeueSpeech()                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  10. Audio Generation & Playback                            │
│      - Try ElevenLabs API: POST /api/voice/speak            │
│      - Success: Play audio via <audio> element              │
│      - Failure: Fallback to browser speechSynthesis         │
│      - During playback: Microphone paused                   │
│      - After playback: Microphone resumes                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 TTS (Text-to-Speech) System

### Dual TTS Architecture:

**Primary: ElevenLabs API**
- **Pros**: High-quality, natural-sounding voice
- **Cons**: Requires API key, uses credits, network latency
- **Implementation**: `voice.py` + `web_gui_server.py` integration
- **Audio Format**: MP3, 44.1kHz, 128kbps

**Fallback: Browser SpeechSynthesis**
- **Pros**: Free, offline, no API required
- **Cons**: Robotic voice quality, browser-dependent
- **Implementation**: `app.js` Web Speech API
- **Activation**: Auto-enabled when ElevenLabs fails

### TTS Queue Processing:

**CRITICAL**: Fixed dual TTS bug (2025-10-24)

**Problem (Before Fix)**:
```javascript
async dequeueSpeech() {
    try {
        await audioElement.play(); // API TTS succeeds
    } catch (error) {
        speechSynthesis.speak(utterance); // Never runs
    } finally {
        // ALWAYS RUNS - processes queue again!
        if (this.ttsQueue.length) this.dequeueSpeech();
    }
}
// Result: BOTH API and browser TTS play simultaneously
```

**Solution (After Fix)**:
```javascript
async dequeueSpeech() {
    try {
        // API TTS
        audioElement.onended = () => {
            // Process queue ONLY in callback
            if (this.ttsQueue.length) this.dequeueSpeech();
        };
        await audioElement.play();
        return; // EXIT - don't run fallback or finally
    } catch (error) {
        // Browser TTS fallback
        utterance.onend = () => {
            // Process queue ONLY in callback
            if (this.ttsQueue.length) this.dequeueSpeech();
        };
        speechSynthesis.speak(utterance);
        return; // EXIT - don't run finally
    } finally {
        // Only runs if BOTH methods fail
        if (this.ttsQueue.length) this.dequeueSpeech();
    }
}
// Result: Only ONE TTS method plays
```

**Key Fix Points**:
1. ✅ Queue processing moved into `onended`/`onend` callbacks
2. ✅ Early `return;` statements prevent fallback execution
3. ✅ `finally` block only runs if both TTS methods fail
4. ✅ Microphone automatically pauses during TTS playback
5. ✅ Microphone automatically resumes after TTS completes

---

## 🎙️ STT (Speech-to-Text) System

### Web Speech API Configuration:

```javascript
const recognition = new SpeechRecognition();
recognition.continuous = true;      // Keep listening after each result
recognition.interimResults = false; // Only return final results
recognition.lang = 'en-US';         // Language setting

// Event Handlers:
recognition.onstart = () => {
    // Microphone activated
    this.isListening = true;
    this.shouldRestartRecognition = true;
};

recognition.onresult = (event) => {
    // Process speech-to-text results
    const transcript = event.results[0][0].transcript;
    handleVoiceTranscript(transcript);
};

recognition.onerror = (event) => {
    // Handle errors (permission denied, no speech, etc.)
    if (event.error === 'not-allowed') {
        // Microphone permission denied by user
        this.voiceEnabled = false;
    }
};

recognition.onend = () => {
    // Auto-restart if still enabled
    this.isListening = false;
    if (this.shouldRestartRecognition && this.voiceEnabled) {
        recognition.start();
    }
};
```

### Continuous Listening Logic:

**Goal**: Keep microphone active even during AI processing

**Implementation**:
1. Recognition starts when voice enabled
2. `onresult` fires when user speaks
3. Transcript sent to LLM for processing
4. `onend` fires automatically after each result
5. If `this.shouldRestartRecognition === true`, restart immediately
6. Cycle continues until user disables voice

**Pause During TTS**:
```javascript
// In dequeueSpeech():
if (this.recognition && this.isListening) {
    this.recognition.stop(); // Pause mic during AI speech
}

// In audioElement.onended or utterance.onend:
if (this.voiceRecognition && this.voiceEnabled) {
    this.recognition.start(); // Resume mic after AI finishes
}
```

---

## 🔧 Configuration

### ElevenLabs API Setup:

**1. Get API Key**:
- Visit: https://elevenlabs.io/
- Sign up and copy API key from settings

**2. Set Environment Variable**:
```powershell
# Windows PowerShell
$env:ELEVENLABS_APIKEY = "your_api_key_here"

# Or add to system environment variables permanently
```

**3. Update ultron_config.json**:
```json
{
    "voice_enabled": true,
    "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY",
    "voice_engine": "elevenlabs",
    "tts_engine": "elevenlabs",
    "stt_engine": "whisper",
    "voice_model": "e3mik6xHn4Sl51poljxK"
}
```

**4. Verify Connection**:
```bash
# Check voice.py logs
tail -f logs/voice.log

# Expected output:
# ✅ ElevenLabs connected successfully
# 2025-10-24 16:21:22 - voice - INFO - ElevenLabs initialized successfully with 32 voices available
```

### Voice Configuration Options:

| Setting | Description | Default | Options |
|---------|-------------|---------|---------|
| `voice_enabled` | Master voice toggle | `false` | `true`/`false` |
| `voice_engine` | TTS provider | `"elevenlabs"` | `"elevenlabs"`, `"pyttsx3"` |
| `stt_engine` | STT provider | `"whisper"` | `"whisper"`, `"browser"` |
| `voice_model` | ElevenLabs voice ID | `"e3mik6xHn4Sl51poljxK"` | Any ElevenLabs voice ID |
| `tts_engine` | Text-to-speech backend | `"elevenlabs"` | `"elevenlabs"`, `"pyttsx3"` |

---

## 🐛 Troubleshooting

### Issue 1: Microphone Not Working

**Symptoms**:
- Clicking voice button does nothing
- Browser doesn't prompt for microphone
- Error: "Voice recognition is not supported"

**Solutions**:
1. **Check Browser Compatibility**:
   - Chrome/Edge: ✅ Full support
   - Firefox: ⚠️ Limited support
   - Safari: ⚠️ Requires webkit prefix

2. **Check Microphone Permission**:
   ```javascript
   // In browser console:
   navigator.permissions.query({name: 'microphone'})
     .then(result => console.log(result.state));
   ```

3. **Reset Browser Permission**:
   - Chrome: `chrome://settings/content/microphone`
   - Edge: `edge://settings/content/microphone`
   - Allow `localhost:8080`

4. **Check Hardware**:
   ```powershell
   # Windows: Test microphone in Settings
   Start-Process ms-settings:sound
   ```

---

### Issue 2: TTS Not Speaking

**Symptoms**:
- AI responds but no audio plays
- Error: "Voice synthesis unavailable"

**Solutions**:
1. **Check ElevenLabs Credits**:
   - Login to: https://elevenlabs.io/
   - Verify credits remaining
   - Expected usage: ~250 credits per response

2. **Check API Key**:
   ```powershell
   # Verify environment variable set
   echo $env:ELEVENLABS_APIKEY
   ```

3. **Check Logs**:
   ```bash
   # View voice service logs
   tail -f logs/voice.log

   # Expected output on success:
   # 2025-10-24 16:25:16 - voice - INFO - TTS initiated for AI response

   # Error output on API failure:
   # 2025-10-24 16:25:17 - voice - WARNING - ElevenLabs TTS failed: quota_exceeded
   ```

4. **Test Browser Fallback**:
   ```javascript
   // In browser console:
   const utterance = new SpeechSynthesisUtterance('Test');
   window.speechSynthesis.speak(utterance);
   ```

---

### Issue 3: Dual TTS (Both API and Browser Playing)

**Status**: ✅ **FIXED** (2025-10-24)

**If Still Occurring**:
1. Hard refresh browser: `Ctrl+Shift+R`
2. Clear browser cache completely
3. Check `app.js` Line 1841 for fix:
   ```javascript
   // Must have early return after successful TTS:
   await this.audioElement.play();
   return; // <-- MUST BE HERE
   ```

---

### Issue 4: Voice Auto-Enables on Startup

**Status**: ✅ **FIXED** (2025-10-24)

**If Still Occurring**:
1. Check `app.js` Line 360:
   ```javascript
   async handleStartupAnnouncement() {
       this.voiceEnabled = false; // <-- MUST BE FALSE
       // No speakText() call here
   }
   ```

2. Check `app.js` Line 520:
   ```javascript
   // Must NOT auto-enable from server status
   const voiceStatusText = (voiceSnapshot.status || 'DISABLED').toUpperCase();
   // No this.voiceEnabled = true assignment
   ```

---

## 📝 Developer Notes

### Adding New TTS Providers:

**Step 1**: Update `voice.py`
```python
class VoiceAssistant:
    async def speak(self, text: str):
        if self.tts_engine == "elevenlabs":
            return await self._elevenlabs_speak(text)
        elif self.tts_engine == "new_provider":
            return await self._new_provider_speak(text)
        else:
            return await self._fallback_speak(text)
```

**Step 2**: Add API integration
```python
async def _new_provider_speak(self, text: str):
    # Implement new provider API calls
    response = await self.new_provider_client.synthesize(text)
    return response.audio_content
```

**Step 3**: Update config options in `ultron_config.json`

---

### Testing Voice System:

**Unit Test Voice Toggle**:
```python
# tests/test_voice.py
async def test_voice_toggle():
    voice = VoiceAssistant()

    # Test enable
    result = await voice.toggle(True)
    assert result["voice_enabled"] == True

    # Test disable
    result = await voice.toggle(False)
    assert result["voice_enabled"] == False
```

**Integration Test Full Flow**:
```python
async def test_voice_conversation():
    # 1. Enable voice
    response = await client.post("/api/voice/toggle", json={"enable": True})
    assert response.json()["voice_enabled"] == True

    # 2. Send voice command
    response = await client.post("/api/llm/chat", json={"message": "Hello"})
    assert "response" in response.json()

    # 3. Verify TTS called
    # Check logs for TTS initiation
```

---

## 🔗 Related Files

### Core Voice Files:
- `voice.py` - Backend voice service (ElevenLabs, pyttsx3)
- `gui/ultron_enhanced/web/app.js` - Frontend voice controller
- `web_gui_server.py` - Voice API endpoints (Lines 345, 417)
- `ultron_config.json` - Voice configuration settings

### Documentation:
- `.github/copilot-instructions.md` - Main developer guide
- `FIXES_SUMMARY_2025-10-24.md` - Recent voice fixes
- `GUI_DOCUMENTATION.md` - GUI interaction patterns

### Logs:
- `logs/voice.log` - Voice service logs
- `logs/web_gui_server.log` - API endpoint logs
- `ultron_master_startup.log` - System startup logs

---

## ✅ Voice System Health Checklist

Before reporting voice issues, verify:

- [ ] **Services Running**: `run.bat` completed successfully
- [ ] **Browser Compatible**: Using Chrome/Edge (not Firefox/Safari)
- [ ] **Microphone Permission**: Granted in browser settings
- [ ] **Hardware Working**: Test microphone in OS settings
- [ ] **API Key Set**: `$env:ELEVENLABS_APIKEY` exists
- [ ] **Credits Available**: ElevenLabs account has credits
- [ ] **Network Connection**: Can reach https://api.elevenlabs.io
- [ ] **Logs Clean**: No errors in `logs/voice.log`
- [ ] **Port 8080 Open**: Web GUI accessible at localhost:8080
- [ ] **Latest Code**: Hard refresh browser (`Ctrl+Shift+R`)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-24 17:35 UTC
**Status**: ✅ Voice & Microphone Fully Functional
**Recent Fixes**: Dual TTS prevention, Auto-enable prevention

---

## 🎯 Quick Reference

### Enable Voice (User):
1. Open http://localhost:8080
2. Click microphone icon in nav bar
3. Allow browser microphone permission
4. Speak commands naturally

### Disable Voice (User):
1. Click microphone icon again
2. Voice stops listening immediately

### Voice Button States:
- **🎤 Gray/Off**: Voice disabled
- **🎤 Green/On**: Voice enabled, listening
- **🎤 Red/Error**: Permission denied or error

### Common Voice Commands:
- "What time is it?"
- "Run system diagnostics"
- "Open LLM chat"
- "Show me the tools"
- "Execute [tool name]"

---

**For Support**: Check `logs/voice.log` and browser console for detailed error messages.
