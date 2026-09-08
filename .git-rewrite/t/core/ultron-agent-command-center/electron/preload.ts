import { contextBridge, ipcRenderer } from 'electron'

// Custom APIs for renderer
const api = {
  // Ollama APIs
  getOllamaModels: () => ipcRenderer.invoke('get-ollama-models'),
  chatWithModel: (modelName: string, messages: any[]) => 
    ipcRenderer.invoke('chat-with-model', modelName, messages),
  
  // ElevenLabs APIs
  getElevenLabsVoices: () => ipcRenderer.invoke('get-elevenlabs-voices'),
  textToSpeech: (text: string, voiceId: string, settings?: any) => 
    ipcRenderer.invoke('text-to-speech', text, voiceId, settings),
  speechToText: (audioData: ArrayBuffer) => 
    ipcRenderer.invoke('speech-to-text', audioData),
  getElevenLabsUsage: () => ipcRenderer.invoke('get-elevenlabs-usage'),
  getElevenLabsConnectionStatus: () => ipcRenderer.invoke('get-elevenlabs-connection-status'),
  testElevenLabsConnection: () => ipcRenderer.invoke('test-elevenlabs-connection'),
  
  // Database APIs
  saveConversation: (conversation: any) => 
    ipcRenderer.invoke('save-conversation', conversation),
  loadConversations: () => ipcRenderer.invoke('load-conversations'),
  
  // Tool APIs
  executeTool: (toolName: string, params: any) => 
    ipcRenderer.invoke('execute-tool', toolName, params),
  
  // System Metrics APIs
  getSystemMetrics: () => ipcRenderer.invoke('get-system-metrics'),
  getCpuInfo: () => ipcRenderer.invoke('get-cpu-info'),
  getMemoryInfo: () => ipcRenderer.invoke('get-memory-info'),
  getPlatformInfo: () => ipcRenderer.invoke('get-platform-info'),
  checkResourceAlerts: () => ipcRenderer.invoke('check-resource-alerts'),
  
  // Security & Audit APIs
  getSecurityEvents: (limit?: number) => ipcRenderer.invoke('get-security-events', limit),
  addSecurityEvent: (event: string, level: string, details?: any) => 
    ipcRenderer.invoke('add-security-event', event, level, details),
  clearSecurityEvents: () => ipcRenderer.invoke('clear-security-events'),
  
  // Database Management APIs
  exportData: () => ipcRenderer.invoke('export-data'),
  importData: (data: any) => ipcRenderer.invoke('import-data', data),
  getConversationStats: () => ipcRenderer.invoke('get-conversation-stats'),
  getStoragePaths: () => ipcRenderer.invoke('get-storage-paths'),
  
  // Platform info
  platform: process.platform,
}

// Use `contextBridge` APIs to expose Electron APIs to renderer
contextBridge.exposeInMainWorld('electronAPI', api)

export type ElectronAPI = typeof api
