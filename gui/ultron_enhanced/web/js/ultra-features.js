// Ultra Features - Maximum Functionality Pack
class UltraFeatures {
    constructor() {
        this.init();
    }

    init() {
        this.setupAutoComplete();
        this.setupSmartSearch();
        this.setupVoiceCommands();
        this.setupTaskQueue();
        this.setupClipboardManager();
        this.setupBookmarks();
        this.setupMacros();
        this.setupExport();
    }

    // Auto-complete for commands
    setupAutoComplete() {
        const commands = ['screenshot', 'analyze', 'status', 'help', 'clear', 'refresh', 'save', 'load', 'export'];
        const inputs = document.querySelectorAll('#console-input, #chat-input');
        
        inputs.forEach(input => {
            if (!input) return;
            
            const suggestions = document.createElement('div');
            suggestions.className = 'autocomplete-suggestions';
            input.parentNode.appendChild(suggestions);

            input.addEventListener('input', (e) => {
                const val = e.target.value.toLowerCase();
                suggestions.innerHTML = '';
                
                if (val.length < 2) return;
                
                const matches = commands.filter(cmd => cmd.startsWith(val));
                matches.forEach(cmd => {
                    const div = document.createElement('div');
                    div.textContent = cmd;
                    div.onclick = () => { input.value = cmd; suggestions.innerHTML = ''; };
                    suggestions.appendChild(div);
                });
            });
        });
    }

    // Smart search across all content
    setupSmartSearch() {
        const searchBtn = document.createElement('button');
        searchBtn.className = 'search-btn';
        searchBtn.innerHTML = '🔍';
        searchBtn.title = 'Smart Search (Ctrl+F)';
        document.body.appendChild(searchBtn);

        searchBtn.onclick = () => this.showSearchModal();
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                this.showSearchModal();
            }
        });
    }

    showSearchModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">Smart Search</div>
                <input type="text" id="search-input" placeholder="Search commands, logs, files..." autofocus>
                <div id="search-results"></div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);

        const input = modal.querySelector('#search-input');
        const results = modal.querySelector('#search-results');

        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (query.length < 2) { results.innerHTML = ''; return; }

            const allText = document.body.textContent.toLowerCase();
            const matches = allText.split('\n').filter(line => line.includes(query)).slice(0, 10);
            
            results.innerHTML = matches.map(m => `<div class="search-result">${m.substring(0, 100)}</div>`).join('');
        });

        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    // Voice command recognition
    setupVoiceCommands() {
        if (!('webkitSpeechRecognition' in window)) return;

        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'voice-command-btn';
        voiceBtn.innerHTML = '🎙️';
        voiceBtn.title = 'Voice Commands (Click to speak)';
        document.body.appendChild(voiceBtn);

        voiceBtn.onclick = () => {
            recognition.start();
            voiceBtn.classList.add('listening');
        };

        recognition.onresult = (e) => {
            const command = e.results[0][0].transcript.toLowerCase();
            this.executeVoiceCommand(command);
            voiceBtn.classList.remove('listening');
        };

        recognition.onerror = () => voiceBtn.classList.remove('listening');
    }

    executeVoiceCommand(command) {
        const actions = {
            'screenshot': () => window.advancedFeatures?.takeScreenshot(),
            'analyze': () => window.advancedFeatures?.analyzeScreen(),
            'help': () => window.advancedFeatures?.showHelp(),
            'clear': () => window.advancedFeatures?.clearConsole(),
            'refresh': () => window.advancedFeatures?.refreshStatus()
        };

        for (const [key, action] of Object.entries(actions)) {
            if (command.includes(key)) {
                action();
                this.notify(`Executed: ${key}`, 'success');
                return;
            }
        }
        this.notify('Command not recognized', 'warning');
    }

    // Task queue manager
    setupTaskQueue() {
        this.tasks = [];
        
        const queueBtn = document.createElement('button');
        queueBtn.className = 'queue-btn';
        queueBtn.innerHTML = '📋';
        queueBtn.title = 'Task Queue';
        document.body.appendChild(queueBtn);

        queueBtn.onclick = () => this.showTaskQueue();
    }

    showTaskQueue() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">Task Queue</div>
                <div class="task-input">
                    <input type="text" id="new-task" placeholder="Add new task...">
                    <button id="add-task">Add</button>
                </div>
                <div id="task-list">${this.renderTasks()}</div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector('#add-task').onclick = () => {
            const input = modal.querySelector('#new-task');
            if (input.value.trim()) {
                this.tasks.push({ text: input.value, done: false, id: Date.now() });
                input.value = '';
                modal.querySelector('#task-list').innerHTML = this.renderTasks();
                this.saveTasks();
            }
        };

        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    renderTasks() {
        return this.tasks.map(t => `
            <div class="task-item ${t.done ? 'done' : ''}">
                <input type="checkbox" ${t.done ? 'checked' : ''} onchange="window.ultraFeatures.toggleTask(${t.id})">
                <span>${t.text}</span>
                <button onclick="window.ultraFeatures.deleteTask(${t.id})">🗑️</button>
            </div>
        `).join('');
    }

    toggleTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) { task.done = !task.done; this.saveTasks(); }
    }

    deleteTask(id) {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.saveTasks();
        document.querySelector('#task-list').innerHTML = this.renderTasks();
    }

    saveTasks() {
        localStorage.setItem('ultron_tasks', JSON.stringify(this.tasks));
    }

    loadTasks() {
        const saved = localStorage.getItem('ultron_tasks');
        if (saved) this.tasks = JSON.parse(saved);
    }

    // Clipboard manager
    setupClipboardManager() {
        this.clipboard = [];
        
        document.addEventListener('copy', (e) => {
            const text = window.getSelection().toString();
            if (text) {
                this.clipboard.push({ text, time: Date.now() });
                if (this.clipboard.length > 20) this.clipboard.shift();
            }
        });

        const clipBtn = document.createElement('button');
        clipBtn.className = 'clipboard-btn';
        clipBtn.innerHTML = '📎';
        clipBtn.title = 'Clipboard History';
        document.body.appendChild(clipBtn);

        clipBtn.onclick = () => this.showClipboard();
    }

    showClipboard() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">Clipboard History</div>
                <div class="clipboard-list">
                    ${this.clipboard.map((c, i) => `
                        <div class="clip-item" onclick="navigator.clipboard.writeText('${c.text.replace(/'/g, "\\'")}')">
                            ${c.text.substring(0, 100)}
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    // Bookmarks
    setupBookmarks() {
        this.bookmarks = JSON.parse(localStorage.getItem('ultron_bookmarks') || '[]');
        
        const bookmarkBtn = document.createElement('button');
        bookmarkBtn.className = 'bookmark-btn';
        bookmarkBtn.innerHTML = '⭐';
        bookmarkBtn.title = 'Bookmarks (Ctrl+D)';
        document.body.appendChild(bookmarkBtn);

        bookmarkBtn.onclick = () => this.showBookmarks();

        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                this.addBookmark();
            }
        });
    }

    addBookmark() {
        const section = document.querySelector('.section-content.active')?.id || 'unknown';
        this.bookmarks.push({ section, time: Date.now() });
        localStorage.setItem('ultron_bookmarks', JSON.stringify(this.bookmarks));
        this.notify('Bookmark added', 'success');
    }

    showBookmarks() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">Bookmarks</div>
                <div class="bookmark-list">
                    ${this.bookmarks.map((b, i) => `
                        <div class="bookmark-item" onclick="window.ultraFeatures.goToBookmark('${b.section}')">
                            ${b.section} - ${new Date(b.time).toLocaleString()}
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    goToBookmark(section) {
        const btn = document.querySelector(`[data-section="${section}"]`);
        if (btn) btn.click();
        document.querySelectorAll('.modal').forEach(m => m.remove());
    }

    // Macro recorder
    setupMacros() {
        this.recording = false;
        this.macros = [];
        this.currentMacro = [];

        const macroBtn = document.createElement('button');
        macroBtn.className = 'macro-btn';
        macroBtn.innerHTML = '⏺️';
        macroBtn.title = 'Record Macro';
        document.body.appendChild(macroBtn);

        macroBtn.onclick = () => this.toggleRecording(macroBtn);
    }

    toggleRecording(btn) {
        this.recording = !this.recording;
        btn.innerHTML = this.recording ? '⏹️' : '⏺️';
        btn.classList.toggle('recording');

        if (!this.recording && this.currentMacro.length > 0) {
            this.macros.push({ actions: [...this.currentMacro], time: Date.now() });
            this.currentMacro = [];
            this.notify('Macro saved', 'success');
        }
    }

    // Export data
    setupExport() {
        const exportBtn = document.createElement('button');
        exportBtn.className = 'export-btn';
        exportBtn.innerHTML = '💾';
        exportBtn.title = 'Export Data';
        document.body.appendChild(exportBtn);

        exportBtn.onclick = () => this.exportData();
    }

    exportData() {
        const data = {
            tasks: this.tasks,
            bookmarks: this.bookmarks,
            history: window.advancedFeatures?.commandHistory || [],
            timestamp: Date.now()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ultron-export-${Date.now()}.json`;
        a.click();
        this.notify('Data exported', 'success');
    }

    notify(msg, type) {
        if (window.NotificationManager) {
            window.NotificationManager.show(msg, type);
        }
    }
}

// Auto-init
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.ultraFeatures = new UltraFeatures();
        window.ultraFeatures.loadTasks();
    });
} else {
    window.ultraFeatures = new UltraFeatures();
    window.ultraFeatures.loadTasks();
}
