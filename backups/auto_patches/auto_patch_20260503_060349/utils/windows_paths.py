"""
Windows-compatible path utilities for ULTRON Agent
Provides cross-platform path handling with Windows-specific optimizations
"""

import os
import sys
from pathlib import Path

def get_pictures_path():
    """Get the appropriate Pictures folder path for the current platform"""
    if os.name == 'nt':  # Windows
        # Try common Windows Pictures locations
        pictures_paths = [
            Path.home() / "Pictures" / "Screenshots",
            Path.home() / "OneDrive" / "Pictures" / "Screenshots",
            Path.home() / "Pictures",
            Path.home() / "My Pictures"
        ]
        for path in pictures_paths:
            if path.exists():
                return str(path)
        # Default to creating Pictures/Screenshots
        return str(Path.home() / "Pictures" / "Screenshots")
    else:  # Linux/Mac
        return str(Path.home() / "Pictures" / "Screenshots")

def get_desktop_path():
    """Get the Desktop path for the current platform"""
    if os.name == 'nt':  # Windows
        desktop_paths = [
            Path.home() / "Desktop",
            Path.home() / "OneDrive" / "Desktop"
        ]
        for path in desktop_paths:
            if path.exists():
                return str(path)
        return str(Path.home() / "Desktop")
    else:  # Linux/Mac
        return str(Path.home() / "Desktop")

def get_app_data_path():
    """Get application data path for the current platform"""
    if os.name == 'nt':  # Windows
        return os.environ.get('APPDATA', str(Path.home() / "AppData" / "Roaming"))
    else:  # Linux/Mac
        return str(Path.home() / ".config")

def get_temp_path():
    """Get temporary directory path for the current platform"""
    if os.name == 'nt':  # Windows
        return os.environ.get('TEMP', str(Path.home() / "AppData" / "Local" / "Temp"))
    else:  # Linux/Mac
        return "/tmp"

def normalize_path(path):
    """Normalize path separators for the current platform"""
    return str(Path(path))

def ensure_dir_exists(path):
    """Ensure directory exists, create if necessary"""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return str(path_obj)

# Windows-specific executable paths
def get_ollama_executable():
    """Get Ollama executable path for Windows"""
    if os.name == 'nt':
        ollama_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'Ollama' / 'ollama.exe',
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / 'Ollama' / 'ollama.exe',
            Path.home() / 'AppData' / 'Local' / 'Programs' / 'Ollama' / 'ollama.exe',
            Path.home() / 'AppData' / 'Roaming' / 'Ollama' / 'ollama.exe'
        ]
        for path in ollama_paths:
            if path.exists():
                return str(path)
        return str(Path.home() / 'AppData' / 'Local' / 'Programs' / 'Ollama' / 'ollama.exe')
    else:
        return 'ollama'

def get_chrome_executable():
    """Get Chrome executable path for Windows"""
    if os.name == 'nt':
        chrome_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
            Path.home() / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'Application' / 'chrome.exe'
        ]
        for path in chrome_paths:
            if path.exists():
                return str(path)
        return 'chrome.exe'
    else:
        return 'google-chrome'

def get_edge_executable():
    """Get Edge executable path for Windows"""
    if os.name == 'nt':
        edge_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'Microsoft' / 'Edge' / 'Application' / 'msedge.exe',
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / 'Microsoft' / 'Edge' / 'Application' / 'msedge.exe'
        ]
        for path in edge_paths:
            if path.exists():
                return str(path)
        return 'msedge.exe'
    else:
        return 'microsoft-edge'

def get_firefox_executable():
    """Get Firefox executable path for Windows"""
    if os.name == 'nt':
        firefox_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'Mozilla Firefox' / 'firefox.exe',
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / 'Mozilla Firefox' / 'firefox.exe'
        ]
        for path in firefox_paths:
            if path.exists():
                return str(path)
        return 'firefox.exe'
    else:
        return 'firefox'
