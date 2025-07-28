import sys
import os
import signal
import psutil

def release_microphone():
    # Try to find and terminate processes that may be holding the microphone
    mic_keywords = ["audiodg", "SpeechRuntime", "Cortana", "Teams", "Zoom", "Skype", "discord", "chrome", "firefox"]
    released = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if any(keyword.lower() in pname for keyword in mic_keywords):
                # On Windows, try to terminate the process
                os.system(f"taskkill /F /PID {proc.info['pid']}")
                released = True
        except Exception:
            continue
    return released

if __name__ == "__main__":
    released = release_microphone()
    if released:
        print("Microphone released from other processes.")
    else:
        print("No microphone-holding processes found or released.")
