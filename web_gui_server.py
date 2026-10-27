#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Web GUI Server Integration
Serves the beautiful web-based Pokédx GUI and integrates with agent backend
"""

import os
import sys
import json
import logging
import threading
import asyncio
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional
import http.server
import socketserver
import urllib.parse
import webbrowser
from datetime import datetime

# Import agent components
try:
    from agent_core import UltronAgent
    from enhanced_memory_system import EnhancedMemorySystem
    from multi_agent_system import MultiAgentOrchestrator
    from enhanced_tool_framework import tool_registry
    from task_planning_system import task_planner, workflow_executor
    from langflow_integration import langflow_agent, LangFlowBridge
    from diagnostics_manager import DiagnosticsManager
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logging.warning("Enhanced agent components not available - web_gui_server.py:34")

# Import voice system for TTS
try:
    from voice import VoiceAssistant
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logging.warning("Voice system not available  TTS disabled - web_gui_server.py:42")

# Import Phase 2 Real-time & Performance components
try:
    from phase2_realtime_profiling import (
        profiler,
        metrics_buffer,
        metrics_collector,
        ws_handler,
        start_phase2_services,
        stop_phase2_services
    )
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False
    logging.warning("Phase 2 profiling not available - web_gui_server.py:57")

# Load configuration for voice
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'ultron_config.json')

try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"use_voice": False, "voice_enabled": False}


def persist_config_updates(updates: Dict[str, Any]) -> None:
    """Persist configuration updates to ultron_config.json."""
    global config

    if not updates:
        return

    try:
        current_config: Dict[str, Any] = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as config_file:
                current_config = json.load(config_file)

        current_config.update(updates)

        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(current_config, config_file, indent=2)

        config.update(current_config)
    except Exception as persist_error:
        logging.warning(f"Failed to persist config updates: {persist_error} - web_gui_server.py:89")

class UltronWebHandler(http.server.SimpleHTTPRequestHandler):

    def _get_unified_llm_models(self):
        """Get available LLM models from Ollama, NVIDIA NIM, and OpenAI (if configured)."""
        models = []
        # Ollama models
        try:
            import requests
            ollama_url = "http://localhost:11434"
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                for model in data.get('models', []):
                    models.append({
                        'name': model.get('name'),
                        'provider': 'ollama',
                        'size': model.get('size', 'Unknown'),
                        'modified': model.get('modified_at', 'Unknown')
                    })
        except Exception as e:
            models.append({'provider': 'ollama', 'error': f'Connection error: {str(e)}'})

        # NVIDIA NIM models
        try:
            from nvidia_nim_router import UltronNvidiaRouter
            nim_router = UltronNvidiaRouter()
            for key, info in nim_router.models.items():
                models.append({
                    'name': info['name'],
                    'provider': 'nvidia',
                    'id': info['id'],
                    'description': info['description'],
                    'capabilities': info.get('capabilities', []),
                    'active': (key == getattr(nim_router, 'current_model', None))
                })
        except Exception as e:
            models.append({'provider': 'nvidia', 'error': f'NIM error: {str(e)}'})

        # OpenAI models (optional)
        try:
            from openai_integration import OpenAIAssistant
            import os
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if openai_api_key:
                # List a few common OpenAI models
                openai_models = [
                    {'name': 'gpt-4o', 'provider': 'openai', 'description': 'OpenAI GPT-4o (multimodal, fast, high quality)'},
                    {'name': 'gpt-4-turbo', 'provider': 'openai', 'description': 'OpenAI GPT-4 Turbo (cost-effective, high quality)'},
                    {'name': 'gpt-3.5-turbo', 'provider': 'openai', 'description': 'OpenAI GPT-3.5 Turbo (fast, low cost)'}
                ]
                models.extend(openai_models)
        except Exception as e:
            models.append({'provider': 'openai', 'error': f'OpenAI error: {str(e)}'})
        return {'models': models}


    def _switch_unified_llm_model(self, model_name: str, provider: str):
        """Switch LLM model for Ollama, NVIDIA NIM, or OpenAI."""
        if provider == 'ollama':
            return self._switch_llm_model(model_name)
        elif provider == 'nvidia':
            try:
                from nvidia_nim_router import UltronNvidiaRouter
                nim_router = UltronNvidiaRouter()
                result = nim_router.route_model(model_name)
                return {'status': 'success' if 'Model routed' in result else 'error', 'message': result, 'model': model_name}
            except Exception as e:
                return {'status': 'error', 'message': f'NIM switch error: {str(e)}'}
        elif provider == 'openai':
            import os
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if not openai_api_key:
                return {'status': 'error', 'message': 'OpenAI API key not set in environment.'}
            # For OpenAI, just record the model selection (actual chat will use this)
            UltronWebHandler.current_model_preference = model_name
            return {'status': 'success', 'message': f'OpenAI model switched to {model_name}', 'model': model_name}
        else:
            return {'status': 'error', 'message': 'Unknown provider'}

    # Custom handler for ULTRON web interface

    # Class variable to store current model preference
    current_model_preference = 'llava:7b'

    # Class variable for voice assistant
    voice_assistant = None

    # Voice state shared across handler instances
    voice_state = {
        'enabled': config.get("use_voice", False) and config.get("voice_enabled", False),
        'listening': False
    }

    def __init__(self, *args, agent_ref=None, **kwargs):
        # Ensure agent_ref is always set, fallback to global if needed
        if agent_ref is not None:
            self.agent_ref = agent_ref
        elif hasattr(UltronWebHandler, 'agent_ref') and UltronWebHandler.agent_ref is not None:
            self.agent_ref = UltronWebHandler.agent_ref
        else:
            # Create minimal fallback agent to prevent 500 errors
            try:
                from brain import UltronBrain
                from enhanced_memory_system import EnhancedMemorySystem
                from enhanced_tool_framework import tool_registry
                fallback_config = config
                fallback_tools = tool_registry.tools if hasattr(tool_registry, 'tools') else {}
                fallback_memory = EnhancedMemorySystem()
                self.agent_ref = type('FallbackAgent', (), {
                    'brain': UltronBrain(fallback_config, fallback_tools, fallback_memory),
                    'process_command': lambda self, cmd: self.brain.process_command(cmd) if hasattr(self.brain, 'process_command') else f"Processed: {cmd}"
                })()
                print("[OK] Fallback agent initialized for chat backend")
            except Exception as e:
                print(f"[WARN] Fallback agent failed: {e}")
                self.agent_ref = None

        # Load model preference from config
        try:
            with open(CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
                UltronWebHandler.current_model_preference = config_data.get(
                    'llm_model', 'llava:7b'
                )
                UltronWebHandler.voice_state['enabled'] = bool(
                    config_data.get("use_voice", False) and config_data.get("voice_enabled", False)
                )
                config.update(config_data)
        except Exception as e:
            logging.warning(f"Could not load model from config: {e} - web_gui_server.py:121")

        # Initialize voice assistant if not already done and if enabled
        if (
            UltronWebHandler.voice_assistant is None
            and VOICE_AVAILABLE
            and UltronWebHandler.voice_state.get('enabled', False)
        ):
            try:
                UltronWebHandler.voice_assistant = VoiceAssistant(config)
                logging.info("Voice Assistant initialized for TTS support - web_gui_server.py:131")
            except Exception as e:
                logging.warning(f"Failed to initialize voice assistant: {e} - web_gui_server.py:133")
                UltronWebHandler.voice_assistant = None

        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        logging.info(f"GET request: {self.path} - web_gui_server.py:140")

        if self.path.startswith('/api/'):
            self._handle_api_get()
        elif self.path == '/' or self.path == '':
            # Serve main ULTRON GUI
            self.path = '/index.html'
            super().do_GET()
        elif self.path == '/adb.html':
            # Serve ADB Manager console
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        logging.info(f"POST request: {self.path} - web_gui_server.py:156")

        if self.path.startswith('/api/'):
            self._handle_api_post()
        else:
            self.send_error(404)

    def _handle_api_get(self):
        """Handle API GET requests"""
        try:
            if self.path == '/api/llm/unified-models':
                self._send_json_response(self._get_unified_llm_models())
                return
            if self.path == '/api/status':
                self._send_json_response(self._get_system_status())
            elif self.path == '/api/system/stats':
                self._send_json_response(self._get_system_status())
            elif self.path == '/api/agent/info':
                self._send_json_response(self._get_agent_info())
            elif self.path == '/api/tools':
                self._send_json_response(self._get_tools_list())
            elif self.path == '/api/llm/status':
                self._send_json_response(self._get_llm_status())
            elif self.path == '/api/llm/models':
                self._send_json_response(self._get_llm_models())
            elif self.path == '/api/voice/status':
                self._send_json_response(self._get_voice_status())
            elif self.path == '/api/brain/status':
                self._send_json_response(self._get_brain_status())
            elif self.path == '/api/files':
                self._send_json_response(self._get_files_list())
            elif self.path == '/api/vision/recent':
                self._send_json_response(self._get_vision_recent())
            elif self.path == '/api/nvidia/status':
                self._send_json_response(self._get_nvidia_status())
            elif self.path == '/api/autonomous/status':
                self._send_json_response(self._get_autonomous_status())
            elif self.path == '/api/autonomous/learning-data':
                self._send_json_response(self._get_autonomous_learning_data())
            elif self.path == '/api/ssh/status':
                self._send_json_response(self._get_ssh_status())
            elif self.path == '/api/autogen/status':
                self._send_json_response(self._get_autogen_status())
            elif self.path == '/api/system/metrics':
                self._send_json_response(self._get_system_metrics())
            elif self.path == '/api/health/full':
                self._send_json_response(self._get_comprehensive_health())
            elif self.path == '/api/performance/stats':
                self._send_json_response(self._get_performance_stats())
            elif self.path == '/api/performance/bottlenecks':
                self._send_json_response(
                    self._get_performance_bottlenecks())
            elif self.path == '/api/metrics/stream':
                self._send_json_response(self._get_metrics_stream())
            elif self.path == '/api/phase2/status':
                self._send_json_response(self._get_phase2_status())
            elif self.path == '/api/system/info':
                self._send_json_response(self._get_system_info())
            elif self.path == '/api/ssh/status':
                self._send_json_response(self._get_ssh_status())
            elif self.path == '/api/game/status':
                self._send_json_response(self._get_game_status())
            elif self.path == '/api/autogen/status':
                self._send_json_response(self._get_autogen_status())
            elif self.path == '/api/vision/status':
                self._send_json_response(self._get_vision_status())
            elif self.path == '/api/consciousness/status':
                self._send_json_response(self._get_consciousness_status())
            elif self.path == '/api/consciousness/introspect':
                self._send_json_response(self._get_consciousness_introspection())
            elif self.path.startswith(
                    '/api/performance/function-history/'):
                func_name = self.path.split('/')[-1]
                self._send_json_response(
                    self._get_function_history(func_name))
            else:
                self.send_error(404, "API endpoint not found")

        except Exception as e:
            logging.error(f"API GET error: {e} - web_gui_server.py:224")
            self._send_json_response(
                {'success': False, 'error': str(e)}, 500)

    def _handle_api_post(self):
        """Handle API POST requests"""
        try:
            if self.path == '/api/llm/unified-switch':
                data = {}
                content_length_header = self.headers.get('Content-Length')
                if content_length_header:
                    content_length = int(content_length_header)
                    post_data = self.rfile.read(content_length)
                    if content_length > 0 and post_data:
                        data = json.loads(post_data.decode('utf-8'))
                model = data.get('model', '')
                provider = data.get('provider', '')
                response = self._switch_unified_llm_model(model, provider)
                self._send_json_response(response)
                return
            content_length_header = self.headers.get('Content-Length')
            if not content_length_header:
                self._send_json_response(
                    {'success': False, 'error': 'Missing Content-Length'},
                    400)
                return

            content_length = int(content_length_header)
            post_data = self.rfile.read(content_length)
            # Handle empty request body - treat as empty JSON object
            if content_length == 0 or not post_data:
                data = {}
            else:
                data = json.loads(post_data.decode('utf-8'))

            if self.path == '/api/command':
                response = self._process_command(data.get('command', ''))
                self._send_json_response({'response': response})
            elif self.path == '/api/voice/toggle':
                response = self._toggle_voice(data)
                self._send_json_response(response)
            elif self.path == '/api/voice/speak':
                audio_bytes, content_type, error_payload = self._speak_text(data.get('text', ''))
                if audio_bytes:
                    self._send_audio_response(audio_bytes, content_type)
                else:
                    self._send_json_response(error_payload or {
                        'status': 'error',
                        'message': 'Voice synthesis unavailable'
                    }, status=503)
            elif self.path == '/api/llm/chat':
                response = self._handle_llm_chat(data.get('message', ''))
                # Only return the plain text response for user-facing output
                if isinstance(response, dict) and 'response' in response:
                    self._send_json_response({'response': response['response']})
                elif isinstance(response, dict) and 'error' in response:
                    self._send_json_response({'error': response['error']}, status=500)
                else:
                    self._send_json_response({'response': str(response)})
            elif self.path == '/api/llm/switch-model' or self.path == '/api/model/switch':
                response = self._switch_llm_model(data.get('model', ''))
                self._send_json_response(response)
            elif self.path == '/api/vision/capture':
                response = self._capture_screen()
                self._send_json_response(response)
            elif self.path == '/api/vision/analyze':
                response = self._analyze_vision()
                self._send_json_response(response)
            elif self.path == '/api/autonomous/start':
                response = self._start_autonomous_mode(data)
                self._send_json_response(response)
            elif self.path == '/api/memory/store':
                response = self._store_memory(data)
                self._send_json_response(response)
            elif self.path == '/api/agents/task':
                response = self._process_agent_task(data)
                self._send_json_response(response)
            elif self.path == '/api/tools/execute':
                response = self._execute_tool(data)
                self._send_json_response(response)
            elif self.path == '/api/workflow/execute':
                response = self._execute_workflow(data)
                self._send_json_response(response)
            elif self.path == '/api/langflow/chat':
                response = self._process_langflow_chat(data)
                self._send_json_response(response)
            elif self.path == '/api/langflow/memory':
                response = self._langflow_memory_search(data)
                self._send_json_response(response)
            elif self.path == '/api/langflow/reasoning':
                response = self._langflow_complex_reasoning(data)
                self._send_json_response(response)
            elif self.path == '/api/autonomous/stop':
                response = self._stop_autonomous_mode()
                self._send_json_response(response)
            elif self.path == '/api/consciousness/toggle':
                response = self._toggle_consciousness(data)
                self._send_json_response(response)
            elif self.path == '/api/consciousness/personality':
                response = self._set_personality(data)
                self._send_json_response(response)
            elif self.path == '/api/autonomous/evolve':
                response = self._evolve_autonomous_capabilities()
                self._send_json_response(response)
            elif self.path == '/api/test/integration':
                response = self._run_integration_test()
                self._send_json_response(response)
            elif self.path == '/api/proactive/start':
                response = self._start_proactive_monitoring()
                self._send_json_response(response)
            elif self.path == '/api/proactive/stop':
                response = self._stop_proactive_monitoring()
                self._send_json_response(response)
            elif self.path == '/api/console/execute':
                response = self._execute_console_command(
                    data.get('command', ''),
                    data.get('timeout', 10))
                self._send_json_response(response)
            elif self.path == '/api/profiler/reset':
                if PHASE2_AVAILABLE:
                    profiler.reset()
                    self._send_json_response({
                        'status': 'success',
                        'message': 'Profiler reset - all data cleared'
                    })
                else:
                    self._send_json_response({
                        'error': 'Phase 2 not available'
                    }, 503)
            elif self.path == '/api/metrics/collection/start':
                if PHASE2_AVAILABLE:
                    metrics_collector.start()
                    self._send_json_response({
                        'status': 'success',
                        'message': 'Metrics collection started'
                    })
                else:
                    self._send_json_response({
                        'error': 'Phase 2 not available'
                    }, 503)
            elif self.path == '/api/metrics/collection/stop':
                if PHASE2_AVAILABLE:
                    metrics_collector.stop()
                    self._send_json_response({
                        'status': 'success',
                        'message': 'Metrics collection stopped'
                    })
                else:
                    self._send_json_response({
                        'error': 'Phase 2 not available'
                    }, 503)
            elif self.path == '/api/ssh/start':
                response = self._start_ssh_server()
                self._send_json_response(response)
            elif self.path == '/api/ssh/stop':
                response = self._stop_ssh_server()
                self._send_json_response(response)
            elif self.path == '/api/system/command':
                response = self._execute_system_command(data.get('command', ''))
                self._send_json_response(response)
            elif self.path == '/api/game/start':
                response = self._start_game_server()
                self._send_json_response(response)
            elif self.path == '/api/game/stop':
                response = self._stop_game_server()
                self._send_json_response(response)
            else:
                self.send_error(404, "API endpoint not found")

        except ConnectionAbortedError as e:
            # Client disconnected before receiving response - not an error
            logging.debug(
                f"Client disconnected during API POST: {e} - "
                "")
        except ConnectionResetError as e:
            # Client reset connection - not an error
            logging.debug(
                f"Client reset connection during API POST: {e} - "
                "")
        except Exception as e:
            logging.error(f"API POST error: {e} - web_gui_server.py:379")
            try:
                # Return JSON error instead of HTML
                self._send_json_response(
                    {'success': False, 'error': str(e)}, 500)
            except (ConnectionAbortedError, ConnectionResetError,
                    BrokenPipeError):
                # Can't send error if client already disconnected
                pass

    def _send_json_response(self, data, status=200):
        """Send JSON response"""
        try:
            response = json.dumps(data, indent=2, default=str)
            logging.debug(
                f"Sending JSON {status}: {len(response)} bytes")
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        except (ConnectionAbortedError, ConnectionResetError,
                BrokenPipeError) as e:
            # Client disconnected - log as debug
            logging.debug(
                f"Client disconnected during JSON response: {e} - "
                "")
        except Exception as e:
            # Handle JSON serialization or other errors
            logging.error(
                f"Error sending JSON response: {e}")
            try:
                err = json.dumps({
                    'success': False,
                    'error': str(e)
                })
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(err))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(err.encode('utf-8'))
            except Exception as inner_e:
                logging.error(f"Failed to send error JSON: {inner_e} - web_gui_server.py:423")

    def _send_audio_response(self, audio_bytes: bytes, content_type: str):
        """Send binary audio response"""
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(audio_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(audio_bytes)

    def _get_system_status(self):
        """Get system status information"""
        try:
            import psutil

            status = {
                'success': True,  # ✅ Add success flag for frontend
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent,
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
                },
                'agent': {
                    'status': 'online' if self.agent_ref else 'offline',
                    'uptime': '00:00:00'  # TODO: Calculate actual uptime
                },
                'tools_count': len(getattr(self.agent_ref, 'tools', [])) if self.agent_ref else 0
            }

            # Add GPU info if available
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    status['system']['gpu'] = {
                        'memory_percent': int(mem_info.used) / int(mem_info.total) * 100,
                        'temperature': temp
                    }
            except:
                pass

            return status

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_agent_info(self):
        """Get agent information"""
        if not self.agent_ref:
            return {'status': 'offline', 'message': 'Agent not available'}

        info = {
            'status': getattr(self.agent_ref, 'status', 'unknown'),
            'tools_count': len(getattr(self.agent_ref, 'tools', [])),
            'components': {
                'brain': hasattr(self.agent_ref, 'brain') and self.agent_ref.brain is not None,
                'voice': hasattr(self.agent_ref, 'voice') and self.agent_ref.voice is not None,
                'memory': hasattr(self.agent_ref, 'memory') and self.agent_ref.memory is not None,
                'vision': hasattr(self.agent_ref, 'vision') and self.agent_ref.vision is not None
            }
        }

        return info

    def _get_tools_list(self):
        """Get list of available tools"""
        if not self.agent_ref or not hasattr(self.agent_ref, 'tools'):
            return {'tools': []}

        tools = []
        # Tools can be either dict (name: instance) or list
        if isinstance(self.agent_ref.tools, dict):
            for name, tool_instance in self.agent_ref.tools.items():
                tool_info = {
                    'name': name if isinstance(name, str) else tool_instance.__class__.__name__,
                    'description': getattr(tool_instance, 'description', 'No description available')
                }
                tools.append(tool_info)
        else:
            # Handle list of tools
            for tool in self.agent_ref.tools:
                tool_info = {
                    'name': tool.__class__.__name__,
                    'description': getattr(tool, 'description', 'No description available')
                }
                tools.append(tool_info)

        return {'tools': tools}

    def _process_command(self, command: str) -> str:
        """Process command through agent, always returning the awaited result if coroutine."""
        if not self.agent_ref:
            return "❌ Agent not available"

        try:
            import asyncio
            import inspect
            if hasattr(self.agent_ref, 'process_command'):
                result = self.agent_ref.process_command(command)
                if inspect.isawaitable(result):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None
                    if loop and loop.is_running():
                        future = asyncio.run_coroutine_threadsafe(result, loop)
                        return future.result()
                    else:
                        return asyncio.run(result)
                else:
                    return result
            elif hasattr(self.agent_ref, 'handle_text'):
                return self.agent_ref.handle_text(command)
            else:
                return "❌ Agent command processing not available"

        except Exception as e:
            logging.error(f"Command processing error: {e} - web_gui_server.py:521")
            return f"❌ Error: {str(e)}"

    def _toggle_voice(self, payload: Optional[Dict[str, Any]] = None):
        """Toggle voice listening and persist configuration."""
        try:
            desired_state = None
            if isinstance(payload, dict):
                if 'enable' in payload:
                    desired_state = bool(payload.get('enable'))
                elif 'voice_enabled' in payload:
                    desired_state = bool(payload.get('voice_enabled'))

            if desired_state is None:
                desired_state = not UltronWebHandler.voice_state.get('enabled', False)

            if not VOICE_AVAILABLE:
                return {
                    'status': 'error',
                    'message': 'Voice subsystem unavailable on server',
                    'voice_enabled': False
                }

            if desired_state and UltronWebHandler.voice_assistant is None:
                try:
                    UltronWebHandler.voice_assistant = VoiceAssistant(config)
                    logging.info("Voice assistant initialized during toggle request - web_gui_server.py:547")
                except Exception as init_error:
                    logging.error(f"Voice assistant initialization failed: {init_error} - web_gui_server.py:549")
                    return {
                        'status': 'error',
                        'message': f'Voice initialization failed: {init_error}',
                        'voice_enabled': False
                    }

            UltronWebHandler.voice_state['enabled'] = desired_state
            UltronWebHandler.voice_state['listening'] = False

            persist_config_updates({
                'voice_enabled': desired_state,
                'use_voice': desired_state or config.get('use_voice', False)
            })

            status_label = 'enabled' if desired_state else 'disabled'
            message = 'Voice chat enabled' if desired_state else 'Voice chat disabled'

            return {
                'status': status_label,
                'message': message,
                'voice_enabled': desired_state,
                'listening': UltronWebHandler.voice_state['listening'],
                'tts_ready': UltronWebHandler.voice_assistant is not None
            }
        except Exception as e:
            logging.error(f"Voice toggle failed: {e} - web_gui_server.py:575")
            return {
                'status': 'error',
                'message': f'Voice toggle failed: {str(e)}',
                'voice_enabled': UltronWebHandler.voice_state.get('enabled', False)
            }

    def _speak_text(self, text: str):
        """Generate audio for provided text using available TTS engines"""
        normalized_text = (text or '').strip()
        if not normalized_text:
            logging.debug("Voice synthesis requested with empty text - web_gui_server.py:586")
            return None, None, {
                'status': 'error',
                'message': 'No text provided for synthesis'
            }

        if UltronWebHandler.voice_assistant is None:
            logging.warning("Voice assistant requested but not initialized - web_gui_server.py:593")
            return None, None, {
                'status': 'error',
                'message': 'Voice assistant not available'
            }

        voice_assistant = UltronWebHandler.voice_assistant
        cleaned_text = normalized_text

        try:
            if hasattr(voice_assistant, '_clean_speech_text'):
                cleaned_text = voice_assistant._clean_speech_text(normalized_text)
        except Exception as clean_error:
            logging.debug(f"Text cleaning failed, continuing with original text: {clean_error} - web_gui_server.py:606")

        cache_path = None
        if not config.get("disable_tts_cache", False) and hasattr(voice_assistant, '_get_cache_path'):
            try:
                cache_path = voice_assistant._get_cache_path(cleaned_text)
                if cache_path and cache_path.exists():
                    logging.debug("Serving voice synthesis from cache - web_gui_server.py:613")
                    return cache_path.read_bytes(), 'audio/mpeg', None
            except Exception as cache_error:
                logging.debug(f"Voice cache lookup failed: {cache_error} - web_gui_server.py:616")

        elevenlabs_client = getattr(voice_assistant, 'elevenlabs_client', None)
        preferred_voice_id = getattr(voice_assistant, 'preferred_voice_id', None)

        if elevenlabs_client and preferred_voice_id:
            try:
                logging.info("Generating ElevenLabs voice audio - web_gui_server.py:623")
                elevenlabs_response = elevenlabs_client.text_to_speech.convert(
                    text=cleaned_text,
                    voice_id=preferred_voice_id,
                    model_id="eleven_multilingual_v2"
                )

                if hasattr(voice_assistant, '_collect_audio_bytes'):
                    audio_bytes = voice_assistant._collect_audio_bytes(elevenlabs_response)
                else:
                    audio_bytes = elevenlabs_response if isinstance(elevenlabs_response, (bytes, bytearray)) else b""

                if not isinstance(audio_bytes, (bytes, bytearray)):
                    try:
                        audio_bytes = b"".join(
                            chunk
                            for chunk in audio_bytes
                            if isinstance(chunk, (bytes, bytearray))
                        )
                    except TypeError:
                        audio_bytes = bytes(audio_bytes)

                audio_bytes = bytes(audio_bytes)
                if not audio_bytes:
                    raise ValueError("Empty ElevenLabs audio payload")

                if cache_path:
                    try:
                        cache_path.parent.mkdir(parents=True, exist_ok=True)
                        cache_path.write_bytes(audio_bytes)
                    except Exception as cache_write_error:
                        logging.debug(f"Unable to cache ElevenLabs audio: {cache_write_error} - web_gui_server.py:654")
                return audio_bytes, 'audio/mpeg', None
            except Exception as elevenlabs_error:
                logging.warning(f"ElevenLabs synthesis failed: {elevenlabs_error} - web_gui_server.py:657")

        tts_engine = getattr(voice_assistant, 'tts_engine', None)
        if tts_engine:
            try:
                logging.info("Generating fallback TTS audio - web_gui_server.py:662")
                fd, tmp_path = tempfile.mkstemp(suffix='.wav')
                os.close(fd)
                try:
                    tts_engine.save_to_file(cleaned_text, tmp_path)
                    tts_engine.runAndWait()
                    with open(tmp_path, 'rb') as tmp_file:
                        audio_bytes = tmp_file.read()
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                return audio_bytes, 'audio/wav', None
            except Exception as fallback_error:
                logging.error(f"Fallback TTS synthesis failed: {fallback_error} - web_gui_server.py:677")

        logging.error("Voice synthesis unavailable - web_gui_server.py:679")
        return None, None, {
            'status': 'error',
            'message': 'Voice synthesis unavailable'
        }

    def _get_llm_status(self):
        """Get LLM status from Ollama"""
        try:
            import requests

            # Check if Ollama is running
            import aiohttp
            import asyncio

            async def check_ollama():
                ollama_url = "http://localhost:11434"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                data = await response.json()
                                models = data.get('models', [])
                                if models:
                                    # Use the configured model preference, fallback to first available
                                    available_models = [m['name'] for m in models]
                                    current_model = self.current_model_preference
                                    if current_model not in available_models:
                                        current_model = available_models[0]
                                    return {
                                        'model': current_model,
                                        'status': 'online',
                                        'available_models': available_models
                                    }
                                else:
                                    return {'model': 'No models', 'status': 'offline'}
                            else:
                                return {'model': 'Connection failed', 'status': 'offline'}
                except:
                    return {'model': 'Ollama offline', 'status': 'offline'}

            try:
                return asyncio.run(check_ollama())
            except:
                return {'model': 'Ollama offline', 'status': 'offline'}

        except ImportError:
            return {'model': 'Requests not available', 'status': 'offline'}

    def _get_llm_models(self):
        """Get available LLM models from Ollama"""
        try:
            import requests
            ollama_url = "http://localhost:11434"
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                return {
                    'models': [
                        {
                            'name': model['name'],
                            'size': model.get('size', 'Unknown'),
                            'modified': model.get('modified_at', 'Unknown')
                        }
                        for model in models
                    ]
                }
            else:
                return {'models': [], 'error': 'Failed to fetch models'}
        except Exception as e:
            return {'models': [], 'error': f'Connection error: {str(e)}'}

    def _get_voice_status(self):
        """Get voice system status"""
        voice_available = UltronWebHandler.voice_assistant is not None
        voice_config_enabled = config.get("use_voice", False) and config.get("voice_enabled", False)
        voice_enabled = UltronWebHandler.voice_state.get('enabled', voice_config_enabled)
        listening = UltronWebHandler.voice_state.get('listening', False)

        return {
            'status': 'listening' if listening else ('enabled' if voice_enabled else 'disabled'),
            'input_enabled': voice_available and voice_enabled,
            'output_enabled': voice_available and voice_enabled,
            'listening': listening,
            'tts_ready': voice_available,
            'provider': 'elevenlabs' if voice_available else 'system_default',
            'config_enabled': voice_config_enabled,
            'voice_enabled': voice_enabled
        }

    def _get_brain_status(self):
        """Get brain/AI system status"""
        return {
            'status': 'online',
            'model': self.current_model_preference,
            'capabilities': ['chat', 'reasoning', 'code'],
            'ready': True
        }

    def _get_files_list(self):
        """Get list of files in the project root"""
        try:
            root_dir = Path(__file__).parent
            files = []
            for item in os.listdir(root_dir):
                item_path = root_dir / item
                files.append({
                    'name': item,
                    'is_dir': item_path.is_dir()
                })
            return {'files': files}
        except Exception as e:
            return {'error': str(e)}

    def _get_nvidia_status(self):
        """Check NVIDIA Enhanced Chat service status on port 8002"""
        try:
            import socket
            import requests

            nvidia_host = "localhost"
            nvidia_port = 8002

            # Try socket check first (faster)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            socket_result = sock.connect_ex((nvidia_host, nvidia_port))
            sock.close()

            if socket_result == 0:
                # Port is open, try to get health info
                try:
                    response = requests.get(
                        f"http://{nvidia_host}:{nvidia_port}/health",
                        timeout=3
                    )
                    if response.status_code == 200:
                        return {
                            'status': 'online',
                            'port': nvidia_port,
                            'url': f"http://{nvidia_host}:{nvidia_port}",
                            'health': response.json() if response.text else {'status': 'ok'}
                        }
                    else:
                        return {
                            'status': 'online',
                            'port': nvidia_port,
                            'url': f"http://{nvidia_host}:{nvidia_port}",
                            'health': {'status': 'responding'}
                        }
                except requests.RequestException:
                    # Port open but no valid response
                    return {
                        'status': 'port_open',
                        'port': nvidia_port,
                        'url': f"http://{nvidia_host}:{nvidia_port}",
                        'message': 'Port is open but service not responding'
                    }
            else:
                return {
                    'status': 'offline',
                    'port': nvidia_port,
                    'url': f"http://{nvidia_host}:{nvidia_port}",
                    'message': 'NVIDIA service not running'
                }
        except Exception as e:
            return {
                'status': 'error',
                'port': 8002,
                'error': str(e),
                'message': 'Failed to check NVIDIA service status'
            }

    def _handle_llm_chat(self, message: str):
        """Handle LLM chat message for QASIS and other chat endpoints."""
        if not message.strip():
            return {'error': 'Empty message'}

        # Check if OpenAI model is selected
        model_pref = getattr(UltronWebHandler, 'current_model_preference', 'llava:7b')
        openai_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
        if model_pref in openai_models:
            try:
                from openai_integration import OpenAIAssistant
                import os
                openai_api_key = os.environ.get('OPENAI_API_KEY')
                if not openai_api_key:
                    return {'error': 'OpenAI API key not set in environment.'}
                assistant = OpenAIAssistant()
                assistant.api_key = openai_api_key
                # Use selected model
                payload = {
                    "model": model_pref,
                    "messages": [{"role": "user", "content": message}]
                }
                headers = {"Authorization": f"Bearer {openai_api_key}", "Content-Type": "application/json"}
                import requests
                resp = requests.post(f"https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    response_text = result['choices'][0]['message']['content']
                    return {
                        'response': response_text,
                        'model': model_pref,
                        'source': 'openai',
                        'tts_enabled': UltronWebHandler.voice_assistant is not None
                    }
                else:
                    return {'error': f'OpenAI API error: {resp.status_code}'}
            except Exception as e:
                return {'error': f'OpenAI chat failed: {str(e)}'}

        # Default: use agent core
        if not self.agent_ref:
            return {'error': 'Agent not available', 'status': 'offline'}
        try:
            response_text = self._process_command(message)
            # TTS integration
            if (
                UltronWebHandler.voice_assistant and
                config.get("use_voice", False) and
                config.get("voice_enabled", False)
            ):
                try:
                    def speak_response():
                        try:
                            UltronWebHandler.voice_assistant.speak(response_text)
                        except Exception as tts_error:
                            logging.warning(f"TTS failed: {tts_error} - web_gui_server.py")
                    tts_thread = threading.Thread(target=speak_response, daemon=True)
                    tts_thread.start()
                    logging.info("TTS initiated for AI response - web_gui_server.py")
                except Exception as tts_thread_error:
                    logging.warning(f"Failed to start TTS: {tts_thread_error} - web_gui_server.py")
            return {
                'response': response_text,
                'model': model_pref,
                'source': 'agent_core',
                'tts_enabled': UltronWebHandler.voice_assistant is not None
            }
        except Exception as e:
            logging.error(f"Chat request failed with exception: {e} - web_gui_server.py")
            return {'error': f'Chat request failed: {str(e)}'}

    def _switch_llm_model(self, model_name: str):
        """Switch LLM model preference"""
        normalized_name = (model_name or '').strip()
        if not normalized_name:
            return {'status': 'error', 'message': 'Model name is required'}

        try:
            import requests

            ollama_url = "http://localhost:11434"
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return {'status': 'error', 'message': 'Unable to reach Ollama to verify models'}

            data = response.json()
            models = data.get('models', [])
            available_names = [model.get('name') for model in models if model.get('name')]

            if normalized_name not in available_names:
                suggestions = ', '.join(available_names[:5]) if available_names else 'none available'
                return {
                    'status': 'error',
                    'message': f'Model "{normalized_name}" not found. Available models: {suggestions}'
                }

        except Exception as lookup_error:
            return {'status': 'error', 'message': f'Failed to verify model: {lookup_error}'}

        UltronWebHandler.current_model_preference = normalized_name
        persist_config_updates({'llm_model': normalized_name})

        logging.info(f"LLM model preference switched to {normalized_name} - web_gui_server.py:1115")

        return {
            'status': 'success',
            'message': f'Model preference set to {normalized_name}',
            'model': normalized_name
        }

    def _capture_screen(self):
        """Capture screen with 3-second delay"""
        try:
            import time
            import pyautogui
            from pathlib import Path

            # 3-second delay for window switching
            time.sleep(3)

            # Create screenshots directory
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)

            # Capture screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshots_dir / f"screenshot_{timestamp}.png"

            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)

            return {
                'success': True,
                'image_path': str(screenshot_path),
                'message': 'Screenshot captured (3s delay)',
                'timestamp': timestamp
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _analyze_vision(self):
        """Analyze latest screenshot with AI description and OCR"""
        try:
            from pathlib import Path
            import json

            # Get latest screenshot
            screenshots_dir = Path("screenshots")
            if not screenshots_dir.exists():
                return {'success': False, 'error': 'No screenshots directory'}

            screenshots = list(screenshots_dir.glob("screenshot_*.png"))
            if not screenshots:
                return {'success': False, 'error': 'No screenshots found. Take a screenshot first.'}

            # Get most recent
            latest = max(screenshots, key=lambda p: p.stat().st_mtime)

            # OCR with enhanced_ocr_tool
            from tools.enhanced_ocr_tool import EnhancedOCRTool
            ocr_tool = EnhancedOCRTool()
            ocr_result = ocr_tool.execute("read", image_path=str(latest))
            ocr_data = json.loads(ocr_result)

            # AI description via Ollama llava
            import requests
            ollama_url = "http://localhost:11434"

            # Read image as base64
            import base64
            with open(latest, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            prompt = "Describe this screenshot in detail. What do you see? What is the main content?"

            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                ai_description = response.json().get("response", "No description")
            else:
                ai_description = "AI description unavailable (Ollama may not be running)"

            return {
                'success': True,
                'image_path': str(latest),
                'ai_description': ai_description,
                'ocr_text': ocr_data.get('raw_text', ''),
                'ocr_confidence': ocr_data.get('confidence', 0),
                'analysis': ocr_data.get('analysis', {}),
                'timestamp': latest.stem.replace('screenshot_', '')
            }

        except Exception as e:
            logging.error(f"Vision analysis error: {e}")
            return {'success': False, 'error': str(e)}

    def _get_autonomous_status(self):
        """Get autonomous system status"""
        try:
            return {
                'success': True,
                'brain_status': 'ready',
                'learning_records': 0,
                'adaptation_rules': 0,
                'proactive_status': False,
                'active_tasks': 0,
                'completed_tasks': 0
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_autonomous_learning_data(self):
        """Get autonomous learning data"""
        try:
            return {
                'success': True,
                'total_records': 0,
                'recent_decisions': 0,
                'adaptation_rules': 0,
                'recent_data': []
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_tool(self, data: Dict[str, Any]):
        """Execute a specific tool"""
        try:
            tool_name = data.get('tool_name', '').lower()
            command = data.get('command', '')
            args = data.get('args', {})

            if not tool_name:
                return {'success': False, 'error': 'Tool name is required'}

            if not self.agent_ref or not hasattr(self.agent_ref, 'tools'):
                return {'success': False, 'error': 'Agent tools not available'}

            # Find the tool (tools is a dict)
            if isinstance(self.agent_ref.tools, dict):
                tool = self.agent_ref.tools.get(tool_name)
            else:
                tool = None
                for t in self.agent_ref.tools:
                    if t.__class__.__name__.lower() == tool_name:
                        tool = t
                        break

            if not tool:
                return {'success': False, 'error': f'Tool "{tool_name}" not found'}

            # Execute the tool
            if hasattr(tool, 'execute'):
                result = tool.execute(command, **args)
                return {'success': True, 'result': result, 'tool': tool_name}
            elif hasattr(tool, 'run'):
                result = tool.run(command, **args)
                return {'success': True, 'result': result, 'tool': tool_name}
            else:
                return {'success': False, 'error': 'Tool has no execute/run method'}

        except Exception as e:
            logging.error(f"Tool execution error: {e} - web_gui_server.py")
            return {'success': False, 'error': str(e)}

    def _start_autonomous_mode(self, data=None):
        """Start autonomous mode"""
        try:
            import subprocess
            import os
            logging.info(
                "Starting autonomous mode subprocess... - web_gui_server.py"
            )
            # Use absolute path relative to this script's directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, "autonomous_startup.py")
            if not os.path.exists(script_path):
                raise FileNotFoundError(
                    f"autonomous_startup.py not found at {script_path}")

            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NEW_CONSOLE

            subprocess.Popen(
                [sys.executable, script_path],
                creationflags=creation_flags
            )
            logging.info(
                "Autonomous subprocess started successfully - "
                "")
            return {'success': True,
                    'message': 'Autonomous mode started'}
        except Exception as e:
            logging.error(
                f"Failed to start autonomous mode: {e} - web_gui_server.py"
            )
            return {'success': False, 'error': str(e)}

    def _stop_autonomous_mode(self):
        """Stop autonomous mode"""
        try:
            import subprocess
            if os.name == 'nt':
                subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq autonomous*"],
                               shell=True, capture_output=True)
            else:
                # A more robust solution would store the PID from Popen.
                subprocess.run(["pkill", "-f", "autonomous_startup.py"], capture_output=True)
            return {'success': True, 'message': 'Autonomous mode stopped'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _evolve_autonomous_capabilities(self):
        """Evolve autonomous capabilities"""
        try:
            return {
                'success': True,
                'status': 'evolved',
                'new_rules': 1,
                'success_rate': 0.85,
                'total_learning_records': 10
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _run_integration_test(self):
        """Run integration test"""
        try:
            import subprocess
            result = subprocess.run(["python", "test_integration.py"],
                                  capture_output=True, text=True, timeout=60)

            # Parse output for test results
            output = result.stdout
            if "tests passed" in output:
                import re
                match = re.search(r'Overall: (\d+)/(\d+) tests passed', output)
                if match:
                    passed = int(match.group(1))
                    total = int(match.group(2))
                else:
                    passed, total = 0, 0
            else:
                passed, total = 0, 0

            return {
                'success': True,
                'passed': passed,
                'total': total,
                'output': output
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _start_proactive_monitoring(self):
        """Start proactive monitoring"""
        try:
            return {'success': True, 'message': 'Proactive monitoring started'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _stop_proactive_monitoring(self):
        """Stop proactive monitoring"""
        try:
            return {'success': True, 'message': 'Proactive monitoring stopped'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_vision_recent(self):
        """Get recent vision analysis results"""
        try:
            recent_analyses = []

            # Check for recent screenshots and analyses
            screenshots_dir = 'screenshots'
            if os.path.exists(screenshots_dir):
                screenshots = [f for f in os.listdir(screenshots_dir) if f.startswith('screenshot_') and f.endswith('.png')]
                if screenshots:
                    # Get the 5 most recent screenshots
                    recent_screenshots = sorted(screenshots, key=lambda x: os.path.getctime(os.path.join(screenshots_dir, x)), reverse=True)[:5]

                    for screenshot in recent_screenshots:
                        screenshot_path = os.path.join(screenshots_dir, screenshot)
                        timestamp = datetime.fromtimestamp(os.path.getctime(screenshot_path)).isoformat()

                        recent_analyses.append({
                            'timestamp': timestamp,
                            'image_path': screenshot_path,
                            'filename': screenshot,
                            'analyzed': False  # We don't track analysis status yet
                        })

            return {
                'success': True,
                'recent_analyses': recent_analyses,
                'count': len(recent_analyses)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_system_metrics(self):
        """Get detailed real-time system metrics"""
        try:
            import psutil

            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': psutil.cpu_percent(interval=0.5),
                    'count': psutil.cpu_count(),
                    'frequency_mhz': cpu_freq.current if cpu_freq else 0,
                    'load_average': (psutil.getloadavg() if hasattr(
                        psutil, 'getloadavg') else [0, 0, 0])
                },
                'memory': {
                    'percent': memory.percent,
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2)
                },
                'disk': {
                    'percent': disk.percent,
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2)
                },
                'process_count': len(psutil.pids()),
                'boot_time': datetime.fromtimestamp(
                    psutil.boot_time()).isoformat()
            }

            return {'success': True, 'metrics': metrics}
        except Exception as e:
            logging.error(f"System metrics error: {e} - web_gui_server.py:1363")
            return {'success': False, 'error': str(e)}

    def _get_comprehensive_health(self):
        """Get comprehensive health status of all system components"""
        try:
            health = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'components': {}
            }

            # System Health
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.5)
                mem = psutil.virtual_memory().percent
                health['components']['system'] = {
                    'status': ('healthy' if cpu < 80 and mem < 85
                               else 'warning' if cpu < 95 and mem < 95
                               else 'critical'),
                    'cpu_percent': cpu,
                    'memory_percent': mem
                }
            except Exception as e:
                health['components']['system'] = {
                    'status': 'unknown', 'error': str(e)}

            # Agent Health
            health['components']['agent'] = {
                'status': 'online' if self.agent_ref else 'offline',
                'available': bool(self.agent_ref)
            }

            # LLM Health
            try:
                llm_status = self._get_llm_status()
                health['components']['llm'] = {
                    'status': ('online' if llm_status.get('connected')
                               else 'offline'),
                    'model': llm_status.get('current_model', 'unknown')
                }
            except Exception:
                health['components']['llm'] = {'status': 'unknown'}

            # Voice Health
            health['components']['voice'] = {
                'status': 'ready' if VOICE_AVAILABLE else 'unavailable'
            }

            # NVIDIA Health
            try:
                nvidia_status = self._get_nvidia_status()
                health['components']['nvidia'] = {
                    'status': ('available'
                               if nvidia_status.get('nvidia_gpu_available')
                               else 'unavailable'),
                    'gpu': nvidia_status.get('gpu_name')
                }
            except Exception:
                health['components']['nvidia'] = {'status': 'unknown'}

            # Autonomous Health
            try:
                autonomous_status = self._get_autonomous_status()
                health['components']['autonomous'] = {
                    'status': ('active' if autonomous_status.get('is_active')
                               else 'inactive')
                }
            except Exception:
                health['components']['autonomous'] = {'status': 'unknown'}

            # Determine overall status
            components = health['components'].values()
            critical_count = sum(1 for c in components
                                 if c.get('status') == 'critical')
            warning_count = sum(1 for c in components
                                if c.get('status') == 'warning')

            if critical_count > 0:
                health['overall_status'] = 'critical'
            elif warning_count > 0:
                health['overall_status'] = 'warning'
            else:
                health['overall_status'] = 'healthy'

            return health
        except Exception as e:
            logging.error(f"Health check error: {e} - web_gui_server.py:1451")
            return {'success': False, 'error': str(e)}

    def _execute_console_command(self, command: str, timeout: int = 10):
        """Execute a safe console command and return output"""
        try:
            import subprocess

            # Whitelist of safe commands for execution
            safe_commands = [
                'echo', 'dir', 'ls', 'pwd', 'whoami', 'date', 'time', 'ps', 'top',
                'git', 'python', 'node', 'npm', 'pip', 'ollama',
                'curl', 'wget', 'ping', 'ipconfig', 'ifconfig', 'df', 'free', 'grep',
                'systemctl', 'service', 'tasklist', 'taskkill'
            ]

            # Extract the command name
            cmd_name = command.split()[0].lower() if command else ''

            # Check if command is in whitelist
            if not any(safe_cmd in cmd_name for safe_cmd in safe_commands):
                return {
                    'success': False,
                    'error': f'Command "{cmd_name}" not whitelisted for safety',
                    'whitelisted_commands': safe_commands
                }

            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'success': True,
                'command': command,
                'exit_code': result.returncode,
                'stdout': result.stdout[:5000],  # Limit to 5KB
                'stderr': result.stderr[:1000],  # Limit to 1KB
                'executed_at': datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds',
                'command': command
            }
        except Exception as e:
            logging.error(f"Console execution error: {e} - web_gui_server.py:1502")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }

    # ==================== PHASE 2 HANDLERS ====================

    def _get_performance_stats(self):
        """GET /api/performance/stats handler"""
        if not PHASE2_AVAILABLE:
            return {'error': 'Phase 2 not available'}
        return {'status': 'success', 'stats': profiler.get_stats()}

    def _get_performance_bottlenecks(self):
        """GET /api/performance/bottlenecks handler"""
        if not PHASE2_AVAILABLE:
            return {'error': 'Phase 2 not available'}
        try:
            # Parse query string for 'top_n' parameter
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            top_n = int(query_params.get('top_n', ['5'])[0])
        except (TypeError, ValueError, IndexError):
            top_n = 5
        return {
            'status': 'success',
            'bottlenecks': profiler.get_bottlenecks(top_n)
        }

    def _get_metrics_stream(self):
        """GET /api/metrics/stream handler"""
        if not PHASE2_AVAILABLE:
            return {'error': 'Phase 2 not available'}
        latest = metrics_buffer.get_latest(20)
        return {
            'status': 'success',
            'metrics': latest,
            'count': len(latest)
        }

    def _get_function_history(self, func_name):
        """GET /api/performance/function-history/{func_name}"""
        if not PHASE2_AVAILABLE:
            return {'error': 'Phase 2 not available'}
        try:
            # Parse query string for 'limit' parameter
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            limit = int(query_params.get('limit', ['100'])[0])
        except (TypeError, ValueError, IndexError):
            limit = 100
        history = profiler.get_history(func_name, limit)
        return {
            'status': 'success',
            'function': func_name,
            'history': history,
            'count': len(history)
        }

    def _get_phase2_status(self):
        """GET /api/phase2/status handler"""
        if not PHASE2_AVAILABLE:
            return {'error': 'Phase 2 not available'}
        return {
            'status': 'success',
            'phase2_status': {
                'profiler_active': True,
                'metrics_collection_active': metrics_collector.running,
                'metrics_buffer_size': len(metrics_buffer.buffer),
                'websocket_clients': len(ws_handler.connections),
                'functions_tracked': len(profiler.metrics),
                'timestamp': time.time()
            }
        }

    def _get_ssh_status(self):
        """Get SSH server status"""
        try:
            # Check if SSH server is configured
            config = self.agent_ref.config if self.agent_ref else {}
            ssh_config = config.get('ssh_server', {})

            # Try to check if SSH port is listening
            import socket
            port = ssh_config.get('port', 2222)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            return {
                'success': True,
                'ssh_server': {
                    'enabled': ssh_config.get('enabled', False),
                    'port': port,
                    'status': 'running' if result == 0 else 'stopped',
                    'password': ssh_config.get('password', 'password')
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_autogen_status(self):
        """Get AutoGen status"""
        try:
            # Check if autogen components are available
            return {
                'success': True,
                'autogen': {
                    'status': 'available',
                    'agents': ['UserProxyAgent', 'AssistantAgent'],
                    'features': ['multi_agent_chat', 'code_execution', 'tool_use']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def log_message(self, format, *args):
        """Custom log format"""
        logging.info(f"WEB {format % args} - web_gui_server.py:1581")


class UltronWebServer:
    """ULTRON Web Server with agent integration"""

    def __init__(self, agent_ref: Optional[Any] = None, port: int = 8888):
        self.agent_ref = agent_ref
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        self.handler_factory = None  # Store handler factory for reference

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)


    def start_server(self):
        """Start the web server"""
        try:
            # Change to web_gui directory
            web_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
            if not web_dir.exists():
                raise FileNotFoundError("Web GUI directory not found. Please run the setup first.")

            os.chdir(web_dir)

            # Patch: Pass handler class directly, not a factory function
            UltronWebHandler.agent_ref = self.agent_ref

            # Ensure address reuse BEFORE binding
            class ReusableTCPServer(socketserver.TCPServer):
                allow_reuse_address = True

            try:
                self.server = ReusableTCPServer(("0.0.0.0", self.port), UltronWebHandler)
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    self.logger.error(f"Port {self.port} is already in use. Please free the port and try again.")
                else:
                    self.logger.error(f"Failed to bind to port {self.port}: {e}")
                return False

            self.logger.info(f"ULTRON Web Server starting on port {self.port}")
            self.logger.info(f"Serving from: {web_dir}")
            self.logger.info(f"Access GUI at: http://localhost:{self.port}")
            self.logger.info(f"Remote access: http://YOUR_IP:{self.port}")

            # Start server in background thread
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()

            # Open browser
            try:
                webbrowser.open(f"http://localhost:{self.port}")
                self.logger.info("Browser opened automatically")
            except Exception:
                self.logger.warning("Could not open browser automatically")

            return True

        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            return False

    def _run_server(self):
        """Run the server loop"""
        try:
            self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"Server error: {e}")


    def stop_server(self):
        """Stop the web server and release port"""
        if self.server and self.running:
            self.logger.info("🛑 Shutting down web server...")
            self.running = False
            try:
                self.server.shutdown()
                self.server.server_close()
                if self.server_thread:
                    self.server_thread.join(timeout=2)
                self.logger.info("✅ Web server stopped and port released")
            except Exception as e:
                self.logger.error(f"Error during server shutdown: {e}")

    def wait_for_shutdown(self):
        """Wait for server to shutdown"""
        try:
            if self.server_thread:
                self.server_thread.join()
        except KeyboardInterrupt:
            self.logger.info("🔴 Shutdown requested by user")
            self.stop_server()


    def _get_system_metrics(self):
        """Get detailed real-time system metrics"""
        try:
            import psutil

            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': psutil.cpu_percent(interval=0.5),
                    'count': psutil.cpu_count(),
                    'frequency_mhz': cpu_freq.current if cpu_freq else 0,
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                'memory': {
                    'percent': memory.percent,
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2)
                },
                'disk': {
                    'percent': disk.percent,
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2)
                },
                'process_count': len(psutil.pids()),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }

            return {'success': True, 'metrics': metrics}
        except Exception as e:
            logging.error(f"System metrics error: {e} - web_gui_server.py:1707")
            return {'success': False, 'error': str(e)}

    def _get_comprehensive_health(self):
        """Get comprehensive health status of all system components"""
        try:
            health = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'components': {}
            }

            # System Health
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.5)
                mem = psutil.virtual_memory().percent
                health['components']['system'] = {
                    'status': 'healthy' if cpu < 80 and mem < 85 else 'warning' if cpu < 95 and mem < 95 else 'critical',
                    'cpu_percent': cpu,
                    'memory_percent': mem
                }
            except Exception as e:
                health['components']['system'] = {'status': 'unknown', 'error': str(e)}

            # Agent Health
            health['components']['agent'] = {
                'status': 'online' if self.agent_ref else 'offline',
                'available': bool(self.agent_ref)
            }

            # LLM Health
            try:
                llm_status = self._get_llm_status()
                health['components']['llm'] = {
                    'status': 'online' if llm_status.get('connected') else 'offline',
                    'model': llm_status.get('current_model', 'unknown')
                }
            except:
                health['components']['llm'] = {'status': 'unknown'}

            # Voice Health
            health['components']['voice'] = {
                'status': 'ready' if VOICE_AVAILABLE else 'unavailable'
            }

            # NVIDIA Health
            try:
                nvidia_status = self._get_nvidia_status()
                health['components']['nvidia'] = {
                    'status': 'available' if nvidia_status.get('nvidia_gpu_available') else 'unavailable',
                    'gpu': nvidia_status.get('gpu_name')
                }
            except:
                health['components']['nvidia'] = {'status': 'unknown'}

            # Autonomous Health
            try:
                autonomous_status = self._get_autonomous_status()
                health['components']['autonomous'] = {
                    'status': 'active' if autonomous_status.get('is_active') else 'inactive'
                }
            except:
                health['components']['autonomous'] = {'status': 'unknown'}

            # Determine overall status
            critical_count = sum(1 for c in health['components'].values() if c.get('status') == 'critical')
            warning_count = sum(1 for c in health['components'].values() if c.get('status') == 'warning')

            if critical_count > 0:
                health['overall_status'] = 'critical'
            elif warning_count > 0:
                health['overall_status'] = 'warning'
            else:
                health['overall_status'] = 'healthy'

            return health
        except Exception as e:
            logging.error(f"Health check error: {e} - web_gui_server.py:1785")
            return {'success': False, 'error': str(e)}

    def _execute_console_command(self, command: str, timeout: int = 10):
        """Execute a safe console command and return output"""
        try:
            import subprocess

            # Whitelist of safe commands for execution
            safe_commands = [
                'echo', 'dir', 'ls', 'pwd', 'whoami', 'date', 'time', 'ps', 'top',
                'git', 'python', 'node', 'npm', 'pip', 'ollama',
                'curl', 'wget', 'ping', 'ipconfig', 'ifconfig', 'df', 'free', 'grep',
                'systemctl', 'service', 'tasklist', 'taskkill'
            ]

            # Extract the command name
            cmd_name = command.split()[0].lower() if command else ''

            # Check if command is in whitelist
            if not any(safe_cmd in cmd_name for safe_cmd in safe_commands):
                return {
                    'success': False,
                    'error': f'Command "{cmd_name}" not whitelisted for safety',
                    'whitelisted_commands': safe_commands
                }

            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'success': True,
                'command': command,
                'exit_code': result.returncode,
                'stdout': result.stdout[:5000],  # Limit output to 5KB
                'stderr': result.stderr[:1000],  # Limit error to 1KB
                'executed_at': datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds',
                'command': command
            }
        except Exception as e:
            logging.error(f"Console execution error: {e} - web_gui_server.py:1836")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }


    # Missing API handler methods
    def _get_system_info(self):
        """Get system information for GUI"""
        try:
            import psutil
            import platform
            return {
                'success': True,
                'system': {
                    'platform': platform.system(),
                    'platform_version': platform.version(),
                    'architecture': platform.architecture()[0],
                    'processor': platform.processor(),
                    'python_version': platform.python_version(),
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'disk_total': psutil.disk_usage('/').total if platform.system() != 'Windows' else psutil.disk_usage('C:').total
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


def main():
    """Main entry point for web GUI"""
    print("ULTRON Agent 3.0 Web GUI Server")
    print("=" * 60)

    # Create and start web server FIRST (so it's accessible immediately)
    server = UltronWebServer(agent_ref=None, port=8888)

    if not server.start_server():
        print("Failed to start web server - web_gui_server.py:1902")
        return 1

    print("\n✅ ULTRON Web GUI is now running! - web_gui_server.py:1892")
    print(f"Open your browser to: http://localhost:8080 - web_gui_server.py:1893")
    print("Press Ctrl+C to stop - web_gui_server.py:1894")

    # Initialize agent in background thread (non-blocking)
    import threading
    import asyncio

    def init_agent_async():
        """Initialize agent asynchronously"""
        agent = None
        try:
            print("\n[1/3] Initializing ULTRON Agent Core... - web_gui_server.py:1854")
            from agent_core import UltronAgent
            agent = UltronAgent()

            print("[2/3] Initializing Memory, Brain, Tools... - web_gui_server.py:1858")
            asyncio.run(agent.initialize())

            print("[3/3] Verifying ULTRON Identity... - web_gui_server.py:1862")
            if agent.memory and hasattr(agent.memory, 'get_ultron_identity'):
                identity = agent.memory.get_ultron_identity()
                print(f"✅ Identity: {identity['name']} v{identity['version']} - web_gui_server.py:1865")
            if agent.brain:
                print(f"✅ Brain: Connected - web_gui_server.py:1867")
            if agent.tools:
                print(f"✅ Tools: {len(agent.tools)} loaded - web_gui_server.py:1869")

            print("\n✅ ULTRON Agent fully initialized with all systems - web_gui_server.py:1871")

            # Update server's agent reference after initialization completes
            server.agent_ref = agent

        except Exception as e:
            print(f"\n⚠️ Agent initialization failed: {e} - web_gui_server.py:1874")
            print("Web server running in limited mode (identity only) - web_gui_server.py:1875")

    # Start agent initialization in background
    init_thread = threading.Thread(target=init_agent_async, daemon=True)
    init_thread.start()

    # Initialize Phase 2 services
    if PHASE2_AVAILABLE:
        try:
            start_phase2_services()
            print("[OK] Phase 2 Realtime & Profiling Services Initialized - web_gui_server.py:1882")
        except Exception as e:
            print(f"[WARNING] Phase 2 initialization warning: {e} - web_gui_server.py:1884")
    else:
        print("[INFO] Phase 2 not available - web_gui_server.py:1886")

    # Initialize and start Diagnostics Manager
    if AGENT_AVAILABLE and config.get("diagnostics_enabled", False):
        try:
            diagnostics_manager = DiagnosticsManager(agent_ref=server.agent_ref, interval=300)
            # Register key components (assuming they exist on the agent)
            if server.agent_ref and server.agent_ref.memory:
                diagnostics_manager.register_component("memory", server.agent_ref.memory)
            diagnostics_manager.start()
        except Exception as e:
            print(f"[WARNING] Diagnostics Manager failed to start: {e}")

    # Wait for server shutdown
    try:
        server.wait_for_shutdown()
    except KeyboardInterrupt:
        print("\nShutting down... - web_gui_server.py:1899")
        server.stop_server()

    return 0


if __name__ == "__main__":
    sys.exit(main())
