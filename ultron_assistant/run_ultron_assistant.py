# run_ultron_assistant.py
"""
Ultron Assistant Launcher
========================

This script launches the complete Ultron Assistant system:
1. Checks dependencies
2. Verifies Ollama is running
3. Starts the FastAPI server
4. Opens the GUI interface

Usage:
    python run_ultron_assistant.py [options]

Options:
    --host HOST         Host to bind to (default: 127.0.0.1)
    --port PORT         Port to bind to (default: 8000)
    --no-gui            Run without GUI (server only)
    --check-only        Only check dependencies and exit
    --install-deps      Install missing dependencies
"""

import subprocess
import sys
import os
import json
import time
import argparse
import webbrowser
from pathlib import Path
from typing import List, Tuple, Optional

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltronAssistantLauncher:
    """Launcher for the Ultron Assistant system."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.required_packages = [
            'fastapi>=0.110.0',
            'uvicorn[standard]>=0.29.0',
            'python-socketio[asyncio_client]>=5.11.2',
            'python-socketio[asyncio_server]>=5.11.2',
            'pydantic>=2.7.0',
            'httpx>=0.27.0',
            'PySide6>=6.7.0',
            'SpeechRecognition>=3.10.4',
            'pyttsx3>=2.90',
            'pyautogui>=0.9.54',
            'Pillow>=10.3.0',
            'Jinja2>=3.1.2'
        ]
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            logger.info(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
            return True
        else:
            logger.error(f"✗ Python {version.major}.{version.minor} is not supported. Requires Python 3.8+")
            return False
    
    def check_ollama(self) -> Tuple[bool, str]:
        """Check if Ollama is running and accessible."""
        try:
            import httpx
            response = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                logger.info(f"✓ Ollama is running with {len(models)} models")
                if models:
                    logger.info(f"  Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                    return True, f"Running with {len(models)} models"
                else:
                    return False, "Running but no models available"
            else:
                return False, f"HTTP {response.status_code}"
        except ImportError:
            return False, "httpx not available"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def check_package_installed(self, package: str) -> bool:
        """Check if a package is installed."""
        try:
            # Extract package name (remove version constraints)
            package_name = package.split('>=')[0].split('==')[0].split('[')[0]
            __import__(package_name.replace('-', '_'))
            return True
        except ImportError:
            return False
    
    def check_dependencies(self) -> Tuple[List[str], List[str]]:
        """Check which dependencies are installed/missing."""
        installed = []
        missing = []
        
        for package in self.required_packages:
            if self.check_package_installed(package):
                installed.append(package)
            else:
                missing.append(package)
        
        return installed, missing
    
    def install_dependencies(self, packages: List[str]) -> bool:
        """Install missing dependencies."""
        if not packages:
            logger.info("No packages to install")
            return True
        
        logger.info(f"Installing {len(packages)} packages...")
        
        # Special handling for pyaudio on Windows
        if any('pyaudio' in pkg.lower() for pkg in packages):
            logger.info("Note: pyaudio may require additional setup on Windows")
            logger.info("If installation fails, download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + packages
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Dependencies installed successfully")
                return True
            else:
                logger.error(f"✗ Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Installation error: {e}")
            return False
    
    def start_ollama_if_needed(self) -> bool:
        """Try to start Ollama if it's not running."""
        ollama_running, status = self.check_ollama()
        
        if ollama_running:
            return True
        
        logger.info("Ollama not detected, attempting to start...")
        
        try:
            # Try to start Ollama
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait a moment and check again
            time.sleep(3)
            ollama_running, _ = self.check_ollama()
            
            if ollama_running:
                logger.info("✓ Ollama started successfully")
                return True
            else:
                logger.warning("⚠ Ollama may still be starting...")
                return False
                
        except FileNotFoundError:
            logger.error("✗ Ollama not found. Please install Ollama first.")
            logger.error("  Download from: https://ollama.ai/download")
            return False
        except Exception as e:
            logger.error(f"✗ Failed to start Ollama: {e}")
            return False
    
    def ensure_model_available(self) -> bool:
        """Ensure at least one model is available."""
        try:
            ollama_running, status = self.check_ollama()
            if not ollama_running:
                return False
            
            import httpx
            response = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5)
            data = response.json()
            models = data.get("models", [])
            
            if not models:
                logger.info("No models found, pulling default model...")
                logger.info("This may take several minutes for the first time...")
                
                result = subprocess.run(['ollama', 'pull', 'llama3.2'], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("✓ Default model pulled successfully")
                    return True
                else:
                    logger.error(f"✗ Failed to pull model: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error checking models: {e}")
            return False
    
    def run_system_checks(self, install_missing: bool = False) -> bool:
        """Run all system checks."""
        logger.info("🔍 Running Ultron Assistant system checks...")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check dependencies
        installed, missing = self.check_dependencies()
        
        logger.info(f"✓ {len(installed)} packages installed")
        if missing:
            logger.warning(f"⚠ {len(missing)} packages missing: {', '.join(missing)}")
            
            if install_missing:
                if not self.install_dependencies(missing):
                    return False
            else:
                logger.error("Run with --install-deps to install missing packages")
                return False
        else:
            logger.info("✓ All required packages installed")
        
        # Check Ollama
        if not self.start_ollama_if_needed():
            logger.error("✗ Ollama is required but not available")
            return False
        
        # Ensure model is available
        if not self.ensure_model_available():
            logger.error("✗ No AI models available")
            return False
        
        logger.info("✓ All system checks passed!")
        return True
    
    def start_server(self, host: str = "127.0.0.1", port: int = 8000, use_gui: bool = True) -> None:
        """Start the Ultron Assistant server."""
        logger.info(f"🚀 Starting Ultron Assistant server on {host}:{port}")
        
        # Change to the ultron_assistant directory
        os.chdir(self.script_dir)
        
        # Import and run the app
        try:
            from app import run_server
            run_server(host=host, port=port, use_gui=use_gui)
        except ImportError as e:
            logger.error(f"✗ Failed to import app: {e}")
            logger.error("Make sure you're in the ultron_assistant directory")
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"✗ Server error: {e}")

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description="Ultron Assistant Launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-gui", action="store_true", help="Run without GUI")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies")
    
    args = parser.parse_args()
    
    launcher = UltronAssistantLauncher()
    
    # Run system checks
    if not launcher.run_system_checks(install_missing=args.install_deps):
        sys.exit(1)
    
    if args.check_only:
        logger.info("✓ System check complete - ready to launch!")
        return
    
    # Start the server
    try:
        launcher.start_server(
            host=args.host, 
            port=args.port, 
            use_gui=not args.no_gui
        )
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")

if __name__ == "__main__":
    main()
