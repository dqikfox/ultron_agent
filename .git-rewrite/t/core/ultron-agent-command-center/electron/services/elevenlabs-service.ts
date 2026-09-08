import axios from 'axios'
import * as fs from 'fs'
import * as path from 'path'

export interface ElevenLabsVoice {
  voice_id: string
  name: string
  category: string
  description?: string
  settings?: {
    stability: number
    similarity_boost: number
  }
}

export interface VoiceSettings {
  stability: number
  similarity_boost: number
  style?: number
  use_speaker_boost?: boolean
}

export class ElevenLabsService {
  private apiKey: string
  private baseUrl = 'https://api.elevenlabs.io/v1'
  private isConnected: boolean = false

  constructor() {
    // Load from environment or use placeholder
    this.apiKey = process.env.ELEVENLABS_API_KEY || ''
    if (this.apiKey && this.apiKey !== 'your_elevenlabs_api_key_here') {
      this.testConnection()
    } else {
      console.warn('ElevenLabs API key not configured. Using system voices only.')
      this.isConnected = false
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      if (!this.apiKey) {
        console.warn('ElevenLabs API key not found in environment variables')
        this.isConnected = false
        return false
      }
      
      const response = await axios.get(`${this.baseUrl}/voices`, {
        headers: {
          'xi-api-key': this.apiKey
        },
        timeout: 5000
      })
      
      this.isConnected = response.status === 200
      return this.isConnected
    } catch (error) {
      console.error('ElevenLabs connection test failed:', error)
      this.isConnected = false
      return false
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected
  }

  async getVoices(): Promise<ElevenLabsVoice[]> {
    const systemVoices = this.getDefaultVoices()
    
    try {
      if (!this.apiKey || this.apiKey === 'your_elevenlabs_api_key_here') {
        console.warn('ElevenLabs API key not configured')
        return systemVoices
      }
      
      const response = await axios.get(`${this.baseUrl}/voices`, {
        headers: {
          'xi-api-key': this.apiKey
        },
        timeout: 5000
      })
      
      const elevenLabsVoices = (response.data.voices || []).map((voice: any) => ({
        voice_id: voice.voice_id,
        name: voice.name,
        category: 'elevenlabs',
        description: voice.description,
        settings: voice.settings
      }))
      
      // Combine ElevenLabs voices with system voices
      return [...elevenLabsVoices, ...systemVoices]
    } catch (error) {
      console.error('Failed to fetch ElevenLabs voices:', error)
      return systemVoices
    }
  }

  private getDefaultVoices(): ElevenLabsVoice[] {
    return [
      {
        voice_id: 'web-speech-default',
        name: 'Default System Voice',
        category: 'system',
        description: 'Browser default text-to-speech voice'
      },
      {
        voice_id: 'web-speech-male',
        name: 'System Male Voice',
        category: 'system',
        description: 'Browser male text-to-speech voice'
      },
      {
        voice_id: 'web-speech-female',
        name: 'System Female Voice',
        category: 'system',
        description: 'Browser female text-to-speech voice'
      }
    ]
  }

  async textToSpeech(text: string, voiceId: string, settings?: VoiceSettings): Promise<Buffer | null> {
    try {
      // Handle system voices (Web Speech API fallback)
      if (voiceId.startsWith('web-speech-')) {
        return null // Will be handled by Web Speech API in renderer
      }

      if (!this.apiKey) {
        throw new Error('ElevenLabs API key not found')
      }
      
      const voiceSettings: VoiceSettings = {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.5,
        use_speaker_boost: true,
        ...settings
      }
      
      const response = await axios.post(
        `${this.baseUrl}/text-to-speech/${voiceId}`,
        {
          text: text,
          model_id: 'eleven_multilingual_v2', // More advanced model
          voice_settings: voiceSettings
        },
        {
          headers: {
            'xi-api-key': this.apiKey,
            'Content-Type': 'application/json'
          },
          responseType: 'arraybuffer',
          timeout: 30000 // 30 second timeout for longer texts
        }
      )
      
      return Buffer.from(response.data)
    } catch (error) {
      console.error('Failed to convert text to speech:', error)
      return null
    }
  }

  async speechToText(audioData: Buffer): Promise<string> {
    try {
      // ElevenLabs doesn't have native STT API
      // Return a message indicating to use Web Speech API fallback
      throw new Error('STT_USE_WEB_SPEECH_API')
    } catch (error) {
      console.error('Failed to convert speech to text:', error)
      throw error
    }
  }

  // Get usage information
  async getUsage(): Promise<any> {
    try {
      if (!this.apiKey) return null
      
      const response = await axios.get(`${this.baseUrl}/user`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      })
      
      return {
        characterCount: response.data.subscription?.character_count || 0,
        characterLimit: response.data.subscription?.character_limit || 0,
        canExtendCharacterLimit: response.data.subscription?.can_extend_character_limit || false
      }
    } catch (error) {
      console.error('Failed to fetch usage:', error)
      return null
    }
  }

  // Validate voice settings
  validateVoiceSettings(settings: Partial<VoiceSettings>): VoiceSettings {
    return {
      stability: Math.max(0, Math.min(1, settings.stability || 0.5)),
      similarity_boost: Math.max(0, Math.min(1, settings.similarity_boost || 0.75)),
      style: Math.max(0, Math.min(1, settings.style || 0.5)),
      use_speaker_boost: settings.use_speaker_boost ?? true
    }
  }
}
