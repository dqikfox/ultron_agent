"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path_1 = require("path");
const utils_1 = require("./utils");
const websocket_server_1 = require("./websocket-server");
const ollama_service_1 = require("./services/ollama-service");
const elevenlabs_service_1 = require("./services/elevenlabs-service");
const database_service_1 = require("./services/database-service");
const system_metrics_service_1 = require("./services/system-metrics-service");
const tool_service_1 = require("./services/tool-service");
let mainWindow;
const ollamaService = new ollama_service_1.OllamaService();
const elevenLabsService = new elevenlabs_service_1.ElevenLabsService();
const databaseService = new database_service_1.DatabaseService();
const toolService = new tool_service_1.ToolService();
const systemMetricsService = new system_metrics_service_1.SystemMetricsService();
function createWindow() {
    // Create the browser window
    mainWindow = new electron_1.BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 800,
        show: false,
        autoHideMenuBar: true,
        frame: true,
        titleBarStyle: 'default',
        backgroundColor: '#0B0F13',
        icon: (0, path_1.join)(__dirname, '../assets/icon.png'),
        webPreferences: {
            preload: (0, path_1.join)(__dirname, 'preload.js'),
            sandbox: false,
            contextIsolation: true,
            nodeIntegration: false
        }
    });
    mainWindow.on('ready-to-show', () => {
        mainWindow.show();
    });
    mainWindow.webContents.setWindowOpenHandler((details) => {
        electron_1.shell.openExternal(details.url);
        return { action: 'deny' };
    });
    // HMR for renderer base on electron-vite cli.
    // Load the remote URL for development or the local html file for production.
    if (utils_1.is.dev && process.env['VITE_DEV_SERVER_URL']) {
        mainWindow.loadURL(process.env['VITE_DEV_SERVER_URL']);
    }
    else if (utils_1.is.dev) {
        mainWindow.loadURL('http://localhost:5173');
    }
    else {
        mainWindow.loadFile((0, path_1.join)(__dirname, '../dist/index.html'));
    }
}
// This method will be called when Electron has finished initialization
electron_1.app.whenReady().then(() => {
    // Set app user model id for windows
    electron_1.app.setAppUserModelId('com.minimax.ultron-agent');
    // Default open or close DevTools by F12 in development
    electron_1.app.on('browser-window-created', (_, window) => {
        if (utils_1.is.dev) {
            window.webContents.openDevTools();
        }
    });
    createWindow();
    // Initialize services
    databaseService.initialize();
    (0, websocket_server_1.createWebSocketServer)();
    electron_1.app.on('activate', function () {
        if (electron_1.BrowserWindow.getAllWindows().length === 0)
            createWindow();
    });
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
// IPC handlers
electron_1.ipcMain.handle('get-ollama-models', async () => {
    return await ollamaService.getModels();
});
electron_1.ipcMain.handle('chat-with-model', async (_, modelName, messages) => {
    return await ollamaService.chatWithModel(modelName, messages);
});
electron_1.ipcMain.handle('get-elevenlabs-voices', async () => {
    return await elevenLabsService.getVoices();
});
electron_1.ipcMain.handle('text-to-speech', async (_, text, voiceId, settings) => {
    return await elevenLabsService.textToSpeech(text, voiceId, settings);
});
electron_1.ipcMain.handle('speech-to-text', async (_, audioData) => {
    return await elevenLabsService.speechToText(audioData);
});
electron_1.ipcMain.handle('get-elevenlabs-usage', async () => {
    return await elevenLabsService.getUsage();
});
electron_1.ipcMain.handle('get-elevenlabs-connection-status', () => {
    return elevenLabsService.getConnectionStatus();
});
electron_1.ipcMain.handle('test-elevenlabs-connection', async () => {
    return await elevenLabsService.testConnection();
});
electron_1.ipcMain.handle('save-conversation', async (_, conversation) => {
    return await databaseService.saveConversation(conversation);
});
electron_1.ipcMain.handle('load-conversations', async () => {
    return await databaseService.loadConversations();
});
electron_1.ipcMain.handle('execute-tool', async (_, toolName, params) => {
    return await toolService.executeTool(toolName, params);
});
// System metrics handlers
electron_1.ipcMain.handle('get-system-metrics', async () => {
    return await systemMetricsService.getMetrics();
});
electron_1.ipcMain.handle('get-cpu-info', async () => {
    return await systemMetricsService.getCpuInfo();
});
electron_1.ipcMain.handle('get-memory-info', async () => {
    return await systemMetricsService.getMemoryInfo();
});
electron_1.ipcMain.handle('get-platform-info', async () => {
    return await systemMetricsService.getPlatformInfo();
});
electron_1.ipcMain.handle('check-resource-alerts', async () => {
    return systemMetricsService.checkResourceAlerts();
});
// Security and audit handlers
electron_1.ipcMain.handle('get-security-events', async (_, limit = 50) => {
    return await databaseService.getSecurityEvents(limit);
});
electron_1.ipcMain.handle('add-security-event', async (_, event, level, details) => {
    databaseService.addSecurityEvent(event, level, details);
});
electron_1.ipcMain.handle('clear-security-events', async () => {
    return await databaseService.clearSecurityEvents();
});
// Database management handlers
electron_1.ipcMain.handle('export-data', async () => {
    return await databaseService.exportData();
});
electron_1.ipcMain.handle('import-data', async (_, data) => {
    return await databaseService.importData(data);
});
electron_1.ipcMain.handle('get-conversation-stats', async () => {
    return await databaseService.getConversationStats();
});
electron_1.ipcMain.handle('get-storage-paths', async () => {
    return databaseService.getStoragePaths();
});
// Hide menu bar
electron_1.Menu.setApplicationMenu(null);
//# sourceMappingURL=main.js.map