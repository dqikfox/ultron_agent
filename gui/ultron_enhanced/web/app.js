/**
 * ULTRON Pokedex AI Interface - Complete JavaScript Controller
 * Authentic Pokedex-style interface for AI system management
 */

class UltronPokedexInterface {
    constructor() {
        // API Configuration
        this.API_BASE_URL = 'http://localhost:8080';
        this.AGENT_BASE_URL = 'http://localhost:8080';

        this.currentSection = 'console';
        this.isListening = false;
        this.currentTheme = 'red';
        this.isConnected = false;
        this.messages = [];
        this.systemStats = {
            cpu: 0,
            memory: 0,
            disk: 0,
            network: 'CONNECTED'
        };
        this.animationIntervals = [];
        this.apiCallCounts = {}; // Track API call attempts

        this.init();
    }

    init() {
           console.log('🚀 Initializing ULTRON Pokedex Interface... - app.js:30');
           console.log(`🔗 API Base URL: ${this.API_BASE_URL} - app.js:31`);
           console.log(`🤖 Agent Base URL: ${this.AGENT_BASE_URL} - app.js:32`);
           this.setupEventListeners();
           this.initializeTheme();
           this.startAnimations();
           this.loadConfiguration();
           this.startSystemMonitoring();
           // Wait for user interaction to start
           this.setupStartButton();
    }

    setupStartButton() {
        const startButton = document.getElementById('start-button');
        if (startButton) {
            startButton.addEventListener('click', () => {
                const startScreen = document.getElementById('start-screen');
                if (startScreen) {
                    startScreen.classList.add('hidden');
                }
                this.hideLoadingScreen();
                const audio = this.playStartupSound();
                if (audio) {
                    audio.play();
                }
            });
        }
    }

    playStartupSound() {
        const elevenlabsApiKey = 'a831a3df8229fdbf27173e8157e558200528564937c55a093e10ff752bf98bed';
        const voiceId = 'e3mik6xHn4Sl51poljxK';
        const text = 'ultron is online';

        const url = `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`;
        const headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': elevenlabsApiKey
        };
        const data = {
            text: text,
            model_id: 'eleven_monolingual_v1',
            voice_settings: {
                stability: 0.5,
                similarity_boost: 0.5
            }
        };

        const audio = document.getElementById('startup-sound');
        if (!audio) return null;

        fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        })
        .then(response => response.blob())
        .then(blob => {
            audio.src = URL.createObjectURL(blob);
        })
        .catch(error => {
            console.error('Error with ElevenLabs API: - app.js:92', error);
        });

        return audio;
    }

    // Speak any text using ElevenLabs TTS
    async speakText(text) {
        if (!text || !text.trim()) return;
        
        const elevenlabsApiKey = 'a831a3df8229fdbf27173e8157e558200528564937c55a093e10ff752bf98bed';
        const voiceId = 'e3mik6xHn4Sl51poljxK';

        const url = `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`;
        const headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': elevenlabsApiKey
        };
        const data = {
            text: text.trim(),
            model_id: 'eleven_monolingual_v1',
            voice_settings: {
                stability: 0.5,
                similarity_boost: 0.5
            }
        };

        try {
            console.log(`[TTS] Speaking: ${text.substring(0, 50)}...`);
            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audio = new Audio(URL.createObjectURL(audioBlob));
                audio.play();
                console.log('[TTS] Audio playback started');
            } else {
                console.error('[TTS] ElevenLabs API error:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('[TTS] Error speaking text:', error);
        }
    }

    // Helper method to make API calls with proper URL and logging
    async apiCall(endpoint, options = {}) {
        const url = `${this.API_BASE_URL}${endpoint}`;
        console.log(`[API Call] ${url} - app.js:101`, options);
        try {
            const response = await fetch(url, options);
            console.log(`[API Response] ${url}  Status: ${response.status} - app.js:104`);
            return response;
        } catch (error) {
            console.error(`[API Error] ${url} - app.js:107`, error);
            throw error;
        }
    }

    showLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        const mainInterface = document.getElementById('main-interface');

        if (loadingScreen) loadingScreen.classList.remove('hidden');
        if (mainInterface) mainInterface.classList.add('hidden');

        // Animate loading progress
        const progressBar = document.querySelector('.loading-progress');
        if (progressBar) {
            progressBar.style.width = '0%';
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(progressInterval);
                }
                progressBar.style.width = progress + '%';
            }, 200);
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        const mainInterface = document.getElementById('main-interface');

        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
        }
        if (mainInterface) {
            mainInterface.classList.remove('hidden');
        }

        // Initialize the interface
        this.addSystemMessage('🔴 ULTRON AI System Online');
        this.addSystemMessage('🟢 All systems operational');
        this.addSystemMessage('📡 Awaiting commands...');

        this.playSound('wake');
    }

    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.nav-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
                this.playSound('button');
            });
        });

        // Console input
        const consoleInput = document.getElementById('console-input');
        if (consoleInput) {
            consoleInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleConsoleCommand(e.target.value);
                    e.target.value = '';
                }
            });
        }

        // D-pad controls
        document.querySelectorAll('[data-direction]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const direction = e.currentTarget.dataset.direction;
                this.handleDPadInput(direction);
                this.playSound('button');
            });
        });

        // Action buttons
        document.getElementById('btn-a')?.addEventListener('click', () => {
            this.handleActionButton('A');
            this.playSound('confirm');
        });

        document.getElementById('btn-b')?.addEventListener('click', () => {
            this.handleActionButton('B');
            this.playSound('button');
        });

        // System buttons
        document.getElementById('btn-power')?.addEventListener('click', () => {
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

        // Vision controls
        document.getElementById('capture-btn')?.addEventListener('click', () => {
            this.captureScreen();
        });

        document.getElementById('analyze-btn')?.addEventListener('click', () => {
            this.analyzeVision();
        });

        // Theme selector
        document.getElementById('theme-select')?.addEventListener('change', (e) => {
            this.changeTheme(e.target.value);
        });

        // Voice toggle
        document.getElementById('voice-toggle')?.addEventListener('click', () => {
            this.toggleVoice();
        });

        // Power menu
        document.querySelectorAll('.power-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handlePowerAction(action);
            });
        });

        // Close power menu when clicking outside
        document.getElementById('power-menu')?.addEventListener('click', (e) => {
            if (e.target.id === 'power-menu') {
                this.hidePowerMenu();
            }
        });

        // AutoGen Studio event listeners
        document.getElementById('start-autogen-btn')?.addEventListener('click', () => {
            this.startAutoGenStudio();
        });

        document.getElementById('stop-autogen-btn')?.addEventListener('click', () => {
            this.stopAutoGenStudio();
        });

        document.getElementById('refresh-autogen-btn')?.addEventListener('click', () => {
            this.refreshAutoGenStatus();
        });

        document.getElementById('open-autogen-btn')?.addEventListener('click', () => {
            this.openAutoGenStudio();
        });

        document.getElementById('create-agent-btn')?.addEventListener('click', () => {
            this.createAutoGenAgent();
        });

        document.getElementById('create-workflow-btn')?.addEventListener('click', () => {
            this.createAutoGenWorkflow();
        });

        // LLM Chat event listeners
        document.getElementById('send-chat-btn')?.addEventListener('click', () => {
            this.sendChatMessage();
        });

        document.getElementById('voice-chat-btn')?.addEventListener('click', () => {
            this.toggleVoiceChat();
        });

        document.getElementById('clear-chat-btn')?.addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('export-chat-btn')?.addEventListener('click', () => {
            this.exportChat();
        });

        document.getElementById('switch-model-btn')?.addEventListener('click', () => {
            this.switchModel();
        });

        // Chat input enter key
        document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendChatMessage();
            }
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prompt = e.currentTarget.dataset.prompt;
                this.handleQuickAction(prompt);
            });
        });

        // Tools Integration event listeners
        document.getElementById('refresh-tools-btn')?.addEventListener('click', () => {
            this.refreshTools();
        });

        document.getElementById('reload-tools-btn')?.addEventListener('click', () => {
            this.reloadAllTools();
        });

        document.getElementById('test-tools-btn')?.addEventListener('click', () => {
            this.testAllTools();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section=\"${sectionName}\"]`)?.classList.add('active');

        // Update section content
        document.querySelectorAll('.section-content').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`)?.classList.add('active');

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
                nvidia: '🎯 NVIDIA'
            };
            indicator.textContent = icons[sectionName] || '🖥️ CONSOLE';
        }

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    async loadSectionData(section) {
        switch (section) {
            case 'system':
                this.updateSystemInfo();
                break;
            case 'files':
                this.loadFileSystem();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'vision':
                this.loadVisionSystem();
                break;
            case 'profile':
                this.loadProfileData();
                break;
            case 'dashboard':
                this.loadSystemInfo();
                break;
            case 'nvidia':
                this.loadNvidiaStatus();
                break;
            case 'autogen':
                this.loadAutoGenStatus();
                break;
            case 'llm-chat':
                this.loadLLMChatStatus();
                break;
            case 'tools':
                this.loadToolsStatus();
                break;
        }
    }

    handleConsoleCommand(command) {
        if (!command.trim()) return;

        // Add user message
        this.addUserMessage(command);

        // Process command
        this.processCommand(command);
    }

    async processCommand(command) {
        const lowerCommand = command.toLowerCase().trim();

        // Local commands
        if (lowerCommand === 'help') {
            this.addSystemMessage('Available commands:');
            this.addSystemMessage('• help - Show this help');
            this.addSystemMessage('• status - System status');
            this.addSystemMessage('• clear - Clear console');
            this.addSystemMessage('• theme red/blue - Change theme');
            this.addSystemMessage('• capture - Take screenshot');
            this.addSystemMessage('• analyze - Analyze screen');
            this.addSystemMessage('• shutdown - Shutdown system');
            this.addSystemMessage('• restart - Restart system');
            return;
        }

        if (lowerCommand === 'clear') {
            this.clearConsole();
            return;
        }

        if (lowerCommand === 'status') {
            this.addSystemMessage(`CPU: ${this.systemStats.cpu}%`);
            this.addSystemMessage(`Memory: ${this.systemStats.memory}%`);
            this.addSystemMessage(`Disk: ${this.systemStats.disk}%`);
            this.addSystemMessage(`Network: ${this.systemStats.network}`);
            return;
        }

        if (lowerCommand.startsWith('theme ')) {
            const theme = lowerCommand.split(' ')[1];
            if (theme === 'red' || theme === 'blue') {
                this.changeTheme(theme);
                this.addSystemMessage(`Theme changed to ${theme}`);
            } else {
                this.addErrorMessage('Invalid theme. Use \"red\" or \"blue\"');
            }
            return;
        }

        if (lowerCommand === 'capture') {
            this.captureScreen();
            return;
        }

        if (lowerCommand === 'analyze') {
            this.analyzeVision();
            return;
        }

        if (lowerCommand === 'shutdown') {
            this.addSystemMessage('⚠️ Shutdown command received');
            this.addSystemMessage('Use the power button for shutdown options');
            return;
        }

        if (lowerCommand === 'restart') {
            this.addSystemMessage('⚠️ Restart command received');
            this.addSystemMessage('Use the power button for restart options');
            return;
        }

        // Try to send to backend
        try {
            this.addSystemMessage('🔄 Processing command...');

            // Track API call
            this.trackApiCall('/api/command');

            const response = await fetch(`${this.API_BASE_URL}/api/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.addSystemMessage(data.response || 'Command executed successfully');
                } else {
                    this.addErrorMessage(data.error || 'Command failed');
                }
            } else {
                this.addErrorMessage('Backend communication failed');
            }
        } catch (error) {
            this.addErrorMessage('🚫 Backend offline - Local command processing only');
        }
    }

    addSystemMessage(message) {
        this.addMessage('system', message);
    }

    addUserMessage(message) {
        this.addMessage('user', message);
    }

    addErrorMessage(message) {
        this.addMessage('error', message);
    }

    addMessage(type, content) {
        const timestamp = new Date().toLocaleTimeString();
        const message = { type, content, timestamp };
        this.messages.push(message);

        const consoleOutput = document.getElementById('console-output');
        if (consoleOutput) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            // Sanitize content to prevent XSS
            const sanitizedContent = this.sanitizeHTML(content);
            messageDiv.innerHTML = `
                <span class=\"timestamp\">[${timestamp}]</span>
                <span class=\"message-content\">${sanitizedContent}</span>
            `;
            consoleOutput.appendChild(messageDiv);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    }

    sanitizeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    clearConsole() {
        this.messages = [];
        const consoleOutput = document.getElementById('console-output');
        if (consoleOutput) {
            consoleOutput.innerHTML = '';
        }
        this.addSystemMessage('Console cleared');
    }

    handleDPadInput(direction) {
        // Navigate between sections with D-pad
        const sections = ['console', 'system', 'vision', 'tasks', 'files', 'settings'];
        const currentIndex = sections.indexOf(this.currentSection);

        let newIndex = currentIndex;
        switch (direction) {
            case 'up':
                newIndex = Math.max(0, currentIndex - 3);
                break;
            case 'down':
                newIndex = Math.min(sections.length - 1, currentIndex + 3);
                break;
            case 'left':
                newIndex = Math.max(0, currentIndex - 1);
                break;
            case 'right':
                newIndex = Math.min(sections.length - 1, currentIndex + 1);
                break;
        }

        if (newIndex !== currentIndex) {
            this.switchSection(sections[newIndex]);
        }
    }

    handleActionButton(button) {
        if (button === 'A') {
            // Dashboard - Show system overview and stats
            this.switchSection('dashboard');
            this.addSystemMessage('📊 Opening Dashboard...');
            this.updateSystemStats();
        } else if (button === 'B') {
            // Nvidia Interface - Show AI/ML controls and NVIDIA integration
            this.switchSection('nvidia');
            this.addSystemMessage('🎯 Opening NVIDIA Interface...');
            this.loadNvidiaStatus();
        }
    }

    showPowerMenu() {
        const powerMenu = document.getElementById('power-menu');
        if (powerMenu) {
            powerMenu.classList.remove('hidden');
        }
    }

    hidePowerMenu() {
        const powerMenu = document.getElementById('power-menu');
        if (powerMenu) {
            powerMenu.classList.add('hidden');
        }
    }

    async handlePowerAction(action) {
        this.hidePowerMenu();

        switch (action) {
            case 'shutdown':
                this.addSystemMessage('🔴 Initiating system shutdown...');
                try {
                    await this.apiCall('/api/power/shutdown', { method: 'POST' });
                } catch (error) {
                    this.addErrorMessage('Shutdown request failed');
                }
                break;
            case 'restart':
                this.addSystemMessage('🔄 Initiating system restart...');
                try {
                    await this.apiCall('/api/power/restart', { method: 'POST' });
                } catch (error) {
                    this.addErrorMessage('Restart request failed');
                }
                break;
            case 'sleep':
                this.addSystemMessage('💤 Entering sleep mode...');
                try {
                    await this.apiCall('/api/power/sleep', { method: 'POST' });
                } catch (error) {
                    this.addErrorMessage('Sleep request failed');
                }
                break;
            case 'cancel':
                this.addSystemMessage('Power operation cancelled');
                break;
        }
    }

    changeTheme(theme) {
        const pokedexBody = document.getElementById('pokedex-body');
        if (pokedexBody) {
            pokedexBody.className = `pokedex-body pokedex-${theme}`;
        }
        this.currentTheme = theme;

        // Update theme selector
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = theme;
        }
    }

    async captureScreen() {
        this.addSystemMessage('📷 Capturing screen...');
        try {
            const response = await this.apiCall('/api/vision/capture', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage('✅ Screen captured successfully');

                // Switch to vision section to show result
                this.switchSection('vision');

                // Update vision display with screenshot and OCR text
                const visionDisplay = document.getElementById('vision-display');
                if (visionDisplay && data.image_path) {
                    visionDisplay.innerHTML = `
                        <div class="vision-result">
                            <img src="${data.image_path}" alt="Screen Capture" style="max-width: 100%; border-radius: 8px; margin-bottom: 1rem;">
                            <div class="ocr-text" style="background: rgba(0,0,0,0.8); padding: 1rem; border-radius: 8px; color: #00ff41; font-family: monospace; white-space: pre-wrap;">
                                <h4>OCR Text:</h4>
                                <p>${data.ocr_text || 'No text detected'}</p>
                            </div>
                        </div>
                    `;
                }
            } else {
                this.addErrorMessage('Screen capture failed');
            }
        } catch (error) {
            this.addErrorMessage('Screen capture error: ' + error.message);
        }
    }

    async updateSystemStats() {
        try {
            const response = await this.apiCall('/api/status');
            if (response.ok) {
                const data = await response.json();
                this.systemStats.cpu = data.system.cpu_percent;
                this.systemStats.memory = data.system.memory_percent;
                this.systemStats.disk = data.system.disk_percent;
                this.updateStatsDisplay();
            }
        } catch (error) {
            console.error('Failed to update system stats: - app.js:694', error);
        }
    }

    updateStatsDisplay() {
        // Update CPU display
        const cpuDisplay = document.getElementById('cpu-display');
        if (cpuDisplay) {
            cpuDisplay.textContent = `${this.systemStats.cpu.toFixed(1)}%`;
        }

        // Update Memory display
        const memDisplay = document.getElementById('memory-display');
        if (memDisplay) {
            memDisplay.textContent = `${this.systemStats.memory.toFixed(1)}%`;
        }

        // Update Disk display
        const diskDisplay = document.getElementById('disk-display');
        if (diskDisplay) {
            diskDisplay.textContent = `${this.systemStats.disk.toFixed(1)}%`;
        }
    }

    async loadNvidiaStatus() {
        try {
            const response = await this.apiCall('/api/nvidia/status');
            if (response.status === 200) {
                const data = await response.json();
                this.addSystemMessage('🎯 NVIDIA Status: ' + (data.status || 'Available'));
                if (data.models) {
                    this.addSystemMessage('🤖 Available Models: ' + data.models.length);
                }
                // Update UI with NVIDIA data
                this.updateNvidiaUI(data);
            } else {
                this.addSystemMessage('⚠️ NVIDIA service not available');
            }
        } catch (error) {
            this.addSystemMessage('⚠️ NVIDIA integration offline');
        }
    }

    updateNvidiaUI(data) {
        // Update NVIDIA metrics
        const metricsElement = document.getElementById('nvidia-metrics');
        if (metricsElement && data.system) {
            metricsElement.innerHTML = `
                <div class="metric">
                    <span class="metric-label">GPU Memory:</span>
                    <span class="metric-value">${data.system.memory_used || 'N/A'} / ${data.system.memory_total || 'N/A'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Temperature:</span>
                    <span class="metric-value">${data.system.temperature || 'N/A'}°C</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">${data.status || 'Unknown'}</span>
                </div>
            `;
        }

        // Update model list
        const modelListElement = document.getElementById('model-list');
        if (modelListElement && data.models) {
            modelListElement.innerHTML = data.models.map(model =>
                `<div class="model-item">${model.name || model}</div>`
            ).join('');
        }
    }

    toggleVoice() {
        this.isListening = !this.isListening;
        const voiceBtn = document.getElementById('voice-toggle');
        if (voiceBtn) {
            voiceBtn.textContent = this.isListening ? '🎤 Disable' : '🎤 Enable';
        }

        if (this.isListening) {
            this.addSystemMessage('🎤 Voice recognition enabled');
        } else {
            this.addSystemMessage('🔇 Voice recognition disabled');
        }
    }

    toggleSound() {
        // Toggle sound on/off
        this.addSystemMessage('🔊 Sound toggled');
    }

    async loadSystemInfo() {
        try {
            const response = await this.apiCall('/api/status');
            if (response.ok) {
                const data = await response.json();

                // Update dashboard metrics
                const overallStatus = document.getElementById('overall-status');
                if (overallStatus) {
                    overallStatus.textContent = data.overall_status.toUpperCase();
                    overallStatus.className = data.overall_status === 'operational' ? 'status-operational' : 'status-degraded';
                }

                const agentStatus = document.getElementById('agent-status');
                if (agentStatus && data.agent) {
                    agentStatus.textContent = data.agent.status.toUpperCase();
                }

                const systemUptime = document.getElementById('system-uptime');
                if (systemUptime && data.agent) {
                    systemUptime.textContent = data.agent.uptime;
                }

                this.addSystemMessage('📊 Dashboard updated with latest system information');
            }
        } catch (error) {
            console.error('Failed to load system info: - app.js:811', error);
            this.addErrorMessage('Failed to load dashboard information');
        }
    }

    async loadFileSystem() {
        const fileList = document.getElementById('file-list');
        if (fileList) {
            try {
                const response = await this.apiCall('/api/files');
                if (response.ok) {
                    const data = await response.json();
                    if (data.files) {
                        fileList.innerHTML = data.files.map(file => `
                            <div class="file-item">${file.is_dir ? '📁' : '📄'} ${file.name}</div>
                        `).join('');
                    } else {
                        fileList.innerHTML = '<div class="file-item">Error loading files</div>';
                    }
                } else {
                    fileList.innerHTML = '<div class="file-item">Error loading files</div>';
                }
            } catch (error) {
                fileList.innerHTML = '<div class="file-item">Error loading files</div>';
            }
        }
    }

    loadTasks() {
        const taskList = document.getElementById('task-list');
        if (taskList) {
            taskList.innerHTML = `
                <div class="task-item">✅ System initialization complete</div>
                <div class="task-item">🔄 Voice recognition standby</div>
                <div class="task-item">🔄 Vision system monitoring</div>
                <div class="task-item">⏸️ Scheduled maintenance</div>
            `;
        }
    }

    loadVisionSystem() {
        const visionDisplay = document.getElementById('vision-display');
        if (visionDisplay) {
            visionDisplay.innerHTML = `
                <div class="vision-placeholder">
                    Vision system ready<br>
                    Click CAPTURE to take screenshot<br>
                    Click ANALYZE to process current view
                </div>
            `;
        }
    }

    loadProfileData() {
        // Profile data is static for now, but could be loaded from backend
        // Update any dynamic elements if needed
        const profileName = document.querySelector('.profile-name');
        const profileEmail = document.querySelector('.profile-email');
        const profileStatus = document.querySelector('.profile-status .status-online');

        if (profileName) profileName.textContent = 'ULTRON Agent';
        if (profileEmail) profileEmail.textContent = 'ultron.agent@example.com';
        if (profileStatus) profileStatus.textContent = 'Online';

        // Set up event listeners for profile buttons
        this.setupProfileEventListeners();
    }

    setupProfileEventListeners() {
        // Edit Profile button
        document.getElementById('edit-profile-btn')?.addEventListener('click', () => {
            this.addSystemMessage('📝 Profile edit feature coming soon');
            this.playSound('button');
        });

        // Export Data button
        document.getElementById('export-data-btn')?.addEventListener('click', () => {
            this.addSystemMessage('📦 Data export feature coming soon');
            this.playSound('button');
        });

        // Reset System button
        document.getElementById('reset-system-btn')?.addEventListener('click', () => {
            this.addSystemMessage('⚠️ System reset requested');
            this.addSystemMessage('Use the power menu for system reset options');
            this.playSound('button');
        });
    }

    // AutoGen Studio Methods
    async loadAutoGenStatus() {
        try {
            const response = await this.apiCall('/api/autogen/status');
            if (response.ok) {
                const data = await response.json();
                this.updateAutoGenUI(data);
                this.addAutoGenMessage('system', 'AutoGen Studio status loaded');
            } else {
                this.addAutoGenMessage('error', 'Failed to load AutoGen Studio status');
            }
        } catch (error) {
            this.addAutoGenMessage('error', 'AutoGen Studio service unavailable');
        }
    }

    updateAutoGenUI(data) {
        // Update status
        const statusElement = document.getElementById('autogen-status');
        if (statusElement) {
            statusElement.textContent = data.status || 'Unknown';
            statusElement.className = data.status === 'running' ? 'status-running' : 'status-stopped';
        }

        // Update port
        const portElement = document.getElementById('autogen-port');
        if (portElement) {
            portElement.textContent = data.port || '8081';
        }

        // Update sessions
        const sessionsElement = document.getElementById('autogen-sessions');
        if (sessionsElement) {
            sessionsElement.textContent = data.active_sessions || '0';
        }

        // Update agents list
        const agentListElement = document.getElementById('agent-list');
        if (agentListElement && data.agents) {
            agentListElement.innerHTML = data.agents.map(agent =>
                `<div class="agent-item">${agent.name || agent}</div>`
            ).join('') || '<div class="agent-item">No agents available</div>';
        }
    }

    async startAutoGenStudio() {
        this.addAutoGenMessage('system', 'Starting AutoGen Studio...');
        try {
            const response = await this.apiCall('/api/autogen/start', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addAutoGenMessage('system', 'AutoGen Studio started successfully');
                setTimeout(() => this.loadAutoGenStatus(), 2000);
            } else {
                this.addAutoGenMessage('error', 'Failed to start AutoGen Studio');
            }
        } catch (error) {
            this.addAutoGenMessage('error', 'Error starting AutoGen Studio: ' + error.message);
        }
    }

    async stopAutoGenStudio() {
        this.addAutoGenMessage('system', 'Stopping AutoGen Studio...');
        try {
            const response = await this.apiCall('/api/autogen/stop', { method: 'POST' });
            if (response.ok) {
                this.addAutoGenMessage('system', 'AutoGen Studio stopped successfully');
                setTimeout(() => this.loadAutoGenStatus(), 1000);
            } else {
                this.addAutoGenMessage('error', 'Failed to stop AutoGen Studio');
            }
        } catch (error) {
            this.addAutoGenMessage('error', 'Error stopping AutoGen Studio: ' + error.message);
        }
    }

    async refreshAutoGenStatus() {
        this.addAutoGenMessage('system', 'Refreshing AutoGen Studio status...');
        await this.loadAutoGenStatus();
    }

    openAutoGenStudio() {
        const portElement = document.getElementById('autogen-port');
        const port = portElement ? portElement.textContent : '8081';
        const url = `http://localhost:${port}`;
        window.open(url, '_blank');
        this.addAutoGenMessage('system', `Opening AutoGen Studio at ${url}`);
    }

    async createAutoGenAgent() {
        this.addAutoGenMessage('system', 'Creating new AutoGen agent...');
        try {
            const response = await this.apiCall('/api/autogen/create-agent', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addAutoGenMessage('system', `Agent created: ${data.agent_name || 'New Agent'}`);
                setTimeout(() => this.loadAutoGenStatus(), 1000);
            } else {
                this.addAutoGenMessage('error', 'Failed to create agent');
            }
        } catch (error) {
            this.addAutoGenMessage('error', 'Error creating agent: ' + error.message);
        }
    }

    async createAutoGenWorkflow() {
        this.addAutoGenMessage('system', 'Creating new AutoGen workflow...');
        try {
            const response = await this.apiCall('/api/autogen/create-workflow', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addAutoGenMessage('system', `Workflow created: ${data.workflow_name || 'New Workflow'}`);
                setTimeout(() => this.loadAutoGenStatus(), 1000);
            } else {
                this.addAutoGenMessage('error', 'Failed to create workflow');
            }
        } catch (error) {
            this.addAutoGenMessage('error', 'Error creating workflow: ' + error.message);
        }
    }

    async handleAutoGenCommand(command) {
        this.addAutoGenMessage('user', `Executing: ${command}`);
        try {
            const response = await this.apiCall('/api/autogen/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            });
            if (response.ok) {
                const data = await response.json();
                this.addAutoGenMessage('system', data.response || 'Command executed successfully');
                setTimeout(() => this.loadAutoGenStatus(), 1000);
            } else {
                this.addAutoGenMessage('error', 'Command execution failed');
            }
        } catch (error) {
            this.addAutoGenMessage('error', 'Error executing command: ' + error.message);
        }
    }

    addAutoGenMessage(type, content) {
        const timestamp = new Date().toLocaleTimeString();
        const outputElement = document.getElementById('autogen-output');
        if (outputElement) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `output-message ${type}-message`;
            messageDiv.innerHTML = `
                <span class="timestamp">[${timestamp}]</span>
                <span class="message-content">${content}</span>
            `;
            const contentElement = outputElement.querySelector('.output-content');
            if (contentElement) {
                contentElement.appendChild(messageDiv);
                contentElement.scrollTop = contentElement.scrollHeight;
            }
        }
    }

    // LLM Chat Methods
    async loadLLMChatStatus() {
        try {
            const response = await this.apiCall('/api/llm/status');
            if (response.ok) {
                const data = await response.json();
                this.updateLLMStatus(data);
            } else {
                this.updateLLMStatus({ model: 'Unknown', status: 'Offline' });
            }
        } catch (error) {
            this.updateLLMStatus({ model: 'Error', status: 'Offline' });
        }
    }

    updateLLMStatus(data) {
        const modelElement = document.getElementById('active-model');
        const statusElement = document.getElementById('model-status');

        if (modelElement) {
            modelElement.textContent = data.model || 'Loading...';
        }

        if (statusElement) {
            const status = data.status || 'Unknown';
            statusElement.textContent = status === 'online' ? '🟢' : status === 'busy' ? '🟡' : '🔴';
            statusElement.title = status;
        }
    }

    async sendChatMessage() {
        const inputElement = document.getElementById('chat-input');
        if (!inputElement || !inputElement.value.trim()) return;

        const message = inputElement.value.trim();
        inputElement.value = '';

        // Add user message
        this.addChatMessage('user', message, 'You');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Create AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 130000); // 130 seconds (10s more than server)

            const response = await this.apiCall('/api/llm/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Hide typing indicator
            this.hideTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                this.addChatMessage('system', data.response || 'No response', 'ULTRON AI');
                
                // Speak the AI response using ElevenLabs TTS
                if (data.response && data.response.trim()) {
                    this.speakText(data.response);
                }
                
                // Legacy audio data support (if server sends audio)
                if (data.audio_data) {
                    const audioData = new Uint8Array(data.audio_data.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
                    const audioBlob = new Blob([audioData], { type: 'audio/mpeg' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    audio.play();
                }
            } else {
                this.addChatMessage('error', 'Failed to get response from AI', 'System');
            }
        } catch (error) {
            this.hideTypingIndicator();

            if (error.name === 'AbortError') {
                this.addChatMessage('error', 'Request timed out. The AI model is taking too long to respond. Try again or switch to a faster model.', 'System');
            } else {
                this.addChatMessage('error', 'Error communicating with AI: ' + error.message, 'System');
            }
        }
    }

    addChatMessage(type, content, sender) {
        const messagesElement = document.getElementById('chat-messages');
        if (!messagesElement) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}-message`;

        const timestamp = new Date().toLocaleTimeString();
        const avatar = type === 'user' ? '👤' : type === 'error' ? '⚠️' : '🤖';

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-header">${sender}</div>
                <div class="message-text">${content}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;

        messagesElement.appendChild(messageDiv);
        messagesElement.scrollTop = messagesElement.scrollHeight;
    }

    showTypingIndicator() {
        const messagesElement = document.getElementById('chat-messages');
        if (!messagesElement) return;

        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'chat-message system-message typing-indicator';
        indicatorDiv.id = 'typing-indicator';
        indicatorDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-header">ULTRON AI</div>
                <div class="message-text">Typing...</div>
            </div>
        `;

        messagesElement.appendChild(indicatorDiv);
        messagesElement.scrollTop = messagesElement.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    toggleVoiceChat() {
        this.isListening = !this.isListening;
        const voiceBtn = document.getElementById('voice-chat-btn');

        if (this.isListening) {
            if (voiceBtn) {
                voiceBtn.innerHTML = '<span>🎙️</span> Listening...';
                voiceBtn.style.background = 'linear-gradient(145deg, #dc2626, #b91c1c)';
            }
            this.addChatMessage('system', 'Voice input activated. Speak your message.', 'System');
            // Start voice recognition
            this.startVoiceRecognition();
        } else {
            if (voiceBtn) {
                voiceBtn.innerHTML = '<span>🎤</span> Voice';
                voiceBtn.style.background = '';
            }
            this.addChatMessage('system', 'Voice input deactivated.', 'System');
            // Stop voice recognition
            this.stopVoiceRecognition();
        }
    }

    startVoiceRecognition() {
        // Voice recognition implementation
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.addChatMessage('error', 'Voice recognition not supported in this browser.', 'System');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const inputElement = document.getElementById('chat-input');
            if (inputElement) {
                inputElement.value = transcript;
                this.sendChatMessage();
            }
        };

        this.recognition.onerror = (event) => {
            // Handle different error types
            if (event.error === 'no-speech') {
                // Don't deactivate for no-speech - just continue listening
                this.addChatMessage('system', 'No speech detected, continuing to listen...', 'System');
            } else if (event.error === 'audio-capture') {
                this.addChatMessage('error', 'Microphone access denied or not available', 'System');
                this.toggleVoiceChat(); // Turn off voice mode for serious errors
            } else if (event.error === 'not-allowed') {
                this.addChatMessage('error', 'Microphone permission denied', 'System');
                this.toggleVoiceChat(); // Turn off voice mode for permission issues
            } else {
                this.addChatMessage('error', `Voice recognition error: ${event.error}`, 'System');
                // For other errors, continue listening instead of turning off
            }
        };

        this.recognition.onend = () => {
            if (this.isListening) {
                // Restart recognition for continuous listening
                setTimeout(() => {
                    if (this.isListening) {
                        this.recognition.start();
                    }
                }, 1000);
            }
        };

        this.recognition.start();
    }

    stopVoiceRecognition() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    clearChat() {
        const messagesElement = document.getElementById('chat-messages');
        if (messagesElement) {
            messagesElement.innerHTML = '';
            this.addChatMessage('system', 'Chat history cleared.', 'System');
        }
    }

    exportChat() {
        const messages = document.querySelectorAll('.chat-message');
        let chatContent = 'ULTRON AI Chat Export\n';
        chatContent += '=' .repeat(50) + '\n\n';

        messages.forEach(message => {
            const header = message.querySelector('.message-header')?.textContent || '';
            const text = message.querySelector('.message-text')?.textContent || '';
            const time = message.querySelector('.message-time')?.textContent || '';

            chatContent += `[${time}] ${header}: ${text}\n\n`;
        });

        // Create and download file
        const blob = new Blob([chatContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ultron_chat_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.addChatMessage('system', 'Chat exported successfully.', 'System');
    }

    async switchModel() {
        try {
            const response = await this.apiCall('/api/llm/models');
            if (response.ok) {
                const data = await response.json();
                // Show model selection dialog
                this.showModelSelection(data.models);
            } else {
                this.addChatMessage('error', 'Failed to load available models.', 'System');
            }
        } catch (error) {
            this.addChatMessage('error', 'Error loading models: ' + error.message, 'System');
        }
    }

    showModelSelection(models) {
        // Create modal for model selection
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-title">SELECT AI MODEL</div>
                <div class="model-list" style="margin: 2rem 0;">
                    ${models.map(model => `
                        <button class="model-option" data-model="${model.name}" style="
                            display: block;
                            width: 100%;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            background: rgba(0, 255, 65, 0.1);
                            border: 1px solid #00ff41;
                            border-radius: 8px;
                            color: #00ff41;
                            font-family: 'Orbitron', monospace;
                            cursor: pointer;
                            transition: all 0.2s ease;
                        " onmouseover="this.style.background='rgba(0, 255, 65, 0.2)'" onmouseout="this.style.background='rgba(0, 255, 65, 0.1)'">
                            ${model.name} - ${model.description || 'AI Model'}
                        </button>
                    `).join('')}
                </div>
                <div style="text-align: center;">
                    <button class="power-btn" data-action="cancel" style="margin-top: 1rem;">CANCEL</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle model selection
        modal.querySelectorAll('.model-option').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const modelName = e.currentTarget.dataset.model;
                await this.selectModel(modelName);
                document.body.removeChild(modal);
            });
        });

        // Handle cancel
        modal.querySelector('[data-action="cancel"]').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }

    async selectModel(modelName) {
        try {
            const response = await this.apiCall('/api/llm/switch-model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: modelName })
            });

            if (response.ok) {
                this.addChatMessage('system', `Switched to model: ${modelName}`, 'System');
                setTimeout(() => this.loadLLMChatStatus(), 1000);
            } else {
                this.addChatMessage('error', 'Failed to switch model.', 'System');
            }
        } catch (error) {
            this.addChatMessage('error', 'Error switching model: ' + error.message, 'System');
        }
    }

    async handleQuickAction(prompt) {
        const inputElement = document.getElementById('chat-input');
        if (inputElement) {
            inputElement.value = prompt;
            this.addChatMessage('system', `Quick action selected: ${prompt}`, 'System');
        }
    }

    // Tool Integration Methods
    async loadToolsStatus() {
        try {
            const response = await this.apiCall('/api/tools/status');
            if (response.ok) {
                const data = await response.json();
                this.updateToolsUI(data);
            } else {
                this.showToolsError('Failed to load tools status');
            }
        } catch (error) {
            this.showToolsError('Error loading tools: ' + error.message);
        }
    }

    updateToolsUI(data) {
        // Update statistics
        const totalToolsElement = document.getElementById('total-tools');
        const activeToolsElement = document.getElementById('active-tools');
        const toolUsageElement = document.getElementById('tool-usage');

        if (totalToolsElement) totalToolsElement.textContent = data.total || 0;
        if (activeToolsElement) activeToolsElement.textContent = data.active || 0;
        if (toolUsageElement) toolUsageElement.textContent = data.usage || 0;

        // Update tools grid
        this.renderToolsGrid(data.tools || []);
    }

    renderToolsGrid(tools) {
        const toolsGrid = document.getElementById('tools-grid');
        if (!toolsGrid) return;

        if (!tools || tools.length === 0) {
            toolsGrid.innerHTML = `
                <div class="tool-placeholder">
                    <div class="loading-spinner"></div>
                    <p>No tools available</p>
                </div>
            `;
            return;
        }

        const toolsHtml = tools.map(tool => this.createToolCard(tool)).join('');
        toolsGrid.innerHTML = toolsHtml;

        // Add click handlers for tool cards
        toolsGrid.querySelectorAll('.tool-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const toolName = e.currentTarget.dataset.tool;
                this.selectTool(toolName);
            });
        });
    }

    createToolCard(tool) {
        const statusClass = tool.status === 'active' ? 'active' : tool.status === 'loading' ? 'loading' : 'inactive';
        const statusText = tool.status || 'unknown';
        const icon = this.getToolIcon(tool.name);

        return `
            <div class="tool-card" data-tool="${tool.name}">
                <div class="tool-card-header">
                    <div style="display: flex; align-items: center;">
                        <span class="tool-icon">${icon}</span>
                        <span class="tool-name">${tool.name}</span>
                    </div>
                    <span class="tool-status ${statusClass}">${statusText}</span>
                </div>
                <div class="tool-description">${tool.description || 'No description available'}</div>
                <div class="tool-meta">
                    <span>Uses: ${tool.usage_count || 0}</span>
                    <span>Last: ${tool.last_used || 'Never'}</span>
                </div>
            </div>
        `;
    }

    getToolIcon(toolName) {
        const iconMap = {
            'calculator': '🧮',
            'file_tool': '📁',
            'code_analysis': '💻',
            'web_search': '🌐',
            'weather': '🌤️',
            'system_monitor': '⚙️',
            'audio_manager': '🔊',
            'image_generation': '🎨',
            'database': '🗄️',
            'network': '📡',
            'process_management': '🔧',
            'screen_reader': '👁️',
            'system_control': '🎛️',
            'geocode': '📍',
            'blockchain': '⛓️',
            'quantum_computing': '⚛️',
            'pochi': '🐕',
            'autogen_studio': '🤖',
            'openai_tools': '🧠',
            'agent_network': '🌐'
        };

        // Try exact match first
        if (iconMap[toolName]) {
            return iconMap[toolName];
        }

        // Try partial match
        for (const [key, icon] of Object.entries(iconMap)) {
            if (toolName.includes(key)) {
                return icon;
            }
        }

        return '🔧'; // Default tool icon
    }

    async selectTool(toolName) {
        // Update selected tool visual
        document.querySelectorAll('.tool-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-tool="${toolName}"]`).classList.add('selected');

        // Load tool details
        try {
            const response = await this.apiCall(`/api/tools/${toolName}`);
            if (response.ok) {
                const toolData = await response.json();
                this.showToolDetails(toolData);
            } else {
                this.showToolDetails({ name: toolName, error: 'Failed to load tool details' });
            }
        } catch (error) {
            this.showToolDetails({ name: toolName, error: 'Error loading tool details: ' + error.message });
        }
    }

    showToolDetails(tool) {
        const detailsElement = document.getElementById('tool-details');
        if (!detailsElement) return;

        if (tool.error) {
            detailsElement.innerHTML = `
                <div class="tool-info-placeholder">
                    Error: ${tool.error}
                </div>
            `;
            return;
        }

        const icon = this.getToolIcon(tool.name);
        const statusClass = tool.status === 'active' ? 'active' : tool.status === 'loading' ? 'loading' : 'inactive';

        detailsElement.innerHTML = `
            <div class="tool-detail-content">
                <div class="tool-detail-header">
                    <span class="tool-detail-icon">${icon}</span>
                    <div class="tool-detail-info">
                        <h3>${tool.name}</h3>
                        <span class="tool-detail-status ${statusClass}">${tool.status || 'unknown'}</span>
                    </div>
                </div>
                <div class="tool-detail-description">
                    ${tool.description || 'No description available'}
                </div>
                <div class="tool-detail-meta">
                    <div class="tool-detail-meta-item">
                        <h4>Usage Statistics</h4>
                        <p>Total Uses: ${tool.usage_count || 0}</p>
                        <p>Last Used: ${tool.last_used || 'Never'}</p>
                        <p>Success Rate: ${tool.success_rate || 'N/A'}%</p>
                    </div>
                    <div class="tool-detail-meta-item">
                        <h4>Technical Details</h4>
                        <p>Class: ${tool.class_name || 'Unknown'}</p>
                        <p>Module: ${tool.module || 'Unknown'}</p>
                        <p>Version: ${tool.version || 'N/A'}</p>
                    </div>
                    <div class="tool-detail-meta-item">
                        <h4>Parameters</h4>
                        <p>${tool.parameters ? Object.keys(tool.parameters).length : 0} parameters</p>
                        <p>Async: ${tool.is_async ? 'Yes' : 'No'}</p>
                        <p>Requires Config: ${tool.requires_config ? 'Yes' : 'No'}</p>
                    </div>
                </div>
                <div class="tool-detail-actions">
                    <button class="tool-btn" onclick="ultronInterface.testTool('${tool.name}')">🧪 Test Tool</button>
                    <button class="tool-btn" onclick="ultronInterface.reloadTool('${tool.name}')">🔄 Reload</button>
                    <button class="tool-btn" onclick="ultronInterface.executeTool('${tool.name}')">▶️ Execute</button>
                </div>
            </div>
        `;
    }

    async refreshTools() {
        this.addSystemMessage('🔄 Refreshing tools status...');
        await this.loadToolsStatus();
        this.addSystemMessage('✅ Tools status refreshed');
    }

    async reloadAllTools() {
        this.addSystemMessage('⚡ Reloading all tools...');
        try {
            const response = await this.apiCall('/api/tools/reload', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage(`✅ Reloaded ${data.reloaded || 0} tools`);
                await this.loadToolsStatus();
            } else {
                this.addSystemMessage('❌ Failed to reload tools');
            }
        } catch (error) {
            this.addSystemMessage('❌ Error reloading tools: ' + error.message);
        }
    }

    async testAllTools() {
        this.addSystemMessage('🧪 Testing all tools...');
        try {
            const response = await this.apiCall('/api/tools/test', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                const passed = data.results.filter(r => r.passed).length;
                const total = data.results.length;
                this.addSystemMessage(`✅ Tool tests completed: ${passed}/${total} passed`);
                await this.loadToolsStatus();
            } else {
                this.addSystemMessage('❌ Failed to run tool tests');
            }
        } catch (error) {
            this.addSystemMessage('❌ Error testing tools: ' + error.message);
        }
    }

    async testTool(toolName) {
        this.addSystemMessage(`🧪 Testing tool: ${toolName}`);
        try {
            const response = await this.apiCall(`/api/tools/${toolName}/test`, { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                if (data.passed) {
                    this.addSystemMessage(`✅ Tool ${toolName} test passed`);
                } else {
                    this.addSystemMessage(`❌ Tool ${toolName} test failed: ${data.error || 'Unknown error'}`);
                }
                await this.loadToolsStatus();
            } else {
                this.addSystemMessage(`❌ Failed to test tool ${toolName}`);
            }
        } catch (error) {
            this.addSystemMessage(`❌ Error testing tool ${toolName}: ` + error.message);
        }
    }

    async reloadTool(toolName) {
        this.addSystemMessage(`🔄 Reloading tool: ${toolName}`);
        try {
            const response = await this.apiCall(`/api/tools/${toolName}/reload`, { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.addSystemMessage(`✅ Tool ${toolName} reloaded successfully`);
                } else {
                    this.addSystemMessage(`❌ Failed to reload tool ${toolName}: ${data.error || 'Unknown error'}`);
                }
                await this.loadToolsStatus();
            } else {
                this.addSystemMessage(`❌ Failed to reload tool ${toolName}`);
            }
        } catch (error) {
            this.addSystemMessage(`❌ Error reloading tool ${toolName}: ` + error.message);
        }
    }

    async executeTool(toolName) {
        // Show a simple command input dialog
        const command = prompt(`Enter command for ${toolName}:`);
        if (!command || !command.trim()) return;

        this.addSystemMessage(`▶️ Executing ${toolName} with: ${command}`);
        try {
            const response = await this.apiCall(`/api/tools/${toolName}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            });
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage(`✅ Tool ${toolName} executed: ${data.result || 'Success'}`);
            } else {
                this.addSystemMessage(`❌ Tool ${toolName} execution failed`);
            }
        } catch (error) {
            this.addSystemMessage(`❌ Error executing tool ${toolName}: ` + error.message);
        }
    }

    showToolsError(message) {
        const toolsGrid = document.getElementById('tools-grid');
        if (toolsGrid) {
            toolsGrid.innerHTML = `
                <div class="tool-placeholder">
                    <p style="color: #ff4141;">${message}</p>
                </div>
            `;
        }
    }

    startAnimations() {
        // LED animations
        this.animateMainLED();
        this.animateStatusLEDs();
        // Initialize LED status monitoring
        this.initializeLEDStatus();
    }

    initializeLEDStatus() {
        // Initialize LED status labels
        this.updateLEDLabels();
        // Start monitoring system status for LED updates
        this.startLEDStatusMonitoring();
    }

    updateLEDLabels() {
        // Add status labels next to LEDs if they don't exist
        const ledCluster = document.querySelector('.led-cluster');
        if (ledCluster && !document.querySelector('.led-labels')) {
            const labelsDiv = document.createElement('div');
            labelsDiv.className = 'led-labels';
            labelsDiv.innerHTML = `
                <div class="led-label">System Ready</div>
                <div class="led-label">Voice Online</div>
                <div class="led-label">AI Connected</div>
            `;
            ledCluster.appendChild(labelsDiv);
        }
    }

    startLEDStatusMonitoring() {
        // Update LED status every 5 seconds
        const interval = setInterval(() => {
            this.updateLEDStatus();
        }, 5000);
        this.animationIntervals.push(interval);

        // Initial status update
        setTimeout(() => this.updateLEDStatus(), 1000);
    }

    async updateLEDStatus() {
        try {
            // Check system status
            const systemStatus = await this.checkSystemStatus();
            const voiceStatus = await this.checkVoiceStatus();
            const aiStatus = await this.checkAIStatus();

            // Update LEDs based on status
            this.setLEDLight('main-led', systemStatus);
            this.setLEDLight('led-1', voiceStatus);
            this.setLEDLight('led-2', aiStatus);
            this.setLEDLight('led-3', 'operational'); // Reserved for future use

            // Update status labels
            this.updateLEDLabelsText(systemStatus, voiceStatus, aiStatus);

        } catch (error) {
            console.error('Failed to update LED status: - app.js:1755', error);
            // Set all LEDs to error state on failure
            this.setLEDLight('main-led', 'error');
            this.setLEDLight('led-1', 'error');
            this.setLEDLight('led-2', 'error');
            this.setLEDLight('led-3', 'error');
        }
    }

    async checkSystemStatus() {
        try {
            const response = await this.apiCall('/api/status');
            if (response.ok) {
                const data = await response.json();
                return data.overall_status === 'operational' ? 'operational' :
                       data.overall_status === 'degraded' ? 'loading' : 'error';
            }
        } catch (error) {
            console.error('System status check failed: - app.js:1773', error);
        }
        return 'error';
    }

    async checkVoiceStatus() {
        try {
            const response = await this.apiCall('/api/voice/status');
            if (response.ok) {
                const data = await response.json();
                // Check if ElevenLabs and fallback TTS are available
                const elevenlabsOk = data.elevenlabs?.available && data.elevenlabs?.voices > 0;
                const fallbackOk = data.pyttsx3?.available;
                const micOk = data.microphone?.available;

                if (elevenlabsOk && micOk) return 'operational';
                if (fallbackOk && micOk) return 'loading'; // Fallback mode
                if (micOk) return 'loading'; // Basic functionality
                return 'error';
            }
        } catch (error) {
            console.error('Voice status check failed: - app.js:1794', error);
        }
        return 'error';
    }

    async checkAIStatus() {
        try {
            const response = await this.apiCall('/api/brain/status');
            if (response.ok) {
                const data = await response.json();
                // Check if Ollama and models are available
                const ollamaOk = data.ollama?.running;
                const modelsOk = data.models?.length > 0;

                if (ollamaOk && modelsOk) return 'operational';
                if (ollamaOk) return 'loading'; // Ollama running but no models
                return 'error';
            }
        } catch (error) {
            console.error('AI status check failed: - app.js:1813', error);
        }
        return 'error';
    }

    setLEDLight(ledId, status) {
        const led = document.getElementById(ledId);
        if (!led) return;

        // Remove all status classes
        led.classList.remove('led-red', 'led-yellow', 'led-green', 'led-blue');

        // Add appropriate status class
        switch (status) {
            case 'operational':
            case 'online':
            case 'connected':
                led.classList.add('led-green');
                break;
            case 'loading':
            case 'busy':
            case 'initializing':
                led.classList.add('led-yellow');
                break;
            case 'error':
            case 'offline':
            case 'failed':
            default:
                led.classList.add('led-red');
                break;
        }

        // Update glow effect
        this.updateLEDGlow(led, status);
    }

    updateLEDGlow(led, status) {
        const glow = led.querySelector('.led-glow');
        if (!glow) return;

        switch (status) {
            case 'operational':
            case 'online':
            case 'connected':
                glow.style.background = 'radial-gradient(circle at 30% 30%, rgba(22, 163, 74, 0.8), rgba(22, 163, 74, 0.4))';
                glow.style.boxShadow = '0 0 20px rgba(22, 163, 74, 0.8)';
                break;
            case 'loading':
            case 'busy':
            case 'initializing':
                glow.style.background = 'radial-gradient(circle at 30% 30%, rgba(234, 179, 8, 0.8), rgba(234, 179, 8, 0.4))';
                glow.style.boxShadow = '0 0 20px rgba(234, 179, 8, 0.8)';
                break;
            case 'error':
            case 'offline':
            case 'failed':
            default:
                glow.style.background = 'radial-gradient(circle at 30% 30%, rgba(220, 38, 38, 0.8), rgba(220, 38, 38, 0.4))';
                glow.style.boxShadow = '0 0 20px rgba(220, 38, 38, 0.8)';
                break;
        }
    }

    updateLEDLabelsText(systemStatus, voiceStatus, aiStatus) {
        const labels = document.querySelectorAll('.led-label');
        if (labels.length >= 3) {
            // Update system status label
            labels[0].textContent = this.getStatusText('System', systemStatus);
            labels[0].className = `led-label status-${systemStatus}`;

            // Update voice status label
            labels[1].textContent = this.getStatusText('Voice', voiceStatus);
            labels[1].className = `led-label status-${voiceStatus}`;

            // Update AI status label
            labels[2].textContent = this.getStatusText('AI', aiStatus);
            labels[2].className = `led-label status-${aiStatus}`;
        }
    }

    getStatusText(component, status) {
        const statusMap = {
            operational: `${component} Online`,
            online: `${component} Online`,
            connected: `${component} Connected`,
            loading: `${component} Loading`,
            busy: `${component} Busy`,
            initializing: `${component} Init`,
            error: `${component} Error`,
            offline: `${component} Offline`,
            failed: `${component} Failed`
        };
        return statusMap[status] || `${component} Unknown`;
    }

    animateMainLED() {
        const mainLed = document.getElementById('main-led');
        if (mainLed) {
            let glowIntensity = 0;
            const interval = setInterval(() => {
                glowIntensity = (glowIntensity + 0.1) % (Math.PI * 2);
                const opacity = 0.5 + 0.5 * Math.sin(glowIntensity);
                mainLed.style.boxShadow = `0 0 20px rgba(220, 38, 38, ${opacity})`;
            }, 100);
            this.animationIntervals.push(interval);
        }
    }

    animateStatusLEDs() {
        const leds = ['led-1', 'led-2', 'led-3'];
        leds.forEach((id, index) => {
            const led = document.getElementById(id);
            if (led) {
                const interval = setInterval(() => {
                    const shouldBlink = Math.random() > 0.7;
                    led.style.opacity = shouldBlink ? '0.3' : '1';
                }, 1000 + index * 500);
                this.animationIntervals.push(interval);
            }
        });
    }

    startSystemMonitoring() {
        // Update system stats every 2 seconds
        const interval = setInterval(() => {
            if (this.currentSection === 'system') {
                this.updateSystemInfo();
            }
        }, 2000);
        this.animationIntervals.push(interval);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl + Enter for quick command execution
        if (e.ctrlKey && e.key === 'Enter') {
            const input = document.getElementById('console-input');
            if (input && input.value.trim()) {
                this.handleConsoleCommand(input.value);
                input.value = '';
            }
        }

        // Function keys for section switching
        const fKeyMap = {
            'F1': 'console',
            'F2': 'system',
            'F3': 'vision',
            'F4': 'tasks',
            'F5': 'files',
            'F6': 'settings'
        };

        if (fKeyMap[e.key]) {
            e.preventDefault();
            this.switchSection(fKeyMap[e.key]);
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            this.hidePowerMenu();
        }
    }

    loadConfiguration() {
        // Load saved settings from localStorage
        const savedTheme = localStorage.getItem('ultron-theme');
        if (savedTheme) {
            this.changeTheme(savedTheme);
        }
    }

    saveConfiguration() {
        // Save current settings to localStorage
        localStorage.setItem('ultron-theme', this.currentTheme);
    }

    playSound(soundName) {
        try {
            const audio = document.getElementById(`audio-${soundName}`);
            if (audio) {
                audio.currentTime = 0;
                audio.play().catch(e => console.log('Audio play failed: - app.js:1994', e));
            }
        } catch (error) {
            console.log('Sound play error: - app.js:1997', error);
        }
    }

    initializeTheme() {
        // Set initial theme
        this.changeTheme(this.currentTheme);
    }

    destroy() {
        // Clean up intervals when needed
        this.animationIntervals.forEach(interval => clearInterval(interval));
        this.animationIntervals = [];
    }
}

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 ULTRON Pokedex Interface loading... - app.js:2015');
    window.ultronInterface = new UltronPokedexInterface();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.ultronInterface) {
        window.ultronInterface.destroy();
    }
});
