# ollama_client.py
import httpx
import json
import logging
from typing import AsyncGenerator, Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"

async def ollama_chat(messages: List[Dict[str, str]], model: str = "qwen2.5vl", stream: bool = True) -> AsyncGenerator[str, None]:
    """
    Sends a list of messages to Ollama and streams the response.
    Each yielded string is a chunk of the model's reply.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The model name to use (default: qwen2.5vl)
        stream: Whether to stream the response (default: True)
    
    Yields:
        str: Chunks of the model's response
    """
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            logger.info(f"Sending request to Ollama with model: {model}")
            
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json=payload,
            ) as response:
                if response.status_code != 200:
                    logger.error(f"Ollama API error: {response.status_code}")
                    yield f"Error: Ollama API returned status {response.status_code}"
                    return
                
                full_response = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # Ollama streams partial responses under `message.content`
                            if "message" in data and "content" in data["message"]:
                                chunk = data["message"]["content"]
                                full_response += chunk
                                yield chunk
                            elif "done" in data and data["done"]:
                                # Stream is complete
                                break
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON line: {line}, error: {e}")
                            continue
                
                logger.info(f"Completed Ollama chat. Total response length: {len(full_response)}")
                
    except httpx.ConnectError:
        error_msg = "Failed to connect to Ollama. Make sure Ollama is running on http://127.0.0.1:11434"
        logger.error(error_msg)
        yield error_msg
    except Exception as e:
        error_msg = f"Unexpected error communicating with Ollama: {str(e)}"
        logger.error(error_msg)
        yield error_msg

async def ollama_generate(prompt: str, model: str = "qwen2.5vl", stream: bool = True) -> AsyncGenerator[str, None]:
    """
    Generate text from a prompt using Ollama's generate endpoint.
    
    Args:
        prompt: The text prompt to generate from
        model: The model name to use (default: qwen2.5vl)
        stream: Whether to stream the response (default: True)
    
    Yields:
        str: Chunks of the generated text
    """
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            logger.info(f"Generating text with Ollama model: {model}")
            
            async with client.stream(
                "POST",
                OLLAMA_GENERATE_URL,
                json=payload,
            ) as response:
                if response.status_code != 200:
                    logger.error(f"Ollama Generate API error: {response.status_code}")
                    yield f"Error: Ollama Generate API returned status {response.status_code}"
                    return
                
                full_response = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                chunk = data["response"]
                                full_response += chunk
                                yield chunk
                            elif "done" in data and data["done"]:
                                break
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON line: {line}, error: {e}")
                            continue
                
                logger.info(f"Completed text generation. Total response length: {len(full_response)}")
                
    except httpx.ConnectError:
        error_msg = "Failed to connect to Ollama. Make sure Ollama is running on http://127.0.0.1:11434"
        logger.error(error_msg)
        yield error_msg
    except Exception as e:
        error_msg = f"Unexpected error generating text with Ollama: {str(e)}"
        logger.error(error_msg)
        yield error_msg

async def check_ollama_status() -> Dict[str, Any]:
    """
    Check if Ollama is running and get available models.
    
    Returns:
        dict: Status information including availability and models
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if Ollama is running
            response = await client.get("http://127.0.0.1:11434/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                models = [model["name"] for model in models_data.get("models", [])]
                return {
                    "available": True,
                    "models": models,
                    "status": "running"
                }
            else:
                return {
                    "available": False,
                    "models": [],
                    "status": f"HTTP {response.status_code}"
                }
    except httpx.ConnectError:
        return {
            "available": False,
            "models": [],
            "status": "not_running"
        }
    except Exception as e:
        return {
            "available": False,
            "models": [],
            "status": f"error: {str(e)}"
        }

# Convenience function for synchronous usage
def sync_ollama_chat(messages: List[Dict[str, str]], model: str = "qwen2.5vl") -> str:
    """
    Synchronous wrapper for ollama_chat.
    Returns the complete response as a single string.
    """
    import asyncio
    
    async def _get_response():
        response = ""
        async for chunk in ollama_chat(messages, model):
            response += chunk
        return response
    
    return asyncio.run(_get_response())

if __name__ == "__main__":
    # Simple test
    import asyncio
    
    async def test():
        print("Testing Ollama connection... - ollama_client.py:192")
        status = await check_ollama_status()
        print(f"Status: {status} - ollama_client.py:194")
        
        if status["available"]:
            print("\nTesting chat... - ollama_client.py:197")
            messages = [{"role": "user", "content": "Hello, who are you?"}]
            async for chunk in ollama_chat(messages):
                print(chunk, end="", flush=True)
            print("\n - ollama_client.py:201")
    
    asyncio.run(test())
