"""
Continuous Improvement System for ULTRON Agent 3.0
Automated code review, diagnostics, and self-improvement capabilities
"""

import asyncio
import logging
import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import tempfile
import shutil

logger = logging.getLogger(__name__)

@dataclass
class ImprovementSuggestion:
    """Represents a suggested improvement"""
    id: str
    category: str  # "performance", "security", "functionality", "ui", "documentation"
    priority: str  # "critical", "high", "medium", "low"  
    title: str
    description: str
    suggested_action: str
    confidence: float  # 0.0 to 1.0
    auto_applicable: bool
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    timestamp: Optional[datetime] = None
    applied: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SystemDiagnostic:
    """Represents a system diagnostic finding"""
    category: str
    severity: str  # "info", "warning", "error", "critical"
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False

class ContinuousImprovementSystem:
    """
    Automated system for continuous code improvement, diagnostics, and self-healing
    """
    
    def __init__(self, agent=None, config: Optional[Dict] = None):
        self.agent = agent
        self.config = config or {}
        self.suggestions: List[ImprovementSuggestion] = []
        self.diagnostics: List[SystemDiagnostic] = []
        self.improvement_thread: Optional[threading.Thread] = None
        self.active = False
        self.last_analysis_time: Optional[datetime] = None
        
        # Analysis intervals (in seconds)
        self.code_analysis_interval = self.config.get("analysis_interval", 300)  # 5 minutes
        self.diagnostic_interval = self.config.get("diagnostic_interval", 60)    # 1 minute
        self.auto_apply_threshold = self.config.get("auto_apply_threshold", 0.9) # Auto-apply if confidence > 90%
        
        # Directories to analyze
        self.watch_dirs = [
            Path("."),
            Path("tools"),
            Path("utils"), 
            Path("gui"),
            Path("new pokedex")
        ]
        
        # File patterns to include/exclude
        self.include_patterns = ["*.py", "*.js", "*.html", "*.css", "*.json", "*.yaml", "*.md"]
        self.exclude_patterns = [
            "__pycache__", "*.pyc", ".git", "node_modules", "venv", ".env",
            "screenshots", "logs", "cache", "*.log"
        ]
        
        self.improvement_log_file = Path("improvement_log.json")
        self.diagnostic_log_file = Path("diagnostic_log.json")
        
        # Load previous improvements and diagnostics
        self._load_previous_data()

    def start_continuous_improvement(self):
        """Start the continuous improvement system"""
        if self.improvement_thread and self.improvement_thread.is_alive():
            logger.info("Continuous improvement already running")
            return
            
        self.active = True
        self.improvement_thread = threading.Thread(target=self._improvement_loop, daemon=True)
        self.improvement_thread.start()
        
        logger.info("🔄 Continuous Improvement System started")
        logger.info(f"  - Code analysis every {self.code_analysis_interval}s")
        logger.info(f"  - Diagnostics every {self.diagnostic_interval}s") 
        logger.info(f"  - Auto-apply threshold: {self.auto_apply_threshold}")

    def stop_continuous_improvement(self):
        """Stop the continuous improvement system"""
        self.active = False
        if self.improvement_thread:
            self.improvement_thread.join(timeout=5)
        logger.info("🛑 Continuous Improvement System stopped")

    def _improvement_loop(self):
        """Main improvement loop running in background"""
        last_code_analysis = 0
        last_diagnostic = 0
        
        while self.active:
            try:
                current_time = time.time()
                
                # Run diagnostics
                if current_time - last_diagnostic >= self.diagnostic_interval:
                    self._run_diagnostics()
                    last_diagnostic = current_time
                
                # Run code analysis
                if current_time - last_code_analysis >= self.code_analysis_interval:
                    self._run_code_analysis()
                    self._apply_automatic_improvements()
                    last_code_analysis = current_time
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in improvement loop: {e}", exc_info=True)
                time.sleep(30)  # Wait longer on errors

    def _run_diagnostics(self):
        """Run system diagnostics"""
        logger.debug("🔍 Running system diagnostics...")
        
        # Check service health
        try:
            from service_manager import get_service_manager
            service_manager = get_service_manager()
            report = service_manager.get_service_status_report()
            
            for service_name, service_info in report["services"].items():
                if service_info["required"] and not service_info["healthy"]:
                    self.diagnostics.append(SystemDiagnostic(
                        category="service_health",
                        severity="error" if service_info["required"] else "warning",
                        message=f"Service {service_name} is not healthy",
                        details=service_info,
                        timestamp=datetime.now()
                    ))
        except ImportError:
            logger.warning("Service manager not available for diagnostics")
        
        # Check disk space
        disk_usage = shutil.disk_usage(Path.cwd())
        free_gb = disk_usage.free / (1024**3)
        
        if free_gb < 1:  # Less than 1GB free
            self.diagnostics.append(SystemDiagnostic(
                category="system_resources",
                severity="critical",
                message="Critically low disk space",
                details={"free_gb": free_gb, "total_gb": disk_usage.total / (1024**3)},
                timestamp=datetime.now()
            ))
        elif free_gb < 5:  # Less than 5GB free
            self.diagnostics.append(SystemDiagnostic(
                category="system_resources", 
                severity="warning",
                message="Low disk space",
                details={"free_gb": free_gb, "total_gb": disk_usage.total / (1024**3)},
                timestamp=datetime.now()
            ))
        
        # Check for common configuration issues
        self._check_configuration_issues()
        
        # Check for missing dependencies
        self._check_dependencies()
        
        # Save diagnostics
        self._save_diagnostics()

    def _check_configuration_issues(self):
        """Check for common configuration problems"""
        config_file = Path("ultron_config.json")
        
        if not config_file.exists():
            self.diagnostics.append(SystemDiagnostic(
                category="configuration",
                severity="error", 
                message="Configuration file missing",
                details={"file": str(config_file)},
                timestamp=datetime.now()
            ))
            return
        
        try:
            with open(config_file) as f:
                config = json.load(f)
                
            # Check for missing critical config values
            critical_keys = ["nvidia_nim", "llm_model", "version"]
            for key in critical_keys:
                if key not in config:
                    self.diagnostics.append(SystemDiagnostic(
                        category="configuration",
                        severity="warning",
                        message=f"Missing configuration key: {key}",
                        details={"key": key, "file": str(config_file)},
                        timestamp=datetime.now()
                    ))
                    
            # Check for null API keys that might be needed
            api_keys = ["openai_api_key", "nvidia_nim.api_key", "anthropic_api_key"]
            for key_path in api_keys:
                value = config
                try:
                    for key in key_path.split('.'):
                        value = value[key]
                    if value is None:
                        self.diagnostics.append(SystemDiagnostic(
                            category="configuration",
                            severity="info",
                            message=f"API key not configured: {key_path}",
                            details={"key": key_path},
                            timestamp=datetime.now()
                        ))
                except (KeyError, TypeError):
                    pass  # Key doesn't exist, that's okay
                    
        except Exception as e:
            self.diagnostics.append(SystemDiagnostic(
                category="configuration",
                severity="error",
                message=f"Error reading configuration: {e}",
                details={"file": str(config_file), "error": str(e)},
                timestamp=datetime.now()
            ))

    def _check_dependencies(self):
        """Check for missing Python dependencies"""
        try:
            import pkg_resources
            
            # Common dependencies that should be available
            required_packages = [
                "pyautogui", "requests", "psutil", "pathlib", "logging",
                "asyncio", "threading", "json", "time", "datetime"
            ]
            
            for package in required_packages:
                try:
                    if package in ["pathlib", "logging", "asyncio", "threading", "json", "time", "datetime"]:
                        # These are built-in modules
                        __import__(package)
                    else:
                        pkg_resources.get_distribution(package)
                except (ImportError, pkg_resources.DistributionNotFound):
                    self.diagnostics.append(SystemDiagnostic(
                        category="dependencies",
                        severity="warning",
                        message=f"Missing dependency: {package}",
                        details={"package": package},
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")

    def _run_code_analysis(self):
        """Run code analysis and generate improvement suggestions"""
        logger.debug("🔍 Running code analysis...")
        self.last_analysis_time = datetime.now()
        
        # Analyze Python files for common improvements
        for directory in self.watch_dirs:
            if not directory.exists():
                continue
                
            for py_file in directory.rglob("*.py"):
                if self._should_analyze_file(py_file):
                    self._analyze_python_file(py_file)
        
        # Analyze configuration files
        self._analyze_config_files()
        
        # Analyze documentation
        self._analyze_documentation()
        
        # Save suggestions
        self._save_suggestions()
        
        logger.info(f"📊 Code analysis complete. Found {len(self.suggestions)} suggestions")

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        path_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.replace("*", "") in path_str:
                return False
        
        # Don't analyze this file to avoid recursion
        if file_path.name == __file__ or "continuous_improvement" in file_path.name:
            return False
            
        return True

    def _analyze_python_file(self, file_path: Path):
        """Analyze a Python file for improvements"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # Check for common improvements
                self._check_error_handling(file_path, line_num, line, lines)
                self._check_logging_improvements(file_path, line_num, line)
                self._check_performance_issues(file_path, line_num, line)
                self._check_security_issues(file_path, line_num, line)
                self._check_code_style(file_path, line_num, line)
                
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

    def _check_error_handling(self, file_path: Path, line_num: int, line: str, all_lines: List[str]):
        """Check for error handling improvements"""
        line_stripped = line.strip()
        
        # Look for bare except clauses
        if line_stripped == "except:" or line_stripped.startswith("except:"):
            self.suggestions.append(ImprovementSuggestion(
                id=f"error_handling_{file_path.name}_{line_num}",
                category="functionality",
                priority="medium",
                title="Avoid bare except clauses",
                description="Bare except clauses catch all exceptions including system exits",
                suggested_action="Replace with 'except Exception as e:' and add logging",
                confidence=0.85,
                auto_applicable=True,
                file_path=str(file_path),
                line_number=line_num,
                code_before=line,
                code_after=line.replace("except:", "except Exception as e:")
            ))
        
        # Look for missing exception logging
        if line_stripped.startswith("except ") and "as " in line_stripped:
            # Check if next few lines have logging
            has_logging = False
            for j in range(line_num, min(line_num + 5, len(all_lines))):
                if "logger" in all_lines[j] or "logging" in all_lines[j] or "print" in all_lines[j]:
                    has_logging = True
                    break
            
            if not has_logging:
                self.suggestions.append(ImprovementSuggestion(
                    id=f"exception_logging_{file_path.name}_{line_num}",
                    category="functionality",
                    priority="low",
                    title="Add exception logging",
                    description="Exception caught but not logged for debugging",
                    suggested_action="Add logging statement in exception handler",
                    confidence=0.7,
                    auto_applicable=False,
                    file_path=str(file_path),
                    line_number=line_num
                ))

    def _check_logging_improvements(self, file_path: Path, line_num: int, line: str):
        """Check for logging improvements"""
        # Look for print statements that should be logging
        if "print(" in line and not any(x in line for x in ["test", "debug", "__main__"]):
            self.suggestions.append(ImprovementSuggestion(
                id=f"logging_{file_path.name}_{line_num}",
                category="functionality",
                priority="low",
                title="Replace print with logging",
                description="Print statement should use proper logging",
                suggested_action="Replace print() with logger.info() or appropriate level",
                confidence=0.6,
                auto_applicable=False,
                file_path=str(file_path),
                line_number=line_num,
                code_before=line.strip()
            ))

    def _check_performance_issues(self, file_path: Path, line_num: int, line: str):
        """Check for performance issues"""
        # Look for inefficient string concatenation in loops
        if "for " in line and "+=" in line and "str" in line:
            self.suggestions.append(ImprovementSuggestion(
                id=f"performance_{file_path.name}_{line_num}",
                category="performance",
                priority="medium",
                title="Inefficient string concatenation",
                description="String concatenation in loops is inefficient",
                suggested_action="Use list.append() and ''.join() instead",
                confidence=0.75,
                auto_applicable=False,
                file_path=str(file_path),
                line_number=line_num
            ))

    def _check_security_issues(self, file_path: Path, line_num: int, line: str):
        """Check for security issues"""
        # Look for potential command injection
        if any(func in line for func in ["subprocess.call", "os.system", "subprocess.run"]) and "shell=True" in line:
            self.suggestions.append(ImprovementSuggestion(
                id=f"security_{file_path.name}_{line_num}",
                category="security",
                priority="high",
                title="Potential command injection risk",
                description="Using shell=True can be dangerous with untrusted input",
                suggested_action="Avoid shell=True or sanitize input carefully",
                confidence=0.8,
                auto_applicable=False,
                file_path=str(file_path),
                line_number=line_num
            ))
        
        # Look for hardcoded credentials
        if any(keyword in line.lower() for keyword in ["password", "secret", "key", "token"]) and "=" in line and any(quote in line for quote in ['"', "'"]):
            if not any(safe in line.lower() for safe in ["input", "config", "env", "none", "null"]):
                self.suggestions.append(ImprovementSuggestion(
                    id=f"security_creds_{file_path.name}_{line_num}",
                    category="security",
                    priority="critical",
                    title="Potential hardcoded credential",
                    description="Hardcoded credentials should be avoided",
                    suggested_action="Use environment variables or configuration files",
                    confidence=0.7,
                    auto_applicable=False,
                    file_path=str(file_path),
                    line_number=line_num
                ))

    def _check_code_style(self, file_path: Path, line_num: int, line: str):
        """Check for code style improvements"""
        # Check for long lines
        if len(line) > 100:
            self.suggestions.append(ImprovementSuggestion(
                id=f"style_line_length_{file_path.name}_{line_num}",
                category="style",
                priority="low",
                title="Long line",
                description=f"Line exceeds 100 characters ({len(line)} chars)",
                suggested_action="Break long line into multiple lines",
                confidence=0.9,
                auto_applicable=False,
                file_path=str(file_path),
                line_number=line_num
            ))

    def _analyze_config_files(self):
        """Analyze configuration files for improvements"""
        config_files = ["ultron_config.json", "package.json", "requirements.txt"]
        
        for config_file in config_files:
            path = Path(config_file)
            if path.exists():
                if config_file == "ultron_config.json":
                    self._analyze_ultron_config(path)

    def _analyze_ultron_config(self, config_path: Path):
        """Analyze ULTRON configuration for improvements"""
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check for missing optional but useful settings
            recommendations = {
                "use_voice": "Enable voice capabilities for better user interaction",
                "use_vision": "Enable vision capabilities for screen analysis",
                "enable_maverick": "Enable Maverick auto-analysis for improvements",
                "pochi_config_path": "Set path to Pochi configuration"
            }
            
            for key, description in recommendations.items():
                if key not in config or config[key] in [None, False, ""]:
                    self.suggestions.append(ImprovementSuggestion(
                        id=f"config_{key}",
                        category="functionality",
                        priority="low",
                        title=f"Consider enabling {key}",
                        description=description,
                        suggested_action=f"Set {key} to appropriate value in {config_path}",
                        confidence=0.6,
                        auto_applicable=False,
                        file_path=str(config_path)
                    ))
                    
        except Exception as e:
            logger.error(f"Error analyzing config {config_path}: {e}")

    def _analyze_documentation(self):
        """Analyze documentation for improvements"""
        doc_files = ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"]
        
        for doc_file in doc_files:
            path = Path(doc_file)
            if not path.exists() and doc_file == "README.md":
                self.suggestions.append(ImprovementSuggestion(
                    id="missing_readme",
                    category="documentation",
                    priority="medium", 
                    title="Missing README.md",
                    description="Project should have a README.md file",
                    suggested_action="Create comprehensive README.md with installation and usage instructions",
                    confidence=0.9,
                    auto_applicable=False
                ))

    def _apply_automatic_improvements(self):
        """Apply improvements that can be safely automated"""
        applied_count = 0
        
        for suggestion in self.suggestions:
            if (suggestion.auto_applicable and 
                suggestion.confidence >= self.auto_apply_threshold and 
                not suggestion.applied):
                
                try:
                    if self._apply_suggestion(suggestion):
                        suggestion.applied = True
                        applied_count += 1
                        logger.info(f"✅ Auto-applied: {suggestion.title}")
                    else:
                        logger.warning(f"❌ Failed to auto-apply: {suggestion.title}")
                except Exception as e:
                    logger.error(f"Error applying suggestion {suggestion.id}: {e}")
        
        if applied_count > 0:
            logger.info(f"🔧 Auto-applied {applied_count} improvements")

    def _apply_suggestion(self, suggestion: ImprovementSuggestion) -> bool:
        """Apply a specific improvement suggestion"""
        if not suggestion.file_path or not suggestion.code_before or not suggestion.code_after:
            return False
            
        try:
            file_path = Path(suggestion.file_path)
            if not file_path.exists():
                return False
                
            content = file_path.read_text(encoding='utf-8')
            
            # Simple replacement - could be made more sophisticated
            if suggestion.code_before in content:
                new_content = content.replace(suggestion.code_before, suggestion.code_after)
                
                # Create backup
                backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
                shutil.copy2(file_path, backup_path)
                
                # Write new content
                file_path.write_text(new_content, encoding='utf-8')
                
                logger.info(f"Applied improvement to {file_path}")
                return True
            else:
                logger.warning(f"Code to replace not found in {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying suggestion to {suggestion.file_path}: {e}")
            return False

    def get_improvement_report(self) -> Dict[str, Any]:
        """Generate comprehensive improvement report"""
        suggestions_by_category = {}
        suggestions_by_priority = {}
        
        for suggestion in self.suggestions:
            # Group by category
            if suggestion.category not in suggestions_by_category:
                suggestions_by_category[suggestion.category] = []
            suggestions_by_category[suggestion.category].append(suggestion)
            
            # Group by priority
            if suggestion.priority not in suggestions_by_priority:
                suggestions_by_priority[suggestion.priority] = []
            suggestions_by_priority[suggestion.priority].append(suggestion)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "last_analysis": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "total_suggestions": len(self.suggestions),
            "applied_suggestions": len([s for s in self.suggestions if s.applied]),
            "auto_applicable": len([s for s in self.suggestions if s.auto_applicable]),
            "high_confidence": len([s for s in self.suggestions if s.confidence >= 0.8]),
            "categories": {cat: len(suggestions) for cat, suggestions in suggestions_by_category.items()},
            "priorities": {pri: len(suggestions) for pri, suggestions in suggestions_by_priority.items()},
            "suggestions": [asdict(s) for s in self.suggestions[-20:]],  # Last 20 suggestions
            "diagnostics": [asdict(d) for d in self.diagnostics[-10:]]   # Last 10 diagnostics
        }
        
        return report

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for improvement dashboard"""
        recent_suggestions = [s for s in self.suggestions if 
                            s.timestamp and s.timestamp > datetime.now() - timedelta(hours=24)]
        
        recent_diagnostics = [d for d in self.diagnostics if 
                            d.timestamp > datetime.now() - timedelta(hours=24)]
        
        return {
            "status": "active" if self.active else "inactive",
            "last_analysis": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "recent_suggestions": len(recent_suggestions),
            "recent_diagnostics": len(recent_diagnostics),
            "critical_issues": len([d for d in recent_diagnostics if d.severity == "critical"]),
            "auto_applied": len([s for s in recent_suggestions if s.applied]),
            "suggestions_by_priority": {
                "critical": len([s for s in recent_suggestions if s.priority == "critical"]),
                "high": len([s for s in recent_suggestions if s.priority == "high"]),
                "medium": len([s for s in recent_suggestions if s.priority == "medium"]),
                "low": len([s for s in recent_suggestions if s.priority == "low"])
            }
        }

    def _load_previous_data(self):
        """Load previous suggestions and diagnostics"""
        try:
            if self.improvement_log_file.exists():
                with open(self.improvement_log_file) as f:
                    data = json.load(f)
                    for item in data.get("suggestions", []):
                        suggestion = ImprovementSuggestion(**item)
                        suggestion.timestamp = datetime.fromisoformat(item["timestamp"]) if item.get("timestamp") else datetime.now()
                        self.suggestions.append(suggestion)
                        
        except Exception as e:
            logger.error(f"Error loading previous improvements: {e}")
        
        try:
            if self.diagnostic_log_file.exists():
                with open(self.diagnostic_log_file) as f:
                    data = json.load(f)
                    for item in data.get("diagnostics", []):
                        diagnostic = SystemDiagnostic(
                            category=item["category"],
                            severity=item["severity"],
                            message=item["message"],
                            details=item["details"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            resolved=item.get("resolved", False)
                        )
                        self.diagnostics.append(diagnostic)
                        
        except Exception as e:
            logger.error(f"Error loading previous diagnostics: {e}")

    def _save_suggestions(self):
        """Save improvement suggestions to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "suggestions": [asdict(s) for s in self.suggestions[-100:]]  # Keep last 100
            }
            
            with open(self.improvement_log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving suggestions: {e}")

    def _save_diagnostics(self):
        """Save diagnostics to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "diagnostics": [asdict(d) for d in self.diagnostics[-50:]]  # Keep last 50
            }
            
            with open(self.diagnostic_log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving diagnostics: {e}")

    def force_analysis(self):
        """Force immediate code analysis"""
        logger.info("🔄 Forcing immediate code analysis...")
        self._run_code_analysis()
        self._run_diagnostics()
        self._apply_automatic_improvements()
        return self.get_improvement_report()

    def apply_suggestion_by_id(self, suggestion_id: str) -> bool:
        """Manually apply a specific suggestion by ID"""
        for suggestion in self.suggestions:
            if suggestion.id == suggestion_id:
                if self._apply_suggestion(suggestion):
                    suggestion.applied = True
                    self._save_suggestions()
                    logger.info(f"✅ Applied suggestion: {suggestion.title}")
                    return True
                else:
                    logger.error(f"❌ Failed to apply suggestion: {suggestion.title}")
                    return False
        
        logger.warning(f"Suggestion {suggestion_id} not found")
        return False

# Global instance
_improvement_system = None

def get_improvement_system(agent=None, config=None) -> ContinuousImprovementSystem:
    """Get the global continuous improvement system"""
    global _improvement_system
    if _improvement_system is None:
        _improvement_system = ContinuousImprovementSystem(agent=agent, config=config)
    return _improvement_system

def main():
    """Test the continuous improvement system"""
    logging.basicConfig(level=logging.INFO)
    
    system = ContinuousImprovementSystem()
    
    print("🔄 ULTRON Continuous Improvement System Test")
    print("=" * 50)
    
    # Force immediate analysis
    report = system.force_analysis()
    
    print(f"Analysis Results:")
    print(f"  Total suggestions: {report['total_suggestions']}")
    print(f"  Auto-applicable: {report['auto_applicable']}")
    print(f"  High confidence: {report['high_confidence']}")
    
    print("\nSuggestions by Category:")
    for category, count in report['categories'].items():
        print(f"  {category}: {count}")
    
    print("\nSuggestions by Priority:")
    for priority, count in report['priorities'].items():
        print(f"  {priority}: {count}")
    
    # Start continuous mode for testing
    print("\n🚀 Starting continuous improvement (Ctrl+C to stop)...")
    system.start_continuous_improvement()
    
    try:
        while True:
            time.sleep(30)
            dashboard = system.get_dashboard_data()
            print(f"\nDashboard Update: {dashboard['recent_suggestions']} suggestions, "
                  f"{dashboard['critical_issues']} critical issues")
    except KeyboardInterrupt:
        print("\n🛑 Stopping continuous improvement...")
        system.stop_continuous_improvement()

if __name__ == "__main__":
    main()