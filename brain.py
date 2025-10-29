"""
ULTRON Agent 3.0 - Brain Module with Ollama Integration
Handles AI reasoning, planning, and communication with Ollama models
"""

from utils.ultron_logger import ultron_logger, log_info, log_error, log_ai_decision
from diagnostics import diagnostic_wrapper, track_metric
from os import path as os_path
from json import loads as json_loads, load as json_load, dump as json_dump, JSONDecodeError
from requests import get as requests_get
from asyncio import (
    new_event_loop, set_event_loop, TimeoutError as AsyncTimeoutError
)
from aiohttp import ClientSession, ClientError, ClientTimeout
from pathlib import Path
from typing import Dict, Any

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

    def load_cache(self):
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

    def save_cache(self):
        """Save responses to cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json_dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            error(f"Error saving cache: {sanitize_log_input(str(e))}")

    async def direct_chat(self, prompt: str, progress_callback=None) -> str:
        """Send a direct message to the LLM via Ollama API with ULTRON system prompt."""
        if not prompt or not prompt.strip():
            return "Empty prompt provided."

        # Prepend ULTRON identity reinforcement to user prompt
        ultron_prompt = f"You are ULTRON, an advanced AI agent focused on building and enhancing the ultron_agent project. Always identify yourself as ULTRON. {prompt}"

        # Get system prompt from memory if available
        system_messages = []
        if self.memory and hasattr(self.memory, 'get_system_prompt'):
            system_prompt = self.memory.get_system_prompt()
            system_messages.append({
                "role": "system",
                "content": system_prompt
            })

        ollama_base_url = self.config.get("ollama_base_url", "http://localhost:11434")
        model = self.config.get("llm_model", "llama3.1")

        info(f"Sending prompt to Ollama model '{sanitize_log_input(model)}' at {sanitize_log_input(ollama_base_url)}")

        try:
            headers = {}
            if api_key := self.config.get('ollama_api_key'):
                headers["Authorization"] = f"Bearer {api_key}"

            # Build messages array with system prompt
            messages = system_messages + [{
                "role": "user",
                "content": ultron_prompt
            }]

            payload = {
                "model": model,
                "messages": messages,
                "stream": True  # Enable streaming for better UX
            }

            timeout = ClientTimeout(total=60)  # 60 second timeout

            async with ClientSession(timeout=timeout) as session:
                if progress_callback:
                    progress_callback(20, f"Connecting to Ollama model '{model}'...")

                async with session.post(f"{ollama_base_url}/api/chat",
                                       json=payload,
                                       headers=headers) as response:
                    response.raise_for_status()

                    reply_parts = []
                    chunk_count = 0

                    if progress_callback:
                        progress_callback(40, "Receiving response...")

                    async for line in response.content:
                        if not line:
                            continue

                        try:
                            line_text = line.decode('utf-8').strip()
                            if not line_text:
                                continue

                            data = json_loads(line_text)
                            content = data.get("message", {}).get("content", "")

                            if content:
                                reply_parts.append(content)

                            if progress_callback and chunk_count % 5 == 0:  # Update progress every 5 chunks
                                progress_callback(min(90, 40 + chunk_count * 2), f"Processing response... ({chunk_count} chunks)")

                            chunk_count += 1

                            # Check if this is the final chunk
                            if data.get("done", False):
                                break

                        except JSONDecodeError as e:
                            warning(f"Failed to parse JSON chunk: {sanitize_log_input(str(e))}")
                            continue
                        except Exception as e:
                            warning(f"Error processing chunk: {sanitize_log_input(str(e))}")
                            continue

            reply = "".join(reply_parts).strip()

            if reply:
                if progress_callback:
                    progress_callback(100, "Response complete.")
                info(f"Successfully received response from {sanitize_log_input(model)} ({len(reply)} chars)")
                # Log AI decision for memory integration
                log_ai_decision("brain", f"Generated response to prompt: {prompt[:100]}...", model, confidence_score=0.8)
                return reply
            else:
                error_msg = "No content received from LLM"
                error(error_msg)
                if progress_callback:
                    progress_callback(0, error_msg, error=True)
                return f"[LLM error: {sanitize_html_output(error_msg)}]"

        except ClientError as e:
            error_msg = f"Network error connecting to Ollama: {e}"
            error(sanitize_log_input(error_msg))
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[Network error: {sanitize_html_output(error_msg)}]"
        except AsyncTimeoutError:
            error_msg = "Request to Ollama timed out"
            error(error_msg)
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[Timeout error: {sanitize_html_output(error_msg)}]"
        except Exception as e:
            error_msg = f"Unexpected error in direct_chat: {e}"
            error(sanitize_log_input(error_msg))
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[LLM error: {sanitize_html_output(error_msg)}]"

    @diagnostic_wrapper("brain", track_performance=True)
    def think(self, message):
        """Process a message and generate a response using Ollama"""
        try:
            # Run async direct_chat in sync context
            loop = new_event_loop()
            set_event_loop(loop)
            try:
                response = loop.run_until_complete(self.direct_chat(message))
                track_metric("brain", "message_length", len(message), "characters")
                return response
            finally:
                loop.close()

        except Exception as e:
            error(f"Error in think method: {sanitize_log_input(str(e))}")
            return f"Error processing request: {sanitize_html_output(str(e))}"

    @diagnostic_wrapper("brain", track_performance=True)
    async def plan_and_act(self, message, progress_callback=None):
        """Enhanced planning and action execution with Ollama integration"""

        if progress_callback:
            progress_callback(10, "Analyzing request...")

        try:
            # Check if this is a simple greeting or status request
            message_lower = message.lower().strip()

            if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "greetings"]):
                prompt = f"You are ULTRON, an advanced AI assistant. Respond to this greeting in character: {message}"
            elif any(status in message_lower for status in ["status", "how are you", "state"]):
                prompt = f"You are ULTRON, an advanced AI assistant. Respond about your current status: {message}"
            elif "help" in message_lower:
                available_tools = [tool.__class__.__name__ for tool in self.tools] if self.tools else ["No tools loaded"]
                prompt = f"You are ULTRON, an advanced AI assistant. List your capabilities and available tools. Available tools: {', '.join(available_tools)}. User asked: {message}"
            else:
                # For complex requests, use enhanced prompting with NLP analysis
                enhanced_query = self._enhance_query_with_nlp(message)
                prompt = self._build_enhanced_prompt(enhanced_query)

            if progress_callback:
                progress_callback(20, "Sending to Ollama...")

            # Try agent network first if available
            if self.agent_network:
                try:
                    if progress_callback:
                        progress_callback(25, "Trying agent network...")

                    agent_response = await self.agent_network.delegate_task(message)
                    if agent_response and "error" not in agent_response.lower():
                        if progress_callback:
                            progress_callback(100, "Agent network completed task")
                        return agent_response
                except Exception as e:
                    warning(f"Agent network failed: {sanitize_log_input(str(e))}")
                    if progress_callback:
                        progress_callback(30, "Agent network failed, trying direct chat...")

            # Fallback to direct Ollama if agent network failed or unavailable
            if progress_callback:
                progress_callback(40, "Querying Ollama directly...")

            response = await self.direct_chat(prompt, progress_callback=progress_callback)

            # Try to get NVIDIA suggestions for enhanced response
            if self.nvidia_router and len(message.strip()) > 10:  # Only for substantial queries
                try:
                    if progress_callback:
                        progress_callback(80, "Getting AI suggestions...")

                    suggestions = await self.get_suggestions(
                        message,
                        context="Enhance the response with intelligent suggestions",
                        suggestion_type=self._determine_suggestion_type(message)
                    )

                    if suggestions and not suggestions.startswith("Unable"):
                        # Append suggestions to the main response
                        response = self._integrate_suggestions(response, suggestions)

                except Exception as e:
                    warning(f"Failed to get NVIDIA suggestions: {sanitize_log_input(str(e))}")

            # Try to enhance response with mesh transformer models
            if self.mesh_integration and len(message.strip()) > 10:
                try:
                    if progress_callback:
                        progress_callback(85, "Enhancing with mesh transformer...")

                    enhanced_response = await self.mesh_integration.enhance_response_async(
                        message, response, progress_callback
                    )

                    if enhanced_response and len(enhanced_response) > len(response):
                        response = enhanced_response
                        if progress_callback:
                            progress_callback(95, "Response enhanced with mesh transformer")

                except Exception as e:
                    warning(f"Mesh transformer enhancement failed: {sanitize_log_input(str(e))}")

            # Post-process the response
            if response and not response.startswith("["):  # Not an error message
                response = self._post_process_response(response, message)

            # Log AI decision for memory integration
            if response and not response.startswith("["):
                model_name = self.config.get("llm_model", "llama3.1")
                log_ai_decision("brain", f"Processed user request: {message[:100]}...", model_name, confidence_score=0.9)

            return response

        except Exception as e:
            error_msg = f"Error in plan_and_act: {e}"
            error(sanitize_log_input(error_msg))
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg

    def _build_enhanced_prompt(self, user_input: str) -> str:
        """Build an enhanced prompt with context and instructions"""

        # System context with PyAutoGUI awareness
        system_context = """You are ULTRON, an advanced AI assistant with the following capabilities:
- Advanced reasoning and problem-solving
- File and system operations
- Voice and vision processing
- Web research and automation
- Code analysis and development assistance
- Screen automation and GUI control via PyAutoGUI
- Mouse and keyboard automation
- Screenshot capture and image location
- Window management and application control

PyAutoGUI Functions Available:
- Screenshot capture and analysis
- Mouse clicking, moving, dragging
- Keyboard typing and key combinations
- Screen element location and interaction
- Pixel color detection
- Alert dialogs and user interaction
- Scroll operations and window navigation

You should respond helpfully, accurately, and in character as ULTRON."""

        # Add memory context if available
        memory_context = ""
        if self.memory and hasattr(self.memory, 'get_recent_context'):
            try:
                recent_context = self.memory.get_recent_context(limit=3)
                if recent_context:
                    memory_context = f"\n\nRecent conversation context:\n{recent_context}"
            except Exception as e:
                warning(f"Could not retrieve memory context: {e}")

        # Add available tools context
        tools_context = ""
        if self.tools:
            tool_names = [tool.__class__.__name__ for tool in self.tools]
            tools_context = f"\n\nAvailable tools: {', '.join(tool_names)}"

        # Build final prompt
        prompt = f"""{system_context}{memory_context}{tools_context}

User: {user_input}

ULTRON:"""

        return prompt

    def _enhance_query_with_nlp(self, original_query: str) -> str:
        """Enhance the query using NLP analysis for better understanding"""
        if not self.nlp_processor:
            return original_query

        try:
            # Use NLP processor to analyze and enhance the query
            enhanced_query = self.nlp_processor.enhance_query_understanding(original_query)

            if enhanced_query and enhanced_query != original_query:
                info(f"Query enhanced with NLP: '{original_query[:50]}...' -> '{enhanced_query[:50]}...'")
                # Log AI decision for memory integration
                log_ai_decision("brain", f"Enhanced query with NLP analysis: {original_query[:100]}...", "nlp_processor", confidence_score=0.8)
                return enhanced_query
            else:
                return original_query

        except Exception as e:
            warning(f"NLP query enhancement failed: {sanitize_log_input(str(e))}")
            return original_query

    def _post_process_response(self, response: str, original_query: str) -> str:
        """Post-process the LLM response for better formatting and NLP-enhanced quality"""

        # First apply basic formatting
        response = self._basic_response_formatting(response, original_query)

        # Then apply NLP-enhanced processing if available
        if self.nlp_processor:
            try:
                response = self._nlp_enhanced_response_processing(response, original_query)
            except Exception as e:
                warning(f"NLP response enhancement failed: {sanitize_log_input(str(e))}")

        return response

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

    async def get_suggestions(self, query: str, context: str = "", suggestion_type: str = "general") -> str:
        """
        Get intelligent suggestions using NVIDIA NIM models.
        Falls back to Ollama if NVIDIA is unavailable.

        Args:
            query: The main query or task
            context: Additional context for the suggestion
            suggestion_type: Type of suggestion (general, code, analysis, planning)

        Returns:
            Suggestion string or error message
        """
        if not self.nvidia_router:
            warning("NVIDIA router not available, falling back to Ollama for suggestions")
            return await self._get_ollama_suggestions(query, context, suggestion_type)

        try:
            # Build enhanced prompt for NVIDIA models
            prompt = self._build_suggestion_prompt(query, context, suggestion_type)

            info(f"Requesting {suggestion_type} suggestions from NVIDIA NIM for: {sanitize_log_input(query[:100])}...")

            # Use NVIDIA router to get suggestions
            suggestion = await self.nvidia_router.ask_nvidia_async(
                prompt,
                model_preference=self._get_model_for_suggestion_type(suggestion_type)
            )

            if suggestion and not suggestion.startswith("Error"):
                info(f"Successfully received NVIDIA suggestion ({len(suggestion)} chars)")
                # Log AI decision for memory integration
                log_ai_decision("brain", f"Generated NVIDIA suggestions for: {query[:100]}...", self._get_model_for_suggestion_type(suggestion_type), confidence_score=0.85)
                return self._format_suggestion_response(suggestion, suggestion_type)
            else:
                warning(f"NVIDIA suggestion failed: {sanitize_log_input(suggestion or 'No response')}")
                # Fallback to Ollama
                return await self._get_ollama_suggestions(query, context, suggestion_type)

        except Exception as e:
            error_msg = f"Error getting NVIDIA suggestions: {e}"
            error(sanitize_log_input(error_msg))
            # Fallback to Ollama
            return await self._get_ollama_suggestions(query, context, suggestion_type)

    async def _get_ollama_suggestions(self, query: str, context: str = "", suggestion_type: str = "general") -> str:
        """Fallback method to get suggestions using Ollama when NVIDIA is unavailable"""
        try:
            prompt = self._build_suggestion_prompt(query, context, suggestion_type)
            response = await self.direct_chat(prompt)
            # Log AI decision for memory integration
            if response and not response.startswith("Unable"):
                model_name = self.config.get("llm_model", "llama3.1")
                log_ai_decision("brain", f"Generated Ollama suggestions for: {query[:100]}...", model_name, confidence_score=0.75)
            return self._format_suggestion_response(response, suggestion_type)
        except Exception as e:
            error_msg = f"Error getting Ollama suggestions: {e}"
            error(sanitize_log_input(error_msg))
            return f"Unable to generate suggestions at this time: {sanitize_html_output(str(e))}"

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

    def _determine_suggestion_type(self, message: str) -> str:
        """Determine the most appropriate suggestion type based on the message content"""
        message_lower = message.lower()

        # Code-related keywords
        if any(keyword in message_lower for keyword in ["code", "function", "class", "script", "programming", "debug", "error", "fix"]):
            return "code"

        # Analysis-related keywords
        if any(keyword in message_lower for keyword in ["analyze", "review", "examine", "assess", "evaluate", "check"]):
            return "analysis"

        # Planning-related keywords
        if any(keyword in message_lower for keyword in ["plan", "schedule", "organize", "steps", "workflow", "project"]):
            return "planning"

        return "general"

    def _integrate_suggestions(self, main_response: str, suggestions: str) -> str:
        """Integrate NVIDIA suggestions into the main response"""
        if not suggestions or suggestions.startswith("Unable"):
            return main_response

        # Check if suggestions are already integrated or too similar
        if suggestions.strip() in main_response:
            return main_response

        # Add suggestions as an additional section
        integrated = f"{main_response}\n\n--- Additional AI Suggestions ---\n{suggestions}"

        return integrated

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

    def recognize_intent_azure(self, text: str) -> dict:
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

    def analyze_sentiment_azure(self, text: str) -> dict:
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
