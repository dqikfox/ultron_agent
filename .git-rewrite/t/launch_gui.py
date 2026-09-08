"""
ULTRON Agent 3.0 - GUI Launcher
Launches the correct ULTRON Enhanced GUI interface
"""

import os
import sys
import webbrowser
import logging
from pathlib import Path

def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def launch_ultron_gui():
    """Launch the ULTRON Enhanced GUI interface."""
    logger = setup_logging()
    
    # Define GUI paths
    gui_file = "gui/ultron_enhanced/web/index.html"
    gui_url = f"file:///{os.path.abspath(gui_file).replace(os.sep, '/')}"
    
    logger.info("🚀 Launching ULTRON Enhanced GUI...")
    logger.info(f"📍 GUI Location: {gui_file}")
    logger.info(f"🌐 GUI URL: {gui_url}")
    
    try:
        # Check if GUI file exists
        if not os.path.exists(gui_file):
            logger.error(f"❌ GUI file not found: {gui_file}")
            logger.info("📂 Available GUI files:")
            
            # List available GUI files
            gui_dir = Path("gui")
            if gui_dir.exists():
                for item in gui_dir.rglob("*.html"):
                    logger.info(f"   - {item}")
            else:
                logger.error("❌ GUI directory not found")
            return False
        
        # Launch GUI in default browser
        logger.info("🌐 Opening GUI in default browser...")
        webbrowser.open(gui_url)
        
        logger.info("✅ ULTRON Enhanced GUI launched successfully!")
        logger.info("🎮 Features available:")
        logger.info("   - 🖥️ Console Interface")
        logger.info("   - ⚙️ System Monitoring")
        logger.info("   - 👁️ Vision System")
        logger.info("   - 📋 Task Management")
        logger.info("   - 📁 File Browser")
        logger.info("   - 🔧 Configuration")
        logger.info("   - 👤 User Profile")
        logger.info("   - 🤖 AI Chat Integration")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to launch GUI: {e}")
        logger.info("🔧 Manual access:")
        logger.info(f"   Copy and paste this URL in your browser:")
        logger.info(f"   {gui_url}")
        return False

def main():
    """Main entry point."""
    print("=" * 60)
    print("🤖 ULTRON Agent 3.0 - GUI Launcher")
    print("=" * 60)
    
    success = launch_ultron_gui()
    
    if success:
        print("\n✅ GUI launched successfully!")
        print("📖 For more information, see GUI_DOCUMENTATION.md")
    else:
        print("\n❌ GUI launch failed!")
        print("🔧 Try manual access:")
        print("   1. Navigate to gui/ultron_enhanced/web/")
        print("   2. Open index.html in your browser")
    
    print("\n" + "=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()