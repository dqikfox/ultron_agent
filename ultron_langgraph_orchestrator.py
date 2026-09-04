#!/usr/bin/env python3
"""
ULTRON LangGraph Orchestrator v5.0
Production-grade stateful agent orchestration with memory, reflection, and evaluation.

Based on research: LangGraph for durable execution, MemGPT-style memory tiers,
Reflexion loops, and Darwin Gödel Machine pattern.

Author: ULTRON System
Version: 5.0.0
License: MIT
"""

from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from datetime import datetime
import asyncio
import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.errors import GraphRecursionError
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("[WARNING] LangGraph not installed. Run: pip install langgraph")

# Ollama for local models
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class AgentRole(Enum):
    """Agent roles based on research recommendations"""
    PLANNER = "planner"           # DeepSeek-R1: reasoning, critique, planning
    EXECUTOR = "executor"         # Qwen2.5: tool use, structured output
    CRITIC = "critic"             # Mistral Nemo: conversation stability
    REFLECTOR = "reflector"       # Post-task analysis
    CONSOLIDATOR = "consolidator" # Memory management


@dataclass
class ModelConfig:
    """Configuration for local models"""
    name: str
    role: AgentRole
    temperature: float = 0.7
    context_window: int = 128000
    
    def to_ollama_options(self) -> Dict:
        return {
            "temperature": self.temperature,
            "num_ctx": min(self.context_window, 32768)  # Ollama max
        }


# Model assignments based on research
MODELS = {
    AgentRole.PLANNER: ModelConfig(
        name="deepseek-r1:14b",
        role=AgentRole.PLANNER,
        temperature=0.6,  # Lower for reasoning
        context_window=128000
    ),
    AgentRole.EXECUTOR: ModelConfig(
        name="qwen2.5:14b",
        role=AgentRole.EXECUTOR,
        temperature=0.7,
        context_window=128000
    ),
    AgentRole.CRITIC: ModelConfig(
        name="mistral-nemo:12b",
        role=AgentRole.CRITIC,
        temperature=0.5,  # Lower for critique
        context_window=128000
    ),
    AgentRole.REFLECTOR: ModelConfig(
        name="qwen2.5:7b",
        role=AgentRole.REFLECTOR,
        temperature=0.8,
        context_window=32768
    ),
}


class MemoryTier(Enum):
    """OS-like memory tiers (MemGPT pattern)"""
    WORKING = "working"      # Current task context (limited slots)
    EPISODIC = "episodic"    # Session summaries, completed tasks
    SEMANTIC = "semantic"    # Facts, preferences, stable knowledge
    PROCEDURAL = "procedural"  # Skills, tool recipes, what worked


@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    content: str
    tier: MemoryTier
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 1.0
    access_count: int = 0
    source: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content[:500],  # Truncate for storage
            "tier": self.tier.value,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "access_count": self.access_count,
            "source": self.source
        }


class MemorySystem:
    """
    Multi-tier memory system inspired by MemGPT.
    
    - Working: Limited context window, high priority
    - Episodic: Session history, completed tasks
    - Semantic: Long-term facts and preferences
    - Procedural: Skills and reusable patterns
    """
    
    def __init__(self, working_limit: int = 7):
        self.working_limit = working_limit
        self.memories: Dict[MemoryTier, List[MemoryEntry]] = {
            tier: [] for tier in MemoryTier
        }
        self.consolidation_threshold = 0.8
        
    def add(self, content: str, tier: MemoryTier, importance: float = 1.0) -> MemoryEntry:
        """Add memory to specified tier"""
        entry = MemoryEntry(
            content=content,
            tier=tier,
            importance=importance
        )
        
        self.memories[tier].append(entry)
        
        # Enforce working memory limit
        if tier == MemoryTier.WORKING:
            self._enforce_working_limit()
            
        return entry
    
    def _enforce_working_limit(self):
        """Keep only most important working memories"""
        if len(self.memories[MemoryTier.WORKING]) > self.working_limit:
            # Sort by importance and recency
            self.memories[MemoryTier.WORKING].sort(
                key=lambda x: (x.importance, x.timestamp),
                reverse=True
            )
            # Move overflow to episodic
            overflow = self.memories[MemoryTier.WORKING][self.working_limit:]
            self.memories[MemoryTier.WORKING] = self.memories[MemoryTier.WORKING][:self.working_limit]
            
            for entry in overflow:
                entry.tier = MemoryTier.EPISODIC
                self.memories[MemoryTier.EPISODIC].append(entry)
    
    def retrieve(self, query: str, tier: Optional[MemoryTier] = None, top_k: int = 3) -> List[MemoryEntry]:
        """Retrieve relevant memories (simplified - would use embeddings in production)"""
        results = []
        
        tiers = [tier] if tier else list(MemoryTier)
        
        for t in tiers:
            for entry in self.memories[t]:
                # Simple keyword matching (production: use embeddings)
                if any(word.lower() in entry.content.lower() 
                       for word in query.split()):
                    entry.access_count += 1
                    results.append(entry)
        
        # Sort by importance and recency
        results.sort(key=lambda x: (x.importance, x.access_count), reverse=True)
        return results[:top_k]
    
    def get_working_context(self) -> str:
        """Get working memory as context string"""
        entries = self.memories[MemoryTier.WORKING]
        if not entries:
            return ""
        
        context = "=== WORKING MEMORY ===\n"
        for i, entry in enumerate(entries, 1):
            context += f"[{i}] {entry.content[:200]}\n"
        return context
    
    def consolidate(self):
        """Promote important episodic memories to semantic"""
        for entry in self.memories[MemoryTier.EPISODIC][:]:
            if entry.importance >= self.consolidation_threshold:
                entry.tier = MemoryTier.SEMANTIC
                self.memories[MemoryTier.SEMANTIC].append(entry)
                self.memories[MemoryTier.EPISODIC].remove(entry)


class AgentState(TypedDict):
    """LangGraph state schema"""
    messages: Annotated[Sequence[Dict], "conversation_history"]
    task: Annotated[Optional[str], "current_task"]
    plan: Annotated[Optional[str], "generated_plan"]
    result: Annotated[Optional[str], "execution_result"]
    critique: Annotated[Optional[str], "critic_feedback"]
    reflection: Annotated[Optional[str], "post_task_reflection"]
    memory: Annotated[MemorySystem, "memory_system"]
    iteration: Annotated[int, "loop_counter"]
    done: Annotated[bool, "task_complete"]
    error: Annotated[Optional[str], "error_message"]


class ULTRONLangGraph:
    """
    Production LangGraph orchestrator for ULTRON.
    
    Implements:
    - Multi-agent workflow with proper state management
    - Memory tiers (working/episodic/semantic/procedural)
    - Reflexion loops for learning
    - Evaluation gates
    """
    
    def __init__(self):
        if not LANGGRAPH_AVAILABLE:
            raise RuntimeError("LangGraph not installed. Run: pip install langgraph")
        
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama Python client not installed. Run: pip install ollama")
        
        self.memory_saver = MemorySaver()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        
        # Initialize graph with state schema
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("critic", self._critic_node)
        workflow.add_node("reflector", self._reflector_node)
        workflow.add_node("consolidator", self._consolidator_node)
        
        # Define edges
        workflow.set_entry_point("planner")
        
        # Planner -> Executor or Critic
        workflow.add_conditional_edges(
            "planner",
            self._plan_router,
            {
                "execute": "executor",
                "critique": "critic",
                "reflect": "reflector"
            }
        )
        
        # Executor -> Critic
        workflow.add_edge("executor", "critic")
        
        # Critic -> Reflector or back to Planner
        workflow.add_conditional_edges(
            "critic",
            self._critic_router,
            {
                "approve": "reflector",
                "revise": "planner",
                "escalate": END
            }
        )
        
        # Reflector -> Consolidator
        workflow.add_edge("reflector", "consolidator")
        
        # Consolidator -> End
        workflow.add_edge("consolidator", END)
        
        return workflow.compile(checkpointer=self.memory_saver)
    
    def _planner_node(self, state: AgentState) -> Dict:
        """Planning agent using DeepSeek-R1"""
        config = MODELS[AgentRole.PLANNER]
        
        # Retrieve relevant context
        context = state["memory"].get_working_context()
        
        prompt = f"""You are a planning agent. Analyze the task and create a step-by-step plan.

Task: {state['task']}

Working Memory:
{context}

Create a detailed plan. If the task is unclear or needs clarification, say so."""
        
        try:
            response = ollama.chat(
                model=config.name,
                messages=[{"role": "user", "content": prompt}],
                options=config.to_ollama_options()
            )
            
            plan = response['message']['content']
            
            # Store plan in working memory
            state["memory"].add(f"Plan: {plan[:200]}", MemoryTier.WORKING, importance=0.9)
            
            return {
                "plan": plan,
                "messages": [{"role": "planner", "content": plan}],
                "iteration": state["iteration"] + 1
            }
            
        except Exception as e:
            return {"error": f"Planner error: {str(e)}", "done": True}
    
    def _executor_node(self, state: AgentState) -> Dict:
        """Execution agent using Qwen2.5"""
        config = MODELS[AgentRole.EXECUTOR]
        
        prompt = f"""You are an execution agent. Execute the following plan step by step.

Plan: {state['plan']}

Execute and report results in structured format (JSON if applicable)."""
        
        try:
            response = ollama.chat(
                model=config.name,
                messages=[{"role": "user", "content": prompt}],
                options=config.to_ollama_options()
            )
            
            result = response['message']['content']
            
            return {
                "result": result,
                "messages": [{"role": "executor", "content": result}],
                "iteration": state["iteration"] + 1
            }
            
        except Exception as e:
            return {"error": f"Executor error: {str(e)}", "done": True}
    
    def _critic_node(self, state: AgentState) -> Dict:
        """Critic agent using Mistral Nemo"""
        config = MODELS[AgentRole.CRITIC]
        
        prompt = f"""You are a critic. Review the execution result and provide feedback.

Plan: {state['plan']}
Result: {state['result']}

Evaluate:
1. Did the execution match the plan?
2. Was the output high quality?
3. Are there errors or improvements needed?

Respond with APPROVE, REVISE, or ESCALATE and explain why."""
        
        try:
            response = ollama.chat(
                model=config.name,
                messages=[{"role": "user", "content": prompt}],
                options=config.to_ollama_options()
            )
            
            critique = response['message']['content']
            
            return {
                "critique": critique,
                "messages": [{"role": "critic", "content": critique}],
                "iteration": state["iteration"] + 1
            }
            
        except Exception as e:
            return {"error": f"Critic error: {str(e)}", "done": True}
    
    def _reflector_node(self, state: AgentState) -> Dict:
        """Reflector agent - post-task analysis (Reflexion pattern)"""
        config = MODELS[AgentRole.REFLECTOR]
        
        prompt = f"""You are a reflection agent. Analyze what was learned from this task.

Task: {state['task']}
Plan: {state['plan']}
Result: {state['result']}
Critique: {state['critique']}

Generate a reflection summary that captures:
1. What worked well
2. What failed or could improve
3. Key lessons to remember for future tasks

This will be stored in episodic memory."""
        
        try:
            response = ollama.chat(
                model=config.name,
                messages=[{"role": "user", "content": prompt}],
                options=config.to_ollama_options()
            )
            
            reflection = response['message']['content']
            
            # Store in episodic memory
            state["memory"].add(
                f"Reflection: {reflection[:300]}",
                MemoryTier.EPISODIC,
                importance=0.8
            )
            
            return {
                "reflection": reflection,
                "messages": [{"role": "reflector", "content": reflection}],
                "done": True
            }
            
        except Exception as e:
            return {"error": f"Reflector error: {str(e)}", "done": True}
    
    def _consolidator_node(self, state: AgentState) -> Dict:
        """Consolidator - memory management"""
        # Run memory consolidation
        state["memory"].consolidate()
        
        # Mark task as complete
        return {"done": True}
    
    def _plan_router(self, state: AgentState) -> str:
        """Route from planner based on output"""
        if state.get("error"):
            return "reflect"
        if state.get("plan"):
            return "execute"
        return "critique"
    
    def _critic_router(self, state: AgentState) -> str:
        """Route from critic based on feedback"""
        critique = state.get("critique", "").upper()
        
        if "APPROVE" in critique:
            return "approve"
        elif "ESCALATE" in critique or state["iteration"] > 5:
            return "escalate"
        else:
            return "revise"
    
    async def execute_task(self, task: str, thread_id: Optional[str] = None) -> Dict:
        """
        Execute a task through the full agent workflow.
        
        Args:
            task: The task description
            thread_id: Optional thread ID for persistence
            
        Returns:
            Final state with results, reflections, and memory updates
        """
        thread_id = thread_id or f"thread_{hashlib.md5(task.encode()).hexdigest()[:8]}"
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            task=task,
            plan=None,
            result=None,
            critique=None,
            reflection=None,
            memory=MemorySystem(),
            iteration=0,
            done=False,
            error=None
        )
        
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        try:
            # Run graph
            result = self.graph.invoke(initial_state, config)
            
            return {
                "success": True,
                "task": task,
                "plan": result.get("plan"),
                "result": result.get("result"),
                "critique": result.get("critique"),
                "reflection": result.get("reflection"),
                "iterations": result.get("iteration", 0),
                "memory_summary": {
                    tier.value: len(entries) 
                    for tier, entries in result["memory"].memories.items()
                }
            }
            
        except GraphRecursionError:
            return {
                "success": False,
                "error": "Maximum iterations exceeded",
                "task": task
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task
            }


# Example usage
async def main():
    """Demonstrate LangGraph orchestrator"""
    print("=" * 60)
    print("ULTRON LangGraph Orchestrator v5.0")
    print("Production-grade stateful agent system")
    print("=" * 60)
    
    if not LANGGRAPH_AVAILABLE or not OLLAMA_AVAILABLE:
        print("\n[ERROR] Required dependencies not installed.")
        print("Run: pip install langgraph ollama")
        return
    
    # Initialize orchestrator
    ultron = ULTRONLangGraph()
    
    # Example task
    task = "Create a Python function to calculate Fibonacci numbers with memoization"
    
    print(f"\nExecuting task: {task}")
    print("-" * 60)
    
    result = await ultron.execute_task(task)
    
    print("\nRESULTS:")
    print("-" * 60)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"\nPlan:\n{result['plan'][:300]}...")
        print(f"\nResult:\n{result['result'][:300]}...")
        print(f"\nReflection:\n{result['reflection'][:300]}...")
        print(f"\nIterations: {result['iterations']}")
        print(f"Memory: {result['memory_summary']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
