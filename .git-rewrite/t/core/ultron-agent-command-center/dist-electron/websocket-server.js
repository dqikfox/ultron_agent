"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createWebSocketServer = createWebSocketServer;
const ws_1 = __importDefault(require("ws"));
const ollama_service_1 = require("./services/ollama-service");
function createWebSocketServer() {
    const wss = new ws_1.default.Server({ port: 8080 });
    const ollamaService = new ollama_service_1.OllamaService();
    wss.on('connection', (ws) => {
        console.log('WebSocket client connected');
        ws.on('message', async (message) => {
            try {
                const data = JSON.parse(message);
                switch (data.type) {
                    case 'stream-chat':
                        await handleStreamChat(ws, data, ollamaService);
                        break;
                    case 'ping':
                        ws.send(JSON.stringify({ type: 'pong' }));
                        break;
                    default:
                        ws.send(JSON.stringify({
                            type: 'error',
                            message: 'Unknown message type'
                        }));
                }
            }
            catch (error) {
                ws.send(JSON.stringify({
                    type: 'error',
                    message: 'Invalid message format'
                }));
            }
        });
        ws.on('close', () => {
            console.log('WebSocket client disconnected');
        });
        // Send welcome message
        ws.send(JSON.stringify({
            type: 'welcome',
            message: 'Connected to Ultron Agent Command Center'
        }));
    });
    console.log('WebSocket server started on port 8080');
    return wss;
}
async function handleStreamChat(ws, data, ollamaService) {
    try {
        const { modelName, messages } = data;
        // Start streaming response
        ws.send(JSON.stringify({
            type: 'stream-start',
            id: data.id
        }));
        // For now, we'll send the complete response
        // In a full implementation, you'd implement true streaming
        const response = await ollamaService.chatWithModel(modelName, messages);
        // Simulate streaming by sending chunks
        const words = response.split(' ');
        for (let i = 0; i < words.length; i++) {
            const chunk = words[i] + (i < words.length - 1 ? ' ' : '');
            ws.send(JSON.stringify({
                type: 'stream-chunk',
                id: data.id,
                content: chunk
            }));
            // Small delay to simulate streaming
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        ws.send(JSON.stringify({
            type: 'stream-end',
            id: data.id
        }));
    }
    catch (error) {
        ws.send(JSON.stringify({
            type: 'stream-error',
            id: data.id,
            message: error instanceof Error ? error.message : 'Unknown error'
        }));
    }
}
//# sourceMappingURL=websocket-server.js.map