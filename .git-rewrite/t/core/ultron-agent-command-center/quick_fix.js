// Quick fix for Ultron Agent Command Center
// This will patch the main issues

const fs = require('fs');
const path = require('path');

console.log('🔧 Applying quick fixes for Ultron Agent...');

// 1. Fix the Ollama service to work with qwen2.5-coder:7b-instruct
const ollamaServicePath = path.join(__dirname, 'electron', 'services', 'ollama-service.ts');
const ollamaServiceContent = `
import axios from 'axios'

export class OllamaService {
  private baseUrl = 'http://localhost:11434'

  async getModels() {
    try {
      const response = await axios.get(\`\${this.baseUrl}/api/tags\`)
      return response.data.models || []
    } catch (error) {
      console.error('Failed to get Ollama models:', error)
      return []
    }
  }

  async chatWithModel(modelName: string, messages: any[]) {
    try {
      console.log('Sending to Ollama:', { modelName, messageCount: messages.length })
      
      const response = await axios.post(\`\${this.baseUrl}/api/chat\`, {
        model: modelName,
        messages: messages,
        stream: false
      })

      const content = response.data.message?.content || 'No response from model'
      console.log('Ollama response:', content.substring(0, 100) + '...')
      
      return content
    } catch (error) {
      console.error('Chat with model failed:', error)
      throw new Error(\`Failed to chat with model \${modelName}: \${error.message}\`)
    }
  }
}
`;

// 2. Create a simple test HTML file
const testHtmlPath = path.join(__dirname, 'test_chat.html');
const testHtmlContent = `
<!DOCTYPE html>
<html>
<head>
    <title>Ultron Chat Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: white; }
        .chat { max-width: 800px; margin: 0 auto; }
        .messages { height: 400px; overflow-y: auto; border: 1px solid #333; padding: 10px; background: #2a2a2a; margin-bottom: 10px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #0066cc; text-align: right; }
        .assistant { background: #333; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; background: #333; color: white; border: 1px solid #555; }
        button { padding: 10px 20px; background: #0066cc; color: white; border: none; cursor: pointer; }
        button:disabled { background: #666; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="chat">
        <h1>🤖 Ultron Chat Test - qwen2.5-coder:7b-instruct</h1>
        <div id="messages" class="messages">
            <div class="message assistant">Ready to chat! Using qwen2.5-coder:7b-instruct model.</div>
        </div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message...">
            <button onclick="sendMessage()" id="sendBtn">Send</button>
        </div>
    </div>

    <script>
        let isLoading = false;

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const messages = document.getElementById('messages');
            const sendBtn = document.getElementById('sendBtn');
            
            if (!input.value.trim() || isLoading) return;

            const userMessage = input.value.trim();
            input.value = '';
            
            // Add user message
            const userDiv = document.createElement('div');
            userDiv.className = 'message user';
            userDiv.textContent = userMessage;
            messages.appendChild(userDiv);
            
            // Show loading
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant';
            loadingDiv.textContent = '🤔 Thinking...';
            loadingDiv.id = 'loading';
            messages.appendChild(loadingDiv);
            
            isLoading = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            
            try {
                // Test with direct Ollama API call
                const response = await fetch('http://localhost:11434/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'qwen2.5-coder:7b-instruct',
                        messages: [{ role: 'user', content: userMessage }],
                        stream: false
                    })
                });

                if (!response.ok) {
                    throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
                }

                const data = await response.json();
                const aiResponse = data.message?.content || 'No response received';
                
                // Remove loading message
                document.getElementById('loading').remove();
                
                // Add AI response
                const aiDiv = document.createElement('div');
                aiDiv.className = 'message assistant';
                aiDiv.textContent = aiResponse;
                messages.appendChild(aiDiv);
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('loading').textContent = \`❌ Error: \${error.message}\`;
            }
            
            isLoading = false;
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            messages.scrollTop = messages.scrollHeight;
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isLoading) sendMessage();
        });
    </script>
</body>
</html>
`;

// Write the files
try {
    // Create services directory if it doesn't exist
    const servicesDir = path.join(__dirname, 'electron', 'services');
    if (!fs.existsSync(servicesDir)) {
        fs.mkdirSync(servicesDir, { recursive: true });
    }
    
    fs.writeFileSync(ollamaServicePath, ollamaServiceContent);
    fs.writeFileSync(testHtmlPath, testHtmlContent);
    
    console.log('✅ Quick fixes applied!');
    console.log('📁 Files created:');
    console.log('  - electron/services/ollama-service.ts (fixed)');
    console.log('  - test_chat.html (test interface)');
    console.log('');
    console.log('🚀 Next steps:');
    console.log('1. Open test_chat.html in browser to test Ollama connection');
    console.log('2. Run: npm run build && npm run dist:win');
    console.log('3. Test the rebuilt app');
    
} catch (error) {
    console.error('❌ Error applying fixes:', error.message);
}