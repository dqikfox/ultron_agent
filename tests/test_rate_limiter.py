"""Tests for rate limiting functionality."""

import time
import pytest
from utils.rate_limiter import RateLimitManager, rate_limit


class TestRateLimitManager:
    """Test RateLimitManager class."""
    
    def test_token_bucket_algorithm(self):
        """Test basic token bucket algorithm."""
        limiter = RateLimitManager(requests_per_hour=5, burst_size=2)
        
        # First 5 requests should succeed
        for i in range(5):
            assert limiter.is_allowed('test_ip'), f"Request {i+1} should be allowed"
        
        # 6th request should fail
        assert not limiter.is_allowed('test_ip'), "Request 6 should be blocked"
    
    def test_rate_limit_per_ip(self):
        """Test rate limiting is per IP address."""
        limiter = RateLimitManager(requests_per_hour=3, burst_size=1)
        
        # IP1: 3 requests allowed
        assert limiter.is_allowed('ip1')
        assert limiter.is_allowed('ip1')
        assert limiter.is_allowed('ip1')
        assert not limiter.is_allowed('ip1')
        
        # IP2: Still has full quota
        assert limiter.is_allowed('ip2')
        assert limiter.is_allowed('ip2')
        assert limiter.is_allowed('ip2')
        assert not limiter.is_allowed('ip2')
    
    def test_remaining_requests(self):
        """Test get_remaining method."""
        limiter = RateLimitManager(requests_per_hour=10, burst_size=2)
        
        # Initial state
        assert limiter.get_remaining('test_ip') == 10
        
        # After 3 requests
        limiter.is_allowed('test_ip')
        limiter.is_allowed('test_ip')
        limiter.is_allowed('test_ip')
        assert limiter.get_remaining('test_ip') == 7
    
    def test_window_expiration(self):
        """Test that old requests expire after time window."""
        limiter = RateLimitManager(requests_per_hour=2, burst_size=1)
        limiter.window_seconds = 1  # 1 second window for testing
        
        # Use up quota
        assert limiter.is_allowed('test_ip')
        assert limiter.is_allowed('test_ip')
        assert not limiter.is_allowed('test_ip')
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed('test_ip')


class TestRateLimitDecorator:
    """Test rate_limit decorator."""
    
    def test_decorator_blocks_excess_requests(self):
        """Test decorator blocks requests after limit."""
        from flask import Flask
        
        app = Flask(__name__)
        
        @app.route('/test')
        @rate_limit(requests_per_hour=3, burst_size=1)
        def test_endpoint():
            return {'status': 'ok'}, 200
        
        with app.test_client() as client:
            # First 3 requests succeed
            for i in range(3):
                response = client.get('/test')
                assert response.status_code == 200, f"Request {i+1} should succeed"
            
            # 4th request blocked
            response = client.get('/test')
            assert response.status_code == 429, "Request 4 should be blocked"
            assert 'Rate limit exceeded' in response.get_json()['error']
    
    def test_performance_overhead(self):
        """Test rate limiter has minimal performance overhead."""
        limiter = RateLimitManager(requests_per_hour=1000, burst_size=10)
        
        # Measure 100 checks
        start_time = time.time()
        for i in range(100):
            limiter.is_allowed(f'ip_{i % 10}')
        elapsed = time.time() - start_time
        
        # Should be < 50ms total (< 0.5ms per check)
        assert elapsed < 0.05, f"Performance overhead too high: {elapsed*1000:.2f}ms"


class TestBruteForceProtection:
    """Test brute force attack protection."""
    
    def test_brute_force_blocked(self):
        """Test that brute force attacks are blocked."""
        limiter = RateLimitManager(requests_per_hour=100, burst_size=10)
        
        # Simulate 105 rapid requests
        allowed_count = 0
        blocked_count = 0
        
        for i in range(105):
            if limiter.is_allowed('attacker_ip'):
                allowed_count += 1
            else:
                blocked_count += 1
        
        # Should allow exactly 100, block 5
        assert allowed_count == 100, f"Should allow 100 requests, allowed {allowed_count}"
        assert blocked_count == 5, f"Should block 5 requests, blocked {blocked_count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
