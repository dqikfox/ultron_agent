"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OllamaService = void 0;
const axios_1 = __importDefault(require("axios"));
class OllamaService {
    constructor() {
        this.baseUrl = 'http://localhost:11434';
    }
    async getModels() {
        try {
            const response = await axios_1.default.get(`${this.baseUrl}/api/tags`);
            return response.data.models || [];
        }
        catch (error) {
            console.error('Failed to fetch Ollama models:', error);
            return [];
        }
    }
    async chatWithModel(modelName, messages) {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/api/chat`, {
                model: modelName,
                messages: messages,
                stream: false
            });
            return response.data.message?.content || 'No response';
        }
        catch (error) {
            console.error('Failed to chat with model:', error);
            throw error;
        }
    }
    async generateWithModel(modelName, prompt, images) {
        try {
            const payload = {
                model: modelName,
                prompt: prompt,
                stream: false
            };
            if (images && images.length > 0) {
                payload.images = images;
            }
            const response = await axios_1.default.post(`${this.baseUrl}/api/generate`, payload);
            return response.data.response || 'No response';
        }
        catch (error) {
            console.error('Failed to generate with model:', error);
            throw error;
        }
    }
    async checkConnection() {
        try {
            await axios_1.default.get(`${this.baseUrl}/api/tags`, { timeout: 5000 });
            return true;
        }
        catch (error) {
            return false;
        }
    }
    getModelCapabilities(modelName) {
        const name = modelName.toLowerCase();
        return {
            isVision: name.includes('vision') || name.includes('vl') || name.includes('qwen2.5vl'),
            isCode: name.includes('coder') || name.includes('starcoder') || name.includes('code'),
            isChat: name.includes('chat') || name.includes('instruct') || name.includes('hermes')
        };
    }
}
exports.OllamaService = OllamaService;
//# sourceMappingURL=ollama-service.js.map