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
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing ULTRON Pokedex Interface...');
        this.setupEventListeners();
        this.initializeTheme();
        this.startAnimations();
        this.loadConfiguration();
        this.startSystemMonitoring();
        this.showLoadingScreen();
        
        // Simulate loading and then show main interface
        setTimeout(() => {
            this.hideLoadingScreen();
        }, 3000);
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
            
            const response = await fetch('/api/command', {
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

    updateSystemInfo() {
        // Simulate system stats updates
        this.systemStats.cpu = Math.floor(Math.random() * 30) + 10;
        this.systemStats.memory = Math.floor(Math.random() * 40) + 30;
        this.systemStats.disk = Math.floor(Math.random() * 20) + 60;

        // Update UI
        document.getElementById('cpu-usage').textContent = this.systemStats.cpu + '%';
        document.getElementById('memory-usage').textContent = this.systemStats.memory + '%';
        document.getElementById('disk-usage').textContent = this.systemStats.disk + '%';
        document.getElementById('network-status').textContent = this.systemStats.network;

        // Update progress bars
        document.getElementById('cpu-bar').style.width = this.systemStats.cpu + '%';
        document.getElementById('memory-bar').style.width = this.systemStats.memory + '%';
        document.getElementById('disk-bar').style.width = this.systemStats.disk + '%';

        // Update process list
        const processContent = document.querySelector('.process-content');
        if (processContent) {
            processContent.textContent = `
SYSTEM PROCESSES:
• ultron.exe - 12.4% CPU
• chrome.exe - 8.2% CPU  
• python.exe - 5.1% CPU
• svchost.exe - 3.8% CPU
• explorer.exe - 2.1% CPU
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
