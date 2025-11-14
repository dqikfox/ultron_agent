"""Tests for ULTRON Agent enhancements"""
import pytest
from pathlib import Path
from utils.config_validator import validate_config, check_environment
from utils.health_check import system_health_check
from utils.command_history import CommandHistory
from utils.error_recovery import retry_on_failure, safe_execute
from utils.performance_tracker import track_performance, PerformanceMonitor

def test_config_validator():
    """Test configuration validation"""
    try:
        config = validate_config()
        assert 'llm_model' in config
    except FileNotFoundError:
        pytest.skip("Config file not found")

def test_health_check():
    """Test system health check"""
    passed, checks = system_health_check()
    assert isinstance(checks, dict)
    assert 'logs_dir' in checks

def test_command_history():
    """Test command history tracking"""
    history = CommandHistory(max_size=5)
    history.add("test command", "success")
    last = history.get_last(1)
    assert len(last) == 1
    assert last[0]['command'] == "test command"

def test_error_recovery():
    """Test retry decorator"""
    call_count = 0
    
    @retry_on_failure(max_retries=3, delay=0)
    def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Test error")
        return "success"
    
    result = failing_func()
    assert result == "success"
    assert call_count == 3

def test_performance_tracker():
    """Test performance monitoring"""
    monitor = PerformanceMonitor()
    monitor.record("test_op", 1.5)
    monitor.record("test_op", 2.0)
    
    stats = monitor.get_stats("test_op")
    assert stats['count'] == 2
    assert stats['avg'] == 1.75
