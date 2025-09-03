#!/usr/bin/env python3
"""Simple monitoring feature validation script."""

import sys
import os
import asyncio
import time

# Add the project root to the path
sys.path.insert(0, '.')

def test_imports():
    """Test that all monitoring modules can be imported."""
    try:
        from ultron_agent.health import HealthChecker, UsageMetrics, HealthStatus
        from ultron_agent.api import app
        from ultron_agent.logging_config import setup_logging, get_logger
        print("✅ All monitoring modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_usage_metrics():
    """Test usage metrics functionality."""
    try:
        from ultron_agent.health import HealthChecker
        
        health = HealthChecker()
        
        # Test command recording
        health.record_command_execution("test_command", 0.5, success=True)
        assert health.usage_metrics.commands_executed == 1
        assert health.usage_metrics.error_count == 0
        
        # Test error recording
        health.record_command_execution("failing_command", 0.2, success=False)
        assert health.usage_metrics.commands_executed == 2
        assert health.usage_metrics.error_count == 1
        
        # Test API request recording
        health.record_api_request("/test", "GET", 0.1, 200)
        assert health.usage_metrics.api_requests == 1
        assert health.usage_metrics.api_errors == 0
        
        # Test voice and GUI tracking
        health.record_voice_command()
        health.record_gui_interaction()
        health.record_session_start()
        
        assert health.usage_metrics.voice_commands == 1
        assert health.usage_metrics.gui_interactions == 1
        assert health.usage_metrics.session_count == 1
        
        # Test custom metrics
        health.set_custom_metric("test_metric", 42)
        assert health.custom_metrics["test_metric"] == 42
        
        print("✅ Usage metrics functionality verified")
        return True
    except Exception as e:
        print(f"❌ Usage metrics test failed: {e}")
        return False

async def test_enhanced_prometheus_metrics():
    """Test enhanced Prometheus metrics."""
    try:
        from ultron_agent.health import HealthChecker
        
        health = HealthChecker()
        
        # Generate test data
        health.record_command_execution("test_cmd", 0.1, success=True)
        health.record_command_execution("failing_cmd", 0.2, success=False)
        health.record_api_request("/test", "GET", 0.05, 200)
        health.record_voice_command()
        health.set_custom_metric("test_metric", 100)
        
        # Get metrics
        metrics = await health.get_metrics()
        metrics_text = metrics["body"]
        
        # Verify enhanced metrics are present
        required_metrics = [
            "ultron_commands_total",
            "ultron_command_errors_total",
            "ultron_api_requests_total",
            "ultron_voice_commands_total",
            "ultron_response_time_seconds",
            "ultron_custom_test_metric"
        ]
        
        for metric in required_metrics:
            if metric not in metrics_text:
                print(f"❌ Missing metric: {metric}")
                return False
        
        print("✅ Enhanced Prometheus metrics verified")
        return True
    except Exception as e:
        print(f"❌ Enhanced metrics test failed: {e}")
        return False

def test_api_integration():
    """Test API metrics integration."""
    try:
        from ultron_agent.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Make API requests
        response = client.get("/healthz")
        assert response.status_code == 200
        
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "ultron_api_requests_total" in response.text
        
        print("✅ API metrics integration verified")
        return True
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def test_performance_metrics():
    """Test performance metrics calculation."""
    try:
        from ultron_agent.health import HealthChecker
        
        health = HealthChecker()
        
        # Record multiple commands with different response times
        response_times = [0.1, 0.2, 0.3, 0.4, 0.5]
        for i, rt in enumerate(response_times):
            health.record_command_execution(f"cmd_{i}", rt, success=True)
        
        # Check that performance metrics are calculated
        assert health.usage_metrics.avg_response_time > 0
        assert health.usage_metrics.p95_response_time > 0
        assert health.usage_metrics.p99_response_time > 0
        
        print("✅ Performance metrics calculation verified")
        return True
    except Exception as e:
        print(f"❌ Performance metrics test failed: {e}")
        return False

async def main():
    """Run all monitoring tests."""
    print("🔍 Testing ULTRON Agent Enhanced Monitoring Features")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Usage Metrics", test_usage_metrics),
        ("Enhanced Prometheus Metrics", test_enhanced_prometheus_metrics),
        ("API Integration", test_api_integration),
        ("Performance Metrics", test_performance_metrics),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All monitoring features are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)