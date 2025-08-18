import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import toast from 'react-hot-toast'

interface VoiceHook {
  isListening: boolean
  isSupported: boolean
  transcript: string
  startListening: () => void
  stopListening: () => void
  resetTranscript: () => void
  speakText: (text: string, voice?: string) => Promise<void>
  isSpeaking: boolean
}

export function useVoice(): VoiceHook {
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [recognition, setRecognition] = useState<any>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    
    if (SpeechRecognition) {
      setIsSupported(true)
      const recognitionInstance = new SpeechRecognition()
      recognitionInstance.continuous = true
      recognitionInstance.interimResults = true
      recognitionInstance.lang = 'en-US'

      recognitionInstance.onresult = (event: any) => {
        let finalTranscript = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript)
        }
      }

      recognitionInstance.onstart = () => {
        setIsListening(true)
      }

      recognitionInstance.onend = () => {
        setIsListening(false)
      }

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        toast.error('Speech recognition error: ' + event.error)
      }

      setRecognition(recognitionInstance)
    }
  }, [])

  const startListening = () => {
    if (recognition && !isListening) {
      try {
        recognition.start()
      } catch (error) {
        console.error('Error starting recognition:', error)
        toast.error('Failed to start speech recognition')
      }
    }
  }

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop()
    }
  }

  const resetTranscript = () => {
    setTranscript('')
  }

  const speakText = async (text: string, voice: string = 'Rachel') => {
    try {
      setIsSpeaking(true)
      
      const { data, error } = await supabase.functions.invoke('text-to-speech', {
        body: {
          text,
          voice
        }
      })

      if (error) {
        throw error
      }

      // Play the audio
      const audio = new Audio(data.data.audioData)
      audio.onended = () => setIsSpeaking(false)
      audio.onerror = () => {
        setIsSpeaking(false)
        toast.error('Failed to play audio')
      }
      
      await audio.play()
    } catch (error: any) {
      console.error('Text-to-speech error:', error)
      setIsSpeaking(false)
      toast.error('Failed to generate speech: ' + error.message)
    }
  }

  return {
    isListening,
    isSupported,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
    speakText,
    isSpeaking
  }
}