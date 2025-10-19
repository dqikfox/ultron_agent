"""
ULTRON Agent 3.0 - Evolution Engine
Self-improvement tracking, code quality metrics, and evolution reporting
"""

import json
import ast
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import subprocess

from utils.ultron_logger import get_logger

logger = get_logger("evolution_engine")


@dataclass
class CodeMetrics:
    """Code quality metrics for a file or module"""
    lines_of_code: int
    comment_lines: int
    blank_lines: int
    function_count: int
    class_count: int
    complexity_score: float  # Cyclomatic complexity
    maintainability_index: float  # 0-100, higher is better
    test_coverage: float  # 0-100%


@dataclass
class EvolutionEvent:
    """Represents a single evolution event"""
    timestamp: str
    event_type: str  # enhance, optimize, extend, refactor, integrate, document
    component: str
    description: str
    metrics_before: Optional[Dict[str, Any]]
    metrics_after: Optional[Dict[str, Any]]
    impact_score: float  # 0-1.0
    ai_model: str


@dataclass
class EvolutionReport:
    """Comprehensive evolution report"""
    report_id: str
    generated_at: str
    cycle_number: int
    total_events: int
    events_by_type: Dict[str, int]
    efficiency_gain: float
    code_quality_improvement: float
    suggested_improvements: List[str]
    performance_metrics: Dict[str, Any]


class EvolutionEngine:
    """
    Self-improvement tracking and evolution management system.
    Monitors code changes, tracks improvements, and suggests enhancements.
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.evolution_file = self.workspace_root / "logs" / "evolution_history.jsonl"
        self.metrics_file = self.workspace_root / "logs" / "code_metrics.json"
        self.cycle_number = 0
        self.events: List[EvolutionEvent] = []
        
        # Ensure logs directory exists
        self.evolution_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load previous state
        self._load_state()
        
        logger.info(f"Evolution engine initialized (Cycle #{self.cycle_number})")

    def _load_state(self) -> None:
        """Load evolution history and current cycle number"""
        try:
            if self.evolution_file.exists():
                with open(self.evolution_file, 'r') as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())
                            event = EvolutionEvent(**event_data)
                            self.events.append(event)
                        except Exception:
                            continue
                
                # Determine current cycle number
                if self.events:
                    last_event = self.events[-1]
                    # Extract cycle number from description or timestamp
                    self.cycle_number = len(set(e.timestamp.split('T')[0] for e in self.events))
                
                logger.info(f"Loaded {len(self.events)} evolution events")
                
        except Exception as e:
            logger.error(f"Error loading evolution state: {e}")

    def record_evolution(self,
                        event_type: str,
                        component: str,
                        description: str,
                        metrics_before: Optional[Dict[str, Any]] = None,
                        metrics_after: Optional[Dict[str, Any]] = None,
                        impact_score: float = 0.5,
                        ai_model: str = "copilot") -> EvolutionEvent:
        """
        Record an evolution event
        
        Args:
            event_type: Type of evolution (enhance, optimize, extend, refactor, integrate, document)
            component: Component or file affected
            description: Description of the change
            metrics_before: Metrics before change
            metrics_after: Metrics after change
            impact_score: Estimated impact (0-1.0)
            ai_model: AI model that made the change
            
        Returns:
            EvolutionEvent object
        """
        event = EvolutionEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            component=component,
            description=description,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            impact_score=impact_score,
            ai_model=ai_model
        )
        
        # Append to events list
        self.events.append(event)
        
        # Write to file
        try:
            with open(self.evolution_file, 'a') as f:
                f.write(json.dumps(asdict(event)) + '\n')
            
            logger.info(f"Evolution event recorded: {event_type} - {component}")
            
        except Exception as e:
            logger.error(f"Error recording evolution event: {e}")
        
        return event

    def analyze_python_file(self, file_path: Path) -> CodeMetrics:
        """
        Analyze Python file for code quality metrics
        
        Args:
            file_path: Path to Python file
            
        Returns:
            CodeMetrics object
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Count different types of lines
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            blank_lines = sum(1 for line in lines if not line.strip())
            code_lines = total_lines - comment_lines - blank_lines
            
            # Parse AST for function and class counts
            try:
                tree = ast.parse(content)
                function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
                class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            except SyntaxError:
                function_count = 0
                class_count = 0
            
            # Calculate complexity (simplified - count branches)
            complexity_score = self._calculate_complexity(content)
            
            # Calculate maintainability index (simplified)
            maintainability_index = self._calculate_maintainability(
                code_lines, comment_lines, complexity_score
            )
            
            return CodeMetrics(
                lines_of_code=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                function_count=function_count,
                class_count=class_count,
                complexity_score=complexity_score,
                maintainability_index=maintainability_index,
                test_coverage=0.0  # Would require pytest-cov integration
            )
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return CodeMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0)

    def _calculate_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity (simplified)"""
        # Count decision points
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with']
        complexity = 1  # Base complexity
        
        for keyword in decision_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + keyword + r'\b'
            complexity += len(re.findall(pattern, content))
        
        return float(complexity)

    def _calculate_maintainability(self, code_lines: int, comment_lines: int, complexity: float) -> float:
        """Calculate maintainability index (0-100)"""
        if code_lines == 0:
            return 100.0
        
        # Simplified formula based on comment ratio and complexity
        comment_ratio = comment_lines / (code_lines + comment_lines) if code_lines > 0 else 0
        
        # Higher comment ratio = better maintainability
        # Lower complexity = better maintainability
        maintainability = 100 - (complexity * 2) + (comment_ratio * 20)
        
        return max(0.0, min(100.0, maintainability))

    def scan_codebase_metrics(self) -> Dict[str, CodeMetrics]:
        """
        Scan entire codebase and generate metrics
        
        Returns:
            Dictionary mapping file paths to CodeMetrics
        """
        metrics = {}
        
        # Scan Python files
        python_files = list(self.workspace_root.rglob("*.py"))
        
        for file_path in python_files:
            # Skip test files and virtual environments
            if 'test' in str(file_path).lower() or 'venv' in str(file_path) or '.venv' in str(file_path):
                continue
            
            try:
                relative_path = file_path.relative_to(self.workspace_root)
                metrics[str(relative_path)] = self.analyze_python_file(file_path)
            except Exception as e:
                logger.error(f"Error scanning {file_path}: {e}")
        
        # Save metrics
        try:
            metrics_dict = {path: asdict(m) for path, m in metrics.items()}
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_dict, f, indent=2)
            
            logger.info(f"Scanned {len(metrics)} Python files")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
        
        return metrics

    def generate_evolution_report(self, 
                                 days: int = 7,
                                 save_to_file: bool = True) -> EvolutionReport:
        """
        Generate comprehensive evolution report
        
        Args:
            days: Number of days to include in report
            save_to_file: Whether to save report to file
            
        Returns:
            EvolutionReport object
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter events within time range
        recent_events = [
            e for e in self.events
            if datetime.fromisoformat(e.timestamp) >= cutoff_date
        ]
        
        # Count events by type
        events_by_type = defaultdict(int)
        total_impact = 0.0
        
        for event in recent_events:
            events_by_type[event.event_type] += 1
            total_impact += event.impact_score
        
        # Calculate efficiency gain
        efficiency_gain = total_impact / len(recent_events) if recent_events else 0.0
        
        # Calculate code quality improvement
        code_quality_improvement = self._calculate_quality_improvement(recent_events)
        
        # Generate suggestions
        suggestions = self._generate_improvement_suggestions(recent_events)
        
        # Get performance metrics
        performance_metrics = self._get_performance_metrics()
        
        # Increment cycle number
        self.cycle_number += 1
        
        report = EvolutionReport(
            report_id=f"EVO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            generated_at=datetime.now().isoformat(),
            cycle_number=self.cycle_number,
            total_events=len(recent_events),
            events_by_type=dict(events_by_type),
            efficiency_gain=efficiency_gain,
            code_quality_improvement=code_quality_improvement,
            suggested_improvements=suggestions,
            performance_metrics=performance_metrics
        )
        
        if save_to_file:
            report_file = self.workspace_root / "logs" / f"evolution_report_{report.report_id}.json"
            with open(report_file, 'w') as f:
                json.dump(asdict(report), f, indent=2)
            
            logger.info(f"Evolution report generated: {report_file}")
        
        return report

    def _calculate_quality_improvement(self, events: List[EvolutionEvent]) -> float:
        """Calculate overall code quality improvement from events"""
        if not events:
            return 0.0
        
        improvements = []
        
        for event in events:
            if event.metrics_before and event.metrics_after:
                # Compare maintainability indices
                before = event.metrics_before.get('maintainability_index', 50.0)
                after = event.metrics_after.get('maintainability_index', 50.0)
                improvement = after - before
                improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0.0

    def _generate_improvement_suggestions(self, events: List[EvolutionEvent]) -> List[str]:
        """Generate improvement suggestions based on recent activity"""
        suggestions = []
        
        # Analyze event patterns
        event_types = [e.event_type for e in events]
        
        # Check if certain types are underrepresented
        if event_types.count('document') < len(events) * 0.1:
            suggestions.append("Increase documentation coverage - only {:.1f}% of recent changes included documentation".format(
                event_types.count('document') / len(events) * 100 if events else 0
            ))
        
        if event_types.count('optimize') < len(events) * 0.15:
            suggestions.append("Focus on optimization - performance improvements could yield high value")
        
        if event_types.count('refactor') < len(events) * 0.2:
            suggestions.append("Consider refactoring older code - technical debt may be accumulating")
        
        # Analyze component diversity
        components = [e.component for e in events]
        if len(set(components)) < len(components) * 0.3:
            suggestions.append("Broaden evolution scope - changes are concentrated in few components")
        
        return suggestions or ["Continue current evolution strategy - metrics are healthy"]

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        # This would integrate with the performance profiler
        # For now, return basic metrics
        return {
            'avg_response_time_ms': 0,  # Would come from profiler
            'cache_hit_rate': 0.0,  # Would come from cache manager
            'error_rate': 0.0,  # Would come from error tracking
            'uptime_hours': 0.0
        }

    def suggest_next_improvements(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generate prioritized list of next improvement suggestions
        
        Args:
            limit: Maximum number of suggestions
            
        Returns:
            List of improvement suggestions with priority and details
        """
        suggestions = []
        
        # Scan codebase for potential improvements
        metrics = self.scan_codebase_metrics()
        
        # Find files with low maintainability
        for file_path, file_metrics in metrics.items():
            if file_metrics.maintainability_index < 60:
                suggestions.append({
                    'priority': 'high',
                    'type': 'refactor',
                    'target': file_path,
                    'reason': f"Low maintainability index ({file_metrics.maintainability_index:.1f})",
                    'estimated_impact': 0.7
                })
        
        # Find files with high complexity
        for file_path, file_metrics in metrics.items():
            if file_metrics.complexity_score > 50:
                suggestions.append({
                    'priority': 'medium',
                    'type': 'optimize',
                    'target': file_path,
                    'reason': f"High complexity score ({file_metrics.complexity_score:.1f})",
                    'estimated_impact': 0.6
                })
        
        # Find files lacking documentation
        for file_path, file_metrics in metrics.items():
            comment_ratio = file_metrics.comment_lines / (file_metrics.lines_of_code + file_metrics.comment_lines)
            if comment_ratio < 0.1:
                suggestions.append({
                    'priority': 'low',
                    'type': 'document',
                    'target': file_path,
                    'reason': f"Low documentation coverage ({comment_ratio*100:.1f}%)",
                    'estimated_impact': 0.4
                })
        
        # Sort by priority and impact
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: (priority_order[x['priority']], -x['estimated_impact']))
        
        return suggestions[:limit]

    def get_evolution_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of evolution activity"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_events = [
            e for e in self.events
            if datetime.fromisoformat(e.timestamp) >= cutoff_date
        ]
        
        return {
            'total_events': len(recent_events),
            'cycle_number': self.cycle_number,
            'days_analyzed': days,
            'avg_impact_score': sum(e.impact_score for e in recent_events) / len(recent_events) if recent_events else 0.0,
            'most_active_component': max(
                (e.component for e in recent_events),
                key=lambda c: sum(1 for e in recent_events if e.component == c),
                default='none'
            ),
            'dominant_event_type': max(
                (e.event_type for e in recent_events),
                key=lambda t: sum(1 for e in recent_events if e.event_type == t),
                default='none'
            )
        }


# Global instance
_evolution_engine: Optional[EvolutionEngine] = None


def get_evolution_engine() -> EvolutionEngine:
    """Get or create global evolution engine instance"""
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = EvolutionEngine()
    return _evolution_engine


# Convenience functions
def record_evolution(event_type: str, component: str, description: str, **kwargs) -> EvolutionEvent:
    """Record an evolution event"""
    return get_evolution_engine().record_evolution(event_type, component, description, **kwargs)


def generate_evolution_report(days: int = 7) -> EvolutionReport:
    """Generate evolution report"""
    return get_evolution_engine().generate_evolution_report(days)


def suggest_improvements(limit: int = 5) -> List[Dict[str, Any]]:
    """Get improvement suggestions"""
    return get_evolution_engine().suggest_next_improvements(limit)
