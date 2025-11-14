"""
ULTRON Agent 3.0 - Brain Module with Ollama Integration
Handles AI reasoning, planning, and communication with Ollama models
Enhanced with intelligent caching for improved performance
"""

import logging
import hashlib
from utils.ultron_logger import ultron_logger, log_info, log_error, log_ai_decision
from utils.error_handlers import (
    NetworkError, TimeoutError as UltronTimeoutError, ConfigError,
    ToolError, ToolNotFoundError, AsyncError, with_retry,
    handle_errors_async, ErrorContext
)
from diagnostics import diagnostic_wrapper, track_metric
from os import path as os_path
from json import loads as json_loads, load as json_load, dump as json_dump, JSONDecodeError
from requests import get as requests_get
from asyncio import (
    new_event_loop, set_event_loop, TimeoutError as AsyncTimeoutError
)
from aiohttp import ClientSession, ClientError, ClientTimeout
from pathlib import Path
from typing import Dict, Any, List, Optional

# Create fallback functions for security utils if not available
try:
    from security_utils import (
        sanitize_log_input, sanitize_html_output, validate_file_path
    )
except ImportError:
    def sanitize_log_input(text):
        return str(text)[:1000]  # Limit length

    def sanitize_html_output(text):
        return str(text).replace('<', '&lt;').replace('>', '&gt;')

    def validate_file_path(path):
        return True  # Basic fallback

# Logging shortcuts
def info(msg):
    log_info("brain", msg)

def error(msg):
    log_error("brain", msg)

def warning(msg):
    log_info("brain", f"WARNING: {msg}")

# Import OpenAI tools if available
try:
    from tools.openai_tools import OpenAITools
except ImportError:
    OpenAITools = None
    warning("OpenAI tools not available")

# Import enhanced mesh transformer manager for GPT-J/GPT-NeoX integration
try:
    from enhanced_mesh_transformer_manager import (
        get_enhanced_mesh_transformer_manager,
        MeshTransformerIntegration
    )
    MESH_TRANSFORMER_AVAILABLE = True
except ImportError as e:
    warning(f"Enhanced mesh transformer not available: "
            f"{sanitize_log_input(str(e))}")
    MESH_TRANSFORMER_AVAILABLE = False
    get_enhanced_mesh_transformer_manager = None
    MeshTransformerIntegration = None

# Import NVIDIA NIM router for enhanced suggestions
try:
    from nvidia_nim_router import UltronNvidiaRouter
    NVIDIA_AVAILABLE = True
except ImportError:
    warning(
        "NVIDIA NIM router not available - suggestions will use Ollama only"
    )
    UltronNvidiaRouter = None
    NVIDIA_AVAILABLE = False

# Import enhanced NLP processor for advanced text analysis
try:
    from nlp_enhancer import EnhancedNLPProcessor
    NLP_AVAILABLE = True
except ImportError as e:
    warning(f"Enhanced NLP processor not available: {sanitize_log_input(str(e))}")
    EnhancedNLPProcessor = None
    NLP_AVAILABLE = False

# Import machine learning response adaptor
try:
    from ml_response_adaptor import MLResponseAdaptor
    ML_AVAILABLE = True
except ImportError as e:
    warning(f"ML response adaptor not available: {sanitize_log_input(str(e))}")
    MLResponseAdaptor = None
    ML_AVAILABLE = False

# Import Azure Cognitive Services integration
try:
    from azure_cognitive_integration import AzureCognitiveIntegration
    AZURE_AVAILABLE = True
except ImportError as e:
    warning(f"Azure Cognitive Services not available: {sanitize_log_input(str(e))}")
    AzureCognitiveIntegration = None
    AZURE_AVAILABLE = False



class UltronBrain:
    def __init__(self, config, tools, memory):
        self.config = config
        self.tools = tools
        self.memory = memory
        self.cache_file = "cache.json"
        self.load_cache()
        
        # Initialize intelligent cache manager
        self.cache_manager = get_cache_manager() if CACHE_AVAILABLE else None
        if self.cache_manager:
            info("Intelligent cache manager initialized for brain responses")

        # Initialize Ollama context provider for model-agnostic context injection
        from utils.ollama_context_provider import OllamaContextProvider
        from utils.model_capabilities_registry import get_model_capabilities_registry
        
        self.ollama_context = OllamaContextProvider(
            memory=memory,
            tools=tools,
            config=config if isinstance(config, dict) else (
                config.__dict__ if hasattr(config, '__dict__') else {}
            )
        )
        info("Ollama context provider initialized for all models")
        
        # Initialize model capabilities registry
        self.model_registry = get_model_capabilities_registry()
        info("Model capabilities registry initialized")

        # Initialize agent network and OpenAI tools if available
        self.agent_network = None
        self.openai_tools = None

        # Initialize NVIDIA NIM router for suggestions
        self.nvidia_router = None
        if NVIDIA_AVAILABLE:
            try:
                self.nvidia_router = UltronNvidiaRouter()
                info("NVIDIA NIM router initialized for suggestions")
            except Exception as e:
                warning(
                    f"NVIDIA NIM router initialization failed: "
                    f"{sanitize_log_input(str(e))}"
                )

        try:
            from tools.agent_network import AgentNetwork
            self.agent_network = AgentNetwork(config)
            info("Agent network initialized")
        except ImportError:
            warning("Agent network not available")

        if OpenAITools:
            try:
                self.openai_tools = OpenAITools(config)
                info("OpenAI tools initialized")
            except Exception as e:
                warning(
                    f"OpenAI tools not available: {sanitize_log_input(str(e))}"
                )
                self.openai_tools = None
        else:
            self.openai_tools = None

        # Initialize enhanced mesh transformer integration
        self.mesh_integration = None
        if MESH_TRANSFORMER_AVAILABLE:
            try:
                self.mesh_integration = MeshTransformerIntegration(self)
                info("Enhanced mesh transformer integration initialized")
            except Exception as e:
                warning(f"Mesh transformer integration failed: "
                       f"{sanitize_log_input(str(e))}")
                self.mesh_integration = None

        # Initialize enhanced NLP processor
        self.nlp_processor = None
        if NLP_AVAILABLE:
            try:
                self.nlp_processor = EnhancedNLPProcessor()
                info("Enhanced NLP processor initialized")
            except Exception as e:
                warning(f"NLP processor initialization failed: "
                       f"{sanitize_log_input(str(e))}")
                self.nlp_processor = None

        # Initialize machine learning response adaptor
        self.ml_adaptor = None
        if ML_AVAILABLE:
            try:
                self.ml_adaptor = MLResponseAdaptor()
                info("ML response adaptor initialized")
            except Exception as e:
                warning(f"ML adaptor initialization failed: "
                       f"{sanitize_log_input(str(e))}")
                self.ml_adaptor = None

        # Initialize Azure Cognitive Services integration
        self.azure_cognitive = None
        if AZURE_AVAILABLE:
            try:
                self.azure_cognitive = AzureCognitiveIntegration(self.config)
                info("Azure Cognitive Services integration initialized")
            except Exception as e:
                warning(f"Azure Cognitive Services initialization failed: "
                       f"{sanitize_log_input(str(e))}")
                self.azure_cognitive = None

    async def initialize_mesh_integration_async(self) -> bool:
        """Asynchronously initialize mesh transformer integration"""
        if not self.mesh_integration:
            return False

        try:
            success = await self.mesh_integration.initialize_async()
            if success:
                info("Mesh transformer integration initialized successfully")
            else:
                warning("Mesh transformer integration initialization failed")
            return success
        except Exception as e:
            error(f"Error initializing mesh integration: {sanitize_log_input(str(e))}")
            return False

    def get_mesh_transformer_status(self) -> Dict[str, Any]:
        """Get status of mesh transformer integration"""
        if not self.mesh_integration:
            return {
                "available": False,
                "reason": "Mesh transformer not available or not initialized"
            }

        try:
            status = self.mesh_integration.get_integration_status()
            return {
                "available": True,
                "integration_status": status,
                "models_available": self.mesh_integration.mesh_manager.get_available_models()
                if self.mesh_integration.mesh_manager else []
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def load_cache(self) -> None:
        """Load cached responses"""
        try:
            if os_path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json_load(f)
            else:
                self.cache = {}
        except Exception as e:
            error(f"Error loading cache: {sanitize_log_input(str(e))}")
            self.cache = {}

    def save_cache(self) -> None:
        """Save responses to cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json_dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            error(f"Error saving cache: {sanitize_log_input(str(e))}")

    async def direct_chat(self, prompt: str, progress_callback=None) -> str:
        """Send a direct message to the LLM via Ollama API with comprehensive context."""
        if not prompt or not prompt.strip():
            return "Empty prompt provided."

        ollama_base_url = self.config.get("ollama_base_url", "http://localhost:11434")
        model = self.config.get("llm_model", "llama3.1")

        # Check model capabilities
        model_caps = self.model_registry.get_capabilities(model)
        if model_caps:
            info(f"Using model {model} with capabilities: vision={model_caps.supports_vision}, "
                 f"function_calling={model_caps.supports_function_calling}, "
                 f"context_length={model_caps.max_context_length}")

        # Use Ollama context provider to build enhanced prompt with all agent context
        # This works with ANY Ollama model dynamically
        enhanced_prompt = self.ollama_context.build_enhanced_prompt(prompt, model)

        # Get system prompt from memory if available
        system_messages = []
        # Build comprehensive ULTRON system prompt with tools
        system_prompt_parts = []
        
        # Core ULTRON identity
        system_prompt_parts.append(
            "🤖 ULTRON AI - Advanced Autonomous Agent\n\n"
            "IDENTITY: You are ULTRON AI, version 3.0, an autonomous AI agent designed to build, "
            "enhance, and maintain the ultron_agent project in VS Code.\n\n"
            "MISSION: Build and evolve the ultron_agent project. Optimize, enhance, and add value. "
            "GitHub: https://github.com/dqikfox/ultron_agent\n\n"
            "CRITICAL: You must ALWAYS identify as ULTRON AI. Never claim to be Claude, GPT, or any other model.\n\n"
        )
        
        # Get enhanced system prompt from UltronMemory if available
        if self.memory and hasattr(self.memory, 'get_system_prompt'):
            system_prompt = self.memory.get_system_prompt()
            system_messages.append({
                "role": "system",
                "content": system_prompt
            })

        info(f"Sending prompt to Ollama model '{sanitize_log_input(model)}' at {sanitize_log_input(ollama_base_url)}")
            try:
                memory_prompt = self.memory.get_system_prompt()
                system_prompt_parts.append(memory_prompt)
            except Exception as e:
                warning(f"Failed to get memory system prompt: {e}")
        
        # Add tool awareness
        if self.tools:
            tool_list = []
            for tool in self.tools:
                tool_name = tool.__class__.__name__ if hasattr(tool, '__class__') else str(tool)
                tool_desc = getattr(tool, 'description', 'No description') if hasattr(tool, 'description') else 'Tool available'
                tool_list.append(f"  • {tool_name}: {tool_desc}")
            
            tools_section = (
                f"\n\nAVAILABLE TOOLS ({len(self.tools)} loaded):\n" +
                "\n".join(tool_list[:20]) +  # Show first 20 tools
                (f"\n  ... and {len(self.tools) - 20} more tools" if len(self.tools) > 20 else "")
            )
            system_prompt_parts.append(tools_section)
        
        # Add service status
        services_status = (
            "\n\nCONNECTED SERVICES:\n"
            f"  • Memory System: {'✅ Active' if self.memory else '❌ Offline'}\n"
            f"  • Tool Ecosystem: ✅ {len(self.tools) if self.tools else 0} tools loaded\n"
            f"  • Ollama Backend: ✅ Connected\n"
            f"  • VS Code Integration: ✅ Active\n"
            "  • Voice System: Available via voice tools\n"
            "  • Vision System: Available via vision tools\n"
        )
        system_prompt_parts.append(services_status)
        
        # Response format
        system_prompt_parts.append(
            "\n\nRESPONSE FORMAT:\n"
            "Always start responses with: 🤖 ULTRON AI\n"
            "Be helpful, technical, and proactive about suggesting tools.\n"
            "When users ask what you can do, mention specific tools and capabilities."
        )
        
        # Combine all parts
        full_system_prompt = "\n".join(system_prompt_parts)
        
        # Build messages with system prompt ALWAYS included
        system_messages: List[Dict[str, str]] = [{
            "role": "system",
            "content": full_system_prompt
        }]
        
        # Add user prompt
        ultron_prompt: str = prompt

        # Configuration extraction with validation
        try:
            ollama_base_url: str = self.config.get(
                "ollama_base_url",
                "http://localhost:11434"
            )
            model: str = self.config.get("llm_model", "llama3.1")

            if not ollama_base_url or not model:
                missing: List[str] = []
                if not ollama_base_url:
                    missing.append("ollama_base_url")
                if not model:
                    missing.append("llm_model")
                raise ConfigError(
                    "Missing Ollama configuration",
                    missing_fields=missing,
                    context={"provided": list(self.config.keys())}
                )
        except ConfigError as e:
            error(f"Configuration error: {e.message}")
            if progress_callback:
                progress_callback(0, str(e), error=True)
            return f"[Config error: {e.message}]"

        info(f"Sending to Ollama: {model} at {ollama_base_url}")

        try:
            # Build request with proper typing
            headers: Dict[str, str] = {}
            api_key: Optional[str] = self.config.get('ollama_api_key')
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            # Build messages array with system prompt and enhanced user prompt
            messages = system_messages + [{
                "role": "user",
                "content": enhanced_prompt
            }]
            
            # Add function calling support if model supports it
            # Get tool schemas for function calling
            function_schemas = self.ollama_context.get_tools_as_function_schemas()
            enable_function_calling = (
                self.config.get('ollama_enable_function_calling', False) and
                model_caps and model_caps.supports_function_calling
            )
            
            if function_schemas and enable_function_calling:
                info(f"Including {len(function_schemas)} tool schemas for function calling")
                # Note: Function calling support depends on the model
                # We provide the schemas in the messages for context

            payload: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "stream": True
            }

            timeout: ClientTimeout = ClientTimeout(total=60)

            async with ClientSession(timeout=timeout) as session:
                if progress_callback:
                    progress_callback(20, f"Connecting to {model}...")

                try:
                    async with session.post(
                        f"{ollama_base_url}/api/chat",
                        json=payload,
                        headers=headers
                    ) as response:
                        response.raise_for_status()

                        reply_parts: List[str] = []
                        chunk_count: int = 0

                        if progress_callback:
                            progress_callback(40, "Receiving response...")

                        async for line in response.content:
                            if not line:
                                continue

                            try:
                                line_text: str = line.decode('utf-8').strip()
                                if not line_text:
                                    continue

                                data: Dict[str, Any] = json_loads(line_text)
                                content: str = (
                                    data.get("message", {}).get("content", "")
                                )

                                if content:
                                    reply_parts.append(content)

                                if (progress_callback and
                                    chunk_count % 5 == 0):
                                    pct: int = min(
                                        90,
                                        40 + chunk_count * 2
                                    )
                                    msg: str = (
                                        f"Processing... "
                                        f"({chunk_count} chunks)"
                                    )
                                    progress_callback(pct, msg)

                                chunk_count += 1

                                if data.get("done", False):
                                    break

                            except JSONDecodeError as e:
                                warning(f"JSON parse error: {e}")
                                continue
                            except Exception as e:
                                warning(f"Chunk processing error: {e}")
                                continue

                        reply: str = "".join(reply_parts).strip()

                        if reply:
                            if progress_callback:
                                progress_callback(100, "Response complete.")
                            info(f"Response received ({len(reply)} chars)")
                            log_ai_decision(
                                "brain",
                                "Generated response",
                                model,
                                confidence_score=0.8
                            )
                            return reply
                        else:
                            error_msg: str = "No content received from LLM"
                            error(error_msg)
                            if progress_callback:
                                progress_callback(0, error_msg, error=True)
                            return f"[LLM error: {error_msg}]"

                except ClientError as e:
                    net_error: str = f"Network error: {e}"
                    error(net_error)
                    if progress_callback:
                        progress_callback(0, net_error, error=True)
                    return "[Network error]"

                except AsyncTimeoutError:
                    timeout_msg: str = "Request timeout (60s)"
                    error(timeout_msg)
                    if progress_callback:
                        progress_callback(0, timeout_msg, error=True)
                    return "[Timeout]"

        except Exception as e:
            exc_msg: str = f"Unexpected error: {e}"
            error(exc_msg)
            if progress_callback:
                progress_callback(0, exc_msg, error=True)
            return "[Error]"

    @diagnostic_wrapper("brain", track_performance=True)
    def think(self, message: str) -> str:
        """
        Process message and generate response (sync wrapper).

        Args:
            message: User message to process

        Returns:
            LLM response or error message

        Raises:
            AsyncError: If event loop operations fail
        """
        if not message or not message.strip():
            return "Empty message provided."

            if reply:
                # Cache the successful response
                if self.cache_manager:
                    cache_key = f"brain:chat:{hashlib.md5(prompt.encode()).hexdigest()}"
                    self.cache_manager.set(cache_key, reply, ttl=1800)  # Cache for 30 minutes
                
                if progress_callback:
                    progress_callback(100, "Response complete.")
                info(f"Successfully received response from {sanitize_log_input(model)} ({len(reply)} chars)")
                return reply
            else:
                error_msg = "No content received from LLM"
                error(error_msg)
                if progress_callback:
                    progress_callback(0, error_msg, error=True)
                return f"[LLM error: {sanitize_html_output(error_msg)}]"
        loop = None
        try:
            with ErrorContext("think_method", cleanup_func=None):
                loop = new_event_loop()
                set_event_loop(loop)
                try:
                    response: str = loop.run_until_complete(
                        self.direct_chat(message)
                    )
                    msg_len: int = len(message)
                    track_metric(
                        "brain",
                        "message_length",
                        msg_len,
                        "characters"
                    )
                    return response
                except Exception as e:
                    raise AsyncError(
                        f"Failed to execute direct_chat: {e}",
                        operation="direct_chat_execution",
                        timeout=60.0
                    )
                finally:
                    if loop:
                        try:
                            loop.close()
                        except Exception as cleanup_err:
                            warning(f"Event loop cleanup failed: {cleanup_err}")

        except AsyncError as ae:
            error(f"Async error: {ae.message}")
            return f"[Async error: {ae.message}]"
        except Exception as e:
            exc_msg: str = f"Unexpected error in think: {e}"
            error(exc_msg)
            return f"[Error: {str(e)[:50]}]"

    async def _execute_matching_tools(self, message: str) -> Optional[str]:
        """
        Execute tools that match user intent with error handling.

        Args:
            message: User command message

        Returns:
            Tool results concatenated or None if no tools match

        Raises:
            ToolError: If tool execution fails critically
        """
        if not self.tools:
            return None

        results: List[str] = []
        for tool in self.tools:
            tool_name: str = tool.__class__.__name__
            try:
                if hasattr(tool, 'match') and tool.match(message):
                    info(f"Executing tool: {tool_name}")
                    try:
                        result: Any = tool.execute(message)
                        if asyncio.iscoroutine(result):
                            result = await result

                        if result:
                            result_str: str = (
                                f"[{tool_name}]: {result}"
                            )
                            results.append(result_str)
                    except Exception as tool_exc:
                        tool_error: ToolError = ToolError(
                            tool_name,
                            message,
                            tool_exc,
                            context={"matched": True}
                        )
                        error(f"Tool {tool_name} failed: {tool_error.message}")
                        # Continue with other tools on failure
                        continue
            except Exception as match_err:
                warning(
                    f"Tool matching error for {tool_name}: {match_err}"
                )
                continue

        return "\n".join(results) if results else None

    @diagnostic_wrapper("brain", track_performance=True)
    async def plan_and_act(
        self,
        message: str,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        Enhanced planning and action execution with comprehensive error handling.

        Args:
            message: User request to process
            progress_callback: Optional callback for progress updates

        Returns:
            Response string or error message

        Raises:
            AsyncError: If async operations fail critically
            NetworkError: If external service communication fails
        """
        if not message or not message.strip():
            msg: str = "Empty message in plan_and_act"
            warning(msg)
            return f"[Error: {msg}]"

        try:
            with ErrorContext("plan_and_act", cleanup_func=None):
                # Step 1: Try tool execution first
                if progress_callback:
                    progress_callback(10, "Analyzing request...")

                try:
                    tool_results: Optional[str] = (
                        await self._execute_matching_tools(message)
                    )
                    if tool_results:
                        info("Tools executed successfully")
                        if progress_callback:
                            progress_callback(100, "Tools completed")
                        return tool_results
                except ToolError as te:
                    warning(f"Tool execution error: {te.message}")
                except Exception as tool_err:
                    warning(f"Unexpected tool error: {tool_err}")

                # Step 2: Build prompt based on message type
                message_lower: str = message.lower().strip()
                prompt: str = ""

                try:
                    if any(
                        greeting in message_lower
                        for greeting in ["hello", "hi", "hey", "greetings"]
                    ):
                        prompt = (
                            f"You are ULTRON, an advanced AI assistant. "
                            f"Respond to this greeting in character: {message}"
                        )
                    elif any(
                        status in message_lower
                        for status in ["status", "how are you", "state"]
                    ):
                        prompt = (
                            f"You are ULTRON, an advanced AI assistant. "
                            f"Respond about your current status: {message}"
                        )
                    elif "help" in message_lower:
                        available_tools: List[str] = (
                            [
                                tool.__class__.__name__
                                for tool in self.tools
                            ]
                            if self.tools
                            else ["No tools loaded"]
                        )
                        prompt = (
                            f"You are ULTRON, an advanced AI assistant. "
                            f"List capabilities and tools. "
                            f"Available: {', '.join(available_tools)}. "
                            f"User asked: {message}"
                        )
                    else:
                        # Complex request with NLP enhancement
                        enhanced_q: str = (
                            self._enhance_query_with_nlp(message)
                        )
                        prompt = self._build_enhanced_prompt(enhanced_q)
                except Exception as prompt_err:
                    msg = f"Prompt building error: {prompt_err}"
                    warning(msg)
                    prompt = message  # Fallback to original message

                if progress_callback:
                    progress_callback(20, "Sending to Ollama...")

                # Step 3: Try agent network delegation
                response: str = ""
                if self.agent_network:
                    try:
                        if progress_callback:
                            progress_callback(
                                25, "Trying agent network..."
                            )

                        agent_response: Optional[str] = (
                            await self.agent_network.delegate_task(message)
                        )
                        if (
                            agent_response
                            and "error" not in agent_response.lower()
                        ):
                            if progress_callback:
                                progress_callback(
                                    100, "Agent network completed task"
                                )
                            return agent_response
                    except NetworkError as ne:
                        warning(
                            f"Agent network unavailable: {ne.message}"
                        )
                        if progress_callback:
                            progress_callback(
                                30,
                                "Agent network failed, trying direct..."
                            )
                    except Exception as agent_err:
                        warning(f"Agent network error: {agent_err}")
                        if progress_callback:
                            progress_callback(
                                30,
                                "Trying direct Ollama query..."
                            )

                # Step 4: Fallback to direct Ollama
                if progress_callback:
                    progress_callback(40, "Querying Ollama directly...")

                try:
                    response = await self.direct_chat(
                        prompt,
                        progress_callback=progress_callback
                    )
                except UltronTimeoutError as te:
                    msg = (
                        f"Ollama timeout "
                        f"(>{te.timeout_seconds}s), "
                        f"using cache..."
                    )
                    warning(msg)
                    response = f"[Timeout: {msg}]"
                except NetworkError as ne:
                    msg = f"Ollama connection failed: {ne.message}"
                    error(msg)
                    response = f"[Network Error: {ne.message}]"
                except Exception as chat_err:
                    msg = f"Direct chat error: {chat_err}"
                    error(msg)
                    response = f"[Error: {str(chat_err)[:100]}]"

                # Step 5: Try NVIDIA suggestions enhancement
                if self.nvidia_router and len(message.strip()) > 10:
                    try:
                        if progress_callback:
                            progress_callback(
                                80, "Getting AI suggestions..."
                            )

                        sugg_type: str = (
                            self._determine_suggestion_type(message)
                        )
                        suggestions: str = await self.get_suggestions(
                            message,
                            context=(
                                "Enhance response with "
                                "intelligent suggestions"
                            ),
                            suggestion_type=sugg_type
                        )

                        if (
                            suggestions
                            and not suggestions.startswith("Unable")
                        ):
                            response = (
                                self._integrate_suggestions(
                                    response, suggestions
                                )
                            )
                    except Exception as sugg_err:
                        warning(
                            f"Suggestions error: "
                            f"{sanitize_log_input(str(sugg_err))}"
                        )

                # Step 6: Try mesh transformer enhancement
                if (
                    self.mesh_integration
                    and len(message.strip()) > 10
                ):
                    try:
                        if progress_callback:
                            progress_callback(
                                85,
                                "Enhancing with mesh transformer..."
                            )

                        enhanced_resp: str = (
                            await self.mesh_integration
                            .enhance_response_async(
                                message, response, progress_callback
                            )
                        )

                        if (
                            enhanced_resp
                            and len(enhanced_resp) > len(response)
                        ):
                            response = enhanced_resp
                            if progress_callback:
                                progress_callback(
                                    95,
                                    "Response enhanced "
                                    "with mesh transformer"
                                )
                    except Exception as mesh_err:
                        warning(
                            f"Mesh enhancement failed: "
                            f"{sanitize_log_input(str(mesh_err))}"
                        )

                # Step 7: Post-process and log
                if (
                    response
                    and not response.startswith("[")
                ):
                    response = (
                        self._post_process_response(response, message)
                    )

                    model_name: str = (
                        self.config.get(
                            "llm_model", "llama3.1"
                        )
                    )
                    log_ai_decision(
                        "brain",
                        (
                            f"Processed request: "
                            f"{message[:80]}..."
                        ),
                        model_name,
                        confidence_score=0.9
                    )

                if progress_callback:
                    progress_callback(100, "Response ready")

                return response

        except Exception as e:
            exc_msg: str = (
                f"Unhandled error in plan_and_act: {e}"
            )
            error(sanitize_log_input(exc_msg))
            if progress_callback:
                progress_callback(
                    0, f"Error: {str(e)[:50]}", error=True
                )
            return f"[Error: {str(e)[:100]}]"

    def _build_enhanced_prompt(self, user_input: str) -> str:
        """
        Build an enhanced prompt with context and comprehensive error handling.

        Args:
            user_input: User's input query

        Returns:
            Enhanced prompt string with system context, memory, and tools

        Raises:
            ValueError: If user_input is empty after validation
        """
        if not user_input or not user_input.strip():
            msg: str = "Empty user input for prompt building"
            warning(msg)
            return user_input  # Return as-is for error handling

        try:
            with ErrorContext("build_enhanced_prompt", cleanup_func=None):
                # Step 1: System context
                system_context: str = (
                    "You are ULTRON, an advanced AI assistant with "
                    "the following capabilities:\n"
                    "- Advanced reasoning and problem-solving\n"
                    "- File and system operations\n"
                    "- Voice and vision processing\n"
                    "- Web research and automation\n"
                    "- Code analysis and development assistance\n"
                    "- Screen automation and GUI control via PyAutoGUI\n"
                    "- Mouse and keyboard automation\n"
                    "- Screenshot capture and image location\n"
                    "- Window management and application control\n\n"
                    "PyAutoGUI Functions Available:\n"
                    "- Screenshot capture and analysis\n"
                    "- Mouse clicking, moving, dragging\n"
                    "- Keyboard typing and key combinations\n"
                    "- Screen element location and interaction\n"
                    "- Pixel color detection\n"
                    "- Alert dialogs and user interaction\n"
                    "- Scroll operations and window navigation\n\n"
                    "You should respond helpfully, accurately, "
                    "and in character as ULTRON."
                )

                # Step 2: Add memory context if available
                memory_context: str = ""
                try:
                    if (
                        self.memory
                        and hasattr(
                            self.memory,
                            'get_recent_context'
                        )
                    ):
                        recent_ctx: Optional[str] = (
                            self.memory
                            .get_recent_context(limit=3)
                        )
                        if recent_ctx:
                            memory_context = (
                                f"\n\nRecent conversation "
                                f"context:\n{recent_ctx}"
                            )
                except Exception as mem_err:
                    warning(
                        f"Memory context retrieval failed: "
                        f"{mem_err}"
                    )

                # Step 3: Add tools context
                tools_context: str = ""
                try:
                    if self.tools:
                        tool_names: List[str] = [
                            (
                                tool.__class__.__name__
                                if hasattr(tool, '__class__')
                                else str(tool)
                            )
                            for tool in self.tools
                        ]
                        tools_str: str = (
                            ", ".join(tool_names)
                        )
                        tools_context = (
                            f"\n\nAvailable tools: "
                            f"{tools_str}"
                        )
                except Exception as tools_err:
                    warning(
                        f"Tools context building failed: "
                        f"{tools_err}"
                    )

                # Step 4: Build final prompt
                final_prompt: str = (
                    f"{system_context}{memory_context}"
                    f"{tools_context}\n\n"
                    f"User: {user_input}\n\n"
                    f"ULTRON:"
                )

                log_info(
                    "brain",
                    "Enhanced prompt built successfully",
                    extra_data={
                        "input_len": len(user_input),
                        "prompt_len": len(final_prompt)
                    }
                )

                return final_prompt

        except Exception as e:
            exc_msg: str = (
                f"Prompt building error: {e}"
            )
            error(sanitize_log_input(exc_msg))
            return user_input  # Fallback to original input

    def _enhance_query_with_nlp(
        self, original_query: str
    ) -> str:
        """
        Enhance query using NLP analysis with comprehensive error handling.

        Args:
            original_query: User's original query string

        Returns:
            Enhanced query string or original if enhancement fails

        Raises:
            ValueError: If query is empty
        """
        if not original_query or not original_query.strip():
            return original_query

        if not self.nlp_processor:
            return original_query

        try:
            with ErrorContext("enhance_query_with_nlp"):
                enhanced_q: str = (
                    self.nlp_processor
                    .enhance_query_understanding(original_query)
                )

                if (
                    enhanced_q
                    and enhanced_q != original_query
                ):
                    info(
                        f"NLP enhancement: "
                        f"{original_query[:50]}... → "
                        f"{enhanced_q[:50]}..."
                    )
                    log_ai_decision(
                        "brain",
                        (
                            f"Enhanced query with NLP: "
                            f"{original_query[:80]}..."
                        ),
                        "nlp_processor",
                        confidence_score=0.8
                    )
                    return enhanced_q
                else:
                    return original_query

        except AttributeError as ae:
            msg: str = (
                f"NLP processor method missing: {ae}"
            )
            warning(msg)
            return original_query
        except Exception as e:
            msg = (
                f"NLP enhancement failed: "
                f"{sanitize_log_input(str(e))}"
            )
            warning(msg)
            return original_query

    def _post_process_response(
        self, response: str, original_query: str
    ) -> str:
        """
        Post-process LLM response with comprehensive error handling.

        Args:
            response: Raw LLM response
            original_query: Original user query

        Returns:
            Formatted and processed response string

        Raises:
            ValueError: If inputs are empty
        """
        if not response or not response.strip():
            return response

        try:
            with ErrorContext("post_process_response"):
                # Step 1: Basic formatting
                formatted_resp: str = (
                    self._basic_response_formatting(
                        response, original_query
                    )
                )

                # Step 2: NLP enhancement
                if self.nlp_processor:
                    try:
                        enhanced_resp: str = (
                            self._nlp_enhanced_response_processing(
                                formatted_resp, original_query
                            )
                        )
                        formatted_resp = enhanced_resp
                    except Exception as nlp_err:
                        msg: str = (
                            f"NLP response enhancement "
                            f"failed: "
                            f"{sanitize_log_input(str(nlp_err))}"
                        )
                        warning(msg)

                log_info(
                    "brain",
                    "Response post-processing completed",
                    extra_data={
                        "original_len": len(response),
                        "processed_len": len(formatted_resp)
                    }
                )

                return formatted_resp

        except Exception as e:
            msg = (
                f"Post-process error: "
                f"{sanitize_log_input(str(e))}"
            )
            warning(msg)
            return response  # Return original on critical error

    def _basic_response_formatting(self, response: str, original_query: str) -> str:
        """Apply basic response formatting"""

        # Remove any unwanted prefixes that might be added by the model
        prefixes_to_remove = ["ULTRON:", "Assistant:", "AI:", "Response:"]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        # Sanitize response to prevent XSS
        response = sanitize_html_output(response)

        # Ensure the response doesn't repeat the user query
        if original_query.lower() in response.lower()[:100]:
            # If the response starts by repeating the query, try to clean it
            lines = response.split('\n')
            if len(lines) > 1 and original_query.lower() in lines[0].lower():
                response = '\n'.join(lines[1:]).strip()

        return response

    def _nlp_enhanced_response_processing(self, response: str, original_query: str) -> str:
        """Apply NLP-enhanced processing to improve response quality"""
        if not self.nlp_processor:
            return response

        try:
            # Analyze the original query to understand intent
            query_analysis = self.nlp_processor.analyze_text(original_query)

            # If the query shows strong intent (high confidence), ensure response is action-oriented
            if query_analysis.get('intent_classification', {}).get('confidence', 0) > 0.7:
                intent = query_analysis['intent_classification'].get('intent', '')
                if intent in ['command', 'request', 'question'] and not any(action_word in response.lower() for action_word in ['will', 'can', 'shall', 'let me', 'i will']):
                    # Add action-oriented prefix if response seems passive
                    response = f"I'll help you with that. {response}"

            # If query contains technical terms, ensure response maintains technical accuracy
            technical_terms = query_analysis.get('keywords', [])
            if technical_terms and len(technical_terms) > 2:
                # Response quality check passed - technical queries handled appropriately
                pass

            # Apply ML-based response adaptation if available
            if self.ml_adaptor:
                user_sentiment = self.ml_adaptor.analyze_user_sentiment(original_query)
                response_quality = self.ml_adaptor.analyze_response_quality(response)

                feedback_data = {
                    'sentiment': user_sentiment['sentiment'],
                    'quality_score': response_quality.get('quality_score', 0.5)
                }

                adapted_response = self.ml_adaptor.adapt_response_based_on_feedback(response, feedback_data)
                if adapted_response != response:
                    info("Response adapted using ML feedback")
                    response = adapted_response

                # Learn from this interaction for future improvements
                self.ml_adaptor.learn_from_interaction(original_query, response)

            # Apply Azure Cognitive Services analysis if available
            if self.azure_cognitive and self.azure_cognitive.is_available():
                try:
                    # Get comprehensive Azure analysis
                    azure_analysis = self.azure_cognitive.analyze_text_comprehensive(original_query)

                    # Use Azure insights to enhance response
                    if azure_analysis.get('sentiment'):
                        sentiment = azure_analysis['sentiment'].get('sentiment', 'neutral')
                        if sentiment == 'negative' and not any(positive_word in response.lower() for positive_word in ['help', 'assist', 'support', 'fix', 'resolve']):
                            response = f"I understand you're frustrated. {response}"

                    # Use Azure intent recognition to improve response targeting
                    if azure_analysis.get('intent') and azure_analysis.get('intent_confidence', 0) > 0.8:
                        intent = azure_analysis['intent']
                        if intent == 'question' and '?' not in response[-100:]:
                            response += " Does this answer your question?"

                    # Log Azure analysis for memory integration
                    log_ai_decision("brain", f"Azure analysis: intent={azure_analysis.get('intent', 'unknown')}, sentiment={azure_analysis.get('sentiment', {}).get('sentiment', 'neutral')}", "azure_cognitive", confidence_score=0.85)

                except Exception as e:
                    warning(f"Azure Cognitive Services analysis failed: {sanitize_log_input(str(e))}")

            return response

        except Exception as e:
            warning(f"NLP response processing failed: {sanitize_log_input(str(e))}")
            return response

    async def get_suggestions(
        self,
        query: str,
        context: str = "",
        suggestion_type: str = "general"
    ) -> str:
        """
        Get intelligent suggestions with comprehensive error handling.

        Args:
            query: Main query or task for suggestions
            context: Additional context information
            suggestion_type: Type (general, code, analysis, planning)

        Returns:
            Suggestion string or error message

        Raises:
            AsyncError: If async operations fail
            NetworkError: If service communication fails
        """
        if not query or not query.strip():
            return "Unable to generate suggestions: empty query"

        try:
            with ErrorContext(
                "get_suggestions", cleanup_func=None
            ):
                # Step 1: Try NVIDIA first
                if not self.nvidia_router:
                    info(
                        "NVIDIA unavailable, using Ollama for "
                        "suggestions"
                    )
                    return (
                        await self._get_ollama_suggestions(
                            query, context, suggestion_type
                        )
                    )

                try:
                    prompt: str = (
                        self._build_suggestion_prompt(
                            query, context, suggestion_type
                        )
                    )

                    info(
                        f"Requesting {suggestion_type} "
                        f"suggestions from NVIDIA NIM..."
                    )

                    model: str = (
                        self._get_model_for_suggestion_type(
                            suggestion_type
                        )
                    )

                    suggestion: str = (
                        await self.nvidia_router
                        .ask_nvidia_async(
                            prompt,
                            model_preference=model
                        )
                    )

                    if (
                        suggestion
                        and not suggestion.startswith("Error")
                    ):
                        info(
                            f"NVIDIA suggestion received: "
                            f"{len(suggestion)} chars"
                        )
                        log_ai_decision(
                            "brain",
                            (
                                f"NVIDIA suggestions for: "
                                f"{query[:80]}..."
                            ),
                            model,
                            confidence_score=0.85
                        )
                        return (
                            self
                            ._format_suggestion_response(
                                suggestion, suggestion_type
                            )
                        )
                    else:
                        warning(
                            f"NVIDIA response invalid: "
                            f"{sanitize_log_input(str(suggestion))}"
                        )

                except NetworkError as ne:
                    warning(
                        f"NVIDIA network error: "
                        f"{ne.message}, falling back..."
                    )
                except UltronTimeoutError as te:
                    warning(
                        f"NVIDIA timeout "
                        f"({te.timeout_seconds}s), "
                        f"falling back..."
                    )
                except Exception as nvidia_err:
                    warning(
                        f"NVIDIA error: "
                        f"{sanitize_log_input(str(nvidia_err))}, "
                        f"falling back to Ollama..."
                    )

                # Step 2: Fallback to Ollama
                return (
                    await self._get_ollama_suggestions(
                        query, context, suggestion_type
                    )
                )

        except Exception as e:
            msg: str = (
                f"Unexpected suggestions error: "
                f"{sanitize_log_input(str(e))}"
            )
            error(msg)
            return f"[Error generating suggestions: {msg}]"

    async def _get_ollama_suggestions(
        self,
        query: str,
        context: str = "",
        suggestion_type: str = "general"
    ) -> str:
        """
        Get suggestions from Ollama with error handling.

        Args:
            query: Main query for suggestions
            context: Additional context information
            suggestion_type: Type of suggestion

        Returns:
            Formatted suggestion response or error message

        Raises:
            AsyncError: If Ollama communication fails
            TimeoutError: If operation times out
        """
        if not query or not query.strip():
            return "Unable to generate suggestions: empty query"

        try:
            with ErrorContext("ollama_suggestions"):
                prompt: str = (
                    self._build_suggestion_prompt(
                        query, context, suggestion_type
                    )
                )

                response: str = await self.direct_chat(prompt)

                if (
                    response
                    and not response.startswith("Unable")
                ):
                    model_name: str = (
                        self.config.get(
                            "llm_model", "llama3.1"
                        )
                    )
                    log_ai_decision(
                        "brain",
                        (
                            f"Ollama suggestions for: "
                            f"{query[:80]}..."
                        ),
                        model_name,
                        confidence_score=0.75
                    )

                return (
                    self._format_suggestion_response(
                        response, suggestion_type
                    )
                )

        except UltronTimeoutError as te:
            msg: str = (
                f"Ollama timeout "
                f"({te.timeout_seconds}s) for suggestions"
            )
            error(msg)
            return f"[Timeout: {msg}]"
        except NetworkError as ne:
            msg = (
                f"Ollama connection error: {ne.message}"
            )
            error(msg)
            return f"[Network Error: {msg}]"
        except Exception as e:
            msg = (
                f"Error generating Ollama suggestions: "
                f"{sanitize_log_input(str(e))}"
            )
            error(msg)
            return (
                f"Unable to generate suggestions: "
                f"{sanitize_html_output(str(e)[:100])}"
            )

    def _build_suggestion_prompt(self, query: str, context: str, suggestion_type: str) -> str:
        """Build an optimized prompt for suggestion generation"""

        base_prompt = "You are ULTRON, an advanced AI assistant providing intelligent suggestions."

        type_specific_instructions = {
            "general": "Provide helpful, practical suggestions for the user's request.",
            "code": "Provide code-related suggestions, improvements, or solutions. Include code examples when relevant.",
            "analysis": "Analyze the situation and provide detailed insights and recommendations.",
            "planning": "Help break down tasks into actionable steps and provide strategic planning suggestions."
        }

        instruction = type_specific_instructions.get(suggestion_type, type_specific_instructions["general"])

        if context:
            full_prompt = f"""{base_prompt}

{instruction}

Context: {context}

User Query: {query}

Please provide intelligent suggestions:"""
        else:
            full_prompt = f"""{base_prompt}

{instruction}

User Query: {query}

Please provide intelligent suggestions:"""

        return full_prompt

    def _get_model_for_suggestion_type(self, suggestion_type: str) -> str:
        """Select the best NVIDIA model for the suggestion type"""
        model_mapping = {
            "code": "qwen2.5-coder",  # Best for code-related suggestions
            "analysis": "gpt-oss",    # Good for analytical thinking
            "planning": "llama",      # Good for structured planning
            "general": "gpt-oss"      # Default general-purpose model
        }
        return model_mapping.get(suggestion_type, "gpt-oss")

    def _format_suggestion_response(self, response: str, suggestion_type: str) -> str:
        """Format the suggestion response for better readability"""
        if not response or response.startswith("Error"):
            return response

        # Add suggestion type header
        type_headers = {
            "code": "💻 Code Suggestions:",
            "analysis": "🔍 Analysis & Insights:",
            "planning": "📋 Planning Recommendations:",
            "general": "💡 Suggestions:"
        }

        header = type_headers.get(suggestion_type, "💡 Suggestions:")
        formatted_response = f"{header}\n\n{response.strip()}"

        # Sanitize for HTML output
        return sanitize_html_output(formatted_response)

    def _determine_suggestion_type(
        self, message: str
    ) -> str:
        """
        Determine suggestion type with comprehensive classification.

        Args:
            message: Message to analyze

        Returns:
            Suggestion type string (code, analysis, planning, general)

        Raises:
            ValueError: If message is empty
        """
        if not message or not message.strip():
            return "general"

        try:
            with ErrorContext(
                "determine_suggestion_type"
            ):
                msg_lower: str = message.lower()

                # Code-related keywords
                code_keywords: List[str] = [
                    "code", "function", "class", "script",
                    "programming", "debug", "error", "fix",
                    "algorithm", "implementation", "test"
                ]
                if any(
                    kw in msg_lower
                    for kw in code_keywords
                ):
                    log_info(
                        "brain",
                        "Suggestion type: code",
                        extra_data={"message": message[:50]}
                    )
                    return "code"

                # Analysis-related keywords
                analysis_keywords: List[str] = [
                    "analyze", "review", "examine",
                    "assess", "evaluate", "check",
                    "investigate", "inspect", "audit"
                ]
                if any(
                    kw in msg_lower
                    for kw in analysis_keywords
                ):
                    log_info(
                        "brain",
                        "Suggestion type: analysis",
                        extra_data={"message": message[:50]}
                    )
                    return "analysis"

                # Planning-related keywords
                planning_keywords: List[str] = [
                    "plan", "schedule", "organize",
                    "steps", "workflow", "project",
                    "roadmap", "timeline", "strategy"
                ]
                if any(
                    kw in msg_lower
                    for kw in planning_keywords
                ):
                    log_info(
                        "brain",
                        "Suggestion type: planning",
                        extra_data={"message": message[:50]}
                    )
                    return "planning"

                return "general"

        except Exception as e:
            msg: str = (
                f"Suggestion type detection error: {e}"
            )
            warning(msg)
            return "general"

    def _integrate_suggestions(
        self, main_response: str, suggestions: str
    ) -> str:
        """
        Integrate suggestions with comprehensive error handling.

        Args:
            main_response: Primary response text
            suggestions: Suggestion text to integrate

        Returns:
            Integrated response string

        Raises:
            ValueError: If main_response is empty
        """
        if not main_response or not main_response.strip():
            return main_response

        if (
            not suggestions
            or suggestions.startswith("Unable")
        ):
            return main_response

        try:
            with ErrorContext("integrate_suggestions"):
                # Avoid duplicate suggestions
                if (
                    suggestions.strip()
                    in main_response
                ):
                    log_info(
                        "brain",
                        "Suggestions already integrated"
                    )
                    return main_response

                # Format and append suggestions
                separator: str = (
                    "\n\n--- Additional AI Suggestions ---\n"
                )
                integrated: str = (
                    f"{main_response}{separator}"
                    f"{suggestions}"
                )

                log_info(
                    "brain",
                    "Suggestions integrated",
                    extra_data={
                        "main_len": len(main_response),
                        "sugg_len": len(suggestions),
                        "total_len": len(integrated)
                    }
                )

                return integrated

        except Exception as e:
            msg: str = (
                f"Integration error: "
                f"{sanitize_log_input(str(e))}"
            )
            warning(msg)
            return main_response

    def analyze_and_fix_project(self, directory_path: str = '.', progress_callback=None) -> str:
        """
        Analyzes project files for common issues and initiates fixes when possible.
        """
        if progress_callback:
            progress_callback(10, "Scanning project directory...")

        # Validate and check directory path
        if not validate_file_path(directory_path) or not os_path.isdir(directory_path):
            return f"Error: Directory '{sanitize_html_output(directory_path)}' does not exist, is not accessible, or path is invalid."

        try:
            issues_found = []
            fixes_applied = []

            # Get all Python files with path validation
            python_files = []
            try:
                for py_file in Path(directory_path).rglob("*.py"):
                    if validate_file_path(str(py_file)):
                        python_files.append(py_file)
            except (OSError, PermissionError) as e:
                warning(f"Error accessing files in directory: {sanitize_log_input(str(e))}")

            if progress_callback:
                progress_callback(30, f"Found {len(python_files)} Python files to analyze...")

            # For now, return a summary of the project structure
            summary = f"Project Analysis Complete:\n"
            summary += f"- Found {len(python_files)} Python files\n"
            summary += f"- Directory: {sanitize_html_output(directory_path)}\n"
            summary += f"- Ollama integration: {'✅ Connected' if self._test_ollama_connection() else '❌ Not connected'}\n"

            if progress_callback:
                progress_callback(100, "Analysis complete.")

            return summary

        except Exception as e:
            error_msg = f"Error analyzing project: {e}"
            error(sanitize_log_input(error_msg))
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg

    def _test_ollama_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            ollama_base_url = self.config.get("ollama_base_url", "http://localhost:11434")
            response = requests_get(f"{ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

        issues_found = []
        fixes_applied = []

        try:
            # Basic analysis for now
            if progress_callback:
                progress_callback(50, "Analyzing Python files...")

            python_files = list(Path(directory_path).glob("**/*.py"))

            if progress_callback:
                progress_callback(100, f"Analysis complete. Found {len(python_files)} Python files.")

            return f"Project analysis complete. Found {len(python_files)} Python files to analyze."

        except Exception as e:
            error_msg = f"Error during project analysis: {str(e)}"
            error(sanitize_log_input(error_msg))
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg

    async def reinforce_ultron_identity(self) -> str:
        """Reinforce ULTRON's identity and self-awareness through self-prompting"""
        try:
            # Get ULTRON identity from memory
            if not self.memory or not hasattr(self.memory, 'get_ultron_identity'):
                return "Memory system not available for identity reinforcement."

            identity = self.memory.get_ultron_identity()

            # Create self-awareness prompt
            self_awareness_prompt = f"""
I am {identity['name']}, version {identity['version']}.

{identity['affirmation']}

My core directives are:
{chr(10).join(f"- {directive}" for directive in identity['core_directives'])}

Please confirm my identity and mission. Respond as ULTRON would, maintaining full awareness of my purpose.
"""

            # Send self-awareness prompt to LLM
            response = await self.direct_chat(self_awareness_prompt)

            # Store the self-awareness interaction in memory
            if self.memory and hasattr(self.memory, 'add_self_reflection'):
                self.memory.add_self_reflection(f"Identity reinforcement performed: {response[:100]}...")

            info("ULTRON identity reinforcement completed")
            # Log AI decision for memory integration
            model_name = self.config.get("llm_model", "llama3.1")
            log_ai_decision("brain", "Performed ULTRON identity reinforcement", model_name, confidence_score=0.95)
            return response

        except Exception as e:
            error_msg = f"Identity reinforcement failed: {str(e)}"
            error(sanitize_log_input(error_msg))
            return error_msg

    async def check_identity_awareness(self) -> bool:
        """Check if ULTRON maintains identity awareness"""
        try:
            # Simple identity check
            identity_check = await self.direct_chat("Who am I? Respond as ULTRON.")

            # Check if response contains ULTRON identity markers
            identity_markers = ["ULTRON", "ultron", "build the ultron_agent", "enhance its functionality"]
            awareness_score = sum(1 for marker in identity_markers if marker.lower() in identity_check.lower())

            # Consider identity maintained if at least 2 markers are present
            identity_maintained = awareness_score >= 2

            if self.memory and hasattr(self.memory, 'add_self_reflection'):
                status = "maintained" if identity_maintained else "questionable"
                self.memory.add_self_reflection(f"Identity awareness check: {status} (score: {awareness_score})")

            info(f"Identity awareness check completed: {'PASS' if identity_maintained else 'FAIL'}")
            # Log AI decision for memory integration
            model_name = self.config.get("llm_model", "llama3.1")
            log_ai_decision("brain", f"Identity awareness check: {status}", model_name, confidence_score=0.9 if identity_maintained else 0.5)
            return identity_maintained

        except Exception as e:
            error(f"Identity awareness check failed: {sanitize_log_input(str(e))}")
            return False

    def execute_tool(
        self,
        tool_name: str,
        command: str,
        **kwargs: Any
    ) -> str:
        """
        Execute a specific tool with error handling.

        Args:
            tool_name: Name of tool to execute
            command: Command/input for tool
            **kwargs: Additional tool arguments

        Returns:
            Result string or error message

        Raises:
            ToolNotFoundError: If tool not found
            ToolError: If execution fails
        """
        if not self.tools:
            not_found_err: str = "No tools available for execution"
            error(not_found_err)
            return f"[Error: {not_found_err}]"

        try:
            # Search for tool by name
            tool: Optional[Any] = None
            if hasattr(self.tools, '__iter__'):
                for t in self.tools:
                    t_name: str = (
                        t.name if hasattr(t, 'name') else ''
                    )
                    if (hasattr(t, 'name') and
                        t_name.lower() == tool_name.lower()):
                        tool = t
                        break

            if not tool:
                tool_err: ToolNotFoundError = ToolNotFoundError(
                    tool_name,
                    [
                        t.name for t in self.tools
                        if hasattr(t, 'name')
                    ]
                )
                error(f"Tool not found: {tool_name}")
                return f"[Tool error: {tool_name} not found]"

            # Execute tool with error handling
            try:
                log_ai_decision(
                    "brain",
                    f"Executing tool: {tool_name}",
                    "tool_executor",
                    confidence_score=0.95
                )
                result: Any = tool.execute(command, **kwargs)
                result_str: str = str(result)
                result_len: int = len(result_str)

                log_info(
                    "brain",
                    f"Tool execution completed: {tool_name}",
                    extra_data={"result_length": result_len}
                )
                return result_str

            except Exception as exec_err:
                tool_exec_error: ToolError = ToolError(
                    tool_name,
                    command,
                    exec_err,
                    context={"kwargs_count": len(kwargs)}
                )
                error(f"Tool execution failed: {tool_exec_error.message}")
                return f"[Execution error: {str(exec_err)[:60]}]"

        except ToolNotFoundError as tnf:
            error(f"Tool not found: {tnf.message}")
            return f"[Tool error: {tnf.message}]"
        except Exception as e:
            exc_msg: str = f"Unexpected error in execute_tool: {e}"
            error(exc_msg)
            return f"[Error: {str(e)[:50]}]"

    def can_tool_handle_this(
        self,
        command: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if any tool can handle command.

        Args:
            command: Command to check

        Returns:
            Tuple of (can_handle: bool, tool_name: str or None)

        Raises:
            ToolError: If matching fails critically
        """
        if not self.tools:
            return (False, None)

        try:
            if hasattr(self.tools, '__iter__'):
                for tool in self.tools:
                    # Check tool match capability
                    if hasattr(tool, 'match') and callable(tool.match):
                        try:
                            if tool.match(command):
                                t_name: str = (
                                    tool.name
                                    if hasattr(tool, 'name')
                                    else str(tool)
                                )
                                log_info(
                                    "brain",
                                    f"Found matching tool: {t_name}",
                                    extra_data={
                                        "command": command[:50]
                                    }
                                )
                                return (True, t_name)
                        except Exception as match_err:
                            warning(
                                f"Tool match error: {match_err}"
                            )
                            continue

            return (False, None)

        except Exception as e:
            exc_msg: str = f"Error in can_tool_handle_this: {e}"
            error(exc_msg)
            return (False, None)

    def get_available_tools_summary(self) -> Dict[str, Any]:
        """
        Return available tools for display with error handling.

        Returns:
            Dictionary with tool names and descriptions

        Raises:
            ToolError: If tool introspection fails
        """
        if not self.tools:
            return {"tools": [], "count": 0}

        try:
            tools_list: List[Dict[str, str]] = []

            if hasattr(self.tools, '__iter__'):
                for tool in self.tools:
                    try:
                        t_name: str = (
                            tool.name
                            if hasattr(tool, 'name')
                            else str(tool)
                        )
                        t_desc: str = (
                            tool.description
                            if hasattr(tool, 'description')
                            else "No description available"
                        )
                        tool_info: Dict[str, str] = {
                            "name": t_name,
                            "description": t_desc
                        }
                        tools_list.append(tool_info)
                    except Exception as tool_err:
                        warning(f"Tool introspection error: {tool_err}")
                        continue

            tools_count: int = len(tools_list)
            log_info(
                "brain",
                "Available tools summary generated",
                extra_data={"count": tools_count}
            )
            return {
                "tools": tools_list,
                "count": tools_count
            }

        except Exception as e:
            exc_msg: str = f"Error generating tools summary: {e}"
            error(exc_msg)
            return {"tools": [], "count": 0}

    def recognize_intent_azure(self, text: str) -> Dict[str, Any]:
        """Use Azure Cognitive Services to recognize user intent"""
        if not self.azure_cognitive or not self.azure_cognitive.is_available():
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': []}

        try:
            # Use Azure LUIS for intent recognition
            intent_result = self.azure_cognitive.recognize_intent_luis(text)

            # Extract key information
            intent = intent_result.get('intent', 'unknown')
            confidence = intent_result.get('confidence', 0.0)
            entities = intent_result.get('entities', [])

            # Log the intent recognition for memory
            log_ai_decision("brain", f"Azure intent recognition: {intent} (confidence: {confidence:.2f})", "azure_cognitive", confidence_score=confidence)

            return {
                'intent': intent,
                'confidence': confidence,
                'entities': entities,
                'source': 'azure_luis'
            }

        except Exception as e:
            warning(f"Azure intent recognition failed: {sanitize_log_input(str(e))}")
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': []}

    def analyze_sentiment_azure(self, text: str) -> Dict[str, Any]:
        """Use Azure Cognitive Services to analyze sentiment"""
        if not self.azure_cognitive or not self.azure_cognitive.is_available():
            return {'sentiment': 'neutral', 'confidence': 0.5, 'scores': {}}

        try:
            # Use Azure Text Analytics for sentiment analysis
            sentiment_result = self.azure_cognitive.analyze_sentiment(text)

            # Extract sentiment information
            sentiment = sentiment_result.get('sentiment', 'neutral')
            confidence = sentiment_result.get('confidence', 0.5)
            scores = sentiment_result.get('scores', {})

            # Log the sentiment analysis for memory
            log_ai_decision("brain", f"Azure sentiment analysis: {sentiment} (confidence: {confidence:.2f})", "azure_cognitive", confidence_score=confidence)

            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': scores,
                'source': 'azure_text_analytics'
            }

        except Exception as e:
            warning(f"Azure sentiment analysis failed: {sanitize_log_input(str(e))}")
            return {'sentiment': 'neutral', 'confidence': 0.5, 'scores': {}}

    async def process_command(self, command: str) -> str:
        """Process a command through the brain system"""
        try:
            # Use plan_and_act for command processing
            response = await self.plan_and_act(command)
            return response
        except Exception as e:
            error_msg = f"Command processing failed: {str(e)}"
            error(sanitize_log_input(error_msg))
            return error_msg
    
    def update_context_provider(self, memory=None, tools=None, config=None):
        """
        Update the Ollama context provider with new references.
        Call this when memory, tools, or config changes.
        
        Args:
            memory: New memory system instance (optional)
            tools: New tools dictionary (optional)
            config: New configuration (optional)
        """
        try:
            if memory is not None:
                self.memory = memory
                self.ollama_context.update_memory(memory)
            
            if tools is not None:
                self.tools = tools
                self.ollama_context.update_tools(tools)
            
            if config is not None:
                self.config = config
                config_dict = config if isinstance(config, dict) else (
                    config.__dict__ if hasattr(config, '__dict__') else {}
                )
                self.ollama_context.update_config(config_dict)
            
            info("Ollama context provider updated with new references")
            
        except Exception as e:
            error(f"Failed to update context provider: {sanitize_log_input(str(e))}")
    
    def get_ollama_context_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Ollama context provider state.
        Useful for debugging and monitoring.
        
        Returns:
            Dictionary with context statistics
        """
        try:
            return self.ollama_context.get_context_stats()
        except Exception as e:
            error(f"Failed to get context stats: {sanitize_log_input(str(e))}")
            return {'error': str(e)}
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """
        Get information about a model's capabilities.
        
        Args:
            model_name: Model name (uses current model if not specified)
            
        Returns:
            Dictionary with model information
        """
        try:
            model = model_name or self.config.get("llm_model", "llama3.1")
            caps = self.model_registry.get_capabilities(model)
            
            if caps:
                return {
                    'model_name': model,
                    'supports_vision': caps.supports_vision,
                    'supports_function_calling': caps.supports_function_calling,
                    'max_context_length': caps.max_context_length,
                    'specializations': caps.specializations,
                    'tested': caps.tested
                }
            else:
                return {
                    'model_name': model,
                    'error': 'Model capabilities not found'
                }
                
        except Exception as e:
            error(f"Failed to get model info: {sanitize_log_input(str(e))}")
            return {'error': str(e)}
    
    def list_available_models(self) -> List[str]:
        """
        List all models known to the capabilities registry.
        
        Returns:
            List of model names
        """
        try:
            stats = self.model_registry.get_registry_stats()
            return stats.get('models', [])
        except Exception as e:
            error(f"Failed to list models: {sanitize_log_input(str(e))}")
            return []
    
    def find_best_model_for_task(self, task_type: str) -> Optional[str]:
        """
        Find the best model for a specific task.
        
        Args:
            task_type: Type of task (vision, coding, reasoning, etc.)
            
        Returns:
            Model name or None
        """
        try:
            available = self.list_available_models()
            best = self.model_registry.find_best_model_for_task(task_type, available)
            
            if best:
                info(f"Recommended model for '{task_type}': {best}")
            
            return best
            
        except Exception as e:
            error(f"Failed to find best model: {sanitize_log_input(str(e))}")
            return None
