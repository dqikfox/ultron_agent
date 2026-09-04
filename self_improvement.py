"""
ULTRON Agent - Self-Improvement & Evolutionary Framework
========================================================
Automated system for continuous enhancement, benchmarking, and optimization.

Core Capabilities:
- Performance monitoring and benchmarking
- Automated enhancement detection
- Module-level improvement suggestions
- Compatibility verification
- Changelog generation
- Scheduled improvement cycles

Usage:
    python self_improvement.py --scan       # Scan for improvements
    python self_improvement.py --benchmark  # Run benchmarks
    python self_improvement.py --suggest    # Get improvement suggestions
    python self_improvement.py --auto       # Run automated improvement cycle
"""

import os
import sys
import json
import time
import psutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from utils.ultron_logger import log_info, log_error, log_ai_decision

# Project root
PROJECT_ROOT = Path(__file__).parent


@dataclass
class PerformanceMetrics:
    """Performance metrics for benchmarking"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    api_latency: float
    ollama_latency: float
    gui_load_time: float
    tool_count: int
    active_services: int
    version: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EnhancementSuggestion:
    """Suggested enhancement with priority and impact"""
    module: str
    category: str  # performance, feature, usability, reliability
    priority: str  # critical, high, medium, low
    description: str
    estimated_impact: str
    suggested_action: str
    confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


class SelfImprovementEngine:
    """Main engine for continuous self-improvement"""

    def __init__(self):
        self.metrics_dir = PROJECT_ROOT / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.benchmark_file = self.metrics_dir / "benchmarks.json"
        self.suggestions_file = self.metrics_dir / "suggestions.json"
        self.changelog_file = PROJECT_ROOT / "EVOLUTION_CHANGELOG.md"
        self.version = self._get_version()

        log_info("self_improvement", "Evolution Framework initialized", version=self.version)

    def _get_version(self) -> str:
        """Get current version from git or config"""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "dev-" + datetime.now().strftime("%Y%m%d")

    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        log_info("self_improvement", "Collecting performance metrics")

        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent

        # Response times (simulate API calls)
        api_start = time.time()
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            api_latency = (time.time() - api_start) * 1000
        except Exception:
            api_latency = -1

        # Ollama latency
        ollama_start = time.time()
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            ollama_latency = (time.time() - ollama_start) * 1000
        except Exception:
            ollama_latency = -1

        # GUI load time (check if web server is responding)
        gui_start = time.time()
        try:
            import requests
            response = requests.get("http://localhost:8080", timeout=5)
            gui_load_time = (time.time() - gui_start) * 1000
        except Exception:
            gui_load_time = -1

        # Tool count
        tools_dir = PROJECT_ROOT / "tools"
        tool_count = len(list(tools_dir.glob("*_tool.py"))) if tools_dir.exists() else 0

        # Active services (check common ports)
        active_services = 0
        for port in [5000, 8080, 11434, 5175, 8002]:
            for conn in psutil.net_connections():
                local_port = getattr(conn.laddr, "port", None)
                if local_port == port and conn.status == 'LISTEN':
                    active_services += 1
                    break

        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_usage=cpu_percent,
            memory_usage=memory_percent,
            response_time=50.0,  # Placeholder for actual agent response time
            api_latency=api_latency,
            ollama_latency=ollama_latency,
            gui_load_time=gui_load_time,
            tool_count=tool_count,
            active_services=active_services,
            version=self.version
        )

        log_info("self_improvement", "Metrics collected", **metrics.to_dict())
        return metrics

    def save_metrics(self, metrics: PerformanceMetrics):
        """Save metrics to historical file"""
        history = []
        if self.benchmark_file.exists():
            with open(self.benchmark_file, 'r') as f:
                history = json.load(f)

        history.append(metrics.to_dict())

        # Keep last 100 entries
        history = history[-100:]

        with open(self.benchmark_file, 'w') as f:
            json.dump(history, f, indent=2)

        log_info("self_improvement", "Metrics saved to history", count=len(history))

    def compare_metrics(self, current: PerformanceMetrics) -> Dict[str, Any]:
        """Compare current metrics with historical data"""
        if not self.benchmark_file.exists():
            return {"status": "no_history", "comparison": None}

        with open(self.benchmark_file, 'r') as f:
            history = json.load(f)

        if not history:
            return {"status": "no_history", "comparison": None}

        # Get last 10 entries for comparison
        recent = history[-10:]

        # Calculate averages
        avg_cpu = sum(m['cpu_usage'] for m in recent) / len(recent)
        avg_memory = sum(m['memory_usage'] for m in recent) / len(recent)
        avg_api = sum(m['api_latency'] for m in recent if m['api_latency'] > 0) / max(1, len([m for m in recent if m['api_latency'] > 0]))

        comparison = {
            "cpu_change": current.cpu_usage - avg_cpu,
            "memory_change": current.memory_usage - avg_memory,
            "api_latency_change": current.api_latency - avg_api if current.api_latency > 0 else 0,
            "tool_count_change": current.tool_count - recent[-1]['tool_count'],
            "status": "improved" if (current.cpu_usage < avg_cpu and current.memory_usage < avg_memory) else "degraded"
        }

        log_info("self_improvement", "Metrics comparison complete", **comparison)
        return {"status": "compared", "comparison": comparison}

    def scan_for_improvements(self) -> List[EnhancementSuggestion]:
        """Scan codebase for potential improvements"""
        log_info("self_improvement", "Scanning for improvement opportunities")
        suggestions = []

        # 1. Check for large files that could be optimized
        for py_file in PROJECT_ROOT.glob("**/*.py"):
            if py_file.stat().st_size > 50000:  # Files > 50KB
                suggestions.append(EnhancementSuggestion(
                    module=str(py_file.relative_to(PROJECT_ROOT)),
                    category="performance",
                    priority="medium",
                    description=f"Large file ({py_file.stat().st_size / 1024:.1f}KB) may benefit from modularization",
                    estimated_impact="Improved maintainability and load times",
                    suggested_action="Split into smaller modules or refactor",
                    confidence=0.7
                ))

        # 2. Check for missing docstrings
        for py_file in PROJECT_ROOT.glob("*.py"):
            if py_file.name not in ['conftest.py', '__init__.py']:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '"""' not in content[:500]:  # No docstring in first 500 chars
                        suggestions.append(EnhancementSuggestion(
                            module=str(py_file.relative_to(PROJECT_ROOT)),
                            category="usability",
                            priority="low",
                            description="Missing module-level docstring",
                            estimated_impact="Improved code documentation and maintainability",
                            suggested_action="Add comprehensive docstring at module start",
                            confidence=0.9
                        ))

        # 3. Check for TODO/FIXME comments
        for py_file in PROJECT_ROOT.glob("**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if 'TODO' in line or 'FIXME' in line:
                            suggestions.append(EnhancementSuggestion(
                                module=str(py_file.relative_to(PROJECT_ROOT)),
                                category="reliability",
                                priority="medium",
                                description=f"TODO/FIXME found at line {line_num}: {line.strip()[:50]}",
                                estimated_impact="Resolve pending issues",
                                suggested_action="Address TODO/FIXME comment",
                                confidence=0.8
                            ))
            except Exception as e:
                continue

        # 4. Check for unused imports (simple heuristic)
        for py_file in PROJECT_ROOT.glob("**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    imports = [l for l in lines if l.strip().startswith('import ') or l.strip().startswith('from ')]
                    if len(imports) > 20:
                        suggestions.append(EnhancementSuggestion(
                            module=str(py_file.relative_to(PROJECT_ROOT)),
                            category="performance",
                            priority="low",
                            description=f"Large number of imports ({len(imports)}) - potential for optimization",
                            estimated_impact="Reduced memory footprint and faster imports",
                            suggested_action="Review and remove unused imports",
                            confidence=0.6
                        ))
            except Exception:
                continue

        # 5. Check for error handling
        for py_file in PROJECT_ROOT.glob("**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'def ' in content and 'try:' not in content:
                        suggestions.append(EnhancementSuggestion(
                            module=str(py_file.relative_to(PROJECT_ROOT)),
                            category="reliability",
                            priority="high",
                            description="Functions without error handling detected",
                            estimated_impact="Improved system stability and error recovery",
                            suggested_action="Add try/except blocks to critical functions",
                            confidence=0.7
                        ))
            except Exception:
                continue

        # 6. Check tool directory for potential enhancements
        tools_dir = PROJECT_ROOT / "tools"
        if tools_dir.exists():
            tool_files = list(tools_dir.glob("*_tool.py"))
            if len(tool_files) < 30:
                suggestions.append(EnhancementSuggestion(
                    module="tools/",
                    category="feature",
                    priority="medium",
                    description=f"Tool ecosystem has {len(tool_files)} tools - potential for expansion",
                    estimated_impact="Enhanced agent capabilities",
                    suggested_action="Add new tools for common tasks (e.g., database, cloud services)",
                    confidence=0.8
                ))

        # 7. Check for test coverage
        test_dir = PROJECT_ROOT / "tests"
        if test_dir.exists():
            test_count = len(list(test_dir.glob("test_*.py")))
            py_file_count = len(list(PROJECT_ROOT.glob("*.py")))
            coverage_ratio = test_count / max(1, py_file_count)
            if coverage_ratio < 0.3:
                suggestions.append(EnhancementSuggestion(
                    module="tests/",
                    category="reliability",
                    priority="high",
                    description=f"Low test coverage: {test_count} tests for {py_file_count} modules ({coverage_ratio*100:.1f}%)",
                    estimated_impact="Improved code quality and regression prevention",
                    suggested_action="Add unit tests for core modules",
                    confidence=0.9
                ))

        log_info("self_improvement", f"Scan complete: {len(suggestions)} suggestions generated")
        return suggestions

    def save_suggestions(self, suggestions: List[EnhancementSuggestion]):
        """Save suggestions to file"""
        with open(self.suggestions_file, 'w') as f:
            json.dump([s.to_dict() for s in suggestions], f, indent=2)
        log_info("self_improvement", "Suggestions saved", count=len(suggestions))

    def load_suggestions(self) -> List[EnhancementSuggestion]:
        """Load suggestions from file"""
        if not self.suggestions_file.exists():
            return []
        with open(self.suggestions_file, 'r') as f:
            data = json.load(f)
            return [EnhancementSuggestion(**s) for s in data]

    def generate_changelog_entry(self, improvements: List[str]) -> str:
        """Generate changelog entry for improvements"""
        date = datetime.now().strftime("%Y-%m-%d")
        version = self.version

        entry = f"\n## [{version}] - {date}\n\n"
        entry += "### Enhancements\n"
        for improvement in improvements:
            entry += f"- {improvement}\n"
        entry += "\n"

        return entry

    def update_changelog(self, entry: str):
        """Update EVOLUTION_CHANGELOG.md"""
        if not self.changelog_file.exists():
            self.changelog_file.write_text(f"# ULTRON Agent - Evolution Changelog\n\nDocumentation of continuous improvements and enhancements.\n{entry}")
        else:
            content = self.changelog_file.read_text()
            # Insert after header
            lines = content.split('\n')
            header_end = 2  # After title and blank line
            lines.insert(header_end, entry)
            self.changelog_file.write_text('\n'.join(lines))

        log_info("self_improvement", "Changelog updated")

    def run_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark cycle"""
        log_info("self_improvement", "Starting benchmark cycle")

        metrics = self.collect_metrics()
        self.save_metrics(metrics)
        comparison = self.compare_metrics(metrics)

        result = {
            "timestamp": metrics.timestamp,
            "metrics": metrics.to_dict(),
            "comparison": comparison,
            "status": "success"
        }

        log_ai_decision("self_improvement", "Benchmark cycle complete",
                       ai_model="heuristic", confidence_score=1.0,
                       reasoning="Performance metrics collected and compared")

        return result

    def run_improvement_scan(self) -> Dict[str, Any]:
        """Run improvement scan cycle"""
        log_info("self_improvement", "Starting improvement scan")

        suggestions = self.scan_for_improvements()
        self.save_suggestions(suggestions)

        # Categorize by priority
        critical = [s for s in suggestions if s.priority == 'critical']
        high = [s for s in suggestions if s.priority == 'high']
        medium = [s for s in suggestions if s.priority == 'medium']
        low = [s for s in suggestions if s.priority == 'low']

        result = {
            "timestamp": datetime.now().isoformat(),
            "total_suggestions": len(suggestions),
            "by_priority": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low)
            },
            "suggestions": [s.to_dict() for s in suggestions],
            "status": "success"
        }

        log_ai_decision("self_improvement", f"Scan complete: {len(suggestions)} suggestions",
                       ai_model="heuristic", confidence_score=0.85,
                       reasoning="Code analysis and improvement detection completed")

        return result

    def auto_improvement_cycle(self) -> Dict[str, Any]:
        """Run automated improvement cycle"""
        log_info("self_improvement", "Starting automated improvement cycle")

        # Step 1: Benchmark
        benchmark_result = self.run_benchmark()

        # Step 2: Scan for improvements
        scan_result = self.run_improvement_scan()

        # Step 3: Generate report
        report = {
            "cycle_timestamp": datetime.now().isoformat(),
            "version": self.version,
            "benchmark": benchmark_result,
            "scan": scan_result,
            "recommendations": []
        }

        # Add top recommendations
        suggestions = self.load_suggestions()
        high_priority = [s for s in suggestions if s.priority in ['critical', 'high']]
        report["recommendations"] = [s.to_dict() for s in high_priority[:10]]

        # Step 4: Save report
        report_file = self.metrics_dir / f"improvement_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        log_info("self_improvement", "Automated improvement cycle complete",
                report_file=str(report_file))

        return report


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="ULTRON Agent Self-Improvement & Evolution Framework"
    )
    parser.add_argument('--scan', action='store_true',
                       help='Scan for improvement opportunities')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmark')
    parser.add_argument('--suggest', action='store_true',
                       help='Show improvement suggestions')
    parser.add_argument('--auto', action='store_true',
                       help='Run automated improvement cycle')
    parser.add_argument('--report', action='store_true',
                       help='Generate comprehensive report')

    args = parser.parse_args()

    engine = SelfImprovementEngine()

    if args.benchmark:
        print("\n🔬 Running Performance Benchmark...")
        result = engine.run_benchmark()
        print(f"\n✅ Benchmark Complete!")
        print(f"   CPU Usage: {result['metrics']['cpu_usage']:.1f}%")
        print(f"   Memory Usage: {result['metrics']['memory_usage']:.1f}%")
        print(f"   API Latency: {result['metrics']['api_latency']:.1f}ms")
        print(f"   Active Services: {result['metrics']['active_services']}")
        if result['comparison']['comparison']:
            comp = result['comparison']['comparison']
            print(f"\n   Status: {comp['status'].upper()}")
            print(f"   CPU Change: {comp['cpu_change']:+.1f}%")
            print(f"   Memory Change: {comp['memory_change']:+.1f}%")

    elif args.scan:
        print("\n🔍 Scanning for Improvements...")
        result = engine.run_improvement_scan()
        print(f"\n✅ Scan Complete! Found {result['total_suggestions']} suggestions:")
        print(f"   Critical: {result['by_priority']['critical']}")
        print(f"   High: {result['by_priority']['high']}")
        print(f"   Medium: {result['by_priority']['medium']}")
        print(f"   Low: {result['by_priority']['low']}")
        print(f"\n   Suggestions saved to: {engine.suggestions_file}")

    elif args.suggest:
        print("\n💡 Loading Improvement Suggestions...")
        suggestions = engine.load_suggestions()
        if not suggestions:
            print("   No suggestions available. Run --scan first.")
        else:
            high_priority = [s for s in suggestions if s.priority in ['critical', 'high']]
            print(f"\n📋 Top {len(high_priority)} High-Priority Suggestions:\n")
            for i, sug in enumerate(high_priority[:10], 1):
                print(f"   {i}. [{sug.priority.upper()}] {sug.module}")
                print(f"      {sug.description}")
                print(f"      Action: {sug.suggested_action}")
                print(f"      Impact: {sug.estimated_impact}\n")

    elif args.auto:
        print("\n🤖 Running Automated Improvement Cycle...")
        result = engine.auto_improvement_cycle()
        print(f"\n✅ Cycle Complete!")
        print(f"   Version: {result['version']}")
        print(f"   Timestamp: {result['cycle_timestamp']}")
        print(f"   Total Suggestions: {result['scan']['total_suggestions']}")
        print(f"   High Priority: {result['scan']['by_priority']['high']}")
        print(f"   Recommendations: {len(result['recommendations'])}")

    elif args.report:
        print("\n📊 Generating Comprehensive Report...")
        # Run both benchmark and scan
        benchmark = engine.run_benchmark()
        scan = engine.run_improvement_scan()

        print("\n" + "="*60)
        print("ULTRON AGENT - EVOLUTION REPORT")
        print("="*60)
        print(f"\nVersion: {engine.version}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n📈 PERFORMANCE METRICS")
        print("-" * 60)
        print(f"CPU Usage: {benchmark['metrics']['cpu_usage']:.1f}%")
        print(f"Memory Usage: {benchmark['metrics']['memory_usage']:.1f}%")
        print(f"API Latency: {benchmark['metrics']['api_latency']:.1f}ms")
        print(f"Ollama Latency: {benchmark['metrics']['ollama_latency']:.1f}ms")
        print(f"GUI Load Time: {benchmark['metrics']['gui_load_time']:.1f}ms")
        print(f"Active Services: {benchmark['metrics']['active_services']}")
        print(f"Tool Count: {benchmark['metrics']['tool_count']}")

        print("\n🔍 IMPROVEMENT OPPORTUNITIES")
        print("-" * 60)
        print(f"Total Suggestions: {scan['total_suggestions']}")
        print(f"  Critical: {scan['by_priority']['critical']}")
        print(f"  High: {scan['by_priority']['high']}")
        print(f"  Medium: {scan['by_priority']['medium']}")
        print(f"  Low: {scan['by_priority']['low']}")

        print("\n" + "="*60)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
