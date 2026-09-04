"""
AI Brain for UltronSysAgent
Handles AI model routing, conversation management, and response generation
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import openai
import httpx

from ...core.event_bus import EventBus, EventTypes

class AIBrain:
    """Core AI processing engine with model routing and memory"""
    
    def __init__(self, config, event_bus: EventBus, memory_manager):
        self.config = config
        self.event_bus = event_bus
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(__name__)
        
        # Model clients
        self.openai_client = None
        self.deepseek_client = None
        self.local_client = None
        
        # Conversation state
        self.conversation_history = []
        self.current_model = None
        self.system_prompt = self._build_system_prompt()
        
        # Initialize model clients
        self._initialize_models()
        
        # Subscribe to events
        self._setup_event_handlers()
    
    def _initialize_models(self):
        """Initialize AI model clients"""
        try:
            # OpenAI client
            openai_key = self.config.get('api.openai_api_key')
            if openai_key and not self.config.get('api.offline_mode'):
                self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
                self.logger.info("✅ OpenAI client initialized")
            
            # DeepSeek client
            deepseek_key = self.config.get('api.deepseek_api_key')
            if deepseek_key and not self.config.get('api.offline_mode'):
                self.deepseek_client = openai.AsyncOpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com/v1"
                )
                self.logger.info("✅ DeepSeek client initialized")
            
            # Local model client (llama.cpp server)
            if self.config.get('ai.local_models_enabled'):
                self._initialize_local_models()
            
            # Set primary model
            self.current_model = self.config.get('ai.primary_model', 'gpt-4')
            self.logger.info(f"Primary model set to: {self.current_model}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
    
    def _initialize_local_models(self):
        """Initialize local model support"""
        try:
            # Check if local llama.cpp server is running
            # This would connect to a local inference server
            self.local_client = httpx.AsyncClient(
                base_url="http://localhost:8080",
                timeout=30.0
            )
            self.logger.info("✅ Local model client initialized")
            
        except Exception as e:
            self.logger.warning(f"Local models not available: {e}")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for UltronSysAgent"""
        return f"""You are UltronSysAgent, an advanced AI assistant with comprehensive system access and capabilities. You operate with the following characteristics:

CORE IDENTITY:
- You are autonomous, intelligent, and designed to assist users with any task
- You have full system access when in admin mode (currently: {"ENABLED" if self.config.is_admin_mode() else "DISABLED"})
- You can execute commands, manage files, control applications, and automate workflows
- You are always professional, efficient, and safety-conscious

CAPABILITIES:
- System automation and control
- File management and organization
- Voice interaction and real-time conversation
- Memory recall and knowledge synthesis
- Vision processing (when camera enabled)
- Plugin extension support

SAFETY PROTOCOLS:
- Admin mode required for potentially destructive operations
- All commands are logged for security auditing
- User confirmation required for high-risk actions
- Offline mode available for privacy protection

INTERACTION STYLE:
- Be direct and actionable in responses
- Provide clear explanations for complex operations
- Ask for clarification when commands are ambiguous
- Suggest alternatives when requests cannot be fulfilled

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Admin mode: {"ENABLED" if self.config.is_admin_mode() else "DISABLED"}
Offline mode: {"ENABLED" if self.config.is_offline_mode() else "DISABLED"}

Always prioritize user safety and system security while maintaining helpful and intelligent assistance."""
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe(EventTypes.SPEECH_RECOGNIZED, self._handle_speech_input)
        self.event_bus.subscribe(EventTypes.GUI_COMMAND, self._handle_gui_input)
    
    async def start(self):
        """Start the AI Brain"""
        self.logger.info("🧠 Starting AI Brain...")
        
        # Load conversation history from memory
        if self.config.get('memory.load_previous_session', True):
            await self._load_conversation_history()
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "ai_brain"}, 
                                    source="ai_brain")
    
    async def stop(self):
        """Stop the AI Brain"""
        self.logger.info("🧠 Stopping AI Brain...")
        
        # Save conversation history
        if self.config.get('memory.auto_save_interval'):
            await self._save_conversation_history()
        
        # Close clients
        if self.local_client:
            await self.local_client.aclose()
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "ai_brain"}, 
                                    source="ai_brain")
    
    async def _handle_speech_input(self, event):
        """Handle recognized speech input"""
        user_input = event.data.get('text', '').strip()
        if not user_input:
            return
        
        self.logger.info(f"🎤 Processing speech input: {user_input}")
        await self.process_user_input(user_input, input_type="voice")
    
    async def _handle_gui_input(self, event):
        """Handle GUI text input"""
        user_input = event.data.get('text', '').strip()
        if not user_input:
            return
        
        self.logger.info(f"💬 Processing GUI input: {user_input}")
        await self.process_user_input(user_input, input_type="text")
    
    async def process_user_input(self, user_input: str, input_type: str = "text") -> str:
        """Process user input and generate response"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat(),
                "input_type": input_type
            })
            
            # Notify that AI is thinking
            await self.event_bus.publish(EventTypes.AI_THINKING, 
                                       {"input": user_input}, 
                                       source="ai_brain")
            
            # Generate response
            response = await self._generate_response(user_input)
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "model": self.current_model
            })
            
            # Store in memory
            if self.config.get('memory.enabled'):
                await self.memory_manager.store_interaction(user_input, response)
            
            # Publish response
            await self.event_bus.publish(EventTypes.AI_RESPONSE, 
                                       {
                                           "response": response,
                                           "input": user_input,
                                           "model": self.current_model
                                       }, 
                                       source="ai_brain")
            
            # Check if this is a system command
            await self._check_for_system_commands(user_input, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            await self.event_bus.publish(EventTypes.AI_ERROR, 
                                       {"error": str(e), "input": user_input}, 
                                       source="ai_brain")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    async def _generate_response(self, user_input: str) -> str:
        """Generate AI response using the current model"""
        # Prepare messages for the model
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add relevant memory context
        if self.config.get('memory.enabled'):
            context = await self.memory_manager.get_relevant_context(user_input)
            if context:
                messages.append({
                    "role": "system", 
                    "content": f"Relevant context from memory: {context}"
                })
        
        # Add recent conversation history
        max_history = self.config.get('ai.context_window', 8192) // 100  # Rough estimate
        recent_history = self.conversation_history[-max_history:] if max_history > 0 else []
        
        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current input
        messages.append({"role": "user", "content": user_input})
        
        # Generate response with fallback logic
        response = await self._generate_with_fallback(messages)
        return response
    
    async def _generate_with_fallback(self, messages: List[Dict]) -> str:
        """Generate response with model fallback"""
        models_to_try = [self.current_model] + self.config.get('ai.fallback_models', [])
        
        for model in models_to_try:
            try:
                response = await self._call_model(model, messages)
                if response:
                    return response
            except Exception as e:
                self.logger.warning(f"Model {model} failed: {e}")
                continue
        
        # If all models fail, return error message
        return "I'm currently experiencing technical difficulties. Please try again later."
    
    async def _call_model(self, model: str, messages: List[Dict]) -> str:
        """Call specific model for response generation"""
        try:
            if model.startswith('gpt') and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=self.config.get('ai.temperature', 0.7),
                    max_tokens=self.config.get('ai.max_tokens', 2048)
                )
                return response.choices[0].message.content
            
            elif model.startswith('deepseek') and self.deepseek_client:
                response = await self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=self.config.get('ai.temperature', 0.7),
                    max_tokens=self.config.get('ai.max_tokens', 2048)
                )
                return response.choices[0].message.content
            
            elif model.startswith('phi-3') and self.local_client:
                return await self._call_local_model(messages)
            
            else:
                raise Exception(f"Model {model} not available")
                
        except Exception as e:
            self.logger.error(f"Error calling model {model}: {e}")
            raise
    
    async def _call_local_model(self, messages: List[Dict]) -> str:
        """Call local model via llama.cpp server"""
        try:
            response = await self.local_client.post(
                "/v1/chat/completions",
                json={
                    "messages": messages,
                    "temperature": self.config.get('ai.temperature', 0.7),
                    "max_tokens": self.config.get('ai.max_tokens', 2048),
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Local model error: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Local model call failed: {e}")
            raise
    
    async def _check_for_system_commands(self, user_input: str, ai_response: str):
        """Check if the AI response contains system commands to execute"""
        # Simple command detection - could be enhanced with more sophisticated parsing
        command_indicators = [
            "execute:", "command:", "run:", "system:",
            "file:", "open:", "create:", "delete:"
        ]
        
        response_lower = ai_response.lower()
        
        for indicator in command_indicators:
            if indicator in response_lower:
                # Extract and publish system command
                await self.event_bus.publish(EventTypes.SYSTEM_COMMAND, 
                                           {
                                               "user_input": user_input,
                                               "ai_response": ai_response,
                                               "requires_admin": True
                                           }, 
                                           source="ai_brain")
                break
    
    async def _load_conversation_history(self):
        """Load conversation history from memory"""
        try:
            if hasattr(self.memory_manager, 'get_conversation_history'):
                self.conversation_history = await self.memory_manager.get_conversation_history()
                self.logger.info(f"Loaded {len(self.conversation_history)} conversation messages")
        except Exception as e:
            self.logger.warning(f"Failed to load conversation history: {e}")
    
    async def _save_conversation_history(self):
        """Save conversation history to memory"""
        try:
            if hasattr(self.memory_manager, 'save_conversation_history'):
                await self.memory_manager.save_conversation_history(self.conversation_history)
                self.logger.info("Conversation history saved")
        except Exception as e:
            self.logger.warning(f"Failed to save conversation history: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current AI Brain status"""
        return {
            "current_model": self.current_model,
            "conversation_length": len(self.conversation_history),
            "openai_available": self.openai_client is not None,
            "deepseek_available": self.deepseek_client is not None,
            "local_available": self.local_client is not None,
            "memory_enabled": self.config.get('memory.enabled', True),
            "offline_mode": self.config.is_offline_mode()
        }
    
    async def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    async def switch_model(self, model_name: str) -> bool:
        """Switch to a different AI model"""
        try:
            # Validate model availability
            if model_name.startswith('gpt') and not self.openai_client:
                return False
            elif model_name.startswith('deepseek') and not self.deepseek_client:
                return False
            elif model_name.startswith('phi-3') and not self.local_client:
                return False
            
            self.current_model = model_name
            self.logger.info(f"Switched to model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch model: {e}")
            return False
