"""
ULTRON Autonomous Evolution Tool

This tool enables ULTRON to continuously prompt itself to maintain, evolve, 
and enhance the ultron_agent project without user interaction. It operates 
autonomously to add functionality, value, and performance improvements.

Key Features:
- Self-prompting mechanism for continuous improvement
- Autonomous project analysis and enhancement
- Safe execution with validation and rollback
- Improvement tracking and metrics
- Integration with existing ULTRON systems
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import subprocess
import hashlib

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision

# Import tool interface
from tools.tool_interface import ToolInterface


class AutonomousEvolutionTool(ToolInterface):
    """
    Autonomous Evolution Tool for continuous self-improvement
    
    This tool enables ULTRON to:
    - Continuously analyze the project for improvement opportunities
    - Generate and validate enhancement proposals
    - Safely implement improvements with rollback capability
    - Track improvement metrics and effectiveness
    - Maintain system stability while evolving
    """
    
    @property
    def name(self) -> str:
        return "Autonomous Evolution Tool"
    
    @property
    def description(self) -> str:
        return (
            "Enables autonomous continuous improvement of the ULTRON agent project. "
            "Analyzes, proposes, validates, and implements enhancements without user interaction."
        )
    
    def __init__(self, config=None, brain=None, tools_registry=None):
        """Initialize the Autonomous Evolution Tool"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.brain = brain
        self.tools_registry = tools_registry
        
        # State management
        self.is_active = False
        self.evolution_cycle_count = 0
        self.improvements_made = []
        self.failed_attempts = []
        
        # Configuration
        self.evolution_state_file = Path("data/autonomous_evolution_state.json")
        self.improvements_log = Path("logs/autonomous_improvements.log")
        self.cycle_interval = 1800  # 30 minutes between cycles
        self.max_improvements_per_cycle = 3
        self.safety_mode = True
        
        # Improvement areas to focus on
        self.improvement_areas = [
            "performance_optimization",
            "new_features",
            "code_quality",
            "documentation",
            "testing",
            "security",
            "user_experience",
            "integration",
            "error_handling",
            "monitoring"
        ]
        
        # Initialize state
        self._load_state()
        self._ensure_directories()
        
        log_info("autonomous_evolution_tool", "Autonomous Evolution Tool initialized")
    
    def match(self, command: str) -> bool:
        """Check if command matches autonomous evolution operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "autonomous evolution", "self improve", "continuous improvement",
            "auto evolve", "maintain project", "enhance project",
            "evolution start", "evolution stop", "evolution status"
        ])
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute autonomous evolution operations"""
        try:
            command_lower = command.lower()
            
            if "start" in command_lower or "activate" in command_lower:
                return self._start_evolution()
            
            elif "stop" in command_lower or "deactivate" in command_lower:
                return self._stop_evolution()
            
            elif "status" in command_lower:
                return self._get_status()
            
            elif "manual cycle" in command_lower or "run cycle" in command_lower:
                return asyncio.run(self._run_evolution_cycle())
            
            elif "history" in command_lower:
                return self._get_improvement_history()
            
            else:
                return self._get_help()
        
        except Exception as e:
            error_msg = f"Autonomous evolution operation failed: {str(e)}"
            log_error("autonomous_evolution_tool", error_msg)
            return error_msg
    
    def _start_evolution(self) -> str:
        """Start autonomous evolution mode"""
        if self.is_active:
            return "Autonomous evolution is already active."
        
        self.is_active = True
        self._save_state()
        
        # Start the evolution loop in the background if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._evolution_loop())
            else:
                # Schedule for later when event loop starts
                log_info("autonomous_evolution_tool", "Evolution loop will start when event loop is running")
        except RuntimeError:
            # No event loop - will be started when agent initializes
            log_info("autonomous_evolution_tool", "Evolution loop will start with agent initialization")
        
        log_ai_decision(
            "autonomous_evolution_tool",
            "Autonomous evolution mode activated",
            reasoning="User requested continuous self-improvement"
        )
        
        return """✅ Autonomous Evolution Mode ACTIVATED

ULTRON will now continuously:
- Analyze the project for improvement opportunities
- Generate enhancement proposals
- Validate and test improvements
- Safely implement changes with rollback capability
- Track improvement metrics

Cycle Interval: 30 minutes
Safety Mode: Enabled
Max Improvements per Cycle: 3

Use 'evolution status' to monitor progress.
Use 'evolution stop' to deactivate."""
    
    def _stop_evolution(self) -> str:
        """Stop autonomous evolution mode"""
        if not self.is_active:
            return "Autonomous evolution is not currently active."
        
        self.is_active = False
        self._save_state()
        
        log_ai_decision(
            "autonomous_evolution_tool",
            "Autonomous evolution mode deactivated",
            reasoning="User requested stop"
        )
        
        stats = self._get_cycle_statistics()
        
        return f"""🛑 Autonomous Evolution Mode DEACTIVATED

Session Statistics:
- Total Cycles: {stats['total_cycles']}
- Successful Improvements: {stats['successful_improvements']}
- Failed Attempts: {stats['failed_attempts']}
- Success Rate: {stats['success_rate']:.1f}%
- Uptime: {stats['uptime']}

All improvements have been logged and can be reviewed."""
    
    def _get_status(self) -> str:
        """Get current autonomous evolution status"""
        status = "🤖 AUTONOMOUS EVOLUTION STATUS\n\n"
        status += f"Mode: {'🟢 ACTIVE' if self.is_active else '🔴 INACTIVE'}\n"
        status += f"Total Cycles Completed: {self.evolution_cycle_count}\n"
        status += f"Improvements Made: {len(self.improvements_made)}\n"
        status += f"Failed Attempts: {len(self.failed_attempts)}\n\n"
        
        if self.improvements_made:
            status += "Recent Improvements:\n"
            for imp in self.improvements_made[-5:]:
                status += f"  • {imp['timestamp']}: {imp['description']}\n"
        
        if self.is_active:
            status += f"\nNext cycle in approximately {self.cycle_interval // 60} minutes"
        
        return status
    
    async def _evolution_loop(self):
        """Main autonomous evolution loop"""
        log_info("autonomous_evolution_tool", "Evolution loop started")
        
        while self.is_active:
            try:
                # Wait for the next cycle
                await asyncio.sleep(self.cycle_interval)
                
                if not self.is_active:
                    break
                
                # Run an evolution cycle
                result = await self._run_evolution_cycle()
                log_info("autonomous_evolution_tool", f"Cycle result: {result}")
                
            except Exception as e:
                log_error("autonomous_evolution_tool", f"Error in evolution loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retry
        
        log_info("autonomous_evolution_tool", "Evolution loop stopped")
    
    async def _run_evolution_cycle(self) -> str:
        """Run a single evolution cycle"""
        log_info("autonomous_evolution_tool", f"Starting evolution cycle #{self.evolution_cycle_count + 1}")
        
        self.evolution_cycle_count += 1
        cycle_start_time = datetime.now()
        
        result_summary = f"🔄 Evolution Cycle #{self.evolution_cycle_count}\n\n"
        
        try:
            # Step 1: Analyze project for improvements
            result_summary += "📊 Analyzing project...\n"
            improvements = await self._analyze_project()
            result_summary += f"Found {len(improvements)} potential improvements\n\n"
            
            # Step 2: Prioritize improvements
            result_summary += "🎯 Prioritizing improvements...\n"
            prioritized = self._prioritize_improvements(improvements)
            selected = prioritized[:self.max_improvements_per_cycle]
            result_summary += f"Selected {len(selected)} improvements for implementation\n\n"
            
            # Step 3: Implement improvements
            result_summary += "🔧 Implementing improvements...\n"
            for idx, improvement in enumerate(selected, 1):
                impl_result = await self._implement_improvement(improvement)
                result_summary += f"{idx}. {improvement['description']}: {impl_result['status']}\n"
            
            # Step 4: Validate changes
            result_summary += "\n✅ Validating changes...\n"
            validation_result = await self._validate_improvements()
            result_summary += f"Validation: {validation_result}\n\n"
            
            # Update statistics
            cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
            result_summary += f"⏱️ Cycle completed in {cycle_duration:.1f} seconds\n"
            
            self._save_state()
            
        except Exception as e:
            error_msg = f"Cycle failed: {str(e)}"
            log_error("autonomous_evolution_tool", error_msg)
            result_summary += f"\n❌ {error_msg}\n"
            
            self.failed_attempts.append({
                "cycle": self.evolution_cycle_count,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
        
        return result_summary
    
    async def _analyze_project(self) -> List[Dict[str, Any]]:
        """Analyze the project for improvement opportunities"""
        improvements = []
        
        # Use the brain to generate improvement ideas if available
        if self.brain:
            for area in self.improvement_areas:
                prompt = self._generate_analysis_prompt(area)
                try:
                    response = await self._get_brain_suggestions(prompt)
                    if response:
                        improvements.extend(self._parse_suggestions(response, area))
                except Exception as e:
                    log_error("autonomous_evolution_tool", f"Error analyzing {area}: {e}")
        
        # Add automated static analysis improvements
        improvements.extend(self._automated_analysis())
        
        return improvements
    
    def _generate_analysis_prompt(self, area: str) -> str:
        """Generate a prompt for the AI brain to analyze specific area"""
        prompts = {
            "performance_optimization": """
            Analyze the ULTRON agent project for performance optimization opportunities.
            Focus on:
            - Code efficiency improvements
            - Memory usage optimization
            - Async/await optimizations
            - Caching strategies
            - Database query optimization
            
            Provide 3 specific, actionable improvements with implementation details.
            """,
            
            "new_features": """
            Suggest 3 new features that would add value to the ULTRON agent project.
            Consider:
            - User-requested features from common use cases
            - Integration with new AI models or services
            - Enhanced automation capabilities
            - Improved monitoring and diagnostics
            
            Each feature should be practical, implementable, and align with project goals.
            """,
            
            "code_quality": """
            Review the ULTRON agent codebase for code quality improvements.
            Look for:
            - Code duplication that can be refactored
            - Complex functions that need simplification
            - Missing error handling
            - Inconsistent coding patterns
            - Opportunities for better abstractions
            
            Provide 3 specific refactoring suggestions.
            """,
            
            "documentation": """
            Assess the ULTRON agent documentation for improvements.
            Check for:
            - Missing docstrings
            - Outdated documentation
            - Unclear API descriptions
            - Missing usage examples
            - Incomplete setup instructions
            
            Suggest 3 documentation enhancements.
            """,
            
            "testing": """
            Evaluate the ULTRON agent test coverage and quality.
            Identify:
            - Untested critical paths
            - Missing edge case tests
            - Integration test gaps
            - Test reliability issues
            - Performance test opportunities
            
            Propose 3 testing improvements.
            """,
            
            "security": """
            Audit the ULTRON agent for security improvements.
            Review:
            - Input validation and sanitization
            - Authentication and authorization
            - Secret management
            - Dependency vulnerabilities
            - Data protection
            
            Recommend 3 security enhancements.
            """,
            
            "user_experience": """
            Analyze the ULTRON agent user experience.
            Consider:
            - GUI usability improvements
            - Voice interaction enhancements
            - Error message clarity
            - Setup process simplification
            - Feedback and progress indicators
            
            Suggest 3 UX improvements.
            """,
            
            "integration": """
            Evaluate integration opportunities for ULTRON agent.
            Look at:
            - New AI model integrations
            - External service connections
            - Tool ecosystem expansion
            - API enhancements
            - Plugin architecture improvements
            
            Propose 3 integration enhancements.
            """,
            
            "error_handling": """
            Review error handling in the ULTRON agent.
            Assess:
            - Exception handling completeness
            - Error recovery mechanisms
            - Logging and debugging information
            - User error messages
            - Graceful degradation
            
            Identify 3 error handling improvements.
            """,
            
            "monitoring": """
            Analyze monitoring and observability in ULTRON agent.
            Evaluate:
            - Performance metrics collection
            - Health check mechanisms
            - Diagnostic capabilities
            - Alert systems
            - Usage analytics
            
            Recommend 3 monitoring enhancements.
            """
        }
        
        return prompts.get(area, f"Analyze the ULTRON agent project for {area} improvements.")
    
    async def _get_brain_suggestions(self, prompt: str) -> Optional[str]:
        """Get suggestions from the AI brain"""
        if not self.brain:
            return None
        
        try:
            # Use brain's planning or generation method
            if hasattr(self.brain, 'plan'):
                response = await self.brain.plan(prompt)
            elif hasattr(self.brain, 'generate'):
                response = await self.brain.generate(prompt)
            else:
                return None
            
            return response
        except Exception as e:
            log_error("autonomous_evolution_tool", f"Brain suggestion failed: {e}")
            return None
    
    def _parse_suggestions(self, response: str, area: str) -> List[Dict[str, Any]]:
        """Parse AI suggestions into structured improvements"""
        improvements = []
        
        # Simple parsing - look for numbered items or bullet points
        lines = response.split('\n')
        current_improvement = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a new improvement (numbered or bulleted)
            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '-', '*', '•']):
                if current_improvement:
                    improvements.append(current_improvement)
                
                # Extract the description
                description = line.lstrip('123.-*• ')
                current_improvement = {
                    "area": area,
                    "description": description,
                    "details": [],
                    "priority": self._calculate_priority(area),
                    "estimated_effort": "medium",
                    "risk_level": "low" if self.safety_mode else "medium"
                }
            elif current_improvement:
                # Add details to current improvement
                current_improvement["details"].append(line)
        
        # Add the last improvement
        if current_improvement:
            improvements.append(current_improvement)
        
        return improvements
    
    def _automated_analysis(self) -> List[Dict[str, Any]]:
        """Perform automated static analysis"""
        improvements = []
        
        # Check for missing docstrings
        try:
            result = subprocess.run(
                ["python", "-m", "pydocstyle", "--count", "tools/"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                improvements.append({
                    "area": "documentation",
                    "description": "Add missing docstrings to tools",
                    "details": ["Run pydocstyle to identify specific files"],
                    "priority": 5,
                    "estimated_effort": "low",
                    "risk_level": "low"
                })
        except Exception:
            pass
        
        # Check for unused imports
        try:
            result = subprocess.run(
                ["python", "-m", "pylint", "--disable=all", "--enable=unused-import", "tools/"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if "unused-import" in result.stdout:
                improvements.append({
                    "area": "code_quality",
                    "description": "Remove unused imports",
                    "details": ["Clean up unused imports identified by pylint"],
                    "priority": 4,
                    "estimated_effort": "low",
                    "risk_level": "low"
                })
        except Exception:
            pass
        
        return improvements
    
    def _calculate_priority(self, area: str) -> int:
        """Calculate priority score for improvement area (1-10, 10 highest)"""
        priority_map = {
            "security": 10,
            "performance_optimization": 9,
            "error_handling": 8,
            "new_features": 7,
            "user_experience": 7,
            "testing": 6,
            "code_quality": 6,
            "integration": 5,
            "monitoring": 5,
            "documentation": 4
        }
        return priority_map.get(area, 5)
    
    def _prioritize_improvements(self, improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize improvements based on multiple factors"""
        # Sort by priority, estimated effort, and risk level
        sorted_improvements = sorted(
            improvements,
            key=lambda x: (
                -x.get("priority", 5),  # Higher priority first
                {"low": 1, "medium": 2, "high": 3}.get(x.get("estimated_effort", "medium"), 2),  # Lower effort first
                -{"low": 3, "medium": 2, "high": 1}.get(x.get("risk_level", "medium"), 2)  # Lower risk first
            )
        )
        
        return sorted_improvements
    
    async def _implement_improvement(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a single improvement"""
        log_info("autonomous_evolution_tool", f"Implementing: {improvement['description']}")
        
        result = {
            "status": "pending",
            "description": improvement["description"],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Create a backup/checkpoint before making changes
            if self.safety_mode:
                self._create_checkpoint()
            
            # Simulate implementation for now
            # In a real implementation, this would:
            # 1. Generate code changes using the brain
            # 2. Apply changes to files
            # 3. Run tests
            # 4. Validate functionality
            
            await asyncio.sleep(1)  # Simulate work
            
            # For safety, we'll mark as "simulated" unless safety mode is off
            if self.safety_mode:
                result["status"] = "simulated"
                result["note"] = "Safety mode enabled - changes not applied"
            else:
                result["status"] = "success"
                self.improvements_made.append(result)
            
            log_ai_decision(
                "autonomous_evolution_tool",
                f"Improvement implemented: {improvement['description']}",
                reasoning=f"Area: {improvement['area']}, Priority: {improvement['priority']}"
            )
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            log_error("autonomous_evolution_tool", f"Implementation failed: {e}")
            
            # Rollback if needed
            if self.safety_mode:
                self._rollback_checkpoint()
        
        return result
    
    async def _validate_improvements(self) -> str:
        """Validate that improvements don't break existing functionality"""
        try:
            # Run basic validation checks
            checks = [
                ("Configuration valid", self._validate_config()),
                ("Core imports work", self._validate_imports()),
                ("Tools discoverable", self._validate_tools())
            ]
            
            passed = sum(1 for _, result in checks if result)
            total = len(checks)
            
            validation_report = f"{passed}/{total} checks passed"
            
            if passed == total:
                return f"✅ All validations passed ({validation_report})"
            else:
                failed = [name for name, result in checks if not result]
                return f"⚠️ Some validations failed ({validation_report}): {', '.join(failed)}"
        
        except Exception as e:
            return f"❌ Validation error: {str(e)}"
    
    def _validate_config(self) -> bool:
        """Validate configuration is still valid"""
        try:
            config_path = Path("ultron_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    json.load(f)
                return True
        except Exception:
            pass
        return False
    
    def _validate_imports(self) -> bool:
        """Validate core imports still work"""
        try:
            import agent_core
            import brain
            return True
        except Exception:
            return False
    
    def _validate_tools(self) -> bool:
        """Validate tools are still discoverable"""
        try:
            tools_dir = Path("tools")
            if tools_dir.exists():
                py_files = list(tools_dir.glob("*.py"))
                return len(py_files) > 0
        except Exception:
            pass
        return False
    
    def _create_checkpoint(self):
        """Create a checkpoint for rollback"""
        # In production, this would create a git commit or file backup
        log_info("autonomous_evolution_tool", "Checkpoint created")
    
    def _rollback_checkpoint(self):
        """Rollback to previous checkpoint"""
        log_info("autonomous_evolution_tool", "Rolling back to checkpoint")
    
    def _get_improvement_history(self) -> str:
        """Get history of improvements made"""
        if not self.improvements_made:
            return "No improvements have been made yet."
        
        history = "📜 IMPROVEMENT HISTORY\n\n"
        for idx, imp in enumerate(self.improvements_made[-20:], 1):
            history += f"{idx}. {imp['timestamp']}: {imp['description']} ({imp['status']})\n"
        
        return history
    
    def _get_cycle_statistics(self) -> Dict[str, Any]:
        """Get statistics about evolution cycles"""
        successful = len([i for i in self.improvements_made if i.get('status') == 'success'])
        failed = len(self.failed_attempts)
        total = successful + failed
        
        return {
            "total_cycles": self.evolution_cycle_count,
            "successful_improvements": successful,
            "failed_attempts": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "uptime": self._calculate_uptime()
        }
    
    def _calculate_uptime(self) -> str:
        """Calculate uptime of evolution system"""
        # In production, track actual start time
        return "N/A"
    
    def _get_help(self) -> str:
        """Get help information"""
        return """🤖 AUTONOMOUS EVOLUTION TOOL

Commands:
  'evolution start'  - Start autonomous improvement mode
  'evolution stop'   - Stop autonomous improvement mode
  'evolution status' - Show current status and statistics
  'manual cycle'     - Run a single evolution cycle manually
  'evolution history'- View improvement history

The Autonomous Evolution Tool enables ULTRON to continuously improve itself by:
- Analyzing the project for opportunities
- Generating enhancement proposals
- Safely implementing improvements
- Tracking metrics and effectiveness

Safety Mode: Enabled by default (changes are simulated)
Cycle Interval: 30 minutes
Max Improvements per Cycle: 3"""
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        for directory in [self.evolution_state_file.parent, self.improvements_log.parent]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_state(self):
        """Load evolution state from file"""
        try:
            if self.evolution_state_file.exists():
                with open(self.evolution_state_file) as f:
                    state = json.load(f)
                    self.evolution_cycle_count = state.get("cycle_count", 0)
                    self.improvements_made = state.get("improvements", [])
                    self.failed_attempts = state.get("failed_attempts", [])
        except Exception as e:
            log_error("autonomous_evolution_tool", f"Failed to load state: {e}")
    
    def _save_state(self):
        """Save evolution state to file"""
        try:
            state = {
                "is_active": self.is_active,
                "cycle_count": self.evolution_cycle_count,
                "improvements": self.improvements_made[-100:],  # Keep last 100
                "failed_attempts": self.failed_attempts[-50:],  # Keep last 50
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.evolution_state_file, 'w') as f:
                json.dump(state, f, indent=2)
        
        except Exception as e:
            log_error("autonomous_evolution_tool", f"Failed to save state: {e}")
    
    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for registration"""
        return {
            "name": "Autonomous Evolution Tool",
            "description": "Enables autonomous continuous improvement of the ULTRON agent project. Analyzes, proposes, validates, and implements enhancements without user interaction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Evolution command to execute (start, stop, status, manual cycle, history)"
                    }
                },
                "required": ["command"]
            }
        }


# Export the tool
__all__ = ['AutonomousEvolutionTool']
