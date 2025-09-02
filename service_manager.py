"""
Enhanced Service Manager for ULTRON Agent 3.0
Manages all services, connections, and ensures proper startup coordination
"""

import asyncio
import logging
import requests
import subprocess
import time
import psutil
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    description: str
    command: Optional[str] = None
    port: Optional[int] = None
    health_check_url: Optional[str] = None
    required: bool = True
    startup_delay: float = 0
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass 
class ServiceStatus:
    """Status information for a service"""
    name: str
    running: bool = False
    pid: Optional[int] = None
    port: Optional[int] = None
    health_ok: bool = False
    last_checked: Optional[datetime] = None
    error_message: Optional[str] = None
    startup_time: Optional[datetime] = None
    
class UltronServiceManager:
    """
    Comprehensive service management for ULTRON Agent 3.0
    Handles service startup, monitoring, health checks, and connection management
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "ultron_config.json"
        self.services: Dict[str, ServiceConfig] = {}
        self.statuses: Dict[str, ServiceStatus] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.startup_log: List[str] = []
        
        # Load configuration
        self._load_config()
        self._setup_default_services()
        
    def _load_config(self):
        """Load configuration from file"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
                logger.warning(f"Config file {self.config_path} not found, using defaults")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {}
            
    def _setup_default_services(self):
        """Setup default service configurations"""
        
        # Ollama Service - Critical for AI functionality
        self.services["ollama"] = ServiceConfig(
            name="ollama",
            description="Ollama AI Model Server",
            command="ollama serve",
            port=11434,
            health_check_url="http://localhost:11434/api/tags",
            required=True,
            startup_delay=2.0
        )
        
        # Web GUI Server
        self.services["web_gui"] = ServiceConfig(
            name="web_gui", 
            description="ULTRON Web GUI Server",
            command="python web_gui_server.py",
            port=8080,
            health_check_url="http://localhost:8080/",
            required=False,
            startup_delay=1.0,
            dependencies=["ollama"]
        )
        
        # Agent Core
        self.services["agent_core"] = ServiceConfig(
            name="agent_core",
            description="ULTRON Agent Core System", 
            command="python main.py --headless",
            required=True,
            startup_delay=0.5,
            dependencies=["ollama"]
        )
        
        # Monitoring Dashboard
        self.services["monitoring"] = ServiceConfig(
            name="monitoring",
            description="System Monitoring Dashboard",
            command="python monitoring_dashboard.py",
            port=9000,
            health_check_url="http://localhost:9000/",
            required=False,
            startup_delay=3.0
        )
        
        # Initialize statuses
        for service_name in self.services:
            self.statuses[service_name] = ServiceStatus(name=service_name)

    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        if service_name not in self.services:
            return False
            
        service = self.services[service_name]
        status = self.statuses[service_name]
        
        # Check if process is running
        if service.port:
            status.running = self._is_port_in_use(service.port)
        
        # Health check via HTTP if URL provided
        if service.health_check_url:
            try:
                response = requests.get(service.health_check_url, timeout=5)
                status.health_ok = response.status_code == 200
            except Exception as e:
                status.health_ok = False
                status.error_message = str(e)
        else:
            # Assume healthy if running
            status.health_ok = status.running
            
        status.last_checked = datetime.now()
        return status.health_ok

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return True
            return False
        except Exception:
            return False

    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        service = self.services[service_name]
        status = self.statuses[service_name]
        
        # Check dependencies first
        for dep in service.dependencies:
            if not self.check_service_health(dep):
                logger.error(f"Dependency {dep} not running for service {service_name}")
                return False
        
        # Check if already running
        if self.check_service_health(service_name):
            logger.info(f"Service {service_name} already running")
            return True
            
        # Start the service
        if service.command:
            try:
                logger.info(f"Starting service: {service_name}")
                
                # Special handling for Ollama
                if service_name == "ollama":
                    return self._start_ollama_service()
                
                # Standard service startup
                process = subprocess.Popen(
                    service.command.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=Path.cwd()
                )
                
                status.pid = process.pid
                status.startup_time = datetime.now()
                
                # Wait for startup delay
                time.sleep(service.startup_delay)
                
                # Verify service started
                if self.check_service_health(service_name):
                    logger.info(f"✅ Service {service_name} started successfully")
                    self.startup_log.append(f"✅ {service_name}: Started successfully")
                    return True
                else:
                    logger.error(f"❌ Service {service_name} failed to start properly")
                    self.startup_log.append(f"❌ {service_name}: Failed to start")
                    return False
                    
            except Exception as e:
                logger.error(f"Error starting service {service_name}: {e}")
                status.error_message = str(e)
                self.startup_log.append(f"❌ {service_name}: Error - {e}")
                return False
        else:
            logger.warning(f"No command specified for service {service_name}")
            return False

    def _start_ollama_service(self) -> bool:
        """Special handling for Ollama service startup"""
        try:
            # Check if Ollama is already running
            if self._is_port_in_use(11434):
                logger.info("Ollama already running on port 11434")
                self.startup_log.append("✅ Ollama: Already running")
                return True
            
            # Try to start Ollama
            logger.info("Starting Ollama service...")
            
            # On Windows, try ollama serve
            # On Linux, might need systemctl or direct command
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Ollama to start
            for attempt in range(30):  # 30 seconds timeout
                if self._is_port_in_use(11434):
                    logger.info("✅ Ollama service started successfully")
                    self.startup_log.append("✅ Ollama: Started successfully")
                    return True
                time.sleep(1)
                
            logger.error("❌ Ollama failed to start within timeout")
            self.startup_log.append("❌ Ollama: Timeout during startup")
            return False
            
        except FileNotFoundError:
            logger.error("❌ Ollama not found. Please install Ollama first.")
            self.startup_log.append("❌ Ollama: Not installed")
            return False
        except Exception as e:
            logger.error(f"❌ Error starting Ollama: {e}")
            self.startup_log.append(f"❌ Ollama: Error - {e}")
            return False

    def start_all_services(self) -> Dict[str, bool]:
        """Start all services in dependency order"""
        logger.info("🚀 Starting all ULTRON services...")
        self.startup_log.clear()
        self.startup_log.append(f"🚀 ULTRON Service Startup - {datetime.now()}")
        
        results = {}
        
        # Build dependency graph and start in correct order
        started = set()
        max_attempts = len(self.services) * 2  # Prevent infinite loops
        attempt = 0
        
        while len(started) < len(self.services) and attempt < max_attempts:
            attempt += 1
            made_progress = False
            
            for service_name, service in self.services.items():
                if service_name in started:
                    continue
                    
                # Check if all dependencies are started
                deps_ready = all(dep in started for dep in service.dependencies)
                
                if deps_ready:
                    success = self.start_service(service_name)
                    results[service_name] = success
                    if success:
                        started.add(service_name)
                        made_progress = True
                    elif service.required:
                        logger.error(f"Required service {service_name} failed to start")
                        break
            
            if not made_progress:
                logger.warning("No progress made in service startup, breaking loop")
                break
                
        # Start monitoring
        self.start_monitoring()
        
        return results

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.statuses:
            return False
            
        status = self.statuses[service_name]
        
        if status.pid:
            try:
                process = psutil.Process(status.pid)
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"Service {service_name} stopped")
                status.pid = None
                status.running = False
                return True
            except Exception as e:
                logger.error(f"Error stopping service {service_name}: {e}")
                return False
        return True

    def stop_all_services(self):
        """Stop all services"""
        logger.info("🛑 Stopping all ULTRON services...")
        self.monitoring_active = False
        
        for service_name in reversed(list(self.services.keys())):
            self.stop_service(service_name)

    def start_monitoring(self):
        """Start service monitoring in background thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_services, daemon=True)
        self.monitoring_thread.start()
        logger.info("📊 Service monitoring started")

    def _monitor_services(self):
        """Monitor services in background"""
        while self.monitoring_active:
            try:
                for service_name in self.services:
                    self.check_service_health(service_name)
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in service monitoring: {e}")
                time.sleep(5)

    def get_service_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "services": {},
            "startup_log": self.startup_log.copy()
        }
        
        unhealthy_count = 0
        
        for service_name, service in self.services.items():
            status = self.statuses[service_name]
            self.check_service_health(service_name)  # Fresh check
            
            service_info = {
                "name": service_name,
                "description": service.description,
                "required": service.required,
                "running": status.running,
                "healthy": status.health_ok,
                "port": service.port,
                "pid": status.pid,
                "last_checked": status.last_checked.isoformat() if status.last_checked else None,
                "error": status.error_message,
                "startup_time": status.startup_time.isoformat() if status.startup_time else None
            }
            
            report["services"][service_name] = service_info
            
            if service.required and not status.health_ok:
                unhealthy_count += 1
                
        if unhealthy_count > 0:
            report["overall_health"] = "degraded" if unhealthy_count == 1 else "critical"
            
        return report

    def fix_connection_issues(self) -> List[str]:
        """Attempt to fix common connection issues"""
        fixes_applied = []
        
        # Fix Ollama connection issues
        if not self.check_service_health("ollama"):
            logger.info("Attempting to fix Ollama connection...")
            
            # Try restarting Ollama
            self.stop_service("ollama")
            time.sleep(2)
            if self.start_service("ollama"):
                fixes_applied.append("Restarted Ollama service")
            
            # Update configuration files with correct URL
            self._fix_ollama_urls()
            fixes_applied.append("Updated Ollama URLs in configuration files")
        
        # Fix port conflicts
        port_conflicts = self._detect_port_conflicts()
        if port_conflicts:
            fixes_applied.append(f"Detected port conflicts: {port_conflicts}")
            
        return fixes_applied

    def _fix_ollama_urls(self):
        """Fix Ollama URL configurations in various files"""
        correct_url = "http://localhost:11434"
        
        # Files that might have incorrect Ollama URLs
        files_to_fix = [
            "ultron.js",
            "index.html", 
            "web_gui/index.html",
            "ultron_config.json"
        ]
        
        for file_path in files_to_fix:
            try:
                path = Path(file_path)
                if path.exists():
                    content = path.read_text()
                    
                    # Replace common incorrect URLs
                    incorrect_patterns = [
                        "http://localhost:11435",
                        "http://127.0.0.1:11435", 
                        "https://localhost:11434",
                        "ollama_url: null"
                    ]
                    
                    modified = False
                    for pattern in incorrect_patterns:
                        if pattern in content:
                            content = content.replace(pattern, correct_url)
                            modified = True
                            
                    if modified:
                        path.write_text(content)
                        logger.info(f"Fixed Ollama URLs in {file_path}")
                        
            except Exception as e:
                logger.error(f"Error fixing URLs in {file_path}: {e}")

    def _detect_port_conflicts(self) -> List[str]:
        """Detect services that might be conflicting on ports"""
        conflicts = []
        
        for service_name, service in self.services.items():
            if service.port and self._is_port_in_use(service.port):
                status = self.statuses[service_name]
                if not status.health_ok:
                    conflicts.append(f"{service_name} (port {service.port})")
                    
        return conflicts

    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get detailed diagnostic information"""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "network_connections": [],
            "processes": [],
            "services": self.get_service_status_report()["services"]
        }
        
        # Get network connections on relevant ports
        relevant_ports = [service.port for service in self.services.values() if service.port]
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port in relevant_ports:
                    diagnostics["network_connections"].append({
                        "port": conn.laddr.port,
                        "status": conn.status,
                        "pid": conn.pid
                    })
        except Exception as e:
            logger.error(f"Error getting network connections: {e}")
        
        # Get relevant processes
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any(keyword in ' '.join(proc.info['cmdline'] or []) for keyword in 
                          ['ollama', 'ultron', 'python']):
                        diagnostics["processes"].append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'], 
                            "cmdline": proc.info['cmdline']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
            
        return diagnostics

# Global service manager instance
_service_manager = None

def get_service_manager() -> UltronServiceManager:
    """Get the global service manager instance"""
    global _service_manager
    if _service_manager is None:
        _service_manager = UltronServiceManager()
    return _service_manager

def main():
    """Main function for testing service manager"""
    logging.basicConfig(level=logging.INFO)
    
    manager = UltronServiceManager()
    
    print("🚀 ULTRON Service Manager Test")
    print("=" * 50)
    
    # Start all services
    results = manager.start_all_services()
    
    print("\nStartup Results:")
    for service, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {service}")
    
    # Get status report
    time.sleep(5)
    report = manager.get_service_status_report()
    
    print(f"\nOverall Health: {report['overall_health']}")
    print("\nService Status:")
    for name, info in report["services"].items():
        health = "🟢" if info["healthy"] else "🔴"
        print(f"  {health} {name}: {info['description']}")
        if info["port"]:
            print(f"    Port: {info['port']}")
        if info["error"]:
            print(f"    Error: {info['error']}")
    
    print("\nStartup Log:")
    for log_entry in report["startup_log"]:
        print(f"  {log_entry}")

if __name__ == "__main__":
    main()