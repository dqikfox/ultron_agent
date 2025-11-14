// Advanced Features Module for ULTRON GUI
// Adds: Drag-drop, Command history, Quick actions, Theme switcher, Performance monitor

class AdvancedFeatures {
    constructor() {
        this.commandHistory = [];
        this.historyIndex = -1;
        this.quickActions = [];
        this.init();
    }

    init() {
        this.setupDragDrop();
        this.setupCommandHistory();
        this.setupQuickActions();
        this.setupThemeSwitcher();
        this.setupPerformanceMonitor();
        this.setupKeyboardShortcuts();
        this.setupContextMenu();
    }

    // Drag & Drop File Upload
    setupDragDrop() {
        const dropZones = document.querySelectorAll('.section-content');
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', async (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
                
                const files = Array.from(e.dataTransfer.files);
                await this.handleFileUpload(files);
            });
        });
    }

    async handleFileUpload(files) {
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                this.notify(`Uploaded: ${file.name}`, 'success');
            } catch (error) {
                this.notify(`Failed: ${file.name}`, 'error');
            }
        }
    }

    // Command History with Arrow Keys
    setupCommandHistory() {
        const consoleInput = document.getElementById('console-input');
        const chatInput = document.getElementById('chat-input');

        [consoleInput, chatInput].forEach(input => {
            if (!input) return;

            input.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.navigateHistory('up', input);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.navigateHistory('down', input);
                } else if (e.key === 'Enter' && !e.shiftKey) {
                    const cmd = input.value.trim();
                    if (cmd) {
                        this.addToHistory(cmd);
                    }
                }
            });
        });
    }

    addToHistory(command) {
        this.commandHistory.push(command);
        if (this.commandHistory.length > 100) {
            this.commandHistory.shift();
        }
        this.historyIndex = this.commandHistory.length;
        this.saveHistory();
    }

    navigateHistory(direction, input) {
        if (this.commandHistory.length === 0) return;

        if (direction === 'up') {
            this.historyIndex = Math.max(0, this.historyIndex - 1);
        } else {
            this.historyIndex = Math.min(this.commandHistory.length, this.historyIndex + 1);
        }

        input.value = this.commandHistory[this.historyIndex] || '';
    }

    saveHistory() {
        localStorage.setItem('ultron_command_history', JSON.stringify(this.commandHistory));
    }

    loadHistory() {
        const saved = localStorage.getItem('ultron_command_history');
        if (saved) {
            this.commandHistory = JSON.parse(saved);
            this.historyIndex = this.commandHistory.length;
        }
    }

    // Quick Actions Bar
    setupQuickActions() {
        this.quickActions = [
            { icon: '📸', label: 'Screenshot', action: () => this.takeScreenshot() },
            { icon: '🔍', label: 'Analyze', action: () => this.analyzeScreen() },
            { icon: '💾', label: 'Save', action: () => this.saveSession() },
            { icon: '📋', label: 'Copy', action: () => this.copyOutput() },
            { icon: '🔄', label: 'Refresh', action: () => this.refreshStatus() },
            { icon: '🎤', label: 'Voice', action: () => this.toggleVoice() }
        ];

        this.createQuickActionsBar();
    }

    createQuickActionsBar() {
        const bar = document.createElement('div');
        bar.className = 'quick-actions-bar';
        bar.innerHTML = this.quickActions.map(action => `
            <button class="quick-action-btn" title="${action.label}">
                ${action.icon}
            </button>
        `).join('');

        document.body.appendChild(bar);

        bar.querySelectorAll('.quick-action-btn').forEach((btn, i) => {
            btn.addEventListener('click', this.quickActions[i].action);
        });
    }

    // Theme Switcher
    setupThemeSwitcher() {
        const themes = ['ultron-steampunk', 'pokedex-red', 'pokedex-blue', 'high-contrast'];
        let currentTheme = localStorage.getItem('ultron_theme') || 'ultron-steampunk';

        document.body.className = currentTheme;

        const switcher = document.createElement('div');
        switcher.className = 'theme-switcher';
        switcher.innerHTML = `
            <button class="theme-btn" title="Change Theme">🎨</button>
            <div class="theme-menu hidden">
                ${themes.map(t => `<div class="theme-option" data-theme="${t}">${t}</div>`).join('')}
            </div>
        `;

        document.body.appendChild(switcher);

        const btn = switcher.querySelector('.theme-btn');
        const menu = switcher.querySelector('.theme-menu');

        btn.addEventListener('click', () => menu.classList.toggle('hidden'));

        menu.querySelectorAll('.theme-option').forEach(opt => {
            opt.addEventListener('click', () => {
                const theme = opt.dataset.theme;
                document.body.className = theme;
                localStorage.setItem('ultron_theme', theme);
                menu.classList.add('hidden');
                this.notify(`Theme: ${theme}`, 'info');
            });
        });
    }

    // Performance Monitor
    setupPerformanceMonitor() {
        setInterval(() => {
            const perf = performance.memory;
            if (perf) {
                const used = (perf.usedJSHeapSize / 1048576).toFixed(1);
                const total = (perf.totalJSHeapSize / 1048576).toFixed(1);
                
                const monitor = document.getElementById('perf-monitor');
                if (monitor) {
                    monitor.textContent = `Memory: ${used}/${total} MB`;
                }
            }
        }, 5000);
    }

    // Enhanced Keyboard Shortcuts
    setupKeyboardShortcuts() {
        const shortcuts = {
            'Ctrl+S': () => this.takeScreenshot(),
            'Ctrl+A': () => this.analyzeScreen(),
            'Ctrl+H': () => this.showHistory(),
            'Ctrl+K': () => this.clearConsole(),
            'Ctrl+/': () => this.showHelp(),
            'Escape': () => this.closeModals(),
            'F1': () => this.showHelp(),
            'F5': () => this.refreshStatus()
        };

        document.addEventListener('keydown', (e) => {
            const key = `${e.ctrlKey ? 'Ctrl+' : ''}${e.key}`;
            if (shortcuts[key]) {
                e.preventDefault();
                shortcuts[key]();
            }
        });
    }

    // Context Menu
    setupContextMenu() {
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu(e.clientX, e.clientY);
        });
    }

    showContextMenu(x, y) {
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.left = `${x}px`;
        menu.style.top = `${y}px`;
        menu.innerHTML = `
            <div class="context-item" data-action="copy">📋 Copy</div>
            <div class="context-item" data-action="paste">📄 Paste</div>
            <div class="context-item" data-action="screenshot">📸 Screenshot</div>
            <div class="context-item" data-action="analyze">🔍 Analyze</div>
        `;

        document.body.appendChild(menu);

        menu.querySelectorAll('.context-item').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                this[action]?.();
                menu.remove();
            });
        });

        setTimeout(() => {
            document.addEventListener('click', () => menu.remove(), { once: true });
        }, 100);
    }

    // Action Methods
    async takeScreenshot() {
        try {
            const response = await fetch('/api/screenshot');
            const result = await response.json();
            this.notify('Screenshot captured', 'success');
        } catch (error) {
            this.notify('Screenshot failed', 'error');
        }
    }

    async analyzeScreen() {
        try {
            const response = await fetch('/api/analyze');
            const result = await response.json();
            this.notify('Analysis complete', 'success');
        } catch (error) {
            this.notify('Analysis failed', 'error');
        }
    }

    saveSession() {
        const session = {
            history: this.commandHistory,
            theme: document.body.className,
            timestamp: Date.now()
        };
        localStorage.setItem('ultron_session', JSON.stringify(session));
        this.notify('Session saved', 'success');
    }

    copyOutput() {
        const output = document.getElementById('console-output')?.textContent || '';
        navigator.clipboard.writeText(output);
        this.notify('Copied to clipboard', 'success');
    }

    refreshStatus() {
        if (window.ultronInterface) {
            window.ultronInterface.loadSystemInfo();
            this.notify('Status refreshed', 'info');
        }
    }

    toggleVoice() {
        if (window.ultronInterface) {
            window.ultronInterface.toggleVoice();
        }
    }

    showHistory() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">Command History</div>
                <div class="history-list">
                    ${this.commandHistory.map((cmd, i) => `
                        <div class="history-item" data-index="${i}">${cmd}</div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                const cmd = item.textContent;
                const input = document.getElementById('console-input');
                if (input) input.value = cmd;
                modal.remove();
            });
        });

        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    }

    clearConsole() {
        const output = document.getElementById('console-output');
        if (output) {
            output.innerHTML = '<div class="message system-message"><span class="timestamp">[00:00:00]</span><span class="message-content">Console cleared</span></div>';
            this.notify('Console cleared', 'info');
        }
    }

    showHelp() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content help-modal">
                <div class="modal-title">Keyboard Shortcuts</div>
                <div class="shortcuts-grid">
                    <div class="shortcut"><kbd>Ctrl+S</kbd> Screenshot</div>
                    <div class="shortcut"><kbd>Ctrl+A</kbd> Analyze</div>
                    <div class="shortcut"><kbd>Ctrl+H</kbd> History</div>
                    <div class="shortcut"><kbd>Ctrl+K</kbd> Clear</div>
                    <div class="shortcut"><kbd>F1</kbd> Help</div>
                    <div class="shortcut"><kbd>F5</kbd> Refresh</div>
                    <div class="shortcut"><kbd>↑/↓</kbd> Navigate History</div>
                    <div class="shortcut"><kbd>Esc</kbd> Close Modals</div>
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;

        document.body.appendChild(modal);
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(m => m.remove());
    }

    notify(message, type = 'info') {
        if (window.NotificationManager) {
            window.NotificationManager.show(message, type);
        } else {
            console.log(`[${type}] ${message}`);
        }
    }
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.advancedFeatures = new AdvancedFeatures();
    });
} else {
    window.advancedFeatures = new AdvancedFeatures();
}
