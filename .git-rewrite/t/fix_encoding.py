#!/usr/bin/env python3
"""
Fix Windows console encoding for Unicode support
"""
import sys
import os
import locale

def fix_console_encoding():
    """Fix Windows console encoding to support Unicode characters"""
    try:
        # Set console code page to UTF-8
        if sys.platform == "win32":
            os.system("chcp 65001 >nul 2>&1")
            
        # Set environment variables for UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # Try to set locale
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except locale.Error:
                pass  # Use system default
        
        print("Console encoding fixed for Unicode support")
        return True
        
    except Exception as e:
        print(f"Warning: Could not fix console encoding: {e}")
        return False

if __name__ == "__main__":
    fix_console_encoding()