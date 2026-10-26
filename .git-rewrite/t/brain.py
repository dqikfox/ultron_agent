"""
ULTRON Agent 3.0 - Brain Module with Ollama Integration
Handles AI reasoning, planning, and communication with Ollama models
"""

from logging import getLogger, info, error, warning
from os import path as os_path, listdir
from re import sub as re_sub
from json import loads as json_loads, dumps as json_dumps, JSONDecodeError
from requests import get as requests_get
from asyncio import new_event_loop, set_event_loop, TimeoutError as AsyncTimeoutError
from aiohttp import ClientSession, ClientError, ClientTimeout
from pathlib import Path
from security_utils import sanitize_log_input, sanitize_html_output, validate_file_path

from tools.openai_tools import OpenAITools

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

        try:
            from tools.agent_network import AgentNetwork
            self.agent_network = AgentNetwork(config)
            info("Agent network initialized")
        except ImportError:
            warning("Agent network not available")

        try:
            self.openai_tools = OpenAITools(config)
            info("OpenAI tools initialized")
        except Exception as e:
            warning(f"OpenAI tools not available: {sanitize_log_input(str(e))}")

    def load_cache(self):
        """Load cached responses"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            error(f"Error loading cache: {sanitize_log_input(str(e))}")
            self.cache = {}

    def save_cache(self):
        """Save responses to cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            error(f"Error saving cache: {sanitize_log_input(str(e))}")

    async def direct_chat(self, prompt: str, progress_callback=None) -> str:
        """Send a direct message to the LLM via Ollama API."""
        if not prompt or not prompt.strip():
            return "Empty prompt provided."

        ollama_base_url = self.config.get("ollama_base_url", "http://localhost:11434")
        model = self.config.get("llm_model", "qwen2.5:latest")

        info(f"Sending prompt to Ollama model '{sanitize_log_input(model)}' at {sanitize_log_input(ollama_base_url)}")

        try:
            headers = {}
            if api_key := self.config.get('ollama_api_key'):
                headers["Authorization"] = f"Bearer {api_key}"

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
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

    def think(self, message):
        """Process a message and generate a response using Ollama"""
        try:
            # Run async direct_chat in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(self.direct_chat(message))
                return response
            finally:
                loop.close()

        except Exception as e:
            error(f"Error in think method: {sanitize_log_input(str(e))}")
            return f"Error processing request: {sanitize_html_output(str(e))}"

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
                # For complex requests, use enhanced prompting
                prompt = self._build_enhanced_prompt(message)

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

            # Post-process the response
            if response and not response.startswith("["):  # Not an error message
                response = self._post_process_response(response, message)

            return response

        except Exception as e:
            error_msg = f"Error in plan_and_act: {e}"
            error(sanitize_log_input(error_msg))
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg

    def _build_enhanced_prompt(self, user_input: str) -> str:
        """Build an enhanced prompt with context and instructions"""

        # System context
        system_context = """You are ULTRON, an advanced AI assistant with the following capabilities:
- Advanced reasoning and problem-solving
- File and system operations
- Voice and vision processing
- Web research and automation
- Code analysis and development assistance

You should respond helpfully, accurately, and in character as ULTRON."""

        # Add memory context if available
        memory_context = ""
        if self.memory and hasattr(self.memory, 'get_recent_context'):
            try:
                recent_context = self.memory.get_recent_context(limit=3)
                if recent_context:
                    memory_context = f"\n\nRecent conversation context:\n{recent_context}"
            except Exception as e:
                logging.warning(f"Could not retrieve memory context: {e}")

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

    def _post_process_response(self, response: str, original_query: str) -> str:
        """Post-process the LLM response for better formatting"""

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
