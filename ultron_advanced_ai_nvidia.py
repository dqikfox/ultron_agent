"""
ULTRON Enhanced AI Implementation with NVIDIA Advisor Improvements
Implementing the AI integration improvements suggested by NVIDIA models
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass, field

# ULTRON imports
from nvidia_nim_router import UltronNvidiaRouter
from ultron_enhanced_ai import UltronEnhancedAI

logger = logging.getLogger(__name__)

@dataclass
class ModelPerformanceMetric:
    """Track performance metrics for adaptive model selection"""
    model_name: str
    accuracy_score: float = 0.0
    latency_ms: float = 0.0
    context_relevance: float = 0.0
    user_satisfaction: float = 0.0
    total_queries: int = 0
    success_rate: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass 
class ContextMemoryNode:
    """Advanced context memory with graph-based relationships"""
    node_id: str
    content: str
    context_type: str
    timestamp: str
    relationships: List[str] = field(default_factory=list)
    importance_score: float = 0.5
    access_count: int = 0

class AdaptiveModelSelector:
    """Implement adaptive model selection based on context and performance"""
    
    def __init__(self):
        """Initialize the adaptive model selector"""
        self.performance_metrics = {}
        self.context_history = []
        self.model_capabilities = {
            "gpt-oss": ["general", "reasoning", "analysis"],
            "llama": ["conversation", "automation", "safety"],
            "qwen2.5-coder:1.5b": ["coding", "technical", "development"]  # Memory optimized
        }
        
    def update_performance(self, model_name: str, latency: float, success: bool, 
                          context_type: str, user_feedback: float = 0.5):
        """Update performance metrics for a model"""
        
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = ModelPerformanceMetric(model_name)
        
        metric = self.performance_metrics[model_name]
        metric.total_queries += 1
        metric.latency_ms = (metric.latency_ms * 0.8) + (latency * 0.2)  # Moving average
        
        if success:
            metric.success_rate = ((metric.success_rate * (metric.total_queries - 1)) + 1.0) / metric.total_queries
        else:
            metric.success_rate = (metric.success_rate * (metric.total_queries - 1)) / metric.total_queries
        
        # Update context relevance based on model capabilities
        if context_type in self.model_capabilities.get(model_name, []):
            metric.context_relevance = min(1.0, metric.context_relevance + 0.1)
        else:
            metric.context_relevance = max(0.0, metric.context_relevance - 0.05)
        
        metric.user_satisfaction = (metric.user_satisfaction * 0.7) + (user_feedback * 0.3)
        metric.last_updated = datetime.now().isoformat()
        
        logger.info(f"Updated metrics for {model_name}: Success={metric.success_rate:.2f}, "
                   f"Latency={metric.latency_ms:.1f}ms, Relevance={metric.context_relevance:.2f}")
    
    def select_best_model(self, query: str, context_type: str = "general") -> str:
        """Select the best model based on current metrics and context"""
        
        if not self.performance_metrics:
            # Default fallback based on context
        context_defaults = {
                "coding": "qwen2.5-coder:1.5b",  # Memory optimized
                "technical": "qwen2.5-coder:1.5b",  # Memory optimized
                "safety": "llama",
                "automation": "llama",
                "general": "llama",  # Changed from gpt-oss due to empty responses
                "conversation": "llama"
            }
            return context_defaults.get(context_type, "llama")
        
        # Calculate weighted scores for each model
        scores = {}
        for model_name, metric in self.performance_metrics.items():
            # Composite score: success_rate * 0.4 + context_relevance * 0.3 + 
            # user_satisfaction * 0.2 + (1 - normalized_latency) * 0.1
            normalized_latency = min(1.0, metric.latency_ms / 5000.0)  # Normalize to 5 second max
            
            score = (
                metric.success_rate * 0.4 +
                metric.context_relevance * 0.3 +
                metric.user_satisfaction * 0.2 +
                (1.0 - normalized_latency) * 0.1
            )
            
            # Boost score if model capabilities match context
            if context_type in self.model_capabilities.get(model_name, []):
                score *= 1.2
            
            scores[model_name] = score
        
        # Select highest scoring model
        best_model = max(scores, key=scores.get)
        logger.info(f"Selected {best_model} for {context_type} context (score: {scores[best_model]:.3f})")
        
        return best_model

class AdvancedContextManager:
    """Enhanced context management with graph-based memory"""
    
    def __init__(self, max_nodes: int = 1000):
        """Initialize the advanced context manager"""
        self.memory_graph = {}
        self.max_nodes = max_nodes
        self.context_embeddings = {}  # Placeholder for embeddings
        
    def add_context_node(self, content: str, context_type: str, 
                        relationships: List[str] = None) -> str:
        """Add a new context node to the memory graph"""
        
        node_id = f"{context_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        node = ContextMemoryNode(
            node_id=node_id,
            content=content,
            context_type=context_type,
            timestamp=datetime.now().isoformat(),
            relationships=relationships or []
        )
        
        self.memory_graph[node_id] = node
        
        # Prune old nodes if we exceed max_nodes
        if len(self.memory_graph) > self.max_nodes:
            self._prune_memory()
        
        logger.info(f"Added context node: {node_id} ({context_type})")
        return node_id
    
    def retrieve_related_context(self, query: str, context_type: str = None, 
                               max_nodes: int = 5) -> List[ContextMemoryNode]:
        """Retrieve related context nodes"""
        
        relevant_nodes = []
        
        for node_id, node in self.memory_graph.items():
            # Simple relevance scoring (could be improved with embeddings)
            relevance_score = 0.0
            
            # Type matching
            if context_type and node.context_type == context_type:
                relevance_score += 0.3
            
            # Content similarity (basic keyword matching)
            query_words = set(query.lower().split())
            content_words = set(node.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            if len(query_words) > 0:
                relevance_score += (overlap / len(query_words)) * 0.4
            
            # Recency bonus
            node_time = datetime.fromisoformat(node.timestamp)
            time_diff = datetime.now() - node_time
            recency_score = max(0, 1.0 - (time_diff.total_seconds() / 86400))  # Decay over 24 hours
            relevance_score += recency_score * 0.2
            
            # Importance and access count
            relevance_score += node.importance_score * 0.1
            
            if relevance_score > 0.2:  # Threshold for relevance
                node.access_count += 1
                relevant_nodes.append((relevance_score, node))
        
        # Sort by relevance and return top nodes
        relevant_nodes.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in relevant_nodes[:max_nodes]]
    
    def _prune_memory(self):
        """Prune old, less important memory nodes"""
        
        nodes_by_importance = sorted(
            self.memory_graph.items(),
            key=lambda x: (x[1].importance_score + x[1].access_count * 0.1),
            reverse=True
        )
        
        # Keep the most important 80% of nodes
        keep_count = int(self.max_nodes * 0.8)
        nodes_to_keep = dict(nodes_by_importance[:keep_count])
        
        removed_count = len(self.memory_graph) - len(nodes_to_keep)
        self.memory_graph = nodes_to_keep
        
        logger.info(f"Pruned {removed_count} memory nodes, kept {len(nodes_to_keep)}")

class UltronAdvancedAI:
    """Advanced AI system implementing NVIDIA model suggestions"""
    
    def __init__(self):
        """Initialize the advanced AI system"""
        self.nvidia_router = UltronNvidiaRouter()
        self.model_selector = AdaptiveModelSelector()
        self.context_manager = AdvancedContextManager()
        self.explanation_mode = True
        self.learning_enabled = True
        
        # Performance tracking
        self.query_history = []
        self.user_feedback_history = []
        
        logger.info("🔴 ULTRON Advanced AI System initialized with NVIDIA improvements")
    
    async def process_query_with_improvements(self, query: str, context_type: str = "general",
                                            require_explanation: bool = False) -> Dict[str, Any]:
        """Process query with all NVIDIA-suggested improvements"""
        
        start_time = time.time()
        
        # 1. Adaptive Model Selection
        selected_model = self.model_selector.select_best_model(query, context_type)
        
        # 2. Enhanced Context Retrieval
        related_context = self.context_manager.retrieve_related_context(query, context_type)
        context_summary = self._generate_context_summary(related_context)
        
        # 3. Prepare Enhanced Query
        enhanced_query = self._enhance_query_with_context(query, context_summary)
        
        # 4. Execute Query with Selected Model
        try:
            self.nvidia_router.route_model(selected_model)
            
            response = await self.nvidia_router.ask_nvidia_async(
                enhanced_query,
                max_tokens=1024,
                temperature=0.7
            )
            
            success = len(response) > 0
            latency = (time.time() - start_time) * 1000
            
        except Exception as e:
            logger.error(f"Error with {selected_model}: {e}")
            # Fallback to working model
            self.nvidia_router.route_model("llama")
            response = await self.nvidia_router.ask_nvidia_async(
                enhanced_query,
                max_tokens=1024,
                temperature=0.7
            )
            success = len(response) > 0
            latency = (time.time() - start_time) * 1000
            selected_model = "llama"
        
        # 5. Generate Explanation (if requested)
        explanation = ""
        if require_explanation and self.explanation_mode:
            explanation = await self._generate_explanation(query, response, selected_model, related_context)
        
        # 6. Update Context Memory
        if success:
            self.context_manager.add_context_node(
                content=f"Q: {query}\nA: {response}",
                context_type=context_type,
                relationships=[node.node_id for node in related_context[:3]]
            )
        
        # 7. Update Performance Metrics
        self.model_selector.update_performance(
            selected_model, latency, success, context_type
        )
        
        # 8. Store Query History for Continuous Learning
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context_type": context_type,
            "selected_model": selected_model,
            "response": response,
            "latency_ms": latency,
            "success": success,
            "context_nodes_used": len(related_context)
        }
        self.query_history.append(query_record)
        
        # Keep only recent history
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-800:]
        
        return {
            "response": response,
            "explanation": explanation,
            "model_used": selected_model,
            "latency_ms": latency,
            "success": success,
            "context_nodes_used": len(related_context),
            "related_context": [node.content[:100] + "..." for node in related_context[:3]]
        }
    
    def _enhance_query_with_context(self, query: str, context_summary: str) -> str:
        """Enhance query with relevant context"""
        
        if not context_summary:
            return query
        
        enhanced = f"""Context from previous interactions:
{context_summary}

Current query: {query}

Please provide a response that takes into account the above context while answering the current query."""
        
        return enhanced
    
    def _generate_context_summary(self, context_nodes: List[ContextMemoryNode]) -> str:
        """Generate a summary of relevant context"""
        
        if not context_nodes:
            return ""
        
        summaries = []
        for node in context_nodes:
            summary = node.content[:200] + "..." if len(node.content) > 200 else node.content
            summaries.append(f"- {summary}")
        
        return "\n".join(summaries)
    
    async def _generate_explanation(self, query: str, response: str, model: str, 
                                  context: List[ContextMemoryNode]) -> str:
        """Generate explanation for the AI's decision-making process"""
        
        explanation_query = f"""Please explain the reasoning behind this response:

Query: {query}
Response: {response[:300]}...
Model Used: {model}
Context Nodes: {len(context)}

Provide a brief explanation of:
1. Why this response was appropriate
2. How the model selection was optimal
3. What context influenced the response
"""
        
        try:
            # Use Llama for explanations (most reliable)
            self.nvidia_router.route_model("llama")
            explanation = await self.nvidia_router.ask_nvidia_async(
                explanation_query,
                max_tokens=400,
                temperature=0.3
            )
            return explanation
        except Exception as e:
            return f"Explanation generation failed: {str(e)}"
    
    def provide_feedback(self, query_index: int, satisfaction_score: float, 
                        feedback_text: str = ""):
        """Allow users to provide feedback for continuous learning"""
        
        if 0 <= query_index < len(self.query_history):
            query_record = self.query_history[query_index]
            
            # Update model performance with feedback
            self.model_selector.update_performance(
                query_record["selected_model"],
                query_record["latency_ms"],
                query_record["success"],
                query_record["context_type"],
                satisfaction_score
            )
            
            # Store feedback for future analysis
            feedback_record = {
                "timestamp": datetime.now().isoformat(),
                "query_index": query_index,
                "satisfaction_score": satisfaction_score,
                "feedback_text": feedback_text,
                "query": query_record["query"],
                "model": query_record["selected_model"]
            }
            self.user_feedback_history.append(feedback_record)
            
            logger.info(f"Received feedback: {satisfaction_score}/1.0 for {query_record['selected_model']}")
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        
        analytics = {
            "total_queries": len(self.query_history),
            "model_performance": {},
            "context_memory_size": len(self.context_manager.memory_graph),
            "average_latency": 0.0,
            "success_rate": 0.0,
            "feedback_count": len(self.user_feedback_history)
        }
        
        if self.query_history:
            analytics["average_latency"] = sum(q["latency_ms"] for q in self.query_history) / len(self.query_history)
            analytics["success_rate"] = sum(1 for q in self.query_history if q["success"]) / len(self.query_history)
        
        # Model performance breakdown
        for model_name, metric in self.model_selector.performance_metrics.items():
            analytics["model_performance"][model_name] = {
                "success_rate": metric.success_rate,
                "avg_latency_ms": metric.latency_ms,
                "context_relevance": metric.context_relevance,
                "user_satisfaction": metric.user_satisfaction,
                "total_queries": metric.total_queries
            }
        
        return analytics


# Demo and Testing Functions
async def demo_advanced_ai():
    """Demonstrate the advanced AI system"""
    
    print("🔴 ULTRON ADVANCED AI DEMO - NVIDIA IMPROVEMENTS IMPLEMENTED 🔴")
    print("=" * 70)
    
    ai_system = UltronAdvancedAI()
    
    # Test queries
    test_queries = [
        ("What safety precautions should ULTRON have for automation?", "safety"),
        ("How can I improve the GUI accessibility?", "accessibility"),
        ("Write a Python function to check system status", "coding"),
        ("Explain how voice recognition works in ULTRON", "technical"),
        ("What's the best way to handle user feedback?", "general")
    ]
    
    print("🧪 Testing Adaptive Model Selection and Context Management...\n")
    
    for i, (query, context_type) in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print(f"Context: {context_type}")
        print("-" * 50)
        
        result = await ai_system.process_query_with_improvements(
            query, 
            context_type, 
            require_explanation=True
        )
        
        print(f"Model Selected: {result['model_used']}")
        print(f"Response Length: {len(result['response'])} characters")
        print(f"Latency: {result['latency_ms']:.1f}ms")
        print(f"Success: {'✅' if result['success'] else '❌'}")
        print(f"Context Nodes Used: {result['context_nodes_used']}")
        
        if result['response']:
            print(f"Response Preview: {result['response'][:200]}...")
        
        if result['explanation']:
            print(f"AI Explanation: {result['explanation'][:150]}...")
        
        print("=" * 70)
        
        # Simulate user feedback
        feedback_score = 0.8 if result['success'] else 0.2
        ai_system.provide_feedback(i-1, feedback_score, "Demo feedback")
        
        await asyncio.sleep(1)  # Brief pause between queries
    
    # Show analytics
    print("\n📊 SYSTEM ANALYTICS AFTER DEMO:")
    print("-" * 50)
    analytics = ai_system.get_system_analytics()
    
    print(f"Total Queries: {analytics['total_queries']}")
    print(f"Average Latency: {analytics['average_latency']:.1f}ms")
    print(f"Success Rate: {analytics['success_rate']:.1%}")
    print(f"Context Memory Size: {analytics['context_memory_size']}")
    print(f"Feedback Count: {analytics['feedback_count']}")
    
    print("\n🤖 MODEL PERFORMANCE BREAKDOWN:")
    for model, perf in analytics['model_performance'].items():
        print(f"  {model.upper()}:")
        print(f"    Success Rate: {perf['success_rate']:.1%}")
        print(f"    Avg Latency: {perf['avg_latency_ms']:.1f}ms")
        print(f"    User Satisfaction: {perf['user_satisfaction']:.2f}/1.0")
        print(f"    Total Queries: {perf['total_queries']}")
    
    print("\n🎉 NVIDIA IMPROVEMENT IMPLEMENTATION COMPLETE!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_advanced_ai())
