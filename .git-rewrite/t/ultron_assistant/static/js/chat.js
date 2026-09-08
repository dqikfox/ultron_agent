// static/js/chat.js
class UltronChat {
    constructor() {
        this.socket = io();
        this.chatBox = document.getElementById('chat-box');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.micBtn = document.getElementById('mic-btn');
        this.statusIndicator = null;
        this.isListening = false;
        this.isConnected = false;
        this.conversationId = this.generateConversationId();
        this.currentAssistantMessage = null;
        
        this.init();
    }
    
    init() {
        this.setupSocketListeners();
        this.setupUIListeners();
        this.createStatusIndicator();
        this.addWelcomeMessage();
    }
    
    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    createStatusIndicator() {
        // Create connection status indicator
        this.statusIndicator = document.createElement('div');
        this.statusIndicator.className = 'connection-status connecting';
        this.statusIndicator.textContent = 'Connecting...';
        document.body.appendChild(this.statusIndicator);
    }
    
    updateConnectionStatus(status) {
        if (this.statusIndicator) {
            this.statusIndicator.className = `connection-status ${status}`;
            switch (status) {
                case 'connected':
                    this.statusIndicator.textContent = 'Connected';
                    this.isConnected = true;
                    break;
                case 'disconnected':
                    this.statusIndicator.textContent = 'Disconnected';
                    this.isConnected = false;
                    break;
                case 'connecting':
                    this.statusIndicator.textContent = 'Connecting...';
                    this.isConnected = false;
                    break;
            }
            
            // Auto-hide after 3 seconds if connected
            if (status === 'connected') {
                setTimeout(() => {
                    if (this.statusIndicator) {
                        this.statusIndicator.style.opacity = '0';
                    }
                }, 3000);
            } else {
                this.statusIndicator.style.opacity = '1';
            }
        }
    }
    
    setupSocketListeners() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to Ultron Assistant');
            this.updateConnectionStatus('connected');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from Ultron Assistant');
            this.updateConnectionStatus('disconnected');
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus('disconnected');
        });
        
        // Message events
        this.socket.on('assistant_chunk', (data) => {
            this.handleAssistantChunk(data.chunk);
        });
        
        this.socket.on('assistant_done', () => {
            this.handleAssistantDone();
        });
        
        this.socket.on('error', (data) => {
            this.addMessage(data.message, 'assistant error');
        });
        
        this.socket.on('status', (data) => {
            console.log('Status:', data.message);
        });
    }
    
    setupUIListeners() {
        // Send button
        this.sendBtn.onclick = () => this.sendMessage();
        
        // Enter key in input
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Microphone button
        this.micBtn.onclick = () => this.toggleVoiceInput();
        
        // Auto-resize input
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
        });
        
        // Focus input on load
        this.userInput.focus();
    }
    
    addWelcomeMessage() {
        const welcomeText = "Hello! I'm Ultron, your advanced AI assistant. I can help you with various tasks including automation, web searches, taking screenshots, and general questions. How can I assist you today?";
        this.addMessage(welcomeText, 'assistant');
    }
    
    addMessage(text, role, animate = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        if (animate) {
            msgDiv.style.opacity = '0';
            msgDiv.style.transform = 'translateY(10px)';
        }
        
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        // Handle different message types
        if (role.includes('error')) {
            bubble.style.background = 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)';
            text = '⚠️ ' + text;
        }
        
        // Convert markdown-style formatting
        text = this.formatMessage(text);
        bubble.innerHTML = text;
        
        msgDiv.appendChild(bubble);
        this.chatBox.appendChild(msgDiv);
        
        if (animate) {
            // Trigger animation
            requestAnimationFrame(() => {
                msgDiv.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                msgDiv.style.opacity = '1';
                msgDiv.style.transform = 'translateY(0)';
            });
        }
        
        this.scrollToBottom();
        return msgDiv;
    }
    
    formatMessage(text) {
        // Basic markdown-style formatting
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 3px;">$1</code>');
        text = text.replace(/\n/g, '<br>');
        return text;
    }
    
    scrollToBottom() {
        this.chatBox.scrollTop = this.chatBox.scrollHeight;
    }
    
    sendMessage() {
        const text = this.userInput.value.trim();
        if (!text) return;
        
        if (!this.isConnected) {
            this.addMessage('Not connected to server. Please wait...', 'assistant error');
            return;
        }
        
        // Add user message to UI
        this.addMessage(text, 'user');
        
        // Send to server
        this.socket.emit('user_message', {
            text: text,
            conversation_id: this.conversationId
        });
        
        // Clear input
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        
        // Create placeholder for assistant response
        this.currentAssistantMessage = this.addMessage('', 'assistant', false);
        this.showTypingIndicator();
    }
    
    handleAssistantChunk(chunk) {
        if (this.currentAssistantMessage) {
            const bubble = this.currentAssistantMessage.querySelector('.bubble');
            
            // Remove typing indicator if present
            this.hideTypingIndicator();
            
            // Append chunk to existing content
            const currentText = bubble.textContent || '';
            const newText = currentText + chunk;
            bubble.innerHTML = this.formatMessage(newText);
            
            this.scrollToBottom();
        }
    }
    
    handleAssistantDone() {
        this.hideTypingIndicator();
        this.currentAssistantMessage = null;
    }
    
    showTypingIndicator() {
        if (this.currentAssistantMessage) {
            const bubble = this.currentAssistantMessage.querySelector('.bubble');
            bubble.innerHTML = '<span class="typing-indicator">Ultron is thinking</span>';
        }
    }
    
    hideTypingIndicator() {
        if (this.currentAssistantMessage) {
            const bubble = this.currentAssistantMessage.querySelector('.bubble');
            const indicator = bubble.querySelector('.typing-indicator');
            if (indicator && bubble.textContent.trim() === 'Ultron is thinking') {
                bubble.innerHTML = '';
            }
        }
    }
    
    async toggleVoiceInput() {
        if (this.isListening) {
            return; // Prevent multiple simultaneous requests
        }
        
        if (!this.isConnected) {
            this.addMessage('Voice input requires server connection.', 'assistant error');
            return;
        }
        
        this.isListening = true;
        this.micBtn.classList.add('listening');
        this.micBtn.innerHTML = '<i class="bi bi-mic-fill"></i>';
        
        try {
            // Add status message
            const statusMsg = this.addMessage('🎤 Listening... Speak now!', 'assistant');
            
            const response = await fetch('/voice', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ timeout: 10 })
            });
            
            const data = await response.json();
            
            // Remove status message
            statusMsg.remove();
            
            if (data.success && data.text) {
                this.userInput.value = data.text;
                this.addMessage(`🎤 "${data.text}"`, 'user');
                // Auto-send the message
                setTimeout(() => this.sendMessage(), 500);
            } else {
                this.addMessage('Could not understand speech. Please try again.', 'assistant error');
            }
        } catch (error) {
            console.error('Voice input error:', error);
            this.addMessage('Voice input failed. Please check your microphone.', 'assistant error');
        } finally {
            this.isListening = false;
            this.micBtn.classList.remove('listening');
            this.micBtn.innerHTML = '<i class="bi bi-mic"></i>';
        }
    }
    
    // Utility methods
    clearChat() {
        this.chatBox.innerHTML = '';
        this.addWelcomeMessage();
    }
    
    exportChat() {
        const messages = Array.from(this.chatBox.querySelectorAll('.message')).map(msg => {
            const role = msg.classList.contains('user') ? 'User' : 'Ultron';
            const text = msg.querySelector('.bubble').textContent;
            return `${role}: ${text}`;
        }).join('\n\n');
        
        const blob = new Blob([messages], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ultron-chat-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter to send message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.sendMessage();
            }
            
            // Ctrl+K to clear chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.clearChat();
            }
            
            // Ctrl+M for voice input
            if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
                e.preventDefault();
                this.toggleVoiceInput();
            }
        });
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chat = new UltronChat();
    chat.setupKeyboardShortcuts();
    
    // Make chat globally available for debugging
    window.ultronChat = chat;
    
    // Add some helpful keyboard shortcuts info
    console.log('Ultron Chat Keyboard Shortcuts:');
    console.log('Ctrl+Enter: Send message');
    console.log('Ctrl+K: Clear chat');
    console.log('Ctrl+M: Voice input');
});

// Additional utility functions
function addCustomCommand() {
    // Placeholder for future custom command functionality
    console.log('Custom commands feature coming soon...');
}

function toggleTheme() {
    // Placeholder for theme switching
    console.log('Theme switching feature coming soon...');
}

// Error handling for the entire page
window.addEventListener('error', (e) => {
    console.error('Page error:', e.error);
    if (window.ultronChat) {
        window.ultronChat.addMessage('A client-side error occurred. Please refresh the page.', 'assistant error');
    }
});

// Service worker registration (for future PWA support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}
