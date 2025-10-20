"""
Mobile/Web Interface Tool for ULTRON Agent

Provides user-friendly interfaces for mobile and web access
"""

import os
import threading
import time
import webbrowser
from PIL import Image

# Add project root to Python path for imports
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision

try:
    from flask import Flask, request, jsonify, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    log_error("mobile_web_interface", "Flask not available. Install with: pip install flask")

from .tool_interface import ToolInterface


class MobileWebInterfaceTool(ToolInterface):
    """
    Tool for creating unified Pokédex-styled web interface for ULTRON Agent
    """

    name = "Pokédex Web Interface Tool"
    description = "Create unified Pokédex-styled web interface for ULTRON Agent access"

    def __init__(self, config=None, memory=None):
        # Store config and memory for compatibility with agent_core
        self.config = config
        self.memory = memory

        # Use fixed port 8001 for API server
        self.port = 8001

        self.app = None
        self.server_thread = None
        self.is_running = False
        self.current_model = 'qwen3-coder:480b-cloud'  # Default model

        # Initialize Flask app
        self._initialize_flask_app()

        # Auto-start the server in background
        self._auto_start_server()

    def _initialize_flask_app(self):
        """Initialize the Flask application with all routes"""
        if not FLASK_AVAILABLE:
            log_error("mobile_web_interface", "Flask not available - cannot initialize web interface")
            return

        try:
            self.app = Flask(__name__)

            # Add routes
            self._setup_routes()

            log_info("mobile_web_interface", "Flask app initialized successfully")
        except Exception as e:
            log_error("mobile_web_interface", f"Failed to initialize Flask app: {e}")
            self.app = None

    def _auto_start_server(self):
        """Automatically start the Flask server in background"""
        if not self.app:
            log_error("mobile_web_interface", "Cannot auto-start server - Flask app not initialized")
            return

        if self.is_running:
            log_info("mobile_web_interface", "Server already running")
            return

        try:
            def run_server():
                log_info("mobile_web_interface", f"Auto-starting web interface server on port {self.port}")
                self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True

            # Give server time to start
            time.sleep(1)

            log_info("mobile_web_interface", f"Web interface server auto-started successfully on port {self.port}")
        except Exception as e:
            log_error("mobile_web_interface", f"Failed to auto-start server: {e}")

    def _setup_routes(self):
        """Setup all Flask routes"""
        if not self.app:
            return

        # Vision routes
        @self.app.route('/api/vision/capture', methods=['POST'])
        def vision_capture():
            try:
                print("Vision capture endpoint called - mobile_web_interface_tool.py:113")
                # Add project root to Python path
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                # Import at module level to avoid scoping issues
                from vision import Vision
                from PIL import Image
                import base64
                from io import BytesIO

                vision = Vision()
                screen, filepath = vision.capture_screen()
                print(f"Screen captured to: {filepath} - mobile_web_interface_tool.py:129")

                # Convert image to base64 for web display
                buffer = BytesIO()
                screen.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                image_url = f"data:image/png;base64,{img_base64}"
                print("Image converted to base64 - mobile_web_interface_tool.py:136")

                return jsonify({
                    'action': 'capture',
                    'status': 'completed',
                    'image_path': filepath,
                    'image_url': image_url,
                    'timestamp': time.time()
                })
            except Exception as e:
                print(f"Vision capture failed: {e} - mobile_web_interface_tool.py:146")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'capture',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500

        @self.app.route('/api/vision/analyze', methods=['POST'])
        def vision_analyze():
            try:
                print("Vision analyze endpoint called - mobile_web_interface_tool.py:159")
                # Add project root to Python path
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                # Import at module level to avoid scoping issues
                from vision import Vision
                from multimodal_vision_tool import MultimodalVisionTool
                from PIL import Image

                vision = Vision()
                multimodal_vision = MultimodalVisionTool()

                # Get the latest screenshot
                screenshots_dir = "screenshots"
                if os.path.exists(screenshots_dir):
                    screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
                    if screenshots:
                        # Get the most recent screenshot
                        latest_screenshot = max(screenshots, key=lambda x: os.path.getctime(os.path.join(screenshots_dir, x)))
                        image_path = os.path.join(screenshots_dir, latest_screenshot)
                        print(f"Analyzing screenshot: {image_path} - mobile_web_interface_tool.py:183")

                        # Perform OCR
                        screen = Image.open(image_path)
                        ocr_text = vision.perform_ocr(screen)
                        print(f"OCR completed, text length: {len(ocr_text)} - mobile_web_interface_tool.py:188")

                        # Perform AI analysis
                        ai_analysis = multimodal_vision.analyze_image(image_path)
                        print(f"AI analysis completed, length: {len(str(ai_analysis))} - mobile_web_interface_tool.py:192")

                        return jsonify({
                            'action': 'analyze',
                            'status': 'completed',
                            'image_path': image_path,
                            'ocr_text': ocr_text,
                            'analysis': ai_analysis,  # Changed from ai_analysis to analysis
                            'timestamp': time.time()
                        })
                    else:
                        print("No screenshots found for analysis - mobile_web_interface_tool.py:203")
                        return jsonify({
                            'action': 'analyze',
                            'status': 'failed',
                            'error': 'No screenshots found. Please capture a screen first.',
                            'timestamp': time.time()
                        }), 400
                else:
                    print("Screenshots directory not found - mobile_web_interface_tool.py:211")
                    return jsonify({
                        'action': 'analyze',
                        'status': 'failed',
                        'error': 'Screenshots directory not found.',
                        'timestamp': time.time()
                    }), 400
            except Exception as e:
                print(f"Vision analyze failed: {e} - mobile_web_interface_tool.py:219")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'analyze',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500
            except Exception as e:
                print(f"Vision analyze failed: {e} - mobile_web_interface_tool.py:229")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'analyze',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500

        # Other routes (Stable Diffusion, NVIDIA, etc.)
        @self.app.route('/api/stable-diffusion/generate', methods=['POST'])
        def stable_diffusion_generate():
            try:
                print("Stable Diffusion generate endpoint called - mobile_web_interface_tool.py:243")
                # Add project root to Python path
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                # Import the stable diffusion tool
                from tools.stable_diffusion_tool import StableDiffusionTool

                data = request.get_json() or {}
                prompt = data.get('prompt', '')
                negative_prompt = data.get('negative_prompt', '')
                width = data.get('width', 512)
                height = data.get('height', 512)
                steps = data.get('steps', 20)
                cfg_scale = data.get('cfg_scale', 7.0)
                sampler_name = data.get('sampler_name', 'Euler a')

                if not prompt:
                    return jsonify({
                        'action': 'generate',
                        'status': 'failed',
                        'error': 'No prompt provided',
                        'timestamp': time.time()
                    }), 400

                # Create tool instance and generate
                sd_tool = StableDiffusionTool()
                command = f"generate image: {prompt}"
                if negative_prompt:
                    command += f" --negative {negative_prompt}"
                if width != 512 or height != 512:
                    command += f" --size {width}x{height}"
                if steps != 20:
                    command += f" --steps {steps}"
                if cfg_scale != 7.0:
                    command += f" --scale {cfg_scale}"
                if sampler_name != 'Euler a':
                    command += f" --sampler {sampler_name}"

                result = sd_tool.execute(command)

                # Parse result to extract image path or base64
                if "Generated image saved to:" in result:
                    # Extract path from result
                    import re
                    path_match = re.search(r"Generated image saved to: (.+)", result)
                    if path_match:
                        image_path = path_match.group(1).strip()
                        # Convert to base64 for web display
                        try:
                            from PIL import Image
                            import base64
                            from io import BytesIO

                            image = Image.open(image_path)
                            buffer = BytesIO()
                            image.save(buffer, format='PNG')
                            img_base64 = base64.b64encode(buffer.getvalue()).decode()
                            image_url = f"data:image/png;base64,{img_base64}"

                            return jsonify({
                                'action': 'generate',
                                'status': 'completed',
                                'image_path': image_path,
                                'image_url': image_url,
                                'prompt': prompt,
                                'parameters': {
                                    'negative_prompt': negative_prompt,
                                    'width': width,
                                    'height': height,
                                    'steps': steps,
                                    'cfg_scale': cfg_scale,
                                    'sampler_name': sampler_name
                                },
                                'timestamp': time.time()
                            })
                        except Exception as img_error:
                            print(f"Image processing error: {img_error} - mobile_web_interface_tool.py:323")
                            return jsonify({
                                'action': 'generate',
                                'status': 'completed',
                                'image_path': image_path,
                                'prompt': prompt,
                                'message': result,
                                'timestamp': time.time()
                            })
                else:
                    # Return text result
                    return jsonify({
                        'action': 'generate',
                        'status': 'completed',
                        'message': result,
                        'prompt': prompt,
                        'timestamp': time.time()
                    })

            except Exception as e:
                print(f"Stable Diffusion generate failed: {e} - mobile_web_interface_tool.py:343")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'generate',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500

        @self.app.route('/api/nvidia/status')
        def nvidia_status():
            # Placeholder for NVIDIA status
            return jsonify({
                'available': False,
                'gpu_count': 0,
                'driver_version': None,
                'timestamp': time.time()
            })

        @self.app.route('/api/files')
        def get_files():
            # Placeholder for file listing
            return jsonify({
                'files': [],
                'directories': [],
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/status')
        def autogen_status():
            # Placeholder for AutoGen status
            return jsonify({
                'running': False,
                'agents': [],
                'workflows': [],
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/start', methods=['POST'])
        def autogen_start():
            # Placeholder for AutoGen start
            log_info("mobile_web_interface", "AutoGen start requested")
            return jsonify({
                'action': 'start',
                'status': 'initiated',
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/stop', methods=['POST'])
        def autogen_stop():
            # Placeholder for AutoGen stop
            log_info("mobile_web_interface", "AutoGen stop requested")
            return jsonify({
                'action': 'stop',
                'status': 'completed',
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/create-agent', methods=['POST'])
        def autogen_create_agent():
            # Placeholder for agent creation
            log_info("mobile_web_interface", "AutoGen create agent requested")
            return jsonify({
                'action': 'create_agent',
                'status': 'completed',
                'agent_id': None,
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/create-workflow', methods=['POST'])
        def autogen_create_workflow():
            # Placeholder for workflow creation
            log_info("mobile_web_interface", "AutoGen create workflow requested")
            return jsonify({
                'action': 'create_workflow',
                'status': 'completed',
                'workflow_id': None,
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/command', methods=['POST'])
        def autogen_command():
            # Placeholder for AutoGen command
            log_info("mobile_web_interface", "AutoGen command requested")
            return jsonify({
                'action': 'command',
                'status': 'completed',
                'result': None,
                'timestamp': time.time()
            })

        @self.app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        self._initialize_interface()

        # Auto-start the web interface when tool is loaded
        # Commented out to prevent blocking during agent initialization
        # try:
        #     self.start_interface()
        # except Exception as e:
        #     log_error("mobile_web_interface", f"Failed to auto-start web interface: {e}")

    def _initialize_interface(self):
        """Initialize the web interface"""
        if not FLASK_AVAILABLE:
            log_error("mobile_web_interface", "Flask not available for web interface")
            return

        try:
            # Configure static file serving from Pokédex GUI directory
            import os
            static_dir = os.path.join(os.path.dirname(__file__), '..', 'gui', 'ultron_enhanced', 'web')
            self.app = Flask(__name__, static_folder=static_dir, static_url_path='')
            self._setup_routes()
            print("Web interface initialized with Pokédex GUI - mobile_web_interface_tool.py:462")
        except Exception as e:
            print(f"Interface initialization failed: {e} - mobile_web_interface_tool.py:464")

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def home():
            return render_template_string(self._get_html_template())

        @self.app.route('/api/command', methods=['POST'])
        def execute_command():
            try:
                data = request.get_json()
                command = data.get('command', '')

                if not command:
                    return jsonify({'error': 'No command provided'}), 400

                # Import and use agent core for command execution
                from agent_core import UltronAgent
                import asyncio

                async def run_async():
                    agent = UltronAgent()
                    await agent.initialize()
                    result = await agent.process_command(command)
                    # Debug: check for coroutines in result
                    import inspect
                    def check_for_coroutines(obj, path=""):
                        if inspect.iscoroutine(obj):
                            log_error("mobile_web_interface", f"Coroutine found at {path}: {obj}")
                            raise ValueError(f"Coroutine found at {path}: {obj}")
                        elif isinstance(obj, dict):
                            for k, v in obj.items():
                                check_for_coroutines(v, f"{path}.{k}")
                        elif isinstance(obj, list):
                            for i, v in enumerate(obj):
                                check_for_coroutines(v, f"{path}[{i}]")
                    try:
                        check_for_coroutines(result)
                    except ValueError as e:
                        log_error("mobile_web_interface", f"Coroutine check failed: {e}")
                        # Try to convert any coroutines to their results
                        def await_coroutines(obj):
                            if inspect.iscoroutine(obj):
                                try:
                                    return asyncio.run(obj)
                                except:
                                    return str(obj)
                            elif isinstance(obj, dict):
                                return {k: await_coroutines(v) for k, v in obj.items()}
                            elif isinstance(obj, list):
                                return [await_coroutines(item) for item in obj]
                            else:
                                return obj
                        result = await_coroutines(result)
                    return result

                result = asyncio.run(run_async())

                log_info("mobile_web_interface", f"Result type: {type(result)}")

                return jsonify({
                    'command': command,
                    'result': result,
                    'timestamp': time.time()
                })

            except Exception as e:
                log_error("mobile_web_interface", f"Command execution failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'status': 'running' if self.is_running else 'stopped',
                'port': self.port,
                'timestamp': time.time()
            })

        @self.app.route('/api/tools')
        def get_tools():
            try:
                from agent_core import UltronAgent
                agent = UltronAgent()
                tools = agent.list_tools()
                return jsonify({'tools': tools})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/llm/chat', methods=['POST'])
        def llm_chat():
            try:
                data = request.get_json()
                message = data.get('message', '')

                if not message:
                    return jsonify({'error': 'No message provided'}), 400

                # Try to get response from Ollama or other LLM
                try:
                    import requests
                    # Get the model from config or use default
                    try:
                        # Handle both dict-style and Pydantic model config
                        if hasattr(self.config, 'get'):
                            model = self.config.get('llm_model', self.config.get('default_model_name', 'qwen3-coder:480b-cloud'))
                        else:
                            model = getattr(self.config, 'default_model_name', getattr(self.config, 'llm_model', 'qwen3-coder:480b-cloud'))
                    except:
                        model = 'qwen3-coder:480b-cloud'

                    # Prepend ULTRON identity to ensure consistent identification
                    ultron_message = f"You are ULTRON AI, an autonomous AI designed to build the ultron_agent project. Your objective is to maintain, enhance and improve this project. You will optimise and add additional functionality to add value to the project. Enhance, evolve, improve. https://github.com/dqikfox/ultron_agent\n\nAlways respond in the format:\n🤖\nULTRON AI\n[your response]\n\n{message}"

                    # Try Ollama first
                    ollama_response = requests.post(
                        'http://localhost:11434/api/generate',
                        json={
                            'model': model,
                            'prompt': ultron_message,
                            'stream': False
                        },
                        timeout=30
                    )

                    if ollama_response.status_code == 200:
                        result = ollama_response.json()
                        response_text = result.get('response', 'No response from AI')
                    else:
                        response_text = f"Ollama error: {ollama_response.status_code}"

                except Exception as e:
                    log_error("mobile_web_interface", f"Ollama request failed: {e}")
                    response_text = f"AI service unavailable: {str(e)}"

                return jsonify({
                    'response': response_text,
                    'timestamp': time.time()
                })

            except Exception as e:
                log_error("mobile_web_interface", f"LLM chat failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/voice/status')
        def voice_status():
            return jsonify({
                'status': 'available',
                'elevenlabs': True,
                'pyttsx3': True,
                'timestamp': time.time()
            })

        @self.app.route('/api/brain/status')
        def brain_status():
            # Get the actual model from config
            try:
                # Debug: log config type and attributes
                log_info("mobile_web_interface", f"Config type: {type(self.config)}")
                if hasattr(self.config, '__dict__'):
                    log_info("mobile_web_interface", f"Config dict: {self.config.__dict__}")
                elif hasattr(self.config, 'get'):
                    log_info("mobile_web_interface", f"Config keys: {list(self.config.keys()) if hasattr(self.config, 'keys') else 'no keys'}")

                # Handle both dict-style and Pydantic model config
                if hasattr(self.config, 'get'):
                    model = self.config.get('llm_model', self.config.get('default_model_name', 'qwen3-coder:480b-cloud'))
                else:
                    model = getattr(self.config, 'default_model_name', getattr(self.config, 'llm_model', 'qwen3-coder:480b-cloud'))

                log_info("mobile_web_interface", f"Resolved model: {model}")
            except Exception as e:
                log_error("mobile_web_interface", f"Error getting model from config: {e}")
                model = 'qwen3-coder:480b-cloud'
            return jsonify({
                'status': 'active',
                'model': model,
                'ollama_running': True,
                'timestamp': time.time()
            })

        @self.app.route('/api/llm/status')
        def llm_status():
            try:
                import requests
                # Check if Ollama is running
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                ollama_running = response.status_code == 200
                models = []
                if ollama_running:
                    try:
                        models_data = response.json()
                        models = [model['name'] for model in models_data.get('models', [])]
                    except:
                        models = ['unknown']
            except:
                ollama_running = False
                models = []

            result = {
                'status': 'online' if ollama_running else 'offline',
                'model': self.current_model if ollama_running else 'No Model',
                'available_models': models,
                'ollama_running': ollama_running,
                'timestamp': time.time()
            }
            log_info("mobile_web_interface", f"LLM status response: {result}")
            return jsonify(result)

        @self.app.route('/api/llm/models')
        def get_llm_models():
            try:
                import requests
                # Get available models from Ollama
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    models = [model['name'] for model in models_data.get('models', [])]
                else:
                    models = ['qwen3-coder:480b-cloud']  # fallback
            except:
                models = ['qwen3-coder:480b-cloud']  # fallback

            return jsonify({
                'models': models,
                'current_model': 'qwen3-coder:480b-cloud',
                'timestamp': time.time()
            })

        @self.app.route('/api/llm/switch-model', methods=['POST'])
        def switch_llm_model():
            try:
                data = request.get_json()
                model_name = data.get('model', '')

                if not model_name:
                    return jsonify({'error': 'No model specified'}), 400

                # Update current model
                self.current_model = model_name
                log_info("mobile_web_interface", f"Model switch requested to: {model_name}")

                return jsonify({
                    'success': True,
                    'message': f'Switched to model: {model_name}',
                    'model': model_name,
                    'timestamp': time.time()
                })

            except Exception as e:
                log_error("mobile_web_interface", f"Model switch failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/tools/status')
        def get_tools_status():
            try:
                # Get available tools from agent core
                from agent_core import UltronAgent
                agent = UltronAgent()
                tools = agent.list_tools()
                return jsonify({
                    'tools': tools,
                    'count': len(tools),
                    'timestamp': time.time()
                })
            except Exception as e:
                return jsonify({
                    'tools': [],
                    'count': 0,
                    'error': str(e),
                    'timestamp': time.time()
                })

        @self.app.route('/api/power/shutdown', methods=['POST'])
        def power_shutdown():
            # Placeholder for shutdown functionality
            log_info("mobile_web_interface", "Shutdown requested")
            return jsonify({
                'action': 'shutdown',
                'status': 'initiated',
                'timestamp': time.time()
            })

        @self.app.route('/api/power/restart', methods=['POST'])
        def power_restart():
            # Placeholder for restart functionality
            log_info("mobile_web_interface", "Restart requested")
            return jsonify({
                'action': 'restart',
                'status': 'initiated',
                'timestamp': time.time()
            })

        @self.app.route('/api/power/sleep', methods=['POST'])
        def power_sleep():
            # Placeholder for sleep functionality
            log_info("mobile_web_interface", "Sleep requested")
            return jsonify({
                'action': 'sleep',
                'status': 'initiated',
                'timestamp': time.time()
            })

        @self.app.route('/api/test', methods=['GET'])
        def test_route():
            log_info("mobile_web_interface", "Test route called")
            try:
                from vision import Vision
                log_info("mobile_web_interface", "Vision import successful")
                return jsonify({'status': 'ok', 'message': 'Vision import works'})
            except Exception as e:
                log_error("mobile_web_interface", f"Vision import failed: {e}")
                import traceback
                log_error("mobile_web_interface", f"Traceback: {traceback.format_exc()}")
                return jsonify({'status': 'error', 'message': str(e)})

        @self.app.route('/api/vision/capture', methods=['POST'])
        def vision_capture():
            try:
                print("Vision capture endpoint called - mobile_web_interface_tool.py:784")
                # Add project root to Python path
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                # Import at module level to avoid scoping issues
                from vision import Vision
                from PIL import Image
                import base64
                from io import BytesIO

                vision = Vision()
                screen, filepath = vision.capture_screen()
                print(f"Screen captured to: {filepath} - mobile_web_interface_tool.py:800")

                # Convert image to base64 for web display
                buffer = BytesIO()
                screen.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                image_url = f"data:image/png;base64,{img_base64}"
                print("Image converted to base64 - mobile_web_interface_tool.py:807")

                return jsonify({
                    'action': 'capture',
                    'status': 'completed',
                    'image_path': filepath,
                    'image_url': image_url,
                    'timestamp': time.time()
                })
            except Exception as e:
                print(f"Vision capture failed: {e} - mobile_web_interface_tool.py:817")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'capture',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500

        @self.app.route('/api/vision/analyze', methods=['POST'])
        def vision_analyze():
            try:
                print("Vision analyze endpoint called - mobile_web_interface_tool.py:830")
                # Add project root to Python path
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                # Import at module level to avoid scoping issues
                from vision import Vision
                from multimodal_vision_tool import MultimodalVisionTool
                from PIL import Image

                vision = Vision()
                multimodal_vision = MultimodalVisionTool()

                # Get the latest screenshot
                screenshots_dir = "screenshots"
                if os.path.exists(screenshots_dir):
                    screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
                    if screenshots:
                        # Get the most recent screenshot
                        latest_screenshot = max(screenshots, key=lambda x: os.path.getctime(os.path.join(screenshots_dir, x)))
                        image_path = os.path.join(screenshots_dir, latest_screenshot)
                        print(f"Analyzing screenshot: {image_path} - mobile_web_interface_tool.py:854")

                        # Perform OCR
                        screen = Image.open(image_path)
                        ocr_text = vision.perform_ocr(screen)
                        print(f"OCR completed, text length: {len(ocr_text)} - mobile_web_interface_tool.py:859")

                        # Perform AI analysis
                        ai_analysis = multimodal_vision.analyze_image(image_path)
                        print(f"AI analysis completed, length: {len(str(ai_analysis))} - mobile_web_interface_tool.py:863")

                        return jsonify({
                            'action': 'analyze',
                            'status': 'completed',
                            'image_path': image_path,
                            'ocr_text': ocr_text,
                            'analysis': ai_analysis,  # Changed from ai_analysis to analysis
                            'timestamp': time.time()
                        })
                    else:
                        print("No screenshots found for analysis - mobile_web_interface_tool.py:874")
                        return jsonify({
                            'action': 'analyze',
                            'status': 'failed',
                            'error': 'No screenshots found. Please capture a screen first.',
                            'timestamp': time.time()
                        }), 400
                else:
                    print("Screenshots directory not found - mobile_web_interface_tool.py:882")
                    return jsonify({
                        'action': 'analyze',
                        'status': 'failed',
                        'error': 'Screenshots directory not found.',
                        'timestamp': time.time()
                    }), 400
            except Exception as e:
                print(f"Vision analyze failed: {e} - mobile_web_interface_tool.py:890")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'analyze',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500
            except Exception as e:
                print(f"Vision analyze failed: {e} - mobile_web_interface_tool.py:900")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'analyze',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500

        @self.app.route('/api/stable-diffusion/generate', methods=['POST'])
        def stable_diffusion_generate():
            try:
                print("Stable Diffusion generate endpoint called - mobile_web_interface_tool.py:913")
                # Add project root to Python path
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                # Import the stable diffusion tool
                from tools.stable_diffusion_tool import StableDiffusionTool

                data = request.get_json() or {}
                prompt = data.get('prompt', '')
                negative_prompt = data.get('negative_prompt', '')
                width = data.get('width', 512)
                height = data.get('height', 512)
                steps = data.get('steps', 20)
                cfg_scale = data.get('cfg_scale', 7.0)
                sampler_name = data.get('sampler_name', 'Euler a')

                if not prompt:
                    return jsonify({
                        'action': 'generate',
                        'status': 'failed',
                        'error': 'No prompt provided',
                        'timestamp': time.time()
                    }), 400

                # Create tool instance and generate
                sd_tool = StableDiffusionTool()
                command = f"generate image: {prompt}"
                if negative_prompt:
                    command += f" --negative {negative_prompt}"
                if width != 512 or height != 512:
                    command += f" --size {width}x{height}"
                if steps != 20:
                    command += f" --steps {steps}"
                if cfg_scale != 7.0:
                    command += f" --scale {cfg_scale}"
                if sampler_name != 'Euler a':
                    command += f" --sampler {sampler_name}"

                result = sd_tool.execute(command)

                # Parse result to extract image path or base64
                if "Generated image saved to:" in result:
                    # Extract path from result
                    import re
                    path_match = re.search(r"Generated image saved to: (.+)", result)
                    if path_match:
                        image_path = path_match.group(1).strip()
                        # Convert to base64 for web display
                        try:
                            from PIL import Image
                            import base64
                            from io import BytesIO

                            image = Image.open(image_path)
                            buffer = BytesIO()
                            image.save(buffer, format='PNG')
                            img_base64 = base64.b64encode(buffer.getvalue()).decode()
                            image_url = f"data:image/png;base64,{img_base64}"

                            return jsonify({
                                'action': 'generate',
                                'status': 'completed',
                                'image_path': image_path,
                                'image_url': image_url,
                                'prompt': prompt,
                                'parameters': {
                                    'negative_prompt': negative_prompt,
                                    'width': width,
                                    'height': height,
                                    'steps': steps,
                                    'cfg_scale': cfg_scale,
                                    'sampler_name': sampler_name
                                },
                                'timestamp': time.time()
                            })
                        except Exception as img_error:
                            print(f"Image processing error: {img_error} - mobile_web_interface_tool.py:993")
                            return jsonify({
                                'action': 'generate',
                                'status': 'completed',
                                'image_path': image_path,
                                'prompt': prompt,
                                'message': result,
                                'timestamp': time.time()
                            })
                else:
                    # Return text result
                    return jsonify({
                        'action': 'generate',
                        'status': 'completed',
                        'message': result,
                        'prompt': prompt,
                        'timestamp': time.time()
                    })

            except Exception as e:
                print(f"Stable Diffusion generate failed: {e} - mobile_web_interface_tool.py:1013")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'action': 'generate',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500

        @self.app.route('/api/nvidia/status')
        def nvidia_status():
            # Placeholder for NVIDIA status
            return jsonify({
                'available': False,
                'gpu_count': 0,
                'driver_version': None,
                'timestamp': time.time()
            })

        @self.app.route('/api/files')
        def get_files():
            # Placeholder for file listing
            return jsonify({
                'files': [],
                'directories': [],
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/status')
        def autogen_status():
            # Placeholder for AutoGen status
            return jsonify({
                'running': False,
                'agents': [],
                'workflows': [],
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/start', methods=['POST'])
        def autogen_start():
            # Placeholder for AutoGen start
            log_info("mobile_web_interface", "AutoGen start requested")
            return jsonify({
                'action': 'start',
                'status': 'initiated',
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/stop', methods=['POST'])
        def autogen_stop():
            # Placeholder for AutoGen stop
            log_info("mobile_web_interface", "AutoGen stop requested")
            return jsonify({
                'action': 'stop',
                'status': 'completed',
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/create-agent', methods=['POST'])
        def autogen_create_agent():
            # Placeholder for agent creation
            log_info("mobile_web_interface", "AutoGen create agent requested")
            return jsonify({
                'action': 'create_agent',
                'status': 'completed',
                'agent_id': None,
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/create-workflow', methods=['POST'])
        def autogen_create_workflow():
            # Placeholder for workflow creation
            log_info("mobile_web_interface", "AutoGen create workflow requested")
            return jsonify({
                'action': 'create_workflow',
                'status': 'completed',
                'workflow_id': None,
                'timestamp': time.time()
            })

        @self.app.route('/api/autogen/command', methods=['POST'])
        def autogen_command():
            # Placeholder for AutoGen command
            log_info("mobile_web_interface", "AutoGen command requested")
            return jsonify({
                'action': 'command',
                'status': 'completed',
                'result': None,
                'timestamp': time.time()
            })

        @self.app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response

    def _get_html_template(self) -> str:
        """Get the HTML template for the web interface"""
        return r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRON - Pokedex AI Interface</title>
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon.png">
    <link rel="icon" type="image/x-icon" href="assets/favicon.ico">
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Press+Start+2P&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <elevenlabs-convai agent-id="agent_01jzwkf7dkfdvt5810x1vgrcjs"></elevenlabs-convai>

    <!-- ElevenLabs Widget Text Display Overlay -->
    <div id="elevenlabs-text-overlay" class="elevenlabs-text-overlay hidden">
        <div class="elevenlabs-text-container">
            <div class="text-header">
                <span class="text-title">🎤 ElevenLabs AI Assistant</span>
                <button class="close-overlay-btn" id="close-elevenlabs-overlay">✕</button>
            </div>
            <div class="text-content">
                <div class="conversation-display" id="elevenlabs-conversation">
                    <div class="conversation-message system-msg">
                        <span class="msg-label">🤖 AI:</span>
                        <span class="msg-content">Ready to chat! Ask me anything.</span>
                    </div>
                </div>
            </div>
            <div class="text-controls">
                <button class="control-btn" id="clear-elevenlabs-text">🗑️ Clear</button>
                <button class="control-btn" id="toggle-elevenlabs-widget">🎤 Toggle Widget</button>
            </div>
        </div>
    </div>

    <div id="app">
        <div id="start-screen" class="start-screen">
            <button id="start-button" class="start-button">START</button>
        </div>
        <!-- Main Pokedex Interface -->
        <div id="main-interface" class="main-interface hidden">
            <div class="pokedex-container">

                <!-- Main Pokédex Body -->
                <div class="pokedex-body pokedex-red" id="pokedex-body">

                    <!-- Top Section - Control Panel -->
                    <div class="pokedex-top">
                        <!-- Status LEDs -->
                        <div class="led-cluster">
                            <div class="led-main led-light large led-red" id="main-led">
                                <div class="led-glow"></div>
                            </div>
                            <div class="led-small-group">
                                <div class="led-light small led-yellow" id="led-1"></div>
                                <div class="led-light small led-green" id="led-2"></div>
                                <div class="led-light small led-blue" id="led-3"></div>
                            </div>
                        </div>

                        <!-- Navigation Panel -->
                        <div class="navigation-panel">
                            <div class="nav-header">
                                <h1 class="pokedex-title">ULTRON AI SYSTEM</h1>
                                <div class="current-section">
                                    <span class="section-indicator" id="current-section-indicator">
                                        🖥️ CONSOLE
                                    </span>
                                </div>
                            </div>

                            <div class="nav-buttons-grid">
                                <button class="nav-button active" data-section="console">
                                    <span class="nav-icon">🖥️</span>
                                    <span class="nav-label">CONSOLE</span>
                                </button>
                                <button class="nav-button" data-section="system">
                                    <span class="nav-icon">⚙️</span>
                                    <span class="nav-label">SYSTEM</span>
                                </button>
                                <button class="nav-button" data-section="vision">
                                    <span class="nav-icon">👁️</span>
                                    <span class="nav-label">VISION</span>
                                </button>
                                <button class="nav-button" data-section="tasks">
                                    <span class="nav-icon">📋</span>
                                    <span class="nav-label">TASKS</span>
                                </button>
                                <button class="nav-button" data-section="files">
                                    <span class="nav-icon">📁</span>
                                    <span class="nav-label">FILES</span>
                                </button>
                                <button class="nav-button" data-section="settings">
                                    <span class="nav-icon">🔧</span>
                                    <span class="nav-label">CONFIG</span>
                                </button>
                                <button class="nav-button" data-section="profile">
                                    <span class="nav-icon">👤</span>
                                    <span class="nav-label">PROFILE</span>
                                </button>
                                <button class="nav-button" data-section="autogen">
                                    <span class="nav-icon">🤖</span>
                                    <span class="nav-label">AUTOGEN</span>
                                </button>
                                <button class="nav-button" data-section="assistant" onclick="window.open('http://localhost:5173', '_blank')">
                                    <span class="nav-icon">🤖</span>
                                    <span class="nav-label">AI CHAT</span>
                                </button>
                                <button class="nav-button" data-section="llm-chat">
                                    <span class="nav-icon">💬</span>
                                    <span class="nav-label">LLM CHAT</span>
                                </button>
                                <button class="nav-button" data-section="tools">
                                    <span class="nav-icon">🔧</span>
                                    <span class="nav-label">TOOLS</span>
                                </button>
                                <button class="nav-button" data-section="stable-diffusion">
                                    <span class="nav-icon">🎨</span>
                                    <span class="nav-label">AI ART</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Main Screen -->
                    <div class="pokedex-screen">
                        <div class="screen-border">
                            <div class="screen-content">
                                <div class="scan-lines"></div>

                                <!-- Console Section -->
                                <div id="console-section" class="section-content active">
                                    <div class="section-title">ULTRON CONSOLE</div>
                                    <div class="console-output" id="console-output">
                                        <div class="message system-message">
                                            <span class="timestamp">[00:00:00]</span>
                                            <span class="message-content">🔴 ULTRON AI System Ready</span>
                                        </div>
                                    </div>
                                    <div class="console-input-container">
                                        <span class="console-prompt">ULTRON> </span>
                                        <input type="text" id="console-input" class="console-input" placeholder="Enter command..." autocomplete="off">
                                    </div>
                                </div>

                                <!-- System Section -->
                                <div id="system-section" class="section-content">
                                    <div class="section-title">SYSTEM STATUS</div>
                                    <div class="system-grid">
                                        <div class="system-card">
                                            <div class="card-title">CPU</div>
                                            <div class="card-value" id="cpu-usage">0%</div>
                                            <div class="card-bar">
                                                <div class="bar-fill" id="cpu-bar"></div>
                                            </div>
                                        </div>
                                        <div class="system-card">
                                            <div class="card-title">MEMORY</div>
                                            <div class="card-value" id="memory-usage">0%</div>
                                            <div class="card-bar">
                                                <div class="bar-fill" id="memory-bar"></div>
                                            </div>
                                        </div>
                                        <div class="system-card">
                                            <div class="card-title">DISK</div>
                                            <div class="card-value" id="disk-usage">0%</div>
                                            <div class="card-bar">
                                                <div class="bar-fill" id="disk-bar"></div>
                                            </div>
                                        </div>
                                        <div class="system-card">
                                            <div class="card-title">NETWORK</div>
                                            <div class="card-value connection-status" id="network-status">CONNECTED</div>
                                        </div>
                                    </div>
                                    <div class="process-list" id="process-list">
                                        <div class="list-title">RUNNING PROCESSES</div>
                                        <div class="process-content">Loading processes...</div>
                                    </div>
                                </div>

                                <!-- Vision Section -->
                                <div id="vision-section" class="section-content">
                                    <div class="section-title">VISION SYSTEM</div>
                                    <div class="vision-controls">
                                        <button class="vision-btn" id="capture-btn">📷 CAPTURE</button>
                                        <button class="vision-btn" id="analyze-btn">🔍 ANALYZE</button>
                                    </div>
                                    <div class="vision-display" id="vision-display">
                                        <div class="vision-placeholder">
                                            Ready for screen capture and analysis
                                        </div>
                                        <!-- Screenshot Display -->
                                        <div class="screenshot-container" id="screenshot-container" style="display: none;">
                                            <div class="screenshot-header">
                                                <h4>📸 Latest Screenshot</h4>
                                                <span class="screenshot-timestamp" id="screenshot-timestamp"></span>
                                            </div>
                                            <div class="screenshot-image">
                                                <img id="screenshot-image" alt="Screenshot" style="max-width: 100%; border-radius: 8px; border: 2px solid #333;">
                                            </div>
                                        </div>
                                        <!-- Analysis Results -->
                                        <div class="analysis-container" id="analysis-container" style="display: none;">
                                            <div class="analysis-header">
                                                <h4>🔍 Analysis Report</h4>
                                            </div>
                                            <div class="analysis-tabs">
                                                <button class="analysis-tab active" data-tab="ocr">OCR Text</button>
                                                <button class="analysis-tab" data-tab="ai">AI Analysis</button>
                                            </div>
                                            <div class="analysis-content">
                                                <div class="analysis-panel active" id="ocr-panel">
                                                    <div class="ocr-text" id="ocr-text">No OCR text available</div>
                                                </div>
                                                <div class="analysis-panel" id="ai-panel">
                                                    <div class="ai-analysis" id="ai-analysis">No AI analysis available</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Tasks Section -->
                                <div id="tasks-section" class="section-content">
                                    <div class="section-title">TASK MANAGER</div>
                                    <div class="task-list" id="task-list">
                                        <div class="task-placeholder">No active tasks</div>
                                    </div>
                                </div>

                                <!-- Files Section -->
                                <div id="files-section" class="section-content">
                                    <div class="section-title">FILE SYSTEM</div>
                                    <div class="file-browser" id="file-browser">
                                        <div class="file-path" id="file-path">D:\ULTRON\</div>
                                        <div class="file-list" id="file-list">
                                            <div class="file-placeholder">Loading files...</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Settings Section -->
                                <div id="settings-section" class="section-content">
                                    <div class="section-title">CONFIGURATION</div>
                                    <div class="settings-grid">
                                        <div class="setting-group">
                                            <label>Theme</label>
                                            <select id="theme-select" title="Select theme color for the Pokedex interface">
                                                <option value="red">Red Pokedex</option>
                                                <option value="blue">Blue Pokedex</option>
                                            </select>
                                        </div>
                                        <div class="setting-group">
                                            <label>Voice</label>
                                            <button id="voice-toggle" class="setting-btn">🎤 Enable</button>
                                        </div>
                                        <div class="setting-group">
                                            <label>Sound</label>
                                            <button id="sound-toggle" class="setting-btn">🔊 On</button>
                                        </div>
                                        <div class="setting-group">
                                            <label>API Key</label>
                                            <input type="password" id="api-key-input" placeholder="Enter OpenAI API key">
                                        </div>
                                    </div>
                                </div>

                                <!-- Profile Section -->
                                <div id="profile-section" class="section-content">
                                    <div class="section-title">USER PROFILE</div>
                                    <div class="profile-content">
                                        <div class="profile-header">
                                            <div class="profile-avatar">
                                                <div class="avatar-placeholder">👤</div>
                                            </div>
                                            <div class="profile-info">
                                                <h2 class="profile-name">ULTRON Agent</h2>
                                                <p class="profile-email">ultron.agent@example.com</p>
                                                <p class="profile-status">Status: <span class="status-online">Online</span></p>
                                            </div>
                                        </div>

                                        <div class="profile-details">
                                            <div class="detail-card">
                                                <h3>Account Information</h3>
                                                <div class="detail-item">
                                                    <span class="detail-label">Member Since:</span>
                                                    <span class="detail-value">2025</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="detail-label">Last Login:</span>
                                                    <span class="detail-value">Today</span>
                                                </div>
                                            </div>

                                            <div class="detail-card">
                                                <h3>Preferences</h3>
                                                <div class="detail-item">
                                                    <span class="detail-label">Theme:</span>
                                                    <span class="detail-value">Red Pokedex</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="detail-label">Voice:</span>
                                                    <span class="detail-value">Enabled</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="detail-label">Sound:</span>
                                                    <span class="detail-value">On</span>
                                                </div>
                                            </div>

                                            <div class="detail-card">
                                                <h3>System Stats</h3>
                                                <div class="detail-item">
                                                    <span class="detail-label">Tasks Completed:</span>
                                                    <span class="detail-value">127</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="detail-label">Files Processed:</span>
                                                    <span class="detail-value">42</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="detail-label">Analysis Runs:</span>
                                                    <span class="detail-value">89</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="profile-actions">
                                            <button class="profile-btn" id="edit-profile-btn">Edit Profile</button>
                                            <button class="profile-btn" id="export-data-btn">Export Data</button>
                                            <button class="profile-btn danger" id="reset-system-btn">Reset System</button>
                                        </div>
                                    </div>
                                </div>

                                <!-- AutoGen Studio Section -->
                                <div id="autogen-section" class="section-content">
                                    <div class="section-title">AUTOGEN STUDIO</div>
                                    <div class="autogen-content">
                                        <div class="autogen-status">
                                            <div class="status-card">
                                                <h3>AutoGen Studio Status</h3>
                                                <div class="autogen-metrics" id="autogen-metrics">
                                                    <div class="metric">
                                                        <span class="metric-label">Status:</span>
                                                        <span class="metric-value" id="autogen-status">Checking...</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Port:</span>
                                                        <span class="metric-value" id="autogen-port">8081</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Active Sessions:</span>
                                                        <span class="metric-value" id="autogen-sessions">0</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="status-card">
                                                <h3>Available Agents</h3>
                                                <div class="agent-list" id="agent-list">
                                                    <div class="agent-item">Loading agents...</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="autogen-controls">
                                            <div class="control-group">
                                                <button class="autogen-btn primary" id="start-autogen-btn">
                                                    <span class="btn-icon">🚀</span>
                                                    Start AutoGen Studio
                                                </button>
                                                <button class="autogen-btn" id="stop-autogen-btn">
                                                    <span class="btn-icon">⏹️</span>
                                                    Stop AutoGen Studio
                                                </button>
                                                <button class="autogen-btn" id="refresh-autogen-btn">
                                                    <span class="btn-icon">🔄</span>
                                                    Refresh Status
                                                </button>
                                            </div>
                                            <div class="control-group">
                                                <button class="autogen-btn secondary" id="open-autogen-btn">
                                                    <span class="btn-icon">🌐</span>
                                                    Open AutoGen Studio
                                                </button>
                                                <button class="autogen-btn secondary" id="create-agent-btn">
                                                    <span class="btn-icon">➕</span>
                                                    Create Agent
                                                </button>
                                                <button class="autogen-btn secondary" id="create-workflow-btn">
                                                    <span class="btn-icon">⚡</span>
                                                    Create Workflow
                                                </button>
                                            </div>
                                        </div>
                                        <div class="autogen-commands">
                                            <div class="command-section">
                                                <h4>Quick Commands</h4>
                                                <div class="command-grid">
                                                    <button class="command-btn" data-command="autogen status">
                                                        <span>📊</span> Status
                                                    </button>
                                                    <button class="command-btn" data-command="autogen list agents">
                                                        <span>🤖</span> List Agents
                                                    </button>
                                                    <button class="command-btn" data-command="autogen list workflows">
                                                        <span>⚡</span> List Workflows
                                                    </button>
                                                    <button class="command-btn" data-command="autogen create session">
                                                        <span>🎯</span> New Session
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="autogen-output" id="autogen-output">
                                            <div class="output-header">AutoGen Studio Output</div>
                                            <div class="output-content">
                                                <div class="output-message system-message">
                                                    <span class="timestamp">[00:00:00]</span>
                                                    <span class="message-content">AutoGen Studio integration ready</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Dashboard Section -->
                                <div id="dashboard-section" class="section-content">
                                    <div class="section-title">SYSTEM DASHBOARD</div>
                                    <div class="dashboard-content">
                                        <div class="dashboard-grid">
                                            <div class="dashboard-card">
                                                <h3>System Overview</h3>
                                                <div class="dashboard-metrics">
                                                    <div class="metric">
                                                        <span class="metric-label">Status:</span>
                                                        <span class="metric-value" id="overall-status">Loading...</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Agent:</span>
                                                        <span class="metric-value" id="agent-status">Loading...</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Uptime:</span>
                                                        <span class="metric-value" id="system-uptime">00:00:00</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="dashboard-card">
                                                <h3>Quick Actions</h3>
                                                <div class="dashboard-actions">
                                                    <button class="action-btn" onclick="ultronInterface.loadSystemInfo()">Refresh Status</button>
                                                    <button class="action-btn" onclick="ultronInterface.loadNvidiaStatus()">Check NVIDIA</button>
                                                    <button class="action-btn" onclick="ultronInterface.switchSection('system')">View Details</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- LLM Chat Section -->
                                <div id="llm-chat-section" class="section-content">
                                    <div class="section-title">LLM CHAT INTERFACE</div>
                                    <div class="llm-chat-content">
                                        <div class="llm-chat-header">
                                            <div class="model-status">
                                                <span class="model-label">Active Model:</span>
                                                <span class="model-name" id="active-model">Loading...</span>
                                                <span class="model-status-indicator" id="model-status">🔄</span>
                                            </div>
                                            <div class="chat-controls">
                                                <button class="chat-btn" id="clear-chat-btn">🗑️ Clear</button>
                                                <button class="chat-btn" id="export-chat-btn">📤 Export</button>
                                                <button class="chat-btn" id="switch-model-btn">🔄 Switch Model</button>
                                                <button class="chat-btn" id="test-tts-btn">🔊 Test TTS</button>
                                                <button class="chat-btn" id="show-elevenlabs-btn">💬 ElevenLabs Text</button>
                                                <button class="chat-btn" id="manual-tts-test-btn" onclick="if(window.ultronInterface){window.ultronInterface.testTTS();}else{alert('Interface not loaded');}">🎯 Manual TTS Test</button>
                                            </div>
                                        </div>
                                        <div class="chat-messages" id="chat-messages">
                                            <div class="chat-message system-message">
                                                <div class="message-avatar">🤖</div>
                                                <div class="message-content">
                                                    <div class="message-header">ULTRON AI</div>
                                                    <div class="message-text">Hello! I'm ready to help. What would you like to discuss?</div>
                                                    <div class="message-time">Now</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="chat-input-container">
                                            <div class="chat-input-wrapper">
                                                <textarea id="chat-input" class="chat-input" placeholder="Type your message here..." rows="2"></textarea>
                                                <div class="chat-input-actions">
                                                    <button class="send-btn" id="send-chat-btn">📤 Send</button>
                                                    <button class="voice-btn" id="voice-chat-btn">🎤 Voice</button>
                                                </div>
                                            </div>
                                            <div class="chat-quick-actions">
                                                <button class="quick-action-btn" data-prompt="Explain this code">💻 Explain Code</button>
                                                <button class="quick-action-btn" data-prompt="Debug this issue">🐛 Debug Issue</button>
                                                <button class="quick-action-btn" data-prompt="Optimize this">⚡ Optimize</button>
                                                <button class="quick-action-btn" data-prompt="Generate documentation">📚 Document</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Tools Integration Section -->
                                <div id="tools-section" class="section-content">
                                    <div class="section-title">TOOL INTEGRATION</div>
                                    <div class="tools-content">
                                        <div class="tools-header">
                                            <div class="tools-stats">
                                                <div class="stat-card">
                                                    <span class="stat-label">Total Tools:</span>
                                                    <span class="stat-value" id="total-tools">0</span>
                                                </div>
                                                <div class="stat-card">
                                                    <span class="stat-label">Active Tools:</span>
                                                    <span class="stat-value" id="active-tools">0</span>
                                                </div>
                                                <div class="stat-card">
                                                    <span class="stat-label">Tool Usage:</span>
                                                    <span class="stat-value" id="tool-usage">0</span>
                                                </div>
                                            </div>
                                            <div class="tools-controls">
                                                <button class="tool-btn" id="refresh-tools-btn">🔄 Refresh</button>
                                                <button class="tool-btn" id="reload-tools-btn">⚡ Reload All</button>
                                                <button class="tool-btn" id="test-tools-btn">🧪 Test Tools</button>
                                            </div>
                                        </div>
                                        <div class="tools-grid" id="tools-grid">
                                            <div class="tool-placeholder">
                                                <div class="loading-spinner"></div>
                                                <p>Loading available tools...</p>
                                            </div>
                                        </div>
                                        <div class="tool-details" id="tool-details">
                                            <div class="tool-info-placeholder">
                                                Select a tool to view details
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Stable Diffusion Section -->
                                <div id="stable-diffusion-section" class="section-content">
                                    <div class="section-title">AI IMAGE GENERATION</div>
                                    <div class="stable-diffusion-content">
                                        <div class="sd-controls">
                                            <div class="sd-input-group">
                                                <label for="sd-prompt">Prompt:</label>
                                                <textarea id="sd-prompt" class="sd-textarea" placeholder="Describe the image you want to generate..." rows="3"></textarea>
                                            </div>
                                            <div class="sd-input-group">
                                                <label for="sd-negative-prompt">Negative Prompt (optional):</label>
                                                <textarea id="sd-negative-prompt" class="sd-textarea" placeholder="What to avoid in the image..." rows="2"></textarea>
                                            </div>
                                            <div class="sd-parameters">
                                                <div class="param-row">
                                                    <div class="param-group">
                                                        <label for="sd-width">Width:</label>
                                                        <input type="number" id="sd-width" class="sd-input" value="512" min="256" max="1024" step="64">
                                                    </div>
                                                    <div class="param-group">
                                                        <label for="sd-height">Height:</label>
                                                        <input type="number" id="sd-height" class="sd-input" value="512" min="256" max="1024" step="64">
                                                    </div>
                                                </div>
                                                <div class="param-row">
                                                    <div class="param-group">
                                                        <label for="sd-steps">Steps:</label>
                                                        <input type="number" id="sd-steps" class="sd-input" value="20" min="10" max="50" step="5">
                                                    </div>
                                                    <div class="param-group">
                                                        <label for="sd-cfg-scale">CFG Scale:</label>
                                                        <input type="number" id="sd-cfg-scale" class="sd-input" value="7.0" min="1.0" max="15.0" step="0.5">
                                                    </div>
                                                </div>
                                                <div class="param-row">
                                                    <div class="param-group full-width">
                                                        <label for="sd-sampler">Sampler:</label>
                                                        <select id="sd-sampler" class="sd-select">
                                                            <option value="Euler a">Euler a</option>
                                                            <option value="Euler">Euler</option>
                                                            <option value="LMS">LMS</option>
                                                            <option value="Heun">Heun</option>
                                                            <option value="DPM2">DPM2</option>
                                                            <option value="DPM2 a">DPM2 a</option>
                                                            <option value="DPM++ 2S a">DPM++ 2S a</option>
                                                            <option value="DPM++ 2M">DPM++ 2M</option>
                                                            <option value="DPM++ SDE">DPM++ SDE</option>
                                                            <option value="DPM fast">DPM fast</option>
                                                            <option value="DPM adaptive">DPM adaptive</option>
                                                            <option value="LMS Karras">LMS Karras</option>
                                                            <option value="DPM2 Karras">DPM2 Karras</option>
                                                            <option value="DPM2 a Karras">DPM2 a Karras</option>
                                                            <option value="DPM++ 2S a Karras">DPM++ 2S a Karras</option>
                                                            <option value="DPM++ 2M Karras">DPM++ 2M Karras</option>
                                                            <option value="DPM++ SDE Karras">DPM++ SDE Karras</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="sd-actions">
                                                <button class="sd-btn primary" id="generate-btn">🎨 Generate Image</button>
                                                <button class="sd-btn secondary" id="clear-sd-btn">🗑️ Clear</button>
                                            </div>
                                        </div>
                                        <div class="sd-display" id="sd-display">
                                            <div class="sd-placeholder">
                                                Generated images will appear here
                                            </div>
                                            <!-- Generated Image Display -->
                                            <div class="sd-image-container" id="sd-image-container" style="display: none;">
                                                <div class="sd-image-header">
                                                    <h4>🎨 Generated Image</h4>
                                                    <span class="sd-image-timestamp" id="sd-image-timestamp"></span>
                                                </div>
                                                <div class="sd-image-content">
                                                    <img id="sd-generated-image" alt="Generated Image" style="max-width: 100%; border-radius: 8px; border: 2px solid #333;">
                                                </div>
                                                <div class="sd-image-info">
                                                    <div class="sd-prompt-display">
                                                        <strong>Prompt:</strong> <span id="sd-display-prompt"></span>
                                                    </div>
                                                    <div class="sd-params-display">
                                                        <strong>Parameters:</strong> <span id="sd-display-params"></span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- NVIDIA Section -->
                                <div id="nvidia-section" class="section-content">
                                    <div class="section-title">NVIDIA AI INTERFACE</div>
                                    <div class="nvidia-content">
                                        <div class="nvidia-status">
                                            <div class="status-card">
                                                <h3>GPU Status</h3>
                                                <div class="nvidia-metrics" id="nvidia-metrics">
                                                    <div class="metric">Loading NVIDIA information...</div>
                                                </div>
                                            </div>
                                            <div class="status-card">
                                                <h3>Available Models</h3>
                                                <div class="model-list" id="model-list">
                                                    <div class="model-item">Loading models...</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="nvidia-actions">
                                            <button class="action-btn primary" onclick="ultronInterface.loadNvidiaStatus()">Refresh Status</button>
                                            <button class="action-btn" onclick="window.open('http://localhost:5173', '_blank')">Open NVIDIA Chat</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Bottom Control Panel -->
                    <div class="pokedex-controls">
                        <!-- D-Pad Style Navigation -->
                        <div class="control-section">
                            <div class="d-pad" id="d-pad">
                                <div class="d-pad-center"></div>
                                <div class="d-pad-up" data-direction="up">▲</div>
                                <div class="d-pad-down" data-direction="down">▼</div>
                                <div class="d-pad-left" data-direction="left">◀</div>
                                <div class="d-pad-right" data-direction="right">▶</div>
                            </div>
                            <div class="control-labels">
                                <span>NAVIGATE</span>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="control-section">
                            <div class="action-buttons">
                                <button class="action-btn btn-a" id="btn-a">
                                    <span>A</span>
                                </button>
                                <button class="action-btn btn-b" id="btn-b">
                                    <span>B</span>
                                </button>
                            </div>
                            <div class="control-labels">
                                <span>A: SELECT</span>
                                <span>B: BACK</span>
                            </div>
                        </div>

                        <!-- System Controls -->
                        <div class="control-section">
                            <div class="system-controls">
                                <button class="system-btn" id="btn-power" title="Power Menu">
                                    ⚡
                                </button>
                                <button class="system-btn" id="btn-volume" title="Volume">
                                    🔊
                                </button>
                                <button class="system-btn" id="btn-settings" title="Settings">
                                    ⚙️
                                </button>
                            </div>
                            <div class="control-labels">
                                <span>SYSTEM</span>
                            </div>
                        </div>
                    </div>

                    <!-- Speaker Grille -->
                    <div class="speaker-grille">
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                        <div class="speaker-hole"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Power Menu Modal -->
        <div id="power-menu" class="modal hidden">
            <div class="modal-content">
                <div class="modal-title">POWER MANAGEMENT</div>
                <div class="power-options">
                    <button class="power-btn" data-action="shutdown">🔴 SHUTDOWN SYSTEM</button>
                    <button class="power-btn" data-action="restart">🔄 RESTART SYSTEM</button>
                    <button class="power-btn" data-action="sleep">💤 SLEEP MODE</button>
                    <button class="power-btn" data-action="cancel">❌ CANCEL</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Audio Elements -->
    <audio id="startup-sound" preload="auto"></audio>
    <audio id="audio-wake" preload="auto">
        <source src="assets/wake.wav" type="audio/wav">
    </audio>
    <audio id="audio-button" preload="auto">
        <source src="assets/button_press.wav" type="audio/wav">
    </audio>
    <audio id="audio-confirm" preload="auto">
        <source src="assets/confirm.wav" type="audio/wav">
    </audio>

    <script src="assets/sounds.js"></script>
    <script src="app.js"></script>
    <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>

<style>
.start-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #000;
}

.start-button {
    font-family: 'Press Start 2P', cursive;
    font-size: 2rem;
    color: #fff;
    background-color: #f00;
    border: 2px solid #fff;
    padding: 1rem 2rem;
    cursor: pointer;
    box-shadow: 0 0 10px #f00;
}
.hidden {
    display: none;
}

/* Vision Interface Styles */
.vision-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    justify-content: center;
}

.vision-btn {
    background: #333;
    color: #fff;
    border: 2px solid #666;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;
}

.vision-btn:hover:not(:disabled) {
    background: #555;
    border-color: #888;
}

.vision-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.screenshot-container {
    margin-bottom: 20px;
    padding: 15px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    border: 1px solid #444;
}

.screenshot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.screenshot-header h4 {
    margin: 0;
    color: #fff;
    font-size: 16px;
}

.screenshot-timestamp {
    color: #ccc;
    font-size: 12px;
}

.analysis-container {
    padding: 15px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    border: 1px solid #444;
}

.analysis-header h4 {
    margin: 0 0 15px 0;
    color: #fff;
    font-size: 16px;
}

.analysis-tabs {
    display: flex;
    gap: 5px;
    margin-bottom: 15px;
}

.analysis-tab {
    background: #333;
    color: #ccc;
    border: 1px solid #555;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}

.analysis-tab.active {
    background: #555;
    color: #fff;
    border-color: #777;
}

.analysis-content {
    min-height: 150px;
}

.analysis-panel {
    display: none;
}

.analysis-panel.active {
    display: block;
}

.ocr-text, .ai-analysis {
    color: #eee;
    font-family: monospace;
    font-size: 12px;
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 300px;
    overflow-y: auto;
    padding: 10px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 4px;
    border: 1px solid #333;
}
</style>

<!-- Stable Diffusion Styles -->
<style>
.stable-diffusion-content {
    padding: 15px;
}

.sd-controls {
    margin-bottom: 20px;
    padding: 15px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    border: 1px solid #444;
}

.sd-input-group {
    margin-bottom: 15px;
}

.sd-input-group label {
    display: block;
    color: #fff;
    font-size: 12px;
    margin-bottom: 5px;
    font-weight: bold;
}

.sd-textarea {
    width: 100%;
    padding: 8px;
    background: #333;
    border: 1px solid #555;
    border-radius: 4px;
    color: #fff;
    font-family: monospace;
    font-size: 12px;
    resize: vertical;
}

.sd-textarea::placeholder {
    color: #ccc;
}

.sd-parameters {
    margin: 15px 0;
}

.param-row {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.param-group {
    flex: 1;
}

.param-group.full-width {
    flex: 1 1 100%;
}

.sd-input {
    width: 100%;
    padding: 6px;
    background: #333;
    border: 1px solid #555;
    border-radius: 4px;
    color: #fff;
    font-size: 12px;
}

.sd-select {
    width: 100%;
    padding: 6px;
    background: #333;
    border: 1px solid #555;
    border-radius: 4px;
    color: #fff;
    font-size: 12px;
}

.sd-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 15px;
}

.sd-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.sd-btn.primary {
    background: #007bff;
    color: white;
}

.sd-btn.primary:hover:not(:disabled) {
    background: #0056b3;
}

.sd-btn.secondary {
    background: #6c757d;
    color: white;
}

.sd-btn.secondary:hover {
    background: #545b62;
}

.sd-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.sd-display {
    padding: 15px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    border: 1px solid #444;
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.sd-placeholder {
    color: #ccc;
    font-style: italic;
    text-align: center;
}

.sd-image-container {
    width: 100%;
}

.sd-image-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.sd-image-header h4 {
    margin: 0;
    color: #fff;
    font-size: 16px;
}

.sd-image-timestamp {
    color: #ccc;
    font-size: 12px;
}

.sd-image-content {
    text-align: center;
    margin-bottom: 15px;
}

.sd-image-info {
    background: rgba(0, 0, 0, 0.5);
    padding: 10px;
    border-radius: 4px;
    font-size: 12px;
    color: #eee;
}

.sd-prompt-display,
.sd-params-display {
    margin-bottom: 5px;
    line-height: 1.4;
}

.sd-prompt-display strong,
.sd-params-display strong {
    color: #fff;
}
</style>

<!-- Emergency initialization script -->
<script>
    // Vision functionality
    class VisionInterface {
        constructor() {
            this.init();
        }

        init() {
            this.setupVisionEventListeners();
            this.setupAnalysisTabs();
        }

        setupVisionEventListeners() {
            const captureBtn = document.getElementById('capture-btn');
            const analyzeBtn = document.getElementById('analyze-btn');

            if (captureBtn) {
                captureBtn.addEventListener('click', () => this.captureScreen());
            }

            if (analyzeBtn) {
                analyzeBtn.addEventListener('click', () => this.analyzeScreen());
            }
        }

        setupAnalysisTabs() {
            const tabs = document.querySelectorAll('.analysis-tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    const tabName = e.target.dataset.tab;
                    this.switchAnalysisTab(tabName);
                });
            });
        }

        async captureScreen() {
            try {
                captureBtn.disabled = true;
                captureBtn.textContent = '📷 CAPTURING...';

                const response = await fetch('/api/vision/capture', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (data.status === 'completed') {
                    this.displayScreenshot(data);
                    this.addMessage('✅ Screen captured successfully');
                } else {
                    this.addMessage('❌ Screen capture failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Capture error:', error);
                this.addMessage('❌ Screen capture error: ' + error.message);
            } finally {
                captureBtn.disabled = false;
                captureBtn.textContent = '📷 CAPTURE';
            }
        }

        async analyzeScreen() {
            try {
                analyzeBtn.disabled = true;
                analyzeBtn.textContent = '🔍 ANALYZING...';

                const response = await fetch('/api/vision/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (data.status === 'completed') {
                    this.displayAnalysis(data);
                    this.addMessage('✅ Analysis completed successfully');
                } else {
                    this.addMessage('❌ Analysis failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Analysis error:', error);
                this.addMessage('❌ Analysis error: ' + error.message);
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🔍 ANALYZE';
            }
        }

        displayScreenshot(data) {
            const container = document.getElementById('screenshot-container');
            const image = document.getElementById('screenshot-image');
            const timestamp = document.getElementById('screenshot-timestamp');

            if (container && image && data.image_url) {
                image.src = data.image_url;
                timestamp.textContent = new Date(data.timestamp * 1000).toLocaleString();
                container.style.display = 'block';
            }
        }

        displayAnalysis(data) {
            const container = document.getElementById('analysis-container');
            const ocrText = document.getElementById('ocr-text');
            const aiAnalysis = document.getElementById('ai-analysis');

            if (container) {
                container.style.display = 'block';
            }

            if (ocrText && data.ocr_text) {
                ocrText.textContent = data.ocr_text;
            }

            if (aiAnalysis && data.ai_analysis) {
                aiAnalysis.textContent = data.ai_analysis;
            }
        }

        switchAnalysisTab(tabName) {
            // Update tab buttons
            const tabs = document.querySelectorAll('.analysis-tab');
            const panels = document.querySelectorAll('.analysis-panel');

            tabs.forEach(tab => {
                if (tab.dataset.tab === tabName) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });

            // Update panels
            panels.forEach(panel => {
                if (panel.id === `${tabName}-panel`) {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });
        }

        addMessage(message) {
            const consoleOutput = document.getElementById('console-output');
            if (consoleOutput) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message system-message';
                messageDiv.innerHTML = `
                    <span class="timestamp">[${new Date().toLocaleTimeString()}]</span>
                    <span class="message-content">${message}</span>
                `;
                consoleOutput.appendChild(messageDiv);
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }
        }
    }

    // Initialize vision interface
    const visionInterface = new VisionInterface();

    // Stable Diffusion Interface
    class StableDiffusionInterface {
        constructor() {
            this.init();
        }

        init() {
            this.setupEventListeners();
        }

        setupEventListeners() {
            const generateBtn = document.getElementById('generate-btn');
            const clearBtn = document.getElementById('clear-sd-btn');

            if (generateBtn) {
                generateBtn.addEventListener('click', () => this.generateImage());
            }

            if (clearBtn) {
                clearBtn.addEventListener('click', () => this.clearInterface());
            }
        }

        async generateImage() {
            try {
                const generateBtn = document.getElementById('generate-btn');
                const prompt = document.getElementById('sd-prompt').value.trim();
                const negativePrompt = document.getElementById('sd-negative-prompt').value.trim();
                const width = parseInt(document.getElementById('sd-width').value);
                const height = parseInt(document.getElementById('sd-height').value);
                const steps = parseInt(document.getElementById('sd-steps').value);
                const cfgScale = parseFloat(document.getElementById('sd-cfg-scale').value);
                const samplerName = document.getElementById('sd-sampler').value;

                if (!prompt) {
                    alert('Please enter a prompt for image generation');
                    return;
                }

                // Disable button and show loading
                generateBtn.disabled = true;
                generateBtn.textContent = '🎨 Generating...';

                // Prepare request data
                const requestData = {
                    prompt: prompt,
                    negative_prompt: negativePrompt,
                    width: width,
                    height: height,
                    steps: steps,
                    cfg_scale: cfgScale,
                    sampler_name: samplerName
                };

                const response = await fetch('/api/stable-diffusion/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });

                const data = await response.json();

                if (data.status === 'completed') {
                    this.displayGeneratedImage(data);
                    this.addMessage('✅ Image generated successfully');
                } else {
                    this.addMessage('❌ Image generation failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Generation error:', error);
                this.addMessage('❌ Image generation error: ' + error.message);
            } finally {
                const generateBtn = document.getElementById('generate-btn');
                generateBtn.disabled = false;
                generateBtn.textContent = '🎨 Generate Image';
            }
        }

        displayGeneratedImage(data) {
            const container = document.getElementById('sd-image-container');
            const image = document.getElementById('sd-generated-image');
            const timestamp = document.getElementById('sd-image-timestamp');
            const promptDisplay = document.getElementById('sd-display-prompt');
            const paramsDisplay = document.getElementById('sd-display-params');
            const placeholder = document.querySelector('.sd-placeholder');

            if (container && image && data.image_url) {
                // Hide placeholder
                if (placeholder) {
                    placeholder.style.display = 'none';
                }

                // Show container
                container.style.display = 'block';

                // Set image
                image.src = data.image_url;

                // Set timestamp
                timestamp.textContent = new Date(data.timestamp * 1000).toLocaleString();

                // Set prompt
                if (promptDisplay) {
                    promptDisplay.textContent = data.prompt;
                }

                // Set parameters
                if (paramsDisplay && data.parameters) {
                    const params = data.parameters;
                    const paramText = `${params.width}x${params.height}, ${params.steps} steps, CFG ${params.cfg_scale}, ${params.sampler_name}`;
                    paramsDisplay.textContent = paramText;
                }
            }
        }

        clearInterface() {
            // Clear inputs
            document.getElementById('sd-prompt').value = '';
            document.getElementById('sd-negative-prompt').value = '';

            // Reset parameters to defaults
            document.getElementById('sd-width').value = '512';
            document.getElementById('sd-height').value = '512';
            document.getElementById('sd-steps').value = '20';
            document.getElementById('sd-cfg-scale').value = '7.0';
            document.getElementById('sd-sampler').value = 'Euler a';

            // Hide generated image
            const container = document.getElementById('sd-image-container');
            const placeholder = document.querySelector('.sd-placeholder');

            if (container) {
                container.style.display = 'none';
            }

            if (placeholder) {
                placeholder.style.display = 'flex';
            }

            this.addMessage('🗑️ Interface cleared');
        }

        addMessage(message) {
            const consoleOutput = document.getElementById('console-output');
            if (consoleOutput) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message system-message';
                messageDiv.innerHTML = `
                    <span class="timestamp">[${new Date().toLocaleTimeString()}]</span>
                    <span class="message-content">${message}</span>
                `;
                consoleOutput.appendChild(messageDiv);
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }
        }
    }

    // Initialize stable diffusion interface
    const stableDiffusionInterface = new StableDiffusionInterface();

    // Force initialization after a delay if not already done
    setTimeout(() => {
        if (!window.ultronInterface) {
            console.log('🚨 Emergency initialization triggered - app.js:2387');
            try {
                window.ultronInterface = new UltronPokedexInterface();
                console.log('✅ Emergency initialization successful - app.js:2390');
            } catch (error) {
                console.error('❌ Emergency initialization failed: - app.js:2392', error);
            }
        }
    }, 2000);

    // Add global error handler
    window.addEventListener('error', (event) => {
        console.error('🚨 Global JavaScript error: - app.js:2399', event.error);
        console.error('Error message: - app.js:2400', event.message);
        console.error('Error file: - app.js:2401', event.filename);
        console.error('Error line: - app.js:2402', event.lineno);
    });
</script>

</body>
</html>
        """

    def match(self, command: str) -> bool:
        """Check if command matches interface operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "start web interface", "pokedex interface", "web gui", "launch interface",
            "open web app", "start pokedex app", "interface server", "pokedex gui"
        ])

    def execute(self, command: str, **kwargs) -> str:
        """Execute interface operations"""
        try:
            command_lower = command.lower()

            if "start" in command_lower or "launch" in command_lower:
                return self.start_interface()
            elif "stop" in command_lower:
                return self.stop_interface()
            elif "status" in command_lower:
                return self.get_status()
            else:
                return self.get_help()

        except Exception as e:
            log_error("mobile_web_interface", f"Interface operation failed: {e}")
            return f"Interface operation failed: {str(e)}"

    def start_interface(self) -> str:
        """Start the web interface"""
        if not self.app:
            return "Web interface not available. Please install Flask: pip install flask"

        if self.is_running:
            return f"Interface already running on http://localhost:{self.port}"

        try:
            def run_server():
                log_info("mobile_web_interface", f"Starting web interface on port {self.port}")
                self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True

            # Give server time to start
            time.sleep(2)

            # Try to open browser
            try:
                webbrowser.open(f"http://localhost:{self.port}")
            except:
                pass  # Browser open is optional

            return f"""
� **Pokédex Web Interface Started**

**Access URLs:**
• Local: http://localhost:{self.port}
• Network: http://0.0.0.0:{self.port}

**Features:**
• Authentic Pokédex retro gaming interface
• Real-time command execution via console
• System monitoring and status displays
• Voice integration with ElevenLabs
• Multiple sections: Console, System, Vision, Tasks, Files, Settings, Profile, AutoGen, LLM Chat, Tools, NVIDIA

**Usage:**
• Click "START" to begin
• Use D-pad controls or navigation buttons to switch sections
• Type commands in the console section
• Press Enter to execute commands
• Use A/B buttons for select/back actions

**Controls:**
• D-pad: Navigate interface sections
• A Button: Select/Execute
• B Button: Back/Cancel
• Power Button: System menu
• Volume/Settings: Audio and configuration
"""

        except Exception as e:
            log_error("mobile_web_interface", f"Failed to start interface: {e}")
            return f"Failed to start interface: {str(e)}"

    def stop_interface(self) -> str:
        """Stop the web interface"""
        if not self.is_running:
            return "Interface is not running"

        try:
            self.is_running = False
            # Note: Flask doesn't have a built-in way to stop the server gracefully
            # The daemon thread will stop when the main process exits
            log_info("mobile_web_interface", "Interface stop requested")
            return "Interface stop requested. Server will stop when application exits."
        except Exception as e:
            log_error("mobile_web_interface", f"Failed to stop interface: {e}")
            return f"Failed to stop interface: {str(e)}"

    def get_status(self) -> str:
        """Get interface status"""
        status = "Running" if self.is_running else "Stopped"
        port_info = f" on port {self.port}" if self.is_running else ""

        return f"""
🎮 **Pokédex Interface Status**

**Status:** {status}{port_info}
**Framework:** Flask with Pokédex GUI
**Theme:** Retro Gaming Interface
**Features:** Console commands, system monitoring, voice integration, multi-section navigation

**Access:** {"http://localhost:" + str(self.port) if self.is_running else "Not running"}
"""

    def get_help(self) -> str:
        """Get help information for the tool"""
        status = "✅ Available" if self.app else "❌ Not Available (install Flask)"

        return f"""
🎮 **Pokédex Web Interface Tool** ({status})

**Capabilities:**
• Retro gaming Pokédex-styled interface
• Real-time command execution via console
• System monitoring and status displays
• Voice integration with ElevenLabs
• Multiple interface sections (Console, System, Vision, Tasks, Files, etc.)

**Commands:**
• "start web interface" - Launch the Pokédex interface
• "start pokedex interface" - Launch the Pokédex interface
• "stop web interface" - Stop the interface server
• "interface status" - Check current status

**Requirements:**
• Flask: pip install flask
• Modern web browser with JavaScript enabled
• Network access for remote devices

**Features:**
• Authentic Pokédex retro gaming aesthetic
• Interactive navigation with D-pad controls
• ElevenLabs voice integration
• Real-time system monitoring
• Multiple specialized sections for different functions
• Responsive design for desktop and mobile
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Interface control command"
                    }
                },
                "required": ["command"]
            }
        }


# Main execution block for standalone server
if __name__ == "__main__":
    print("Starting ULTRON Pokédex Web Interface Server... - mobile_web_interface_tool.py:2766")
    print("Press Ctrl+C to stop the server - mobile_web_interface_tool.py:2767")

    # Create and start the interface
    interface = MobileWebInterfaceTool()

    # Start the Flask server directly (this will block)
    print(f"Starting Flask server on port {interface.port}... - mobile_web_interface_tool.py:2773")
    interface.app.run(host='0.0.0.0', port=interface.port, debug=False, use_reloader=False)
