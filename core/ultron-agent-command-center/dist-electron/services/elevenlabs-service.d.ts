export interface ElevenLabsVoice {
    voice_id: string;
    name: string;
    category: string;
    description?: string;
    settings?: {
        stability: number;
        similarity_boost: number;
    };
}
export interface VoiceSettings {
    stability: number;
    similarity_boost: number;
    style?: number;
    use_speaker_boost?: boolean;
}
export declare class ElevenLabsService {
    private apiKey;
    private baseUrl;
    private isConnected;
    constructor();
    testConnection(): Promise<boolean>;
    getConnectionStatus(): boolean;
    getVoices(): Promise<ElevenLabsVoice[]>;
    private getDefaultVoices;
    textToSpeech(text: string, voiceId: string, settings?: VoiceSettings): Promise<Buffer | null>;
    speechToText(audioData: Buffer): Promise<string>;
    getUsage(): Promise<any>;
    validateVoiceSettings(settings: Partial<VoiceSettings>): VoiceSettings;
}
