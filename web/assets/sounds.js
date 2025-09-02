// ULTRON Enhanced - Sound System
// Generates audio effects and manages sound playback

class UltronSoundSystem {
    constructor() {
        this.audioContext = null;
        this.sounds = {};
        this.enabled = true;
        this.volume = 0.5;
        
        this.initAudioContext();
        this.generateSounds();
    }
    
    initAudioContext() {
        try {
            // Create AudioContext (handles browser compatibility)
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            console.log('Audio context initialized');
        } catch (e) {
            console.warn('Web Audio API not supported:', e);
            this.enabled = false;
        }
    }
    
    generateSounds() {
        if (!this.audioContext) return;
        
        // Generate beep sound
        this.sounds.beep = this.generateBeep(800, 0.2, 0.3);
        
        // Generate startup sound
        this.sounds.startup = this.generateStartup();
        
        // Generate button click
        this.sounds.click = this.generateClick();
        
        // Generate error sound
        this.sounds.error = this.generateError();
        
        // Generate success sound
        this.sounds.success = this.generateSuccess();
        
        // Generate wake word detection
        this.sounds.wakeWord = this.generateWakeWord();
        
        console.log('Generated', Object.keys(this.sounds).length, 'sounds');
    }
    
    generateBeep(frequency, duration, volume = 0.3) {
        if (!this.audioContext) return null;
        
        const sampleRate = this.audioContext.sampleRate;
        const numSamples = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = buffer.getChannelData(0);
        
        // Generate sine wave
        for (let i = 0; i < numSamples; i++) {
            const time = i / sampleRate;
            const envelope = Math.exp(-time * 3); // Exponential decay
            channelData[i] = Math.sin(2 * Math.PI * frequency * time) * envelope * volume;
        }
        
        return buffer;
    }
    
    generateStartup() {
        if (!this.audioContext) return null;
        
        const duration = 2.0;
        const sampleRate = this.audioContext.sampleRate;
        const numSamples = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = buffer.getChannelData(0);
        
        // Generate ascending tones
        for (let i = 0; i < numSamples; i++) {
            const time = i / sampleRate;
            const progress = time / duration;
            
            // Frequency sweep from 200Hz to 800Hz
            const frequency = 200 + (600 * progress);
            const envelope = Math.sin(Math.PI * progress) * 0.3;
            
            channelData[i] = Math.sin(2 * Math.PI * frequency * time) * envelope;
        }
        
        return buffer;
    }
    
    generateClick() {
        if (!this.audioContext) return null;
        
        const duration = 0.1;
        const sampleRate = this.audioContext.sampleRate;
        const numSamples = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = buffer.getChannelData(0);
        
        // Generate brief noise burst
        for (let i = 0; i < numSamples; i++) {
            const time = i / sampleRate;
            const envelope = Math.exp(-time * 50);
            const noise = (Math.random() * 2 - 1) * 0.1;
            const tone = Math.sin(2 * Math.PI * 1200 * time) * 0.2;
            
            channelData[i] = (noise + tone) * envelope;
        }
        
        return buffer;
    }
    
    generateError() {
        if (!this.audioContext) return null;
        
        const duration = 0.5;
        const sampleRate = this.audioContext.sampleRate;
        const numSamples = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = buffer.getChannelData(0);
        
        // Generate descending harsh tone
        for (let i = 0; i < numSamples; i++) {
            const time = i / sampleRate;
            const progress = time / duration;
            
            const frequency = 400 - (200 * progress); // Descending
            const envelope = Math.exp(-time * 2) * 0.4;
            
            // Add some distortion
            let sample = Math.sin(2 * Math.PI * frequency * time);
            sample = Math.sign(sample) * Math.pow(Math.abs(sample), 0.7);
            
            channelData[i] = sample * envelope;
        }
        
        return buffer;
    }
    
    generateSuccess() {
        if (!this.audioContext) return null;
        
        const duration = 0.8;
        const sampleRate = this.audioContext.sampleRate;
        const numSamples = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = buffer.getChannelData(0);
        
        // Generate pleasant ascending chord
        const frequencies = [523, 659, 784]; // C5, E5, G5
        
        for (let i = 0; i < numSamples; i++) {
            const time = i / sampleRate;
            const envelope = Math.exp(-time * 1.5) * 0.2;
            
            let sample = 0;
            frequencies.forEach(freq => {
                sample += Math.sin(2 * Math.PI * freq * time);
            });
            
            channelData[i] = (sample / frequencies.length) * envelope;
        }
        
        return buffer;
    }
    
    generateWakeWord() {
        if (!this.audioContext) return null;
        
        const duration = 0.3;
        const sampleRate = this.audioContext.sampleRate;
        const numSamples = sampleRate * duration;
        const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate);
        const channelData = buffer.getChannelData(0);
        
        // Generate two-tone chime
        for (let i = 0; i < numSamples; i++) {
            const time = i / sampleRate;
            const envelope = Math.sin(Math.PI * time / duration) * 0.3;
            
            const tone1 = Math.sin(2 * Math.PI * 800 * time);
            const tone2 = Math.sin(2 * Math.PI * 1000 * time);
            
            // Alternate between tones
            const sample = time < duration / 2 ? tone1 : tone2;
            channelData[i] = sample * envelope;
        }
        
        return buffer;
    }
    
    play(soundName, volume = null) {
        if (!this.enabled || !this.audioContext || !this.sounds[soundName]) {
            console.warn(`Sound not available: ${soundName}`);
            return;
        }
        
        try {
            // Resume audio context if suspended (browser policy)
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }
            
            const source = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            
            source.buffer = this.sounds[soundName];
            
            // Set volume
            const finalVolume = (volume !== null ? volume : this.volume);
            gainNode.gain.value = finalVolume;
            
            // Connect nodes
            source.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // Play sound
            source.start();
            
            console.log(`Played sound: ${soundName}`);
        } catch (e) {
            console.error('Error playing sound:', e);
        }
    }
    
    playBeep(frequency = 800, duration = 0.2, volume = 0.3) {
        if (!this.audioContext) return;
        
        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';
            
            // Envelope
            const now = this.audioContext.currentTime;
            gainNode.gain.setValueAtTime(0, now);
            gainNode.gain.linearRampToValueAtTime(volume, now + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
            
            oscillator.start(now);
            oscillator.stop(now + duration);
        } catch (e) {
            console.error('Error playing beep:', e);
        }
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        console.log(`Sound volume set to: ${this.volume}`);
    }
    
    enable() {
        this.enabled = true;
        console.log('Sound system enabled');
    }
    
    disable() {
        this.enabled = false;
        console.log('Sound system disabled');
    }
    
    toggle() {
        this.enabled = !this.enabled;
        console.log(`Sound system ${this.enabled ? 'enabled' : 'disabled'}`);
        return this.enabled;
    }
    
    // Play startup sequence
    playStartupSequence() {
        this.play('startup');
        
        // Play additional beeps
        setTimeout(() => this.playBeep(600, 0.1), 500);
        setTimeout(() => this.playBeep(800, 0.1), 700);
        setTimeout(() => this.playBeep(1000, 0.2), 900);
    }
    
    // Play error sequence
    playErrorSequence() {
        this.play('error');
        setTimeout(() => this.playBeep(300, 0.3, 0.2), 200);
    }
    
    // Play success sequence
    playSuccessSequence() {
        this.play('success');
    }
    
    // Play interaction sound (click, hover, etc.)
    playInteraction(type = 'click') {
        switch (type) {
            case 'click':
                this.play('click');
                break;
            case 'hover':
                this.playBeep(1200, 0.05, 0.1);
                break;
            case 'select':
                this.playBeep(800, 0.1, 0.2);
                break;
            default:
                this.play('click');
        }
    }
}

// Create global sound system instance
window.ultronSounds = new UltronSoundSystem();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UltronSoundSystem;
}