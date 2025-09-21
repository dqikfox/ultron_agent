"""
Security utilities for ULTRON Agent 3.0
Provides input sanitization and security validation functions
"""

import html
import re
import os
from pathlib import Path
from typing import Any, Union


def sanitize_log_input(text: str) -> str:
    """Sanitize input before logging to prevent log injection attacks."""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove or encode newline characters and control characters
    sanitized = text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    # Remove other control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Limit length to prevent log flooding
    if len(sanitized) > 1000:
        sanitized = sanitized[:997] + "..."
    
    return sanitized


def sanitize_html_output(text: str) -> str:
    """Sanitize text for HTML output to prevent XSS attacks."""
    if not isinstance(text, str):
        text = str(text)
    
    # First escape HTML entities
    sanitized = html.escape(text, quote=True)
    
    # Remove dangerous attributes and event handlers
    dangerous_patterns = [
        r'on\w+\s*=',  # Event handlers like onclick, onerror
        r'javascript:',  # JavaScript URLs
        r'data:',  # Data URLs
        r'vbscript:',  # VBScript URLs
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_file_path(file_path: str, allowed_base_paths: list = None) -> bool:
    """Validate file path to prevent path traversal attacks."""
    try:
        # Check for path traversal attempts
        if '..' in file_path:
            return False
        
        # Normalize the path
        normalized_path = os.path.normpath(file_path)
        
        # If allowed base paths are specified, check against them
        if allowed_base_paths:
            try:
                resolved_path = Path(file_path).resolve()
                for base_path in allowed_base_paths:
                    base_resolved = Path(base_path).resolve()
                    try:
                        resolved_path.relative_to(base_resolved)
                        return True
                    except ValueError:
                        continue
                return False
            except (OSError, ValueError):
                return False
        
        # If no allowed base paths, reject absolute paths
        if file_path.startswith('/'):  # Unix absolute path
            return False
            
        # Check for Windows absolute paths (C:, D:, etc.)
        if len(file_path) > 1 and file_path[1] == ':':
            return False
            
        # Check for UNC paths (\\server\share)
        if file_path.startswith('\\\\'):
            return False
        
        # Check if normalized path is absolute
        if os.path.isabs(normalized_path):
            return False
        
        return True
        
    except (OSError, ValueError):
        return False


def secure_filename(filename: str) -> str:
    """Generate a secure filename by removing dangerous characters."""
    import re
    # Remove path separators and dangerous characters
    filename = re.sub(r'[^\w\s._-]', '', filename)
    
    # Remove leading dots and spaces
    filename = filename.lstrip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename or 'unnamed_file'


def validate_api_key(api_key: str) -> bool:
    """Basic validation for API keys."""
    if not isinstance(api_key, str):
        return False
    
    # Check minimum length
    if len(api_key.strip()) < 10:
        return False
    
    # Check for suspicious patterns
    if api_key.strip().lower() in ['test', 'demo', 'example', 'placeholder']:
        return False
    
    return True


class SecurityConfig:
    """Security configuration and validation."""
    
    ALLOWED_FILE_EXTENSIONS = {'.py', '.txt', '.md', '.json', '.yaml', '.yml', '.log'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_LOG_ENTRY_SIZE = 1000
    
    @classmethod
    def is_safe_file_extension(cls, filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = Path(filename).suffix.lower()
        return ext in cls.ALLOWED_FILE_EXTENSIONS
    
    @classmethod
    def is_safe_file_size(cls, file_path: str) -> bool:
        """Check if file size is within limits."""
        try:
            return os.path.getsize(file_path) <= cls.MAX_FILE_SIZE
        except OSError:
            return False