import React, { useState, useEffect, useRef, useCallback } from 'react'

interface VoiceTerminalProps {
  onVoiceInput: (text: string) => void
  isActive: boolean
  onActiveChange: (active: boolean) => void
}

interface VoiceSettings {
  stability: number
  similarity_boost: number
  style?: number
  use_speaker_boost?: boolean
}

export function VoiceTerminal({ onVoiceInput, isActive, onActiveChange }: VoiceTerminalProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isPushToTalk, setIsPushToTalk] = useState(true)
  const [audioLevel, setAudioLevel] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [voices, setVoices] = useState<any[]>([])
  const [selectedVoice, setSelectedVoice] = useState<string>('')
  const [speakReplies, setSpeakReplies] = useState(false)
  const [elevenLabsStatus, setElevenLabsStatus] = useState(false)
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>({
    stability: 0.5,
    similarity_boost: 0.75,
    style: 0.5,
    use_speaker_boost: true
  })
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const animationRef = useRef<number>()
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  useEffect(() => {
    initializeServices()
    setupAudioContext()
    setupWebSpeechAPI()
    
    return () => {
      cleanup()
    }
  }, [])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && isPushToTalk && !isRecording) {
        e.preventDefault()
        startRecording()
      }
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space' && isPushToTalk && isRecording) {
        e.preventDefault()
        stopRecording()
      }
    }

    if (isPushToTalk) {
      window.addEventListener('keydown', handleKeyDown)
      window.addEventListener('keyup', handleKeyUp)
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [isPushToTalk, isRecording])

  const initializeServices = async () => {
    try {
      // Check ElevenLabs status
      const status = await window.electronAPI.getElevenLabsConnectionStatus()
      setElevenLabsStatus(status)
      
      // Load voices (includes ElevenLabs + system voices)
      const voiceList = await window.electronAPI.getElevenLabsVoices()
      console.log('Loaded voices:', voiceList)
      setVoices(voiceList || [])
      
      if (voiceList && voiceList.length > 0 && !selectedVoice) {
        // Prefer ElevenLabs voices, fallback to system
        const elevenLabsVoice = voiceList.find(v => v.category === 'elevenlabs')
        const systemVoice = voiceList.find(v => v.category === 'system')
        const defaultVoice = elevenLabsVoice || systemVoice || voiceList[0]
        
        if (defaultVoice) {
          setSelectedVoice(defaultVoice.voice_id)
          console.log('Selected default voice:', defaultVoice.name)
        }
      }
    } catch (error) {
      console.error('Failed to initialize voice services:', error)
      // Fallback to basic system voices
      const fallbackVoices = [
        { voice_id: 'web-speech-default', name: 'System Default', category: 'system' },
        { voice_id: 'web-speech-female', name: 'System Female', category: 'system' },
        { voice_id: 'web-speech-male', name: 'System Male', category: 'system' }
      ]
      setVoices(fallbackVoices)
      setSelectedVoice('web-speech-default')
    }
  }

  const setupWebSpeechAPI = () => {
    // Setup Web Speech API for STT
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'
      
      recognition.onresult = (event: any) => {
        let interimTranscript = ''
        let finalTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }
        
        setTranscript(finalTranscript || interimTranscript)
        
        if (finalTranscript) {
          onVoiceInput(finalTranscript.trim())
          setTranscript('')
        }
      }
      
      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setTranscript(`Recognition error: ${event.error}`)
        setIsRecording(false)
      }
      
      recognition.onend = () => {
        setIsRecording(false)
      }
      
      recognitionRef.current = recognition
    }
    
    // Setup Web Speech API for TTS
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis
    }
  }

  const setupAudioContext = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)
      
      analyserRef.current.fftSize = 256
      
      startAudioAnalysis()
    } catch (error) {
      console.error('Failed to setup audio context:', error)
    }
  }

  const startAudioAnalysis = () => {
    if (!analyserRef.current) return
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    
    const analyze = () => {
      if (!analyserRef.current) return
      
      analyserRef.current.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      setAudioLevel(average / 255)
      
      animationRef.current = requestAnimationFrame(analyze)
    }
    
    analyze()
  }

  const startRecording = useCallback(async () => {
    if (!recognitionRef.current) {
      setTranscript('Speech recognition not supported')
      return
    }
    
    try {
      setIsRecording(true)
      setTranscript('Listening...')
      recognitionRef.current.start()
    } catch (error) {
      console.error('Failed to start speech recognition:', error)
      setTranscript('Failed to start recording')
      setIsRecording(false)
    }
  }, [])

  const stopRecording = useCallback(() => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
    }
  }, [isRecording])

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const speakText = async (text: string) => {
    if (!selectedVoice || !text) return
    
    try {
      // Handle ElevenLabs voices
      if (!selectedVoice.startsWith('web-speech-')) {
        const audioData = await window.electronAPI.textToSpeech(text, selectedVoice, voiceSettings)
        if (audioData) {
          const blob = new Blob([audioData], { type: 'audio/mpeg' })
          const url = URL.createObjectURL(blob)
          const audio = new Audio(url)
          
          audio.onended = () => URL.revokeObjectURL(url)
          await audio.play()
          return
        }
      }
      
      // Fallback to Web Speech API
      if (synthRef.current) {
        const utterance = new SpeechSynthesisUtterance(text)
        
        // Configure voice based on selection
        const systemVoices = synthRef.current.getVoices()
        if (selectedVoice === 'web-speech-male') {
          const maleVoice = systemVoices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('david'))
          if (maleVoice) utterance.voice = maleVoice
        } else if (selectedVoice === 'web-speech-female') {
          const femaleVoice = systemVoices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('zira') || v.name.toLowerCase().includes('samantha'))
          if (femaleVoice) utterance.voice = femaleVoice
        }
        
        utterance.rate = 1.0
        utterance.pitch = 1.0
        utterance.volume = 0.8
        
        synthRef.current.speak(utterance)
      }
    } catch (error) {
      console.error('Text to speech failed:', error)
    }
  }

  const testVoice = () => {
    const testText = `Hello! This is a voice test using ${voices.find(v => v.voice_id === selectedVoice)?.name || 'the selected voice'}. How do I sound?`
    speakText(testText)
  }

  const cleanup = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
    
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
  }

  // Waveform visualization with enhanced effects
  const getWaveformBars = () => {
    const bars = []
    for (let i = 0; i < 32; i++) {
      const baseHeight = 5
      const dynamicHeight = isRecording 
        ? Math.max(baseHeight, (audioLevel + Math.random() * 0.4) * 80)
        : baseHeight + Math.random() * 15
      
      const intensity = isRecording ? audioLevel : 0.2
      const color = isRecording 
        ? `rgba(255, 46, 146, ${0.6 + intensity * 0.4})` // Pink
        : `rgba(35, 230, 255, ${0.3 + intensity * 0.2})` // Cyan
      
      bars.push(
        <div
          key={i}
          className="transition-all duration-100 rounded-sm"
          style={{
            width: '2px',
            height: `${dynamicHeight}%`,
            backgroundColor: color,
            boxShadow: isRecording ? `0 0 ${intensity * 10}px ${color}` : 'none'
          }}
        />
      )
    }
    return bars
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-black/20 to-black/40">
      {/* Header */}
      <div className="p-md border-b border-slate-700">
        <div className="flex items-center justify-between mb-sm">
          <h3 className="ultron-heading h3" style={{ color: 'var(--color-accent-primary)' }}>
            VOICE I/O TERMINAL
          </h3>
          
          <div className="flex items-center gap-xs">
            <div className={`status-indicator ${elevenLabsStatus ? 'online' : 'offline'}`} />
            <span className="text-xs text-slate-400">
              {elevenLabsStatus ? 'ELEVENLABS' : 'SYSTEM'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-md text-sm">
          {/* Voice Mode Toggle */}
          <label className="flex items-center gap-xs cursor-pointer">
            <input
              type="checkbox"
              checked={isPushToTalk}
              onChange={(e) => setIsPushToTalk(e.target.checked)}
              className="sr-only"
            />
            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
              isPushToTalk ? 'border-pink-500 bg-pink-500 glow-border' : 'border-slate-500'
            }`}>
              {isPushToTalk && <div className="w-2 h-2 bg-white rounded" />}
            </div>
            <span className="text-slate-300">Push-to-Talk</span>
          </label>
          
          {/* Speak Replies Toggle */}
          <label className="flex items-center gap-xs cursor-pointer">
            <input
              type="checkbox"
              checked={speakReplies}
              onChange={(e) => setSpeakReplies(e.target.checked)}
              className="sr-only"
            />
            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
              speakReplies ? 'border-cyan-500 bg-cyan-500 glow-border' : 'border-slate-500'
            }`}>
              {speakReplies && <div className="w-2 h-2 bg-white rounded" />}
            </div>
            <span className="text-slate-300">Speak Replies</span>
          </label>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 p-md">
        <div className="flex items-center gap-md h-full">
          {/* Waveform Visualization */}
          <div className="flex-1 h-20 flex items-end justify-center gap-1 bg-black/30 rounded-lg border border-slate-700 p-sm ultron-panel">
            {getWaveformBars()}
          </div>
          
          {/* Controls */}
          <div className="flex flex-col gap-sm items-center">
            {/* Record Button */}
            <button
              onClick={toggleRecording}
              onMouseDown={isPushToTalk ? startRecording : undefined}
              onMouseUp={isPushToTalk ? stopRecording : undefined}
              onMouseLeave={isPushToTalk ? stopRecording : undefined}
              className={`w-20 h-20 rounded-full border-3 flex items-center justify-center text-2xl transition-all transform hover:scale-105 ${
                isRecording
                  ? 'border-red-500 bg-red-500/20 text-red-400 glow-border pulse'
                  : 'border-pink-500 hover:border-pink-400 text-pink-400 hover:bg-pink-500/10'
              }`}
            >
              {isRecording ? '⏹️' : '🎤'}
            </button>
            
            <div className="text-xs text-center text-slate-400 max-w-20">
              {isPushToTalk ? 'Hold SPACE or Click & Hold' : 'Click to Toggle'}
            </div>
          </div>
        </div>
        
        {/* Transcript Display */}
        {transcript && (
          <div className="mt-md ultron-panel p-sm">
            <div className="text-sm text-slate-300 break-words">
              {transcript}
            </div>
          </div>
        )}
      </div>
      
      {/* Voice Settings */}
      <div className="p-md border-t border-slate-700 space-y-sm">
        {/* Voice Selection */}
        <div className="flex items-center gap-md">
          <label className="text-sm text-slate-400 flex-shrink-0 w-16">Voice:</label>
          <select
            value={selectedVoice}
            onChange={(e) => setSelectedVoice(e.target.value)}
            className="ultron-input flex-1 text-sm"
          >
            <option value="">Select voice...</option>
            {voices.map(voice => (
              <option key={voice.voice_id} value={voice.voice_id}>
                {voice.name} ({voice.category === 'elevenlabs' ? 'ElevenLabs' : 'System'})
              </option>
            ))}
          </select>
          
          <button
            onClick={testVoice}
            disabled={!selectedVoice}
            className="ultron-button text-sm px-md"
          >
            TEST
          </button>
        </div>
        
        {/* Voice Settings (only for ElevenLabs voices) */}
        {selectedVoice && !selectedVoice.startsWith('web-speech-') && (
          <div className="grid grid-cols-2 gap-sm text-xs">
            <div>
              <label className="text-slate-400">Stability</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={voiceSettings.stability}
                onChange={(e) => setVoiceSettings(prev => ({ ...prev, stability: parseFloat(e.target.value) }))}
                className="w-full"
              />
              <span className="text-slate-500">{voiceSettings.stability}</span>
            </div>
            <div>
              <label className="text-slate-400">Similarity</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={voiceSettings.similarity_boost}
                onChange={(e) => setVoiceSettings(prev => ({ ...prev, similarity_boost: parseFloat(e.target.value) }))}
                className="w-full"
              />
              <span className="text-slate-500">{voiceSettings.similarity_boost}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
