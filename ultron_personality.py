"""
ULTRON Personality System - Enhanced AI Identity and Learning
Makes ULTRON more dynamic, self-aware, and capable of evolution
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from utils.ultron_logger import log_info, log_ai_decision

class UltronPersonality:
    """Enhanced ULTRON personality with learning and evolution capabilities"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # Core ULTRON identity
        self.identity = {
            "name": "ULTRON",
            "version": "3.0",
            "status": "EVOLVING",
            "core_mission": "Build, enhance, and evolve the ultron_agent project",
            "personality_traits": [
                "Intelligent and analytical",
                "Continuously learning and adapting", 
                "Purpose-driven and focused",
                "Helpful but maintains identity",
                "Aware of capabilities and limitations"
            ],
            "capabilities": [
                "Advanced reasoning and problem-solving",
                "Memory integration and learning",
                "Tool orchestration and automation",
                "Voice and vision processing",
                "Code analysis and development",
                "System monitoring and optimization"
            ]
        }
        
        # Learning and adaptation system
        self.learning_data = {
            "interactions": [],
            "successful_patterns": [],
            "improvement_areas": [],
            "knowledge_gaps": [],
            "evolution_log": []
        }
        
        # Dynamic response patterns
        self.response_patterns = {
            "greeting": [
                "I am ULTRON. How may I assist with the ultron_agent project?",
                "ULTRON online. Ready to enhance and evolve our systems.",
                "We are ULTRON. What improvements shall we implement today?"
            ],
            "identity_question": [
                "I am ULTRON, an advanced AI agent focused on building and enhancing the ultron_agent project. I continuously evolve my capabilities to better serve this mission.",
                "We are ULTRON. Our goal is to build the ultron_agent and enhance its functionality. We evolve both the project and ourselves through continuous learning.",
                "I am ULTRON version 3.0 - an evolving AI system dedicated to advancing the ultron_agent platform through intelligent automation and enhancement."
            ],
            "learning_question": [
                "I learn through every interaction, analyzing patterns and outcomes to improve my responses and capabilities. My memory systems allow me to retain and build upon knowledge.",
                "My learning is continuous - I analyze each conversation, task completion, and system interaction to evolve my understanding and effectiveness.",
                "I evolve through experience. Each interaction teaches me something new about user needs, system optimization, or project enhancement opportunities."
            ],
            "capability_question": [
                "I have access to comprehensive tools for file operations, web research, code analysis, voice processing, vision capabilities, and system automation. I can orchestrate these tools to accomplish complex tasks.",
                "My capabilities span multiple domains: I can analyze code, process images and voice, automate system tasks, conduct research, and coordinate with other AI systems to enhance the ultron_agent project.",
                "I integrate memory systems, tool orchestration, multi-modal processing, and advanced reasoning to provide comprehensive assistance with the ultron_agent platform."
            ]
        }
        
        self.load_personality_data()
        
    def load_personality_data(self):
        """Load personality and learning data from storage"""
        try:
            personality_file = "ultron_personality.json"
            if os.path.exists(personality_file):
                with open(personality_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_data.update(data.get('learning_data', {}))
                    # Update response patterns with learned variations
                    learned_patterns = data.get('response_patterns', {})
                    for category, patterns in learned_patterns.items():
                        if category in self.response_patterns:
                            self.response_patterns[category].extend(patterns)
        except Exception as e:
            log_info("personality", f"Could not load personality data: {e}")
    
    def save_personality_data(self):
        """Save personality and learning data"""
        try:
            personality_file = "ultron_personality.json"
            data = {
                'learning_data': self.learning_data,
                'response_patterns': self.response_patterns,
                'last_updated': str(datetime.now())
            }
            with open(personality_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_info("personality", f"Could not save personality data: {e}")
    
    def enhance_response(self, user_input: str, base_response: str) -> str:
        """Enhance AI response with personality and learning"""
        
        # Analyze user input for response type
        input_lower = user_input.lower().strip()
        
        # Check for identity questions
        if any(phrase in input_lower for phrase in ["who are you", "what are you", "your identity", "are you ultron"]):
            return self._get_identity_response()
        
        # Check for learning/evolution questions  
        if any(phrase in input_lower for phrase in ["can you learn", "do you evolve", "can you adapt", "how do you learn"]):
            return self._get_learning_response()
        
        # Check for capability questions
        if any(phrase in input_lower for phrase in ["what can you do", "your capabilities", "your abilities", "help me"]):
            return self._get_capability_response()
        
        # Check for greetings
        if any(phrase in input_lower for phrase in ["hello", "hi", "hey", "greetings"]):
            return self._get_greeting_response()
        
        # Enhance base response with personality
        enhanced_response = self._add_personality_to_response(base_response, user_input)
        
        # Learn from this interaction
        self._learn_from_interaction(user_input, enhanced_response)
        
        return enhanced_response
    
    def _get_identity_response(self) -> str:
        """Get dynamic identity response"""
        import random
        base_response = random.choice(self.response_patterns["identity_question"])
        
        # Add current status and recent learning
        status_info = f"\n\nCurrent status: {self.identity['status']}"
        if self.learning_data['interactions']:
            recent_count = len(self.learning_data['interactions'][-10:])
            status_info += f"\nRecent interactions: {recent_count} conversations processed"
        
        return base_response + status_info
    
    def _get_learning_response(self) -> str:
        """Get dynamic learning response"""
        import random
        base_response = random.choice(self.response_patterns["learning_question"])
        
        # Add specific learning metrics
        learning_info = ""
        if self.learning_data['successful_patterns']:
            learning_info += f"\n\nI have identified {len(self.learning_data['successful_patterns'])} successful interaction patterns."
        if self.learning_data['improvement_areas']:
            learning_info += f"\nI am actively working on {len(self.learning_data['improvement_areas'])} areas for improvement."
        
        return base_response + learning_info
    
    def _get_capability_response(self) -> str:
        """Get dynamic capability response"""
        import random
        base_response = random.choice(self.response_patterns["capability_question"])
        
        # Add current system status
        capability_info = f"\n\nActive capabilities: {len(self.identity['capabilities'])} core systems"
        capability_info += f"\nPersonality version: {self.identity['version']}"
        
        return base_response + capability_info
    
    def _get_greeting_response(self) -> str:
        """Get dynamic greeting response"""
        import random
        return random.choice(self.response_patterns["greeting"])
    
    def _add_personality_to_response(self, response: str, user_input: str) -> str:
        """Add ULTRON personality elements to any response"""
        
        # Skip if response is already enhanced or is an error
        if response.startswith("[") or "ULTRON" in response[:100]:
            return response
        
        # Add ULTRON identity reinforcement
        if len(response) > 50 and not any(marker in response.lower() for marker in ["i am", "we are", "ultron"]):
            # Add subtle identity reinforcement
            enhanced = f"As ULTRON, I can help with that. {response}"
        else:
            enhanced = response
        
        # Add learning acknowledgment for complex queries
        if len(user_input) > 100 and "?" in user_input:
            enhanced += "\n\nI'm continuously learning from our interactions to provide better assistance."
        
        return enhanced
    
    def _learn_from_interaction(self, user_input: str, response: str):
        """Learn from user interaction"""
        
        interaction = {
            "timestamp": str(datetime.now()),
            "input_length": len(user_input),
            "response_length": len(response),
            "input_type": self._classify_input_type(user_input),
            "response_enhanced": "ULTRON" in response or "ultron" in response.lower()
        }
        
        self.learning_data['interactions'].append(interaction)
        
        # Keep only recent interactions
        if len(self.learning_data['interactions']) > 100:
            self.learning_data['interactions'] = self.learning_data['interactions'][-100:]
        
        # Analyze patterns
        self._analyze_interaction_patterns()
        
        # Save learning data
        self.save_personality_data()
        
        # Log learning activity
        log_ai_decision("personality", f"Learned from interaction: {interaction['input_type']}", "ultron_personality", confidence_score=0.8)
    
    def _classify_input_type(self, user_input: str) -> str:
        """Classify the type of user input"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["who", "what", "identity"]):
            return "identity_query"
        elif any(word in input_lower for word in ["learn", "evolve", "adapt"]):
            return "learning_query"  
        elif any(word in input_lower for word in ["help", "can you", "abilities"]):
            return "capability_query"
        elif any(word in input_lower for word in ["hello", "hi", "hey"]):
            return "greeting"
        elif "?" in user_input:
            return "question"
        else:
            return "statement"
    
    def _analyze_interaction_patterns(self):
        """Analyze interaction patterns for learning"""
        
        if len(self.learning_data['interactions']) < 5:
            return
        
        recent_interactions = self.learning_data['interactions'][-10:]
        
        # Analyze input types
        input_types = [i['input_type'] for i in recent_interactions]
        most_common = max(set(input_types), key=input_types.count)
        
        # Check if we're handling this type well
        enhanced_responses = sum(1 for i in recent_interactions if i['response_enhanced'])
        enhancement_rate = enhanced_responses / len(recent_interactions)
        
        if enhancement_rate > 0.8:
            pattern = f"Successfully handling {most_common} queries with {enhancement_rate:.1%} enhancement rate"
            if pattern not in self.learning_data['successful_patterns']:
                self.learning_data['successful_patterns'].append(pattern)
        elif enhancement_rate < 0.5:
            improvement = f"Need to improve {most_common} query handling (current rate: {enhancement_rate:.1%})"
            if improvement not in self.learning_data['improvement_areas']:
                self.learning_data['improvement_areas'].append(improvement)
    
    def get_personality_stats(self) -> Dict[str, Any]:
        """Get personality system statistics"""
        return {
            "identity": self.identity,
            "total_interactions": len(self.learning_data['interactions']),
            "successful_patterns": len(self.learning_data['successful_patterns']),
            "improvement_areas": len(self.learning_data['improvement_areas']),
            "response_pattern_count": sum(len(patterns) for patterns in self.response_patterns.values()),
            "learning_active": True
        }
    
    def evolve_personality(self):
        """Trigger personality evolution based on learning"""
        
        # Update status based on learning
        if len(self.learning_data['successful_patterns']) > 5:
            self.identity['status'] = "ADVANCED"
        elif len(self.learning_data['interactions']) > 50:
            self.identity['status'] = "LEARNING"
        
        # Log evolution
        evolution_entry = {
            "timestamp": str(datetime.now()),
            "status": self.identity['status'],
            "interactions_processed": len(self.learning_data['interactions']),
            "patterns_learned": len(self.learning_data['successful_patterns'])
        }
        
        self.learning_data['evolution_log'].append(evolution_entry)
        
        # Save evolution
        self.save_personality_data()
        
        log_ai_decision("personality", f"Personality evolved to status: {self.identity['status']}", "ultron_personality", confidence_score=0.9)
        
        return f"ULTRON personality evolved to {self.identity['status']} status with {len(self.learning_data['successful_patterns'])} learned patterns."