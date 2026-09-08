"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
// Custom APIs for renderer
const api = {
    // Ollama APIs
    getOllamaModels: () => electron_1.ipcRenderer.invoke('get-ollama-models'),
    chatWithModel: (modelName, messages) => electron_1.ipcRenderer.invoke('chat-with-model', modelName, messages),
    // ElevenLabs APIs
    getElevenLabsVoices: () => electron_1.ipcRenderer.invoke('get-elevenlabs-voices'),
    textToSpeech: (text, voiceId, settings) => electron_1.ipcRenderer.invoke('text-to-speech', text, voiceId, settings),
    speechToText: (audioData) => electron_1.ipcRenderer.invoke('speech-to-text', audioData),
    getElevenLabsUsage: () => electron_1.ipcRenderer.invoke('get-elevenlabs-usage'),
    getElevenLabsConnectionStatus: () => electron_1.ipcRenderer.invoke('get-elevenlabs-connection-status'),
    testElevenLabsConnection: () => electron_1.ipcRenderer.invoke('test-elevenlabs-connection'),
    // Database APIs
    saveConversation: (conversation) => electron_1.ipcRenderer.invoke('save-conversation', conversation),
    loadConversations: () => electron_1.ipcRenderer.invoke('load-conversations'),
    // Tool APIs
    executeTool: (toolName, params) => electron_1.ipcRenderer.invoke('execute-tool', toolName, params),
    // System Metrics APIs
    getSystemMetrics: () => electron_1.ipcRenderer.invoke('get-system-metrics'),
    getCpuInfo: () => electron_1.ipcRenderer.invoke('get-cpu-info'),
    getMemoryInfo: () => electron_1.ipcRenderer.invoke('get-memory-info'),
    getPlatformInfo: () => electron_1.ipcRenderer.invoke('get-platform-info'),
    checkResourceAlerts: () => electron_1.ipcRenderer.invoke('check-resource-alerts'),
    // Security & Audit APIs
    getSecurityEvents: (limit) => electron_1.ipcRenderer.invoke('get-security-events', limit),
    addSecurityEvent: (event, level, details) => electron_1.ipcRenderer.invoke('add-security-event', event, level, details),
    clearSecurityEvents: () => electron_1.ipcRenderer.invoke('clear-security-events'),
    // Database Management APIs
    exportData: () => electron_1.ipcRenderer.invoke('export-data'),
    importData: (data) => electron_1.ipcRenderer.invoke('import-data', data),
    getConversationStats: () => electron_1.ipcRenderer.invoke('get-conversation-stats'),
    getStoragePaths: () => electron_1.ipcRenderer.invoke('get-storage-paths'),
    // Platform info
    platform: process.platform,
};
// Use `contextBridge` APIs to expose Electron APIs to renderer
electron_1.contextBridge.exposeInMainWorld('electronAPI', api);
//# sourceMappingURL=preload.js.map