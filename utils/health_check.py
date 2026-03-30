"""System health check for ULTRON Agent"""
import os
import shutil
from pathlib import Path
from utils.ultron_logger import log_info, log_error

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        return Path(tesseract_path).exists()
    except:
        return False

def check_disk_space(min_gb=1):
    """Check available disk space"""
    disk_usage_stats = shutil.disk_usage('.')
    free_gb = disk_usage_stats.free / (1024**3)
    return free_gb >= min_gb

def check_logs_directory():
    """Ensure logs directory exists"""
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
    return logs_dir.exists()

def system_health_check():
    """Run all health checks"""
    checks = {
        'tesseract': check_tesseract(),
        'disk_space': check_disk_space(),
        'logs_dir': check_logs_directory(),
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        log_info("health_check", f"{status} {check}: {'PASS' if passed else 'FAIL'}")
    
    return all_passed, checks
