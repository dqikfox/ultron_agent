import { app, BrowserWindow, ipcMain, Menu, shell } from 'electron'
import { join } from 'path'
import { is } from './utils'
import { createWebSocketServer } from './websocket-server'
import { OllamaService } from './services/ollama-service'
import { ElevenLabsService } from './services/elevenlabs-service'
import { DatabaseService } from './services/database-service'
import { SystemMetricsService } from './services/system-metrics-service'
import { ToolService } from './services/tool-service'

let mainWindow: BrowserWindow
const ollamaService = new OllamaService()
const elevenLabsService = new ElevenLabsService()
const databaseService = new DatabaseService()
const toolService = new ToolService()
const systemMetricsService = new SystemMetricsService()

function createWindow(): void {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    show: false,
    autoHideMenuBar: true,
    frame: true,
    titleBarStyle: 'default',
    backgroundColor: '#0B0F13',
    icon: join(__dirname, '../assets/icon.png'),
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['VITE_DEV_SERVER_URL']) {
    mainWindow.loadURL(process.env['VITE_DEV_SERVER_URL'])
  } else if (is.dev) {
    mainWindow.loadURL('http://localhost:5173')
  } else {
    mainWindow.loadFile(join(__dirname, '../dist/index.html'))
  }
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  // Set app user model id for windows
  app.setAppUserModelId('com.minimax.ultron-agent')

  // Default open or close DevTools by F12 in development
  app.on('browser-window-created', (_, window) => {
    if (is.dev) {
      window.webContents.openDevTools()
    }
  })

  createWindow()
  
  // Initialize services
  databaseService.initialize()
  createWebSocketServer()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC handlers
ipcMain.handle('get-ollama-models', async () => {
  return await ollamaService.getModels()
})

ipcMain.handle('chat-with-model', async (_, modelName: string, messages: any[]) => {
  return await ollamaService.chatWithModel(modelName, messages)
})

ipcMain.handle('get-elevenlabs-voices', async () => {
  return await elevenLabsService.getVoices()
})

ipcMain.handle('text-to-speech', async (_, text: string, voiceId: string, settings?: any) => {
  return await elevenLabsService.textToSpeech(text, voiceId, settings)
})

ipcMain.handle('speech-to-text', async (_, audioData: Buffer) => {
  return await elevenLabsService.speechToText(audioData)
})

ipcMain.handle('get-elevenlabs-usage', async () => {
  return await elevenLabsService.getUsage()
})

ipcMain.handle('get-elevenlabs-connection-status', () => {
  return elevenLabsService.getConnectionStatus()
})

ipcMain.handle('test-elevenlabs-connection', async () => {
  return await elevenLabsService.testConnection()
})

ipcMain.handle('save-conversation', async (_, conversation: any) => {
  return await databaseService.saveConversation(conversation)
})

ipcMain.handle('load-conversations', async () => {
  return await databaseService.loadConversations()
})

ipcMain.handle('execute-tool', async (_, toolName: string, params: any) => {
  return await toolService.executeTool(toolName, params)
})

// System metrics handlers
ipcMain.handle('get-system-metrics', async () => {
  return await systemMetricsService.getMetrics()
})

ipcMain.handle('get-cpu-info', async () => {
  return await systemMetricsService.getCpuInfo()
})

ipcMain.handle('get-memory-info', async () => {
  return await systemMetricsService.getMemoryInfo()
})

ipcMain.handle('get-platform-info', async () => {
  return await systemMetricsService.getPlatformInfo()
})

ipcMain.handle('check-resource-alerts', async () => {
  return systemMetricsService.checkResourceAlerts()
})

// Security and audit handlers
ipcMain.handle('get-security-events', async (_, limit: number = 50) => {
  return await databaseService.getSecurityEvents(limit)
})

ipcMain.handle('add-security-event', async (_, event: string, level: string, details?: any) => {
  databaseService.addSecurityEvent(event, level as any, details)
})

ipcMain.handle('clear-security-events', async () => {
  return await databaseService.clearSecurityEvents()
})

// Database management handlers
ipcMain.handle('export-data', async () => {
  return await databaseService.exportData()
})

ipcMain.handle('import-data', async (_, data: any) => {
  return await databaseService.importData(data)
})

ipcMain.handle('get-conversation-stats', async () => {
  return await databaseService.getConversationStats()
})

ipcMain.handle('get-storage-paths', async () => {
  return databaseService.getStoragePaths()
})

// Hide menu bar
Menu.setApplicationMenu(null)
