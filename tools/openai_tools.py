import logging
import asyncio
import json
import aiohttp
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import os

class OpenAITools:
    def __init__(self, config):
        self.config = config
        api_key = config.data.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not found in configuration")
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def text_to_speech(self, text: str, voice: str = "alloy", model: str = "tts-1", output_file: str = None) -> str:
        """Convert text to speech using OpenAI's TTS API."""
        try:
            if not output_file:
                output_file = f"speech_{hash(text)}.mp3"
                
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )
            
            await response.astream_to_file(output_file)
            logging.info(f"Generated speech saved to {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"TTS error: {e}")
            raise

    async def speech_to_text(self, audio_file: str, model: str = "whisper-1", language: str = None) -> str:
        """Convert speech to text using OpenAI's Whisper API."""
        try:
            with open(audio_file, "rb") as audio:
                transcription = await self.client.audio.transcriptions.create(
                    model=model,
                    file=audio,
                    language=language
                )
            logging.info("Successfully transcribed audio")
            return transcription.text
            
        except Exception as e:
            logging.error(f"STT error: {e}")
            raise

    async def agent_invoke_tools(self, prompt: str, tools: List[Dict[str, Any]], 
                               messages: List[Dict[str, str]] = None) -> Dict:
        """Invoke agent with tools using OpenAI's Function Calling API."""
        try:
            if not messages:
                messages = []
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Here you'd implement the actual tool execution
                    tool_response = await self._execute_tool(function_name, function_args)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_response)
                    })
                
                final_response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages
                )
                return {
                    "response": final_response.choices[0].message.content,
                    "tool_calls": tool_calls,
                    "messages": messages
                }
            
            return {
                "response": response_message.content,
                "tool_calls": None,
                "messages": messages
            }
            
        except Exception as e:
            logging.error(f"Agent tools error: {e}")
            raise

    async def _execute_tool(self, function_name: str, function_args: Dict) -> Any:
        """Execute the appropriate tool based on the function name."""
        try:
            # Add your tool implementations here
            tools_map = {
                # Example:
                # "search_web": self._search_web,
                # "run_code": self._run_code,
            }
            
            if function_name in tools_map:
                return await tools_map[function_name](**function_args)
            else:
                return f"Tool {function_name} not implemented"
                
        except Exception as e:
            logging.error(f"Tool execution error: {e}")
            raise
