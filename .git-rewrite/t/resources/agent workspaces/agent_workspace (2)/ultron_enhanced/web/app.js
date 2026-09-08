/**
 * ULTRON Pokedex AI Interface - JavaScript Controller
 * Handles UI interactions, communication with backend, and system management
 */

class UltronInterface {
    constructor() {
        this.currentSection = 'console';
        this.isListening = false;
        this.recognition = null;
        this.currentTheme = 'red';
        this.isConnected = false;
        this.messages = [];
        this.tasks = [];
        this.systemStats = {
            cpu: 0,
            memory: 0,
            disk: 0,
            network: 'CONNECTED'
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeTheme();
        this.startAnimations();
        this.setupSpeechRecognition();
        this.loadConfiguration();
        this.startSystemMonitoring();
        
        // Show loading screen initially
        this.showLoadingScreen();
        
        // Wait for backend to be ready
        this.waitForBackendReady();
    }

    async waitForBackendReady() {
        const maxAttempts = 15; // 15 seconds max wait
        let attempts = 0;
        
        console.log('Waiting for ULTRON backend to be ready...');
        
        const checkStatus = async () => {
            try {
                attempts++;
                console.log(`🔍 Checking backend status... attempt ${attempts}/${maxAttempts}`);
                
                // Update loading text with current status
                const loadingText = document.querySelector('.loading-text');
                if (loadingText) {
                    loadingText.textContent = `Connecting to ULTRON Core... (${attempts}/${maxAttempts})`;
                }
                
                // Create a promise that rejects after timeout
                const timeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject(new Error('Request timeout')), 3000);
                });
                
                // Race between fetch and timeout
                const fetchPromise = fetch('/api/status', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                });
                
                const response = await Promise.race([fetchPromise, timeoutPromise]);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('✅ Backend status received:', data);
                    
                    // Verify the response has the expected structure
                    if (data.success !== undefined) {
                        this.onBackendReady(data);
                        return true;
                    } else {
                        console.warn('⚠️ Backend response format unexpected:', data);
                    }
                } else {
                    console.warn(`⚠️ Backend responded with status: ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ Backend not ready: ${error.message}`);
            }
            
            // If we've reached max attempts, proceed in offline mode
            if (attempts >= maxAttempts) {
                console.warn('⏰ Backend status check timed out, proceeding with offline mode');
                this.onBackendReady({ 
                    success: false, 
                    status: { server_running: false }, 
                    message: 'Operating in offline mode' 
                });
                return true;
            }
            
            // Try again in 1 second
            setTimeout(checkStatus, 1000);
            return false;
        };
        
        // Start checking immediately
        checkStatus();
    }

    onBackendReady(statusData) {
        console.log('🚀 Backend ready, initializing interface...', statusData);
        
        // Determine connection status from response
        this.isConnected = statusData.success === true && 
                          statusData.status && 
                          statusData.status.server_running === true;
        
        console.log(`🔗 Connection status: ${this.isConnected ? 'CONNECTED' : 'OFFLINE'}`);
        
        // Hide loading screen with a small delay for smooth transition
        setTimeout(() => {
            this.hideLoadingScreen();
        }, 500);
        
        // Play wake sound (will fallback to generated sound if file missing)
        setTimeout(() => {
            this.playSound('wake');
        }, 800);
        
        // Add welcome message
        const message = this.isConnected 
            ? '🔴 ULTRON AI system online. Pokedex interface activated.'
            : '🔵 ULTRON AI system online. Operating in offline mode.';
        
        setTimeout(() => {
            this.addMessage('system', message);
            
            // Show system capabilities
            if (statusData.status) {
                const capabilities = [];
                if (statusData.status.ultron_core_available) capabilities.push('Core AI');
                if (statusData.status.websocket_available) capabilities.push('Real-time sync');
                if (statusData.status.connected_clients !== undefined) {
                    capabilities.push(`${statusData.status.connected_clients} client(s)`);
                }
                
                if (capabilities.length > 0) {
                    this.addMessage('system', `📊 Available: ${capabilities.join(', ')}`);
                }
            }
        }, 1200);
        
        // Initialize connection status indicator
        this.updateConnectionStatus();
        
        // Start WebSocket connection if available
        if (this.isConnected && statusData.status.websocket_available) {
            setTimeout(() => {
                this.initializeWebSocket();
            }, 1500);
        }
    }

    initializeWebSocket() {
        try {
            console.log('🔌 Initializing WebSocket connection...');
            
            // WebSocket connection for real-time updates
            if (window.io && this.isConnected) {
                this.socket = io('ws://localhost:3001');
                
                this.socket.on('connect', () => {
                    console.log('✅ WebSocket connected');
                    this.addMessage('system', '🔗 Real-time connection established');
                });
                
                this.socket.on('disconnect', () => {
                    console.log('❌ WebSocket disconnected');
                    this.addMessage('system', '⚠️ Real-time connection lost');
                });
                
                this.socket.on('system_update', (data) => {
                    this.handleSystemUpdate(data);
                });
                
                this.socket.on('error', (error) => {
                    console.warn('WebSocket error:', error);
                });
            }
        } catch (error) {
            console.warn('WebSocket initialization failed:', error);
        }
    }

    handleSystemUpdate(data) {
        // Handle real-time system updates
        if (data.type === 'stats') {
            this.systemStats = { ...this.systemStats, ...data.stats };
            this.updateSystemDisplay();
        } else if (data.type === 'message') {
            this.addMessage('system', data.message);
        }
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.playSound('button');
                this.switchSection(e.target.closest('.nav-btn').dataset.section);
            });
        });

        // D-Pad controls
        document.querySelectorAll('.dpad-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.playSound('button');
                this.handleDPadInput(e.target.dataset.direction);
            });
        });

        // Action buttons
        document.getElementById('btn-a').addEventListener('click', () => {
            this.playSound('button');
            this.handleActionButton('A');
        });

        document.getElementById('btn-b').addEventListener('click', () => {
            this.playSound('button');
            this.handleActionButton('B');
        });

        // System buttons
        document.getElementById('btn-power').addEventListener('click', () => {
            this.playSound('button');
            this.showPowerMenu();
        });

        document.getElementById('btn-volume').addEventListener('click', () => {
            this.playSound('button');
            this.handleVolumeControl();
        });

        document.getElementById('btn-settings').addEventListener('click', () => {
            this.playSound('button');
            this.switchSection('settings');
        });

        // Input handling
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('voice-btn').addEventListener('click', () => {
            this.toggleVoiceInput();
        });

        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearMessages();
        });

        // Vision controls
        document.getElementById('capture-btn').addEventListener('click', () => {
            this.captureScreen();
        });

        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.analyzeScreen();
        });

        // Power menu
        document.querySelectorAll('.power-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handlePowerAction(e.target.closest('.power-option').dataset.action);
            });
        });

        // Settings
        document.getElementById('save-config-btn').addEventListener('click', () => {
            this.saveConfiguration();
        });

        // System refresh
        document.getElementById('refresh-system').addEventListener('click', () => {
            this.refreshSystemStats();
        });

        // Theme selector
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.changeTheme(e.target.value);
        });

        // Modal close on background click
        document.getElementById('power-menu').addEventListener('click', (e) => {
            if (e.target.id === 'power-menu') {
                this.hidePowerMenu();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    initializeTheme() {
        const theme = localStorage.getItem('ultron-theme') || 'red';
        this.changeTheme(theme);
    }

    changeTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('ultron-theme', theme);
        
        // Update main LED color
        const mainLed = document.querySelector('.led-main');
        if (mainLed) {
            mainLed.style.setProperty('--primary-color', 
                theme === 'red' ? '#FF0000' : '#0066FF'
            );
        }
        
        this.addMessage('system', `Theme changed to ${theme.toUpperCase()}`);
    }

    showLoadingScreen() {
        document.getElementById('loading-screen').classList.remove('hidden');
        document.getElementById('main-interface').classList.add('hidden');
        
        // Animate loading progress
        const progress = document.querySelector('.loading-progress');
        progress.style.width = '0%';
        
        let width = 0;
        const interval = setInterval(() => {
            width += Math.random() * 15;
            if (width >= 100) {
                width = 100;
                clearInterval(interval);
            }
            progress.style.width = width + '%';
        }, 100);
    }

    hideLoadingScreen() {
        document.getElementById('loading-screen').classList.add('hidden');
        document.getElementById('main-interface').classList.remove('hidden');
    }

    startAnimations() {
        // Update time
        setInterval(() => {
            this.updateTime();
        }, 1000);

        // LED animations
        this.animateLEDs();
        
        // Status updates
        setInterval(() => {
            this.updateStatusIndicators();
        }, 2000);
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toTimeString().split(' ')[0];
        document.getElementById('current-time').textContent = timeString;
    }

    animateLEDs() {
        const mainLed = document.getElementById('main-led');
        const smallLeds = document.querySelectorAll('.led-small');
        
        // Main LED pulsing
        setInterval(() => {
            if (mainLed) {
                mainLed.style.opacity = 0.7 + Math.sin(Date.now() * 0.003) * 0.3;
            }
        }, 50);

        // Small LEDs blinking pattern
        let ledIndex = 0;
        setInterval(() => {
            smallLeds.forEach((led, index) => {
                led.style.opacity = index === ledIndex ? 1 : 0.3;
            });
            ledIndex = (ledIndex + 1) % smallLeds.length;
        }, 1000);
    }

    updateStatusIndicators() {
        // Connection status
        const connectionStatus = document.getElementById('connection-status');
        if (connectionStatus) {
            connectionStatus.textContent = this.isConnected ? 'CONNECTED' : 'OFFLINE';
            connectionStatus.style.color = this.isConnected ? '#00FF41' : '#FF0000';
        }

        // Voice status
        const voiceStatus = document.getElementById('voice-status');
        if (voiceStatus) {
            voiceStatus.style.opacity = this.isListening ? 1 : 0.5;
            voiceStatus.style.color = this.isListening ? '#00FF41' : '#888888';
        }
    }

    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isListening = true;
                this.addMessage('system', 'Voice recognition started. Listening for commands...');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[event.results.length - 1][0].transcript.trim();
                this.processVoiceCommand(transcript);
            };

            this.recognition.onerror = (event) => {
                this.addMessage('system', `Voice recognition error: ${event.error}`);
                this.isListening = false;
            };

            this.recognition.onend = () => {
                this.isListening = false;
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
            this.addMessage('system', 'Voice recognition not supported in this browser');
        }
    }

    processVoiceCommand(transcript) {
        this.addMessage('user', `🎤 ${transcript}`);
        
        // Check for wake words
        const wakeWords = ['ultron', 'jarvis', 'computer', 'ai'];
        const hasWakeWord = wakeWords.some(word => 
            transcript.toLowerCase().includes(word)
        );

        if (hasWakeWord) {
            this.playSound('wake');
            this.processCommand(transcript);
        } else {
            // Process as regular command if listening is active
            if (this.isListening) {
                this.processCommand(transcript);
            }
        }
    }

    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`section-${sectionName}`).classList.add('active');

        // Update status
        document.getElementById('current-section').textContent = sectionName.toUpperCase();
        this.currentSection = sectionName;

        // Section-specific initialization
        switch (sectionName) {
            case 'system':
                this.loadSystemInfo();
                break;
            case 'vision':
                this.initializeVision();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'files':
                this.loadFiles();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }

        this.addMessage('system', `Switched to ${sectionName.toUpperCase()} section`);
    }

    handleDPadInput(direction) {
        switch (direction) {
            case 'up':
                this.navigateUp();
                break;
            case 'down':
                this.navigateDown();
                break;
            case 'left':
                this.navigateLeft();
                break;
            case 'right':
                this.navigateRight();
                break;
            case 'center':
                this.selectCurrent();
                break;
        }
        
        this.addMessage('system', `D-Pad: ${direction.toUpperCase()}`);
    }

    handleActionButton(button) {
        if (button === 'A') {
            // Execute current action
            this.executeCurrentAction();
        } else if (button === 'B') {
            // Go back or cancel
            this.goBack();
        }
        
        this.addMessage('system', `Action Button ${button} pressed`);
    }

    sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (!message) return;

        this.addMessage('user', message);
        input.value = '';
        
        this.processCommand(message);
    }

    addMessage(type, content) {
        const messageArea = document.getElementById('message-area');
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        
        if (type === 'ai' || type === 'system') {
            messageElement.classList.add('ai-message');
        } else {
            messageElement.classList.add('user-message');
        }

        const timestamp = new Date().toLocaleTimeString();
        messageElement.innerHTML = `
            <div class="message-content">${this.formatMessage(content)}</div>
            <div class="message-time">${type === 'system' ? 'SYSTEM' : timestamp}</div>
        `;

        messageArea.appendChild(messageElement);
        messageArea.scrollTop = messageArea.scrollHeight;

        // Store message
        this.messages.push({
            type,
            content,
            timestamp: new Date()
        });

        // Limit message history
        if (this.messages.length > 100) {
            this.messages.shift();
            messageArea.removeChild(messageArea.firstChild);
        }
    }

    formatMessage(content) {
        // Basic formatting for system messages
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    processCommand(command) {
        this.showTypingIndicator();
        
        // Simulate AI processing delay
        setTimeout(() => {
            this.hideTypingIndicator();
            
            const response = this.generateResponse(command);
            this.addMessage('ai', response);
            
            // Execute system commands if needed
            this.executeSystemCommand(command);
            
        }, Math.random() * 2000 + 1000);
    }

    generateResponse(command) {
        const cmd = command.toLowerCase();
        
        // System commands
        if (cmd.includes('status') || cmd.includes('system')) {
            return `**System Status Report:**
            - CPU: ${this.systemStats.cpu}%
            - Memory: ${this.systemStats.memory}%
            - Disk: ${this.systemStats.disk}%
            - Network: ${this.systemStats.network}
            - All systems operational`;
        }
        
        if (cmd.includes('time')) {
            return `Current time: ${new Date().toLocaleString()}`;
        }
        
        if (cmd.includes('theme')) {
            return `Current theme: ${this.currentTheme.toUpperCase()}. Use theme controls to change.`;
        }
        
        if (cmd.includes('help')) {
            return `**Available Commands:**
            - "status" - System status report
            - "time" - Current time
            - "theme" - Theme information
            - "capture" - Take screenshot
            - "analyze" - Analyze screen
            - "clear" - Clear console
            
            **Voice Commands:**
            Use wake words: "Ultron", "Jarvis", "Computer", "AI"`;
        }
        
        if (cmd.includes('capture') || cmd.includes('screenshot')) {
            this.captureScreen();
            return 'Screenshot capture initiated.';
        }
        
        if (cmd.includes('analyze') || cmd.includes('vision')) {
            this.analyzeScreen();
            return 'Screen analysis started.';
        }
        
        if (cmd.includes('clear')) {
            setTimeout(() => this.clearMessages(), 1000);
            return 'Console will be cleared.';
        }
        
        // Default responses
        const responses = [
            'Command acknowledged. Processing request.',
            'ULTRON system responding. Task registered.',
            'AI analysis complete. Awaiting further instructions.',
            'System ready. What would you like me to do next?',
            'Command received. Standing by for additional directives.',
            'ULTRON online. How may I assist you today?'
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    executeSystemCommand(command) {
        // This would communicate with the Python backend
        // For now, we'll simulate the execution
        console.log('Executing system command:', command);
    }

    showTypingIndicator() {
        document.getElementById('typing-indicator').classList.remove('hidden');
    }

    hideTypingIndicator() {
        document.getElementById('typing-indicator').classList.add('hidden');
    }

    clearMessages() {
        const messageArea = document.getElementById('message-area');
        messageArea.innerHTML = `
            <div class="welcome-message">
                <div class="message ai-message">
                    <div class="message-content">
                        <strong>ULTRON AI ONLINE</strong><br>
                        Console cleared. Ready for new commands.
                    </div>
                    <div class="message-time">System</div>
                </div>
            </div>
        `;
        this.messages = [];
        this.playSound('confirm');
    }

    toggleVoiceInput() {
        if (this.recognition) {
            if (this.isListening) {
                this.recognition.stop();
                this.addMessage('system', 'Voice recognition stopped');
            } else {
                this.recognition.start();
            }
        } else {
            this.addMessage('system', 'Voice recognition not available');
        }
    }

    captureScreen() {
        this.addMessage('system', 'Initiating screen capture...');
        
        // Simulate screen capture
        setTimeout(() => {
            const screenshotArea = document.getElementById('screenshot-area');
            screenshotArea.innerHTML = `
                <div style="background: linear-gradient(45deg, #333, #111); width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #00FF41;">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">📷</div>
                        <div>Screenshot captured</div>
                        <div style="font-size: 0.8rem; margin-top: 5px;">${new Date().toLocaleString()}</div>
                    </div>
                </div>
            `;
            this.addMessage('system', 'Screen capture completed successfully');
            this.playSound('confirm');
        }, 1500);
    }

    analyzeScreen() {
        this.addMessage('system', 'Analyzing screen content...');
        
        setTimeout(() => {
            const analysisContent = document.getElementById('analysis-content');
            analysisContent.innerHTML = `
                <div style="color: #00FF41; margin-bottom: 10px;"><strong>ANALYSIS RESULTS</strong></div>
                <div style="margin-bottom: 10px;">
                    <strong>Resolution:</strong> ${window.screen.width}x${window.screen.height}<br>
                    <strong>Color Depth:</strong> ${window.screen.colorDepth}-bit<br>
                    <strong>Viewport:</strong> ${window.innerWidth}x${window.innerHeight}
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>UI Elements Detected:</strong><br>
                    • Navigation panel with 6 sections<br>
                    • Control interface with D-Pad and action buttons<br>
                    • Main display screen with tabbed content<br>
                    • Status indicators and system monitoring
                </div>
                <div>
                    <strong>System Status:</strong><br>
                    • Interface: Active and responsive<br>
                    • Theme: ${this.currentTheme.toUpperCase()}<br>
                    • Section: ${this.currentSection.toUpperCase()}<br>
                    • Time: ${new Date().toLocaleString()}
                </div>
            `;
            this.addMessage('system', 'Screen analysis completed. Results displayed in Vision section.');
            this.playSound('confirm');
        }, 2000);
    }

    showPowerMenu() {
        document.getElementById('power-menu').classList.remove('hidden');
        this.addMessage('system', 'Power management menu opened');
    }

    hidePowerMenu() {
        document.getElementById('power-menu').classList.add('hidden');
    }

    handlePowerAction(action) {
        this.hidePowerMenu();
        
        switch (action) {
            case 'shutdown':
                this.addMessage('system', '⚠️ System shutdown command acknowledged. Initiating shutdown sequence...');
                break;
            case 'reboot':
                this.addMessage('system', '⚠️ System reboot command acknowledged. Preparing for restart...');
                break;
            case 'hibernate':
                this.addMessage('system', '⚠️ System hibernate command acknowledged. Entering sleep mode...');
                break;
            case 'cancel':
                this.addMessage('system', 'Power management cancelled');
                return;
        }
        
        this.playSound('confirm');
        
        // In a real implementation, this would communicate with the backend
        console.log(`Power action: ${action}`);
    }

    handleVolumeControl() {
        this.addMessage('system', 'Volume control accessed. Use system volume controls or voice commands.');
    }

    loadSystemInfo() {
        this.refreshSystemStats();
        this.loadProcessList();
    }

    refreshSystemStats() {
        // Simulate system stats
        this.systemStats = {
            cpu: Math.floor(Math.random() * 60) + 10,
            memory: Math.floor(Math.random() * 40) + 30,
            disk: Math.floor(Math.random() * 30) + 45,
            network: 'CONNECTED'
        };

        // Update UI
        document.getElementById('cpu-usage').textContent = `${this.systemStats.cpu}%`;
        document.getElementById('memory-usage').textContent = `${this.systemStats.memory}%`;
        document.getElementById('disk-usage').textContent = `${this.systemStats.disk}%`;
        document.getElementById('network-status').textContent = this.systemStats.network;

        // Update progress bars
        document.getElementById('cpu-bar').style.width = `${this.systemStats.cpu}%`;
        document.getElementById('memory-bar').style.width = `${this.systemStats.memory}%`;
        document.getElementById('disk-bar').style.width = `${this.systemStats.disk}%`;

        this.addMessage('system', 'System statistics refreshed');
    }

    loadProcessList() {
        const processList = document.getElementById('process-list');
        const processes = [
            'chrome.exe - 15.2% CPU - 234 MB',
            'ultron.exe - 8.7% CPU - 156 MB',
            'explorer.exe - 3.1% CPU - 67 MB',
            'winlogon.exe - 0.1% CPU - 12 MB',
            'svchost.exe - 2.3% CPU - 45 MB',
            'firefox.exe - 12.8% CPU - 189 MB',
            'discord.exe - 5.4% CPU - 98 MB',
            'steam.exe - 1.9% CPU - 76 MB'
        ];

        processList.innerHTML = processes.map(process => 
            `<div style="margin-bottom: 5px; color: #00FF41;">${process}</div>`
        ).join('');
    }

    startSystemMonitoring() {
        // Update system stats every 5 seconds
        setInterval(() => {
            if (this.currentSection === 'system') {
                this.refreshSystemStats();
            }
        }, 5000);
    }

    initializeVision() {
        this.addMessage('system', 'Vision system initialized. Use CAPTURE and ANALYZE buttons.');
    }

    loadTasks() {
        // Placeholder for task management
        const taskList = document.getElementById('task-list');
        if (!taskList) return;

        const sampleTasks = [
            { id: 1, title: 'System Health Check', status: 'completed', priority: 'high' },
            { id: 2, title: 'Update Security Protocols', status: 'active', priority: 'medium' },
            { id: 3, title: 'Backup Configuration Files', status: 'pending', priority: 'low' },
            { id: 4, title: 'Monitor Network Traffic', status: 'active', priority: 'high' }
        ];

        taskList.innerHTML = sampleTasks.map(task => `
            <div class="task-item" style="background: linear-gradient(145deg, #1a1a1a, #0f0f0f); border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: #00FF41; font-weight: bold; margin-bottom: 5px;">${task.title}</div>
                        <div style="color: #888; font-size: 0.8rem;">Priority: ${task.priority.toUpperCase()}</div>
                    </div>
                    <div class="task-status" style="padding: 4px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; 
                        background: ${task.status === 'completed' ? '#00AA22' : task.status === 'active' ? '#AAAA00' : '#AA0000'};
                        color: white;">
                        ${task.status.toUpperCase()}
                    </div>
                </div>
            </div>
        `).join('');
    }

    loadFiles() {
        const fileBrowser = document.getElementById('file-browser');
        if (!fileBrowser) return;

        const sampleFiles = [
            { name: 'config.json', size: '2.4 KB', type: 'config', modified: '2 hours ago' },
            { name: 'ultron.log', size: '15.7 MB', type: 'log', modified: '1 minute ago' },
            { name: 'models/', size: '1.2 GB', type: 'folder', modified: '1 day ago' },
            { name: 'assets/', size: '45.6 MB', type: 'folder', modified: '3 hours ago' },
            { name: 'backup_20241229.zip', size: '89.3 MB', type: 'archive', modified: '1 day ago' }
        ];

        fileBrowser.innerHTML = sampleFiles.map(file => `
            <div class="file-item" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; margin-bottom: 5px; border: 1px solid #333; border-radius: 5px; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.2rem;">
                        ${file.type === 'folder' ? '📁' : file.type === 'config' ? '⚙️' : file.type === 'log' ? '📄' : '📦'}
                    </div>
                    <div>
                        <div style="color: #00FF41; font-weight: bold;">${file.name}</div>
                        <div style="color: #888; font-size: 0.8rem;">${file.size} • ${file.modified}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    loadSettings() {
        // Load current configuration
        const apiKey = localStorage.getItem('ultron-api-key') || '';
        const voiceGender = localStorage.getItem('ultron-voice-gender') || 'male';
        const theme = localStorage.getItem('ultron-theme') || 'red';
        const visionEnabled = localStorage.getItem('ultron-vision-enabled') === 'true';
        const autoLaunch = localStorage.getItem('ultron-auto-launch') === 'true';
        const offlineMode = localStorage.getItem('ultron-offline-mode') === 'true';

        // Populate settings form
        document.getElementById('api-key').value = apiKey;
        document.getElementById('voice-gender').value = voiceGender;
        document.getElementById('theme-select').value = theme;
        document.getElementById('vision-enabled').checked = visionEnabled;
        document.getElementById('auto-launch').checked = autoLaunch;
        document.getElementById('offline-mode').checked = offlineMode;
    }

    loadConfiguration() {
        // Load settings from localStorage
        this.loadSettings();
    }

    saveConfiguration() {
        // Save all settings
        const settings = {
            apiKey: document.getElementById('api-key').value,
            voiceGender: document.getElementById('voice-gender').value,
            theme: document.getElementById('theme-select').value,
            visionEnabled: document.getElementById('vision-enabled').checked,
            autoLaunch: document.getElementById('auto-launch').checked,
            offlineMode: document.getElementById('offline-mode').checked
        };

        // Save to localStorage
        Object.entries(settings).forEach(([key, value]) => {
            localStorage.setItem(`ultron-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value);
        });

        // Apply theme change if needed
        if (settings.theme !== this.currentTheme) {
            this.changeTheme(settings.theme);
        }

        this.addMessage('system', 'Configuration saved successfully');
        this.playSound('confirm');
    }

    // Navigation helpers
    navigateUp() {
        // Implementation depends on current section
        console.log('Navigate up');
    }

    navigateDown() {
        // Implementation depends on current section
        console.log('Navigate down');
    }

    navigateLeft() {
        // Implementation depends on current section
        console.log('Navigate left');
    }

    navigateRight() {
        // Implementation depends on current section
        console.log('Navigate right');
    }

    selectCurrent() {
        // Implementation depends on current section
        console.log('Select current');
    }

    executeCurrentAction() {
        // Implementation depends on current context
        switch (this.currentSection) {
            case 'console':
                this.sendMessage();
                break;
            case 'vision':
                this.analyzeScreen();
                break;
            case 'settings':
                this.saveConfiguration();
                break;
            default:
                this.addMessage('system', 'Action executed');
        }
    }

    goBack() {
        // Go back or cancel current action
        if (this.currentSection !== 'console') {
            this.switchSection('console');
        } else {
            this.clearMessages();
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl + shortcuts
        if (e.ctrlKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.switchSection('console');
                    break;
                case '2':
                    e.preventDefault();
                    this.switchSection('system');
                    break;
                case '3':
                    e.preventDefault();
                    this.switchSection('vision');
                    break;
                case 'l':
                    e.preventDefault();
                    this.clearMessages();
                    break;
                case 'Enter':
                    e.preventDefault();
                    this.executeCurrentAction();
                    break;
            }
        }

        // Escape key
        if (e.key === 'Escape') {
            this.hidePowerMenu();
            this.goBack();
        }

        // Space for voice toggle
        if (e.key === ' ' && e.target.tagName !== 'INPUT') {
            e.preventDefault();
            this.toggleVoiceInput();
        }
    }

    playSound(soundName) {
        try {
            // Try to play from audio element first
            const audio = document.getElementById(`audio-${soundName}`);
            if (audio && audio.canPlayType && audio.canPlayType('audio/wav')) {
                audio.currentTime = 0;
                audio.play().catch(e => {
                    console.log('Audio file play failed, using generated sound:', e);
                    this.playGeneratedSound(soundName);
                });
            } else {
                // Fallback to generated sounds
                this.playGeneratedSound(soundName);
            }
        } catch (e) {
            console.log('Sound system error, using fallback:', soundName);
            this.playGeneratedSound(soundName);
        }
    }

    playGeneratedSound(soundName) {
        // Use the UltronSoundSystem from sounds.js if available
        if (window.ultronSounds && typeof window.ultronSounds.playWakeSound === 'function') {
            try {
                switch (soundName) {
                    case 'wake':
                        window.ultronSounds.playWakeSound();
                        break;
                    case 'button':
                        window.ultronSounds.playButtonSound();
                        break;
                    case 'confirm':
                        window.ultronSounds.playConfirmSound();
                        break;
                    case 'error':
                        window.ultronSounds.playErrorSound();
                        break;
                    default:
                        window.ultronSounds.playButtonSound();
                }
                console.log(`🔊 Generated sound played: ${soundName}`);
            } catch (error) {
                console.warn(`Generated sound error for ${soundName}:`, error);
                this.playFallbackSound(soundName);
            }
        } else {
            console.log(`🔇 Generated sound system not available for: ${soundName}`);
            this.playFallbackSound(soundName);
        }
    }

    playFallbackSound(soundName) {
        // Create a very basic beep using Web Audio API if nothing else works
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Different frequencies for different sounds
            const frequencies = {
                'wake': 440,
                'button': 800,
                'confirm': 600,
                'error': 200
            };
            
            oscillator.frequency.value = frequencies[soundName] || 400;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
            
            console.log(`🎵 Fallback beep played: ${soundName}`);
        } catch (error) {
            console.warn('All sound systems failed:', error);
        }
    }

    updateConnectionStatus() {
        const statusElements = document.querySelectorAll('.connection-status');
        const statusText = this.isConnected ? 'CONNECTED' : 'OFFLINE';
        const statusColor = this.isConnected ? '#00FF41' : '#FF4444';
        
        statusElements.forEach(element => {
            if (element) {
                element.textContent = statusText;
                element.style.color = statusColor;
            }
        });

        // Update network status in system stats
        this.systemStats.network = statusText;
        
        // Update the LED indicators
        const mainLed = document.getElementById('main-led');
        if (mainLed) {
            mainLed.style.backgroundColor = statusColor;
            mainLed.style.boxShadow = `0 0 20px ${statusColor}`;
        }
        
        console.log(`Connection status updated: ${statusText}`);
    }
}

// Initialize the interface when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ultronInterface = new UltronInterface();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UltronInterface;
}
