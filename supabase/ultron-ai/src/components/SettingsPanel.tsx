import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { useAuth } from '../contexts/AuthContext'
import {
  CogIcon,
  UserIcon,
  CpuChipIcon,
  SpeakerWaveIcon,
  EyeIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface SettingsPanelProps {
  onClose: () => void
}

export function SettingsPanel({ onClose }: SettingsPanelProps) {
  const { profile, updateProfile } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || '',
    preferred_ai_provider: profile?.preferred_ai_provider || 'openai',
    voice_enabled: profile?.voice_enabled ?? false,
    system_monitoring_enabled: profile?.system_monitoring_enabled ?? true
  })

  const aiProviders = [
    { id: 'openai', name: 'OpenAI', description: 'GPT-3.5, GPT-4' },
    { id: 'deepseek', name: 'DeepSeek', description: 'DeepSeek Chat' },
    { id: 'google', name: 'Google AI', description: 'Gemini Pro' },
    { id: 'ollama', name: 'Ollama', description: 'Local Models' }
  ]

  const handleSave = async () => {
    setLoading(true)
    try {
      await updateProfile(formData)
      onClose()
    } catch (error) {
      // Error handled in AuthContext
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-2xl max-h-[80vh] overflow-y-auto scrollbar-thin"
      >
        <Card className="glass-morphism border-ultron-blue/30">
          <CardHeader>
            <CardTitle className="text-2xl font-orbitron text-white flex items-center space-x-2">
              <CogIcon className="w-6 h-6 text-ultron-blue" />
              <span>Neural Interface Settings</span>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Profile Settings */}
            <div>
              <h3 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
                <UserIcon className="w-5 h-5 text-ultron-red" />
                <span>Profile Configuration</span>
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Full Name
                  </label>
                  <Input
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="bg-ultron-dark/50 border-ultron-blue/30 text-white"
                    placeholder="Enter your full name"
                  />
                </div>
              </div>
            </div>

            {/* AI Provider Settings */}
            <div>
              <h3 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
                <CpuChipIcon className="w-5 h-5 text-ultron-purple" />
                <span>AI Provider Selection</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {aiProviders.map((provider) => (
                  <motion.div
                    key={provider.id}
                    whileHover={{ scale: 1.02 }}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      formData.preferred_ai_provider === provider.id
                        ? 'border-ultron-blue bg-ultron-blue/10'
                        : 'border-ultron-gray/30 hover:border-ultron-blue/50'
                    }`}
                    onClick={() => setFormData({ ...formData, preferred_ai_provider: provider.id })}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        formData.preferred_ai_provider === provider.id
                          ? 'bg-ultron-blue'
                          : 'bg-gray-500'
                      }`} />
                      <div>
                        <p className="text-white font-medium">{provider.name}</p>
                        <p className="text-gray-400 text-sm">{provider.description}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Feature Settings */}
            <div>
              <h3 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
                <EyeIcon className="w-5 h-5 text-ultron-red" />
                <span>Feature Configuration</span>
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-ultron-dark/30 rounded-lg border border-ultron-gray/30">
                  <div className="flex items-center space-x-3">
                    <SpeakerWaveIcon className="w-5 h-5 text-ultron-blue" />
                    <div>
                      <p className="text-white font-medium">Voice Interface</p>
                      <p className="text-gray-400 text-sm">Enable text-to-speech and voice input</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFormData({ ...formData, voice_enabled: !formData.voice_enabled })}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      formData.voice_enabled ? 'bg-ultron-blue' : 'bg-gray-600'
                    }`}
                  >
                    <motion.div
                      animate={{ x: formData.voice_enabled ? 24 : 0 }}
                      className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md"
                    />
                  </button>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-ultron-dark/30 rounded-lg border border-ultron-gray/30">
                  <div className="flex items-center space-x-3">
                    <CogIcon className="w-5 h-5 text-ultron-purple" />
                    <div>
                      <p className="text-white font-medium">System Monitoring</p>
                      <p className="text-gray-400 text-sm">Real-time system performance tracking</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFormData({ ...formData, system_monitoring_enabled: !formData.system_monitoring_enabled })}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      formData.system_monitoring_enabled ? 'bg-ultron-blue' : 'bg-gray-600'
                    }`}
                  >
                    <motion.div
                      animate={{ x: formData.system_monitoring_enabled ? 24 : 0 }}
                      className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md"
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-ultron-gray/30">
              <Button
                variant="outline"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                variant="ultron"
                onClick={handleSave}
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Saving...</span>
                  </div>
                ) : (
                  'Save Settings'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}