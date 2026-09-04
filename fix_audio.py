#!/usr/bin/env python3
"""Fix audio output device selection"""

import subprocess
import os

def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1

def fix_audio_output():
    """Set correct audio output device"""
    print("🔧 FIXING AUDIO OUTPUT DEVICE")
    print("=" * 40)
    
    # Show current default sink
    stdout, code = run_cmd("pactl get-default-sink")
    print(f"Current default: {stdout}")
    
    # List all sinks
    print("\n📋 Available audio devices:")
    stdout, code = run_cmd("pactl list sinks short")
    sinks = []
    for line in stdout.split('\n'):
        if line.strip():
            parts = line.split('\t')
            sink_id = parts[0]
            sink_name = parts[1]
            status = parts[4] if len(parts) > 4 else "UNKNOWN"
            
            # Identify laptop speakers (not HDMI)
            if 'hdmi' not in sink_name.lower() and 'nvidia' not in sink_name.lower():
                print(f"  🔊 {sink_id}: {sink_name} ({status}) <- LAPTOP SPEAKERS")
                sinks.append((sink_id, sink_name))
            else:
                print(f"  📺 {sink_id}: {sink_name} ({status})")
    
    if not sinks:
        print("❌ No laptop speakers found!")
        return False
    
    # Set laptop speakers as default
    laptop_sink_id, laptop_sink_name = sinks[0]
    print(f"\n🎯 Setting laptop speakers as default: {laptop_sink_name}")
    
    # Set default sink
    run_cmd(f"pactl set-default-sink {laptop_sink_id}")
    
    # Set volume to 80%
    run_cmd(f"pactl set-sink-volume {laptop_sink_id} 80%")
    
    # Unmute
    run_cmd(f"pactl set-sink-mute {laptop_sink_id} 0")
    
    print("✅ Audio output fixed!")
    return True

def test_audio():
    """Test audio with laptop speakers"""
    print("\n🎵 Testing audio output...")
    
    # Use paplay to test (works with PipeWire)
    cmd = "timeout 3 paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null || echo 'Test file not found, generating tone...'"
    os.system(cmd)
    
    # Alternative: generate test tone
    cmd = "timeout 2 speaker-test -t sine -f 1000 -c 2 -l 1 2>/dev/null || echo 'speaker-test not available'"
    os.system(cmd)
    
    print("🎧 You should hear sound from your laptop speakers now!")

if __name__ == "__main__":
    if fix_audio_output():
        test_audio()