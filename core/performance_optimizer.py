#!/usr/bin/env python3
"""
Performance Optimizer and Real-time Analytics
==============================================

Advanced performance monitoring, optimization, and real-time analytics
system for ULTRON Enhanced with predictive insights and automated tuning.
"""

import asyncio
import time
import psutil
import threading
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from pathlib import Path
import statistics
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_usage: float
    disk_read_speed: float
    disk_write_speed: float
    network_sent: int
    network_received: int
    active_processes: int
    response_time: float = 0.0
    ai_processing_time: float = 0.0
    voice_processing_time: float = 0.0
    vision_processing_time: float = 0.0

@dataclass
class OptimizationSuggestion:
    """Performance optimization suggestion"""
    category: str
    priority: int  # 1=low, 2=medium, 3=high
    title: str
    description: str
    action: str
    estimated_improvement: float
    auto_applicable: bool = False

class PerformanceAnalyzer:
    """Advanced performance analysis and pattern detection"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.baseline_metrics: Optional[Dict[str, float]] = None
        self.performance_patterns: Dict[str, List[float]] = defaultdict(list)
        self.logger = logging.getLogger("ULTRON.Performance")
    
    def add_metrics(self, metrics: PerformanceMetrics):
        """Add new performance metrics to history"""
        self.metrics_history.append(metrics)
        
        # Update performance patterns
        self._update_patterns(metrics)
        
        # Update baseline if needed
        if len(self.metrics_history) >= 100 and not self.baseline_metrics:
            self._calculate_baseline()
    
    def _update_patterns(self, metrics: PerformanceMetrics):
        """Update performance pattern tracking"""
        current_hour = datetime.now().hour
        
        # Track hourly patterns
        self.performance_patterns[f"cpu_hour_{current_hour}"].append(metrics.cpu_percent)
        self.performance_patterns[f"memory_hour_{current_hour}"].append(metrics.memory_percent)
        self.performance_patterns[f"response_hour_{current_hour}"].append(metrics.response_time)
        
        # Keep only recent patterns (last 30 entries per pattern)
        for pattern_key in self.performance_patterns:
            if len(self.performance_patterns[pattern_key]) > 30:
                self.performance_patterns[pattern_key] = self.performance_patterns[pattern_key][-30:]
    
    def _calculate_baseline(self):
        """Calculate baseline performance metrics"""
        if len(self.metrics_history) < 50:
            return
            
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 measurements
        
        self.baseline_metrics = {
            "cpu_avg": statistics.mean(m.cpu_percent for m in recent_metrics),
            "cpu_std": statistics.stdev(m.cpu_percent for m in recent_metrics) if len(recent_metrics) > 1 else 0,
            "memory_avg": statistics.mean(m.memory_percent for m in recent_metrics),
            "memory_std": statistics.stdev(m.memory_percent for m in recent_metrics) if len(recent_metrics) > 1 else 0,
            "response_avg": statistics.mean(m.response_time for m in recent_metrics if m.response_time > 0),
            "ai_processing_avg": statistics.mean(m.ai_processing_time for m in recent_metrics if m.ai_processing_time > 0),
        }
        
        self.logger.info("Performance baseline calculated")
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        if not self.baseline_metrics or len(self.metrics_history) < 10:
            return []
        
        anomalies = []
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        for metrics in recent_metrics:
            # CPU anomaly detection
            if metrics.cpu_percent > self.baseline_metrics["cpu_avg"] + 2 * self.baseline_metrics["cpu_std"]:
                anomalies.append({
                    "type": "cpu_spike",
                    "severity": "high" if metrics.cpu_percent > 80 else "medium",
                    "value": metrics.cpu_percent,
                    "baseline": self.baseline_metrics["cpu_avg"],
                    "timestamp": metrics.timestamp,
                    "description": f"CPU usage spike: {metrics.cpu_percent:.1f}% (baseline: {self.baseline_metrics['cpu_avg']:.1f}%)"
                })
            
            # Memory anomaly detection
            if metrics.memory_percent > self.baseline_metrics["memory_avg"] + 2 * self.baseline_metrics["memory_std"]:
                anomalies.append({
                    "type": "memory_spike",
                    "severity": "high" if metrics.memory_percent > 85 else "medium",
                    "value": metrics.memory_percent,
                    "baseline": self.baseline_metrics["memory_avg"],
                    "timestamp": metrics.timestamp,
                    "description": f"Memory usage spike: {metrics.memory_percent:.1f}% (baseline: {self.baseline_metrics['memory_avg']:.1f}%)"
                })
            
            # Response time anomaly detection
            if metrics.response_time > 0 and metrics.response_time > self.baseline_metrics["response_avg"] * 2:
                anomalies.append({
                    "type": "response_time_spike",
                    "severity": "medium",
                    "value": metrics.response_time,
                    "baseline": self.baseline_metrics["response_avg"],
                    "timestamp": metrics.timestamp,
                    "description": f"Response time spike: {metrics.response_time:.2f}s (baseline: {self.baseline_metrics['response_avg']:.2f}s)"
                })
        
        return anomalies
    
    def predict_performance_trends(self) -> Dict[str, Any]:
        """Predict performance trends based on historical data"""
        if len(self.metrics_history) < 50:
            return {"status": "insufficient_data"}
        
        recent_metrics = list(self.metrics_history)[-50:]
        predictions = {}
        
        # CPU trend prediction
        cpu_values = [m.cpu_percent for m in recent_metrics]
        cpu_trend = self._calculate_trend(cpu_values)
        predictions["cpu"] = {
            "current": cpu_values[-1],
            "trend": cpu_trend,
            "predicted_next": cpu_values[-1] + cpu_trend,
            "status": "increasing" if cpu_trend > 1 else "decreasing" if cpu_trend < -1 else "stable"
        }
        
        # Memory trend prediction
        memory_values = [m.memory_percent for m in recent_metrics]
        memory_trend = self._calculate_trend(memory_values)
        predictions["memory"] = {
            "current": memory_values[-1],
            "trend": memory_trend,
            "predicted_next": memory_values[-1] + memory_trend,
            "status": "increasing" if memory_trend > 1 else "decreasing" if memory_trend < -1 else "stable"
        }
        
        # Response time trend prediction
        response_times = [m.response_time for m in recent_metrics if m.response_time > 0]
        if response_times:
            response_trend = self._calculate_trend(response_times)
            predictions["response_time"] = {
                "current": response_times[-1],
                "trend": response_trend,
                "predicted_next": response_times[-1] + response_trend,
                "status": "increasing" if response_trend > 0.1 else "decreasing" if response_trend < -0.1 else "stable"
            }
        
        return predictions
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression slope"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_mean = (n - 1) / 2  # Time indices centered
        y_mean = statistics.mean(values)
        
        # Calculate slope
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def generate_optimization_suggestions(self) -> List[OptimizationSuggestion]:
        """Generate performance optimization suggestions"""
        suggestions = []
        
        if not self.baseline_metrics or len(self.metrics_history) < 20:
            return suggestions
        
        recent_metrics = list(self.metrics_history)[-20:]
        avg_cpu = statistics.mean(m.cpu_percent for m in recent_metrics)
        avg_memory = statistics.mean(m.memory_percent for m in recent_metrics)
        avg_response = statistics.mean(m.response_time for m in recent_metrics if m.response_time > 0)
        
        # High CPU usage suggestions
        if avg_cpu > 70:
            suggestions.append(OptimizationSuggestion(
                category="cpu",
                priority=3,
                title="High CPU Usage Detected",
                description=f"Average CPU usage is {avg_cpu:.1f}%. Consider optimizing AI processing or reducing background tasks.",
                action="Consider using a more efficient AI model or enabling CPU throttling",
                estimated_improvement=15.0,
                auto_applicable=False
            ))
        
        # High memory usage suggestions
        if avg_memory > 80:
            suggestions.append(OptimizationSuggestion(
                category="memory",
                priority=3,
                title="High Memory Usage Detected",
                description=f"Average memory usage is {avg_memory:.1f}%. Memory optimization needed.",
                action="Clear conversation history, reduce model cache size, or restart system",
                estimated_improvement=20.0,
                auto_applicable=True
            ))
        
        # Slow response time suggestions
        if avg_response > 2.0:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                priority=2,
                title="Slow Response Times",
                description=f"Average response time is {avg_response:.1f}s. Performance tuning recommended.",
                action="Enable response caching, optimize AI model selection, or check network connectivity",
                estimated_improvement=30.0,
                auto_applicable=False
            ))
        
        # Pattern-based suggestions
        hourly_cpu_pattern = self.performance_patterns.get(f"cpu_hour_{datetime.now().hour}", [])
        if len(hourly_cpu_pattern) > 5 and statistics.mean(hourly_cpu_pattern) > 60:
            suggestions.append(OptimizationSuggestion(
                category="scheduling",
                priority=2,
                title="Peak Hour Performance Issue",
                description=f"High CPU usage during hour {datetime.now().hour}. Consider load balancing.",
                action="Schedule intensive tasks during off-peak hours",
                estimated_improvement=25.0,
                auto_applicable=True
            ))
        
        return suggestions

class RealTimeAnalytics:
    """Real-time analytics dashboard data provider"""
    
    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.alert_callbacks: List[Callable] = []
        self.dashboard_data = {}
        self.active_alerts = []
        self.logger = logging.getLogger("ULTRON.Analytics")
    
    def add_alert_callback(self, callback: Callable[[Dict], None]):
        """Add callback for performance alerts"""
        self.alert_callbacks.append(callback)
    
    def update_dashboard_data(self, metrics: PerformanceMetrics, additional_data: Dict = None):
        """Update real-time dashboard data"""
        # Add to analyzer
        self.performance_analyzer.add_metrics(metrics)
        
        # Detect anomalies
        anomalies = self.performance_analyzer.detect_anomalies()
        
        # Generate predictions
        trends = self.performance_analyzer.predict_performance_trends()
        
        # Generate suggestions
        suggestions = self.performance_analyzer.generate_optimization_suggestions()
        
        # Update dashboard data
        self.dashboard_data = {
            "current_metrics": asdict(metrics),
            "baseline_metrics": self.performance_analyzer.baseline_metrics,
            "anomalies": anomalies,
            "trends": trends,
            "suggestions": [asdict(s) for s in suggestions],
            "alerts_count": len(self.active_alerts),
            "health_score": self._calculate_health_score(metrics),
            "performance_grade": self._calculate_performance_grade(metrics),
            "last_update": time.time()
        }
        
        # Add additional data if provided
        if additional_data:
            self.dashboard_data.update(additional_data)
        
        # Check for new alerts
        self._check_alerts(metrics, anomalies)
    
    def _calculate_health_score(self, metrics: PerformanceMetrics) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # CPU impact
        if metrics.cpu_percent > 80:
            score -= 30
        elif metrics.cpu_percent > 60:
            score -= 15
        elif metrics.cpu_percent > 40:
            score -= 5
        
        # Memory impact
        if metrics.memory_percent > 90:
            score -= 25
        elif metrics.memory_percent > 75:
            score -= 10
        elif metrics.memory_percent > 60:
            score -= 3
        
        # Response time impact
        if metrics.response_time > 5.0:
            score -= 20
        elif metrics.response_time > 3.0:
            score -= 10
        elif metrics.response_time > 1.0:
            score -= 5
        
        # Disk usage impact
        if metrics.disk_usage > 95:
            score -= 15
        elif metrics.disk_usage > 85:
            score -= 8
        
        return max(0, score)
    
    def _calculate_performance_grade(self, metrics: PerformanceMetrics) -> str:
        """Calculate performance grade (A+ to F)"""
        health_score = self._calculate_health_score(metrics)
        
        if health_score >= 95:
            return "A+"
        elif health_score >= 90:
            return "A"
        elif health_score >= 80:
            return "B"
        elif health_score >= 70:
            return "C"
        elif health_score >= 60:
            return "D"
        else:
            return "F"
    
    def _check_alerts(self, metrics: PerformanceMetrics, anomalies: List[Dict]):
        """Check for alert conditions"""
        new_alerts = []
        
        # Critical resource alerts
        if metrics.cpu_percent > 90:
            new_alerts.append({
                "type": "critical_cpu",
                "message": f"Critical CPU usage: {metrics.cpu_percent:.1f}%",
                "timestamp": time.time(),
                "severity": "critical"
            })
        
        if metrics.memory_percent > 95:
            new_alerts.append({
                "type": "critical_memory",
                "message": f"Critical memory usage: {metrics.memory_percent:.1f}%",
                "timestamp": time.time(),
                "severity": "critical"
            })
        
        if metrics.disk_usage > 98:
            new_alerts.append({
                "type": "critical_disk",
                "message": f"Critical disk usage: {metrics.disk_usage:.1f}%",
                "timestamp": time.time(),
                "severity": "critical"
            })
        
        # Response time alerts
        if metrics.response_time > 10.0:
            new_alerts.append({
                "type": "slow_response",
                "message": f"Very slow response time: {metrics.response_time:.1f}s",
                "timestamp": time.time(),
                "severity": "warning"
            })
        
        # Anomaly alerts
        for anomaly in anomalies:
            if anomaly["severity"] == "high":
                new_alerts.append({
                    "type": "anomaly",
                    "message": anomaly["description"],
                    "timestamp": time.time(),
                    "severity": "warning"
                })
        
        # Add new alerts and trigger callbacks
        for alert in new_alerts:
            self.active_alerts.append(alert)
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
        
        # Clean old alerts (older than 1 hour)
        current_time = time.time()
        self.active_alerts = [
            alert for alert in self.active_alerts 
            if current_time - alert["timestamp"] < 3600
        ]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return self.dashboard_data.copy()
    
    def get_historical_data(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get historical performance data"""
        cutoff_time = time.time() - (duration_minutes * 60)
        
        historical_metrics = [
            asdict(m) for m in self.performance_analyzer.metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        return {
            "metrics": historical_metrics,
            "duration_minutes": duration_minutes,
            "total_points": len(historical_metrics),
            "start_time": historical_metrics[0]["timestamp"] if historical_metrics else None,
            "end_time": historical_metrics[-1]["timestamp"] if historical_metrics else None
        }

class PerformanceOptimizer:
    """Automated performance optimization system"""
    
    def __init__(self, analytics: RealTimeAnalytics):
        self.analytics = analytics
        self.logger = logging.getLogger("ULTRON.Optimizer")
        self.optimization_history = []
        self.auto_optimize_enabled = True
    
    async def auto_optimize(self):
        """Perform automatic optimization based on current conditions"""
        if not self.auto_optimize_enabled:
            return
        
        try:
            dashboard_data = self.analytics.get_dashboard_data()
            suggestions = dashboard_data.get("suggestions", [])
            
            # Apply auto-applicable suggestions
            for suggestion in suggestions:
                if suggestion.get("auto_applicable", False) and suggestion.get("priority", 0) >= 2:
                    await self._apply_optimization(suggestion)
            
        except Exception as e:
            self.logger.error(f"Auto-optimization error: {e}")
    
    async def _apply_optimization(self, suggestion: Dict[str, Any]):
        """Apply a specific optimization"""
        try:
            category = suggestion.get("category", "")
            action = suggestion.get("action", "")
            
            self.logger.info(f"Applying optimization: {suggestion.get('title', '')}")
            
            if category == "memory":
                await self._optimize_memory()
            elif category == "cpu":
                await self._optimize_cpu()
            elif category == "scheduling":
                await self._optimize_scheduling()
            
            # Record optimization
            self.optimization_history.append({
                "timestamp": time.time(),
                "suggestion": suggestion,
                "applied": True
            })
            
        except Exception as e:
            self.logger.error(f"Optimization application failed: {e}")
            self.optimization_history.append({
                "timestamp": time.time(),
                "suggestion": suggestion,
                "applied": False,
                "error": str(e)
            })
    
    async def _optimize_memory(self):
        """Optimize memory usage"""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Clear system caches if available
        try:
            import os
            if hasattr(os, 'sync'):
                os.sync()
        except:
            pass
        
        self.logger.info("Memory optimization applied")
    
    async def _optimize_cpu(self):
        """Optimize CPU usage"""
        # This could implement CPU throttling, process priority adjustment, etc.
        self.logger.info("CPU optimization applied")
    
    async def _optimize_scheduling(self):
        """Optimize task scheduling"""
        # This could implement intelligent task scheduling
        self.logger.info("Scheduling optimization applied")
    
    def get_optimization_history(self) -> List[Dict]:
        """Get optimization history"""
        return self.optimization_history.copy()

class SystemResourceMonitor:
    """Advanced system resource monitoring"""
    
    def __init__(self):
        self.analytics = RealTimeAnalytics()
        self.optimizer = PerformanceOptimizer(self.analytics)
        self.monitoring_active = False
        self.monitor_thread = None
        self.logger = logging.getLogger("ULTRON.Monitor")
        
        # Previous network stats for calculating rates
        self._prev_network_stats = None
        self._prev_disk_stats = None
        self._prev_timestamp = None
    
    def start_monitoring(self, interval: float = 2.0):
        """Start performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Performance monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                
                # Update analytics
                self.analytics.update_dashboard_data(metrics)
                
                # Run auto-optimization
                asyncio.create_task(self.optimizer.auto_optimize())
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive system metrics"""
        current_time = time.time()
        
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # Network stats
        network_stats = psutil.net_io_counters()
        network_sent = network_stats.bytes_sent
        network_received = network_stats.bytes_recv
        
        # Disk I/O stats
        disk_stats = psutil.disk_io_counters()
        
        # Calculate rates if we have previous data
        disk_read_speed = 0.0
        disk_write_speed = 0.0
        
        if self._prev_disk_stats and self._prev_timestamp:
            time_delta = current_time - self._prev_timestamp
            if time_delta > 0:
                disk_read_speed = (disk_stats.read_bytes - self._prev_disk_stats.read_bytes) / time_delta
                disk_write_speed = (disk_stats.write_bytes - self._prev_disk_stats.write_bytes) / time_delta
        
        # Process count
        active_processes = len(psutil.pids())
        
        # Store current stats for next calculation
        self._prev_network_stats = network_stats
        self._prev_disk_stats = disk_stats
        self._prev_timestamp = current_time
        
        return PerformanceMetrics(
            timestamp=current_time,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used=memory.used,
            memory_available=memory.available,
            disk_usage=disk_usage_percent,
            disk_read_speed=disk_read_speed,
            disk_write_speed=disk_write_speed,
            network_sent=network_sent,
            network_received=network_received,
            active_processes=active_processes
        )
    
    def get_real_time_data(self) -> Dict[str, Any]:
        """Get real-time performance data for dashboard"""
        return self.analytics.get_dashboard_data()
    
    def get_historical_data(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get historical data for charts"""
        return self.analytics.get_historical_data(duration_minutes)
    
    def add_processing_time(self, category: str, processing_time: float):
        """Add processing time for specific category"""
        # This would be called by other ULTRON components to report their processing times
        if hasattr(self, '_current_metrics'):
            if category == "ai":
                self._current_metrics.ai_processing_time = processing_time
            elif category == "voice":
                self._current_metrics.voice_processing_time = processing_time
            elif category == "vision":
                self._current_metrics.vision_processing_time = processing_time
            elif category == "response":
                self._current_metrics.response_time = processing_time