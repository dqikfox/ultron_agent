/**
 * Enhanced ULTRON GUI with MCP Integration and Natural Language Processing
 * Seamless system control with voice commands and intelligent automation
 */

class EnhancedUltronGUI {
    constructor() {
        this.apiBase = 'http://localhost:5001/api';
        this.isListening = false;
        this.recognition = null;
        this.setupVoiceRecognition();
        this.setupEventListeners();
        this.initializeSystem();
    }

    setupVoiceRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const command = event.results[0][0].transcript;
                this.processVoiceCommand(command);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.updateStatus('Voice recognition error: ' + event.error, 'error');
            };
        }
    }

    setupEventListeners() {
        // Enhanced voice control
        document.getElementById('voiceBtn')?.addEventListener('click', () => {
            this.toggleVoiceListening();
        });
        
        // Voice settings
        document.getElementById('voiceSettings')?.addEventListener('click', () => {
            this.showVoiceSettings();
        });

        // Manual command input
        document.getElementById('commandInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const command = e.target.value;
                if (command.trim()) {
                    this.processCommand(command);
                    e.target.value = '';
                }
            }
        });

        // Quick action buttons
        document.getElementById('screenshotBtn')?.addEventListener('click', () => {
            this.takeEnhancedScreenshot();
        });

        document.getElementById('systemInfoBtn')?.addEventListener('click', () => {
            this.getSystemInfo();
        });
    }

    async initializeSystem() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            const status = await response.json();
            
            if (status.success) {
                this.updateStatus('Enhanced ULTRON System Online', 'success');
                this.displayCapabilities(status.capabilities);
            }
        } catch (error) {
            this.updateStatus('System initialization failed', 'error');
        }
    }

    toggleVoiceListening() {
        if (!this.recognition) {
            this.updateStatus('Voice recognition not supported', 'error');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            this.updateVoiceButton('🎤 Start Listening');
            this.updateStatus('Voice listening stopped', 'info');
        } else {
            // Enhanced voice setup
            this.setupEnhancedVoiceRecognition();
            this.recognition.start();
            this.isListening = true;
            this.updateVoiceButton('🔴 Listening...');
            this.updateStatus('Enhanced voice listening active...', 'info');
        }
    }
    
    setupEnhancedVoiceRecognition() {
        if (this.recognition) {
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.maxAlternatives = 3;
            
            // Enhanced result processing
            this.recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    const confidence = event.results[i][0].confidence;
                    
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                        this.processEnhancedVoiceCommand(transcript, confidence);
                    } else {
                        interimTranscript += transcript;
                        this.updateStatus(`Listening: ${interimTranscript}`, 'info');
                    }
                }
            };
        }
    }
    
    async processEnhancedVoiceCommand(transcript, confidence) {
        // Enhanced processing with confidence checking
        if (confidence < 0.7) {
            this.updateStatus(`Low confidence (${Math.round(confidence * 100)}%). Please repeat.`, 'warning');
            return;
        }
        
        this.updateStatus(`Processing: "${transcript}" (${Math.round(confidence * 100)}% confidence)`, 'info');
        this.addToCommandHistory(transcript, 'voice-enhanced');
        
        // Context-aware processing
        await this.processCommandWithContext(transcript);
    }
    
    async processCommandWithContext(command) {
        // Add conversation context
        const context = {
            recent_commands: this.getRecentCommands(),
            current_time: new Date().toISOString(),
            confidence_boost: this.calculateContextBoost(command)
        };
        
        // Enhanced command processing
        await this.processCommand(command, context);
    }

    async processVoiceCommand(command) {
        this.updateStatus(`Voice command: "${command}"`, 'info');
        this.addToCommandHistory(command, 'voice');
        await this.processCommand(command);
        
        // Auto-stop listening after command
        if (this.isListening) {
            this.toggleVoiceListening();
        }
    }

    async processCommand(command) {
        try {
            this.updateStatus('Processing command...', 'info');
            
            // Determine command type and route appropriately
            if (this.isBrowserCommand(command)) {
                await this.executeBrowserCommand(command);
            } else if (this.isSystemCommand(command)) {
                await this.executeSystemCommand(command);
            } else if (this.isOCRCommand(command)) {
                await this.executeOCRCommand(command);
            } else if (this.isDocsCommand(command)) {
                await this.executeDocsQuery(command);
            } else {
                // Default to system command for natural language
                await this.executeSystemCommand(command);
            }
        } catch (error) {
            this.updateStatus(`Command failed: ${error.message}`, 'error');
        }
    }

    isBrowserCommand(command) {
        const browserKeywords = ['browse', 'navigate', 'search', 'chrome', 'website', 'url'];
        return browserKeywords.some(keyword => command.toLowerCase().includes(keyword));
    }

    isSystemCommand(command) {
        const systemKeywords = ['open', 'launch', 'start', 'close', 'kill', 'run'];
        return systemKeywords.some(keyword => command.toLowerCase().includes(keyword));
    }

    isOCRCommand(command) {
        const ocrKeywords = ['screenshot', 'ocr', 'read', 'text', 'scan'];
        return ocrKeywords.some(keyword => command.toLowerCase().includes(keyword));
    }

    isDocsCommand(command) {
        const docsKeywords = ['docs', 'documentation', 'help', 'guide', 'how to', 'explain'];
        return docsKeywords.some(keyword => command.toLowerCase().includes(keyword));
    }

    async executeBrowserCommand(command) {
        try {
            const response = await fetch(`${this.apiBase}/browser/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });

            const result = await response.json();
            if (result.success) {
                this.updateStatus(`Browser: ${result.result}`, 'success');
                this.displayResult('Browser Action', result.result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.updateStatus(`Browser command failed: ${error.message}`, 'error');
        }
    }

    async executeSystemCommand(command) {
        try {
            const response = await fetch(`${this.apiBase}/system/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });

            const result = await response.json();
            if (result.success) {
                this.updateStatus(`System: ${result.result}`, 'success');
                this.displayResult('System Command', result.result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.updateStatus(`System command failed: ${error.message}`, 'error');
        }
    }

    async executeOCRCommand(command) {
        await this.takeEnhancedScreenshot();
    }

    async executeDocsQuery(query) {
        try {
            const response = await fetch(`${this.apiBase}/docs/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const result = await response.json();
            if (result.success) {
                this.updateStatus(`Docs: Found information`, 'success');
                this.displayResult('Documentation', result.result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.updateStatus(`Docs query failed: ${error.message}`, 'error');
        }
    }

    async takeEnhancedScreenshot() {
        try {
            this.updateStatus('Taking enhanced screenshot...', 'info');
            
            const response = await fetch(`${this.apiBase}/vision/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();
            if (result.success) {
                this.updateStatus('Screenshot analyzed successfully', 'success');
                this.displayOCRResult(result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.updateStatus(`Screenshot failed: ${error.message}`, 'error');
        }
    }

    async getSystemInfo() {
        try {
            const result = await this.executeSystemCommand('system info');
            this.displayResult('System Information', result);
        } catch (error) {
            this.updateStatus(`System info failed: ${error.message}`, 'error');
        }
    }

    displayOCRResult(result) {
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        const ocrHtml = `
            <div class="ocr-result">
                <h3>📸 Enhanced OCR Analysis</h3>
                <div class="ocr-details">
                    <p><strong>Confidence:</strong> ${result.confidence}%</p>
                    <p><strong>Words Found:</strong> ${result.word_count}</p>
                    <div class="text-content">
                        <h4>Extracted Text:</h4>
                        <pre>${result.text_content || 'No text detected'}</pre>
                    </div>
                    ${result.analysis ? `
                        <div class="analysis">
                            <h4>Content Analysis:</h4>
                            <p><strong>Type:</strong> ${result.analysis.type}</p>
                            <ul>
                                ${result.analysis.insights.map(insight => `<li>${insight}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        resultsDiv.innerHTML = ocrHtml;
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    displayResult(title, content) {
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        const resultHtml = `
            <div class="command-result">
                <h3>🤖 ${title}</h3>
                <div class="result-content">
                    <pre>${content}</pre>
                </div>
                <div class="timestamp">${new Date().toLocaleTimeString()}</div>
            </div>
        `;

        resultsDiv.innerHTML = resultHtml;
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    displayCapabilities(capabilities) {
        const capabilitiesDiv = document.getElementById('capabilities');
        if (!capabilitiesDiv) return;

        const capHtml = capabilities.map(cap => `<li>✅ ${cap}</li>`).join('');
        capabilitiesDiv.innerHTML = `<ul>${capHtml}</ul>`;
    }

    addToCommandHistory(command, type = 'manual') {
        const historyDiv = document.getElementById('commandHistory');
        if (!historyDiv) return;

        const historyItem = document.createElement('div');
        historyItem.className = `history-item ${type}`;
        historyItem.innerHTML = `
            <span class="command">${command}</span>
            <span class="type">${type}</span>
            <span class="time">${new Date().toLocaleTimeString()}</span>
        `;

        historyDiv.insertBefore(historyItem, historyDiv.firstChild);

        // Keep only last 10 items
        while (historyDiv.children.length > 10) {
            historyDiv.removeChild(historyDiv.lastChild);
        }
    }

    updateStatus(message, type = 'info') {
        const statusDiv = document.getElementById('status');
        if (!statusDiv) return;

        statusDiv.className = `status ${type}`;
        statusDiv.textContent = message;

        // Auto-clear status after 5 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                if (statusDiv.textContent === message) {
                    statusDiv.textContent = 'Ready';
                    statusDiv.className = 'status';
                }
            }, 5000);
        }
    }

    updateVoiceButton(text) {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.textContent = text;
        }
    }
}

// Initialize Enhanced ULTRON GUI when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.ultronGUI = new EnhancedUltronGUI();
    console.log('Enhanced ULTRON GUI initialized with MCP integration');
});

// Example voice commands for testing
const EXAMPLE_COMMANDS = [
    "hey ultron open chrome and search for the car thing we looked at yesterday",
    "take a screenshot and read the text",
    "open notepad",
    "close all chrome windows", 
    "show system information",
    "navigate to google.com",
    "launch calculator",
    "help with MCP integration",
    "explain Continue documentation", 
    "show codebase information",
    "remember this conversation",
    "what did we search for yesterday",
    "open that file we worked on",
    "continue where we left off"
];

// Add example commands to help section
document.addEventListener('DOMContentLoaded', () => {
    const helpDiv = document.getElementById('exampleCommands');
    if (helpDiv) {
        const exampleHtml = EXAMPLE_COMMANDS.map(cmd => 
            `<div class="example-command" onclick="document.getElementById('commandInput').value='${cmd}'">${cmd}</div>`
        ).join('');
        helpDiv.innerHTML = exampleHtml;
    }
});