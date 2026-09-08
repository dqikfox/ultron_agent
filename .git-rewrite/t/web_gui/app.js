/**
 * ULTRON Pokedex AI Interface - Complete JavaScript Controller
 * Authentic Pokedex-style interface for AI system management
 */

class UltronPokedexInterface {
    constructor() {
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
        this.websocket = null;
        this.apiBaseUrl = window.location.origin;

        this.init();
    }

    init() {
        console.log('🚀 Initializing ULTRON Pokedex Interface...');
        this.setupEventListeners();
        this.initializeTheme();
        this.startAnimations();
        this.loadConfiguration();
        this.connectWebSocket();
        this.startSystemMonitoring();
        this.showLoadingScreen();

        // Simulate loading and then show main interface
        setTimeout(() => {
            this.hideLoadingScreen();
            this.checkSystemStatus();
        }, 3000);
    }

    connectWebSocket() {
        const wsUrl = `ws://${window.location.host}/ws`;
        console.log('🔌 Connecting to WebSocket:', wsUrl);

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('✅ WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.requestSystemUpdate();
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.websocket.onclose = () => {
            console.log('🔴 WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);

            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 5000);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'response':
                this.handleCommandResponse(data.data);
                break;
            case 'system_update':
            case 'system_stats':
                this.updateSystemStats(data.data);
                break;
            case 'error':
                this.addSystemMessage(`❌ Error: ${data.message}`);
                break;
            case 'pong':
                console.log('📶 Connection alive');
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    async sendWebSocketMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    async requestSystemUpdate() {
        await this.sendWebSocketMessage({
            type: 'system_request',
            timestamp: Date.now()
        });
    }

    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/status`);
            const data = await response.json();

            console.log('📊 System status:', data);
            this.updateSystemStats(data.system);
            this.updateAgentStatus(data);

        } catch (error) {
            console.error('Failed to check system status:', error);
            this.showNotification('System status check failed', 'error');
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
                settings: '🔧 CONFIG'
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
        }
    }

    handleConsoleCommand(command) {
        if (!command.trim()) return;

        // Add user message
        this.addUserMessage(command);

        // Process command through API
        this.processCommand(command);
    }

    async processCommand(command) {
        const lowerCommand = command.toLowerCase().trim();

        // Local commands that don't need API
        if (lowerCommand === 'clear') {
            this.clearConsole();
            return;
        }

        if (lowerCommand === 'help') {
            this.addSystemMessage('🤖 ULTRON Command Reference:');
            this.addSystemMessage('• help - Show this help');
            this.addSystemMessage('• status - System status');
            this.addSystemMessage('• tools - List available tools');
            this.addSystemMessage('• clear - Clear console');
            this.addSystemMessage('• theme red/blue - Change theme');
            this.addSystemMessage('• memory - Show memory status');
            this.addSystemMessage('• Any AI query - Talk to ULTRON');
            return;
        }

        if (lowerCommand.startsWith('theme ')) {
            const theme = lowerCommand.split(' ')[1];
            if (theme === 'red' || theme === 'blue') {
                this.currentTheme = theme;
                document.body.className = `theme-${theme}`;
                this.addSystemMessage(`🎨 Theme changed to ${theme}`);
            }
            return;
        }

        // Send command to API
        try {
            this.addSystemMessage('⏳ Processing command...');

            // Use WebSocket if available, otherwise REST API
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                await this.sendWebSocketMessage({
                    type: 'command',
                    data: { command: command },
                    timestamp: Date.now()
                });
            } else {
                // Fallback to REST API
                const response = await fetch(`${this.apiBaseUrl}/api/command`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ command: command })
                });

                const result = await response.json();
                this.handleCommandResponse({
                    success: result.success,
                    data: {
                        response: result.response,
                        command: result.command
                    }
                });
            }
        } catch (error) {
            console.error('Command execution error:', error);
            this.addSystemMessage(`❌ Error: ${error.message}`);
        }
    }

    handleCommandResponse(data) {
        if (data.success) {
            this.addUltronMessage(data.response);
        } else {
            this.addSystemMessage(`❌ Error: ${data.response || 'Command failed'}`);
        }
    }

    // Quick status check
    async showSystemStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/system`);
            const data = await response.json();

            this.addSystemMessage('📊 System Status:');
            this.addSystemMessage(`🖥️ CPU: ${data.cpu.usage.toFixed(1)}%`);
            this.addSystemMessage(`💾 Memory: ${data.memory.usage.toFixed(1)}%`);
            this.addSystemMessage(`💿 Disk: ${data.disk.usage.toFixed(1)}%`);

            if (data.gpu && data.gpu.length > 0) {
                data.gpu.forEach((gpu, i) => {
                    this.addSystemMessage(`🎮 GPU ${i}: ${gpu.memory_usage.toFixed(1)}% | ${gpu.temperature}°C`);
                });
            }

            if (data.agent) {
                this.addSystemMessage(`🤖 Agent: ${data.agent.status}`);
                this.addSystemMessage(`🔧 Tools: ${data.agent.tools_count}`);
            }

        } catch (error) {
            this.addSystemMessage(`❌ Failed to get system status: ${error.message}`);
        }
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

    updateSystemStats(stats) {
        if (!stats) return;

        console.log('📊 Updating system stats:', stats);

        // Update internal stats
        if (stats.cpu) {
            this.systemStats.cpu = Math.round(stats.cpu.usage || stats.cpu || 0);
        }
        if (stats.memory) {
            this.systemStats.memory = Math.round(stats.memory.usage || stats.memory || 0);
        }
        if (stats.disk) {
            this.systemStats.disk = Math.round(stats.disk.usage || stats.disk || 0);
        }

        // Update DOM elements
        this.updateSystemDisplay();
        this.updateProgressBars();
    }

    updateSystemDisplay() {
        // Update system stats in UI
        const cpuElement = document.getElementById('cpu-usage');
        const memoryElement = document.getElementById('memory-usage');
        const diskElement = document.getElementById('disk-usage');

        if (cpuElement) cpuElement.textContent = `${this.systemStats.cpu}%`;
        if (memoryElement) memoryElement.textContent = `${this.systemStats.memory}%`;
        if (diskElement) diskElement.textContent = `${this.systemStats.disk}%`;

        // Update status indicators
        const statusElements = document.querySelectorAll('.status-indicator');
        statusElements.forEach(element => {
            const value = parseInt(element.textContent);
            element.className = 'status-indicator';
            if (value > 80) element.classList.add('critical');
            else if (value > 60) element.classList.add('warning');
            else element.classList.add('normal');
        });
    }

    updateProgressBars() {
        // Update progress bars if they exist
        const cpuBar = document.querySelector('.progress-bar.cpu .progress-fill');
        const memoryBar = document.querySelector('.progress-bar.memory .progress-fill');
        const diskBar = document.querySelector('.progress-bar.disk .progress-fill');

        if (cpuBar) cpuBar.style.width = `${this.systemStats.cpu}%`;
        if (memoryBar) memoryBar.style.width = `${this.systemStats.memory}%`;
        if (diskBar) diskBar.style.width = `${this.systemStats.disk}%`;
    }

    updateAgentStatus(statusData) {
        if (!statusData) return;

        console.log('🤖 Updating agent status:', statusData);

        // Update connection status
        this.isConnected = statusData.agent_available || false;
        this.updateConnectionStatus(this.isConnected);

        // Update agent info display
        const agentStatus = document.getElementById('agent-status');
        if (agentStatus) {
            agentStatus.textContent = statusData.agent_status || 'unknown';
            agentStatus.className = `status ${statusData.agent_status || 'unknown'}`;
        }
    }

    updateConnectionStatus(connected) {
        const connectionIndicator = document.querySelector('.connection-status');
        const statusText = document.getElementById('connection-status-text');

        if (connectionIndicator) {
            connectionIndicator.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        }

        if (statusText) {
            statusText.textContent = connected ? 'CONNECTED' : 'DISCONNECTED';
        }

        // Update network status
        this.systemStats.network = connected ? 'CONNECTED' : 'DISCONNECTED';
    }

    addUltronMessage(message) {
        this.addMessage('agent', message);
        this.playSound('response');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);

        console.log(`📢 Notification (${type}): ${message}`);
    }

    // System monitoring with API
    startSystemMonitoring() {
        // Monitor system stats via WebSocket updates
        setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.sendWebSocketMessage({
                    type: 'ping',
                    timestamp: Date.now()
                });
            }
        }, 30000); // Ping every 30 seconds

        // Fallback API polling if WebSocket fails
        setInterval(async () => {
            if (!this.isConnected) {
                try {
                    await this.checkSystemStatus();
                } catch (error) {
                    console.warn('System status check failed:', error);
                }
            }
        }, 10000); // Check every 10 seconds if disconnected
    }

    addAgentMessage(message) {
        this.addMessage('agent', message);
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
            messageDiv.innerHTML = `
                <span class=\"timestamp\">[${timestamp}]</span>
                <span class=\"message-content\">${content}</span>
            `;
            consoleOutput.appendChild(messageDiv);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
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
            // Execute current selection or enter
            if (this.currentSection === 'console') {
                const input = document.getElementById('console-input');
                if (input && input.value.trim()) {
                    this.handleConsoleCommand(input.value);
                    input.value = '';
                }
            }
        } else if (button === 'B') {
            // Back or cancel
            this.switchSection('console');
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
                    await fetch('/api/power/shutdown', { method: 'POST' });
                } catch (error) {
                    this.addErrorMessage('Shutdown request failed');
                }
                break;
            case 'restart':
                this.addSystemMessage('🔄 Initiating system restart...');
                try {
                    await fetch('/api/power/restart', { method: 'POST' });
                } catch (error) {
                    this.addErrorMessage('Restart request failed');
                }
                break;
            case 'sleep':
                this.addSystemMessage('💤 Entering sleep mode...');
                try {
                    await fetch('/api/power/sleep', { method: 'POST' });
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
            const response = await fetch('/api/vision/capture', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage('✅ Screen captured successfully');

                // Switch to vision section to show result
                this.switchSection('vision');

                // Update vision display
                const visionDisplay = document.getElementById('vision-display');
                if (visionDisplay && data.image_path) {
                    visionDisplay.innerHTML = `
                        <img src=\"${data.image_path}\" alt=\"Screen Capture\" style=\"max-width: 100%; border-radius: 8px;\">
                    `;
                }
            } else {
                this.addErrorMessage('Screen capture failed');
            }
        } catch (error) {
            this.addErrorMessage('Screen capture error: ' + error.message);
        }
    }

    async analyzeVision() {
        this.addSystemMessage('🔍 Analyzing screen...');
        try {
            const response = await fetch('/api/vision/analyze', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage('✅ Analysis complete');
                this.addSystemMessage('👁️ ' + (data.analysis || 'No analysis available'));
            } else {
                this.addErrorMessage('Vision analysis failed');
            }
        } catch (error) {
            this.addErrorMessage('Vision analysis error: ' + error.message);
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

    async updateSystemInfo() {
        try {
            // Try to get real system stats from API
            const response = await fetch('/api/status');
            if (response.ok) {
                const data = await response.json();

                if (data.system) {
                    this.systemStats.cpu = Math.round(data.system.cpu_percent || 0);
                    this.systemStats.memory = Math.round(data.system.memory_percent || 0);
                    this.systemStats.disk = Math.round(data.system.disk_percent || 0);
                    this.systemStats.network = data.agent && data.agent.status === 'online' ? 'CONNECTED' : 'OFFLINE';
                    this.isConnected = data.agent && data.agent.status === 'online';
                }
            } else {
                // Fall back to simulated data
                this.systemStats.cpu = Math.floor(Math.random() * 30) + 10;
                this.systemStats.memory = Math.floor(Math.random() * 40) + 30;
                this.systemStats.disk = Math.floor(Math.random() * 20) + 60;
                this.systemStats.network = 'SIMULATED';
                this.isConnected = false;
            }
        } catch (error) {
            console.warn('System stats API unavailable, using simulated data');
            // Fall back to simulated data
            this.systemStats.cpu = Math.floor(Math.random() * 30) + 10;
            this.systemStats.memory = Math.floor(Math.random() * 40) + 30;
            this.systemStats.disk = Math.floor(Math.random() * 20) + 60;
            this.systemStats.network = 'OFFLINE';
            this.isConnected = false;
        }

        // Update UI elements
        const cpuElement = document.getElementById('cpu-usage');
        const memoryElement = document.getElementById('memory-usage');
        const diskElement = document.getElementById('disk-usage');
        const networkElement = document.getElementById('network-status');

        if (cpuElement) cpuElement.textContent = this.systemStats.cpu + '%';
        if (memoryElement) memoryElement.textContent = this.systemStats.memory + '%';
        if (diskElement) diskElement.textContent = this.systemStats.disk + '%';
        if (networkElement) {
            networkElement.textContent = this.systemStats.network;
            networkElement.className = this.isConnected ? 'status-online' : 'status-offline';
        }

        // Update progress bars
        const cpuBar = document.getElementById('cpu-bar');
        const memoryBar = document.getElementById('memory-bar');
        const diskBar = document.getElementById('disk-bar');

        if (cpuBar) cpuBar.style.width = this.systemStats.cpu + '%';
        if (memoryBar) memoryBar.style.width = this.systemStats.memory + '%';
        if (diskBar) diskBar.style.width = this.systemStats.disk + '%';

        // Update process list
        const processContent = document.querySelector('.process-content');
        if (processContent) {
            processContent.textContent = `
SYSTEM PROCESSES:
• ultron.exe - ${this.systemStats.cpu > 20 ? '15.4%' : '12.4%'} CPU
• chrome.exe - 8.2% CPU
• python.exe - 5.1% CPU
• svchost.exe - 3.8% CPU
• explorer.exe - 2.1% CPU
${this.isConnected ? '• ultron_agent.py - 4.2% CPU' : '• [Agent Offline]'}
            `.trim();
        }
    }

    loadFileSystem() {
        const fileList = document.getElementById('file-list');
        if (fileList) {
            fileList.innerHTML = `
                <div class="file-item">📁 core/</div>
                <div class="file-item">📁 models/</div>
                <div class="file-item">📁 assets/</div>
                <div class="file-item">📁 logs/</div>
                <div class="file-item">📄 config.json</div>
                <div class="file-item">📄 ultron_main.py</div>
                <div class="file-item">📄 README.md</div>
            `;
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

    startAnimations() {
        // LED animations
        this.animateMainLED();
        this.animateStatusLEDs();
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
                audio.play().catch(e => console.log('Audio play failed:', e));
            }
        } catch (error) {
            console.log('Sound play error:', error);
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
    console.log('🎮 ULTRON Pokedex Interface loading...');
    window.ultronInterface = new UltronPokedexInterface();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.ultronInterface) {
        window.ultronInterface.destroy();
    }
});
