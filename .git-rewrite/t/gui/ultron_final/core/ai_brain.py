"""AI brain for conversation and command processing"""
import openai
import logging
from datetime import datetime
import json

class AIBrain:
    def __init__(self, config):
        self.config = config['ai']
        self.available = False
        self.setup()
    
    def setup(self):
        try:
            if self.config.get('openai_api_key'):
                openai.api_key = self.config['openai_api_key']
                self.available = True
                logging.info("AI brain initialized with OpenAI")
            else:
                logging.warning("No OpenAI API key provided")
        except Exception as e:
            logging.error(f"AI brain init failed: {e}")
    
    async def generate_response(self, prompt, context=None):
        if not self.available:
            return self._fallback_response(prompt)
        
        try:
            messages = [
                {"role": "system", "content": "You are ULTRON, an AI assistant. Be helpful and concise."}
            ]
            
            if context:
                for item in context:
                    if item.get('command') and item.get('response'):
                        messages.append({"role": "user", "content": item['command']})
                        messages.append({"role": "assistant", "content": item['response']})
            
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"AI response error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt):
        """Simple fallback responses when AI is unavailable"""
        responses = {
            "hello": "Hello! I'm ULTRON, your AI assistant.",
            "how are you": "I'm functioning optimally, thank you.",
            "what can you do": "I can help with system tasks, file management, screenshots, and more.",
            "thank you": "You're welcome! Happy to help.",
            "goodbye": "Goodbye! Let me know if you need anything."
        }
        
        prompt_lower = prompt.lower()
        for key, response in responses.items():
            if key in prompt_lower:
                return response
        
        return "I understand. How can I assist you further?"
    
    def is_available(self):
        return self.available
