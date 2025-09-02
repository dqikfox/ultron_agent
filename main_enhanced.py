"""
Enhanced Main Entry Point for ULTRON Agent 3.0
Integrates all new enhancement features with the existing agent system
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Enhanced main entry point with all new features"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    print("🚀 ULTRON Agent 3.0 - Enhanced Edition")
    print("=" * 50)
    
    # Initialize enhancement manager first
    try:
        from enhancement_manager import get_enhancement_manager
        manager = get_enhancement_manager()
        
        print("🔧 Enhancement Manager initialized")
        print("   - PyAutoGUI Automation Tool")
        print("   - Service Management System")  
        print("   - Continuous Improvement System")
        print("   - Connection Configuration Fixer")
        print()
        
        # Run enhanced startup sequence
        print("🚀 Running enhanced startup sequence...")
        startup_results = manager.startup_sequence()
        
        print(f"✅ Startup completed:")
        print(f"   - Services started: {startup_results['services_started']}")
        print(f"   - Fixes applied: {startup_results['fixes_applied']}")
        print(f"   - Improvements found: {startup_results['improvements_found']}")
        print(f"   - Overall success: {'✅' if startup_results['overall_success'] else '❌'}")
        print()
        
        # Show system health
        health_report = manager.get_system_health_report()
        health_emoji = {"healthy": "🟢", "degraded": "🟡", "critical": "🔴"}.get(health_report['overall_health'], "❓")
        print(f"🔍 System Health: {health_emoji} {health_report['overall_health']}")
        
        if health_report.get('recommendations'):
            print("📋 Recommendations:")
            for rec in health_report['recommendations'][:3]:
                print(f"   - {rec}")
        print()
        
    except Exception as e:
        logger.error(f"Enhancement manager initialization failed: {e}")
        print(f"❌ Enhancement features unavailable: {e}")
        print("🔄 Falling back to standard startup...")
        print()
    
    # Continue with standard agent startup
    try:
        # Check if we should use enhanced startup
        if "--enhanced" in sys.argv or Path("start_ultron_enhanced.sh").exists():
            print("🎯 Using enhanced ULTRON mode")
            print("   Access points after startup:")
            print("   📊 Dashboard:     http://localhost:9000")
            print("   🤖 Web GUI:       http://localhost:8080") 
            print("   📡 Ollama API:    http://localhost:11434")
            print()
            
            # Enhanced mode - keep enhancement manager active
            try:
                while True:
                    import time
                    time.sleep(30)
                    
                    # Periodic health check
                    if hasattr(manager, 'get_dashboard_data'):
                        dashboard = manager.get_dashboard_data()
                        improvements = dashboard.get('improvements', {})
                        if improvements.get('critical_issues', 0) > 0:
                            logger.warning(f"⚠️  {improvements['critical_issues']} critical issues detected")
                        
            except KeyboardInterrupt:
                print("\n🛑 Shutting down enhanced ULTRON...")
                if 'manager' in locals():
                    manager.shutdown_enhancements()
                print("👋 Goodbye!")
                return 0
        else:
            # Standard mode - import and run original main
            print("🎯 Using standard ULTRON mode")
            print("   (Use --enhanced flag for enhanced features)")
            print()
            
            try:
                from main import main as original_main
                return original_main()
            except ImportError:
                logger.error("Original main.py not found, using basic startup")
                print("⚠️  Original main.py not available")
                return 1
                
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        print(f"❌ ULTRON startup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)