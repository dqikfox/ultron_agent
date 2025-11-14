"""
Voice Integration Improvements for ULTRON Agent
Enhanced voice processing with context awareness and better natural language understanding.
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple
from utils.ultron_logger import log_info, log_error


class VoiceImprovements:
    """Voice system enhancements for ULTRON Agent"""
    
    def __init__(self):
        self.conversation_history = []
        self.context_memory = {}
        self.voice_patterns = self._init_voice_patterns()
    
    def _init_voice_patterns(self) -> Dict:
        """Initialize enhanced voice command patterns"""
        return {
            "wake_words": ["hey ultron", "ultron", "computer"],
            "system_commands": {
                "open": ["launch", "start", "run", "execute"],
                "close": ["kill", "stop", "terminate", "end"],
                "search": ["find", "look for", "locate", "get"]
            },
            "contextual_phrases": {
                "temporal": ["yesterday", "today", "last time", "recently", "before"],
                "referential": ["that thing", "the one", "it", "this", "what we"]
            },
            "confirmation_phrases": ["yes", "okay", "sure", "go ahead", "do it"],
            "cancellation_phrases": ["no", "cancel", "stop", "never mind", "abort"]
        }
    
    async def process_enhanced_voice_command(self, raw_audio: bytes, context: Dict = None) -> Dict:
        """Process voice command with enhanced understanding"""
        try:
            # Step 1: Speech-to-text with multiple engines
            transcription = await self._multi_engine_stt(raw_audio)
            
            # Step 2: Context-aware preprocessing
            processed_text = self._preprocess_with_context(transcription, context)
            
            # Step 3: Intent classification with confidence scoring
            intent = await self._classify_intent_enhanced(processed_text)
            
            # Step 4: Execute with voice feedback
            result = await self._execute_with_feedback(intent, processed_text)
            
            # Step 5: Update conversation memory
            self._update_conversation_memory(processed_text, result)
            
            return {
                "transcription": transcription,
                "processed_text": processed_text,
                "intent": intent,
                "result": result,
                "confidence": intent.get("confidence", 0.0)
            }
            
        except Exception as e:
            log_error("voice_improvements", f"Enhanced processing failed: {str(e)}")
            return {"error": str(e)}
    
    async def _multi_engine_stt(self, audio: bytes) -> str:
        """Multi-engine speech-to-text with fallback"""
        engines = ["elevenlabs", "whisper", "azure_speech", "web_speech"]
        
        for engine in engines:
            try:
                result = await self._stt_engine(engine, audio)
                if result and len(result.strip()) > 0:
                    log_info("voice_improvements", f"STT success with {engine}")
                    return result
            except Exception as e:
                log_error("voice_improvements", f"STT engine {engine} failed: {str(e)}")
                continue
        
        return ""
    
    def _preprocess_with_context(self, text: str, context: Dict = None) -> str:
        """Preprocess text with conversation context"""
        if not text:
            return text
        
        # Resolve pronouns and references
        text = self._resolve_references(text)
        
        # Expand contractions and normalize
        text = self._normalize_text(text)
        
        # Add context from recent conversation
        if context and "recent_topics" in context:
            text = self._add_contextual_hints(text, context["recent_topics"])
        
        return text
    
    def _resolve_references(self, text: str) -> str:
        """Resolve pronouns and contextual references"""
        # Simple reference resolution
        if "that thing" in text.lower() and self.conversation_history:
            last_entity = self._extract_last_entity()
            if last_entity:
                text = text.replace("that thing", last_entity)
        
        if "it" in text.lower() and len(text.split()) < 5:
            # Short command with "it" - likely refers to last mentioned item
            last_entity = self._extract_last_entity()
            if last_entity:
                text = text.replace("it", last_entity)
        
        return text
    
    async def _classify_intent_enhanced(self, text: str) -> Dict:
        """Enhanced intent classification with confidence scoring"""
        intents = {
            "system_control": 0.0,
            "information_query": 0.0,
            "automation": 0.0,
            "conversation": 0.0
        }
        
        # Pattern matching with confidence scoring
        for intent_type, patterns in self.voice_patterns["system_commands"].items():
            if any(pattern in text.lower() for pattern in patterns):
                intents["system_control"] += 0.3
        
        # Contextual boosting
        if any(phrase in text.lower() for phrase in self.voice_patterns["contextual_phrases"]["temporal"]):
            intents["information_query"] += 0.2
        
        # Determine primary intent
        primary_intent = max(intents, key=intents.get)
        confidence = intents[primary_intent]
        
        return {
            "primary": primary_intent,
            "confidence": confidence,
            "all_scores": intents,
            "requires_confirmation": confidence < 0.5
        }
    
    async def _execute_with_feedback(self, intent: Dict, text: str) -> str:
        """Execute command with intelligent voice feedback"""
        from voice_manager import get_voice_manager
        
        voice_manager = get_voice_manager()
        
        # Provide contextual acknowledgment
        if intent["requires_confirmation"]:
            confirmation = f"I think you want to {intent['primary']}. Is that correct?"
            await voice_manager.speak(confirmation, async_mode=True)
            # Wait for confirmation (simplified)
            return "Awaiting confirmation"
        
        # Execute command
        try:
            result = await self._route_command(intent, text)
            
            # Provide intelligent feedback
            feedback = self._generate_smart_feedback(result, intent)
            await voice_manager.speak(feedback, async_mode=True)
            
            return result
            
        except Exception as e:
            error_feedback = f"I encountered an error: {str(e)}"
            await voice_manager.speak(error_feedback, async_mode=True)
            return f"Error: {str(e)}"
    
    def _generate_smart_feedback(self, result: str, intent: Dict) -> str:
        """Generate contextually appropriate voice feedback"""
        if intent["primary"] == "system_control":
            if "opened" in result.lower():
                return "Application launched successfully"
            elif "closed" in result.lower():
                return "Application closed"
            else:
                return "Command executed"
        
        elif intent["primary"] == "information_query":
            if len(result) > 100:
                return "I found the information you requested"
            else:
                return result
        
        else:
            return "Task completed"
    
    def _update_conversation_memory(self, command: str, result: str):
        """Update conversation memory for context"""
        self.conversation_history.append({
            "command": command,
            "result": result,
            "timestamp": asyncio.get_event_loop().time(),
            "entities": self._extract_entities(command)
        })
        
        # Keep only last 10 interactions
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text for context"""
        entities = []
        common_entities = ["chrome", "notepad", "calculator", "file", "email", "car", "search", "music"]
        
        for entity in common_entities:
            if entity in text.lower():
                entities.append(entity)
        
        return entities
    
    def _extract_last_entity(self) -> Optional[str]:
        """Extract the most recent entity from conversation history"""
        for interaction in reversed(self.conversation_history):
            if interaction["entities"]:
                return interaction["entities"][-1]
        return None
    
    async def _route_command(self, intent: Dict, text: str) -> str:
        """Route command to appropriate handler"""
        # This would integrate with existing ULTRON tools
        if intent["primary"] == "system_control":
            from tools.windows_system_tool import WindowsSystemTool
            tool = WindowsSystemTool()
            return tool.execute(text)
        
        # Add other routing logic
        return f"Processed: {text}"
    
    def get_voice_improvements_summary(self) -> Dict:
        """Get summary of voice improvements"""
        return {
            "enhancements": [
                "Multi-engine STT with fallback chain",
                "Context-aware command preprocessing", 
                "Enhanced intent classification with confidence scoring",
                "Conversation memory and reference resolution",
                "Intelligent voice feedback generation",
                "Confirmation dialogs for low-confidence commands"
            ],
            "configuration": {
                "wake_words": self.voice_patterns["wake_words"],
                "supported_engines": ["elevenlabs", "whisper", "azure_speech", "web_speech"],
                "context_memory_size": len(self.conversation_history),
                "confidence_threshold": 0.5
            },
            "integration_points": [
                "Enhanced GUI voice controls",
                "Natural language system commands",
                "Contextual browser automation",
                "Memory-aware conversations"
            ]
        }


# Integration with existing voice system
async def integrate_voice_improvements():
    """Integrate voice improvements with existing ULTRON voice system"""
    improvements = VoiceImprovements()
    
    # Example integration
    sample_command = "hey ultron open chrome and search for that car thing we looked at yesterday"
    
    # Process with enhancements
    result = await improvements.process_enhanced_voice_command(
        raw_audio=b"",  # Would be actual audio bytes
        context={"recent_topics": ["cars", "automotive", "vehicles"]}
    )
    
    log_info("voice_integration", f"Enhanced processing result: {result}")
    
    return improvements.get_voice_improvements_summary()


if __name__ == "__main__":
    # Test voice improvements
    asyncio.run(integrate_voice_improvements())