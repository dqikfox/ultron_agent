#!/usr/bin/env python3
"""
VS Code Crash Prevention System
Initializes resource monitoring and stability measures before starting development
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from resource_monitor import start_resource_monitoring, get_resource_monitor

def setup_logging():
    """Setup logging for crash prevention system"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/crash_prevention.log'),
            logging.StreamHandler()
        ]
    )

def check_system_requirements():
    """Check if system meets minimum requirements for stable operation"""
    logger = logging.getLogger(__name__)
    
    try:
        import psutil
        
        # Check available memory
        memory = psutil.virtual_memory()
        if memory.available < 2 * 1024 * 1024 * 1024:  # 2GB
            logger.warning(f"Low available memory: {memory.available / 1024**3:.1f}GB")
            
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
            
        # Check disk space
        disk = psutil.disk_usage('.')
        if disk.free < 1 * 1024 * 1024 * 1024:  # 1GB
            logger.warning(f"Low disk space: {disk.free / 1024**3:.1f}GB")
            
        logger.info("System requirements check completed")
        return True
        
    except Exception as e:
        logger.error(f"System requirements check failed: {e}")
        return False

def optimize_environment():
    """Optimize environment variables for stability"""
    logger = logging.getLogger(__name__)
    
    # Set memory limits for Node.js (used by VS Code extensions)
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=4096'
    
    # Reduce Python memory usage
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Optimize Git operations
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    
    logger.info("Environment optimized for stability")

def cleanup_temp_files():
    """Clean up temporary files that might cause issues"""
    logger = logging.getLogger(__name__)
    
    try:
        # Clean up VS Code workspace cache
        vscode_dir = Path('.vscode')
        if vscode_dir.exists():
            cache_files = list(vscode_dir.glob('*.log'))
            for cache_file in cache_files:
                try:
                    cache_file.unlink()
                    logger.info(f"Cleaned up: {cache_file}")
                except Exception as e:
                    logger.warning(f"Could not clean {cache_file}: {e}")
        
        # Clean up Python cache
        pycache_dirs = list(Path('.').rglob('__pycache__'))
        for pycache_dir in pycache_dirs[:10]:  # Limit to prevent overload
            try:
                import shutil
                shutil.rmtree(pycache_dir)
                logger.info(f"Cleaned up: {pycache_dir}")
            except Exception as e:
                logger.warning(f"Could not clean {pycache_dir}: {e}")
                
        logger.info("Temporary file cleanup completed")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

def start_crash_prevention():
    """Start the crash prevention system"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting VS Code crash prevention system...")
    
    # Check system requirements
    if not check_system_requirements():
        logger.error("System requirements not met - VS Code may be unstable")
        return False
    
    # Optimize environment
    optimize_environment()
    
    # Clean up temporary files
    cleanup_temp_files()
    
    # Start resource monitoring
    start_resource_monitoring()
    
    # Wait for resource monitor to initialize
    time.sleep(2)
    
    monitor = get_resource_monitor()
    if monitor.is_circuit_open():
        logger.error("System already overloaded - aborting VS Code startup")
        return False
    
    logger.info("✅ Crash prevention system active - VS Code should be more stable")
    return True

def launch_vscode_safely():
    """Launch VS Code with safety measures"""
    logger = logging.getLogger(__name__)
    
    if not start_crash_prevention():
        logger.error("Failed to initialize crash prevention - VS Code launch aborted")
        return False
    
    try:
        # Launch VS Code with the workspace file
        workspace_file = "ultron-agent.code-workspace"
        if Path(workspace_file).exists():
            logger.info(f"Launching VS Code with workspace: {workspace_file}")
            subprocess.Popen(['code', workspace_file])
        else:
            logger.info("Launching VS Code with current directory")
            subprocess.Popen(['code', '.'])
            
        logger.info("VS Code launched successfully with crash prevention active")
        return True
        
    except FileNotFoundError:
        logger.error("VS Code (code command) not found in PATH")
        return False
    except Exception as e:
        logger.error(f"Failed to launch VS Code: {e}")
        return False

def main():
    """Main entry point"""
    setup_logging()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--launch-vscode":
        # Launch VS Code safely
        if not launch_vscode_safely():
            sys.exit(1)
    else:
        # Just start crash prevention
        if not start_crash_prevention():
            sys.exit(1)
        
        # Keep monitoring running
        logger = logging.getLogger(__name__)
        logger.info("Crash prevention system running - press Ctrl+C to stop")
        
        try:
            while True:
                monitor = get_resource_monitor()
                usage = monitor.get_current_usage()
                
                if usage:
                    logger.debug(
                        f"System status - CPU: {usage.get('cpu_percent', 0):.1f}%, "
                        f"Memory: {usage.get('memory_percent', 0):.1f}%, "
                        f"Circuit: {'OPEN' if monitor.is_circuit_open() else 'CLOSED'}"
                    )
                
                time.sleep(30)  # Report every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Stopping crash prevention system...")
            monitor.stop_monitoring()

if __name__ == "__main__":
    main()