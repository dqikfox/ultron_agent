"""
Integration Manager for ULTRON Agent 3.0 Enhancements  
Integrates all new features: PyAutoGUI, Service Management, Continuous Improvement, Connection Fixes
"""

import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class UltronEnhancementManager:
    """
    Central manager for all ULTRON Agent 3.0 enhancements
    Coordinates PyAutoGUI automation, service management, continuous improvement, and connection fixes
    """
    
    def __init__(self, agent=None, config: Optional[Dict] = None):
        self.agent = agent
        self.config = config or {}
        
        # Component managers
        self.service_manager = None
        self.improvement_system = None
        self.connection_fixer = None
        self.pyautogui_tool = None
        
        # Status tracking
        self.initialization_status = {}
        self.last_health_check = None
        self.features_enabled = {
            "service_management": True,
            "continuous_improvement": True, 
            "connection_fixing": True,
            "pyautogui_automation": True,
            "auto_diagnostics": True
        }
        
        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all enhancement components"""
        logger.info("🚀 Initializing ULTRON Enhancement Manager...")
        
        # Initialize Service Manager
        try:
            from service_manager import get_service_manager
            self.service_manager = get_service_manager()
            self.initialization_status["service_manager"] = "✅ Ready"
            logger.info("✅ Service Manager initialized")
        except Exception as e:
            self.initialization_status["service_manager"] = f"❌ Failed: {e}"
            logger.error(f"Failed to initialize Service Manager: {e}")
        
        # Initialize Continuous Improvement System
        try:
            from continuous_improvement_system import get_improvement_system
            self.improvement_system = get_improvement_system(agent=self.agent, config=self.config)
            self.initialization_status["improvement_system"] = "✅ Ready"
            logger.info("✅ Continuous Improvement System initialized")
        except Exception as e:
            self.initialization_status["improvement_system"] = f"❌ Failed: {e}"
            logger.error(f"Failed to initialize Continuous Improvement System: {e}")
        
        # Initialize Connection Fixer
        try:
            from connection_config_fixer import ConnectionConfigurationFixer
            self.connection_fixer = ConnectionConfigurationFixer()
            self.initialization_status["connection_fixer"] = "✅ Ready" 
            logger.info("✅ Connection Configuration Fixer initialized")
        except Exception as e:
            self.initialization_status["connection_fixer"] = f"❌ Failed: {e}"
            logger.error(f"Failed to initialize Connection Fixer: {e}")
        
        # Initialize PyAutoGUI Tool
        try:
            from tools.pyautogui_automation_tool import PyAutoGUIAutomationTool
            self.pyautogui_tool = PyAutoGUIAutomationTool(agent=self.agent)
            self.initialization_status["pyautogui_tool"] = "✅ Ready"
            logger.info("✅ PyAutoGUI Automation Tool initialized")
        except Exception as e:
            self.initialization_status["pyautogui_tool"] = f"⚠️ Limited: {e}"
            logger.warning(f"PyAutoGUI Tool has limitations: {e}")

    def startup_sequence(self) -> Dict[str, Any]:
        """Execute complete ULTRON startup sequence with enhancements"""
        logger.info("🚀 Starting Enhanced ULTRON Startup Sequence...")
        
        startup_results = {
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "overall_success": True,
            "services_started": 0,
            "fixes_applied": 0,
            "improvements_found": 0
        }
        
        # Phase 1: Connection Configuration Fixes
        logger.info("📡 Phase 1: Connection Configuration Fixes")
        if self.connection_fixer and self.features_enabled["connection_fixing"]:
            try:
                fix_results = self.connection_fixer.apply_automatic_fixes()
                startup_results["phases"]["connection_fixes"] = fix_results
                startup_results["fixes_applied"] = fix_results.get("fixes_applied", 0)
                logger.info(f"✅ Applied {startup_results['fixes_applied']} connection fixes")
            except Exception as e:
                startup_results["phases"]["connection_fixes"] = {"error": str(e)}
                logger.error(f"❌ Connection fixes failed: {e}")
        
        # Phase 2: Service Management
        logger.info("🔧 Phase 2: Service Startup and Management") 
        if self.service_manager and self.features_enabled["service_management"]:
            try:
                service_results = self.service_manager.start_all_services()
                startup_results["phases"]["service_management"] = service_results
                startup_results["services_started"] = len([s for s in service_results.values() if s])
                logger.info(f"✅ Started {startup_results['services_started']} services")
            except Exception as e:
                startup_results["phases"]["service_management"] = {"error": str(e)}
                logger.error(f"❌ Service startup failed: {e}")
                startup_results["overall_success"] = False
        
        # Phase 3: Continuous Improvement Activation
        logger.info("🔄 Phase 3: Continuous Improvement System")
        if self.improvement_system and self.features_enabled["continuous_improvement"]:
            try:
                self.improvement_system.start_continuous_improvement()
                
                # Run initial analysis
                initial_report = self.improvement_system.force_analysis()
                startup_results["phases"]["continuous_improvement"] = {
                    "active": True,
                    "initial_suggestions": initial_report.get("total_suggestions", 0)
                }
                startup_results["improvements_found"] = initial_report.get("total_suggestions", 0)
                logger.info(f"✅ Found {startup_results['improvements_found']} improvement opportunities")
            except Exception as e:
                startup_results["phases"]["continuous_improvement"] = {"error": str(e)}
                logger.error(f"❌ Continuous improvement activation failed: {e}")
        
        # Phase 4: Tool Integration
        logger.info("🛠️  Phase 4: Enhanced Tool Integration")
        if self.pyautogui_tool and self.features_enabled["pyautogui_automation"]:
            try:
                # Test PyAutoGUI tool functionality
                test_result = self.pyautogui_tool.execute("get_screen_size")
                startup_results["phases"]["tool_integration"] = {
                    "pyautogui_available": "Warning" not in test_result and "Error" not in test_result,
                    "test_result": test_result
                }
                logger.info("✅ PyAutoGUI tool integration complete")
            except Exception as e:
                startup_results["phases"]["tool_integration"] = {"error": str(e)}
                logger.error(f"❌ Tool integration failed: {e}")
        
        # Phase 5: Health Check and Diagnostics
        logger.info("🔍 Phase 5: System Health Check")
        if self.features_enabled["auto_diagnostics"]:
            try:
                health_report = self.get_system_health_report()
                startup_results["phases"]["health_check"] = health_report
                startup_results["overall_success"] = health_report.get("overall_health") != "critical"
                logger.info(f"✅ System health: {health_report.get('overall_health', 'unknown')}")
            except Exception as e:
                startup_results["phases"]["health_check"] = {"error": str(e)}
                logger.error(f"❌ Health check failed: {e}")
        
        # Summary
        if startup_results["overall_success"]:
            logger.info("🎉 Enhanced ULTRON startup completed successfully!")
        else:
            logger.warning("⚠️  Enhanced ULTRON startup completed with issues")
            
        return startup_results

    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        self.last_health_check = datetime.now()
        
        health_report = {
            "timestamp": self.last_health_check.isoformat(),
            "overall_health": "healthy",
            "component_status": self.initialization_status.copy(),
            "service_health": {},
            "improvement_status": {},
            "connection_status": {},
            "recommendations": []
        }
        
        issues_count = 0
        
        # Check service health
        if self.service_manager:
            try:
                service_report = self.service_manager.get_service_status_report()
                health_report["service_health"] = service_report
                
                if service_report.get("overall_health") == "critical":
                    issues_count += 2
                elif service_report.get("overall_health") == "degraded":
                    issues_count += 1
                    
            except Exception as e:
                health_report["service_health"] = {"error": str(e)}
                issues_count += 1
        
        # Check improvement system status
        if self.improvement_system:
            try:
                improvement_report = self.improvement_system.get_dashboard_data()
                health_report["improvement_status"] = improvement_report
                
                if improvement_report.get("critical_issues", 0) > 0:
                    issues_count += improvement_report["critical_issues"]
                    
            except Exception as e:
                health_report["improvement_status"] = {"error": str(e)}
                issues_count += 1
        
        # Check connection status
        if self.connection_fixer:
            try:
                connection_diagnosis = self.connection_fixer.diagnose_connection_issues()
                health_report["connection_status"] = {
                    "ollama_issues": len(connection_diagnosis.get("ollama_issues", [])),
                    "web_gui_issues": len(connection_diagnosis.get("web_gui_issues", [])),
                    "tamagotchi_issues": len(connection_diagnosis.get("tamagotchi_issues", []))
                }
                
                total_connection_issues = sum(health_report["connection_status"].values())
                if total_connection_issues > 0:
                    issues_count += total_connection_issues
                    
            except Exception as e:
                health_report["connection_status"] = {"error": str(e)}
                issues_count += 1
        
        # Determine overall health
        if issues_count == 0:
            health_report["overall_health"] = "healthy"
        elif issues_count <= 2:
            health_report["overall_health"] = "degraded"
        else:
            health_report["overall_health"] = "critical"
        
        # Generate recommendations
        health_report["recommendations"] = self._generate_health_recommendations(health_report, issues_count)
        
        return health_report

    def _generate_health_recommendations(self, health_report: Dict[str, Any], issues_count: int) -> List[str]:
        """Generate health-based recommendations"""
        recommendations = []
        
        if issues_count == 0:
            recommendations.append("✅ All systems operating normally")
            recommendations.append("🔄 Consider running performance optimization")
            recommendations.append("📊 Review improvement suggestions for enhancements")
        
        elif issues_count <= 2:
            recommendations.append("⚠️  Some issues detected, but system is stable")
            recommendations.append("🔧 Apply automatic fixes using fix_all_issues()")
            recommendations.append("🔍 Monitor system health regularly")
        
        else:
            recommendations.append("🚨 Multiple issues detected - immediate attention needed")
            recommendations.append("🛠️  Run comprehensive diagnostic with fix_all_issues()")
            recommendations.append("📞 Consider manual intervention for critical issues")
            recommendations.append("🔄 Restart services if necessary")
        
        # Specific recommendations based on component status
        if "service_manager" in self.initialization_status and "Failed" in self.initialization_status["service_manager"]:
            recommendations.append("🔧 Service Manager initialization failed - check dependencies")
        
        if health_report.get("connection_status", {}).get("ollama_issues", 0) > 0:
            recommendations.append("📡 Ollama connection issues detected - run connection fixes")
        
        if health_report.get("service_health", {}).get("overall_health") == "critical":
            recommendations.append("⚡ Critical services down - restart all services")
            
        return recommendations

    def fix_all_issues(self) -> Dict[str, Any]:
        """Attempt to fix all detected system issues automatically"""
        logger.info("🔧 Starting comprehensive issue resolution...")
        
        fix_results = {
            "timestamp": datetime.now().isoformat(),
            "connection_fixes": {},
            "service_fixes": {},
            "improvement_fixes": {},
            "total_fixes_applied": 0,
            "remaining_issues": []
        }
        
        # Apply connection fixes
        if self.connection_fixer:
            try:
                connection_results = self.connection_fixer.apply_automatic_fixes()
                fix_results["connection_fixes"] = connection_results
                fix_results["total_fixes_applied"] += connection_results.get("fixes_applied", 0)
                logger.info(f"Applied {connection_results.get('fixes_applied', 0)} connection fixes")
            except Exception as e:
                fix_results["connection_fixes"] = {"error": str(e)}
                logger.error(f"Connection fixes failed: {e}")
        
        # Fix service issues
        if self.service_manager:
            try:
                # Attempt to restart failed services
                status_report = self.service_manager.get_service_status_report()
                failed_services = []
                
                for service_name, service_info in status_report.get("services", {}).items():
                    if service_info.get("required") and not service_info.get("healthy"):
                        failed_services.append(service_name)
                
                restarted_services = []
                for service_name in failed_services:
                    try:
                        if self.service_manager.start_service(service_name):
                            restarted_services.append(service_name)
                    except Exception as e:
                        logger.error(f"Failed to restart service {service_name}: {e}")
                
                fix_results["service_fixes"] = {
                    "failed_services": failed_services,
                    "restarted_services": restarted_services
                }
                fix_results["total_fixes_applied"] += len(restarted_services)
                logger.info(f"Restarted {len(restarted_services)} services")
                
            except Exception as e:
                fix_results["service_fixes"] = {"error": str(e)}
                logger.error(f"Service fixes failed: {e}")
        
        # Apply improvement fixes
        if self.improvement_system:
            try:
                # Force analysis and apply automatic improvements
                improvement_report = self.improvement_system.force_analysis()
                auto_applicable = improvement_report.get("auto_applicable", 0)
                
                fix_results["improvement_fixes"] = {
                    "suggestions_analyzed": improvement_report.get("total_suggestions", 0),
                    "auto_applicable": auto_applicable
                }
                
                logger.info(f"Analyzed {improvement_report.get('total_suggestions', 0)} improvement suggestions")
                
            except Exception as e:
                fix_results["improvement_fixes"] = {"error": str(e)}
                logger.error(f"Improvement fixes failed: {e}")
        
        # Final health check
        try:
            final_health = self.get_system_health_report()
            fix_results["final_health"] = final_health.get("overall_health")
            
            # Identify remaining issues
            if final_health.get("overall_health") != "healthy":
                fix_results["remaining_issues"] = final_health.get("recommendations", [])
                
        except Exception as e:
            fix_results["remaining_issues"] = [f"Health check failed: {e}"]
        
        logger.info(f"🎯 Issue resolution complete: {fix_results['total_fixes_applied']} fixes applied")
        return fix_results

    def get_enhancement_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for all enhancements"""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "system_status": self.initialization_status,
            "features_enabled": self.features_enabled,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }
        
        # Service management dashboard
        if self.service_manager:
            try:
                service_report = self.service_manager.get_service_status_report()
                dashboard["services"] = {
                    "overall_health": service_report.get("overall_health"),
                    "services_count": len(service_report.get("services", {})),
                    "healthy_services": len([s for s in service_report.get("services", {}).values() if s.get("healthy")]),
                    "startup_log": service_report.get("startup_log", [])[-5:]  # Last 5 entries
                }
            except Exception as e:
                dashboard["services"] = {"error": str(e)}
        
        # Continuous improvement dashboard
        if self.improvement_system:
            try:
                improvement_dashboard = self.improvement_system.get_dashboard_data()
                dashboard["improvements"] = improvement_dashboard
            except Exception as e:
                dashboard["improvements"] = {"error": str(e)}
        
        # PyAutoGUI tool status
        if self.pyautogui_tool:
            try:
                test_result = self.pyautogui_tool.execute("get_screen_size")
                dashboard["automation"] = {
                    "pyautogui_available": "Error" not in test_result and "Warning" not in test_result,
                    "last_test_result": test_result,
                    "actions_available": len(self.pyautogui_tool.parameters["properties"]["action"]["enum"])
                }
            except Exception as e:
                dashboard["automation"] = {"error": str(e)}
        
        return dashboard

    def shutdown_enhancements(self):
        """Gracefully shutdown all enhancement systems"""
        logger.info("🛑 Shutting down ULTRON enhancements...")
        
        # Stop continuous improvement
        if self.improvement_system:
            try:
                self.improvement_system.stop_continuous_improvement()
                logger.info("✅ Continuous improvement stopped")
            except Exception as e:
                logger.error(f"Error stopping continuous improvement: {e}")
        
        # Stop service monitoring  
        if self.service_manager:
            try:
                self.service_manager.stop_all_services()
                logger.info("✅ Services stopped")
            except Exception as e:
                logger.error(f"Error stopping services: {e}")
        
        logger.info("🏁 ULTRON enhancement shutdown complete")

# Global enhancement manager instance
_enhancement_manager = None

def get_enhancement_manager(agent=None, config=None) -> UltronEnhancementManager:
    """Get the global enhancement manager instance"""
    global _enhancement_manager
    if _enhancement_manager is None:
        _enhancement_manager = UltronEnhancementManager(agent=agent, config=config)
    return _enhancement_manager

def main():
    """Test the enhancement manager"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    manager = UltronEnhancementManager()
    
    print("🚀 ULTRON Enhancement Manager Test")
    print("=" * 50)
    
    # Show initialization status
    print("Initialization Status:")
    for component, status in manager.initialization_status.items():
        print(f"  {component}: {status}")
    
    # Run startup sequence
    print("\n🚀 Running startup sequence...")
    startup_results = manager.startup_sequence()
    
    print(f"\nStartup Results:")
    print(f"  Overall Success: {'✅' if startup_results['overall_success'] else '❌'}")
    print(f"  Services Started: {startup_results['services_started']}")
    print(f"  Fixes Applied: {startup_results['fixes_applied']}")
    print(f"  Improvements Found: {startup_results['improvements_found']}")
    
    # Show dashboard
    print("\n📊 Enhancement Dashboard:")
    dashboard = manager.get_enhancement_dashboard()
    
    if "services" in dashboard:
        services = dashboard["services"] 
        if "error" not in services:
            print(f"  Services: {services.get('healthy_services', 0)}/{services.get('services_count', 0)} healthy")
    
    if "improvements" in dashboard:
        improvements = dashboard["improvements"]
        if "error" not in improvements:
            print(f"  Improvements: {improvements.get('recent_suggestions', 0)} recent suggestions")
    
    if "automation" in dashboard:
        automation = dashboard["automation"]
        if "error" not in automation:
            available = "✅" if automation.get("pyautogui_available") else "⚠️ "
            print(f"  Automation: {available} PyAutoGUI ({automation.get('actions_available', 0)} actions)")
    
    print("\n🔍 System Health Check:")
    health_report = manager.get_system_health_report()
    print(f"  Overall Health: {health_report['overall_health']}")
    
    if health_report.get("recommendations"):
        print("  Recommendations:")
        for rec in health_report["recommendations"][:3]:  # Show top 3
            print(f"    - {rec}")

if __name__ == "__main__":
    main()