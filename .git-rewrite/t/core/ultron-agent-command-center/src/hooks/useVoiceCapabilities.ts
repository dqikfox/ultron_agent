import { useState, useEffect, useCallback } from 'react'

export interface VoiceCapability {
  sttAvailable: boolean
  ttsAvailable: boolean
  elevenLabsConnected: boolean
  webSpeechAvailable: boolean
}

export function useVoiceCapabilities() {
  const [capabilities, setCapabilities] = useState<VoiceCapability>({
    sttAvailable: false,
    ttsAvailable: false,
    elevenLabsConnected: false,
    webSpeechAvailable: false
  })

  useEffect(() => {
    checkCapabilities()
  }, [])

  const checkCapabilities = useCallback(async () => {
    try {
      // Check ElevenLabs connection
      const elevenLabsStatus = await window.electronAPI.getElevenLabsConnectionStatus()
      
      // Check Web Speech API support
      const webSpeechSTT = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
      const webSpeechTTS = 'speechSynthesis' in window
      
      setCapabilities({
        sttAvailable: webSpeechSTT, // STT via Web Speech API
        ttsAvailable: elevenLabsStatus || webSpeechTTS, // TTS via ElevenLabs or Web Speech
        elevenLabsConnected: elevenLabsStatus,
        webSpeechAvailable: webSpeechSTT && webSpeechTTS
      })
    } catch (error) {
      console.error('Failed to check voice capabilities:', error)
      
      // Fallback to Web Speech API only
      const webSpeechSTT = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
      const webSpeechTTS = 'speechSynthesis' in window
      
      setCapabilities({
        sttAvailable: webSpeechSTT,
        ttsAvailable: webSpeechTTS,
        elevenLabsConnected: false,
        webSpeechAvailable: webSpeechSTT && webSpeechTTS
      })
    }
  }, [])

  const refreshCapabilities = useCallback(() => {
    checkCapabilities()
  }, [checkCapabilities])

  return {
    capabilities,
    refreshCapabilities,
    isVoiceReady: capabilities.sttAvailable || capabilities.ttsAvailable
  }
}