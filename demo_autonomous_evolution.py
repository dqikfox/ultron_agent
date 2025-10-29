#!/usr/bin/env python3
"""
Autonomous Evolution Tool - Demo Script

This script demonstrates the autonomous evolution system capabilities
without requiring the full ULTRON agent setup.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.autonomous_evolution_tool import AutonomousEvolutionTool


class MockBrain:
    """Mock brain for demonstration"""
    
    async def plan(self, prompt: str) -> str:
        """Mock planning response"""
        if "performance" in prompt.lower():
            return """
            1. Implement connection pooling for Ollama API to reduce overhead
            2. Add caching layer for frequently requested AI responses
            3. Optimize async operations in brain.py by using asyncio.gather()
            """
        elif "security" in prompt.lower():
            return """
            1. Add input validation for all user commands before processing
            2. Implement rate limiting on API endpoints to prevent abuse
            3. Enhance secret management with environment variable validation
            """
        elif "testing" in prompt.lower():
            return """
            1. Add integration tests for tool discovery system
            2. Implement edge case tests for voice recognition
            3. Add performance tests for async operations
            """
        else:
            return """
            1. Improve error handling in critical code paths
            2. Add comprehensive logging to track system behavior
            3. Enhance documentation with usage examples
            """


class MockConfig:
    """Mock configuration"""
    
    def __init__(self):
        self.llm_model = "llava:7b"
        self.autonomous_evolution = {
            "enabled": True,
            "cycle_interval": 5,  # 5 seconds for demo
            "max_improvements_per_cycle": 3,
            "safety_mode": True
        }


async def demo_basic_operations():
    """Demonstrate basic autonomous evolution operations"""
    print("=" * 60)
    print("ULTRON Autonomous Evolution Tool - Demo")
    print("=" * 60)
    print()
    
    # Initialize the tool
    print("1. Initializing Autonomous Evolution Tool...")
    config = MockConfig()
    brain = MockBrain()
    tool = AutonomousEvolutionTool(config=config, brain=brain, tools_registry={})
    tool.cycle_interval = 5  # 5 seconds for demo
    print("   ✅ Tool initialized\n")
    
    # Show help
    print("2. Getting help information...")
    help_text = tool.execute("help")
    print(help_text)
    print()
    
    # Check initial status
    print("3. Checking initial status...")
    status = tool.execute("evolution status")
    print(status)
    print()
    
    # Start evolution
    print("4. Starting autonomous evolution mode...")
    result = tool.execute("evolution start")
    print(result)
    print()
    
    # Wait a moment
    print("5. Waiting for evolution to initialize...")
    await asyncio.sleep(2)
    print("   ✅ Evolution system active\n")
    
    # Check status while running
    print("6. Checking status while active...")
    status = tool.execute("evolution status")
    print(status)
    print()
    
    # Run a manual cycle
    print("7. Running a manual evolution cycle...")
    print("   (This will analyze the project and suggest improvements)\n")
    cycle_result = await tool._run_evolution_cycle()
    print(cycle_result)
    print()
    
    # View history
    print("8. Viewing improvement history...")
    history = tool._get_improvement_history()
    print(history)
    print()
    
    # Stop evolution
    print("9. Stopping autonomous evolution...")
    stop_result = tool.execute("evolution stop")
    print(stop_result)
    print()
    
    # Final status
    print("10. Final status check...")
    final_status = tool.execute("evolution status")
    print(final_status)
    print()


async def demo_analysis_capabilities():
    """Demonstrate analysis capabilities"""
    print("=" * 60)
    print("Analysis Capabilities Demo")
    print("=" * 60)
    print()
    
    config = MockConfig()
    brain = MockBrain()
    tool = AutonomousEvolutionTool(config=config, brain=brain, tools_registry={})
    
    # Show improvement areas
    print("1. Available Improvement Areas:")
    for idx, area in enumerate(tool.improvement_areas, 1):
        priority = tool._calculate_priority(area)
        print(f"   {idx:2d}. {area:30s} (Priority: {priority:2d})")
    print()
    
    # Analyze project
    print("2. Analyzing project for improvements...")
    improvements = await tool._analyze_project()
    print(f"   Found {len(improvements)} potential improvements\n")
    
    # Show some improvements
    if improvements:
        print("3. Sample Improvements:")
        for idx, imp in enumerate(improvements[:5], 1):
            print(f"   {idx}. {imp['description']}")
            print(f"      Area: {imp['area']}, Priority: {imp['priority']}, "
                  f"Effort: {imp['estimated_effort']}, Risk: {imp['risk_level']}")
        print()
    
    # Prioritization
    print("4. Prioritizing improvements...")
    prioritized = tool._prioritize_improvements(improvements)
    print(f"   Top 3 improvements for implementation:")
    for idx, imp in enumerate(prioritized[:3], 1):
        print(f"   {idx}. {imp['description']}")
    print()


async def demo_validation_system():
    """Demonstrate validation system"""
    print("=" * 60)
    print("Validation System Demo")
    print("=" * 60)
    print()
    
    config = MockConfig()
    brain = MockBrain()
    tool = AutonomousEvolutionTool(config=config, brain=brain, tools_registry={})
    
    print("1. Running validation checks...")
    print()
    
    # Test individual validators
    checks = [
        ("Configuration", tool._validate_config()),
        ("Imports", tool._validate_imports()),
        ("Tools", tool._validate_tools())
    ]
    
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name:20s}: {status}")
    
    print()
    
    # Run comprehensive validation
    print("2. Running comprehensive validation...")
    validation_result = await tool._validate_improvements()
    print(f"   Result: {validation_result}")
    print()


async def demo_state_persistence():
    """Demonstrate state persistence"""
    print("=" * 60)
    print("State Persistence Demo")
    print("=" * 60)
    print()
    
    config = MockConfig()
    brain = MockBrain()
    tool = AutonomousEvolutionTool(config=config, brain=brain, tools_registry={})
    
    # Add some fake improvements
    print("1. Adding sample improvements to state...")
    tool.improvements_made = [
        {
            "timestamp": "2024-01-15T10:00:00",
            "description": "Optimized async operations",
            "status": "simulated"
        },
        {
            "timestamp": "2024-01-15T10:30:00",
            "description": "Enhanced error handling",
            "status": "simulated"
        }
    ]
    tool.evolution_cycle_count = 5
    print("   ✅ Sample data added\n")
    
    # Save state
    print("2. Saving state to file...")
    tool._save_state()
    print(f"   ✅ State saved to: {tool.evolution_state_file}\n")
    
    # Create new instance and load
    print("3. Creating new tool instance and loading state...")
    new_tool = AutonomousEvolutionTool(config=config, brain=brain, tools_registry={})
    new_tool.evolution_state_file = tool.evolution_state_file
    new_tool._load_state()
    print(f"   ✅ State loaded: {new_tool.evolution_cycle_count} cycles, "
          f"{len(new_tool.improvements_made)} improvements\n")
    
    # Show statistics
    print("4. Statistics from loaded state...")
    stats = new_tool._get_cycle_statistics()
    print(f"   Total Cycles: {stats['total_cycles']}")
    print(f"   Successful Improvements: {stats['successful_improvements']}")
    print(f"   Failed Attempts: {stats['failed_attempts']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print()


async def main():
    """Main demo function"""
    demos = [
        ("Basic Operations", demo_basic_operations),
        ("Analysis Capabilities", demo_analysis_capabilities),
        ("Validation System", demo_validation_system),
        ("State Persistence", demo_state_persistence)
    ]
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   ULTRON Autonomous Evolution Tool - Interactive Demo      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("This demo will showcase the autonomous evolution system")
    print("capabilities in a controlled environment.")
    print()
    
    for idx, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'=' * 60}")
        print(f"Demo {idx}/{len(demos)}: {name}")
        print(f"{'=' * 60}\n")
        
        try:
            await demo_func()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        
        if idx < len(demos):
            print("\nPress Enter to continue to next demo...")
            input()
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Review the generated documentation:")
    print("   - AUTONOMOUS_EVOLUTION_GUIDE.md (comprehensive)")
    print("   - AUTONOMOUS_EVOLUTION_QUICK_REF.md (quick reference)")
    print()
    print("2. Run the test suite:")
    print("   python -m pytest tests/test_autonomous_evolution_tool.py -v")
    print()
    print("3. Integrate with your ULTRON agent:")
    print("   agent.execute_command('evolution start')")
    print()
    print("4. Monitor the logs:")
    print("   tail -f logs/autonomous_improvements.log")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
