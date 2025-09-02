// ULTRON Enhanced - Main JavaScript Application
// Handles all interactive functionality for the Pokédx interface

class UltronApp {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.currentTab = 'console';
        this.systemStats = {};
        this.tasks = [];
        this.bootComplete = false;
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('Initializing ULTRON Enhanced Interface...');
        
        // Initialize socket connection
        this.initSocket();
        
        // Start boot sequence
        this.startBootSequence();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize system monitoring
        this.initSystemMonitoring();
        
        console.log('ULTRON Enhanced Interface initialized');
    }
    
    initSocket() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to ULTRON server');
                this.connected = true;
                this.updateConnectionStatus('connected', 'Connected');
                this.activateStatusLight('green');
                
                if (window.ultronSounds) {
                    window.ultronSounds.play('success');
                }
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from ULTRON server');
                this.connected = false;
                this.updateConnectionStatus('disconnected', 'Disconnected');
                this.deactivateAllStatusLights();
                
                if (window.ultronSounds) {
                    window.ultronSounds.play('error');
                }
            });
            
            this.socket.on('status_update', (data) => {
                this.handleStatusUpdate(data);
            });
            
            this.socket.on('chat_response', (data) => {
                this.handleChatResponse(data);
            });
            
            this.socket.on('live_response', (data) => {
                this.handleChatResponse(data);
            });
            
            this.socket.on('command_result', (data) => {
                this.handleCommandResult(data);
            });
            
            this.socket.on('error', (data) => {
                console.error('Server error:', data);
                this.addChatMessage('system', `Error: ${data.message}`);
            });
            
        } catch (e) {
            console.error('Socket initialization failed:', e);
            this.updateConnectionStatus('error', 'Connection Failed');
        }
    }
    
    startBootSequence() {
        const bootSequence = document.getElementById('boot-sequence');
        const mainInterface = document.getElementById('main-interface');
        const progressBar = document.getElementById('boot-progress');
        const powerLight = document.getElementById('power-light');
        
        if (!bootSequence || !mainInterface || !progressBar) return;
        
        // Activate power light
        powerLight.classList.add('active');
        
        // Play startup sound
        if (window.ultronSounds) {
            window.ultronSounds.playStartupSequence();
        }
        
        // Simulate boot progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10 + 5;
            if (progress > 100) progress = 100;
            
            progressBar.style.width = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                
                setTimeout(() => {
                    bootSequence.style.display = 'none';
                    mainInterface.style.display = 'block';
                    this.bootComplete = true;
                    
                    // Activate all status lights
                    this.activateStatusLight('red');
                    this.activateStatusLight('yellow');
                    this.activateStatusLight('green');
                    
                    // Start systems
                    this.startSystemMonitoring();
                    
                    console.log('Boot sequence complete');
                }, 500);
            }
        }, 200);
    }
    
    setupEventListeners() {
        // Chat functionality
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        const voiceButton = document.getElementById('voice-button');
        
        if (chatInput && sendButton) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (voiceButton) {
            voiceButton.addEventListener('click', () => this.toggleVoiceListening());
        }
        
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
                
                if (window.ultronSounds) {
                    window.ultronSounds.playInteraction('select');
                }
            });
        });
        
        // Control pad
        document.querySelectorAll('.d-pad-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const direction = btn.dataset.direction;
                this.handleDPadClick(direction);
                
                if (window.ultronSounds) {
                    window.ultronSounds.playInteraction('click');
                }
            });
        });
        
        // Action buttons
        document.getElementById('action-a')?.addEventListener('click', () => {
            this.handleActionButton('A');
        });
        
        document.getElementById('action-b')?.addEventListener('click', () => {
            this.handleActionButton('B');
        });
        
        // Vision controls
        document.getElementById('screenshot-btn')?.addEventListener('click', () => {
            this.takeScreenshot();
        });
        
        document.getElementById('ocr-btn')?.addEventListener('click', () => {
            this.performOCR();
        });
        
        document.getElementById('analyze-btn')?.addEventListener('click', () => {
            this.analyzeScreen();
        });
        
        // File controls
        document.getElementById('organize-files-btn')?.addEventListener('click', () => {
            this.organizeFiles();
        });
        
        document.getElementById('cleanup-temp-btn')?.addEventListener('click', () => {
            this.cleanupTemp();
        });
        
        // Task management
        document.getElementById('add-task-btn')?.addEventListener('click', () => {
            this.addTask();
        });
        
        document.getElementById('new-task-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTask();
            }
        });
        
        // Configuration changes
        document.getElementById('voice-speed')?.addEventListener('input', (e) => {
            document.getElementById('voice-speed-value').textContent = e.target.value;
        });
        
        // Power light click to toggle
        document.getElementById('power-light')?.addEventListener('click', () => {
            this.togglePower();
        });
        
        // Add sound effects to all interactive elements
        document.querySelectorAll('button, .nav-tab, .d-pad-btn, .action-btn').forEach(element => {
            element.addEventListener('mouseenter', () => {
                if (window.ultronSounds) {
                    window.ultronSounds.playInteraction('hover');
                }
            });
        });
    }
    
    initSystemMonitoring() {
        // Set up periodic system stats updates
        setInterval(() => {
            if (this.connected && this.bootComplete) {
                this.updateSystemStats();
            }
        }, 5000);
    }
    
    updateSystemStats() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.system_stats) {
                    this.displaySystemStats(data.system_stats);
                }
            })
            .catch(e => console.warn('Failed to update system stats:', e));
    }
    
    displaySystemStats(stats) {
        // Update CPU usage
        const cpuBar = document.getElementById('cpu-bar');
        const cpuValue = document.getElementById('cpu-value');
        if (stats.cpu && cpuBar && cpuValue) {
            const cpuPercent = stats.cpu.percent || 0;
            cpuBar.style.width = cpuPercent + '%';
            cpuValue.textContent = Math.round(cpuPercent) + '%';
        }
        
        // Update Memory usage
        const memoryBar = document.getElementById('memory-bar');
        const memoryValue = document.getElementById('memory-value');
        if (stats.memory && memoryBar && memoryValue) {
            const memoryPercent = stats.memory.percent || 0;
            memoryBar.style.width = memoryPercent + '%';
            memoryValue.textContent = Math.round(memoryPercent) + '%';
        }
        
        // Update Disk usage
        const diskBar = document.getElementById('disk-bar');
        const diskValue = document.getElementById('disk-value');
        if (stats.disk && stats.disk.length > 0 && diskBar && diskValue) {
            const diskPercent = stats.disk[0].percent || 0;
            diskBar.style.width = diskPercent + '%';
            diskValue.textContent = Math.round(diskPercent) + '%';
        }
    }
    
    switchTab(tabName) {
        // Deactivate current tab
        document.querySelector('.nav-tab.active')?.classList.remove('active');
        document.querySelector('.tab-panel.active')?.classList.remove('active');
        
        // Activate new tab
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
        document.getElementById(`${tabName}-panel`)?.classList.add('active');
        
        this.currentTab = tabName;
        console.log('Switched to tab:', tabName);
    }
    
    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addChatMessage('user', message);
        
        // Clear input
        input.value = '';
        
        // Send to server
        if (this.connected) {
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: 'default'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    this.addChatMessage('system', `Error: ${data.error}`);
                }
                // Response handled via socket
            })
            .catch(e => {
                console.error('Chat error:', e);
                this.addChatMessage('system', 'Failed to send message');
            });
        } else {
            this.addChatMessage('system', 'Not connected to server');
        }
    }
    
    addChatMessage(type, message) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `${type}-message`;
        
        const timestamp = new Date().toLocaleTimeString();
        const typeLabel = type.toUpperCase();
        
        messageElement.innerHTML = `
            <span class="timestamp">[${timestamp}] ${typeLabel}:</span>
            ${this.escapeHtml(message)}
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    handleChatResponse(data) {
        if (data.response) {
            this.addChatMessage('ai', data.response);
        }
        if (data.error) {
            this.addChatMessage('system', `Error: ${data.error}`);
        }
    }
    
    handleStatusUpdate(data) {
        console.log('Status update:', data);
        // Handle status updates from server
    }
    
    handleCommandResult(data) {
        console.log('Command result:', data);
        this.addChatMessage('system', `Command completed: ${JSON.stringify(data.result)}`);
    }
    
    takeScreenshot() {
        if (!this.connected) {
            this.addChatMessage('system', 'Not connected to server');
            return;
        }
        
        this.addChatMessage('system', 'Taking screenshot...');
        
        fetch('/api/screenshot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.screenshot_path) {
                this.displayScreenshot(data.screenshot_path);
                this.addChatMessage('system', `Screenshot saved: ${data.screenshot_path}`);
            } else {
                this.addChatMessage('system', `Screenshot failed: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(e => {
            console.error('Screenshot error:', e);
            this.addChatMessage('system', 'Screenshot request failed');
        });
    }
    
    performOCR() {
        if (!this.connected) {
            this.addChatMessage('system', 'Not connected to server');
            return;
        }
        
        this.addChatMessage('system', 'Extracting text from screen...');
        
        fetch('/api/ocr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.text) {
                this.displayVisionResults(`OCR Text:\n${data.text}`);
                this.addChatMessage('system', `Text extracted: ${data.text.length} characters`);
            } else {
                this.addChatMessage('system', 'No text found or OCR failed');
            }
        })
        .catch(e => {
            console.error('OCR error:', e);
            this.addChatMessage('system', 'OCR request failed');
        });
    }
    
    analyzeScreen() {
        this.addChatMessage('system', 'Analyzing screen with AI...');
        // Implementation for AI screen analysis
    }
    
    displayScreenshot(imagePath) {
        const visionImage = document.getElementById('vision-image');
        const visionPlaceholder = document.getElementById('vision-placeholder');
        
        if (visionImage && visionPlaceholder) {
            visionImage.src = imagePath;
            visionImage.style.display = 'block';
            visionPlaceholder.style.display = 'none';
            
            // Switch to vision tab
            this.switchTab('vision');
        }
    }
    
    displayVisionResults(results) {
        const resultsContainer = document.getElementById('vision-results');
        if (resultsContainer) {
            resultsContainer.textContent = results;
        }
    }
    
    organizeFiles() {
        if (!this.connected) return;
        
        this.addChatMessage('system', 'Organizing files...');
        
        fetch('/api/automation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'organize_files',
                params: {}
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.addChatMessage('system', `Files organized: ${JSON.stringify(data.result)}`);
            } else {
                this.addChatMessage('system', `File organization failed: ${data.error}`);
            }
        })
        .catch(e => {
            console.error('File organization error:', e);
            this.addChatMessage('system', 'File organization request failed');
        });
    }
    
    cleanupTemp() {
        if (!this.connected) return;
        
        this.addChatMessage('system', 'Cleaning up temporary files...');
        // Implementation for temp cleanup
    }
    
    addTask() {
        const input = document.getElementById('new-task-input');
        const taskText = input.value.trim();
        
        if (!taskText) return;
        
        const task = {
            id: Date.now(),
            title: taskText,
            description: 'User-created task',
            status: 'pending',
            created: new Date().toISOString()
        };
        
        this.tasks.push(task);
        this.updateTaskList();
        
        input.value = '';
        this.addChatMessage('system', `Task added: ${taskText}`);
    }
    
    updateTaskList() {
        const taskList = document.getElementById('task-list');
        if (!taskList) return;
        
        // Clear existing tasks
        taskList.innerHTML = '';
        
        this.tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-item';
            taskElement.innerHTML = `
                <div class="task-content">
                    <div class="task-title">${this.escapeHtml(task.title)}</div>
                    <div class="task-description">${this.escapeHtml(task.description)}</div>
                </div>
                <div class="task-status ${task.status}">
                    ${task.status === 'completed' ? '✓' : task.status === 'error' ? '✗' : '⏳'}
                </div>
            `;
            taskList.appendChild(taskElement);
        });
    }
    
    handleDPadClick(direction) {
        console.log('D-Pad clicked:', direction);
        
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
    }
    
    handleActionButton(button) {
        console.log('Action button clicked:', button);
        
        if (button === 'A') {
            // Confirm/Select action
            this.selectCurrent();
        } else if (button === 'B') {
            // Back/Cancel action
            this.goBack();
        }
    }
    
    navigateUp() {
        // Navigate up in current context
    }
    
    navigateDown() {
        // Navigate down in current context
    }
    
    navigateLeft() {
        // Navigate left in current context
        const tabs = ['console', 'system', 'vision', 'tasks', 'files', 'config'];
        const currentIndex = tabs.indexOf(this.currentTab);
        const newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
        this.switchTab(tabs[newIndex]);
    }
    
    navigateRight() {
        // Navigate right in current context
        const tabs = ['console', 'system', 'vision', 'tasks', 'files', 'config'];
        const currentIndex = tabs.indexOf(this.currentTab);
        const newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
        this.switchTab(tabs[newIndex]);
    }
    
    selectCurrent() {
        // Select current item
        console.log('Select current item in tab:', this.currentTab);
    }
    
    goBack() {
        // Go back or cancel current operation
        console.log('Go back/cancel');
    }
    
    toggleVoiceListening() {
        if (!this.connected) {
            this.addChatMessage('system', 'Not connected to server');
            return;
        }
        
        const voiceButton = document.getElementById('voice-button');
        if (voiceButton.classList.contains('listening')) {
            // Stop listening
            voiceButton.classList.remove('listening');
            voiceButton.textContent = '🎤';
            this.addChatMessage('system', 'Voice listening stopped');
        } else {
            // Start listening
            voiceButton.classList.add('listening');
            voiceButton.textContent = '🔴';
            this.addChatMessage('system', 'Voice listening started...');
            
            // Request voice input from server
            fetch('/api/voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: 'listen',
                    timeout: 5
                })
            })
            .then(response => response.json())
            .then(data => {
                voiceButton.classList.remove('listening');
                voiceButton.textContent = '🎤';
                
                if (data.success && data.text) {
                    document.getElementById('chat-input').value = data.text;
                    this.addChatMessage('system', `Voice input: "${data.text}"`);
                } else {
                    this.addChatMessage('system', 'No voice input detected');
                }
            })
            .catch(e => {
                console.error('Voice error:', e);
                voiceButton.classList.remove('listening');
                voiceButton.textContent = '🎤';
                this.addChatMessage('system', 'Voice request failed');
            });
        }
    }
    
    togglePower() {
        const powerLight = document.getElementById('power-light');
        
        if (powerLight.classList.contains('active')) {
            // Power off
            powerLight.classList.remove('active');
            this.deactivateAllStatusLights();
            this.addChatMessage('system', 'System powering down...');
            
            if (window.ultronSounds) {
                window.ultronSounds.play('error');
            }
        } else {
            // Power on
            powerLight.classList.add('active');
            this.activateStatusLight('green');
            this.addChatMessage('system', 'System powering up...');
            
            if (window.ultronSounds) {
                window.ultronSounds.playStartupSequence();
            }
        }
    }
    
    activateStatusLight(color) {
        const light = document.getElementById(`status-${color}`);
        if (light) {
            light.classList.add('active');
        }
    }
    
    deactivateAllStatusLights() {
        ['red', 'yellow', 'green'].forEach(color => {
            const light = document.getElementById(`status-${color}`);
            if (light) {
                light.classList.remove('active');
            }
        });
    }
    
    updateConnectionStatus(status, text) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot) {
            statusDot.className = 'status-dot';
            if (status === 'connected') {
                statusDot.classList.add('connected');
            } else if (status === 'connecting') {
                statusDot.classList.add('connecting');
            }
        }
        
        if (statusText) {
            statusText.textContent = text;
        }
    }
    
    startSystemMonitoring() {
        // Start periodic updates
        setInterval(() => {
            if (this.connected && this.bootComplete) {
                this.updateSystemStats();
            }
        }, 3000);
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize the application when page loads
window.ultronApp = new UltronApp();