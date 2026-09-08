"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DatabaseService = void 0;
const electron_store_1 = __importDefault(require("electron-store"));
const electron_1 = require("electron");
class DatabaseService {
    constructor() {
        // Initialize electron-store instances
        this.conversationStore = new electron_store_1.default({
            name: 'conversations',
            defaults: {
                conversations: []
            },
            cwd: electron_1.app.getPath('userData')
        });
        this.settingsStore = new electron_store_1.default({
            name: 'settings',
            defaults: {},
            cwd: electron_1.app.getPath('userData')
        });
        this.securityStore = new electron_store_1.default({
            name: 'security',
            defaults: {
                events: []
            },
            cwd: electron_1.app.getPath('userData')
        });
        // Initialize conversation ID counter
        const conversations = this.conversationStore.get('conversations', []);
        this.conversationIdCounter = conversations.length > 0
            ? Math.max(...conversations.map((c) => c.id || 0)) + 1
            : 1;
    }
    async initialize() {
        console.log('Database service initialized with electron-store');
        console.log('Data directory:', electron_1.app.getPath('userData'));
        // Add initial security event
        this.addSecurityEvent('System startup', 'info', { timestamp: new Date().toISOString() });
    }
    async saveConversation(conversation) {
        const conversations = this.conversationStore.get('conversations', []);
        const id = this.conversationIdCounter++;
        const newConversation = {
            ...conversation,
            id,
            created_at: conversation.created_at || new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        conversations.unshift(newConversation);
        // Keep only last 100 conversations
        if (conversations.length > 100) {
            conversations.splice(100);
        }
        this.conversationStore.set('conversations', conversations);
        this.addSecurityEvent(`Conversation saved: ${newConversation.title}`, 'info', {
            conversationId: id,
            model: newConversation.model,
            messageCount: newConversation.messages.length
        });
        return id;
    }
    async loadConversations() {
        const conversations = this.conversationStore.get('conversations', []);
        return conversations.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
    }
    async updateConversation(id, conversation) {
        const conversations = this.conversationStore.get('conversations', []);
        const index = conversations.findIndex(conv => conv.id === id);
        if (index !== -1) {
            conversations[index] = {
                ...conversations[index],
                ...conversation,
                updated_at: new Date().toISOString()
            };
            this.conversationStore.set('conversations', conversations);
            this.addSecurityEvent(`Conversation updated: ${conversations[index].title}`, 'info', {
                conversationId: id
            });
        }
    }
    async deleteConversation(id) {
        const conversations = this.conversationStore.get('conversations', []);
        const conversation = conversations.find(conv => conv.id === id);
        if (conversation) {
            const filteredConversations = conversations.filter(conv => conv.id !== id);
            this.conversationStore.set('conversations', filteredConversations);
            this.addSecurityEvent(`Conversation deleted: ${conversation.title}`, 'warning', {
                conversationId: id
            });
        }
    }
    async saveSetting(key, value) {
        this.settingsStore.set(key, value);
        this.addSecurityEvent(`Setting updated: ${key}`, 'info', {
            key,
            hasValue: !!value
        });
    }
    async getSetting(key) {
        return this.settingsStore.get(key) || null;
    }
    async getAllSettings() {
        return this.settingsStore.store;
    }
    addSecurityEvent(event, level, details) {
        const events = this.securityStore.get('events', []);
        const newEvent = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            event,
            level,
            details
        };
        events.unshift(newEvent);
        // Keep only last 500 security events
        if (events.length > 500) {
            events.splice(500);
        }
        this.securityStore.set('events', events);
    }
    async getSecurityEvents(limit = 50) {
        const events = this.securityStore.get('events', []);
        return events.slice(0, limit);
    }
    async clearSecurityEvents() {
        this.securityStore.set('events', []);
        this.addSecurityEvent('Security log cleared', 'warning');
    }
    // Statistics and analytics
    async getConversationStats() {
        const conversations = this.conversationStore.get('conversations', []);
        const byModel = {};
        let totalMessages = 0;
        conversations.forEach(conv => {
            byModel[conv.model] = (byModel[conv.model] || 0) + 1;
            totalMessages += conv.messages.length;
        });
        return {
            total: conversations.length,
            byModel,
            totalMessages,
            averageMessagesPerConversation: conversations.length > 0
                ? totalMessages / conversations.length
                : 0
        };
    }
    // Backup and restore
    async exportData() {
        return {
            conversations: this.conversationStore.get('conversations', []),
            settings: this.settingsStore.store,
            securityEvents: this.securityStore.get('events', []),
            exportedAt: new Date().toISOString()
        };
    }
    async importData(data) {
        if (data.conversations) {
            this.conversationStore.set('conversations', data.conversations);
            // Update counter
            const maxId = data.conversations.reduce((max, conv) => Math.max(max, conv.id || 0), 0);
            this.conversationIdCounter = maxId + 1;
        }
        if (data.settings) {
            Object.entries(data.settings).forEach(([key, value]) => {
                this.settingsStore.set(key, value);
            });
        }
        if (data.securityEvents) {
            this.securityStore.set('events', data.securityEvents);
        }
        this.addSecurityEvent('Data imported successfully', 'success', {
            conversationsImported: data.conversations?.length || 0,
            settingsImported: Object.keys(data.settings || {}).length,
            eventsImported: data.securityEvents?.length || 0
        });
    }
    close() {
        this.addSecurityEvent('Database service shutdown', 'info');
        console.log('Database service closed');
    }
    // Get storage paths for debugging
    getStoragePaths() {
        return {
            conversations: this.conversationStore.path,
            settings: this.settingsStore.path,
            security: this.securityStore.path,
            userData: electron_1.app.getPath('userData')
        };
    }
}
exports.DatabaseService = DatabaseService;
//# sourceMappingURL=database-service.js.map