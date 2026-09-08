"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ElevenLabsService = void 0;
const axios_1 = __importDefault(require("axios"));
class ElevenLabsService {
    constructor() {
        this.baseUrl = 'https://api.elevenlabs.io/v1';
        this.isConnected = false;
        this.apiKey = process.env.ELEVENLABS_API_KEY || '';
        this.testConnection();
    }
    async testConnection() {
        try {
            if (!this.apiKey) {
                console.warn('ElevenLabs API key not found in environment variables');
                this.isConnected = false;
                return false;
            }
            const response = await axios_1.default.get(`${this.baseUrl}/voices`, {
                headers: {
                    'xi-api-key': this.apiKey
                },
                timeout: 5000
            });
            this.isConnected = response.status === 200;
            return this.isConnected;
        }
        catch (error) {
            console.error('ElevenLabs connection test failed:', error);
            this.isConnected = false;
            return false;
        }
    }
    getConnectionStatus() {
        return this.isConnected;
    }
    async getVoices() {
        try {
            if (!this.apiKey) {
                console.warn('ElevenLabs API key not found');
                return this.getDefaultVoices();
            }
            const response = await axios_1.default.get(`${this.baseUrl}/voices`, {
                headers: {
                    'xi-api-key': this.apiKey
                }
            });
            const voices = response.data.voices || [];
            return voices.map((voice) => ({
                voice_id: voice.voice_id,
                name: voice.name,
                category: voice.category || 'unknown',
                description: voice.description,
                settings: voice.settings
            }));
        }
        catch (error) {
            console.error('Failed to fetch ElevenLabs voices:', error);
            return this.getDefaultVoices();
        }
    }
    getDefaultVoices() {
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
        ];
    }
    async textToSpeech(text, voiceId, settings) {
        try {
            // Handle system voices (Web Speech API fallback)
            if (voiceId.startsWith('web-speech-')) {
                return null; // Will be handled by Web Speech API in renderer
            }
            if (!this.apiKey) {
                throw new Error('ElevenLabs API key not found');
            }
            const voiceSettings = {
                stability: 0.5,
                similarity_boost: 0.75,
                style: 0.5,
                use_speaker_boost: true,
                ...settings
            };
            const response = await axios_1.default.post(`${this.baseUrl}/text-to-speech/${voiceId}`, {
                text: text,
                model_id: 'eleven_multilingual_v2', // More advanced model
                voice_settings: voiceSettings
            }, {
                headers: {
                    'xi-api-key': this.apiKey,
                    'Content-Type': 'application/json'
                },
                responseType: 'arraybuffer',
                timeout: 30000 // 30 second timeout for longer texts
            });
            return Buffer.from(response.data);
        }
        catch (error) {
            console.error('Failed to convert text to speech:', error);
            return null;
        }
    }
    async speechToText(audioData) {
        try {
            // ElevenLabs doesn't have native STT API
            // Return a message indicating to use Web Speech API fallback
            throw new Error('STT_USE_WEB_SPEECH_API');
        }
        catch (error) {
            console.error('Failed to convert speech to text:', error);
            throw error;
        }
    }
    // Get usage information
    async getUsage() {
        try {
            if (!this.apiKey)
                return null;
            const response = await axios_1.default.get(`${this.baseUrl}/user`, {
                headers: {
                    'xi-api-key': this.apiKey
                }
            });
            return {
                characterCount: response.data.subscription?.character_count || 0,
                characterLimit: response.data.subscription?.character_limit || 0,
                canExtendCharacterLimit: response.data.subscription?.can_extend_character_limit || false
            };
        }
        catch (error) {
            console.error('Failed to fetch usage:', error);
            return null;
        }
    }
    // Validate voice settings
    validateVoiceSettings(settings) {
        return {
            stability: Math.max(0, Math.min(1, settings.stability || 0.5)),
            similarity_boost: Math.max(0, Math.min(1, settings.similarity_boost || 0.75)),
            style: Math.max(0, Math.min(1, settings.style || 0.5)),
            use_speaker_boost: settings.use_speaker_boost ?? true
        };
    }
}
exports.ElevenLabsService = ElevenLabsService;
//# sourceMappingURL=elevenlabs-service.js.map