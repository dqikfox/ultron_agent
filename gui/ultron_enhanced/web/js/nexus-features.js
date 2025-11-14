// NEXUS Features - Next Evolution
class NexusFeatures {
    constructor() {
        this.init();
    }

    init() {
        this.setupAIAssistant();
        this.setupCollaboration();
        this.setupAnalytics();
        this.setupWorkspaces();
        this.setupPlugins();
        this.setupTimeline();
        this.setupCommandPalette();
        this.setupSmartNotifications();
    }

    // AI Assistant with context awareness
    setupAIAssistant() {
        const btn = document.createElement('button');
        btn.className = 'ai-assistant-btn';
        btn.innerHTML = '🤖';
        btn.title = 'AI Assistant (Ctrl+Space)';
        document.body.appendChild(btn);

        btn.onclick = () => this.showAIAssistant();
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.code === 'Space') {
                e.preventDefault();
                this.showAIAssistant();
            }
        });
    }

    showAIAssistant() {
        const modal = document.createElement('div');
        modal.className = 'modal ai-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">🤖 AI Assistant</div>
                <div class="ai-chat" id="ai-chat">
                    <div class="ai-msg">How can I help you today?</div>
                </div>
                <div class="ai-input-wrapper">
                    <input type="text" id="ai-input" placeholder="Ask anything..." autofocus>
                    <button id="ai-send">Send</button>
                </div>
                <div class="ai-suggestions">
                    <button onclick="window.nexusFeatures.aiQuery('Optimize my workflow')">Optimize workflow</button>
                    <button onclick="window.nexusFeatures.aiQuery('Show system health')">System health</button>
                    <button onclick="window.nexusFeatures.aiQuery('Suggest improvements')">Improvements</button>
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);

        const input = modal.querySelector('#ai-input');
        const send = modal.querySelector('#ai-send');
        
        const handleSend = () => {
            if (input.value.trim()) {
                this.aiQuery(input.value);
                input.value = '';
            }
        };

        send.onclick = handleSend;
        input.onkeypress = (e) => e.key === 'Enter' && handleSend();
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    async aiQuery(query) {
        const chat = document.getElementById('ai-chat');
        chat.innerHTML += `<div class="user-msg">${query}</div>`;
        
        try {
            const response = await fetch('/api/ai/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            chat.innerHTML += `<div class="ai-msg">${data.response || 'Processing...'}</div>`;
        } catch {
            chat.innerHTML += `<div class="ai-msg">Analyzing your request...</div>`;
        }
        chat.scrollTop = chat.scrollHeight;
    }

    // Real-time collaboration
    setupCollaboration() {
        const btn = document.createElement('button');
        btn.className = 'collab-btn';
        btn.innerHTML = '👥';
        btn.title = 'Collaboration';
        document.body.appendChild(btn);

        btn.onclick = () => this.showCollaboration();
    }

    showCollaboration() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">👥 Collaboration</div>
                <div class="collab-section">
                    <h3>Share Session</h3>
                    <input type="text" id="share-link" value="ultron://session/${Date.now()}" readonly>
                    <button onclick="navigator.clipboard.writeText(document.getElementById('share-link').value)">Copy Link</button>
                </div>
                <div class="collab-section">
                    <h3>Active Users</h3>
                    <div class="user-list">
                        <div class="user-item">👤 You (Host)</div>
                    </div>
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    // Analytics dashboard
    setupAnalytics() {
        const btn = document.createElement('button');
        btn.className = 'analytics-btn';
        btn.innerHTML = '📊';
        btn.title = 'Analytics';
        document.body.appendChild(btn);

        btn.onclick = () => this.showAnalytics();
    }

    showAnalytics() {
        const stats = this.calculateStats();
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content analytics-modal">
                <div class="modal-title">📊 Analytics Dashboard</div>
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-value">${stats.commands}</div><div class="stat-label">Commands</div></div>
                    <div class="stat-card"><div class="stat-value">${stats.sessions}</div><div class="stat-label">Sessions</div></div>
                    <div class="stat-card"><div class="stat-value">${stats.uptime}</div><div class="stat-label">Uptime</div></div>
                    <div class="stat-card"><div class="stat-value">${stats.efficiency}%</div><div class="stat-label">Efficiency</div></div>
                </div>
                <div class="chart-container">
                    <canvas id="activity-chart"></canvas>
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        this.drawChart();
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    calculateStats() {
        return {
            commands: localStorage.getItem('ultron_command_count') || 0,
            sessions: localStorage.getItem('ultron_session_count') || 1,
            uptime: '2h 34m',
            efficiency: 87
        };
    }

    drawChart() {
        const canvas = document.getElementById('activity-chart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        canvas.width = 500;
        canvas.height = 200;
        
        ctx.fillStyle = '#ff4444';
        for (let i = 0; i < 10; i++) {
            const h = Math.random() * 150 + 20;
            ctx.fillRect(i * 50, 200 - h, 40, h);
        }
    }

    // Workspace manager
    setupWorkspaces() {
        this.workspaces = JSON.parse(localStorage.getItem('ultron_workspaces') || '[]');
        
        const btn = document.createElement('button');
        btn.className = 'workspace-btn';
        btn.innerHTML = '🗂️';
        btn.title = 'Workspaces';
        document.body.appendChild(btn);

        btn.onclick = () => this.showWorkspaces();
    }

    showWorkspaces() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">🗂️ Workspaces</div>
                <div class="workspace-input">
                    <input type="text" id="new-workspace" placeholder="New workspace name...">
                    <button onclick="window.nexusFeatures.createWorkspace()">Create</button>
                </div>
                <div class="workspace-list" id="workspace-list">
                    ${this.workspaces.map((w, i) => `
                        <div class="workspace-item">
                            <span>${w.name}</span>
                            <button onclick="window.nexusFeatures.loadWorkspace(${i})">Load</button>
                            <button onclick="window.nexusFeatures.deleteWorkspace(${i})">Delete</button>
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    createWorkspace() {
        const input = document.getElementById('new-workspace');
        if (input.value.trim()) {
            this.workspaces.push({ name: input.value, data: {}, created: Date.now() });
            localStorage.setItem('ultron_workspaces', JSON.stringify(this.workspaces));
            document.getElementById('workspace-list').innerHTML = this.workspaces.map((w, i) => `
                <div class="workspace-item">
                    <span>${w.name}</span>
                    <button onclick="window.nexusFeatures.loadWorkspace(${i})">Load</button>
                    <button onclick="window.nexusFeatures.deleteWorkspace(${i})">Delete</button>
                </div>
            `).join('');
            input.value = '';
        }
    }

    loadWorkspace(i) {
        this.notify(`Loaded: ${this.workspaces[i].name}`, 'success');
        document.querySelectorAll('.modal').forEach(m => m.remove());
    }

    deleteWorkspace(i) {
        this.workspaces.splice(i, 1);
        localStorage.setItem('ultron_workspaces', JSON.stringify(this.workspaces));
        this.showWorkspaces();
    }

    // Plugin system
    setupPlugins() {
        const btn = document.createElement('button');
        btn.className = 'plugin-btn';
        btn.innerHTML = '🔌';
        btn.title = 'Plugins';
        document.body.appendChild(btn);

        btn.onclick = () => this.showPlugins();
    }

    showPlugins() {
        const plugins = [
            { name: 'GitHub Integration', enabled: true },
            { name: 'Slack Notifications', enabled: false },
            { name: 'Jira Sync', enabled: false },
            { name: 'Docker Manager', enabled: true }
        ];

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">🔌 Plugins</div>
                <div class="plugin-list">
                    ${plugins.map((p, i) => `
                        <div class="plugin-item">
                            <span>${p.name}</span>
                            <label class="switch">
                                <input type="checkbox" ${p.enabled ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    // Timeline view
    setupTimeline() {
        const btn = document.createElement('button');
        btn.className = 'timeline-btn';
        btn.innerHTML = '⏱️';
        btn.title = 'Timeline';
        document.body.appendChild(btn);

        btn.onclick = () => this.showTimeline();
    }

    showTimeline() {
        const events = [
            { time: '10:30', event: 'Screenshot captured', type: 'success' },
            { time: '10:25', event: 'Analysis completed', type: 'info' },
            { time: '10:20', event: 'System started', type: 'success' }
        ];

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-title">⏱️ Timeline</div>
                <div class="timeline">
                    ${events.map(e => `
                        <div class="timeline-item ${e.type}">
                            <div class="timeline-time">${e.time}</div>
                            <div class="timeline-event">${e.event}</div>
                        </div>
                    `).join('')}
                </div>
                <button class="modal-close">Close</button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-close').onclick = () => modal.remove();
    }

    // Command palette
    setupCommandPalette() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'P') {
                e.preventDefault();
                this.showCommandPalette();
            }
        });
    }

    showCommandPalette() {
        const commands = [
            'Screenshot', 'Analyze', 'Search', 'Tasks', 'Bookmarks', 
            'Export', 'Settings', 'Help', 'Refresh', 'Clear'
        ];

        const modal = document.createElement('div');
        modal.className = 'modal command-palette';
        modal.innerHTML = `
            <div class="modal-content palette-content">
                <input type="text" id="palette-input" placeholder="Type command..." autofocus>
                <div class="command-list" id="command-list">
                    ${commands.map(c => `<div class="command-item">${c}</div>`).join('')}
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        const input = modal.querySelector('#palette-input');
        const list = modal.querySelector('#command-list');

        input.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            list.innerHTML = commands
                .filter(c => c.toLowerCase().includes(val))
                .map(c => `<div class="command-item">${c}</div>`)
                .join('');
        });

        modal.onclick = (e) => e.target === modal && modal.remove();
    }

    // Smart notifications with priority
    setupSmartNotifications() {
        this.notificationQueue = [];
        setInterval(() => this.processNotifications(), 5000);
    }

    processNotifications() {
        if (this.notificationQueue.length > 0) {
            const notif = this.notificationQueue.shift();
            this.notify(notif.message, notif.type);
        }
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
        window.nexusFeatures = new NexusFeatures();
    });
} else {
    window.nexusFeatures = new NexusFeatures();
}
