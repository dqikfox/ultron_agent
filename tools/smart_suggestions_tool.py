"""
Smart Suggestions Tool - AI-powered contextual recommendations
Learns from user behavior and provides intelligent suggestions
"""

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from datetime import datetime
from pathlib import Path
import json
from collections import Counter
from typing import List, Dict, Any


class SmartSuggestionsTool(ToolInterface):
    """Intelligent suggestion system that learns from user patterns"""
    
    def __init__(self):
        self.usage_history_file = Path(__file__).parent.parent / "metrics" / "usage_history.json"
        self.suggestions_cache = []
        self.user_patterns = {}
        self._load_usage_history()
    
    @property
    def name(self) -> str:
        return "Smart Suggestions"
    
    @property
    def description(self) -> str:
        return "Provides intelligent, context-aware suggestions based on user behavior patterns and AI analysis"
    
    def match(self, command: str) -> bool:
        """Check if command requests suggestions"""
        keywords = [
            "suggest", "suggestion", "recommend", "what can", 
            "what should", "help me", "ideas", "tips",
            "next", "improve", "optimize", "better way"
        ]
        cmd_lower = command.lower()
        return any(keyword in cmd_lower for keyword in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Generate intelligent suggestions based on context"""
        log_info("smart_suggestions", f"Generating suggestions for: {command}")
        
        try:
            # Determine context
            context = self._determine_context(command, kwargs)
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(context, command)
            
            # Learn from this interaction
            self._record_usage(command, context)
            
            # Format response
            response = self._format_suggestions(suggestions, context)
            
            log_ai_decision(
                "smart_suggestions",
                f"Generated {len(suggestions)} suggestions",
                ai_model="pattern_analysis",
                confidence_score=0.85
            )
            
            return response
            
        except Exception as e:
            log_error("smart_suggestions", f"Error generating suggestions: {e}")
            return f"❌ Failed to generate suggestions: {str(e)}"
    
    def _determine_context(self, command: str, kwargs: Dict) -> str:
        """Determine the context of the request"""
        cmd_lower = command.lower()
        
        # Check for specific contexts
        if any(word in cmd_lower for word in ["code", "program", "function", "class"]):
            return "coding"
        elif any(word in cmd_lower for word in ["file", "folder", "directory", "organize"]):
            return "file_management"
        elif any(word in cmd_lower for word in ["system", "performance", "speed", "optimize"]):
            return "system_optimization"
        elif any(word in cmd_lower for word in ["learn", "tutorial", "how to", "guide"]):
            return "learning"
        elif any(word in cmd_lower for word in ["automate", "task", "workflow", "batch"]):
            return "automation"
        elif any(word in cmd_lower for word in ["search", "find", "locate", "lookup"]):
            return "search"
        else:
            return "general"
    
    def _generate_suggestions(self, context: str, command: str) -> List[Dict[str, Any]]:
        """Generate context-aware suggestions"""
        suggestions = []
        
        # Context-specific suggestions
        if context == "coding":
            suggestions.extend([
                {
                    "title": "Code Review",
                    "description": "Review your code for best practices and potential issues",
                    "command": "review my code",
                    "priority": "high"
                },
                {
                    "title": "Add Error Handling",
                    "description": "Implement try-except blocks for robust error handling",
                    "command": "add error handling to my code",
                    "priority": "high"
                },
                {
                    "title": "Write Unit Tests",
                    "description": "Generate unit tests for your functions",
                    "command": "create unit tests",
                    "priority": "medium"
                },
                {
                    "title": "Optimize Performance",
                    "description": "Analyze and optimize code performance",
                    "command": "optimize my code",
                    "priority": "medium"
                }
            ])
        
        elif context == "file_management":
            suggestions.extend([
                {
                    "title": "Organize by Type",
                    "description": "Sort files into folders by file extension",
                    "command": "organize files by type",
                    "priority": "high"
                },
                {
                    "title": "Find Duplicates",
                    "description": "Locate and remove duplicate files",
                    "command": "find duplicate files",
                    "priority": "medium"
                },
                {
                    "title": "Clean Temp Files",
                    "description": "Remove temporary and cache files",
                    "command": "clean temporary files",
                    "priority": "low"
                }
            ])
        
        elif context == "system_optimization":
            suggestions.extend([
                {
                    "title": "Check System Health",
                    "description": "Run comprehensive system diagnostics",
                    "command": "check system health",
                    "priority": "high"
                },
                {
                    "title": "Monitor Resources",
                    "description": "Track CPU, memory, and disk usage",
                    "command": "monitor system resources",
                    "priority": "high"
                },
                {
                    "title": "Update Software",
                    "description": "Check for and install software updates",
                    "command": "update all software",
                    "priority": "medium"
                }
            ])
        
        elif context == "automation":
            suggestions.extend([
                {
                    "title": "Create Scheduled Task",
                    "description": "Set up recurring automated tasks",
                    "command": "create scheduled task",
                    "priority": "high"
                },
                {
                    "title": "Batch Processing",
                    "description": "Process multiple files at once",
                    "command": "batch process files",
                    "priority": "medium"
                },
                {
                    "title": "Workflow Automation",
                    "description": "Automate multi-step workflows",
                    "command": "create workflow automation",
                    "priority": "medium"
                }
            ])
        
        # Add pattern-based suggestions from usage history
        pattern_suggestions = self._get_pattern_based_suggestions(command)
        suggestions.extend(pattern_suggestions)
        
        # Add trending suggestions
        trending = self._get_trending_suggestions()
        suggestions.extend(trending)
        
        # Rank and return top suggestions
        ranked = self._rank_suggestions(suggestions, context)
        return ranked[:8]  # Return top 8 suggestions
    
    def _get_pattern_based_suggestions(self, command: str) -> List[Dict[str, Any]]:
        """Generate suggestions based on user's past behavior"""
        suggestions = []
        
        if not self.user_patterns:
            return suggestions
        
        # Find similar past commands
        cmd_words = set(command.lower().split())
        similar_commands = []
        
        for past_cmd, count in self.user_patterns.get('frequent_commands', {}).items():
            past_words = set(past_cmd.lower().split())
            similarity = len(cmd_words & past_words) / len(cmd_words | past_words) if cmd_words | past_words else 0
            
            if similarity > 0.3:  # 30% similarity threshold
                similar_commands.append((past_cmd, count, similarity))
        
        # Sort by frequency and similarity
        similar_commands.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Add top similar commands as suggestions
        for past_cmd, count, similarity in similar_commands[:3]:
            suggestions.append({
                "title": "You've Used This Before",
                "description": f"You've used this {count} times",
                "command": past_cmd,
                "priority": "high",
                "confidence": similarity
            })
        
        return suggestions
    
    def _get_trending_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for trending/popular features"""
        trending = [
            {
                "title": "Evolution Framework",
                "description": "Run automated code improvement scan",
                "command": "python self_improvement.py --scan",
                "priority": "medium",
                "category": "trending"
            },
            {
                "title": "View Improvement Suggestions",
                "description": "See what can be enhanced in your codebase",
                "command": "python view_suggestions.py",
                "priority": "medium",
                "category": "trending"
            },
            {
                "title": "Voice Control",
                "description": "Enable hands-free voice commands",
                "command": "enable voice mode",
                "priority": "low",
                "category": "trending"
            }
        ]
        return trending[:2]  # Return top 2 trending
    
    def _rank_suggestions(self, suggestions: List[Dict], context: str) -> List[Dict]:
        """Rank suggestions by relevance and priority"""
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        
        for suggestion in suggestions:
            score = priority_scores.get(suggestion.get("priority", "low"), 1)
            
            # Boost score based on confidence if present
            if "confidence" in suggestion:
                score *= (1 + suggestion["confidence"])
            
            suggestion["score"] = score
        
        # Sort by score (descending)
        suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
        return suggestions
    
    def _format_suggestions(self, suggestions: List[Dict], context: str) -> str:
        """Format suggestions for display"""
        if not suggestions:
            return "💡 No specific suggestions available. How can I help you?"
        
        response = [f"💡 **Smart Suggestions for {context.replace('_', ' ').title()}**\n"]
        
        for i, suggestion in enumerate(suggestions, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                suggestion.get("priority", "low"), "⚪"
            )
            
            response.append(f"{i}. {priority_icon} **{suggestion['title']}**")
            response.append(f"   {suggestion['description']}")
            response.append(f"   💬 Try: `{suggestion['command']}`")
            response.append("")
        
        response.append("📊 **Pro Tip:** These suggestions learn from your usage patterns!")
        return "\n".join(response)
    
    def _record_usage(self, command: str, context: str):
        """Record command usage for learning"""
        try:
            # Load existing history
            history = []
            if self.usage_history_file.exists():
                with open(self.usage_history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new entry
            history.append({
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "context": context
            })
            
            # Keep last 1000 entries
            history = history[-1000:]
            
            # Save updated history
            self.usage_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.usage_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            # Update patterns
            self._analyze_patterns(history)
            
        except Exception as e:
            log_error("smart_suggestions", f"Failed to record usage: {e}")
    
    def _load_usage_history(self):
        """Load usage history on initialization"""
        try:
            if self.usage_history_file.exists():
                with open(self.usage_history_file, 'r') as f:
                    history = json.load(f)
                self._analyze_patterns(history)
        except Exception as e:
            log_error("smart_suggestions", f"Failed to load usage history: {e}")
    
    def _analyze_patterns(self, history: List[Dict]):
        """Analyze usage patterns from history"""
        try:
            # Count command frequencies
            commands = [entry['command'] for entry in history]
            command_freq = Counter(commands)
            
            # Count context frequencies
            contexts = [entry['context'] for entry in history]
            context_freq = Counter(contexts)
            
            # Store patterns
            self.user_patterns = {
                "frequent_commands": dict(command_freq.most_common(20)),
                "frequent_contexts": dict(context_freq.most_common(10)),
                "total_commands": len(history)
            }
            
        except Exception as e:
            log_error("smart_suggestions", f"Failed to analyze patterns: {e}")
    
    @classmethod
    def schema(cls) -> dict:
        """Return tool schema for OpenAI-compatible function calling"""
        return {
            "name": "smart_suggestions",
            "description": "Get intelligent, context-aware suggestions based on user behavior patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The user's query or request for suggestions"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context (coding, file_management, system_optimization, etc.)",
                        "enum": ["coding", "file_management", "system_optimization", "learning", "automation", "search", "general"]
                    }
                },
                "required": ["command"]
            }
        }
