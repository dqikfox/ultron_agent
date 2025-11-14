#!/usr/bin/env python3
"""Enhanced autonomous brain for ULTRON Agent with learning and adaptation"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from utils.ultron_logger import log_info, log_ai_decision
from utils.model_awareness import should_modify_file

class AutonomousBrain:
    """Enhanced AI brain with learning, adaptation, and evolution capabilities"""
    
    def __init__(self):
        self.memory = {}
        self.learning_data = []
        self.adaptation_rules = []
        self.evolution_metrics = {}
        
    async def autonomous_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make autonomous decisions based on context and learned patterns"""
        
        log_ai_decision("autonomous_brain", 
                       f"Processing autonomous decision for context: {context.get('type', 'unknown')}")
        
        # Analyze context
        decision_factors = await self._analyze_context(context)
        
        # Apply learned patterns
        learned_insights = await self._apply_learning(decision_factors)
        
        # Generate decision
        decision = {
            "action": await self._select_action(learned_insights),
            "confidence": learned_insights.get("confidence", 0.5),
            "reasoning": learned_insights.get("reasoning", "Based on current analysis"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Learn from this decision
        await self._record_learning(context, decision)
        
        return decision
    
    async def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current context for decision making"""
        
        factors = {
            "urgency": context.get("urgency", "medium"),
            "complexity": len(str(context)),
            "available_tools": context.get("tools", []),
            "user_intent": context.get("intent", "unknown"),
            "system_state": context.get("system_state", "normal")
        }
        
        return factors
    
    async def _apply_learning(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned patterns to current situation"""
        
        # Find similar past situations
        similar_cases = [case for case in self.learning_data 
                        if case.get("factors", {}).get("urgency") == factors.get("urgency")]
        
        if similar_cases:
            # Use learned patterns
            confidence = min(0.9, 0.5 + len(similar_cases) * 0.1)
            reasoning = f"Based on {len(similar_cases)} similar past cases"
        else:
            # New situation - lower confidence
            confidence = 0.3
            reasoning = "New situation - using base analysis"
        
        return {
            "confidence": confidence,
            "reasoning": reasoning,
            "similar_cases": len(similar_cases)
        }
    
    async def _select_action(self, insights: Dict[str, Any]) -> str:
        """Select best action based on insights"""
        
        if insights["confidence"] > 0.7:
            return "execute_with_confidence"
        elif insights["confidence"] > 0.4:
            return "execute_with_caution"
        else:
            return "request_guidance"
    
    async def _record_learning(self, context: Dict[str, Any], decision: Dict[str, Any]):
        """Record this decision for future learning"""
        
        learning_record = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "decision": decision,
            "factors": await self._analyze_context(context)
        }
        
        self.learning_data.append(learning_record)
        
        # Keep only recent learning data (last 1000 records)
        if len(self.learning_data) > 1000:
            self.learning_data = self.learning_data[-1000:]
        
        log_info("autonomous_brain", f"Recorded learning data. Total records: {len(self.learning_data)}")
    
    async def evolve_capabilities(self) -> Dict[str, Any]:
        """Evolve capabilities based on accumulated learning"""
        
        if len(self.learning_data) < 10:
            return {"status": "insufficient_data", "records": len(self.learning_data)}
        
        # Analyze success patterns
        successful_decisions = [record for record in self.learning_data 
                              if record["decision"]["confidence"] > 0.6]
        
        # Update adaptation rules
        if len(successful_decisions) > 5:
            new_rule = {
                "pattern": "high_confidence_decisions",
                "threshold": 0.6,
                "success_rate": len(successful_decisions) / len(self.learning_data),
                "created": datetime.now().isoformat()
            }
            self.adaptation_rules.append(new_rule)
        
        evolution_result = {
            "status": "evolved",
            "new_rules": len(self.adaptation_rules),
            "success_rate": len(successful_decisions) / len(self.learning_data),
            "total_learning_records": len(self.learning_data)
        }
        
        log_ai_decision("autonomous_brain", 
                       f"Evolution completed: {evolution_result['success_rate']:.2%} success rate")
        
        return evolution_result

# Global instance
_autonomous_brain = None

def get_autonomous_brain() -> AutonomousBrain:
    """Get singleton autonomous brain instance"""
    global _autonomous_brain
    if _autonomous_brain is None:
        _autonomous_brain = AutonomousBrain()
    return _autonomous_brain