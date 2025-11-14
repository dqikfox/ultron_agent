"""
Enhanced Voice Integration Tool
Improved natural language processing and voice command handling.
"""

import asyncio
import json
from typing import Dict, List, Optional
from utils.ultron_logger import log_info, log_error


class EnhancedVoiceTool:
    """Enhanced voice processing with context awareness"""
    
    name = "enhanced_voice"
    description = "Advanced voice command processing with context"
    
    def __init__(self):
        self.conversation_context = []
        self.voice_patterns = self._load_voice_patterns()
    
    def match(self, command: str) -> bool:
        """Match voice-related commands"""
        return any(word in command.lower() for word in ["voice", "speak", "listen", "say"])
    
    async def execute(self, command: str, **kwargs) -> str:
        """Execute enhanced voice processing"""
        try:
            # Context-aware processing
            context = self._analyze_context(command)
            
            # Intent classification
            intent = self._classify_intent(command, context)
            
            # Execute with voice feedback
            result = await self._execute_with_voice(intent, command)
            
            # Update conversation context
            self._update_context(command, result)
            
            return result
            
        except Exception as e:
            log_error("enhanced_voice", f"Voice processing failed: {str(e)}")
            return f"Voice error: {str(e)}"
    
    def _load_voice_patterns(self) -> Dict:
        """Load enhanced voice command patterns"""
        return {
            "system_control": {
                "patterns": ["open", "launch", "start", "close", "kill"],
                "confidence_boost": 0.2
            },
            "information_query": {
                "patterns": ["what", "how", "when", "where", "show me"],
                "confidence_boost": 0.15
            },
            "automation": {
                "patterns": ["automate", "schedule", "remind", "monitor"],
                "confidence_boost": 0.25
            },
            "contextual": {
                "patterns": ["yesterday", "recent", "last", "previous"],
                "confidence_boost": 0.3
            }
        }
    
    def _analyze_context(self, command: str) -> Dict:
        """Analyze conversation context for better understanding"""
        return {
            "recent_commands": self.conversation_context[-3:],
            "temporal_references": self._extract_temporal_refs(command),
            "entity_mentions": self._extract_entities(command),
            "confidence_factors": self._calculate_confidence(command)
        }
    
    def _classify_intent(self, command: str, context: Dict) -> Dict:
        """Enhanced intent classification with context"""
        base_confidence = 0.5
        
        for category, config in self.voice_patterns.items():
            if any(pattern in command.lower() for pattern in config["patterns"]):
                base_confidence += config["confidence_boost"]
        
        # Context boost
        if context["temporal_references"]:
            base_confidence += 0.2
        
        return {
            "primary_intent": self._determine_primary_intent(command),
            "confidence": min(base_confidence, 1.0),
            "context_enhanced": True
        }
    
    async def _execute_with_voice(self, intent: Dict, command: str) -> str:
        """Execute command with voice feedback"""
        from voice_manager import get_voice_manager
        
        voice_manager = get_voice_manager()
        
        # Provide immediate voice acknowledgment
        await voice_manager.speak("Processing your request", async_mode=True)
        
        # Execute the actual command
        result = await self._process_command(intent, command)
        
        # Provide voice feedback on result
        feedback = self._generate_voice_feedback(result)
        await voice_manager.speak(feedback, async_mode=True)
        
        return result
    
    def _extract_temporal_refs(self, command: str) -> List[str]:
        """Extract temporal references for context"""
        temporal_words = ["yesterday", "today", "tomorrow", "last", "recent", "previous", "next"]
        return [word for word in temporal_words if word in command.lower()]
    
    def _extract_entities(self, command: str) -> List[str]:
        """Extract entities mentioned in command"""
        entities = ["chrome", "notepad", "calculator", "file", "email", "car", "search"]
        return [entity for entity in entities if entity in command.lower()]
    
    @staticmethod
    def schema():
        return {
            "name": "enhanced_voice",
            "description": "Advanced voice command processing with context",
            "parameters": {
                "command": {"type": "string", "description": "Voice command to process"}
            }
        }