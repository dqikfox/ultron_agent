declare global {
  interface Window {
    electronAPI: {
      // Ollama APIs
      getOllamaModels: () => Promise<any[]>
      chatWithModel: (modelName: string, messages: any[]) => Promise<string>
      
      // ElevenLabs APIs
      getElevenLabsVoices: () => Promise<any[]>
      textToSpeech: (text: string, voiceId: string, settings?: any) => Promise<ArrayBuffer | null>
      speechToText: (audioData: ArrayBuffer) => Promise<string>
      getElevenLabsUsage: () => Promise<any>
      getElevenLabsConnectionStatus: () => Promise<boolean>
      testElevenLabsConnection: () => Promise<boolean>
      
      // Database APIs
      saveConversation: (conversation: any) => Promise<number>
      loadConversations: () => Promise<any[]>
      
      // Tool APIs
      executeTool: (toolName: string, params: any) => Promise<any>
      
      // System Metrics APIs
      getSystemMetrics: () => Promise<any>
      getCpuInfo: () => Promise<any>
      getMemoryInfo: () => Promise<any>
      getPlatformInfo: () => Promise<any>
      checkResourceAlerts: () => Promise<any>
      
      // Security & Audit APIs
      getSecurityEvents: (limit?: number) => Promise<any[]>
      addSecurityEvent: (event: string, level: string, details?: any) => Promise<void>
      clearSecurityEvents: () => Promise<void>
      
      // Database Management APIs
      exportData: () => Promise<any>
      importData: (data: any) => Promise<void>
      getConversationStats: () => Promise<any>
      getStoragePaths: () => Promise<any>
      
      // Platform info
      platform: string
    }
  }
}

export {}
