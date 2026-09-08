export interface Conversation {
    id?: number;
    title: string;
    model: string;
    messages: any[];
    created_at: string;
    updated_at: string;
}
export interface UserSettings {
    id?: number;
    key: string;
    value: string;
}
export declare class DatabaseService {
    private dataPath;
    private conversations;
    private settings;
    constructor();
    initialize(): Promise<void>;
    saveConversation(conversation: Conversation): Promise<number>;
    loadConversations(): Promise<Conversation[]>;
    updateConversation(id: number, conversation: Partial<Conversation>): Promise<void>;
    deleteConversation(id: number): Promise<void>;
    saveSetting(key: string, value: string): Promise<void>;
    getSetting(key: string): Promise<string | null>;
    close(): void;
}
