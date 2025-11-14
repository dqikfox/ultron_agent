"""Automated build script for ULTRON Agent with all dependencies"""
import subprocess
import sys

HIDDEN_IMPORTS = [
    'pyautogui', 'keyboard', 'cv2', 'pytesseract', 'psutil',
    'pyttsx3', 'speech_recognition', 'openai', 'pygetwindow'
]

def build():
    cmd = ['pyinstaller', '--onefile', '--noconsole']
    cmd.extend([f'--hidden-import={m}' for m in HIDDEN_IMPORTS])
    cmd.append('Ultron_Live.py')
    
    print("Building ULTRON Agent...")
    subprocess.run(cmd, check=True)
    print("✓ Build complete: dist/Ultron_Live.exe")

if __name__ == '__main__':
    build()
