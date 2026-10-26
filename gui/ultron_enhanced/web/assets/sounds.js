/**
 * ULTRON Enhanced - Sound System
 * Handles audio effects and voice feedback for the Pokedex interface
 */

class UltronSoundSystem {
    constructor() {
        this.audioContext = null;
        this.sounds = new Map();
        this.volume = 0.7;
        this.muted = false;
        this.initialized = false;
        
        this.initializeAudioContext();
        this.loadDefaultSounds();
    }

    async initializeAudioContext() {
        try {
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Handle browser autoplay restrictions
            if (this.audioContext.state === 'suspended') {
                document.addEventListener('click', () => {
                    this.audioContext.resume();
                }, { once: true });
            }
            
            this.initialized = true;
            console.log('ULTRON Sound System initialized');
        } catch (error) {
            console.warn('Audio initialization failed:', error);
        }
    }

    loadDefaultSounds() {
        // Define default sound effects using Web Audio API
        this.soundDefinitions = {
            wake: {
                type: 'tone',
                frequency: 440,
                duration: 0.3,
                volume: 0.5
            },
            confirm: {
                type: 'beep',
                frequency: 800,
                duration: 0.1,
                volume: 0.4
            },
            error: {
                type: 'buzz',
                frequency: 200,
                duration: 0.5,
                volume: 0.6
            },
            button: {
                type: 'click',
                frequency: 1000,
                duration: 0.05,
                volume: 0.3
            },
            scan: {
                type: 'sweep',
                startFreq: 300,
                endFreq: 600,
                duration: 0.8,
                volume: 0.4
            },
            startup: {
                type: 'chord',
                frequencies: [220, 330, 440],
                duration: 1.0,
                volume: 0.5
            },
            shutdown: {
                type: 'descent',
                startFreq: 600,
                endFreq: 100,
                duration: 1.2,
                volume: 0.4
            }
        };
    }

    async generateTone(frequency, duration, volume = 0.5, type = 'sine') {
        if (!this.audioContext || this.muted) return;

        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = type;
            
            // Apply volume with fade in/out
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(volume * this.volume, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
            
        } catch (error) {
            console.warn('Sound generation failed:', error);
        }
    }

    async generateBeep(frequency = 800, duration = 0.1) {
        await this.generateTone(frequency, duration, 0.4, 'square');
    }

    async generateBuzz(frequency = 200, duration = 0.5) {
        await this.generateTone(frequency, duration, 0.6, 'sawtooth');
    }

    async generateSweep(startFreq = 300, endFreq = 600, duration = 0.8) {
        if (!this.audioContext || this.muted) return;

        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(startFreq, this.audioContext.currentTime);
            oscillator.frequency.linearRampToValueAtTime(endFreq, this.audioContext.currentTime + duration);
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.4 * this.volume, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
            
        } catch (error) {
            console.warn('Sweep generation failed:', error);
        }
    }

    async generateChord(frequencies = [220, 330, 440], duration = 1.0) {
        if (!this.audioContext || this.muted) return;

        try {
            frequencies.forEach((freq, index) => {
                setTimeout(() => {
                    this.generateTone(freq, duration, 0.3, 'sine');
                }, index * 100);
            });
        } catch (error) {
            console.warn('Chord generation failed:', error);
        }
    }

    async playSound(soundName) {
        if (!this.initialized || this.muted) return;

        const soundDef = this.soundDefinitions[soundName];
        if (!soundDef) {
            console.warn(`Sound '${soundName}' not found`);
            return;
        }

        try {
            switch (soundDef.type) {
                case 'tone':
                    await this.generateTone(soundDef.frequency, soundDef.duration, soundDef.volume);
                    break;
                case 'beep':
                    await this.generateBeep(soundDef.frequency, soundDef.duration);
                    break;
                case 'buzz':
                    await this.generateBuzz(soundDef.frequency, soundDef.duration);
                    break;
                case 'click':
                    await this.generateTone(soundDef.frequency, soundDef.duration, soundDef.volume, 'square');
                    break;
                case 'sweep':
                    await this.generateSweep(soundDef.startFreq, soundDef.endFreq, soundDef.duration);
                    break;
                case 'chord':
                    await this.generateChord(soundDef.frequencies, soundDef.duration);
                    break;
                case 'descent':
                    await this.generateSweep(soundDef.startFreq, soundDef.endFreq, soundDef.duration);
                    break;
                default:
                    await this.generateTone(440, 0.3, 0.5);
            }
        } catch (error) {
            console.warn(`Failed to play sound '${soundName}':`, error);
        }
    }

    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
    }

    getVolume() {
        return this.volume;
    }

    mute() {
        this.muted = true;
    }

    unmute() {
        this.muted = false;
    }

    toggleMute() {
        this.muted = !this.muted;
        return this.muted;
    }

    isMuted() {
        return this.muted;
    }

    // Convenience methods for common UI sounds
    async playWakeSound() {
        await this.playSound('wake');
    }

    async playConfirmSound() {
        await this.playSound('confirm');
    }

    async playErrorSound() {
        await this.playSound('error');
    }

    async playButtonSound() {
        await this.playSound('button');
    }

    async playScanSound() {
        await this.playSound('scan');
    }

    async playStartupSound() {
        await this.playSound('startup');
    }

    async playShutdownSound() {
        await this.playSound('shutdown');
    }

    // Voice synthesis integration
    speak(text, options = {}) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Configure voice
            utterance.rate = options.rate || 1.0;
            utterance.pitch = options.pitch || 1.0;
            utterance.volume = options.volume || this.volume;
            
            // Try to use a robotic/computer voice if available
            const voices = speechSynthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.toLowerCase().includes('robot') ||
                voice.name.toLowerCase().includes('computer') ||
                voice.name.toLowerCase().includes('microsoft david')
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            // Play confirmation sound before speaking
            this.playConfirmSound();
            
            speechSynthesis.speak(utterance);
        } else {
            console.warn('Speech synthesis not supported');
        }
    }

    // Audio context cleanup
    destroy() {
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        this.sounds.clear();
        this.initialized = false;
    }
}

// Export for global use
window.UltronSoundSystem = UltronSoundSystem;

// Create global instance
window.ultronSounds = new UltronSoundSystem();

console.log('ULTRON Sound System loaded');
