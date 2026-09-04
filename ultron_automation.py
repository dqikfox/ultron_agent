#!/usr/bin/env python3
"""
ULTRON Project Automation Tool
Automated maintenance and AI-powered project management
"""

import os
import json
import subprocess
import schedule
import time
import logging
from pathlib import Path
from datetime import datetime
import requests

class UltronAutomation:
    def __init__(self):
        self.setup_logging()
        self.config = self.load_config()
        self.project_root = Path.cwd()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        try:
            with open('ultron_config.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def ai_analyze_project(self):
        """Use AI to analyze project health and suggest improvements"""
        self.logger.info("Running AI project analysis...")
        
        # Collect project metrics
        metrics = self.collect_project_metrics()
        
        # Create analysis prompt
        prompt = f"""
        Analyze this ULTRON Agent project:
        
        Metrics:
        - Python files: {metrics['py_files']}
        - Total lines: {metrics['total_lines']}
        - Git status: {metrics['git_status']}
        - Last commit: {metrics['last_commit']}
        - Dependencies: {len(metrics['dependencies'])}
        - Test files: {metrics['test_files']}
        
        Issues found:
        {metrics['issues']}
        
        Provide specific recommendations for:
        1. Code quality improvements
        2. Performance optimizations
        3. Security enhancements
        4. Maintenance tasks
        5. Feature suggestions
        """
        
        # Send to AI for analysis
        analysis = self.call_ai_for_analysis(prompt)
        
        # Save analysis
        with open('project_analysis.md', 'w') as f:
            f.write(f"# ULTRON Project Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(analysis)
        
        self.logger.info("AI analysis complete - saved to project_analysis.md")
        return analysis
    
    def collect_project_metrics(self):
        """Collect comprehensive project metrics"""
        metrics = {}
        
        # Count files
        py_files = list(self.project_root.rglob("*.py"))
        metrics['py_files'] = len(py_files)
        metrics['test_files'] = len([f for f in py_files if 'test' in f.name.lower()])
        
        # Count lines of code
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        metrics['total_lines'] = total_lines
        
        # Git status
        try:
            metrics['git_status'] = subprocess.getoutput("git status --porcelain")
            metrics['last_commit'] = subprocess.getoutput("git log -1 --format='%h %s (%cr)'")
        except:
            metrics['git_status'] = "No git"
            metrics['last_commit'] = "Unknown"
        
        # Dependencies
        try:
            with open('requirements.txt', 'r') as f:
                metrics['dependencies'] = [line.strip() for line in f if line.strip()]
        except:
            metrics['dependencies'] = []
        
        # Find potential issues
        issues = []
        
        # Check for large files
        for py_file in py_files:
            if py_file.stat().st_size > 10000:  # > 10KB
                issues.append(f"Large file: {py_file} ({py_file.stat().st_size} bytes)")
        
        # Check for TODO/FIXME comments
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'TODO' in content or 'FIXME' in content:
                        issues.append(f"TODO/FIXME found in {py_file}")
            except:
                pass
        
        metrics['issues'] = issues
        return metrics
    
    def call_ai_for_analysis(self, prompt):
        """Call AI service for project analysis"""
        try:
            # Try Claude first
            api_key = self.config.get("anthropic_api_key", "")
            if api_key:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("content", [{}])[0].get("text", "No analysis available")
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
        
        return "AI analysis unavailable - check API configuration"
    
    def auto_update_dependencies(self):
        """Automatically update project dependencies"""
        self.logger.info("Checking for dependency updates...")
        
        try:
            # Check outdated packages
            result = subprocess.run(["pip", "list", "--outdated", "--format=json"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                
                if outdated:
                    self.logger.info(f"Found {len(outdated)} outdated packages")
                    
                    # Create update report
                    with open('dependency_updates.md', 'w') as f:
                        f.write(f"# Dependency Updates - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                        for pkg in outdated:
                            f.write(f"- {pkg['name']}: {pkg['version']} → {pkg['latest_version']}\n")
                    
                    # Ask AI for update recommendations
                    update_prompt = f"Review these dependency updates for the ULTRON Agent project:\n\n"
                    for pkg in outdated:
                        update_prompt += f"- {pkg['name']}: {pkg['version']} → {pkg['latest_version']}\n"
                    update_prompt += "\nWhich updates are safe to apply? Consider compatibility and breaking changes."
                    
                    recommendations = self.call_ai_for_analysis(update_prompt)
                    
                    with open('dependency_updates.md', 'a') as f:
                        f.write(f"\n## AI Recommendations\n\n{recommendations}")
                
                else:
                    self.logger.info("All dependencies are up to date")
        
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
    
    def auto_run_tests(self):
        """Automatically run tests and generate reports"""
        self.logger.info("Running automated tests...")
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                "python3", "-m", "pytest", "tests/", "-v", 
                "--tb=short", "--cov=.", "--cov-report=html"
            ], capture_output=True, text=True)
            
            # Save test results
            with open('test_results.txt', 'w') as f:
                f.write(f"Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("=" * 50 + "\n")
                f.write(result.stdout)
                f.write(result.stderr)
            
            if result.returncode == 0:
                self.logger.info("All tests passed")
            else:
                self.logger.warning("Some tests failed - check test_results.txt")
                
                # Ask AI to analyze test failures
                if result.stderr:
                    analysis_prompt = f"Analyze these test failures and suggest fixes:\n\n{result.stderr}"
                    analysis = self.call_ai_for_analysis(analysis_prompt)
                    
                    with open('test_analysis.md', 'w') as f:
                        f.write(f"# Test Failure Analysis - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                        f.write(analysis)
        
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
    
    def auto_git_maintenance(self):
        """Automated git maintenance tasks"""
        self.logger.info("Running git maintenance...")
        
        try:
            # Check for uncommitted changes
            status = subprocess.getoutput("git status --porcelain")
            
            if status:
                self.logger.info("Found uncommitted changes")
                
                # Ask AI to review changes
                diff = subprocess.getoutput("git diff")
                if diff:
                    review_prompt = f"Review these code changes for the ULTRON Agent project:\n\n{diff[:2000]}..."
                    review = self.call_ai_for_analysis(review_prompt)
                    
                    with open('code_review.md', 'w') as f:
                        f.write(f"# Code Review - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                        f.write(review)
            
            # Clean up old branches (if any)
            subprocess.run(["git", "remote", "prune", "origin"], capture_output=True)
            
        except Exception as e:
            self.logger.error(f"Git maintenance failed: {e}")
    
    def monitor_system_health(self):
        """Monitor system health and performance"""
        self.logger.info("Monitoring system health...")
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "disk_usage": self.get_disk_usage(),
            "memory_usage": self.get_memory_usage(),
            "service_status": self.check_services(),
            "api_status": self.check_apis()
        }
        
        # Save health data
        with open('system_health.json', 'w') as f:
            json.dump(health_data, f, indent=2)
        
        # Check for issues
        issues = []
        if health_data["disk_usage"] > 90:
            issues.append("High disk usage")
        if health_data["memory_usage"] > 80:
            issues.append("High memory usage")
        if not health_data["service_status"]["ollama"]:
            issues.append("Ollama service down")
        
        if issues:
            self.logger.warning(f"Health issues detected: {', '.join(issues)}")
    
    def get_disk_usage(self):
        """Get disk usage percentage"""
        try:
            result = subprocess.getoutput("df -h . | tail -1 | awk '{print $5}' | sed 's/%//'")
            return int(result)
        except:
            return 0
    
    def get_memory_usage(self):
        """Get memory usage percentage"""
        try:
            result = subprocess.getoutput("free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100.0}'")
            return int(result)
        except:
            return 0
    
    def check_services(self):
        """Check status of required services"""
        services = {}
        
        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            services["ollama"] = response.status_code == 200
        except:
            services["ollama"] = False
        
        return services
    
    def check_apis(self):
        """Check API connectivity"""
        apis = {}
        
        # Check MiniMax
        api_key = self.config.get("minimax_api_key", "")
        if api_key:
            try:
                response = requests.post(
                    "https://api.minimax.io/v1/text/chatcompletion",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": "abab6.5s-chat", "messages": [{"role": "user", "content": "test"}]},
                    timeout=5
                )
                apis["minimax"] = response.status_code in [200, 400]
            except:
                apis["minimax"] = False
        
        # Check Claude
        api_key = self.config.get("anthropic_api_key", "")
        if api_key:
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                    json={"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "test"}]},
                    timeout=5
                )
                apis["claude"] = response.status_code in [200, 400]
            except:
                apis["claude"] = False
        
        return apis
    
    def setup_automation_schedule(self):
        """Setup automated tasks schedule"""
        self.logger.info("Setting up automation schedule...")
        
        # Daily tasks
        schedule.every().day.at("09:00").do(self.ai_analyze_project)
        schedule.every().day.at("10:00").do(self.auto_update_dependencies)
        schedule.every().day.at("11:00").do(self.auto_run_tests)
        schedule.every().day.at("12:00").do(self.auto_git_maintenance)
        
        # Hourly tasks
        schedule.every().hour.do(self.monitor_system_health)
        
        self.logger.info("Automation schedule configured")
    
    def run_automation(self):
        """Run the automation loop"""
        self.setup_automation_schedule()
        
        self.logger.info("ULTRON Automation started - running scheduled tasks...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    automation = UltronAutomation()
    
    # Run immediate analysis
    automation.ai_analyze_project()
    automation.monitor_system_health()
    
    # Start automation loop
    automation.run_automation()