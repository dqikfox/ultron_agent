"""
Security tests for ULTRON Agent 3.0
Tests security utilities and validates security measures
"""

import pytest
import os
import tempfile
from pathlib import Path
from security_utils import (
    sanitize_log_input,
    sanitize_html_output,
    validate_file_path,
    secure_filename,
    validate_api_key,
    SecurityConfig
)


class TestSecurityUtils:
    """Test security utility functions."""
    
    def test_sanitize_log_input(self):
        """Test log input sanitization."""
        # Test newline removal
        assert sanitize_log_input("test\nline") == "test\\nline"
        assert sanitize_log_input("test\rline") == "test\\rline"
        assert sanitize_log_input("test\tline") == "test\\tline"
        
        # Test control character removal
        assert sanitize_log_input("test\x00control") == "testcontrol"
        
        # Test length limiting
        long_input = "a" * 2000
        result = sanitize_log_input(long_input)
        assert len(result) <= 1000
        assert result.endswith("...")
        
        # Test non-string input
        assert sanitize_log_input(123) == "123"
        assert sanitize_log_input(None) == "None"
    
    def test_sanitize_html_output(self):
        """Test HTML output sanitization."""
        # Test basic HTML escaping
        assert sanitize_html_output("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        assert sanitize_html_output("test & data") == "test &amp; data"
        assert sanitize_html_output('test "quotes"') == "test &quot;quotes&quot;"
        
        # Test non-string input
        assert sanitize_html_output(123) == "123"
    
    def test_validate_file_path(self):
        """Test file path validation."""
        # Test valid paths
        assert validate_file_path("test.txt") == True
        assert validate_file_path("folder/test.txt") == True
        
        # Test path traversal attempts
        assert validate_file_path("../test.txt") == False
        assert validate_file_path("../../etc/passwd") == False
        assert validate_file_path("/absolute/path") == False
        
        # Test with allowed base paths
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            Path(test_file).touch()
            
            # Should be valid within allowed base
            assert validate_file_path(test_file, [temp_dir]) == True
            
            # Should be invalid outside allowed base
            assert validate_file_path("/etc/passwd", [temp_dir]) == False
    
    def test_secure_filename(self):
        """Test secure filename generation."""
        # Test dangerous characters removal
        assert secure_filename("test<>file.txt") == "testfile.txt"
        assert secure_filename("test|file.txt") == "testfile.txt"
        assert secure_filename("test/file.txt") == "testfile.txt"
        
        # Test leading dots and spaces
        assert secure_filename("...test.txt") == "test.txt"
        assert secure_filename("   test.txt") == "test.txt"
        
        # Test length limiting
        long_name = "a" * 300 + ".txt"
        result = secure_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")
        
        # Test empty filename
        assert secure_filename("") == "unnamed_file"
        assert secure_filename("...") == "unnamed_file"
    
    def test_validate_api_key(self):
        """Test API key validation."""
        # Test valid keys
        assert validate_api_key("sk-1234567890abcdef") == True
        assert validate_api_key("a" * 20) == True
        
        # Test invalid keys
        assert validate_api_key("short") == False
        assert validate_api_key("test") == False
        assert validate_api_key("demo") == False
        assert validate_api_key("") == False
        assert validate_api_key(None) == False
        assert validate_api_key(123) == False


class TestSecurityConfig:
    """Test security configuration."""
    
    def test_safe_file_extension(self):
        """Test file extension validation."""
        # Test allowed extensions
        assert SecurityConfig.is_safe_file_extension("test.py") == True
        assert SecurityConfig.is_safe_file_extension("data.json") == True
        assert SecurityConfig.is_safe_file_extension("config.yaml") == True
        
        # Test disallowed extensions
        assert SecurityConfig.is_safe_file_extension("malware.exe") == False
        assert SecurityConfig.is_safe_file_extension("script.bat") == False
        assert SecurityConfig.is_safe_file_extension("data.bin") == False
    
    def test_safe_file_size(self):
        """Test file size validation."""
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            # Write small file
            temp_file.write(b"small content")
            temp_file.flush()
            
            assert SecurityConfig.is_safe_file_size(temp_file.name) == True
        
        # Test non-existent file
        assert SecurityConfig.is_safe_file_size("non_existent_file.txt") == False


class TestSecurityIntegration:
    """Test security integration with other components."""
    
    def test_log_injection_prevention(self):
        """Test that log injection is prevented."""
        malicious_input = "normal_text\n[FAKE LOG ENTRY] Unauthorized access"
        sanitized = sanitize_log_input(malicious_input)
        
        # Should not contain actual newlines
        assert "\n" not in sanitized
        assert "\\n" in sanitized
    
    def test_xss_prevention(self):
        """Test XSS prevention in HTML output."""
        xss_payload = "<img src=x onerror=alert('XSS')>"
        sanitized = sanitize_html_output(xss_payload)
        
        # Should not contain executable HTML
        assert "<img" not in sanitized
        assert "onerror" not in sanitized
        assert "&lt;img" in sanitized
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention."""
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for attempt in traversal_attempts:
            assert validate_file_path(attempt) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])