"""Unity AI Bridge - Connects ULTRON's Ollama models to Unity AI Inference"""

import asyncio
import json
from aiohttp import web, ClientSession
from utils.ultron_logger import log_info, log_error


class UnityBridge:
    def __init__(self, ollama_url="http://localhost:11434", port=8765):
        self.ollama_url = ollama_url
        self.port = port
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        self.app.router.add_post('/api/assistant', self.assistant_handler)
        self.app.router.add_post('/api/generate', self.generate_handler)
        self.app.router.add_post('/inference', self.inference_handler)
    
    async def assistant_handler(self, request):
        """Handle Unity AI Assistant queries via Ollama"""
        try:
            data = await request.json()
            query = data.get('query', '')
            
            async with ClientSession() as session:
                payload = {
                    "model": "qwen3-coder:480b-cloud",
                    "messages": [{"role": "user", "content": query}],
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/chat", json=payload) as resp:
                    result = await resp.json()
                    response = result.get("message", {}).get("content", "")
                    
                    log_info("unity_bridge", f"Assistant query: {query[:50]}")
                    return web.json_response({"response": response})
        except Exception as e:
            log_error("unity_bridge", f"Assistant error: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def generate_handler(self, request):
        """Handle Unity asset generation via Ollama"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            
            async with ClientSession() as session:
                payload = {
                    "model": "qwen3-coder:480b-cloud",
                    "prompt": f"Generate Unity asset code: {prompt}",
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as resp:
                    result = await resp.json()
                    code = result.get("response", "")
                    
                    log_info("unity_bridge", f"Generated asset: {prompt[:50]}")
                    return web.json_response({"asset_path": "generated.cs", "code": code})
        except Exception as e:
            log_error("unity_bridge", f"Generation error: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def inference_handler(self, request):
        """Handle Unity AI Inference via Ollama"""
        try:
            data = await request.json()
            input_data = data.get('input', '')
            
            async with ClientSession() as session:
                payload = {
                    "model": "qwen3-coder:480b-cloud",
                    "prompt": input_data,
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as resp:
                    result = await resp.json()
                    output = result.get("response", "")
                    
                    log_info("unity_bridge", f"Inference: {input_data[:50]}")
                    return web.json_response({"output": output})
        except Exception as e:
            log_error("unity_bridge", f"Inference error: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    def run(self):
        log_info("unity_bridge", f"Starting Unity Bridge on port {self.port}")
        web.run_app(self.app, host='0.0.0.0', port=self.port)


if __name__ == '__main__':
    bridge = UnityBridge()
    bridge.run()
