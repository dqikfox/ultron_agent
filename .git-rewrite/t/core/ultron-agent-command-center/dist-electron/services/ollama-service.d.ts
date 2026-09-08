export interface OllamaModel {
    name: string;
    model: string;
    modified_at: string;
    size: number;
    digest: string;
    details: {
        parent_model?: string;
        format: string;
        family: string;
        families?: string[];
        parameter_size: string;
        quantization_level: string;
    };
}
export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
    images?: string[];
}
export declare class OllamaService {
    private baseUrl;
    getModels(): Promise<OllamaModel[]>;
    chatWithModel(modelName: string, messages: ChatMessage[]): Promise<string>;
    generateWithModel(modelName: string, prompt: string, images?: string[]): Promise<string>;
    checkConnection(): Promise<boolean>;
    getModelCapabilities(modelName: string): {
        isVision: boolean;
        isCode: boolean;
        isChat: boolean;
    };
}
