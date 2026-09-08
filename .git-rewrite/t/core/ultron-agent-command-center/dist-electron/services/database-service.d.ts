export interface Conversation {
    id?: number;
    title: string;
    model: string;
    messages: any[];
    created_at: string;
    updated_at: string;
}
export interface UserSettings {
    key: string;
    value: string;
}
export interface SecurityEvent {
    id: string;
    timestamp: string;
    event: string;
    level: 'info' | 'warning' | 'error' | 'success';
    details?: any;
}
export declare class DatabaseService {
    private conversationStore;
    private settingsStore;
    private securityStore;
    private conversationIdCounter;
    constructor();
    initialize(): Promise<void>;
    saveConversation(conversation: Conversation): Promise<number>;
    loadConversations(): Promise<Conversation[]>;
    updateConversation(id: number, conversation: Partial<Conversation>): Promise<void>;
    deleteConversation(id: number): Promise<void>;
    saveSetting(key: string, value: string): Promise<void>;
    getSetting(key: string): Promise<string | null>;
    getAllSettings(): Promise<{
        [key: string]: string;
    }>;
    addSecurityEvent(event: string, level: SecurityEvent['level'], details?: any): void;
    getSecurityEvents(limit?: number): Promise<SecurityEvent[]>;
    clearSecurityEvents(): Promise<void>;
    getConversationStats(): Promise<{
        total: number;
        byModel: {
            [model: string]: number;
        };
        totalMessages: number;
        averageMessagesPerConversation: number;
    }>;
    exportData(): Promise<{
        conversations: Conversation[];
        settings: {
            [key: string]: string;
        };
        securityEvents: SecurityEvent[];
        exportedAt: string;
    }>;
    importData(data: {
        conversations?: Conversation[];
        settings?: {
            [key: string]: string;
        };
        securityEvents?: SecurityEvent[];
    }): Promise<void>;
    close(): void;
    getStoragePaths(): {
        conversations: string;
        settings: string;
        security: string;
        userData: string;
    };
}
