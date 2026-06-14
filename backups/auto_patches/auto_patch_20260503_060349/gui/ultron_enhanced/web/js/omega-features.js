// OMEGA Features - Final Evolution
class OmegaFeatures {
    constructor() {
        this.init();
    }

    init() {
        this.setupQuickNotes();
        this.setupScreenRecorder();
        this.setupCodeSnippets();
        this.setupFavorites();
        this.setupGlobalSearch();
        this.setupAutoSave();
        this.setupTutorial();
        this.setupDarkMode();
        this.setupFullscreen();
        this.setupPrintMode();
    }

    // Quick notes with markdown
    setupQuickNotes() {
        const btn = document.createElement('button');
        btn.className = 'notes-btn';
        btn.innerHTML = '📝';
        btn.title = 'Quick Notes (Ctrl+N)';
        document.body.appendChild(btn);

        btn.onclick = () => this.showNotes();
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                this.showNotes();
            }
        });
    }

    showNotes() {
        const notes = localStorage.getItem('ultron_notes') || '';
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">📝 Quick Notes</div>
                <textarea id="notes-area" placeholder="Write your notes here...">${notes}</textarea>
                <div class="notes-actions">
                    <button onclick="window.omegaFeatures.saveNotes()">💾 Save</button>
                    <button onclick="window.omegaFeatures.exportNotes()">📤 Export</button>
                    <button onclick="window.omegaFeatures.clearNotes()">🗑️ Clear</button>
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    saveNotes() {
        const notes = document.getElementById('notes-area').value;
        localStorage.setItem('ultron_notes', notes);
        this.notify('Notes saved', 'success');
    }

    exportNotes() {
        const notes = document.getElementById('notes-area').value;
        const blob = new Blob([notes], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `notes-${Date.now()}.txt`;
        a.click();
        this.notify('Notes exported', 'success');
    }

    clearNotes() {
        if (confirm('Clear all notes?')) {
            document.getElementById('notes-area').value = '';
            localStorage.removeItem('ultron_notes');
            this.notify('Notes cleared', 'info');
        }
    }

    // Screen recorder
    setupScreenRecorder() {
        const btn = document.createElement('button');
        btn.className = 'recorder-btn';
        btn.innerHTML = '🎥';
        btn.title = 'Screen Recorder';
        document.body.appendChild(btn);

        btn.onclick = () => this.toggleRecording(btn);
    }

    async toggleRecording(btn) {
        if (!this.recording) {
            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.chunks = [];

                this.mediaRecorder.ondataavailable = (e) => this.chunks.push(e.data);
                this.mediaRecorder.onstop = () => {
                    const blob = new Blob(this.chunks, { type: 'video/webm' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `recording-${Date.now()}.webm`;
                    a.click();
                    this.notify('Recording saved', 'success');
                };

                this.mediaRecorder.start();
                this.recording = true;
                btn.innerHTML = '⏹️';
                btn.classList.add('recording');
                this.notify('Recording started', 'info');
            } catch {
                this.notify('Recording failed', 'error');
            }
        } else {
            this.mediaRecorder.stop();
            this.recording = false;
            btn.innerHTML = '🎥';
            btn.classList.remove('recording');
        }
    }

    // Code snippets manager
    setupCodeSnippets() {
        this.snippets = JSON.parse(localStorage.getItem('ultron_snippets') || '[]');
        
        const btn = document.createElement('button');
        btn.className = 'snippets-btn';
        btn.innerHTML = '💻';
        btn.title = 'Code Snippets';
        document.body.appendChild(btn);

        btn.onclick = () => this.showSnippets();
    }

    showSnippets() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">💻 Code Snippets</div>
                <div class="snippet-input">
                    <input type="text" id="snippet-name" placeholder="Snippet name...">
                    <textarea id="snippet-code" placeholder="Code..."></textarea>
                    <button onclick="window.omegaFeatures.addSnippet()">Add</button>
                </div>
                <div class="snippet-list" id="snippet-list">
                    ${this.snippets.map((s, i) => `
                        <div class="snippet-item">
                            <strong>${s.name}</strong>
                            <pre>${s.code}</pre>
                            <button onclick="navigator.clipboard.writeText('${s.code.replace(/'/g, "\\'")}')">Copy</button>
                            <button onclick="window.omegaFeatures.deleteSnippet(${i})">Delete</button>
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    addSnippet() {
        const name = document.getElementById('snippet-name').value;
        const code = document.getElementById('snippet-code').value;
        if (name && code) {
            this.snippets.push({ name, code, created: Date.now() });
            localStorage.setItem('ultron_snippets', JSON.stringify(this.snippets));
            this.showSnippets();
        }
    }

    deleteSnippet(i) {
        this.snippets.splice(i, 1);
        localStorage.setItem('ultron_snippets', JSON.stringify(this.snippets));
        this.showSnippets();
    }

    // Favorites system
    setupFavorites() {
        this.favorites = JSON.parse(localStorage.getItem('ultron_favorites') || '[]');
        
        const btn = document.createElement('button');
        btn.className = 'favorites-btn';
        btn.innerHTML = '⭐';
        btn.title = 'Favorites';
        document.body.appendChild(btn);

        btn.onclick = () => this.showFavorites();
    }

    showFavorites() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">⭐ Favorites</div>
                <div class="favorites-list">
                    ${this.favorites.map((f, i) => `
                        <div class="favorite-item" onclick="window.omegaFeatures.goToFavorite('${f.section}')">
                            ${f.name} - ${f.section}
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    goToFavorite(section) {
        const btn = document.querySelector(`[data-section="${section}"]`);
        if (btn) btn.click();
        document.querySelectorAll('.modal').forEach(m => m.remove());
    }

    // Global search
    setupGlobalSearch() {
        const searchBox = document.createElement('div');
        searchBox.className = 'global-search';
        searchBox.innerHTML = `
            <input type="text" id="global-search-input" placeholder="🔍 Search everything...">
            <div id="global-search-results"></div>
        `;
        document.body.appendChild(searchBox);

        const input = document.getElementById('global-search-input');
        const results = document.getElementById('global-search-results');

        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (query.length < 2) {
                results.innerHTML = '';
                return;
            }

            const allText = document.body.textContent.toLowerCase();
            const matches = allText.split('\n').filter(line => line.includes(query)).slice(0, 5);
            
            results.innerHTML = matches.map(m => `<div class="search-result-item">${m.substring(0, 80)}</div>`).join('');
        });
    }

    // Auto-save system
    setupAutoSave() {
        setInterval(() => {
            const state = {
                theme: document.body.className,
                section: document.querySelector('.section-content.active')?.id,
                timestamp: Date.now()
            };
            localStorage.setItem('ultron_autosave', JSON.stringify(state));
        }, 30000); // Every 30 seconds
    }

    // Interactive tutorial
    setupTutorial() {
        if (!localStorage.getItem('ultron_tutorial_done')) {
            setTimeout(() => this.showTutorial(), 2000);
        }

        const btn = document.createElement('button');
        btn.className = 'tutorial-btn';
        btn.innerHTML = '🎓';
        btn.title = 'Tutorial';
        document.body.appendChild(btn);

        btn.onclick = () => this.showTutorial();
    }

    showTutorial() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">🎓 Welcome to ULTRON NEXUS</div>
                <div class="tutorial-content">
                    <h3>Quick Start Guide</h3>
                    <ul>
                        <li><kbd>Ctrl+Space</kbd> - AI Assistant</li>
                        <li><kbd>Ctrl+Shift+P</kbd> - Command Palette</li>
                        <li><kbd>Ctrl+F</kbd> - Smart Search</li>
                        <li><kbd>Ctrl+S</kbd> - Screenshot</li>
                        <li><kbd>F1</kbd> - Help</li>
                    </ul>
                    <p>Click any floating button to explore features!</p>
                </div>
                <button onclick="localStorage.setItem('ultron_tutorial_done', 'true'); this.closest('.modal').remove()">Got it!</button>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Dark mode toggle
    setupDarkMode() {
        const btn = document.createElement('button');
        btn.className = 'darkmode-btn';
        btn.innerHTML = '🌙';
        btn.title = 'Toggle Dark Mode';
        document.body.appendChild(btn);

        btn.onclick = () => {
            document.body.classList.toggle('dark-mode');
            btn.innerHTML = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
            this.notify('Theme toggled', 'info');
        };
    }

    // Fullscreen mode
    setupFullscreen() {
        const btn = document.createElement('button');
        btn.className = 'fullscreen-btn';
        btn.innerHTML = '⛶';
        btn.title = 'Fullscreen (F11)';
        document.body.appendChild(btn);

        btn.onclick = () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
                btn.innerHTML = '⛶';
            } else {
                document.exitFullscreen();
                btn.innerHTML = '⛶';
            }
        };
    }

    // Print mode
    setupPrintMode() {
        const btn = document.createElement('button');
        btn.className = 'print-btn';
        btn.innerHTML = '🖨️';
        btn.title = 'Print (Ctrl+P)';
        document.body.appendChild(btn);

        btn.onclick = () => window.print();
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
        window.omegaFeatures = new OmegaFeatures();
    });
} else {
    window.omegaFeatures = new OmegaFeatures();
}
