import { EventEmitter } from 'events';

export interface OllamaModel {
  name: string;
  model: string;
  modified_at: string;
  size: number;
  digest: string;
  details?: {
    parent_model?: string;
    format?: string;
    family?: string;
    families?: string[];
    parameter_size?: string;
    quantization_level?: string;
  };
}

export interface OllamaModelsResponse {
  models: OllamaModel[];
}

export interface OllamaApiError {
  error: string;
  code?: string;
}

export class OllamaService extends EventEmitter {
  private baseUrl: string;
  private isConnected: boolean = false;

  constructor(baseUrl: string = 'http://localhost:11434') {
    super();
    this.baseUrl = baseUrl;
  }

  /**
   * Test connection to Ollama server
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });
      
      this.isConnected = response.ok;
      this.emit('connection-status', this.isConnected);
      return this.isConnected;
    } catch (error) {
      console.error('Ollama connection test failed:', error);
      this.isConnected = false;
      this.emit('connection-status', this.isConnected);
      return false;
    }
  }

  /**
   * Get list of available models from Ollama
   */
  async getModels(): Promise<OllamaModel[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData: OllamaApiError = await response.json();
        throw new Error(`Ollama API Error: ${errorData.error || 'Unknown error'}`);
      }

      const data: OllamaModelsResponse = await response.json();
      
      // Emit models update event
      this.emit('models-updated', data.models);
      
      return data.models;
    } catch (error) {
      console.error('Failed to fetch models from Ollama:', error);
      this.emit('models-error', error);
      throw error;
    }
  }

  /**
   * Check if Ollama is currently connected
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Get the base URL for Ollama API
   */
  getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Update the base URL for Ollama API
   */
  setBaseUrl(url: string): void {
    this.baseUrl = url;
    this.isConnected = false;
  }

  /**
   * Get model capabilities based on name
   */
  getModelCapabilities(modelName: string): {
    isVision: boolean;
    isCode: boolean;
    isChat: boolean;
  } {
    const name = modelName.toLowerCase();
    
    return {
      isVision: name.includes('vision') || name.includes('vl') || name.includes('qwen2.5vl'),
      isCode: name.includes('code') || name.includes('starcoder') || name.includes('qwen2.5-coder'),
      isChat: true, // Most models support chat
    };
  }

  /**
   * Format model size in human readable format
   */
  formatModelSize(bytes: number): string {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = (bytes / Math.pow(1024, i)).toFixed(1);
    
    return `${size} ${sizes[i]}`;
  }

  /**
   * Extract parameter count from model name
   */
  extractParameterCount(modelName: string): string {
    const name = modelName.toLowerCase();
    
    // Common patterns for parameter counts
    const patterns = [
      /:(\d+\.?\d*)b/,  // :7b, :1.5b, etc.
      /-(\d+\.?\d*)b/,  // -7b, -1.5b, etc.
      /(\d+\.?\d*)b/,   // 7b, 1.5b, etc.
      /:latest/,        // :latest tag
    ];
    
    for (const pattern of patterns) {
      const match = name.match(pattern);
      if (match && match[1]) {
        return `${match[1]}B`;
      }
    }
    
    // Special cases
    if (name.includes('mini')) return 'Mini';
    if (name.includes('large')) return 'Large';
    if (name.includes('embed')) return 'Embed';
    
    return 'Unknown';
  }
}