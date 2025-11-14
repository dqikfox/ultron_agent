"""
Tests for Evolution Engine and Cache Manager
Testing self-improvement tracking and caching functionality
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

from utils.cache_manager import CacheManager, get_cache_manager, cache_get, cache_set
from utils.evolution_engine import (
    EvolutionEngine, get_evolution_engine, CodeMetrics, EvolutionEvent
)


class TestCacheManager:
    """Test suite for intelligent cache manager"""

    @pytest.fixture
    def cache_manager(self, tmp_path):
        """Create cache manager with temporary storage"""
        return CacheManager(
            sqlite_path=str(tmp_path / "test_cache.db"),
            default_ttl=60,
            max_memory_mb=10
        )

    def test_cache_set_and_get(self, cache_manager):
        """Test basic cache set and get operations"""
        key = "test_key"
        value = {"data": "test_value", "number": 42}
        
        # Set value
        assert cache_manager.set(key, value) is True
        
        # Get value
        retrieved = cache_manager.get(key)
        assert retrieved == value

    def test_cache_miss(self, cache_manager):
        """Test cache miss returns None"""
        result = cache_manager.get("non_existent_key")
        assert result is None

    def test_cache_expiration(self, cache_manager):
        """Test that cached items expire after TTL"""
        key = "expiring_key"
        value = "expiring_value"
        
        # Set with 1 second TTL
        cache_manager.set(key, value, ttl=1)
        
        # Should be available immediately
        assert cache_manager.get(key) == value
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache_manager.get(key) is None

    def test_cache_delete(self, cache_manager):
        """Test cache deletion"""
        key = "delete_key"
        value = "delete_value"
        
        cache_manager.set(key, value)
        assert cache_manager.get(key) == value
        
        cache_manager.delete(key)
        assert cache_manager.get(key) is None

    def test_cache_stats(self, cache_manager):
        """Test cache statistics tracking"""
        # Perform some operations
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        cache_manager.get("key1")  # Hit
        cache_manager.get("key1")  # Hit
        cache_manager.get("missing")  # Miss
        
        stats = cache_manager.get_stats()
        
        assert stats['hits'] >= 2
        assert stats['misses'] >= 1
        assert stats['sets'] >= 2
        assert 'hit_rate' in stats

    def test_cache_clear(self, cache_manager):
        """Test clearing all cache"""
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        assert cache_manager.get("key1") is not None
        
        cache_manager.clear()
        
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None

    def test_complex_value_caching(self, cache_manager):
        """Test caching complex nested structures"""
        complex_value = {
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": "b"},
                "bool": True,
                "null": None
            }
        }
        
        cache_manager.set("complex", complex_value)
        retrieved = cache_manager.get("complex")
        
        assert retrieved == complex_value


class TestEvolutionEngine:
    """Test suite for evolution engine"""

    @pytest.fixture
    def evolution_engine(self, tmp_path):
        """Create evolution engine with temporary workspace"""
        return EvolutionEngine(workspace_root=str(tmp_path))

    def test_record_evolution_event(self, evolution_engine):
        """Test recording evolution events"""
        event = evolution_engine.record_evolution(
            event_type="enhance",
            component="test_component",
            description="Test enhancement",
            impact_score=0.8,
            ai_model="copilot"
        )
        
        assert isinstance(event, EvolutionEvent)
        assert event.event_type == "enhance"
        assert event.component == "test_component"
        assert event.impact_score == 0.8

    def test_code_metrics_analysis(self, evolution_engine, tmp_path):
        """Test Python file analysis for code metrics"""
        # Create a test Python file
        test_file = tmp_path / "test_code.py"
        test_code = '''
"""Test module"""

def test_function():
    """A test function"""
    if True:
        return 42
    return 0

class TestClass:
    """Test class"""
    def method(self):
        pass
'''
        test_file.write_text(test_code)
        
        metrics = evolution_engine.analyze_python_file(test_file)
        
        assert isinstance(metrics, CodeMetrics)
        assert metrics.lines_of_code > 0
        assert metrics.function_count >= 1
        assert metrics.class_count >= 1
        assert 0 <= metrics.maintainability_index <= 100

    def test_evolution_report_generation(self, evolution_engine):
        """Test generating evolution reports"""
        # Record some events
        for i in range(3):
            evolution_engine.record_evolution(
                event_type="optimize",
                component=f"component_{i}",
                description=f"Optimization {i}",
                impact_score=0.5 + i * 0.1
            )
        
        report = evolution_engine.generate_evolution_report(days=1, save_to_file=False)
        
        assert report.total_events >= 3
        assert "optimize" in report.events_by_type
        assert report.efficiency_gain > 0

    def test_improvement_suggestions(self, evolution_engine, tmp_path):
        """Test generating improvement suggestions"""
        # Create some test files with varying quality
        for i in range(3):
            test_file = tmp_path / f"code_{i}.py"
            test_file.write_text(f"def func{i}(): pass\n" * (10 + i * 20))
        
        suggestions = evolution_engine.suggest_next_improvements(limit=5)
        
        assert isinstance(suggestions, list)
        for suggestion in suggestions:
            assert 'type' in suggestion
            assert 'target' in suggestion
            assert 'priority' in suggestion
            assert 'estimated_impact' in suggestion

    def test_evolution_summary(self, evolution_engine):
        """Test getting evolution summary"""
        # Record diverse events
        event_types = ['enhance', 'optimize', 'refactor']
        for event_type in event_types:
            evolution_engine.record_evolution(
                event_type=event_type,
                component="test_component",
                description=f"Test {event_type}",
                impact_score=0.7
            )
        
        summary = evolution_engine.get_evolution_summary(days=1)
        
        assert 'total_events' in summary
        assert 'cycle_number' in summary
        assert 'avg_impact_score' in summary
        assert summary['total_events'] >= 3

    def test_complexity_calculation(self, evolution_engine):
        """Test cyclomatic complexity calculation"""
        # Simple code
        simple_code = "def func(): return 42"
        simple_complexity = evolution_engine._calculate_complexity(simple_code)
        
        # Complex code with branches
        complex_code = """
def func():
    if x:
        for i in range(10):
            while True:
                try:
                    pass
                except:
                    pass
"""
        complex_complexity = evolution_engine._calculate_complexity(complex_code)
        
        assert complex_complexity > simple_complexity

    def test_maintainability_calculation(self, evolution_engine):
        """Test maintainability index calculation"""
        # Well-documented code should have higher maintainability
        high_maintainability = evolution_engine._calculate_maintainability(
            code_lines=100,
            comment_lines=20,
            complexity=5
        )
        
        # Poorly documented, complex code should have lower maintainability
        low_maintainability = evolution_engine._calculate_maintainability(
            code_lines=100,
            comment_lines=2,
            complexity=50
        )
        
        assert high_maintainability > low_maintainability


@pytest.mark.integration
class TestCacheBrainIntegration:
    """Integration tests for cache manager with brain module"""

    def test_brain_response_caching(self, tmp_path):
        """Test that brain responses are properly cached"""
        # This would require mocking the brain module
        # For now, test the cache manager directly
        cache = CacheManager(sqlite_path=str(tmp_path / "brain_cache.db"))
        
        prompt_hash = "test_prompt_hash"
        response = "This is a cached response"
        
        # Simulate brain caching
        cache_key = f"brain:chat:{prompt_hash}"
        cache.set(cache_key, response)
        
        # Verify retrieval
        cached_response = cache.get(cache_key)
        assert cached_response == response


@pytest.mark.integration
class TestEvolutionTracking:
    """Integration tests for evolution tracking"""

    def test_full_evolution_cycle(self, tmp_path):
        """Test complete evolution tracking cycle"""
        engine = EvolutionEngine(workspace_root=str(tmp_path))
        
        # Record various improvements
        improvements = [
            ("enhance", "Added new feature"),
            ("optimize", "Improved performance"),
            ("refactor", "Cleaned up code"),
            ("document", "Added documentation")
        ]
        
        for event_type, description in improvements:
            engine.record_evolution(
                event_type=event_type,
                component="test_system",
                description=description,
                impact_score=0.7,
                ai_model="copilot_evolution"
            )
        
        # Generate report
        report = engine.generate_evolution_report(days=1, save_to_file=False)
        
        # Verify report contents
        assert report.total_events == len(improvements)
        assert len(report.events_by_type) == len(set(t for t, _ in improvements))
        assert report.efficiency_gain > 0
        
        # Get suggestions
        suggestions = engine.suggest_next_improvements()
        assert isinstance(suggestions, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
