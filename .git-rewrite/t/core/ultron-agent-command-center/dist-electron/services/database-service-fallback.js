"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DatabaseService = void 0;
const electron_1 = require("electron");
class DatabaseService {
    constructor() {
        this.conversations = [];
        this.settings = new Map();
        const userDataPath = electron_1.app.getPath('userData');
        this.dataPath = userDataPath;
    }
    async initialize() {
        console.log('Database service initialized (localStorage fallback)');
        // In a real implementation, this would set up SQLite
        // For demo purposes, we're using in-memory storage
    }
    async saveConversation(conversation) {
        const id = Date.now();
        const newConversation = {
            ...conversation,
            id,
            updated_at: new Date().toISOString()
        };
        this.conversations.unshift(newConversation);
        // Keep only last 50 conversations
        if (this.conversations.length > 50) {
            this.conversations = this.conversations.slice(0, 50);
        }
        return id;
    }
    async loadConversations() {
        return [...this.conversations];
    }
    async updateConversation(id, conversation) {
        const index = this.conversations.findIndex(conv => conv.id === id);
        if (index !== -1) {
            this.conversations[index] = {
                ...this.conversations[index],
                ...conversation,
                updated_at: new Date().toISOString()
            };
        }
    }
    async deleteConversation(id) {
        this.conversations = this.conversations.filter(conv => conv.id !== id);
    }
    async saveSetting(key, value) {
        this.settings.set(key, value);
    }
    async getSetting(key) {
        return this.settings.get(key) || null;
    }
    close() {
        console.log('Database service closed');
    }
}
exports.DatabaseService = DatabaseService;
//# sourceMappingURL=database-service-fallback.js.map