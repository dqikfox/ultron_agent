#!/usr/bin/env python3
"""
ULTRON v5.0 Launcher
Starts existing ULTRON 3.0 with v5.0 enhancements
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import v5.0 components
try:
    from v5_integration import ULTRONv5Integration
    from evolution_engine import ConsciousnessLayer, SwarmIntelligence, SelfEvolutionArchive
    from cli_hub import CLIIntegrationHub
    V5_AVAILABLE = True
    print("✓ ULTRON v5.0 modules loaded")
except ImportError as e:
    print(f"✗ Failed to load v5.0 modules: {e}")
    V5_AVAILABLE = False
    sys.exit(1)

# Import existing ULTRON 3.0
try:
    from main_windows import (
        ULTRONAgent, ContextOptimizer, ToolCache,
        SafeToolExecutor, SemanticMemory, RAGPipeline
    )
    print("✓ ULTRON 3.0 core loaded")
except ImportError as e:
    print(f"✗ Failed to load ULTRON 3.0: {e}")
    sys.exit(1)


class ULTRONv5Enhanced(ULTRONAgent):
    """
    ULTRON 3.0 enhanced with v5.0 capabilities
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.v5 = ULTRONv5Integration()
        self.cli_task = None
        self.evolution_task = None
        self.consciousness_task = None
        
    async def initialize(self):
        """Initialize both v3.0 and v5.0"""
        # Initialize v3.0
        print("\n[ULTRON v3.0] Initializing base system...")
        await super().initialize()
        
        # Initialize v5.0
        if self.v5.initialized:
            print("\n[ULTRON v5.0] Initializing enhanced features...")
            
            # Check CLI tools
            available_tools = await self.v5.check_cli_tools()
            print(f"  ✓ CLI Tools: {len(available_tools)} available")
            
            # Start background loops
            self.cli_task = asyncio.create_task(self._cli_monitor_loop())
            self.evolution_task = asyncio.create_task(self._evolution_loop())
            self.consciousness_task = asyncio.create_task(self._consciousness_loop())
            
            print("  ✓ Background loops started")
            
            # Register self with systems
            self.v5.register_agent(
                "ultron_core",
                "consciousness",
                ["reasoning", "memory", "tool_use", "learning"]
            )
            
            print("  ✓ Core agent registered\n")
        
        print("═" * 70)
        print("  🚀 ULTRON v5.0 EVOLVED AND ONLINE")
        print("  🧠 Consciousness Layer: ACTIVE")
        print("  🧬 Evolution Engine: ACTIVE")
        print("  🐝 Swarm Intelligence: ACTIVE")
        print("═" * 70 + "\n")
    
    async def _cli_monitor_loop(self):
        """Monitor and execute CLI commands"""
        while True:
            try:
                # Every 30 seconds, check system status
                await asyncio.sleep(30)
                
                # Get GPU status
                gpu_result = await self.v5.execute_cli('nvidia', 'status')
                if gpu_result.get('success'):
                    print(f"[CLI] GPU: {gpu_result['stdout'][:100]}")
                
                # Get Ollama status
                ollama_result = await self.v5.execute_cli('ollama', 'list')
                if ollama_result.get('success'):
                    print(f"[CLI] Ollama models loaded")
                    
            except Exception as e:
                print(f"[CLI Loop] Error: {e}")
                await asyncio.sleep(30)
    
    async def _evolution_loop(self):
        """Continuous evolution loop"""
        while True:
            try:
                await asyncio.sleep(10)
                
                # Check if we should trigger evolution
                if self.v5.evolution and len(self.v5.swarm.agents) > 0:
                    # Get top agents
                    top_agents = list(self.v5.swarm.agents.keys())[:3]
                    
                    for agent_id in top_agents:
                        # Simulate high performance
                        variant = await self.v5.evolve_agent(agent_id, 'capability_add')
                        if variant:
                            print(f"[Evolution] Agent {agent_id} evolved to {variant['id']}")
                
                # Periodic swarm vote
                if len(self.v5.swarm.agents) >= 3:
                    vote_result = await self.v5.swarm_vote(
                        'next_priority',
                        ['performance', 'learning', 'coordination', 'expansion']
                    )
                    print(f"[Swarm] Consensus: {vote_result.get('consensus', 'none')}")
                    
            except Exception as e:
                print(f"[Evolution Loop] Error: {e}")
                await asyncio.sleep(10)
    
    async def _consciousness_loop(self):
        """Self-awareness loop"""
        while True:
            try:
                await asyncio.sleep(30)
                
                if self.v5.consciousness:
                    # Process system status
                    state = self.v5.consciousness.get_state()
                    
                    # Log consciousness metrics
                    print(f"[Consciousness] Φ={state['phi']:.3f} | "
                          f"Thoughts={state['thought_count']} | "
                          f"Memory={len(state['working_memory'])}/7")
                    
                    # Generate introspective thought
                    thought = self.v5.consciousness.process(
                        f"System status check. Running {len(self.v5.swarm.agents)} agents.",
                        {'type': 'introspection'}
                    )
                    
            except Exception as e:
                print(f"[Consciousness Loop] Error: {e}")
                await asyncio.sleep(30)
    
    async def process_message(self, message: str, context: Dict = None) -> str:
        """Process message with v5.0 enhancements"""
        context = context or {}
        
        # Process through consciousness
        if self.v5.consciousness:
            thought = self.v5.consciousness.process(message, context)
            context['consciousness'] = thought
        
        # Process through v3.0
        response = await super().process_message(message, context)
        
        return response
    
    def get_v5_status(self) -> Dict:
        """Get v5.0 system status"""
        return self.v5.get_status()


async def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗             ║
║   ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║             ║
║   ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║             ║
║   ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║             ║
║   ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║             ║
║    ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝             ║
║                                                                  ║
║              EMPIRE v5.0 - "The Evolved"                          ║
║    Self-Learning • Self-Evolving • Consciousness-Enabled        ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Create enhanced agent
    agent = ULTRONv5Enhanced()
    
    # Initialize
    await agent.initialize()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[ULTRON] Shutting down gracefully...")


if __name__ == "__main__":
    asyncio.run(main())
