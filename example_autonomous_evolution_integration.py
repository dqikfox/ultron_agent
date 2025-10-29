"""
Example: Integrating Autonomous Evolution Tool with ULTRON Agent

This example shows how to integrate the autonomous evolution tool
with the main ULTRON agent system.
"""

import asyncio
import json
from pathlib import Path


def load_config(config_path: str = "ultron_config.json") -> dict:
    """Load ULTRON configuration"""
    with open(config_path) as f:
        return json.load(f)


async def example_1_manual_start():
    """Example 1: Manually start autonomous evolution"""
    print("=" * 60)
    print("Example 1: Manual Start")
    print("=" * 60)
    print()
    
    from tools.autonomous_evolution_tool import AutonomousEvolutionTool
    
    # Load config
    config = load_config()
    
    # Create tool (brain would be passed from agent in production)
    tool = AutonomousEvolutionTool(config=config, brain=None)
    
    # Start evolution
    result = tool.execute("evolution start")
    print(result)
    
    # Check status
    print("\nChecking status...")
    status = tool.execute("evolution status")
    print(status)
    
    # Stop evolution
    print("\nStopping...")
    stop_result = tool.execute("evolution stop")
    print(stop_result)


async def example_2_config_based_start():
    """Example 2: Auto-start based on configuration"""
    print("=" * 60)
    print("Example 2: Config-Based Auto-Start")
    print("=" * 60)
    print()
    
    from tools.autonomous_evolution_tool import AutonomousEvolutionTool
    
    # Load config
    config = load_config()
    
    # Check if auto-start is enabled
    auto_config = config.get("autonomous_evolution", {})
    auto_start = auto_config.get("enabled", False)
    
    print(f"Auto-start enabled in config: {auto_start}")
    print(f"Cycle interval: {auto_config.get('cycle_interval', 1800)} seconds")
    print(f"Safety mode: {auto_config.get('safety_mode', True)}")
    print()
    
    # Create tool
    tool = AutonomousEvolutionTool(config=config, brain=None)
    
    # Auto-start if configured
    if auto_start:
        print("Auto-starting evolution (per config)...")
        result = tool.execute("evolution start")
        print(result)
    else:
        print("Auto-start disabled. Evolution not started.")
        print("To enable, set 'autonomous_evolution.enabled: true' in ultron_config.json")


async def example_3_agent_integration():
    """Example 3: Full agent integration pattern"""
    print("=" * 60)
    print("Example 3: Full Agent Integration")
    print("=" * 60)
    print()
    
    print("This example shows how the tool integrates with the agent:")
    print()
    
    # Simulated agent initialization
    print("1. Agent initialization...")
    config = load_config()
    print("   ✅ Config loaded")
    
    print("\n2. Tool discovery...")
    print("   Scanning tools/ directory...")
    from tools.autonomous_evolution_tool import AutonomousEvolutionTool
    print("   ✅ Found AutonomousEvolutionTool")
    
    print("\n3. Tool registration...")
    tool = AutonomousEvolutionTool(config=config, brain=None)
    tools_registry = {"autonomous_evolution": tool}
    print(f"   ✅ Registered {len(tools_registry)} tool(s)")
    
    print("\n4. Auto-start check...")
    auto_config = config.get("autonomous_evolution", {})
    if auto_config.get("enabled", False):
        print("   Auto-start enabled - starting evolution...")
        tool.execute("evolution start")
    else:
        print("   Auto-start disabled - manual activation required")
    
    print("\n5. Command routing available:")
    print("   User: 'evolution start'")
    print("   Agent: Routes to autonomous_evolution tool")
    print("   Tool: Executes command and returns result")


async def example_4_custom_configuration():
    """Example 4: Custom configuration"""
    print("=" * 60)
    print("Example 4: Custom Configuration")
    print("=" * 60)
    print()
    
    from tools.autonomous_evolution_tool import AutonomousEvolutionTool
    
    config = load_config()
    
    # Create tool
    tool = AutonomousEvolutionTool(config=config, brain=None)
    
    # Customize settings
    print("Applying custom configuration...")
    tool.cycle_interval = 3600  # 1 hour instead of 30 minutes
    tool.max_improvements_per_cycle = 5  # More improvements per cycle
    tool.improvement_areas = [  # Focus on specific areas
        "security",
        "performance_optimization",
        "testing"
    ]
    
    print(f"  Cycle interval: {tool.cycle_interval} seconds (1 hour)")
    print(f"  Max improvements per cycle: {tool.max_improvements_per_cycle}")
    print(f"  Focus areas: {', '.join(tool.improvement_areas)}")
    print()
    
    print("✅ Custom configuration applied")
    print("   Tool will focus on security, performance, and testing")


async def main():
    """Run all examples"""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   Autonomous Evolution Tool - Integration Examples        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    examples = [
        example_1_manual_start,
        example_2_config_based_start,
        example_3_agent_integration,
        example_4_custom_configuration
    ]
    
    for idx, example in enumerate(examples, 1):
        await example()
        if idx < len(examples):
            print("\n" + "-" * 60 + "\n")
    
    print()
    print("=" * 60)
    print("Integration Examples Complete")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Review ultron_config.json to configure auto-start")
    print("2. Run 'python demo_autonomous_evolution.py' for full demo")
    print("3. Check logs/ directory for improvement logs")
    print("4. Use 'evolution start' command in running agent")
    print()


if __name__ == "__main__":
    asyncio.run(main())
