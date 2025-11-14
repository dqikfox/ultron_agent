/*
ULTRON AI SIMULATOR - Real AI Integration Patch
==============================================

This file shows the specific changes needed to modify ultron-ai-simulator.html
to use real AI models instead of simulated responses.

To apply these changes:
1. Replace the sendMessage() function in the NPC class
2. Replace the getResponse() function with real AI calls
3. Add AI API configuration
4. Update the character selection to use real AI models
*/

// ===== ADD THESE GLOBALS AT THE TOP OF THE SCRIPT =====

// AI API Configuration
const AI_CONFIG = {
    apiUrl: 'http://localhost:5000/api/ai',
    defaultModel: 'llama3',
    timeout: 10000, // 10 seconds
    retryAttempts: 3
};

// Model availability cache
let availableModels = [];
let aiServiceStatus = 'unknown';

// ===== REPLACE THE sendMessage() FUNCTION IN THE NPC CLASS =====

async sendMessage(message) {
    try {
        // Show thinking indicator
        this.showThinkingIndicator();
        
        // Prepare AI request
        const requestData = {
            npc_id: this.id,
            model: this.model,
            persona_data: {
                name: this.persona.name,
                description: this.persona.description,
                traits: this.persona.traits,
                hunger: this.hunger,
                thirst: this.thirst,
                happiness: this.happiness,
                hp: this.hp,
                goal: this.goal
            },
            message: message
        };

        // Call AI API
        const response = await this.callAI(requestData);
        
        if (response && response.response) {
            this.speak(response.response);
            this.addLog(`Player → ${this.persona.name}: "${message}"`);
            this.addLog(`${this.persona.name} → Player: "${response.response}"`);
            
            // Store interaction in memory
            this.memory.push({
                type: 'conversation',
                player_message: message,
                npc_response: response.response,
                timestamp: Date.now()
            });
            
            // Keep only last 5 conversations
            if (this.memory.length > 5) {
                this.memory.shift();
            }
        } else {
            throw new Error('No response from AI service');
        }
    } catch (error) {
        console.error('AI API Error:', error);
        
        // Fallback to simulated response
        const fallbackResponse = this.getSimulatedResponse(message);
        this.speak(fallbackResponse);
        this.addLog(`[AI SERVICE ERROR] Using fallback: ${fallbackResponse}`);
    } finally {
        this.hideThinkingIndicator();
    }
}

// ===== ADD THESE NEW HELPER FUNCTIONS TO THE NPC CLASS =====

async callAI(requestData) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), AI_CONFIG.timeout);
    
    try {
        const response = await fetch(`${AI_CONFIG.apiUrl}/response`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

getSimulatedResponse(message) {
    // Fallback responses when AI service is unavailable
    const responses = this.getResponse();
    return responses[Math.floor(Math.random() * responses.length)];
}

showThinkingIndicator() {
    if (this.thinkingIndicator) {
        this.hideThinkingIndicator();
    }
    
    const indicator = document.createElement('div');
    indicator.style.cssText = `
        position: absolute;
        top: -30px;
        left: 50%;
        transform: translateX(-50%);
        background: #4a90e2;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 10px;
        animation: pulse 1s infinite;
        z-index: 1000;
    `;
    indicator.textContent = '🤔 Thinking...';
    indicator.className = 'thinking-indicator';
    
    this.sprite.appendChild(indicator);
    this.thinkingIndicator = indicator;
}

hideThinkingIndicator() {
    if (this.thinkingIndicator) {
        this.thinkingIndicator.remove();
        this.thinkingIndicator = null;
    }
}

// ===== REPLACE THE getResponse() FUNCTION =====

async getResponse() {
    try {
        // Check if AI service is available
        if (aiServiceStatus !== 'connected') {
            await this.checkAIServiceStatus();
        }
        
        if (aiServiceStatus === 'connected') {
            // Generate context for AI
            const context = this.buildContextPrompt();
            
            const requestData = {
                npc_id: this.id,
                model: this.model,
                persona_data: {
                    name: this.persona.name,
                    description: this.persona.description,
                    traits: this.persona.traits,
                    hunger: this.hunger,
                    thirst: this.thirst,
                    happiness: this.happiness,
                    hp: this.hp,
                    goal: this.goal
                },
                message: null // Null means internal monologue
            };
            
            const response = await this.callAI(requestData);
            
            if (response && response.response) {
                return [response.response]; // Return as array for compatibility
            }
        }
        
        // Fallback to simulated responses if AI unavailable
        throw new Error('AI service unavailable');
        
    } catch (error) {
        console.warn('AI response failed, using simulation:', error);
        return this.getSimulatedResponse();
    }
}

buildContextPrompt() {
    return `You are ${this.persona.name}, ${this.persona.description}.
    
Current state: Hunger ${this.hunger}/100, Thirst ${this.thirst}/100, 
Happiness ${this.happiness}/100, HP ${this.hp}/100, Goal: ${this.goal}
    
Personality: ${this.persona.traits.join(', ')}

Provide a brief internal monologue or observation based on your current state and personality.`;
}

async checkAIServiceStatus() {
    try {
        const response = await fetch(`${AI_CONFIG.apiUrl}/model-status`);
        const status = await response.json();
        
        aiServiceStatus = status.status;
        availableModels = status.available_models || [];
        
        if (aiServiceStatus === 'connected') {
            this.updateModelStatus('🟢 Connected to AI service', 'success');
        } else {
            this.updateModelStatus('🔴 AI service unavailable', 'error');
        }
        
    } catch (error) {
        aiServiceStatus = 'disconnected';
        this.updateModelStatus('🔴 AI service disconnected', 'error');
    }
}

updateModelStatus(message, type) {
    const statusElement = document.querySelector('.model-status span');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

// ===== ADD INITIALIZATION CODE (call this after DOM loaded) =====

async function initializeAIService() {
    // Check AI service status on load
    try {
        const response = await fetch(`${AI_CONFIG.apiUrl}/model-status`);
        const status = await response.json();
        
        if (status.status === 'connected') {
            aiServiceStatus = 'connected';
            availableModels = status.available_models;
            console.log('🤖 AI Service connected. Available models:', availableModels);
        } else {
            aiServiceStatus = 'disconnected';
            console.log('⚠️ AI Service unavailable, using simulation mode');
        }
    } catch (error) {
        aiServiceStatus = 'disconnected';
        console.log('⚠️ AI Service offline, using simulation mode');
    }
}

// ===== ADD THIS TO YOUR DOMContentLoaded EVENT =====

document.addEventListener('DOMContentLoaded', () => {
    requestAnimationFrame(gameLoop);
    
    // Initialize AI service
    initializeAIService();
    
    // Update model dropdown based on availability
    updateModelDropdown();
    
    console.log('ULTRON AI SIMULATOR initialized with AI integration');
});

// ===== ADD HELPER FUNCTION FOR MODEL DROPDOWN =====

function updateModelDropdown() {
    const modelSelect = document.getElementById('model-select');
    if (!modelSelect) return;
    
    // Clear existing options
    modelSelect.innerHTML = '';
    
    if (aiServiceStatus === 'connected' && availableModels.length > 0) {
        // Add available AI models
        availableModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = `🤖 ${model} (AI)`;
            modelSelect.appendChild(option);
        });
    }
    
    // Always add simulation options as fallback
    const simulationOptions = [
        { value: 'sim_wizard', text: '🧙 Simulated Wizard' },
        { value: 'sim_warrior', text: '⚔️ Simulated Warrior' },
        { value: 'sim_rogue', text: '🗡️ Simulated Rogue' },
        { value: 'sim_cleric', text: '⛪ Simulated Cleric' },
        { value: 'sim_goblin', text: '👹 Simulated Goblin' }
    ];
    
    simulationOptions.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        modelSelect.appendChild(optionElement);
    });
}

// ===== MODIFY NPC CONSTRUCTOR TO HANDLE SIMULATION MODELS =====

// Add this check in the NPC constructor after creating the sprite:
if (this.model.startsWith('sim_')) {
    this.useSimulation = true;
    this.model = this.model.replace('sim_', ''); // Get the character type
} else {
    this.useSimulation = false;
}

// ===== CSS ADDITIONS (Add to your <style> section) =====

.thinking-indicator {
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/*
INTEGRATION INSTRUCTIONS:
========================

1. Start the AI Integration Server:
   python ai_integration_server.py

2. Make sure Ollama is running:
   ollama serve
   ollama pull llama3

3. Apply these code changes to your HTML file

4. The system will automatically:
   - Detect available AI models
   - Use AI responses when service is available
   - Fallback to simulation when AI is unavailable
   - Show connection status in the UI

5. Monitor the browser console for AI service status messages

The system gracefully handles AI service outages by falling back to
simulation mode, ensuring the game always remains playable.
*/