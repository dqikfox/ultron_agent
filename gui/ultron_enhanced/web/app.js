/**
 * ULTRON Pokedex AI Interface - Enhanced JavaScript Controller
 * Purpose: Drive the Pokédex-styled dashboard, wiring DOM events to Ultron services.
 * Dependencies: Relies on REST endpoints exposed by web_gui_server.py and optional Web Speech API.
 * External Requirements: Needs Ollama (default localhost:11434) and honors ULTRON_API_CONFIG.portMap overrides.
 * Interaction: Issues fetch requests to /api/* routes, orchestrates voice playback, tools, and vision workflows.
 */

console.log('[ULTRON] Pokedex interface script loaded - app.js:9');

class UltronPokedexInterface {
    constructor() {
        const injectedConfig = window.ULTRON_API_CONFIG || {};
        this.portMap = injectedConfig.portMap || window.__ULTRON_PORT_MAP || {};
        this.API_BASE_URL = injectedConfig.baseUrl || this.resolveApiBaseUrl();
        this.AGENT_BASE_URL = this.API_BASE_URL;

        this.currentSection = 'dashboard';
        this.currentTheme = 'red';

        // CRITICAL: Voice must NEVER auto-enable on startup - requires explicit user action
        // Dependency: handleStartupAnnouncement() also enforces this.voiceEnabled = false
        // Related: toggleVoiceChat() manages state transitions with server sync
        this.voiceEnabled = false;
        this.soundEnabled = true;
        this.isListening = false;
        this.isSpeaking = false;
        this.shouldRestartRecognition = false;
        this.recognition = null;
        this.lastVoiceResultTimestamp = 0;
        this.powerMenuInitialized = false; // Prevent auto-opening on startup
        this.systemStats = {
            cpu: 0,
            memory: 0,
            disk: 0,
            network: 'DISCONNECTED'
        };
        this.apiCallCounts = {};
        this.timers = {};
        this.ttsQueue = [];
        this.availableModels = [];
        this.lastVisionDigest = {
            count: 0,
            latestTimestamp: null
        };
        this.dashboardLogLimit = 25;
        this.latestAgentInfo = null;
        this.latestVoiceStatus = null;
        this.latestLLMStatus = null;
        this.dom = {};
        this.voiceStartupAnnounced = false;

        this.init();
    }

    resolveApiBaseUrl() {
        const { protocol, hostname, port, origin } = window.location;
        if (this.portMap.webGui) {
            return `${protocol}//${hostname}:${this.portMap.webGui}`;
        }
        if (this.portMap.api) {
            return `${protocol}//${hostname}:${this.portMap.api}`;
        }
        if (origin) {
            return origin;
        }
        const derivedPort = port ? `:${port}` : '';
        return `${protocol}//${hostname}${derivedPort}`;
    }

    init() {
        this.cacheDomReferences();
        this.setupEventListeners();
        this.setupStartButton();
        this.initializeTheme();
        this.startAnimations();
        this.loadConfiguration();
        this.ensureVoiceStatus();
        this.updateClock();
        this.updateDate();
        this.startLEDSequence();
        this.initializeAriaStates();
    }

    cacheDomReferences() {
        this.dom = {
            startScreen: document.getElementById('start-screen'),
            startButton: document.getElementById('start-button'),
            loadingScreen: document.getElementById('loading-screen'),
            mainInterface: document.getElementById('main-interface'),
            consoleOutput: document.getElementById('console-output'),
            consoleInput: document.getElementById('console-input'),
            chatInput: document.getElementById('chat-input'),
            chatMessages: document.getElementById('chat-messages'),
            visionDisplay: document.getElementById('vision-display'),
            toolGrid: document.getElementById('tools-grid'),
            toolDetails: document.getElementById('tool-details'),
            elevenLabsOverlay: document.getElementById('elevenlabs-text-overlay'),
            statusClock: document.getElementById('status-clock'),
            statusDate: document.getElementById('status-date'),
            voiceStatus: document.getElementById('voice-status'),
            dashboardOnlineIndicator: document.getElementById('dashboard-online-indicator'),
            dashboardStatusSubtitle: document.getElementById('dashboard-status-subtitle'),
            dashboardAgentStatus: document.getElementById('dashboard-agent-status'),
            dashboardUptime: document.getElementById('dashboard-uptime'),
            dashboardVoiceStatus: document.getElementById('dashboard-voice-status'),
            dashboardVoiceProvider: document.getElementById('dashboard-voice-provider'),
            dashboardModelName: document.getElementById('dashboard-model-name'),
            dashboardLLMStatus: document.getElementById('dashboard-llm-status'),
            dashboardToolsCount: document.getElementById('dashboard-tools-count'),
            dashboardCpu: document.getElementById('dashboard-cpu'),
            dashboardCpuBar: document.getElementById('dashboard-cpu-bar'),
            dashboardMemory: document.getElementById('dashboard-memory'),
            dashboardMemoryBar: document.getElementById('dashboard-memory-bar'),
            dashboardDisk: document.getElementById('dashboard-disk'),
            dashboardDiskBar: document.getElementById('dashboard-disk-bar'),
            dashboardNetwork: document.getElementById('dashboard-network'),
            dashboardLog: document.getElementById('dashboard-log-feed'),
            leds: {
                led1: document.getElementById('led-1'),
                led2: document.getElementById('led-2'),
                led3: document.getElementById('led-3')
            }
        };
    }

    setupEventListeners() {
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

        if (this.dom.consoleInput) {
            this.dom.consoleInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    this.handleConsoleCommand(event.target.value);
                    event.target.value = '';
                }
            });
        }

        document.querySelectorAll('[data-direction]').forEach(btn => {
            btn.addEventListener('click', (event) => {
                const direction = event.currentTarget.dataset.direction;
                this.handleDPadInput(direction);
                this.playSound('button');
            });
        });

        document.getElementById('btn-a')?.addEventListener('click', () => {
            this.handleActionButton('A');
            this.playSound('confirm');
        });

        document.getElementById('btn-b')?.addEventListener('click', () => {
            this.handleActionButton('B');
            this.playSound('button');
        });

        document.getElementById('btn-power')?.addEventListener('click', () => {
            if (!this.powerMenuInitialized) {
                this.powerMenuInitialized = true;
            }
            this.showPowerMenu();
            this.playSound('button');
        });

        document.getElementById('btn-volume')?.addEventListener('click', () => {
            this.toggleSound();
            this.playSound('button');
        });

        document.getElementById('btn-settings')?.addEventListener('click', () => {
            this.switchSection('settings');
            this.playSound('button');
        });

        document.getElementById('capture-btn')?.addEventListener('click', () => {
            this.captureScreen();
        });

        document.getElementById('analyze-btn')?.addEventListener('click', () => {
            this.analyzeVision();
        });

        document.getElementById('theme-select')?.addEventListener('change', (event) => {
            this.changeTheme(event.target.value);
        });

        document.getElementById('voice-toggle')?.addEventListener('click', async () => {
            try {
                await this.toggleVoice();
            } catch (error) {
                console.debug('[ULTRON] Voice toggle click failed - app.js:221', error);
            }
        });

        document.querySelectorAll('.power-btn').forEach(btn => {
            btn.addEventListener('click', (event) => {
                const action = event.currentTarget.dataset.action;
                this.handlePowerAction(action);
            });
        });

        document.getElementById('power-menu')?.addEventListener('click', (event) => {
            if (event.target.id === 'power-menu') {
                this.hidePowerMenu();
            }
        });

        document.getElementById('send-chat-btn')?.addEventListener('click', () => {
            this.sendChatMessage();
        });

        document.getElementById('voice-chat-btn')?.addEventListener('click', async () => {
            try {
                await this.toggleVoiceChat();
            } catch (error) {
                console.debug('[ULTRON] Voice chat toggle failed - app.js:246', error);
            }
        });

        document.getElementById('clear-chat-btn')?.addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('export-chat-btn')?.addEventListener('click', () => {
            this.userRequestedExport = true; // Mark as user-requested export
            this.exportChat();
        });

        document.getElementById('switch-model-btn')?.addEventListener('click', async () => {
            try {
                await this.switchModel();
            } catch (error) {
                console.debug('[ULTRON] Model switch interaction failed - app.js:263', error);
            }
        });

        document.getElementById('dashboard-clear-log')?.addEventListener('click', () => {
            this.clearDashboardLog();
        });

        if (this.dom.chatInput) {
            this.dom.chatInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    this.sendChatMessage();
                }
            });
        }

        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (event) => {
                const prompt = event.currentTarget.dataset.prompt;
                this.handleQuickAction(prompt);
            });
        });

        document.getElementById('refresh-tools-btn')?.addEventListener('click', () => {
            this.refreshTools();
        });

        document.getElementById('reload-tools-btn')?.addEventListener('click', () => {
            this.reloadAllTools();
        });

        document.getElementById('test-tools-btn')?.addEventListener('click', () => {
            this.testAllTools();
        });

        document.getElementById('show-elevenlabs-btn')?.addEventListener('click', () => {
            this.showElevenLabsTextOverlay();
        });

        document.getElementById('close-elevenlabs-overlay')?.addEventListener('click', () => {
            this.hideElevenLabsTextOverlay();
        });

        document.getElementById('clear-elevenlabs-text')?.addEventListener('click', () => {
            this.clearElevenLabsOverlay();
        });

        document.getElementById('toggle-elevenlabs-widget')?.addEventListener('click', () => {
            this.toggleElevenLabsWidget();
        });

        document.getElementById('test-tts-btn')?.addEventListener('click', () => {
            this.testTTS();
        });

        document.getElementById('manual-tts-test-btn')?.addEventListener('click', () => {
            this.testTTS();
        });

        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
    }

    setupStartButton() {
        if (!this.dom.startButton) {
            this.hideLoadingScreen();
            this.initializeAfterStart();
            return;
        }

        this.dom.startButton.addEventListener('click', async () => {
            this.dom.startScreen?.classList.add('hidden');
            this.hideLoadingScreen();
            this.initializeAfterStart();
            this.playStartupSound();

            try {
                await this.syncVoiceStatus();
            } catch (error) {
                console.debug('[ULTRON] Voice status sync failed during startup - app.js:344', error);
            }

            try {
                await this.handleStartupAnnouncement();
            } catch (error) {
                console.debug('[ULTRON] Startup announcement failed - app.js:350', error);
            }
        });
    }

    initializeAfterStart() {
        this.startSystemMonitoring();
        this.startAnalysisPolling();
        this.loadNvidiaStatus();
        this.loadAutoGenStatus();
        this.loadToolsStatus();
        this.switchSection(this.currentSection);
    }

    async handleStartupAnnouncement() {
        if (this.voiceStartupAnnounced) {
            return;
        }

        if (!this.latestVoiceStatus) {
            try {
                await this.syncVoiceStatus();
            } catch (error) {
                console.debug('[ULTRON] Voice sync before announcement failed - app.js:373', error);
            }
        }

        this.voiceStartupAnnounced = true;

        // CRITICAL: NEVER auto-enable voice - always require manual user action
        // This prevents unwanted microphone activation on page load
        // User must explicitly click the microphone button to enable voice
        // Dependency: This state syncs with web_gui_server.py /api/voice/toggle endpoint
        this.voiceEnabled = false;

        // Just show system message, don't speak
        this.addSystemMessage('Voice services are ready. Click the voice button to enable audio.');
    }

    hideLoadingScreen() {
        this.dom.loadingScreen?.classList.add('hidden');
        this.dom.mainInterface?.classList.remove('hidden');
        this.addSystemMessage('ULTRON AI System Online');
        this.addSystemMessage('All systems operational');
        this.addSystemMessage('Awaiting commands...');
    }

    startSystemMonitoring() {
        if (this.timers.systemMonitor) {
            clearInterval(this.timers.systemMonitor);
        }
        this.updateSystemStats();
        this.timers.systemMonitor = setInterval(() => this.updateSystemStats(), 5000);
    }

    startAnalysisPolling() {
        if (this.timers.analysisMonitor) {
            clearInterval(this.timers.analysisMonitor);
        }
        this.timers.analysisMonitor = setInterval(async () => {
            try {
                const response = await this.apiCall('/api/vision/recent');
                if (!response.ok) {
                    return;
                }
                const data = await response.json();
                const analyses = data.recent_analyses || data.analyses || [];
                if (Array.isArray(analyses) && analyses.length) {
                    const latestEntry = analyses[0];
                    const latestTimestamp = latestEntry?.timestamp || null;
                    const hasNewCount = analyses.length !== this.lastVisionDigest.count;
                    const isNewer = latestTimestamp && latestTimestamp !== this.lastVisionDigest.latestTimestamp;

                    if (hasNewCount || isNewer || !this.lastVisionDigest.latestTimestamp) {
                        const suffix = analyses.length > 1 ? 'analyses' : 'analysis';
                        this.addSystemMessage(`${analyses.length} recent vision ${suffix} ready`);
                        this.lastVisionDigest = {
                            count: analyses.length,
                            latestTimestamp
                        };
                    }
                } else {
                    this.lastVisionDigest = {
                        count: 0,
                        latestTimestamp: null
                    };
                }
            } catch (error) {
                console.debug('[ULTRON] Vision polling failed - app.js:435', error);
            }
        }, 10000);
    }

    async updateSystemStats() {
        try {
            const response = await this.apiCall('/api/system/stats');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const stats = await response.json();
            const system = stats.system || {};
            const agent = stats.agent || {};
            this.systemStats = {
                cpu: Number.parseFloat(system.cpu_percent ?? stats.cpu ?? 0) || 0,
                memory: Number.parseFloat(system.memory_percent ?? stats.memory ?? 0) || 0,
                disk: Number.parseFloat(system.disk_percent ?? stats.disk ?? 0) || 0,
                network: (agent.status ? agent.status.toUpperCase() : (stats.network || 'UNKNOWN'))
            };
            this.latestSystemSnapshot = stats;
        } catch (error) {
            console.debug('[ULTRON] Stats fallback - app.js:457', error);
            this.systemStats = {
                cpu: Math.floor(Math.random() * 25) + 25,
                memory: Math.floor(Math.random() * 30) + 30,
                disk: Math.floor(Math.random() * 25) + 30,
                network: 'SIMULATED'
            };
        }
        this.renderSystemStats();
        this.renderDashboardSnapshot();
    }

    renderSystemStats() {
        const clamp = (value) => Math.max(0, Math.min(100, Math.round(value)));
        const cpu = clamp(this.systemStats.cpu);
        const memory = clamp(this.systemStats.memory);
        const disk = clamp(this.systemStats.disk);

        const cpuValue = document.getElementById('cpu-usage');
        const memValue = document.getElementById('memory-usage');
        const diskValue = document.getElementById('disk-usage');
        const netValue = document.getElementById('network-status');

        cpuValue && (cpuValue.textContent = `${cpu}%`);
        memValue && (memValue.textContent = `${memory}%`);
        diskValue && (diskValue.textContent = `${disk}%`);
        netValue && (netValue.textContent = this.systemStats.network);

        const cpuBar = document.getElementById('cpu-bar');
        const memBar = document.getElementById('memory-bar');
        const diskBar = document.getElementById('disk-bar');
        cpuBar && (cpuBar.style.width = `${cpu}%`);
        memBar && (memBar.style.width = `${memory}%`);
        diskBar && (diskBar.style.width = `${disk}%`);

        if (this.latestSystemSnapshot) {
            const agentStatus = (this.latestSystemSnapshot.agent?.status || 'unknown').toUpperCase();
            const overall = document.getElementById('overall-status');
            const agent = document.getElementById('agent-status');
            const uptime = document.getElementById('system-uptime');

            overall && (overall.textContent = agentStatus);
            agent && (agent.textContent = agentStatus);
            uptime && (uptime.textContent = this.latestSystemSnapshot.agent?.uptime || '00:00:00');
        }
    }

    renderDashboardSnapshot() {
        const indicator = this.dom.dashboardOnlineIndicator;
        if (!indicator) {
            return;
        }

        const agentStatus = (this.latestAgentInfo?.status || this.latestSystemSnapshot?.agent?.status || 'unknown').toUpperCase();
        const isAgentOnline = agentStatus === 'ONLINE';
        const statusText = isAgentOnline ? 'ULTRON IS ONLINE' : `ULTRON ${agentStatus}`;
        this.updateStatusPill(indicator, isAgentOnline, statusText);

        if (this.dom.dashboardStatusSubtitle) {
            this.dom.dashboardStatusSubtitle.textContent = `Updated ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        }

        this.setTextContent(this.dom.dashboardAgentStatus, agentStatus);
        this.setTextContent(this.dom.dashboardUptime, this.latestSystemSnapshot?.agent?.uptime || '00:00:00');

        const voiceSnapshot = this.latestVoiceStatus || {};
        // NEVER auto-enable voice - keep disabled until user manually enables
        const voiceStatusText = (voiceSnapshot.status || 'DISABLED').toUpperCase();
        this.setTextContent(this.dom.dashboardVoiceStatus, voiceStatusText);
        this.setTextContent(this.dom.dashboardVoiceProvider, (voiceSnapshot.provider || 'UNSET').toUpperCase());
        this.ensureVoiceStatus();

        const llmSnapshot = this.latestLLMStatus || {};
        this.setTextContent(this.dom.dashboardLLMStatus, (llmSnapshot.status || 'OFFLINE').toUpperCase());
        this.setTextContent(this.dom.dashboardModelName, (llmSnapshot.model || 'UNKNOWN').toUpperCase());

        const toolCount = this.latestAgentInfo?.tools_count;
        if (typeof toolCount === 'number') {
            this.setTextContent(this.dom.dashboardToolsCount, String(toolCount));
        } else {
            this.setTextContent(this.dom.dashboardToolsCount, '--');
        }

        this.updateMetricDisplays(this.dom.dashboardCpu, this.dom.dashboardCpuBar, this.systemStats.cpu);
        this.updateMetricDisplays(this.dom.dashboardMemory, this.dom.dashboardMemoryBar, this.systemStats.memory);
        this.updateMetricDisplays(this.dom.dashboardDisk, this.dom.dashboardDiskBar, this.systemStats.disk);
        this.setTextContent(this.dom.dashboardNetwork, this.systemStats.network || '--');

        // Update footer status bar
        this.updateFooterStatus();
    }

    updateFooterStatus() {
        // Ollama status
        const ollamaStatus = this.latestLLMStatus?.status === 'online' ? 'ONLINE' : 'OFFLINE';
        this.setTextContent(document.getElementById('footer-ollama'), ollamaStatus);

        // Uptime
        const uptime = this.latestSystemSnapshot?.agent?.uptime || '00:00:00';
        this.setTextContent(document.getElementById('footer-uptime'), uptime);

        // ElevenLabs Voice status
        const voiceStatus = this.voiceEnabled ? 'ENABLED' : 'DISABLED';
        this.setTextContent(document.getElementById('footer-voice'), voiceStatus);

        // LLM Model name
        const modelName = this.latestLLMStatus?.model || 'QWEN3-CODER:480B-CLOUD';
        this.setTextContent(document.getElementById('footer-llm-model'), modelName.toUpperCase());

        // LLM Status
        const llmStatus = this.latestLLMStatus?.status || 'OFFLINE';
        this.setTextContent(document.getElementById('footer-llm-status'), llmStatus.toUpperCase());
    }

    setTextContent(node, value) {
        if (node) {
            node.textContent = value;
        }
    }

    updateMetricDisplays(valueNode, barNode, value) {
        const safeValue = Number.isFinite(value) ? Math.max(0, Math.min(100, Math.round(value))) : 0;
        if (valueNode) {
            valueNode.textContent = `${safeValue}%`;
        }
        if (barNode) {
            barNode.style.width = `${safeValue}%`;
        }
    }

    updateStatusPill(node, isOnline, text) {
        if (!node) {
            return;
        }
        node.textContent = text;
        node.classList.toggle('status-online', Boolean(isOnline));
        node.classList.toggle('status-offline', !isOnline);
    }

    switchSection(sectionName) {
        // Update navigation tab states
        document.querySelectorAll('.nav-button').forEach(btn => {
            const isActive = btn.dataset.section === sectionName;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            btn.setAttribute('tabindex', isActive ? '0' : '-1');
        });

        // Update section visibility with ARIA
        document.querySelectorAll('.section-content').forEach(section => {
            const sectionId = section.id.replace('-section', '');
            const isActive = sectionId === sectionName;
            section.classList.toggle('active', isActive);
            section.setAttribute('aria-hidden', isActive ? 'false' : 'true');
        });

        // Update current section indicator
        const indicator = document.getElementById('current-section-indicator');
        if (indicator) {
            const icons = {
                console: '🖥️ CONSOLE',
                system: '⚙️ SYSTEM',
                vision: '👁️ VISION',
                tasks: '📋 TASKS',
                files: '📁 FILES',
                settings: '🔧 CONFIG',
                profile: '👤 PROFILE',
                autogen: '🤖 AUTOGEN',
                assistant: '🤖 AI CHAT',
                dashboard: '📊 DASHBOARD',
                nvidia: '🎯 NVIDIA',
                tools: '🔧 TOOLS',
                'llm-chat': '💬 LLM CHAT',
                'stable-diffusion': '🎨 AI ART'
            };
            indicator.textContent = icons[sectionName] || '🖥️ CONSOLE';
        }

        this.currentSection = sectionName;
        this.loadSectionData(sectionName);

        // Announce section change to screen readers
        this.announceToScreenReader(`Switched to ${sectionName} section`);
    }

    async loadSectionData(section) {
        switch (section) {
            case 'system':
                await this.updateSystemInfo();
                break;
            case 'files':
                await this.loadFileSystem();
                break;
            case 'tasks':
                await this.loadTasks();
                break;
            case 'vision':
                await this.loadVisionSystem();
                break;
            case 'profile':
                await this.loadProfileData();
                break;
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'nvidia':
                await this.loadNvidiaStatus();
                break;
            case 'autogen':
                await this.loadAutoGenStatus();
                break;
            case 'llm-chat':
                await this.loadLLMChatStatus();
                break;
            case 'tools':
                await this.loadToolsStatus();
                break;
            case 'stable-diffusion':
                // No initial data loading needed for stable diffusion
                break;
        }
    }

    handleConsoleCommand(rawCommand) {
        const command = (rawCommand || '').trim();
        if (!command) {
            return;
        }
        this.addUserMessage(command);
        this.processCommand(command).catch((error) => {
            console.error('[ULTRON] Command processing failed - app.js:689', error);
            this.addErrorMessage('Command failed. Check logs for details.');
        });
    }

    async processCommand(command) {
        const lower = command.toLowerCase();

        switch (true) {
            case lower === 'help':
                this.addSystemMessage('Available commands: help, clear, status, theme <red|blue|high-contrast|ultron-steampunk>, capture, analyze, shutdown, restart');
                return;
            case lower === 'clear':
                this.clearConsole();
                return;
            case lower === 'status':
                this.addSystemMessage(`CPU: ${this.systemStats.cpu}%`);
                this.addSystemMessage(`Memory: ${this.systemStats.memory}%`);
                this.addSystemMessage(`Disk: ${this.systemStats.disk}%`);
                this.addSystemMessage(`Network: ${this.systemStats.network}`);
                return;
            case lower.startsWith('theme '):
                this.changeTheme(lower.split(' ')[1] || 'red');
                this.addSystemMessage(`Theme changed to ${this.currentTheme}`);
                return;
            case lower === 'capture':
                await this.captureScreen();
                return;
            case lower === 'analyze':
                await this.analyzeVision();
                return;
            case lower === 'shutdown':
                this.addSystemMessage('Use the power button for shutdown options.');
                return;
            case lower === 'restart':
                this.addSystemMessage('Use the power button for restart options.');
                return;
        }

        try {
            // NOTE: Removed "Processing command..." notification per user request
            // this.addSystemMessage('Processing command...');
            this.trackApiCall('/api/command');
            const response = await fetch(`${this.API_BASE_URL}/api/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.success) {
                this.addSystemMessage(data.response || 'Command executed successfully');
            } else {
                this.addErrorMessage(data.error || 'Command failed');
            }
        } catch (error) {
            console.error('[ULTRON] Backend command failed - app.js:746', error);
            this.addErrorMessage('Backend unavailable. Running in local mode.');
        }
    }

    clearConsole() {
        if (this.dom.consoleOutput) {
            this.dom.consoleOutput.innerHTML = '';
        }
    }

    initializeAriaStates() {
        // Set initial ARIA states for navigation tabs
        document.querySelectorAll('.nav-button').forEach(btn => {
            const isActive = btn.dataset.section === this.currentSection;
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            btn.setAttribute('tabindex', isActive ? '0' : '-1');
        });

        // Set initial ARIA states for sections
        document.querySelectorAll('.section-content').forEach(section => {
            const sectionId = section.id.replace('-section', '');
            const isActive = sectionId === this.currentSection;
            section.setAttribute('aria-hidden', isActive ? 'false' : 'true');
        });
    }

    changeTheme(theme) {
        const validThemes = ['red', 'blue', 'high-contrast', 'ultron-steampunk'];
        if (!validThemes.includes(theme)) {
            theme = 'red';
        }
        const body = document.getElementById('pokedex-body');
        if (body) {
            // Remove all theme classes first
            body.classList.remove('pokedex-red', 'pokedex-blue');
            // Add the appropriate theme class
            if (theme === 'red' || theme === 'blue') {
                body.className = `pokedex-body pokedex-${theme}`;
            } else {
                // For special themes, apply to document.body
                document.body.className = theme;
            }
        }
        this.currentTheme = theme;
    }

    startAnimations() {
        console.debug('[ULTRON] Animations ready - app.js:794');
    }

    loadConfiguration() {
        console.debug('[ULTRON] Configuration loaded - app.js:798');
    }

    playStartupSound() {
        this.playSound('startup');
    }

    playSound(sound) {
        if (!this.soundEnabled) {
            return;
        }
        try {
            const audio = new Audio(`sounds/${sound}.mp3`);
            audio.volume = 0.4;
            audio.play().catch((error) => console.debug('[ULTRON] Audio blocked - app.js:812', error));
        } catch (error) {
            console.debug('[ULTRON] Audio play failed - app.js:814', error);
        }
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        this.addSystemMessage(`Sound ${this.soundEnabled ? 'enabled' : 'muted'}`);
    }

    startLEDSequence() {
        this.setLEDLight('led1', true);
        setTimeout(() => this.setLEDLight('led2', true), 150);
        setTimeout(() => this.setLEDLight('led3', true), 300);
    }

    setLEDLight(key, enabled) {
        const element = this.dom.leds?.[key];
        if (element) {
            element.classList.toggle('active', Boolean(enabled));
        }
    }

    updateClock() {
        if (!this.dom.statusClock) {
            return;
        }
        const now = new Date();
        this.dom.statusClock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        if (this.timers.clock) {
            clearTimeout(this.timers.clock);
        }
        this.timers.clock = setTimeout(() => this.updateClock(), 60 * 1000);
    }

    updateDate() {
        if (!this.dom.statusDate) {
            return;
        }
        this.dom.statusDate.textContent = new Date().toLocaleDateString();
    }

    async loadSystemInfo() {
        await this.updateSystemStats();
    }

    async updateSystemInfo() {
        await this.updateSystemStats();
    }

    async loadDashboard() {
        await this.updateSystemStats();
        await Promise.all([
            this.syncVoiceStatus(),
            this.refreshAgentInfo(),
            this.loadLLMChatStatus()
        ]);
        this.renderDashboardSnapshot();
    }

    async refreshAgentInfo() {
        try {
            const response = await this.apiCall('/api/agent/info');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.latestAgentInfo = await response.json();
        } catch (error) {
            console.debug('[ULTRON] Agent info unavailable - app.js:881', error);
            this.latestAgentInfo = null;
        }
    }

    async syncVoiceStatus() {
        try {
            const response = await this.apiCall('/api/voice/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.latestVoiceStatus = await response.json();
            const status = this.latestVoiceStatus || {};
            // Don't auto-enable voice - keep it disabled until user clicks enable
            // if (typeof status.voice_enabled === 'boolean') {
            //     this.voiceEnabled = status.voice_enabled;
            // } else {
            //     this.voiceEnabled = Boolean(status.output_enabled || status.input_enabled || status.config_enabled);
            // }
        } catch (error) {
            console.debug('[ULTRON] Voice status unavailable - app.js:901', error);
            this.latestVoiceStatus = { status: 'unavailable' };
            this.voiceEnabled = false;
        }
        this.ensureVoiceStatus();
    }

    async loadVisionSystem() {
        try {
            const response = await this.apiCall('/api/vision/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderVisionStatus(data);
        } catch (error) {
            console.debug('[ULTRON] Vision status unavailable - app.js:917', error);
            this.renderVisionStatus({ status: 'offline' });
        }
    }

    renderVisionStatus(status) {
        const statusEl = document.getElementById('vision-status');
        if (statusEl) {
            statusEl.textContent = status.status ? status.status.toUpperCase() : 'UNKNOWN';
        }
    }

    renderVisionResult(result) {
        if (!this.dom.visionDisplay || !result) {
            return;
        }
        this.dom.visionDisplay.innerHTML = '';
        if (result.image_data) {
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${result.image_data}`;
            img.alt = 'Vision analysis result';
            this.dom.visionDisplay.appendChild(img);
        }
        if (result.description) {
            const description = document.createElement('div');
            description.className = 'vision-description';
            description.textContent = result.description;
            this.dom.visionDisplay.appendChild(description);
        }
    }

    async captureScreen() {
        try {
            this.addSystemMessage('Capturing screen...');
            const response = await this.apiCall('/api/vision/capture');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.addSystemMessage(data.message || 'Screen captured');
            await this.loadVisionSystem();
        } catch (error) {
            console.error('[ULTRON] Capture failed - app.js:959', error);
            this.addErrorMessage('Screen capture unavailable');
        }
    }

    async analyzeVision() {
        try {
            this.addSystemMessage('Running vision analysis...');
            const response = await this.apiCall('/api/vision/analyze');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderVisionResult(data.result || {});
            this.addSystemMessage('Vision analysis complete');
        } catch (error) {
            console.error('[ULTRON] Vision analysis failed - app.js:975', error);
            this.addErrorMessage('Vision analysis unavailable');
        }
    }

    async loadTasks() {
        try {
            const response = await this.apiCall('/api/system/processes');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderTaskList(data.processes || []);
        } catch (error) {
            console.debug('[ULTRON] Process list unavailable - app.js:989', error);
            this.renderTaskList([]);
        }
    }

    renderTaskList(processes) {
        const list = document.getElementById('task-list');
        if (!list) {
            return;
        }
        if (!processes.length) {
            list.innerHTML = '<li class="task-item">Process data unavailable</li>';
            return;
        }
        list.innerHTML = processes.slice(0, 10).map(proc => {
            const cpu = typeof proc.cpu === 'number' ? proc.cpu.toFixed(1) : proc.cpu || '-';
            return `<li class="task-item"><span>${proc.name}</span><span>${cpu}% CPU</span></li>`;
        }).join('');
    }

    async loadFileSystem() {
        try {
            const response = await this.apiCall('/api/filesystem/overview');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderFileSystem(data.entries || []);
        } catch (error) {
            console.debug('[ULTRON] File system data unavailable - app.js:1018', error);
            this.renderFileSystem([]);
        }
    }

    renderFileSystem(entries) {
        const list = document.getElementById('file-system-list');
        if (!list) {
            return;
        }
        if (!entries.length) {
            list.innerHTML = '<li class="file-item">File system data unavailable</li>';
            return;
        }
        list.innerHTML = entries.slice(0, 12).map(entry => {
            const name = entry.name || entry.path || 'Unknown';
            const type = entry.type || '';
            return `<li class="file-item"><span>${name}</span><span>${type}</span></li>`;
        }).join('');
    }

    async loadProfileData() {
        try {
            const response = await this.apiCall('/api/profile');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderProfile(data);
        } catch (error) {
            console.debug('[ULTRON] Profile data unavailable - app.js:1048', error);
            this.renderProfile(null);
        }
    }

    renderProfile(profile) {
        const container = document.getElementById('profile-details');
        if (!container) {
            return;
        }
        if (!profile) {
            container.innerHTML = '<div class="empty-state">Profile data unavailable</div>';
            return;
        }
        container.innerHTML = `
            <div class="profile-card">
                <h3>${profile.name || 'Ultron Operator'}</h3>
                <p>${profile.role || 'Operator'}</p>
            </div>
        `;
    }

    async loadNvidiaStatus() {
        try {
            const response = await this.apiCall('/api/nvidia/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            const statusEl = document.getElementById('nvidia-status');
            if (statusEl) {
                statusEl.textContent = data.status?.toUpperCase?.() || 'READY';
            }
        } catch (error) {
            console.debug('[ULTRON] NVIDIA status unavailable - app.js:1082', error);
        }
    }

    async loadAutoGenStatus() {
        try {
            const response = await this.apiCall('/api/autogen/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderAutoGenStatus(data);
        } catch (error) {
            console.debug('[ULTRON] AutoGen status unavailable - app.js:1095', error);
            this.renderAutoGenStatus({ status: 'offline' });
        }
    }

    renderAutoGenStatus(status) {
        const statusEl = document.getElementById('autogen-status');
        if (statusEl) {
            statusEl.textContent = status.status ? status.status.toUpperCase() : 'UNKNOWN';
        }
        const historyEl = document.getElementById('autogen-history');
        if (historyEl) {
            if (Array.isArray(status.history) && status.history.length) {
                historyEl.innerHTML = status.history.slice(-10).map(item => `<li>${item}</li>`).join('');
            } else {
                historyEl.innerHTML = '<li>No recent AutoGen activity</li>';
            }
        }
    }

    async sendAutoGenAction(endpoint, message) {
        try {
            this.addSystemMessage(message);
            const response = await this.apiCall(endpoint, { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            await this.loadAutoGenStatus();
        } catch (error) {
            console.debug('[ULTRON] AutoGen action failed - app.js:1124', error);
            this.addErrorMessage('AutoGen action failed');
        }
    }

    async startAutoGenStudio() {
        await this.sendAutoGenAction('/api/autogen/start', 'Starting AutoGen Studio...');
    }

    async stopAutoGenStudio() {
        await this.sendAutoGenAction('/api/autogen/stop', 'Stopping AutoGen Studio...');
    }

    async refreshAutoGenStatus() {
        this.addSystemMessage('Refreshing AutoGen status...');
        await this.loadAutoGenStatus();
    }

    async openAutoGenStudio() {
        window.open('/autogen', '_blank');
    }

    async createAutoGenAgent() {
        await this.sendAutoGenAction('/api/autogen/create-agent', 'Creating AutoGen agent...');
    }

    async createAutoGenWorkflow() {
        await this.sendAutoGenAction('/api/autogen/create-workflow', 'Creating AutoGen workflow...');
    }

    async loadToolsStatus() {
        try {
            const response = await this.apiCall('/api/tools');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.renderTools(data.tools || []);
        } catch (error) {
            console.debug('[ULTRON] Tool list unavailable - app.js:1163', error);
            this.renderTools([]);
        }
    }

    renderTools(tools) {
        if (!this.dom.toolGrid) {
            return;
        }
        if (!tools.length) {
            this.dom.toolGrid.innerHTML = '<div class="empty-state">No tools available</div>';
            return;
        }
        this.dom.toolGrid.innerHTML = tools.map(tool => `
            <div class="tool-card" data-tool="${tool.name}">
                <h4>${tool.name}</h4>
                <p>${tool.description || 'No description provided.'}</p>
            </div>
        `).join('');

        this.dom.toolGrid.querySelectorAll('.tool-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showToolDetails(card.dataset.tool, tools);
            });
        });
    }

    showToolDetails(toolName, tools) {
        const tool = tools.find(t => t.name === toolName);
        if (!tool || !this.dom.toolDetails) {
            return;
        }
        this.dom.toolDetails.innerHTML = `
            <h3>${tool.name}</h3>
            <p>${tool.description || 'No description provided.'}</p>
            <pre>${JSON.stringify(tool.parameters || {}, null, 2)}</pre>
        `;
    }

    async refreshTools() {
        this.addSystemMessage('Refreshing tools...');
        await this.loadToolsStatus();
    }

    async reloadAllTools() {
        try {
            this.addSystemMessage('Reloading tools...');
            const response = await this.apiCall('/api/tools/reload', { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            await this.loadToolsStatus();
        } catch (error) {
            console.debug('[ULTRON] Tool reload failed - app.js:1216', error);
            this.addErrorMessage('Tool reload failed');
        }
    }

    async testAllTools() {
        try {
            this.addSystemMessage('Running tool diagnostics...');
            const response = await this.apiCall('/api/tools/test', { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.addSystemMessage(`Tools tested: ${data.passed || 0}/${data.total || 0}`);
        } catch (error) {
            console.debug('[ULTRON] Tool diagnostics failed - app.js:1231', error);
            this.addErrorMessage('Tool diagnostics failed');
        }
    }

    async loadLLMChatStatus() {
        try {
            const response = await this.apiCall('/api/llm/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            this.latestLLMStatus = data;
            const statusText = (data.status || 'offline').toUpperCase();
            const modelName = data.model || 'Unknown Model';

            const statusEl = document.getElementById('chat-status') || document.getElementById('overall-status');
            if (statusEl) {
                statusEl.textContent = statusText;
                if (statusEl.id === 'chat-status') {
                    statusEl.className = `status-indicator status-${statusText.toLowerCase()}`;
                }
            }

            const modelElement = document.getElementById('active-model-name') || document.getElementById('active-model');
            if (modelElement) {
                modelElement.textContent = modelName;
            }

            const modelBadge = document.getElementById('model-status');
            if (modelBadge) {
                modelBadge.textContent = statusText === 'ONLINE' ? '🟢' : '🔴';
            }

            if (Array.isArray(data.available_models)) {
                this.availableModels = data.available_models;
            }
            this.renderDashboardSnapshot();
        } catch (error) {
            console.debug('[ULTRON] Chat status unavailable - app.js:1270', error);
            this.latestLLMStatus = null;
            this.renderDashboardSnapshot();
        }
    }

    async sendChatMessage(messageOverride = null, options = {}) {
        const input = this.dom.chatInput;
        const rawValue = messageOverride !== null && messageOverride !== undefined
            ? messageOverride
            : (input ? input.value : '');
        const message = (rawValue || '').trim();
        if (!message) {
            return;
        }

        if (messageOverride === null && input) {
            input.value = '';
        }

        const userPrefix = typeof options.userLabel === 'string' ? options.userLabel : '';
        const userMessageOptions = {
            prefix: userPrefix,
            avatar: options.userAvatar,
            roleLabel: options.userRole
        };
        this.addUserMessage(message, userMessageOptions);

        const thinkingText = options.thinkingText || 'Thinking…';
        const thinkingMessage = this.appendChatMessage('thinking-message', thinkingText, { returnElement: true });
        try {
            const payload = { message };
            if (options.context) {
                payload.context = options.context;
            }

            const response = await this.apiCall('/api/llm/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                this.removeChatMessage(thinkingMessage);
                this.addErrorMessage(data.error);
                return;
            }
            this.removeChatMessage(thinkingMessage);
            const reply = data.response || data.reply || 'Message received';
            this.addSystemMessage(reply);
            if (data.model) {
                const modelElement = document.getElementById('active-model-name') || document.getElementById('active-model');
                modelElement && (modelElement.textContent = data.model);
            }
            if ((data.tts_enabled && this.voiceEnabled) || options.forceTTS) {
                this.speakText(reply);
            }
            await this.loadLLMChatStatus();
        } catch (error) {
            console.error('[ULTRON] Chat send failed - app.js:1332', error);
            this.removeChatMessage(thinkingMessage);
            this.addErrorMessage('Chat backend unavailable');
        }
    }

    async toggleVoiceChat(forceState) {
        const previousState = Boolean(this.voiceEnabled);
        const desiredState = typeof forceState === 'boolean' ? forceState : !previousState;
        let serverResponse = null;

        try {
            const response = await this.apiCall('/api/voice/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enable: desiredState })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            try {
                serverResponse = await response.json();
            } catch (parseError) {
                console.debug('[ULTRON] Voice toggle JSON parse failed - app.js:1357', parseError);
                serverResponse = {};
            }
        } catch (error) {
            console.debug('[ULTRON] Voice toggle request failed - app.js:1361', error);
            this.addErrorMessage('Voice server toggle failed; keeping previous state.');
            this.voiceEnabled = previousState;
            this.ensureVoiceStatus();
            this.renderDashboardSnapshot();
            return { success: false, voiceEnabled: previousState };
        }

        if (serverResponse && serverResponse.status === 'error') {
            this.addErrorMessage(serverResponse.message || 'Voice server reported an error.');
            this.voiceEnabled = previousState;
            this.ensureVoiceStatus();
            this.renderDashboardSnapshot();
            return { success: false, voiceEnabled: previousState, response: serverResponse };
        }

        const resolvedState = typeof serverResponse?.voice_enabled === 'boolean'
            ? serverResponse.voice_enabled
            : desiredState;

        this.voiceEnabled = Boolean(resolvedState);
        this.latestVoiceStatus = { ...(this.latestVoiceStatus || {}), ...(serverResponse || {}) };
        this.latestVoiceStatus.voice_enabled = this.voiceEnabled;
        this.latestVoiceStatus.status = this.voiceEnabled ? 'enabled' : 'disabled';

        if (this.voiceEnabled) {
            this.startVoiceRecognition();
            this.speakText('Voice chat enabled. I am listening.');
        } else {
            this.stopVoiceRecognition();
            this.stopSpeech();
        }

        this.ensureVoiceStatus();
        this.renderDashboardSnapshot();
        this.addSystemMessage(`Voice chat ${this.voiceEnabled ? 'enabled' : 'disabled'}`);

        return { success: true, voiceEnabled: this.voiceEnabled, response: serverResponse };
    }

    clearChat() {
        if (this.dom.chatMessages) {
            this.dom.chatMessages.innerHTML = '';
        }
        this.addSystemMessage('Chat cleared');
    }

    exportChat() {
        if (!this.dom.chatMessages) {
            return;
        }
        const transcript = Array.from(this.dom.chatMessages.querySelectorAll('.chat-message'))
            .map(node => {
                const label = node.dataset.role || (node.classList.contains('user-message') ? 'You' : node.classList.contains('error-message') ? 'System Alert' : 'ULTRON AI');
                const contentNode = node.querySelector('.message-text');
                const text = (contentNode ? contentNode.textContent : node.textContent || '').trim();
                return `${label}: ${text}`;
            })
            .filter(Boolean)
            .join('\n');
        // Only download if user explicitly requested (prevent auto-download on startup)
        if (this.userRequestedExport) {
            const blob = new Blob([transcript], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `ultron_chat_${Date.now()}.txt`;
            link.click();
            URL.revokeObjectURL(url);
            this.userRequestedExport = false;
        }
    }

    async switchModel() {
        await this.performModelSwitch();
    }

    async performModelSwitch() {
        try {
            if (!Array.isArray(this.availableModels) || !this.availableModels.length) {
                const response = await this.apiCall('/api/llm/models');
                if (response.ok) {
                    const data = await response.json();
                    this.availableModels = data.models || data.available_models || [];
                }
            }

            const modelNames = (this.availableModels || [])
                .map(model => typeof model === 'string' ? model : model?.name)
                .filter(Boolean);

            if (!modelNames.length) {
                this.addErrorMessage('No local models are available from Ollama.');
                return;
            }

            const currentModel = this.latestLLMStatus?.model || modelNames[0];

            // Show custom scrollable modal instead of window.prompt
            const selectedModel = await this.showModelSelectionModal(modelNames, currentModel);

            if (!selectedModel) {
                this.addSystemMessage('Model switch cancelled');
                return;
            }

            const desiredModel = selectedModel.trim();
            if (!desiredModel) {
                this.addErrorMessage('Model switch aborted: empty selection.');
                return;
            }

            const response = await this.apiCall('/api/llm/switch-model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: desiredModel })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            if (result.status !== 'success') {
                this.addErrorMessage(result.message || 'Model switch failed.');
                return;
            }

            this.addSystemMessage(result.message || `Model switched to ${desiredModel}`);
            await this.loadLLMChatStatus();
            this.renderDashboardSnapshot();
        } catch (error) {
            console.error('[ULTRON] Model switch failed - app.js:1493', error);
            this.addErrorMessage('Unable to switch models. Ensure Ollama is running.');
        }
    }

    showModelSelectionModal(modelNames, currentModel) {
        return new Promise((resolve) => {
            // Create modal overlay
            const modal = document.createElement('div');
            modal.className = 'model-select-modal';
            modal.innerHTML = `
                <div class="model-select-content">
                    <div class="model-select-header">
                        <h3>🔄 Select AI Model</h3>
                        <button class="model-close-btn" aria-label="Close">✕</button>
                    </div>
                    <div class="model-select-search">
                        <input type="text" placeholder="🔍 Search models..." class="model-search-input" />
                    </div>
                    <div class="model-select-list">
                        ${modelNames.map(model => `
                            <div class="model-option ${model === currentModel ? 'active' : ''}" data-model="${model}">
                                <span class="model-radio">${model === currentModel ? '●' : '○'}</span>
                                <span class="model-name-text">${model}</span>
                                ${model === currentModel ? '<span class="model-badge">ACTIVE</span>' : ''}
                            </div>
                        `).join('')}
                    </div>
                    <div class="model-select-footer">
                        <button class="model-btn model-btn-cancel">Cancel</button>
                        <button class="model-btn model-btn-confirm">Switch Model</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            let selectedModel = currentModel;

            // Search functionality
            const searchInput = modal.querySelector('.model-search-input');
            const modelOptions = modal.querySelectorAll('.model-option');

            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                modelOptions.forEach(option => {
                    const modelName = option.dataset.model.toLowerCase();
                    option.style.display = modelName.includes(searchTerm) ? 'flex' : 'none';
                });
            });

            // Model selection
            modelOptions.forEach(option => {
                option.addEventListener('click', () => {
                    modelOptions.forEach(opt => {
                        opt.classList.remove('active');
                        opt.querySelector('.model-radio').textContent = '○';
                    });
                    option.classList.add('active');
                    option.querySelector('.model-radio').textContent = '●';
                    selectedModel = option.dataset.model;
                });
            });

            // Close handlers
            const closeModal = (value) => {
                modal.remove();
                resolve(value);
            };

            modal.querySelector('.model-close-btn').addEventListener('click', () => closeModal(null));
            modal.querySelector('.model-btn-cancel').addEventListener('click', () => closeModal(null));
            modal.querySelector('.model-btn-confirm').addEventListener('click', () => closeModal(selectedModel));

            // Close on outside click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal(null);
            });

            // Close on ESC key
            const handleEsc = (e) => {
                if (e.key === 'Escape') {
                    closeModal(null);
                    document.removeEventListener('keydown', handleEsc);
                }
            };
            document.addEventListener('keydown', handleEsc);

            // Focus search input
            searchInput.focus();
        });
    }

    handleQuickAction(prompt) {
        if (!prompt) {
            return;
        }
        this.addSystemMessage(`Quick action: ${prompt}`);
        this.handleConsoleCommand(prompt);
    }

    addUserMessage(message, options = {}) {
        this.appendChatMessage('user-message', message, options);
    }

    addSystemMessage(message, options = {}) {
        this.appendChatMessage('system-message', message, options);
    }

    addErrorMessage(message, options = {}) {
        this.appendChatMessage('error-message', message, options);
    }

    appendChatMessage(cssClass, message, options = {}) {
        if (!this.dom.chatMessages) {
            return;
        }

        const roles = {
            'user-message': { label: 'You', avatar: '🧑' },
            'system-message': { label: 'ULTRON AI', avatar: '🤖' },
            'error-message': { label: 'System Alert', avatar: '⚠️' },
            'thinking-message': { label: 'ULTRON AI', avatar: '🤖' }
        };
        const fallback = roles[cssClass] || { label: 'ULTRON AI', avatar: '🤖' };

        const label = options.roleLabel || fallback.label;
        const avatar = options.avatar || fallback.avatar;
        const prefix = typeof options.prefix === 'string' ? options.prefix : '';
        const safeMessage = typeof message === 'string' ? message : JSON.stringify(message, null, 2);

        const wrapper = document.createElement('div');
        wrapper.className = `chat-message ${cssClass}`;
        wrapper.dataset.role = label;

        const avatarNode = document.createElement('div');
        avatarNode.className = 'message-avatar';
        avatarNode.textContent = avatar;

        const content = document.createElement('div');
        content.className = 'message-content';

        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = label;

        const textNode = document.createElement('div');
        textNode.className = 'message-text';
        textNode.textContent = prefix ? `${prefix}${safeMessage}` : safeMessage;

        const timeNode = document.createElement('div');
        timeNode.className = 'message-time';
        timeNode.textContent = options.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        content.appendChild(header);
        content.appendChild(textNode);
        content.appendChild(timeNode);

        wrapper.appendChild(avatarNode);
        wrapper.appendChild(content);

        this.dom.chatMessages.appendChild(wrapper);
        this.dom.chatMessages.scrollTop = this.dom.chatMessages.scrollHeight;
        if (options.returnElement) {
            return wrapper;
        }
    }

    removeChatMessage(node) {
        if (node && node.parentElement) {
            node.parentElement.removeChild(node);
        }
    }

    ensureVoiceStatus() {
        if (this.dom.voiceStatus) {
            let statusText = 'DISABLED';
            if (this.voiceEnabled) {
                statusText = this.isListening ? 'LISTENING' : 'ENABLED';
            }
            this.dom.voiceStatus.textContent = statusText;
        }
    }

    async toggleVoice() {
        await this.toggleVoiceChat();
    }

    // VOICE RECOGNITION: Browser-based speech-to-text using Web Speech API
    // Dependencies:
    // - Browser must support SpeechRecognition API (Chrome, Edge, Safari)
    // - Microphone permissions must be granted by user
    // - Syncs with backend voice.py for processing transcripts
    startVoiceRecognition() {
        if (this.isListening) {
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.addErrorMessage('Voice recognition is not supported in this browser.');
            this.voiceEnabled = false;
            this.ensureVoiceStatus();
            return;
        }

        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.debug('[ULTRON] Stopping existing recognition failed - app.js:1698', error);
            }
            this.recognition = null;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            this.isListening = true;
            this.shouldRestartRecognition = true;
            this.ensureVoiceStatus();
            this.addSystemMessage('Listening for voice commands…');
        };

        recognition.onresult = (event) => {
            for (let index = event.resultIndex; index < event.results.length; index += 1) {
                const result = event.results[index];
                if (!result || !result.isFinal || !result[0]) {
                    continue;
                }

                const transcript = (result[0].transcript || '').trim();
                if (transcript && transcript.length) {
                    this.handleVoiceTranscript(transcript);
                }
            }
        };

        recognition.onerror = (event) => {
            console.debug('[ULTRON] Voice recognition error - app.js:1730', event);
            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                this.addErrorMessage('Microphone access denied. Voice chat disabled.');
                this.voiceEnabled = false;
                this.shouldRestartRecognition = false;
                this.stopVoiceRecognition(true);
            } else if (event.error !== 'no-speech') {
                this.addErrorMessage(`Voice recognition error: ${event.error}`);
            }
        };

        recognition.onend = () => {
            this.isListening = false;
            this.ensureVoiceStatus();
            if (this.shouldRestartRecognition && this.voiceEnabled) {
                try {
                    recognition.start();
                } catch (error) {
                    console.debug('[ULTRON] Failed to restart recognition - app.js:1748', error);
                }
            }
        };

        try {
            recognition.start();
            this.recognition = recognition;
            this.shouldRestartRecognition = true;
        } catch (error) {
            console.debug('[ULTRON] Unable to start voice recognition - app.js:1758', error);
            this.addErrorMessage('Unable to start voice recognition.');
        }
    }

    stopVoiceRecognition(skipMessage = false) {
        this.shouldRestartRecognition = false;

        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.debug('[ULTRON] Voice recognition stop failed - app.js:1770', error);
            }
            this.recognition = null;
        }

        if (this.isListening) {
            this.isListening = false;
            this.ensureVoiceStatus();
            if (!skipMessage) {
                this.addSystemMessage('Voice recognition stopped');
            }
        }
    }

    async handleVoiceTranscript(transcript) {
        const spokenText = (transcript || '').trim();
        if (!spokenText) {
            return;
        }

        await this.sendChatMessage(spokenText, {
            fromVoice: true,
            thinkingText: 'Processing voice command…',
            userLabel: '🎤 '
        });
    }

    speakText(text) {
        if (!text) {
            return;
        }
        this.ttsQueue.push(text);
        if (!this.isSpeaking) {
            this.dequeueSpeech();
        }
    }

    async dequeueSpeech() {
        if (this.isSpeaking || !this.ttsQueue.length) {
            return;
        }
        const text = this.ttsQueue.shift();
        this.isSpeaking = true;

        // CRITICAL FIX: Capture ORIGINAL listening state before FIRST TTS starts
        // This property persists across all queue items so we know the true starting state
        if (!this.hasOwnProperty('ttsOriginalListeningState')) {
            this.ttsOriginalListeningState = this.isListening;
            console.log(`[ULTRON] DEBUG - Captured ORIGINAL listening state: ${this.ttsOriginalListeningState}`);
        }

        const wasListening = this.ttsOriginalListeningState;
        console.log(`[ULTRON] DEBUG - wasListening: ${wasListening}, voiceEnabled: ${this.voiceEnabled}, isListening: ${this.isListening}, queueLength: ${this.ttsQueue.length}`);

        // CRITICAL FIX: Stop voice recognition IMMEDIATELY to prevent feedback loop
        // The microphone was recording the model's TTS output and looping it back
        // We must completely stop recognition before any audio plays
        if (this.recognition && this.isListening) {
            console.log('[ULTRON] Pausing voice recognition during TTS to prevent feedback loop - app.js:1825');
            this.shouldRestartRecognition = false; // Temporarily prevent auto-restart during TTS
            this.isListening = false;

            try {
                this.recognition.stop();
            } catch (error) {
                console.debug('[ULTRON] Error stopping recognition - app.js:1840', error);
            }
        }        // Additional safeguard: Wait for microphone to fully release
        await new Promise(resolve => setTimeout(resolve, 200));

        try {
            const response = await this.apiCall('/api/voice/speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const blob = await response.blob();

            // Check if we actually got audio data (not just an error response)
            if (blob.size === 0) {
                throw new Error('Empty audio response');
            }

            const audioUrl = URL.createObjectURL(blob);
            this.audioElement = this.audioElement || new Audio();
            this.audioElement.src = audioUrl;

            // Resume voice recognition ONLY AFTER audio completely finishes
            // This prevents the microphone from listening to ULTRON's own speech
            this.audioElement.onended = () => {
                console.log('[ULTRON] TTS playback finished - app.js:1860');
                console.log(`[ULTRON] DEBUG - After TTS: wasListening=${wasListening}, voiceEnabled=${this.voiceEnabled}`);

                // Wait additional time to ensure audio output is fully silent
                setTimeout(() => {
                    console.log(`[ULTRON] DEBUG - Inside setTimeout: wasListening=${wasListening}, voiceEnabled=${this.voiceEnabled}, queueLength=${this.ttsQueue.length}`);

                    // CRITICAL: Process next item in TTS queue first
                    this.isSpeaking = false;
                    if (this.ttsQueue.length > 0) {
                        console.log('[ULTRON] More items in TTS queue, processing next...');
                        this.dequeueSpeech();
                    } else {
                        // Queue is empty - NOW we can resume voice recognition
                        console.log('[ULTRON] TTS queue empty, checking if should resume voice...');
                        delete this.ttsOriginalListeningState; // Clear the saved state

                        if (wasListening && this.voiceEnabled) {
                            console.log('[ULTRON] Resuming voice recognition after TTS - app.js:1864');
                            this.shouldRestartRecognition = true; // Re-enable auto-restart
                            this.startVoiceRecognition();
                        } else {
                            console.log(`[ULTRON] NOT resuming voice - wasListening=${wasListening}, voiceEnabled=${this.voiceEnabled}`);
                        }
                    }
                }, 1000); // 1 second delay to ensure complete audio silence
            };            await this.audioElement.play();
            URL.revokeObjectURL(audioUrl);

            // CRITICAL: Early return prevents dual TTS bug
            // If we don't return here, the finally block will trigger browser TTS
            // causing both ElevenLabs API audio AND browser speech to play simultaneously
            // Dependency: This fix relies on try-catch-finally structure in dequeueSpeech()
            return;

        } catch (error) {
            console.debug('[ULTRON] Voice API unavailable, using browser TTS - app.js:1895', error);

            // Only use browser TTS if API completely failed
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);

                // Resume voice recognition ONLY AFTER speech completely finishes
                utterance.onend = () => {
                    console.log('[ULTRON] Browser TTS finished - app.js:1918');

                    // Wait additional time to ensure audio output is fully silent
                    setTimeout(() => {
                        // CRITICAL: Process next item in TTS queue first
                        this.isSpeaking = false;
                        if (this.ttsQueue.length > 0) {
                            console.log('[ULTRON] More items in TTS queue (browser TTS), processing next...');
                            this.dequeueSpeech();
                        } else {
                            // Queue is empty - NOW we can resume voice recognition
                            console.log('[ULTRON] TTS queue empty (browser TTS), checking if should resume voice...');
                            delete this.ttsOriginalListeningState; // Clear the saved state

                            if (wasListening && this.voiceEnabled) {
                                console.log('[ULTRON] Resuming voice recognition after Web Speech TTS - app.js:1930');
                                this.shouldRestartRecognition = true; // Re-enable auto-restart
                                this.startVoiceRecognition();
                            } else {
                                console.log(`[ULTRON] NOT resuming voice (browser TTS) - wasListening=${wasListening}, voiceEnabled=${this.voiceEnabled}`);
                            }
                        }
                    }, 1000); // 1 second delay to ensure complete audio silence
                };

                window.speechSynthesis.speak(utterance);
                return; // Don't run finally block
            } else {
                // No TTS available, resume voice recognition immediately
                if (wasListening && this.voiceEnabled) {
                    this.startVoiceRecognition();
                }
                // Fall through to finally block to clean up
            }
        } finally {
            // Only runs if both API and browser TTS failed
            this.isSpeaking = false;
            if (this.ttsQueue.length) {
                this.dequeueSpeech();
            }
        }
    }

    stopSpeech() {
        if (this.audioElement) {
            this.audioElement.pause();
            this.audioElement.currentTime = 0;
        }
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
        this.isSpeaking = false;
        this.ttsQueue = [];
    }

    testTTS() {
        this.speakText('This is a test of the Ultron voice system.');
    }

    showElevenLabsTextOverlay() {
        this.dom.elevenLabsOverlay?.classList.remove('hidden');
    }

    hideElevenLabsTextOverlay() {
        this.dom.elevenLabsOverlay?.classList.add('hidden');
    }

    clearElevenLabsOverlay() {
        const input = document.getElementById('elevenlabs-text-input');
        if (input) {
            input.value = '';
        }
    }

    toggleElevenLabsWidget() {
        const widget = document.getElementById('elevenlabs-widget');
        if (widget) {
            widget.classList.toggle('hidden');
        }
    }

    handlePowerAction(action) {
        switch (action) {
            case 'shutdown':
                this.addSystemMessage('Shutdown sequence requested');
                break;
            case 'restart':
                this.addSystemMessage('Restart sequence requested');
                break;
            default:
                this.addErrorMessage('Unknown power action');
        }
    }

    showPowerMenu() {
        // Only show if explicitly called by user (not on startup)
        if (this.powerMenuInitialized !== false) {
            document.getElementById('power-menu')?.classList.remove('hidden');
        }
    }

    hidePowerMenu() {
        document.getElementById('power-menu')?.classList.add('hidden');
    }

    handleDPadInput(direction) {
        this.addSystemMessage(`Direction: ${direction}`);
    }

    handleActionButton(button) {
        this.addSystemMessage(`Button ${button} pressed`);
    }

    handleKeyboardShortcuts(event) {
        if (event.ctrlKey && event.key === 'k') {
            event.preventDefault();
            this.clearConsole();
        }

        // Tab navigation for sections
        if (event.altKey && event.key >= '1' && event.key <= '9') {
            event.preventDefault();
            const sectionIndex = parseInt(event.key) - 1;
            const navButtons = document.querySelectorAll('.nav-button');
            if (navButtons[sectionIndex]) {
                const section = navButtons[sectionIndex].dataset.section;
                this.switchSection(section);
                this.playSound('button');
            }
        }

        // Arrow key navigation for D-pad
        if (!event.ctrlKey && !event.altKey && !event.shiftKey) {
            switch (event.key) {
                case 'ArrowUp':
                    event.preventDefault();
                    this.handleDPadInput('up');
                    this.playSound('button');
                    break;
                case 'ArrowDown':
                    event.preventDefault();
                    this.handleDPadInput('down');
                    this.playSound('button');
                    break;
                case 'ArrowLeft':
                    event.preventDefault();
                    this.handleDPadInput('left');
                    this.playSound('button');
                    break;
                case 'ArrowRight':
                    event.preventDefault();
                    this.handleDPadInput('right');
                    this.playSound('button');
                    break;
                case 'Enter':
                    event.preventDefault();
                    this.handleActionButton('A');
                    this.playSound('confirm');
                    break;
                case 'Escape':
                    event.preventDefault();
                    this.handleActionButton('B');
                    this.playSound('button');
                    break;
            }
        }

        // Voice toggle shortcut
        if (event.ctrlKey && event.key === 'v') {
            event.preventDefault();
            this.toggleVoice();
        }

        // Settings shortcut
        if (event.ctrlKey && event.key === ',') {
            event.preventDefault();
            this.switchSection('settings');
            this.playSound('button');
        }
    }

    announceToScreenReader(message) {
        // Create or update a live region for screen reader announcements
        let liveRegion = document.getElementById('sr-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'sr-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.className = 'sr-only';
            document.body.appendChild(liveRegion);
        }
        liveRegion.textContent = message;

        // Clear the message after a short delay to allow re-announcement
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('ultron_theme') || 'ultron-steampunk';
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = savedTheme;
        }
        this.applyTheme(savedTheme);
    }

    applyTheme(themeName) {
        const body = document.body;
        const pokedexBody = document.getElementById('pokedex-body');

        // Remove all theme classes
        const themeClasses = ['pokedex-red', 'pokedex-blue', 'high-contrast', 'ultron-steampunk'];
        themeClasses.forEach(cls => {
            body.classList.remove(cls);
            if (pokedexBody) pokedexBody.classList.remove(cls);
        });

        // Add new theme class
        body.classList.add(themeName);
        if (pokedexBody) pokedexBody.classList.add(themeName);

        // Save theme preference
        localStorage.setItem('ultron_theme', themeName);
        this.currentTheme = themeName;
        console.log(`[ULTRON] Theme applied: ${themeName} - app.js:2072`);
    }

    trackApiCall(endpoint) {
        if (!this.apiCallCounts) {
            this.apiCallCounts = {};
        }
        this.apiCallCounts[endpoint] = (this.apiCallCounts[endpoint] || 0) + 1;
        console.debug(`[ULTRON] API call: ${endpoint} (count: ${this.apiCallCounts[endpoint]}) - app.js:2080`);
    }

    async apiCall(endpoint, options = {}) {
        this.trackApiCall(endpoint);
        try {
            const response = await fetch(`${this.API_BASE_URL}${endpoint}`, options);
            if (!response.ok) {
                let errorDetail = null;
                const contentType = response.headers.get('content-type') || '';
                try {
                    if (contentType.includes('application/json')) {
                        errorDetail = await response.clone().json();
                    } else {
                        errorDetail = await response.clone().text();
                    }
                } catch (detailError) {
                    console.debug('[ULTRON] Failed to parse error detail - app.js:2097', detailError);
                }

                const error = new Error(`Request to ${endpoint} failed with ${response.status} ${response.statusText}`);
                error.status = response.status;
                error.details = errorDetail;
                throw error;
            }
            return response;
        } catch (error) {
            if (!(error instanceof Error)) {
                throw new Error(String(error));
            }
            throw error;
        }
    }

    destroy() {
        Object.values(this.timers).forEach(timer => clearInterval(timer));
        this.stopSpeech();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.ultronInterface = new UltronPokedexInterface();
    });
} else {
    window.ultronInterface = new UltronPokedexInterface();
}

window.addEventListener('beforeunload', () => {
    window.ultronInterface?.destroy?.();
});
