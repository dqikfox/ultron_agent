# ULTRON GUI - QUICK FIX IMPLEMENTATION GUIDE

Complete code patches ready to deploy. Apply in order.

---

## PATCH 1: NAVIGATION SYSTEM FIX

**File**: `gui/ultron_enhanced/web/app.js`

**Find this section** (around line 259-264):
```javascript
document.querySelectorAll('.nav-button').forEach(btn => {
    btn.addEventListener('click', (event) => {
        const section = btn.dataset.section;
        showSection(section);
    });
});
```

**Replace with**:
```javascript
// Event delegation - single listener for all nav buttons
document.querySelector('.nav-buttons-grid').addEventListener('click', (e) => {
    const btn = e.target.closest('.nav-button');
    if (!btn) return;

    // Prevent default onclick handlers from firing
    e.stopPropagation();

    // Update active state
    document.querySelectorAll('.nav-button').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
        b.setAttribute('tabindex', '-1');
    });

    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
    btn.setAttribute('tabindex', '0');

    // Update section indicator
    const label = btn.querySelector('.nav-label')?.textContent || 'SECTION';
    document.getElementById('current-section-indicator').textContent = `⚡ ${label}`;

    // Handle special external links
    const section = btn.dataset.section;
    if (section === 'game') {
        window.open('ultron_avatar_game.html', '_blank');
        return;
    }
    if (section === 'adb') {
        window.open('adb.html', '_blank');
        return;
    }
    if (section === 'assistant') {
        window.open('http://localhost:8002', '_blank');
        return;
    }

    // Internal section switch
    showSection(section);
});
```

**Also remove** inline `onclick` handlers from HTML buttons. Find:
```html
<button ... onclick="window.open('http://localhost:8002', '_blank')">
```

Change to:
```html
<button ...>
```

The JavaScript will handle all clicks now.

---

## PATCH 2: COMMAND EXECUTION WITH ERROR HANDLING

**File**: `gui/ultron_enhanced/web/app.js`

**Find** (around line 238):
```javascript
this.dom.consoleInput.addEventListener('keypress', (event) => {
    if (event.key !== 'Enter') return;
    this.executeCommand(this.dom.consoleInput.value);
});
```

**Replace with**:
```javascript
this.dom.consoleInput.addEventListener('keypress', async (event) => {
    if (event.key !== 'Enter') return;
    event.preventDefault();

    const command = (this.dom.consoleInput.value || '').trim();
    if (!command) return;

    try {
        // Clear input and disable while processing
        this.dom.consoleInput.value = '';
        this.dom.consoleInput.disabled = true;

        // Add user input to console log
        this.addConsoleEntry(`> ${command}`, 'input');

        // Execute with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch('http://localhost:5000/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        this.addConsoleEntry(result.output || 'Command executed', 'success');

    } catch (error) {
        const errorMsg = error.name === 'AbortError'
            ? 'Command timeout (30s)'
            : `Error: ${error.message}`;
        this.addConsoleEntry(errorMsg, 'error');
    } finally {
        this.dom.consoleInput.disabled = false;
        this.dom.consoleInput.focus();
    }
});

// New helper method
addConsoleEntry(text, type = 'log') {
    const log = document.getElementById('console-log');
    if (!log) return;

    const entry = document.createElement('div');
    entry.className = `console-entry console-${type}`;
    entry.textContent = text;

    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;

    // Limit to 500 entries
    const entries = log.querySelectorAll('.console-entry');
    if (entries.length > 500) {
        entries[0].remove();
    }
}
```

---

## PATCH 3: VOICE SYSTEM COMPLETE REWRITE

**File**: `gui/ultron_enhanced/web/app.js`

**Find** entire voice-related code (search for `speechRecognition` and `speechSynthesis`)

**Replace entire section with**:

```javascript
// VOICE MANAGER - Enterprise-grade voice handling
class VoiceManager {
    constructor() {
        this.isListening = false;
        this.isSpeaking = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.audioElement = null;
        this.voiceEnabled = localStorage.getItem('ultron_voice_enabled') === 'true';

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.initRecognition(SpeechRecognition);
        } else {
            console.warn('Speech Recognition API not available');
        }

        this.setupUI();
    }

    initRecognition(SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI('listening');
        };

        this.recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            transcript = transcript.trim();
            if (transcript) {
                this.handleCommand(transcript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Recognition error:', event.error);
            this.updateUI('error');
            this.isListening = false;
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (!this.isSpeaking) {
                this.updateUI('idle');
            }
        };
    }

    setupUI() {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleListening());
        }

        // Auto-cleanup on page exit
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    async startListening() {
        if (this.isListening || !this.voiceEnabled || !this.recognition) return;

        // Critical: Stop all audio before listening
        await this.stopAllAudio();

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start listening:', error);
            this.updateUI('error');
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            try {
                this.recognition.abort();
            } catch (e) {
                // Already stopped
            }
            this.isListening = false;
        }
    }

    async stopAllAudio() {
        return new Promise(resolve => {
            // Stop TTS
            if (this.synthesis) {
                this.synthesis.cancel();
            }

            // Stop audio playback
            if (this.audioElement) {
                try {
                    this.audioElement.pause();
                    this.audioElement.currentTime = 0;
                } catch (e) {}
            }

            // Stop recognition
            if (this.recognition && this.isListening) {
                try {
                    this.recognition.abort();
                } catch (e) {}
            }

            // Critical delay to prevent feedback
            setTimeout(resolve, 1000);
        });
    }

    async speak(text) {
        if (!this.voiceEnabled || !this.synthesis) return;

        try {
            this.isSpeaking = true;
            this.updateUI('speaking');

            // Stop any listening first
            this.stopListening();
            await this.stopAllAudio();

            return new Promise((resolve, reject) => {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.volume = 0.8;  // Slightly lower to prevent feedback

                utterance.onend = () => {
                    this.isSpeaking = false;
                    this.updateUI('idle');
                    // Brief delay before allowing next action
                    setTimeout(resolve, 300);
                };

                utterance.onerror = (event) => {
                    this.isSpeaking = false;
                    console.error('TTS error:', event.error);
                    reject(new Error(`TTS: ${event.error}`));
                };

                this.synthesis.speak(utterance);
            });
        } catch (error) {
            this.isSpeaking = false;
            throw error;
        }
    }

    async handleCommand(transcript) {
        try {
            // Add to console
            const log = document.getElementById('console-log');
            if (log) {
                const entry = document.createElement('div');
                entry.className = 'console-entry console-input';
                entry.textContent = `[VOICE] > ${transcript}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }

            // Send to API
            const response = await fetch('http://localhost:5000/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: transcript })
            });

            if (!response.ok) throw new Error('Command failed');

            const result = await response.json();
            const output = result.output || 'Command executed';

            // Add response to console
            if (log) {
                const entry = document.createElement('div');
                entry.className = 'console-entry console-success';
                entry.textContent = output;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }

            // Speak response if enabled
            if (this.voiceEnabled && output.length < 500) {
                await this.speak(output);
            }

        } catch (error) {
            const log = document.getElementById('console-log');
            if (log) {
                const entry = document.createElement('div');
                entry.className = 'console-entry console-error';
                entry.textContent = `[ERROR] ${error.message}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }
        }
    }

    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    toggleVoice() {
        this.voiceEnabled = !this.voiceEnabled;
        localStorage.setItem('ultron_voice_enabled', this.voiceEnabled);
        this.updateUI('idle');
        return this.voiceEnabled;
    }

    updateUI(state) {
        const btn = document.getElementById('voiceBtn');
        if (!btn) return;

        btn.classList.remove('listening', 'speaking', 'error');

        switch (state) {
            case 'listening':
                btn.classList.add('listening');
                btn.title = 'Voice: Listening... (click to stop)';
                break;
            case 'speaking':
                btn.classList.add('speaking');
                btn.title = 'Voice: Speaking...';
                break;
            case 'error':
                btn.classList.add('error');
                btn.title = 'Voice: Error (click to retry)';
                break;
            default:
                btn.title = this.voiceEnabled
                    ? 'Voice: Ready (click to listen)'
                    : 'Voice: Disabled';
        }
    }

    cleanup() {
        this.stopListening();
        this.stopAllAudio();
    }
}

// Initialize globally
window.voiceManager = new VoiceManager();
```

---

## PATCH 4: SCREENSHOT FUNCTIONALITY

**File**: `gui/ultron_enhanced/web/app.js`

**Find** (around line 226):
```javascript
document.getElementById('screenshotBtn')?.addEventListener('click', () => {
    // ... broken code ...
});
```

**Replace with**:
```javascript
document.getElementById('screenshotBtn')?.addEventListener('click', async () => {
    try {
        const btn = document.getElementById('screenshotBtn');
        btn.disabled = true;
        btn.textContent = '📸 CAPTURING...';

        // Capture the pokedex screen
        const element = document.querySelector('.pokedex-screen') || document.querySelector('.pokedex-body');
        if (!element) throw new Error('Screen element not found');

        const canvas = await html2canvas(element, {
            backgroundColor: '#000',
            scale: 2,
            useCORS: true,
            allowTaint: false,
            logging: false
        });

        // Create download
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        link.download = `ultron-screenshot-${new Date().toISOString().split('T')[0]}-${Date.now()}.png`;
        link.click();

        btn.textContent = '📸 SAVED!';
        setTimeout(() => {
            btn.textContent = '📸 SCREENSHOT';
            btn.disabled = false;
        }, 2000);

    } catch (error) {
        console.error('Screenshot error:', error);
        alert('Screenshot failed: ' + error.message);
    }
});
```

**Required library** - Add to HTML `<head>`:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

---

## PATCH 5: CHAT SYSTEM WITH PERSISTENCE

**File**: `gui/ultron_enhanced/web/app.js`

**Add this new class** (before the app initialization):

```javascript
class ChatManager {
    constructor() {
        this.messages = this.loadChat();
        this.isWaiting = false;
        this.init();
    }

    init() {
        const sendBtn = document.getElementById('send-chat-btn');
        const input = document.getElementById('chat-input');
        const clearBtn = document.getElementById('clear-chat-btn');
        const exportBtn = document.getElementById('export-chat-btn');

        sendBtn?.addEventListener('click', () => this.send());
        input?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.send();
            }
        });
        clearBtn?.addEventListener('click', () => this.clear());
        exportBtn?.addEventListener('click', () => this.export());

        this.render();
    }

    async send() {
        if (this.isWaiting) return;

        const input = document.getElementById('chat-input');
        const msg = (input?.value || '').trim();
        if (!msg) return;

        this.isWaiting = true;

        try {
            input.disabled = true;

            // Add user message
            this.messages.push({
                role: 'user',
                content: msg,
                time: new Date().toISOString()
            });
            this.render();
            input.value = '';

            // Get response
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    history: this.messages.slice(-5)
                })
            });

            if (!response.ok) throw new Error('API error');

            const data = await response.json();
            this.messages.push({
                role: 'assistant',
                content: data.response || 'No response',
                time: new Date().toISOString()
            });

            this.render();
            this.saveChat();

        } catch (error) {
            this.messages.push({
                role: 'system',
                content: `Error: ${error.message}`,
                time: new Date().toISOString()
            });
            this.render();
        } finally {
            this.isWaiting = false;
            input.disabled = false;
            input?.focus();
        }
    }

    render() {
        const cont = document.getElementById('chat-display');
        if (!cont) return;

        cont.innerHTML = this.messages.map(m => `
            <div class="msg msg-${m.role}">
                <strong>${m.role}:</strong> ${escapeHtml(m.content)}
            </div>
        `).join('');

        cont.scrollTop = cont.scrollHeight;
    }

    clear() {
        if (confirm('Clear chat history?')) {
            this.messages = [];
            this.render();
            localStorage.removeItem('ultron_chat');
        }
    }

    export() {
        const text = this.messages
            .map(m => `${m.role}: ${m.content}`)
            .join('\n\n');

        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    saveChat() {
        try {
            localStorage.setItem('ultron_chat', JSON.stringify(this.messages));
        } catch (e) {}
    }

    loadChat() {
        try {
            return JSON.parse(localStorage.getItem('ultron_chat')) || [];
        } catch (e) {
            return [];
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

window.chatManager = new ChatManager();
```

---

## QUICK DEPLOYMENT CHECKLIST

- [ ] Apply Patch 1: Navigation
- [ ] Apply Patch 2: Commands
- [ ] Apply Patch 3: Voice System
- [ ] Apply Patch 4: Screenshots
- [ ] Apply Patch 5: Chat
- [ ] Add html2canvas library to `<head>`
- [ ] Test each function in browser
- [ ] Open DevTools console, check for errors
- [ ] Test offline mode (network disabled)
- [ ] Refresh page, verify state persists

---

## TESTING COMMANDS

```javascript
// Test navigation
document.querySelector('[data-section="console"]').click();

// Test command execution
document.getElementById('commandInput').value = 'help';
document.getElementById('commandInput').dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter'}));

// Test voice
window.voiceManager.startListening();

// Test chat
window.chatManager.send();

// Test screenshot
document.getElementById('screenshotBtn').click();
```

