#!/usr/bin/env python3
"""Proactive task management for autonomous operation"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from utils.ultron_logger import log_info, log_ai_decision

class ProactiveManager:
    """Manages proactive tasks and autonomous operations"""
    
    def __init__(self):
        self.active_tasks = []
        self.completed_tasks = []
        self.task_patterns = []
        self.monitoring_enabled = True
        
    async def start_proactive_monitoring(self):
        """Start continuous proactive monitoring"""
        
        log_info("proactive_manager", "Starting proactive monitoring system")
        
        while self.monitoring_enabled:
            try:
                # Check for proactive opportunities
                opportunities = await self._identify_opportunities()
                
                for opportunity in opportunities:
                    await self._execute_proactive_task(opportunity)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                log_info("proactive_manager", f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _identify_opportunities(self) -> List[Dict[str, Any]]:
        """Identify proactive task opportunities"""
        
        opportunities = []
        
        # Check system health
        health_check = await self._check_system_health()
        if not health_check["healthy"]:
            opportunities.append({
                "type": "system_maintenance",
                "priority": "high",
                "description": "System health issues detected",
                "action": "run_diagnostics"
            })
        
        # Check for news updates
        last_news_check = await self._get_last_news_check()
        if last_news_check and (datetime.now() - last_news_check).hours > 2:
            opportunities.append({
                "type": "information_update",
                "priority": "medium", 
                "description": "AI news update needed",
                "action": "fetch_ai_news"
            })
        
        # Check for optimization opportunities
        if len(self.completed_tasks) > 10:
            opportunities.append({
                "type": "optimization",
                "priority": "low",
                "description": "Performance optimization available",
                "action": "optimize_performance"
            })
        
        return opportunities
    
    async def _execute_proactive_task(self, opportunity: Dict[str, Any]):
        """Execute a proactive task"""
        
        task_id = f"proactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        log_ai_decision("proactive_manager", 
                       f"Executing proactive task: {opportunity['description']}")
        
        task = {
            "id": task_id,
            "type": opportunity["type"],
            "description": opportunity["description"],
            "action": opportunity["action"],
            "priority": opportunity["priority"],
            "started": datetime.now().isoformat(),
            "status": "running"
        }
        
        self.active_tasks.append(task)
        
        try:
            # Execute based on action type
            if opportunity["action"] == "run_diagnostics":
                result = await self._run_system_diagnostics()
            elif opportunity["action"] == "fetch_ai_news":
                result = await self._fetch_latest_news()
            elif opportunity["action"] == "optimize_performance":
                result = await self._optimize_system_performance()
            else:
                result = {"status": "unknown_action"}
            
            # Mark as completed
            task["status"] = "completed"
            task["completed"] = datetime.now().isoformat()
            task["result"] = result
            
            self.active_tasks.remove(task)
            self.completed_tasks.append(task)
            
            log_info("proactive_manager", f"Completed proactive task: {task_id}")
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["completed"] = datetime.now().isoformat()
            
            self.active_tasks.remove(task)
            self.completed_tasks.append(task)
            
            log_info("proactive_manager", f"Failed proactive task: {task_id} - {e}")
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        
        import requests
        
        health_checks = {
            "ollama": False,
            "web_gui": False,
            "api_server": False
        }
        
        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            health_checks["ollama"] = response.status_code == 200
        except:
            pass
        
        # Check Web GUI
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            health_checks["web_gui"] = response.status_code == 200
        except:
            pass
        
        # Check API Server
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            health_checks["api_server"] = response.status_code == 200
        except:
            pass
        
        healthy = all(health_checks.values())
        
        return {
            "healthy": healthy,
            "checks": health_checks,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_last_news_check(self) -> datetime:
        """Get timestamp of last news check"""
        try:
            with open("logs/last_news_check.json", "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data["timestamp"])
        except:
            return datetime.now() - timedelta(hours=3)  # Default to 3 hours ago
    
    async def _run_system_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics"""
        
        import subprocess
        
        try:
            # Run integration test
            result = subprocess.run(["python", "test_integration.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            return {
                "status": "completed",
                "exit_code": result.returncode,
                "output": result.stdout[:500]  # Limit output
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _fetch_latest_news(self) -> Dict[str, Any]:
        """Fetch latest AI news"""
        
        import subprocess
        
        try:
            result = subprocess.run(["python", "get_ai_news.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            # Update last check timestamp
            with open("logs/last_news_check.json", "w") as f:
                json.dump({"timestamp": datetime.now().isoformat()}, f)
            
            return {
                "status": "completed",
                "articles_found": result.stdout.count("Title:") if result.stdout else 0
            }
        except Exception as e:
            return {
                "status": "failed", 
                "error": str(e)
            }
    
    async def _optimize_system_performance(self) -> Dict[str, Any]:
        """Optimize system performance"""
        
        # Clean up old logs
        import os
        import glob
        
        cleaned_files = 0
        
        try:
            # Clean old log files (older than 7 days)
            log_files = glob.glob("logs/*.log")
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for log_file in log_files:
                if os.path.getmtime(log_file) < cutoff_time.timestamp():
                    os.remove(log_file)
                    cleaned_files += 1
            
            return {
                "status": "completed",
                "cleaned_files": cleaned_files,
                "optimization": "log_cleanup"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current proactive manager status"""
        
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "recent_tasks": self.completed_tasks[-5:] if self.completed_tasks else []
        }

# Global instance
_proactive_manager = None

def get_proactive_manager() -> ProactiveManager:
    """Get singleton proactive manager instance"""
    global _proactive_manager
    if _proactive_manager is None:
        _proactive_manager = ProactiveManager()
    return _proactive_manager