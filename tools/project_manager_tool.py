#!/usr/bin/env python3
"""Project Manager Tool for ULTRON Agent"""

from tools.tool_interface import ToolInterface
from ultron_project_manager import UltronProjectManager
from utils.ultron_logger import log_info, log_error

class ProjectManagerTool(ToolInterface):
    """AI Project Manager integration tool"""

    @property
    def name(self) -> str:
        return "Project Manager Tool"

    @property
    def description(self) -> str:
        return "AI-powered project management and health monitoring"

    def match(self, command: str) -> bool:
        keywords = ["project", "manage", "health", "status", "monitor", "assess", "fix"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            cmd_lower = command.lower()
            manager = UltronProjectManager()
            
            if "start" in cmd_lower or "manage" in cmd_lower:
                return self._start_management(manager)
            elif "health" in cmd_lower or "assess" in cmd_lower:
                return self._check_health(manager)
            elif "report" in cmd_lower:
                return self._generate_report(manager)
            elif "fix" in cmd_lower:
                return self._auto_fix(manager)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("project_manager_tool", f"Error: {e}")
            return f"Project manager error: {e}"

    def _start_management(self, manager):
        """Start autonomous project management"""
        result = manager.start_management()
        
        return f"🤖 ULTRON Project Manager Started\n" + \
               f"Status: {result['status']}\n" + \
               f"Actions Executed: {result['actions_taken']}\n" + \
               f"Assessment: {result['assessment']['ai_assessment'][:100]}..."

    def _check_health(self, manager):
        """Check project health"""
        assessment = manager.assess_project_health()
        health_score = manager.calculate_health_score(assessment)
        
        files_ok = sum(1 for f, data in assessment["raw_data"]["files"].items() if data["exists"])
        services_up = sum(1 for s, data in assessment["raw_data"]["services"].items() 
                         if data.get("status") in ["running", "active"])
        
        return f"📊 ULTRON Project Health Report\n" + \
               f"Health Score: {health_score}/100\n" + \
               f"Critical Files: {files_ok}/7 OK\n" + \
               f"Services Running: {services_up}/4\n" + \
               f"AI Assessment: {assessment['ai_assessment'][:150]}..."

    def _generate_report(self, manager):
        """Generate detailed report"""
        report = manager.generate_report()
        
        return f"📋 Project Management Report Generated\n" + \
               f"Health Score: {report['health_score']}/100\n" + \
               f"Status: {report['project_status']}\n" + \
               f"Recommendations: {report['recommendations'][:100]}...\n" + \
               f"Report saved to: logs/project_management_report.json"

    def _auto_fix(self, manager):
        """Auto-fix project issues"""
        assessment = manager.assess_project_health()
        actions = manager.plan_actions(assessment)
        results = manager.execute_actions(actions)
        
        successful_actions = sum(1 for action, result in results.items() 
                               if result.get("status") not in ["error", "unknown_action"])
        
        return f"🔧 Auto-Fix Completed\n" + \
               f"Actions Planned: {len(actions)}\n" + \
               f"Successful: {successful_actions}\n" + \
               f"Actions: {', '.join(actions)}\n" + \
               f"Results: {len(results)} operations completed"

    def _show_help(self):
        """Show project manager help"""
        return """🤖 ULTRON Project Manager Commands:

🚀 Management:
• "start project management" - Begin autonomous management
• "project health check" - Assess current project status
• "generate project report" - Create detailed health report
• "auto fix project" - Automatically resolve issues

📊 Monitoring:
• Real-time health assessment
• AI-powered issue detection
• Automated problem resolution
• Performance optimization

🔧 Capabilities:
• Service monitoring (Ollama, Web GUI, APIs)
• File integrity checking
• Dependency management
• Backup creation
• Log cleanup
• Performance monitoring

💡 Example Usage:
• "Hey ULTRON, check project health"
• "Start managing the project automatically"
• "Generate a project status report"
• "Fix any project issues automatically"
"""

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "project_manager_tool",
            "description": "AI-powered project management and health monitoring",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Project management command to execute"
                    }
                },
                "required": ["command"]
            }
        }