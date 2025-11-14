# ULTRON GUI FIXES - STEP-BY-STEP DEPLOYMENT

This guide provides exact code replacements with line numbers for applying all 5 critical GUI fixes.

---

## PREREQUISITE: Add HTML2Canvas Library

**File**: `gui/ultron_enhanced/web/index.html`

**Find**: The closing `</head>` tag (around line 50)

**Add this line BEFORE `</head>`**:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

---

## FIX 1: Remove Inline onclick Handlers from HTML

**File**: `gui/ultron_enhanced/web/index.html`

**Find Line 164**:
```html
<button class="nav-button" data-section="assistant" role="tab" aria-selected="false" aria-controls="assistant-section" tabindex="-1" onclick="window.open('http://localhost:8002', '_blank')">
```

**Replace with**:
```html
<button class="nav-button" data-section="assistant" role="tab" aria-selected="false" aria-controls="assistant-section" tabindex="-1">
```

**What changed**: Removed `onclick="window.open('http://localhost:8002', '_blank')"` - JavaScript will handle all nav clicks now.

---

## FIX 2: Replace Navigation Event Listener Setup

**File**: `gui/ultron_enhanced/web/app.js`

**Find Lines 132-150** (the setupEventListeners navigation section):

```javascript
        // Navigation tab keyboard support
        document.querySelectorAll('.nav-button').forEach(btn => {
            btn.addEventListener('click', (event) => {
                const section = event.currentTarget.dataset.section;
                this.switchSection(section);
                this.playSound('button');
            });

            // Keyboard navigation for tabs
            btn.addEventListener('keydown', (event) => {
                const navButtons = Array.from(document.querySelectorAll('.nav-button'));
                const currentIndex = navButtons.indexOf(event.currentTarget);

                switch (event.key) {
                    case 'ArrowLeft':
                        event.preventDefault();
                        const prevIndex = currentIndex > 0 ? currentIndex - 1 : navButtons.length - 1;
                        navButtons[prevIndex].focus();
                        break;
                    case 'ArrowRight':
                        event.preventDefault();
                        const nextIndex = currentIndex < navButtons.length - 1 ? currentIndex + 1 : 0;
                        navButtons[nextIndex].focus();
                        break;
                    case 'Enter':
                    case ' ':
                        event.preventDefault();
                        const section = event.currentTarget.dataset.section;
                        this.switchSection(section);
                        this.playSound('button');
                        break;
                }
            });
        });
```

**Replace with**:

```javascript
        // Event delegation - single listener for all nav buttons
        const navGrid = document.querySelector('.nav-buttons-grid');
        if (navGrid) {
            navGrid.addEventListener('click', (e) => {
                const btn = e.target.closest('.nav-button');
                if (!btn) return;

                e.stopPropagation();
                this.handleNavClick(btn);
            });

            navGrid.addEventListener('keydown', (e) => {
                const btn = e.target.closest('.nav-button');
                if (!btn) return;

                const navButtons = Array.from(navGrid.querySelectorAll('.nav-button'));
                const currentIndex = navButtons.indexOf(btn);

                let targetBtn = null;
                switch (e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        targetBtn = navButtons[currentIndex > 0 ? currentIndex - 1 : navButtons.length - 1];
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        targetBtn = navButtons[currentIndex < navButtons.length - 1 ? currentIndex + 1 : 0];
                        break;
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        this.handleNavClick(btn);
                        return;
                }

                if (targetBtn) {
                    targetBtn.focus();
                }
            });
        }
```

**Add this new method** somewhere in the class (around line 400):

```javascript
    handleNavClick(btn) {
        const section = btn.dataset.section;

        // Update active state
        document.querySelectorAll('.nav-button').forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
            b.setAttribute('tabindex', '-1');
        });

        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        btn.setAttribute('tabindex', '0');

        this.playSound('button');

        // Handle special external links
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
        this.switchSection(section);
    }
```

---

## FIX 3: Update Console Command Handler

**File**: `gui/ultron_enhanced/web/app.js`

**Find Lines 238-244**:

```javascript
        if (this.dom.consoleInput) {
            this.dom.consoleInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    this.handleConsoleCommand(event.target.value);
                    event.target.value = '';
                }
            });
        }
```

**Replace with**:

```javascript
        if (this.dom.consoleInput) {
            this.dom.consoleInput.addEventListener('keypress', async (event) => {
                if (event.key !== 'Enter') return;
                event.preventDefault();

                const command = (event.target.value || '').trim();
                if (!command) return;

                try {
                    event.target.disabled = true;
                    event.target.value = '';

                    // Add user input to console
                    this.addConsoleLog(`> ${command}`, 'input');

                    // Execute with timeout
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 30000);

                    const response = await fetch(`${this.API_BASE_URL}/api/command`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command }),
                        signal: controller.signal
                    });

                    clearTimeout(timeoutId);

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    const result = await response.json();
                    this.addConsoleLog(result.output || 'Command executed', 'success');

                } catch (error) {
                    const msg = error.name === 'AbortError' ? 'Timeout (30s)' : error.message;
                    this.addConsoleLog(`⚠️ ${msg}`, 'error');
                } finally {
                    event.target.disabled = false;
                    event.target.focus();
                }
            });
        }
```

**Add this helper method** around line 450:

```javascript
    addConsoleLog(text, type = 'log') {
        const log = this.dom.consoleOutput;
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

## FIX 4: Add VoiceManager Class

**File**: `gui/ultron_enhanced/web/app.js`

**Add this BEFORE the UltronPokedexInterface class** (at the very top, after comments):

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
        }

        window.addEventListener('beforeunload', () => this.cleanup());
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
            if (transcript.trim()) {
                this.onResult(transcript.trim());
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

    async startListening() {
        if (this.isListening || !this.voiceEnabled || !this.recognition) return;
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
            } catch (e) {}
            this.isListening = false;
        }
    }

    async stopAllAudio() {
        return new Promise(resolve => {
            if (this.synthesis) {
                this.synthesis.cancel();
            }
            if (this.audioElement) {
                try {
                    this.audioElement.pause();
                    this.audioElement.currentTime = 0;
                } catch (e) {}
            }
            if (this.recognition && this.isListening) {
                try {
                    this.recognition.abort();
                } catch (e) {}
            }
            setTimeout(resolve, 1000);
        });
    }

    async speak(text) {
        if (!this.voiceEnabled || !this.synthesis) return;

        try {
            this.isSpeaking = true;
            this.updateUI('speaking');
            this.stopListening();
            await this.stopAllAudio();

            return new Promise((resolve, reject) => {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.volume = 0.8;

                utterance.onend = () => {
                    this.isSpeaking = false;
                    this.updateUI('idle');
                    setTimeout(resolve, 300);
                };

                utterance.onerror = (event) => {
                    this.isSpeaking = false;
                    reject(new Error(`TTS: ${event.error}`));
                };

                this.synthesis.speak(utterance);
            });
        } catch (error) {
            this.isSpeaking = false;
            throw error;
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
                btn.title = 'Voice: Listening...';
                break;
            case 'speaking':
                btn.classList.add('speaking');
                btn.title = 'Voice: Speaking...';
                break;
            case 'error':
                btn.classList.add('error');
                btn.title = 'Voice: Error';
                break;
            default:
                btn.title = this.voiceEnabled ? 'Voice: Ready' : 'Voice: Disabled';
        }
    }

    cleanup() {
        this.stopListening();
        this.stopAllAudio();
    }

    // Override this in init
    onResult(transcript) {
        console.log('Voice recognized:', transcript);
    }
}
```

**Then in the UltronPokedexInterface init()**, add:

```javascript
        // Initialize voice manager
        this.voiceManager = new VoiceManager();
        this.voiceManager.onResult = (transcript) => {
            this.handleVoiceCommand(transcript);
        };
```

---

## FIX 5: Add ChatManager Class

**File**: `gui/ultron_enhanced/web/app.js`

**Add this class BEFORE the UltronPokedexInterface class**:

```javascript
class ChatManager {
    constructor() {
        this.messages = this.loadChat();
        this.isWaiting = false;
        this.apiBase = 'http://localhost:5000';
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
            const response = await fetch(`${this.apiBase}/api/chat`, {
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
                content: `⚠️ Error: ${error.message}`,
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
        const cont = document.getElementById('chat-messages');
        if (!cont) return;

        cont.innerHTML = this.messages.map(m => `
            <div class="chat-message msg-${m.role}">
                <strong>${m.role}:</strong> ${this.escapeHtml(m.content)}
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
        a.download = `ultron-chat-${new Date().toISOString().split('T')[0]}.txt`;
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
```

**Then in the UltronPokedexInterface init()**, add:

```javascript
        // Initialize chat manager
        this.chatManager = new ChatManager();
```

---

## FIX 6: Update Screenshot Function

**File**: `gui/ultron_enhanced/web/app.js`

**Find Line 226** where `captureEnhancedScreenshot()` is defined, or add this if it doesn't exist:

```javascript
    async captureEnhancedScreenshot() {
        try {
            const btn = document.getElementById('screenshotBtn');
            if (btn) {
                btn.disabled = true;
                btn.textContent = '📸 CAPTURING...';
            }

            // Capture the pokedex screen
            const element = document.querySelector('.pokedex-screen') ||
                          document.querySelector('.pokedex-body') ||
                          document.querySelector('#main-interface');

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
            link.download = `ultron-${new Date().toISOString().split('T')[0]}-${Date.now()}.png`;
            link.click();

            if (btn) {
                btn.textContent = '📸 SAVED!';
                setTimeout(() => {
                    btn.textContent = '📸 SCREENSHOT';
                    btn.disabled = false;
                }, 2000);
            }

        } catch (error) {
            console.error('Screenshot error:', error);
            alert('Screenshot failed: ' + error.message);
        }
    }
```

---

## DEPLOYMENT ORDER

Apply fixes in this order:

1. ✅ Add html2canvas library to `<head>`
2. ✅ Remove inline onclick from HTML (line 164)
3. ✅ Add VoiceManager class
4. ✅ Add ChatManager class
5. ✅ Replace navigation event listeners (lines 132-150)
6. ✅ Update console command handler (lines 238-244)
7. ✅ Update screenshot function
8. ✅ Initialize managers in init()

---

## TESTING CHECKLIST

After applying all fixes:

```javascript
// Open browser DevTools console and test:

// 1. Navigation
document.querySelector('[data-section="console"]').click();

// 2. Console Commands
document.getElementById('console-input').value = 'help';
document.getElementById('console-input').dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter'}));

// 3. Voice
window.voiceManager.toggleListening();

// 4. Chat
window.chatManager.send();

// 5. Screenshot
document.getElementById('screenshotBtn')?.click();
```

---

## COMMON ISSUES

### Issue: "html2canvas is not defined"
**Solution**: Make sure the `<script>` tag was added to `<head>` before closing tag

### Issue: "Cannot read property 'addEventListener' of null"
**Solution**: Make sure you're not calling manager initialization before DOM is ready. It should be in `init()` method.

### Issue: Voice not working
**Solution**: Check browser console for `SpeechRecognition` availability. Not all browsers support it.

### Issue: Chat not sending
**Solution**: Verify API endpoint is running on `http://localhost:5000` and has `/api/chat` route

