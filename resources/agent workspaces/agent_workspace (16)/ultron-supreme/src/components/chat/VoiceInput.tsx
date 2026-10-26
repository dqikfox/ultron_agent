import React, { useState, useEffect, useRef } from 'react'
import { Mic, Square, Volume2 } from 'lucide-react'

interface VoiceInputProps {
  onResult: (transcript: string) => void
  onStop: () => void
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onResult, onStop }) => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      setError('Speech recognition not supported in this browser')
      return
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
      setError(null)
    }

    recognition.onresult = (event: any) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }

      setTranscript(finalTranscript + interimTranscript)
      
      if (finalTranscript) {
        onResult(finalTranscript)
        stopListening()
      }
    }

    recognition.onerror = (event: any) => {
      setError(`Speech recognition error: ${event.error}`)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = recognition

    // Start listening immediately
    startListening()

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start()
      } catch (err) {
        setError('Failed to start speech recognition')
      }
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
    onStop()
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <div className="text-red-400 text-sm mb-3">{error}</div>
        <button onClick={onStop} className="btn-ultron text-xs">
          Close
        </button>
      </div>
    )
  }

  return (
    <div className="text-center py-6">
      {/* Microphone Animation */}
      <div className="relative mb-4">
        <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${
          isListening ? 'bg-red-600 pulse-red' : 'bg-gray-600'
        }`}>
          <Mic className="w-8 h-8" />
        </div>
        
        {/* Sound Waves Animation */}
        {isListening && (
          <>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-20 h-20 border-2 border-red-400 rounded-full animate-ping opacity-30" />
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 border-2 border-red-400 rounded-full animate-ping opacity-20" style={{ animationDelay: '0.2s' }} />
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-28 h-28 border-2 border-red-400 rounded-full animate-ping opacity-10" style={{ animationDelay: '0.4s' }} />
          </>
        )}
      </div>

      {/* Status Text */}
      <div className="font-orbitron text-lg font-bold text-glow-red mb-2">
        {isListening ? 'LISTENING...' : 'STARTING...'}
      </div>
      
      <div className="text-sm text-gray-400 font-roboto mb-4">
        {isListening ? 'Speak now. I\'m listening.' : 'Initializing voice recognition...'}
      </div>

      {/* Transcript Display */}
      {transcript && (
        <div className="glass p-3 rounded-lg mb-4 min-h-[40px] flex items-center">
          <div className="text-sm text-gray-300 font-roboto">
            {transcript || 'Waiting for speech...'}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex justify-center space-x-3">
        <button
          onClick={stopListening}
          className="btn-ultron flex items-center space-x-2 px-4 py-2"
        >
          <Square className="w-4 h-4" />
          <span>Stop</span>
        </button>
      </div>

      {/* Instructions */}
      <div className="mt-4 text-xs text-gray-500 font-roboto">
        Speak clearly and pause when finished
      </div>
    </div>
  )
}