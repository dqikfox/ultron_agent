#!/usr/bin/env python3
"""
ULTRON AI - Advanced Voice-Controlled Assistant Launcher
Complete system initialization and startup script
"""

import os
import sys
import argparse
import asyncio
import logging
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ultron_launcher.log')
    ]
)

logger = logging.getLogger("UltronLauncher")

def print_banner():
    """Print ULTRON startup banner"""
    banner = """
    ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗
    ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║
    ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║
    ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║
    ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║
     ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    
    🔴 ADVANCED AI VOICE ASSISTANT 🔴
    ═════════════════════════════════════════════════
    """
    print(banner)

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        import ctypes
        if sys.platform.startswith('win'):
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        'openai', 'torch', 'transformers', 'numpy',
        'psutil', 'speech_recognition', 'pyttsx3',
        'PIL', 'cv2', 'sklearn', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'cv2':
                import cv2
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages using: pip install -r requirements.txt")
        return False
    
    logger.info("All required dependencies available")
    return True

def setup_ultron_directories():
    """Setup ULTRON directory structure"""
    try:
        ultron_root = Path("D:/ULTRON")
        directories = [
            ultron_root,
            ultron_root / "models",
            ultron_root / "assets", 
            ultron_root / "logs",
            ultron_root / "screenshots",
            ultron_root / "Downloads",
            ultron_root / "Sorted",
            ultron_root / "Quarantine"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {directory}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup directories: {e}")
        return False

def create_default_config():
    """Create default configuration if it doesn't exist"""
    try:
        config_path = Path("D:/ULTRON/config.json")
        
        if not config_path.exists():
            import json
            
            default_config = {
                "openai_api_key": "",
                "voice_engine": "pyttsx3",
                "voice_gender": "male",
                "theme": "red",
                "offline_mode": False,
                "vision_enabled": True,
                "web_port": 3000,
                "debug_mode": False,
                "auto_sort_enabled": True,
                "security_enabled": True,
                "trusted_mac_addresses": [],
                "performance_monitoring": True
            }
            
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default config: {config_path}")
            logger.warning("Please update config.json with your OpenAI API key")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create config: {e}")
        return False

def install_audio_models():
    """Download and install offline audio models if needed"""
    try:
        # Download Vosk model if not present
        vosk_dir = Path("D:/ULTRON/models/vosk")
        if not vosk_dir.exists():
            logger.info("Vosk models not found - offline speech recognition will be limited")
        
        # Check Tesseract installation
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR available")
        except:
            logger.warning("Tesseract OCR not found - OCR features will be limited")
        
        return True
        
    except Exception as e:
        logger.error(f"Audio model setup error: {e}")
        return False

async def initialize_ultron_core():
    """Initialize ULTRON core system"""
    try:
        from ultron_main import UltronCore
        
        logger.info("Initializing ULTRON Core...")
        ultron = UltronCore()
        
        logger.info("ULTRON Core initialized successfully")
        return ultron
        
    except Exception as e:
        logger.error(f"ULTRON Core initialization failed: {e}")
        raise

async def run_ultron_system(ultron_core, web_only=False, debug=False):
    """Run the complete ULTRON system"""
    try:
        logger.info("Starting ULTRON AI System...")
        
        # Set debug mode if requested
        if debug:
            ultron_core.config.debug_mode = True
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Start the system
        if web_only:
            logger.info("Starting in web-only mode...")
            # Start only web server
            if ultron_core.web_server:
                await ultron_core.web_server.start()
                logger.info(f"Web interface available at: http://localhost:{ultron_core.config.web_port}")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
        else:
            # Start full system
            await ultron_core.start()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        await ultron_core.stop()
    except Exception as e:
        logger.error(f"ULTRON system error: {e}")
        await ultron_core.stop()
        raise

def check_system_requirements():
    """Check system requirements"""
    try:
        import platform
        
        system_info = {
            "Platform": platform.system(),
            "Architecture": platform.architecture()[0],
            "Python Version": platform.python_version(),
            "Processor": platform.processor()
        }
        
        logger.info("System Information:")
        for key, value in system_info.items():
            logger.info(f"  {key}: {value}")
        
        # Check minimum requirements
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher required")
            return False
        
        # Check available memory
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb < 4:
            logger.warning(f"Low system memory: {memory_gb:.1f}GB (4GB+ recommended)")
        
        return True
        
    except Exception as e:
        logger.error(f"System requirements check failed: {e}")
        return False

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description="ULTRON AI Advanced Voice Assistant")
    parser.add_argument("--web-only", action="store_true", 
                       help="Start only web interface (no voice recognition)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    parser.add_argument("--no-admin-check", action="store_true",
                       help="Skip admin privilege check")
    parser.add_argument("--setup-only", action="store_true",
                       help="Only setup directories and config, don't start system")
    
    args = parser.parse_args()
    
    try:
        # Print banner
        print_banner()
        
        # Check admin privileges
        if not args.no_admin_check:
            admin_status = check_admin_privileges()
            if admin_status:
                logger.info("✅ Running with administrator privileges")
            else:
                logger.warning("⚠️  Not running with administrator privileges")
                logger.warning("   Some features may be limited")
        
        # Check system requirements
        if not check_system_requirements():
            logger.error("❌ System requirements not met")
            return 1
        
        # Check dependencies
        if not check_dependencies():
            logger.error("❌ Missing required dependencies")
            return 1
        
        # Setup directories
        if not setup_ultron_directories():
            logger.error("❌ Failed to setup ULTRON directories")
            return 1
        
        # Create default config
        if not create_default_config():
            logger.error("❌ Failed to create configuration")
            return 1
        
        # Install audio models
        if not install_audio_models():
            logger.warning("⚠️  Audio models setup incomplete")
        
        # If setup only, exit here
        if args.setup_only:
            logger.info("✅ ULTRON setup completed")
            return 0
        
        # Initialize and run ULTRON
        logger.info("🚀 Starting ULTRON AI System...")
        
        # Set event loop policy for Windows
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Run the system
        asyncio.run(main_async(args))
        
        logger.info("✅ ULTRON AI System shutdown complete")
        return 0
        
    except KeyboardInterrupt:
        logger.info("🔴 ULTRON startup cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"❌ ULTRON startup failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

async def main_async(args):
    """Async main function"""
    try:
        # Initialize ULTRON core
        ultron_core = await initialize_ultron_core()
        
        # Run the system
        await run_ultron_system(ultron_core, args.web_only, args.debug)
        
    except Exception as e:
        logger.error(f"ULTRON system error: {e}")
        raise

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
