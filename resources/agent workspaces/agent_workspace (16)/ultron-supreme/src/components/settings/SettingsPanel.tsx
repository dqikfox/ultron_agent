import React, { useState, useEffect } from 'react'
import { X, Save, RotateCcw, User, Mic, Palette, Database } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { UltronLogo } from '@/components/ui/UltronLogo'

interface SettingsPanelProps {
  selectedModel: string
  onModelChange: (model: string) => void
  onClose: () => void
}

interface UserSettings {
  voiceEnabled: boolean
  voiceLanguage: string
  themeMode: 'ultron' | 'classic' | 'neon'
  autoSaveChats: boolean
  systemMonitoring: boolean
  chatHistoryLimit: number
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({ 
  selectedModel,
  onModelChange,
  onClose 
}) => {
  const { user, signIn, signUp, signOut } = useAuth()
  const [settings, setSettings] = useState<UserSettings>({
    voiceEnabled: false,
    voiceLanguage: 'en-US',
    themeMode: 'ultron',
    autoSaveChats: true,
    systemMonitoring: true,
    chatHistoryLimit: 1000
  })
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('ultron-settings')
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings))
      } catch (error) {
        console.error('Failed to parse saved settings:', error)
      }
    }
  }, [])

  const saveSettings = () => {
    localStorage.setItem('ultron-settings', JSON.stringify(settings))
    onClose()
  }

  const resetSettings = () => {
    const defaultSettings: UserSettings = {
      voiceEnabled: false,
      voiceLanguage: 'en-US',
      themeMode: 'ultron',
      autoSaveChats: true,
      systemMonitoring: true,
      chatHistoryLimit: 1000
    }
    setSettings(defaultSettings)
    localStorage.setItem('ultron-settings', JSON.stringify(defaultSettings))
  }

  const handleAuth = async () => {
    if (!email || !password) {
      setAuthError('Email and password are required')
      return
    }

    setAuthLoading(true)
    setAuthError(null)

    try {
      if (authMode === 'signin') {
        const { error } = await signIn(email, password)
        if (error) throw error
      } else {
        const { error } = await signUp(email, password)
        if (error) throw error
        setAuthError('Check your email for verification link')
      }
    } catch (error: any) {
      setAuthError(error.message || 'Authentication failed')
    } finally {
      setAuthLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-intense rounded-lg border border-red-500/30 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-red-500/20">
          <div className="flex items-center space-x-3">
            <UltronLogo size="md" />
            <h2 className="font-orbitron text-xl font-bold text-glow-red">
              SETTINGS
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-red-400 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Authentication Section */}
          <div className="glass p-4 rounded-lg border border-red-500/20">
            <div className="flex items-center space-x-2 mb-4">
              <User className="w-5 h-5 text-blue-400" />
              <h3 className="font-orbitron font-bold">AUTHENTICATION</h3>
            </div>
            
            {user ? (
              <div className="space-y-3">
                <div className="text-sm font-roboto">
                  <div className="text-gray-400">Logged in as:</div>
                  <div className="text-blue-400">{user.email}</div>
                </div>
                <button
                  onClick={() => signOut()}
                  className="btn-ultron"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex space-x-2">
                  <button
                    onClick={() => setAuthMode('signin')}
                    className={`px-4 py-2 rounded font-orbitron text-sm ${
                      authMode === 'signin' 
                        ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
                        : 'text-gray-400 hover:text-red-400'
                    }`}
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => setAuthMode('signup')}
                    className={`px-4 py-2 rounded font-orbitron text-sm ${
                      authMode === 'signup' 
                        ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
                        : 'text-gray-400 hover:text-red-400'
                    }`}
                  >
                    Sign Up
                  </button>
                </div>
                
                <div className="space-y-3">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    className="input-ultron w-full"
                  />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    className="input-ultron w-full"
                  />
                  
                  {authError && (
                    <div className="text-red-400 text-sm">{authError}</div>
                  )}
                  
                  <button
                    onClick={handleAuth}
                    disabled={authLoading}
                    className="btn-ultron w-full disabled:opacity-50"
                  >
                    {authLoading ? 'Processing...' : authMode === 'signin' ? 'Sign In' : 'Sign Up'}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Voice Settings */}
          <div className="glass p-4 rounded-lg border border-red-500/20">
            <div className="flex items-center space-x-2 mb-4">
              <Mic className="w-5 h-5 text-yellow-400" />
              <h3 className="font-orbitron font-bold">VOICE CONTROLS</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="font-roboto">Enable Voice Input</label>
                <button
                  onClick={() => setSettings(prev => ({ ...prev, voiceEnabled: !prev.voiceEnabled }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    settings.voiceEnabled ? 'bg-red-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.voiceEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              
              <div>
                <label className="block font-roboto mb-2">Voice Language</label>
                <select
                  value={settings.voiceLanguage}
                  onChange={(e) => setSettings(prev => ({ ...prev, voiceLanguage: e.target.value }))}
                  className="input-ultron w-full"
                >
                  <option value="en-US">English (US)</option>
                  <option value="en-GB">English (UK)</option>
                  <option value="es-ES">Spanish</option>
                  <option value="fr-FR">French</option>
                  <option value="de-DE">German</option>
                  <option value="zh-CN">Chinese</option>
                  <option value="ja-JP">Japanese</option>
                </select>
              </div>
            </div>
          </div>

          {/* Theme Settings */}
          <div className="glass p-4 rounded-lg border border-red-500/20">
            <div className="flex items-center space-x-2 mb-4">
              <Palette className="w-5 h-5 text-purple-400" />
              <h3 className="font-orbitron font-bold">THEME</h3>
            </div>
            
            <div className="grid grid-cols-3 gap-3">
              {(
                [
                  { id: 'ultron', name: 'Ultron', color: 'bg-red-500' },
                  { id: 'classic', name: 'Classic', color: 'bg-blue-500' },
                  { id: 'neon', name: 'Neon', color: 'bg-green-500' }
                ] as const
              ).map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => setSettings(prev => ({ ...prev, themeMode: theme.id }))}
                  className={`p-3 rounded-lg border transition-all ${
                    settings.themeMode === theme.id
                      ? 'border-red-500 bg-red-500/10'
                      : 'border-gray-600 hover:border-red-500/50'
                  }`}
                >
                  <div className={`w-6 h-6 ${theme.color} rounded mx-auto mb-2`} />
                  <div className="text-sm font-roboto">{theme.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Data Settings */}
          <div className="glass p-4 rounded-lg border border-red-500/20">
            <div className="flex items-center space-x-2 mb-4">
              <Database className="w-5 h-5 text-green-400" />
              <h3 className="font-orbitron font-bold">DATA & STORAGE</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="font-roboto">Auto-save Chats</label>
                <button
                  onClick={() => setSettings(prev => ({ ...prev, autoSaveChats: !prev.autoSaveChats }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    settings.autoSaveChats ? 'bg-red-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.autoSaveChats ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              
              <div className="flex items-center justify-between">
                <label className="font-roboto">System Monitoring</label>
                <button
                  onClick={() => setSettings(prev => ({ ...prev, systemMonitoring: !prev.systemMonitoring }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    settings.systemMonitoring ? 'bg-red-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.systemMonitoring ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
              
              <div>
                <label className="block font-roboto mb-2">
                  Chat History Limit: {settings.chatHistoryLimit}
                </label>
                <input
                  type="range"
                  min="100"
                  max="5000"
                  step="100"
                  value={settings.chatHistoryLimit}
                  onChange={(e) => setSettings(prev => ({ ...prev, chatHistoryLimit: parseInt(e.target.value) }))}
                  className="w-full accent-red-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-red-500/20">
          <button
            onClick={resetSettings}
            className="flex items-center space-x-2 text-gray-400 hover:text-red-400 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset to Defaults</span>
          </button>
          
          <button
            onClick={saveSettings}
            className="btn-ultron flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  )
}