"""Tests for enhanced monitoring and observability features."""
import pytest
import asyncio
import time
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ultron_agent.health import HealthChecker, UsageMetrics, HealthStatus
from ultron_agent.api import app
from fastapi.testclient import TestClient


class TestUsageMetrics:
    """Test usage metrics tracking."""

    def test_usage_metrics_initialization(self):
        """Test that usage metrics initialize properly."""
        metrics = UsageMetrics()
        assert metrics.commands_executed == 0
        assert metrics.error_count == 0
        assert metrics.api_requests == 0
        assert metrics.voice_commands == 0
        assert metrics.gui_interactions == 0
        assert metrics.session_count == 0

    def test_command_execution_recording(self):
        """Test recording command execution."""
        health = HealthChecker()
        
        # Record successful command
        health.record_command_execution("test_command", 0.5, success=True)
        
        assert health.usage_metrics.commands_executed == 1
        assert health.usage_metrics.total_execution_time == 0.5
        assert health.usage_metrics.error_count == 0
        assert health.usage_metrics.last_activity is not None

    def test_command_error_recording(self):
        """Test recording command errors."""
        health = HealthChecker()
        
        # Record failed command
        health.record_command_execution("failing_command", 0.2, success=False)
        
        assert health.usage_metrics.commands_executed == 1
        assert health.usage_metrics.error_count == 1

    def test_api_request_recording(self):
        """Test recording API requests."""
        health = HealthChecker()
        
        # Record successful API request
        health.record_api_request("/healthz", "GET", 0.1, 200)
        
        assert health.usage_metrics.api_requests == 1
        assert health.usage_metrics.api_errors == 0
        
        # Record failed API request
        health.record_api_request("/error", "POST", 0.2, 500)
        
        assert health.usage_metrics.api_requests == 2
        assert health.usage_metrics.api_errors == 1

    def test_voice_command_recording(self):
        """Test recording voice commands."""
        health = HealthChecker()
        
        health.record_voice_command()
        assert health.usage_metrics.voice_commands == 1
        assert health.usage_metrics.last_activity is not None

    def test_gui_interaction_recording(self):
        """Test recording GUI interactions."""
        health = HealthChecker()
        
        health.record_gui_interaction()
        assert health.usage_metrics.gui_interactions == 1
        assert health.usage_metrics.last_activity is not None

    def test_session_tracking(self):
        """Test session tracking."""
        health = HealthChecker()
        
        health.record_session_start()
        assert health.usage_metrics.session_count == 1

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation."""
        health = HealthChecker()
        
        # Record multiple commands with different response times
        response_times = [0.1, 0.2, 0.3, 0.4, 0.5]
        for i, rt in enumerate(response_times):
            health.record_command_execution(f"cmd_{i}", rt, success=True)
        
        # Check that performance metrics are calculated
        assert health.usage_metrics.avg_response_time > 0
        assert health.usage_metrics.p95_response_time > 0
        assert health.usage_metrics.p99_response_time > 0

    def test_custom_metrics(self):
        """Test custom metrics functionality."""
        health = HealthChecker()
        
        # Set custom metrics
        health.set_custom_metric("test_metric", 42)
        health.set_custom_metric("another_metric", 3.14)
        
        assert health.custom_metrics["test_metric"] == 42
        assert health.custom_metrics["another_metric"] == 3.14


class TestEnhancedMetrics:
    """Test enhanced metrics collection and reporting."""

    @pytest.mark.asyncio
    async def test_enhanced_metrics_in_prometheus_format(self):
        """Test that enhanced metrics are included in Prometheus format."""
        health = HealthChecker()
        
        # Generate some usage data
        health.record_command_execution("test_cmd", 0.1, success=True)
        health.record_command_execution("failing_cmd", 0.2, success=False)
        health.record_api_request("/test", "GET", 0.05, 200)
        health.record_api_request("/error", "POST", 0.1, 500)
        health.record_voice_command()
        health.record_gui_interaction()
        health.record_session_start()
        health.set_custom_metric("custom_test", 100)
        
        # Get metrics
        metrics_response = await health.get_metrics()
        metrics_text = metrics_response["body"]
        
        # Verify usage metrics are present
        assert "ultron_commands_total 2" in metrics_text
        assert "ultron_command_errors_total 1" in metrics_text
        assert "ultron_api_requests_total 2" in metrics_text
        assert "ultron_api_errors_total 1" in metrics_text
        assert "ultron_voice_commands_total 1" in metrics_text
        assert "ultron_gui_interactions_total 1" in metrics_text
        assert "ultron_sessions_total 1" in metrics_text
        
        # Verify performance metrics are present
        assert "ultron_response_time_seconds" in metrics_text
        assert "ultron_response_time_p95_seconds" in metrics_text
        assert "ultron_response_time_p99_seconds" in metrics_text
        assert "ultron_error_rate" in metrics_text
        
        # Verify custom metrics are present
        assert "ultron_custom_custom_test 100" in metrics_text

    @pytest.mark.asyncio
    async def test_error_rate_calculation(self):
        """Test error rate calculation."""
        health = HealthChecker()
        
        # Record commands with 25% error rate
        for i in range(4):
            success = i != 0  # First command fails, others succeed
            health.record_command_execution(f"cmd_{i}", 0.1, success=success)
        
        metrics_response = await health.get_metrics()
        metrics_text = metrics_response["body"]
        
        # Should have 25% error rate
        assert "ultron_error_rate 25.0" in metrics_text


class TestAPIMetricsIntegration:
    """Test API metrics integration."""

    def test_api_request_tracking(self):
        """Test that API requests are automatically tracked."""
        client = TestClient(app)
        
        # Make some requests
        response = client.get("/healthz")
        assert response.status_code == 200
        
        response = client.get("/metrics")
        assert response.status_code == 200
        
        # Check that metrics show API requests
        metrics_text = response.text
        assert "ultron_api_requests_total" in metrics_text
        # Should have at least 2 requests (healthz + metrics)
        # Note: The exact number may vary due to middleware processing


class TestMonitoringReliability:
    """Test monitoring system reliability and edge cases."""

    def test_metrics_with_no_data(self):
        """Test metrics collection when no usage data exists."""
        health = HealthChecker()
        
        # Should not crash even with no usage data
        metrics_response = asyncio.run(health.get_metrics())
        assert metrics_response["content_type"] == "text/plain; version=0.0.4; charset=utf-8"
        
        metrics_text = metrics_response["body"]
        assert "ultron_commands_total 0" in metrics_text
        assert "ultron_error_rate" not in metrics_text  # No error rate if no commands

    def test_response_time_history_limit(self):
        """Test that response time history is limited."""
        health = HealthChecker()
        max_times = health.max_response_times
        
        # Record more response times than the limit
        for i in range(max_times + 100):
            health.record_command_execution(f"cmd_{i}", 0.1, success=True)
        
        # Should not exceed the maximum
        assert len(health.response_times) <= max_times

    def test_custom_metric_name_sanitization(self):
        """Test that custom metric names are properly sanitized."""
        health = HealthChecker()
        
        # Set metrics with problematic names
        health.set_custom_metric("test-metric with spaces", 42)
        
        metrics_response = asyncio.run(health.get_metrics())
        metrics_text = metrics_response["body"]
        
        # Should be sanitized to valid Prometheus format
        assert "ultron_custom_test_metric_with_spaces 42" in metrics_text

    @patch('psutil.cpu_percent', return_value=50.0)
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_metrics_error_handling(self, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection with errors."""
        # Mock memory to raise exception
        mock_memory.side_effect = Exception("Memory error")
        
        health = HealthChecker()
        
        # Should not crash on system metrics errors
        metrics_response = asyncio.run(health.get_metrics())
        assert metrics_response["content_type"] == "text/plain; version=0.0.4; charset=utf-8"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])