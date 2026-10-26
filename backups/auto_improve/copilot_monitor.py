#!/usr/bin/env python3
"""
Copilot Monitor - Track GitHub Copilot actions and provide assistance
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class CopilotMonitor:
    """Monitor GitHub Copilot actions and provide assistance"""
    
    def __init__(self):
        self.log_file = Path("copilot_actions.log")
        self.suggestions_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.current_session = {
            "start_time": datetime.now(),
            "suggestions": [],
            "patterns": {}
        }
        
    def log_suggestion(self, suggestion: Dict[str, Any]):
        """Log a Copilot suggestion"""
        self.suggestions_count += 1
        suggestion["timestamp"] = datetime.now().isoformat()
        suggestion["id"] = self.suggestions_count
        
        self.current_session["suggestions"].append(suggestion)
        
        # Log to file
        with open(self.log_file, "a") as f:
            f.write(f"{json.dumps(suggestion)}\n")
    
    def log_acceptance(self, suggestion_id: int):
        """Log suggestion acceptance"""
        self.accepted_count += 1
        self._update_suggestion_status(suggestion_id, "accepted")
        
    def log_rejection(self, suggestion_id: int):
        """Log suggestion rejection"""
        self.rejected_count += 1
        self._update_suggestion_status(suggestion_id, "rejected")
    
    def _update_suggestion_status(self, suggestion_id: int, status: str):
        """Update suggestion status"""
        for suggestion in self.current_session["suggestions"]:
            if suggestion.get("id") == suggestion_id:
                suggestion["status"] = status
                break
    
    def get_advice(self) -> List[str]:
        """Get advice based on Copilot usage patterns"""
        advice = []
        
        if self.suggestions_count == 0:
            advice.append("💡 Try typing comments to get Copilot suggestions")
            advice.append("🔧 Use Ctrl+I for inline chat with Copilot")
            return advice
        
        acceptance_rate = self.accepted_count / self.suggestions_count if self.suggestions_count > 0 else 0
        
        if acceptance_rate < 0.3:
            advice.append("🎯 Low acceptance rate - try more specific comments")
            advice.append("📝 Write clearer function names and docstrings")
        
        if acceptance_rate > 0.8:
            advice.append("✨ Great Copilot usage! High acceptance rate")
            advice.append("🚀 Try using Copilot Chat for complex problems")
        
        recent_suggestions = self.current_session["suggestions"][-5:]
        languages = set(s.get("language", "unknown") for s in recent_suggestions)
        
        if len(languages) > 1:
            advice.append(f"🔄 Working with {len(languages)} languages: {', '.join(languages)}")
        
        return advice
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            "session_duration": str(datetime.now() - self.current_session["start_time"]),
            "total_suggestions": self.suggestions_count,
            "accepted": self.accepted_count,
            "rejected": self.rejected_count,
            "acceptance_rate": f"{(self.accepted_count / max(1, self.suggestions_count)) * 100:.1f}%",
            "advice": self.get_advice()
        }

# Global monitor instance
copilot_monitor = CopilotMonitor()

def track_copilot_action(action_type: str, data: Dict[str, Any] = None):
    """Track a Copilot action"""
    if data is None:
        data = {}
    
    action = {
        "type": action_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    if action_type == "suggestion":
        copilot_monitor.log_suggestion(data)
    elif action_type == "accepted":
        copilot_monitor.log_acceptance(data.get("suggestion_id", 0))
    elif action_type == "rejected":
        copilot_monitor.log_rejection(data.get("suggestion_id", 0))

def get_copilot_advice() -> Dict[str, Any]:
    """Get current Copilot advice and stats"""
    return copilot_monitor.get_stats()

if __name__ == "__main__":
    # Example usage
    print("Copilot Monitor Started")
    print(json.dumps(get_copilot_advice(), indent=2))