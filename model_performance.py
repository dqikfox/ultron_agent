"""
Model Performance Tracker - Monitors AI model accuracy, speed, and reliability
Provides insights into model performance and helps optimize model selection
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from utils.ultron_logger import log_info, log_error
from collections import defaultdict


class ModelPerformanceTracker:
    """Tracks and analyzes AI model performance metrics"""
    
    def __init__(self, metrics_dir: Optional[Path] = None):
        self.metrics_dir = metrics_dir or Path(__file__).parent / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.performance_file = self.metrics_dir / "model_performance.json"
        self.metrics = self._load_metrics()
        
    def _load_metrics(self) -> Dict[str, Any]:
        """Load performance metrics from file"""
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log_error("model_performance", f"Failed to load metrics: {e}")
        return {"models": {}, "history": []}
    
    def _save_metrics(self):
        """Save performance metrics to file"""
        try:
            with open(self.performance_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            log_error("model_performance", f"Failed to save metrics: {e}")
    
    def record_inference(
        self,
        model_name: str,
        task_type: str,
        latency_ms: float,
        success: bool,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        error: Optional[str] = None
    ):
        """Record a model inference operation"""
        
        # Initialize model entry if new
        if model_name not in self.metrics["models"]:
            self.metrics["models"][model_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_latency_ms": 0.0,
                "min_latency_ms": float('inf'),
                "max_latency_ms": 0.0,
                "total_tokens_input": 0,
                "total_tokens_output": 0,
                "by_task": {},
                "error_types": defaultdict(int),
                "first_seen": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
        
        model = self.metrics["models"][model_name]
        
        # Update counters
        model["total_requests"] += 1
        if success:
            model["successful_requests"] += 1
        else:
            model["failed_requests"] += 1
            if error:
                model["error_types"][error] = model.get(
                    "error_types", {}
                ).get(error, 0) + 1
        
        # Update latency stats
        model["total_latency_ms"] += latency_ms
        model["min_latency_ms"] = min(
            model["min_latency_ms"], latency_ms
        )
        model["max_latency_ms"] = max(
            model["max_latency_ms"], latency_ms
        )
        
        # Update token counts
        if tokens_input:
            model["total_tokens_input"] += tokens_input
        if tokens_output:
            model["total_tokens_output"] += tokens_output
        
        # Update task-specific metrics
        if task_type not in model["by_task"]:
            model["by_task"][task_type] = {
                "count": 0,
                "success_count": 0,
                "total_latency": 0.0
            }
        
        task = model["by_task"][task_type]
        task["count"] += 1
        if success:
            task["success_count"] += 1
        task["total_latency"] += latency_ms
        
        # Update last used timestamp
        model["last_used"] = datetime.now().isoformat()
        
        # Add to history
        self.metrics["history"].append({
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "task": task_type,
            "latency_ms": latency_ms,
            "success": success,
            "error": error
        })
        
        # Keep last 10000 history entries
        self.metrics["history"] = self.metrics["history"][-10000:]
        
        # Save to disk
        self._save_metrics()
        
        log_info(
            "model_performance",
            f"Recorded {model_name} inference: {task_type} "
            f"{'✓' if success else '✗'} ({latency_ms:.1f}ms)"
        )
    
    def get_model_stats(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive statistics for a specific model"""
        if model_name not in self.metrics["models"]:
            return None
        
        model = self.metrics["models"][model_name]
        
        # Calculate derived metrics
        total = model["total_requests"]
        avg_latency = model["total_latency_ms"] / total if total > 0 else 0
        success_rate = model["successful_requests"] / total if total > 0 else 0
        
        return {
            "model_name": model_name,
            "total_requests": total,
            "successful_requests": model["successful_requests"],
            "failed_requests": model["failed_requests"],
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "min_latency_ms": model["min_latency_ms"],
            "max_latency_ms": model["max_latency_ms"],
            "total_tokens_input": model["total_tokens_input"],
            "total_tokens_output": model["total_tokens_output"],
            "tasks": model["by_task"],
            "error_types": dict(model.get("error_types", {})),
            "first_seen": model["first_seen"],
            "last_used": model["last_used"]
        }
    
    def get_all_models_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all tracked models"""
        stats = []
        for model_name in self.metrics["models"]:
            model_stats = self.get_model_stats(model_name)
            if model_stats:
                stats.append(model_stats)
        
        # Sort by total requests (descending)
        stats.sort(key=lambda x: x["total_requests"], reverse=True)
        return stats
    
    def get_best_model_for_task(self, task_type: str) -> Optional[str]:
        """Recommend the best model for a specific task"""
        best_model = None
        best_score = -1
        
        for model_name, model in self.metrics["models"].items():
            if task_type in model["by_task"]:
                task = model["by_task"][task_type]
                
                # Calculate score based on success rate and speed
                if task["count"] > 0:
                    success_rate = task["success_count"] / task["count"]
                    avg_latency = task["total_latency"] / task["count"]
                    
                    # Score: 70% success rate, 30% speed (inverse)
                    # Normalize latency to 0-1 range (assume max 10000ms)
                    speed_score = 1 - min(avg_latency / 10000, 1)
                    score = (0.7 * success_rate) + (0.3 * speed_score)
                    
                    if score > best_score:
                        best_score = score
                        best_model = model_name
        
        return best_model
    
    def get_performance_trends(
        self,
        model_name: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance trends for a model over time"""
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_history = [
            entry for entry in self.metrics["history"]
            if entry["model"] == model_name
            and datetime.fromisoformat(entry["timestamp"]) > cutoff
        ]
        
        if not recent_history:
            return {
                "model": model_name,
                "period_hours": hours,
                "data_points": 0,
                "trends": {}
            }
        
        # Calculate trends
        total = len(recent_history)
        successes = sum(1 for e in recent_history if e["success"])
        latencies = [e["latency_ms"] for e in recent_history]
        
        return {
            "model": model_name,
            "period_hours": hours,
            "data_points": total,
            "success_rate": successes / total if total > 0 else 0,
            "avg_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "requests_per_hour": total / hours
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance report"""
        
        report = ["=" * 60]
        report.append("🔴 MODEL PERFORMANCE REPORT 🔴")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall statistics
        total_models = len(self.metrics["models"])
        total_requests = sum(
            m["total_requests"] for m in self.metrics["models"].values()
        )
        total_successes = sum(
            m["successful_requests"] for m in self.metrics["models"].values()
        )
        overall_success_rate = (
            total_successes / total_requests if total_requests > 0 else 0
        )
        
        report.append(f"📊 Total Models Tracked: {total_models}")
        report.append(f"📊 Total Requests: {total_requests:,}")
        report.append(f"📊 Overall Success Rate: {overall_success_rate:.1%}")
        report.append("")
        
        # Per-model statistics
        report.append("=" * 60)
        report.append("📈 PER-MODEL STATISTICS")
        report.append("=" * 60)
        
        for stats in self.get_all_models_stats():
            report.append(f"\n🤖 {stats['model_name']}")
            report.append(f"   Requests: {stats['total_requests']:,}")
            report.append(f"   Success Rate: {stats['success_rate']:.1%}")
            report.append(f"   Avg Latency: {stats['avg_latency_ms']:.1f}ms")
            report.append(
                f"   Latency Range: {stats['min_latency_ms']:.1f}ms - "
                f"{stats['max_latency_ms']:.1f}ms"
            )
            
            if stats['tasks']:
                report.append(f"   Tasks: {', '.join(stats['tasks'].keys())}")
            
            if stats['error_types']:
                report.append("   Recent Errors:")
                for error, count in stats['error_types'].items():
                    report.append(f"     - {error}: {count}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def export_to_json(self, filepath: Optional[Path] = None) -> Path:
        """Export metrics to JSON file"""
        export_path = filepath or (
            self.metrics_dir / f"performance_export_{datetime.now():%Y%m%d_%H%M%S}.json"
        )
        
        with open(export_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        log_info(
            "model_performance",
            f"Exported metrics to {export_path}"
        )
        return export_path


# Global tracker instance
_tracker = None


def get_tracker() -> ModelPerformanceTracker:
    """Get or create the global model performance tracker"""
    global _tracker
    if _tracker is None:
        _tracker = ModelPerformanceTracker()
    return _tracker


if __name__ == "__main__":
    # Test the tracker
    tracker = ModelPerformanceTracker()
    
    # Simulate some inferences
    tracker.record_inference(
        "llava:7b", "chat", 245.3, True, 150, 200
    )
    tracker.record_inference(
        "llama3.1", "chat", 189.7, True, 100, 150
    )
    tracker.record_inference(
        "deepseek-r1:14b", "code", 523.1, True, 200, 300
    )
    tracker.record_inference(
        "llava:7b", "vision", 345.2, False, 100, 0, "Timeout"
    )
    
    # Print report
    print(tracker.generate_report())
    
    # Get best model for task
    best = tracker.get_best_model_for_task("chat")
    print(f"\nBest model for chat: {best}")
