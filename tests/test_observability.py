"""Tests for observability system"""
import pytest
from utils.observability import get_observability, ObservabilitySystem

def test_tracer():
    """Test tracing functionality"""
    obs = get_observability()
    
    with obs.trace_operation("test_op", {"test": True}):
        pass
    
    assert "test_op" in obs.tracer.traces
    assert len(obs.tracer.traces["test_op"]) > 0

def test_metrics():
    """Test metrics collection"""
    obs = get_observability()
    
    obs.record_metric("test_metric", 1.5, {"tag": "test"})
    obs.record_metric("test_metric", 2.5, {"tag": "test"})
    
    stats = obs.metrics.get_stats("test_metric")
    assert stats["count"] == 2
    assert stats["avg"] == 2.0

def test_health():
    """Test health monitoring"""
    obs = get_observability()
    health = obs.get_health()
    
    assert "status" in health
    assert health["status"] == "healthy"
