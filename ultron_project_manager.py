#!/usr/bin/env python3
"""ULTRON Project Manager AI - Autonomous project management system"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from utils.ultron_logger import log_info, log_error, log_ai_decision

class UltronProjectManager:
    """AI-powered project manager for ULTRON Agent"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ollama_url = "http://localhost:11434"
        self.ai_model = "llava:7b"
        self.bedrock_api_key = "ABSKQmVkcm9ja0FQSUtleS05MWhyLWF0LTk0MTI4NDAxOTAxNTo3L1lVOXY2TkZYUUpUdVByb3Y1MGNMdy9rby9IbVlYSW55dVF1MzlqejJIQWhxNHlSTnEwbW1LUGNjQT0="
        self.status = "INITIALIZING"
        
    def start_management(self):
        """Start autonomous project management"""
        log_info("project_manager", "Starting ULTRON Project Manager AI")
        self.status = "ACTIVE"
        
        # Initial project assessment
        assessment = self.assess_project_health()
        log_ai_decision("project_manager", f"Project assessment: {assessment}", ai_model=self.ai_model)
        
        # Execute management cycle
        actions = self.plan_actions(assessment)
        results = self.execute_actions(actions)
        
        return {
            "status": self.status,
            "assessment": assessment,
            "actions_taken": len(actions),
            "results": results
        }
    
    def assess_project_health(self):
        """AI assessment of project health"""
        
        health_data = {
            "files": self.check_critical_files(),
            "services": self.check_services(),
            "dependencies": self.check_dependencies(),
            "git_status": self.check_git_status(),
            "performance": self.check_performance()
        }
        
        # AI analysis
        prompt = f"""
        Analyze ULTRON Agent project health:
        
        Files: {health_data['files']}
        Services: {health_data['services']}
        Dependencies: {health_data['dependencies']}
        Git: {health_data['git_status']}
        Performance: {health_data['performance']}
        
        Provide assessment: EXCELLENT/GOOD/FAIR/POOR and top 3 issues.
        """
        
        ai_response = self.query_ai(prompt)
        
        return {
            "raw_data": health_data,
            "ai_assessment": ai_response,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_critical_files(self):
        """Check critical project files"""
        critical_files = [
            "main.py", "agent_core.py", "brain.py", "ultron_config.json",
            "requirements.txt", "README.md", "Dockerfile"
        ]
        
        status = {}
        for file in critical_files:
            file_path = self.project_root / file
            if file_path.exists():
                status[file] = {"exists": True, "size": file_path.stat().st_size}
            else:
                status[file] = {"exists": False, "size": 0}
        
        return status
    
    def check_services(self):
        """Check running services"""
        services = {
            "ollama": self.check_ollama(),
            "web_gui": self.check_port(8080),
            "api_server": self.check_port(5000),
            "avatar_game": self.check_port(8081)
        }
        return services
    
    def check_ollama(self):
        """Check Ollama service"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {"status": "running", "models": len(models)}
            return {"status": "error", "code": response.status_code}
        except:
            return {"status": "offline"}
    
    def check_port(self, port):
        """Check if port is active"""
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            return {"status": "active", "code": response.status_code}
        except:
            return {"status": "inactive"}
    
    def check_dependencies(self):
        """Check Python dependencies"""
        try:
            result = subprocess.run(["pip", "list"], capture_output=True, text=True)
            packages = len(result.stdout.split('\n')) - 2  # Exclude header
            return {"status": "ok", "packages": packages}
        except:
            return {"status": "error"}
    
    def check_git_status(self):
        """Check Git repository status"""
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            changes = len(result.stdout.split('\n')) - 1
            return {"status": "ok", "uncommitted_changes": changes}
        except:
            return {"status": "no_git"}
    
    def check_performance(self):
        """Check system performance"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('.').percent
            }
        except:
            return {"status": "unavailable"}
    
    def plan_actions(self, assessment):
        """AI-powered action planning"""
        
        prompt = f"""
        Based on ULTRON project assessment: {assessment['ai_assessment']}
        
        Plan 3-5 specific actions to improve project health.
        Format as JSON array: ["action1", "action2", "action3"]
        
        Available actions:
        - restart_ollama
        - update_dependencies  
        - run_tests
        - backup_project
        - optimize_performance
        - fix_config
        - start_services
        - clean_logs
        """
        
        ai_response = self.query_ai(prompt)
        
        try:
            # Extract JSON from AI response
            import re
            json_match = re.search(r'\[.*\]', ai_response)
            if json_match:
                actions = json.loads(json_match.group())
                return actions[:5]  # Limit to 5 actions
        except:
            pass
        
        # Fallback actions
        return ["run_tests", "start_services", "backup_project"]
    
    def execute_actions(self, actions):
        """Execute planned actions"""
        results = {}
        
        for action in actions:
            log_ai_decision("project_manager", f"Executing action: {action}", ai_model=self.ai_model)
            
            try:
                if action == "restart_ollama":
                    results[action] = self.restart_ollama()
                elif action == "update_dependencies":
                    results[action] = self.update_dependencies()
                elif action == "run_tests":
                    results[action] = self.run_tests()
                elif action == "backup_project":
                    results[action] = self.backup_project()
                elif action == "start_services":
                    results[action] = self.start_services()
                elif action == "clean_logs":
                    results[action] = self.clean_logs()
                else:
                    results[action] = {"status": "unknown_action"}
                    
            except Exception as e:
                results[action] = {"status": "error", "message": str(e)}
                log_error("project_manager", f"Action {action} failed: {e}")
        
        return results
    
    def restart_ollama(self):
        """Restart Ollama service"""
        try:
            subprocess.run(["taskkill", "/f", "/im", "ollama.exe"], 
                         capture_output=True, check=False)
            subprocess.Popen(["ollama", "serve"])
            return {"status": "restarted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def update_dependencies(self):
        """Update Python dependencies"""
        try:
            result = subprocess.run(["pip", "install", "-r", "requirements.txt", "--upgrade"],
                                  capture_output=True, text=True)
            return {"status": "updated", "output": result.stdout[:100]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def run_tests(self):
        """Run project tests"""
        try:
            # Test Ollama connectivity
            ollama_test = self.check_ollama()
            
            # Test file integrity
            files_test = self.check_critical_files()
            missing_files = [f for f, data in files_test.items() if not data["exists"]]
            
            return {
                "status": "completed",
                "ollama": ollama_test["status"],
                "missing_files": len(missing_files),
                "files_ok": len(files_test) - len(missing_files)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def backup_project(self):
        """Create project backup"""
        try:
            backup_dir = Path.home() / "ultron_backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ultron_backup_{timestamp}.zip"
            
            # Simple file copy backup
            import shutil
            backup_path = backup_dir / backup_name
            shutil.make_archive(str(backup_path)[:-4], 'zip', self.project_root)
            
            return {"status": "created", "path": str(backup_path), "size": backup_path.stat().st_size}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def start_services(self):
        """Start ULTRON services"""
        services_started = []
        
        try:
            # Start web GUI if not running
            if self.check_port(8080)["status"] == "inactive":
                subprocess.Popen(["python", "web_gui_server.py"], cwd=self.project_root)
                services_started.append("web_gui")
            
            # Start avatar game if not running
            if self.check_port(8081)["status"] == "inactive":
                subprocess.Popen(["python", "avatar_control_api.py"], cwd=self.project_root)
                services_started.append("avatar_game")
            
            return {"status": "started", "services": services_started}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clean_logs(self):
        """Clean old log files"""
        try:
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                cleaned = 0
                
                for log_file in log_files:
                    if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                        log_file.unlink()
                        cleaned += 1
                
                return {"status": "cleaned", "files_removed": cleaned}
            return {"status": "no_logs_dir"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query_ai(self, prompt):
        """Query AI model for decision making"""
        # Try Ollama first
        try:
            payload = {
                "model": self.ai_model,
                "prompt": f"You are ULTRON Project Manager AI. {prompt}",
                "stream": False
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response")
        except Exception as e:
            log_error("project_manager", f"Ollama query error: {e}")
        
        # Fallback to Bedrock if Ollama fails
        try:
            import boto3
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            bedrock_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "messages": [
                    {"role": "user", "content": f"You are ULTRON Project Manager AI. {prompt}"}
                ]
            }
            
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(bedrock_payload)
            )
            
            result = json.loads(response['body'].read())
            return result.get('content', [{}])[0].get('text', 'Bedrock unavailable')
            
        except Exception as e:
            log_error("project_manager", f"Bedrock query error: {e}")
            return "AI unavailable - using fallback logic"
    
    def generate_report(self):
        """Generate management report"""
        assessment = self.assess_project_health()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_status": self.status,
            "health_score": self.calculate_health_score(assessment),
            "recommendations": self.get_recommendations(assessment),
            "next_check": (datetime.now().timestamp() + 3600)  # 1 hour
        }
        
        # Save report
        report_file = self.project_root / "logs" / "project_management_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def calculate_health_score(self, assessment):
        """Calculate project health score (0-100)"""
        score = 100
        
        # Deduct points for issues
        files_data = assessment["raw_data"]["files"]
        missing_files = sum(1 for f, data in files_data.items() if not data["exists"])
        score -= missing_files * 10
        
        services_data = assessment["raw_data"]["services"]
        inactive_services = sum(1 for s, data in services_data.items() if data.get("status") != "running" and data.get("status") != "active")
        score -= inactive_services * 15
        
        return max(0, score)
    
    def get_recommendations(self, assessment):
        """Get AI recommendations"""
        prompt = f"Based on assessment {assessment['ai_assessment']}, provide 3 specific recommendations for ULTRON project improvement."
        return self.query_ai(prompt)

if __name__ == "__main__":
    manager = UltronProjectManager()
    result = manager.start_management()
    report = manager.generate_report()
    
    print("=== ULTRON PROJECT MANAGER AI ===")
    print(f"Status: {result['status']}")
    print(f"Actions Taken: {result['actions_taken']}")
    print(f"Health Score: {report['health_score']}/100")
    print(f"Report saved to: logs/project_management_report.json")