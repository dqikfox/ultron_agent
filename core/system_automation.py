"""
ULTRON System Automation
========================

Advanced system control and automation capabilities including process management,
file operations, window control, and system monitoring.
"""

import os
import sys
import psutil
import subprocess
import threading
import time
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

# System automation imports
try:
    # Handle headless environments
    import os
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    import pyautogui
    pyautogui.FAILSAFE = False
    GUI_AUTOMATION = True
except Exception:
    GUI_AUTOMATION = False
    pyautogui = None

# Windows-specific automation
try:
    import win32gui
    import win32process
    import win32api
    import win32con
    WINDOWS_AUTOMATION = True
except ImportError:
    WINDOWS_AUTOMATION = False
    print("Windows automation not available. Some features limited.")

# Cross-platform automation
try:
    import pynput
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class SystemAutomation:
    """Advanced system automation and control."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize system automation with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # PyAutoGUI configuration
        if GUI_AUTOMATION and pyautogui:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = getattr(config, 'automation_pause', 0.1)
        
        # System monitoring
        self.monitor_active = False
        self.monitor_thread = None
        self.system_stats = {}
        
        # Process tracking
        self.tracked_processes = {}
        self.process_filters = []
        
        # Automation safety
        self.safety_enabled = getattr(config, 'safety_enabled', True)
        self.confirmation_required = getattr(config, 'confirmation_required', True)
        
        self.logger.info("System automation initialized")
    
    # ================================
    # Process Management
    # ================================
    
    def get_running_processes(self, filter_name: str = None) -> List[Dict[str, Any]]:
        """Get list of running processes with optional filtering."""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if filter_name and filter_name.lower() not in proc_info['name'].lower():
                        continue
                    
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent'],
                        'status': proc_info['status']
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting processes: {e}")
        
        return processes
    
    def kill_process(self, process_name: str = None, pid: int = None) -> bool:
        """Kill process by name or PID."""
        if not process_name and not pid:
            return False
        
        try:
            if pid:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=3)
                self.logger.info(f"Killed process PID {pid}")
                return True
            
            elif process_name:
                killed = False
                for proc in psutil.process_iter(['pid', 'name']):
                    if process_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait(timeout=3)
                        killed = True
                        self.logger.info(f"Killed process {proc.info['name']} (PID {proc.info['pid']})")
                
                return killed
                
        except Exception as e:
            self.logger.error(f"Error killing process: {e}")
            return False
    
    def start_process(self, command: str, working_dir: str = None) -> Optional[int]:
        """Start a new process."""
        try:
            if working_dir and not os.path.exists(working_dir):
                working_dir = None
            
            proc = subprocess.Popen(
                command,
                cwd=working_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.logger.info(f"Started process: {command} (PID {proc.pid})")
            return proc.pid
            
        except Exception as e:
            self.logger.error(f"Error starting process: {e}")
            return None
    
    # ================================
    # File Operations
    # ================================
    
    def organize_files(self, directory: str, patterns: Dict[str, str] = None) -> Dict[str, int]:
        """Organize files in directory by type."""
        if not patterns:
            patterns = {
                'Images': ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp'],
                'Documents': ['*.pdf', '*.doc', '*.docx', '*.txt', '*.rtf'],
                'Videos': ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv'],
                'Audio': ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.ogg'],
                'Archives': ['*.zip', '*.rar', '*.7z', '*.tar', '*.gz']
            }
        
        directory_path = Path(directory)
        if not directory_path.exists():
            return {}
        
        organized_count = {}
        
        try:
            for category, extensions in patterns.items():
                category_dir = directory_path / category
                category_dir.mkdir(exist_ok=True)
                
                moved_files = 0
                for ext in extensions:
                    for file_path in directory_path.glob(ext):
                        if file_path.is_file() and file_path.parent == directory_path:
                            new_path = category_dir / file_path.name
                            file_path.rename(new_path)
                            moved_files += 1
                
                organized_count[category] = moved_files
            
            self.logger.info(f"Organized files in {directory}: {organized_count}")
            return organized_count
            
        except Exception as e:
            self.logger.error(f"Error organizing files: {e}")
            return {}
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files and caches."""
        cleanup_paths = [
            os.path.expanduser('~/AppData/Local/Temp'),  # Windows temp
            '/tmp',  # Linux/Mac temp
            os.path.expanduser('~/Library/Caches'),  # Mac cache
        ]
        
        results = {'deleted_files': 0, 'freed_space': 0, 'errors': []}
        
        for temp_path in cleanup_paths:
            if not os.path.exists(temp_path):
                continue
            
            try:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            results['deleted_files'] += 1
                            results['freed_space'] += file_size
                        except Exception as e:
                            results['errors'].append(f"Could not delete {file_path}: {e}")
                            
            except Exception as e:
                results['errors'].append(f"Error accessing {temp_path}: {e}")
        
        self.logger.info(f"Cleanup completed: {results}")
        return results
    
    # ================================
    # Screen and Window Automation
    # ================================
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """Take screenshot and save to file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = Path("screenshots") / filename
            screenshot_path.parent.mkdir(exist_ok=True)
            
            if 'pyautogui' in globals():
                screenshot = pyautogui.screenshot()
                screenshot.save(str(screenshot_path))
            else:
                self.logger.error("PyAutoGUI not available for screenshots")
                return None
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return None
    
    def find_window(self, window_title: str) -> Optional[Dict[str, Any]]:
        """Find window by title."""
        if not WINDOWS_AUTOMATION:
            return None
        
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'rect': rect,
                            'x': rect[0],
                            'y': rect[1],
                            'width': rect[2] - rect[0],
                            'height': rect[3] - rect[1]
                        })
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            return windows[0] if windows else None
            
        except Exception as e:
            self.logger.error(f"Window search error: {e}")
            return None
    
    def activate_window(self, window_title: str) -> bool:
        """Activate window by title."""
        window = self.find_window(window_title)
        if not window:
            return False
        
        try:
            win32gui.SetForegroundWindow(window['hwnd'])
            win32gui.ShowWindow(window['hwnd'], win32con.SW_RESTORE)
            self.logger.info(f"Activated window: {window['title']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Window activation error: {e}")
            return False
    
    def click_at(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """Click at specific coordinates."""
        if not 'pyautogui' in globals():
            return False
        
        try:
            if button == 'left':
                pyautogui.click(x, y, clicks=clicks)
            elif button == 'right':
                pyautogui.rightClick(x, y)
            elif button == 'middle':
                pyautogui.middleClick(x, y)
            
            self.logger.debug(f"Clicked at ({x}, {y}) with {button} button")
            return True
            
        except Exception as e:
            self.logger.error(f"Click error: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.01) -> bool:
        """Type text with optional interval."""
        if not 'pyautogui' in globals():
            return False
        
        try:
            pyautogui.typewrite(text, interval=interval)
            self.logger.debug(f"Typed text: {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Type error: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1) -> bool:
        """Press keyboard key(s)."""
        if not 'pyautogui' in globals():
            return False
        
        try:
            pyautogui.press(key, presses=presses)
            self.logger.debug(f"Pressed key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Key press error: {e}")
            return False
    
    # ================================
    # System Monitoring
    # ================================
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory usage
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk usage
            disk_usage = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    })
                except PermissionError:
                    continue
            
            # Network
            network = psutil.net_io_counters()
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': disk_usage,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'boot_time': boot_time.isoformat(),
                'uptime': str(datetime.now() - boot_time)
            }
            
            self.system_stats = stats
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}
    
    def start_monitoring(self, interval: int = 5):
        """Start system monitoring."""
        if self.monitor_active:
            return
        
        self.monitor_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"Started system monitoring (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitor_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("Stopped system monitoring")
    
    def _monitor_loop(self, interval: int):
        """System monitoring loop."""
        while self.monitor_active:
            try:
                self.get_system_stats()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(interval)
    
    # ================================
    # Utility Functions
    # ================================
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute system command with timeout."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get system automation status."""
        return {
            'pyautogui_available': 'pyautogui' in globals(),
            'windows_automation': WINDOWS_AUTOMATION,
            'pynput_available': PYNPUT_AVAILABLE,
            'monitoring_active': self.monitor_active,
            'safety_enabled': self.safety_enabled,
            'last_stats_time': self.system_stats.get('timestamp', 'Never')
        }


def test_system_automation():
    """Test system automation functionality."""
    automation = SystemAutomation()
    
    print("Testing system automation...")
    
    # Test system stats
    stats = automation.get_system_stats()
    print(f"CPU Usage: {stats.get('cpu', {}).get('percent', 'N/A')}%")
    print(f"Memory Usage: {stats.get('memory', {}).get('percent', 'N/A')}%")
    
    # Test process listing
    processes = automation.get_running_processes()
    print(f"Running processes: {len(processes)}")
    
    # Test screenshot
    screenshot_path = automation.take_screenshot()
    if screenshot_path:
        print(f"Screenshot saved: {screenshot_path}")
    
    print("System automation test complete")
    return automation.get_status()


if __name__ == "__main__":
    # Run system automation test
    test_system_automation()