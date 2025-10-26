"""
ULTRON Agent 3.0 - System Health Monitor
Comprehensive system health checking and monitoring
"""

import os
import sys
import json
import psutil
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests
from .ultron_logger import log_info, log_error, log_ai_decision

class SystemHealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.last_check = None
        self.health_history = []
        
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        log_info("system_health", "Starting comprehensive system health check")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "score": 0.0,
            "checks": {}
        }
        
        # Run all health checks
        checks = [
            ("python_environment", self._check_python_environment),
            ("system_resources", self._check_system_resources),
            ("network_connectivity", self._check_network_connectivity),
            ("file_system", self._check_file_system),
            ("dependencies", self._check_dependencies),
            ("services", self._check_services),
            ("configuration", self._check_configuration),
            ("security", self._check_security)
        ]
        
        total_score = 0
        max_score = len(checks)
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                health_report["checks"][check_name] = result
                
                # Add to total score (1.0 = perfect, 0.0 = failed)
                total_score += result.get("score", 0.0)
                
                log_info("system_health", f"Health check {check_name}: {result.get('status', 'unknown')}")
                
            except Exception as e:
                log_error("system_health", f"Health check {check_name} failed: {e}")
                health_report["checks"][check_name] = {
                    "status": "error",
                    "score": 0.0,
                    "error": str(e)
                }
        
        # Calculate overall score and status
        health_report["score"] = total_score / max_score if max_score > 0 else 0.0
        
        if health_report["score"] >= 0.9:
            health_report["overall_status"] = "excellent"
        elif health_report["score"] >= 0.7:
            health_report["overall_status"] = "good"
        elif health_report["score"] >= 0.5:
            health_report["overall_status"] = "fair"
        elif health_report["score"] >= 0.3:
            health_report["overall_status"] = "poor"
        else:
            health_report["overall_status"] = "critical"
        
        # Store in history
        self.health_history.append(health_report)
        if len(self.health_history) > 100:  # Keep last 100 checks
            self.health_history.pop(0)
        
        self.last_check = datetime.now()
        
        log_info("system_health", f"System health check complete: {health_report['overall_status']} ({health_report['score']:.2f})")
        
        return health_report
    
    def _check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment health"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "python_version": sys.version,
                    "python_executable": sys.executable,
                    "platform": sys.platform,
                    "path_entries": len(sys.path)
                }
            }
            
            # Check Python version
            if sys.version_info < (3, 8):
                result["status"] = "warning"
                result["score"] = 0.5
                result["issues"] = ["Python version < 3.8"]
            
            # Check if running in virtual environment
            result["details"]["virtual_env"] = hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                }
            }
            
            # Check thresholds
            issues = []
            score_deductions = 0
            
            cpu_threshold = self.config.get("cpu_threshold", 80)
            memory_threshold = self.config.get("memory_threshold", 85)
            disk_threshold = self.config.get("disk_threshold", 90)
            
            if cpu_percent > cpu_threshold:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
                score_deductions += 0.3
            
            if memory.percent > memory_threshold:
                issues.append(f"High memory usage: {memory.percent:.1f}%")
                score_deductions += 0.3
            
            if disk.percent > disk_threshold:
                issues.append(f"High disk usage: {disk.percent:.1f}%")
                score_deductions += 0.4
            
            if issues:
                result["issues"] = issues
                result["score"] = max(0.0, 1.0 - score_deductions)
                result["status"] = "warning" if result["score"] > 0.3 else "critical"
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "tests": {}
                }
            }
            
            # Test connections
            tests = [
                ("localhost", "127.0.0.1", 80),
                ("ollama", "127.0.0.1", 11434),
                ("internet", "8.8.8.8", 53),
                ("github", "github.com", 443)
            ]
            
            failed_tests = 0
            
            for test_name, host, port in tests:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    if test_name == "github":
                        # For domain names, resolve first
                        import socket
                        host = socket.gethostbyname(host)
                    
                    result_code = sock.connect_ex((host, port))
                    sock.close()
                    
                    test_result = {
                        "host": host,
                        "port": port,
                        "success": result_code == 0
                    }
                    
                    result["details"]["tests"][test_name] = test_result
                    
                    if not test_result["success"]:
                        failed_tests += 1
                
                except Exception as e:
                    result["details"]["tests"][test_name] = {
                        "host": host,
                        "port": port,
                        "success": False,
                        "error": str(e)
                    }
                    failed_tests += 1
            
            # Calculate score based on failed tests
            if failed_tests > 0:
                result["score"] = max(0.0, 1.0 - (failed_tests * 0.25))
                result["status"] = "warning" if failed_tests <= 2 else "critical"
                result["issues"] = [f"{failed_tests} network connectivity tests failed"]
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_file_system(self) -> Dict[str, Any]:
        """Check file system health"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "directories": {},
                    "files": {}
                }
            }
            
            # Check required directories
            required_dirs = ["logs", "utils", "tools", "gui", "cache"]
            missing_dirs = []
            
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                exists = dir_path.exists()
                is_writable = exists and os.access(dir_path, os.W_OK)
                
                result["details"]["directories"][dir_name] = {
                    "exists": exists,
                    "writable": is_writable
                }
                
                if not exists:
                    missing_dirs.append(dir_name)
                elif not is_writable:
                    missing_dirs.append(f"{dir_name} (not writable)")
            
            # Check critical files
            critical_files = [
                "ultron_config.json",
                "requirements.txt",
                "main.py",
                "agent_core.py"
            ]
            
            missing_files = []
            
            for file_name in critical_files:
                file_path = Path(file_name)
                exists = file_path.exists()
                readable = exists and os.access(file_path, os.R_OK)
                
                result["details"]["files"][file_name] = {
                    "exists": exists,
                    "readable": readable,
                    "size": file_path.stat().st_size if exists else 0
                }
                
                if not exists:
                    missing_files.append(file_name)
                elif not readable:
                    missing_files.append(f"{file_name} (not readable)")
            
            # Calculate score
            issues = []
            score_deduction = 0
            
            if missing_dirs:
                issues.extend([f"Missing directory: {d}" for d in missing_dirs])
                score_deduction += len(missing_dirs) * 0.1
            
            if missing_files:
                issues.extend([f"Missing file: {f}" for f in missing_files])
                score_deduction += len(missing_files) * 0.2
            
            if issues:
                result["issues"] = issues
                result["score"] = max(0.0, 1.0 - score_deduction)
                result["status"] = "warning" if result["score"] > 0.5 else "critical"
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check Python dependencies"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "installed_packages": {},
                    "missing_packages": []
                }
            }
            
            # Core dependencies to check
            core_deps = [
                "fastapi",
                "uvicorn",
                "websockets",
                "requests",
                "psutil",
                "pathlib"
            ]
            
            missing_deps = []
            
            for dep in core_deps:
                try:
                    module = __import__(dep)
                    version = getattr(module, '__version__', 'unknown')
                    result["details"]["installed_packages"][dep] = version
                except ImportError:
                    missing_deps.append(dep)
                    result["details"]["missing_packages"].append(dep)
            
            if missing_deps:
                result["score"] = max(0.0, 1.0 - (len(missing_deps) * 0.2))
                result["status"] = "warning" if len(missing_deps) <= 2 else "critical"
                result["issues"] = [f"Missing dependencies: {', '.join(missing_deps)}"]
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_services(self) -> Dict[str, Any]:
        """Check external services"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "services": {}
                }
            }
            
            # Check Ollama service
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                ollama_status = {
                    "available": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds(),
                    "models": []
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        ollama_status["models"] = [model.get("name", "unknown") for model in data.get("models", [])]
                    except:
                        pass
                
                result["details"]["services"]["ollama"] = ollama_status
                
            except Exception as e:
                result["details"]["services"]["ollama"] = {
                    "available": False,
                    "error": str(e)
                }
            
            # Check GUI server (if running)
            try:
                response = requests.get("http://localhost:5000", timeout=3)
                result["details"]["services"]["gui"] = {
                    "available": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds()
                }
            except:
                result["details"]["services"]["gui"] = {
                    "available": False
                }
            
            # Calculate score based on service availability
            services = result["details"]["services"]
            available_services = sum(1 for s in services.values() if s.get("available", False))
            total_services = len(services)
            
            if total_services > 0:
                service_score = available_services / total_services
                if service_score < 1.0:
                    result["score"] = service_score
                    result["status"] = "warning" if service_score > 0.5 else "critical"
                    unavailable = [name for name, info in services.items() if not info.get("available", False)]
                    result["issues"] = [f"Unavailable services: {', '.join(unavailable)}"]
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "config_file": "ultron_config.json",
                    "valid": False,
                    "keys_present": [],
                    "keys_missing": []
                }
            }
            
            config_path = Path("ultron_config.json")
            
            if not config_path.exists():
                return {
                    "status": "critical",
                    "score": 0.0,
                    "error": "Configuration file not found"
                }
            
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                result["details"]["valid"] = True
                
                # Check for required keys
                required_keys = [
                    "use_voice", "use_gui", "use_api",
                    "llm_model", "ollama_base_url"
                ]
                
                for key in required_keys:
                    if key in config_data:
                        result["details"]["keys_present"].append(key)
                    else:
                        result["details"]["keys_missing"].append(key)
                
                # Calculate score based on missing keys
                if result["details"]["keys_missing"]:
                    missing_count = len(result["details"]["keys_missing"])
                    result["score"] = max(0.0, 1.0 - (missing_count * 0.2))
                    result["status"] = "warning"
                    result["issues"] = [f"Missing config keys: {', '.join(result['details']['keys_missing'])}"]
                
            except json.JSONDecodeError as e:
                result["status"] = "critical"
                result["score"] = 0.0
                result["error"] = f"Invalid JSON in config file: {e}"
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def _check_security(self) -> Dict[str, Any]:
        """Check security configuration"""
        try:
            result = {
                "status": "healthy",
                "score": 1.0,
                "details": {
                    "security_mode": False,
                    "bind_localhost": False,
                    "file_permissions": {}
                }
            }
            
            # Check configuration security settings
            try:
                with open("ultron_config.json", 'r') as f:
                    config = json.load(f)
                
                result["details"]["security_mode"] = config.get("security_mode", False)
                result["details"]["bind_localhost"] = config.get("bind_localhost_only", False)
                
                # Check for exposed API keys
                exposed_keys = []
                for key, value in config.items():
                    if "key" in key.lower() and value and value != "null" and len(str(value)) > 10:
                        exposed_keys.append(key)
                
                if exposed_keys:
                    result["details"]["exposed_api_keys"] = len(exposed_keys)
                    result["issues"] = [f"API keys found in config (ensure they're secure): {len(exposed_keys)} keys"]
                    result["score"] = 0.8  # Minor deduction for having keys in config
                
            except Exception as e:
                result["details"]["config_error"] = str(e)
            
            # Check file permissions on critical files
            critical_files = ["ultron_config.json", "main.py", "agent_core.py"]
            
            for file_name in critical_files:
                file_path = Path(file_name)
                if file_path.exists():
                    stat = file_path.stat()
                    # Check if file is world-readable (potential security issue)
                    world_readable = bool(stat.st_mode & 0o004)
                    result["details"]["file_permissions"][file_name] = {
                        "world_readable": world_readable,
                        "mode": oct(stat.st_mode)
                    }
                    
                    if world_readable and file_name == "ultron_config.json":
                        result["score"] = min(result["score"], 0.7)
                        result["status"] = "warning"
                        if "issues" not in result:
                            result["issues"] = []
                        result["issues"].append("Config file is world-readable")
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": str(e)
            }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health"""
        if not self.last_check:
            return {"status": "no_data", "message": "No health check performed yet"}
        
        latest = self.health_history[-1] if self.health_history else None
        if not latest:
            return {"status": "no_data", "message": "No health data available"}
        
        summary = {
            "overall_status": latest["overall_status"],
            "score": latest["score"],
            "last_check": latest["timestamp"],
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Extract issues and recommendations
        for check_name, check_result in latest["checks"].items():
            if check_result.get("status") == "critical":
                summary["critical_issues"].append(f"{check_name}: {check_result.get('error', 'Critical issue')}")
            elif check_result.get("status") == "warning":
                issues = check_result.get("issues", [])
                summary["warnings"].extend([f"{check_name}: {issue}" for issue in issues])
        
        # Generate recommendations
        if summary["score"] < 0.7:
            summary["recommendations"].append("System health is below optimal - consider addressing critical issues")
        
        if any("missing" in issue.lower() for issue in summary["critical_issues"]):
            summary["recommendations"].append("Install missing dependencies or create missing directories")
        
        if any("high" in warning.lower() for warning in summary["warnings"]):
            summary["recommendations"].append("Monitor system resources - consider closing unnecessary applications")
        
        return summary
    
    def get_health_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trend over time"""
        if not self.health_history:
            return {"status": "no_data", "message": "No health history available"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_checks = []
        for check in self.health_history:
            check_time = datetime.fromisoformat(check["timestamp"])
            if check_time > cutoff_time:
                recent_checks.append(check)
        
        if not recent_checks:
            return {"status": "no_data", "message": f"No health checks in the last {hours} hours"}
        
        scores = [check["score"] for check in recent_checks]
        
        trend = {
            "period_hours": hours,
            "checks_count": len(recent_checks),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "current_score": scores[-1] if scores else 0,
            "trend_direction": "stable"
        }
        
        # Determine trend direction
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / min(3, len(scores))
            older_avg = sum(scores[:-3]) / max(1, len(scores) - 3) if len(scores) > 3 else recent_avg
            
            if recent_avg > older_avg + 0.1:
                trend["trend_direction"] = "improving"
            elif recent_avg < older_avg - 0.1:
                trend["trend_direction"] = "declining"
        
        return trend

# Global health monitor instance
_health_monitor = None

def get_health_monitor(config=None) -> SystemHealthMonitor:
    """Get or create global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor(config)
    return _health_monitor

def quick_health_check() -> Dict[str, Any]:
    """Perform a quick health check"""
    monitor = get_health_monitor()
    return monitor.check_system_health()

def get_health_status() -> str:
    """Get simple health status string"""
    try:
        monitor = get_health_monitor()
        summary = monitor.get_health_summary()
        return summary.get("overall_status", "unknown")
    except Exception:
        return "error"