import logging
import os
import re
import json
import requests
from pathlib import Path

def analyze_and_fix_project(self, directory_path: str = '.', progress_callback=None) -> str:
    """
    Analyzes project files for common issues and initiates fixes when possible.

    Args:
        directory_path: Path to the project directory to analyze (defaults to current directory)
        progress_callback: Optional callback function to report progress

    Returns:
        A summary of issues found and fixes applied
    """
    if progress_callback:
        progress_callback(10, "Scanning project directory...")
    
    # Make sure the directory exists
    if not os.path.isdir(directory_path):
        return f"Error: Directory '{directory_path}' does not exist or is not accessible."
    issues_found = []
    fixes_applied = []

    try:
        # Get all Python files in the directory
        python_files = list(Path(directory_path).rglob("*.py"))
        total_files = len(python_files)

        if progress_callback:
            progress_callback(20, f"Found {total_files} Python files to analyze.")

        if total_files == 0:
            return "No Python files found in the specified directory."

        # Common code issues to detect
        patterns = {
            "missing_logging": (r'except.*?:', r'(?!.*logging\.)', "Exception handler without logging"),
            "bare_except": (r'except\s*:', None, "Bare except clause (should specify exception type)"),
            "unreferenced_import": (r'import\s+(\w+)', r'(?!.*\1)', "Potentially unused import"),
            "hardcoded_credentials": (r'(?:password|api_key|secret)\s*=\s*["\'](?!None|BASE_|ENV_|os\.getenv)[^"\']+["\']',
                                     None, "Possible hardcoded credential"),
            "unhandled_file_io": (r'open\(', r'(?!.*try)', "File operation without error handling")
        }

        # Process each file
        for i, file_path in enumerate(python_files):
            if progress_callback:
                progress_callback(20 + (70 * i // total_files), f"Analyzing {file_path.name}...")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_issues = []
                file_rel_path = os.path.relpath(file_path, directory_path)

                # Check for issues
                for issue_type, (pattern, negative_pattern, description) in patterns.items():
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        # If there's a negative pattern and it matches, skip this instance
                        if negative_pattern and re.search(negative_pattern, match.group(0)):
                            continue

                        line_num = content[:match.start()].count('\n') + 1
                        issue = f"{file_rel_path}:{line_num} - {description}"
                        file_issues.append((issue_type, issue, line_num))

                # Apply simple fixes for certain issues
                if file_issues:
                    issues_found.extend([issue for _, issue, _ in file_issues])

                    # Attempt fixes
                    modified_content = content
                    fix_applied = False

                    # Add logging to exception handlers
                    for issue_type, _, line_num in file_issues:
import asyncio
                            lines = modified_content.split('\n')
                            if line_num < len(lines):
                                # Insert logging after the except line
                                indent_match = re.match(r'^(\s*)', lines[line_num-1])
                                indent = indent_match.group(1) if indent_match else "    "
                                logging_line = f"{indent}    logging.exception('Error occurred:')"

                                # Only insert if not already present
                                if not any("logging.exception" in line for line in lines[line_num:line_num+2]):
                                    lines.insert(line_num, logging_line)
                                    modified_content = '\n'.join(lines)
from tools.agent_network import AgentNetwork
                                    fix_applied = True

                    # Save changes if fixes were applied
                    if fix_applied:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)

            except Exception as e:
                logging.exception(f"Error analyzing {file_path}: {e}")
                issues_found.append(f"Error analyzing {file_path}: {e}")

        # Prepare summary
        summary = []
        if issues_found:
            summary.append(f"Found {len(issues_found)} potential issues:")
            for issue in issues_found[:10]:  # Limit to first 10 issues
                summary.append(f"- {issue}")

            if len(issues_found) > 10:
                summary.append(f"... and {len(issues_found) - 10} more issues.")
        else:
            summary.append("No issues found in the codebase.")

        if fixes_applied:
            summary.append(f"\nApplied {len(fixes_applied)} automatic fixes:")
            for fix in fixes_applied[:10]:  # Limit to first 10 fixes
                summary.append(f"- {fix}")

            if len(fixes_applied) > 10:
                summary.append(f"... and {len(fixes_applied) - 10} more fixes.")

        if progress_callback:
            progress_callback(100, "Analysis complete.")

        return "\n".join(summary)

    except Exception as e:
        error_msg = f"Error analyzing project: {e}"
        logging.exception(error_msg)
        if progress_callback:
            progress_callback(0, error_msg, error=True)
        return error_msg
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
        if config.data.get("openai_api_key"):
            try:
                self.agent_network = AgentNetwork(config)
                self.openai_tools = OpenAITools(config)
                self._register_tools()
                logging.info("Agent network initialized - brain.py:157")
            except Exception as e:
                logging.error(f"Agent network initialization failed: {e} - brain.py:159")

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logging.error(f"Failed to load cache: {e} - brain.py:169")
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get_tool_descriptions(self) -> str:
        return "\n".join([
            f"- {t.name}: {t.description}\n  Parameters: {getattr(t, 'parameters', {})}" for t in self.tools
        ])

    async def direct_chat(self, prompt: str, progress_callback=None) -> str:
        """Send a direct message to the LLM without any tools or complex logic."""
        if not prompt or not prompt.strip():
            return "Empty prompt provided."
            
        ollama_base_url = self.config.data.get("ollama_base_url", "http://localhost:11434")
        model = self.config.data.get("llm_model", "qwen2.5")
        
        try:
            # Use aiohttp for async requests instead of requests
            import aiohttp
            import json as jsonlib
            
            headers = {}
            if api_key := self.config.data.get('ollama_api_key'):
                headers["Authorization"] = f"Bearer {api_key}"
                
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True  # Enable streaming for better UX
            }
            
            timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{ollama_base_url}/api/chat", 
                                       json=payload, 
                                       headers=headers) as response:
                    response.raise_for_status()
                    
                    reply_parts = []
                    chunk_count = 0
                    
                    async for line in response.content:
                        if not line:
                            continue
                            
                        try:
                            line_text = line.decode('utf-8').strip()
                            if not line_text:
                                continue
                                
                            data = jsonlib.loads(line_text)
                            content = data.get("message", {}).get("content", "")
                            
                            if content:
                                reply_parts.append(content)
                                
                            if progress_callback and chunk_count % 5 == 0:  # Update progress every 5 chunks
                                progress_callback(min(90, chunk_count * 2), f"Processing response... ({chunk_count} chunks)")
                                
                            chunk_count += 1
                            
                            # Check if this is the final chunk
                            if data.get("done", False):
                                break
                                
                        except jsonlib.JSONDecodeError as e:
                            logging.warning(f"Failed to parse JSON chunk: {e} - brain.py:240")
                            continue
                        except Exception as e:
                            logging.warning(f"Error processing chunk: {e} - brain.py:243")
                            continue
            
            reply = "".join(reply_parts).strip()
            
            if reply:
                if progress_callback:
                    progress_callback(100, "Response complete.")
                logging.info(f"Successfully received response from {model} ({len(reply)} chars) - brain.py:251")
                return reply
            else:
                error_msg = "No content received from LLM"
                logging.error(f"{error_msg} - brain.py:255")
                if progress_callback:
                    progress_callback(0, error_msg, error=True)
                return f"[LLM error: {error_msg}]"
                
        except aiohttp.ClientError as e:
            error_msg = f"Network error connecting to Ollama: {e}"
            logging.error(f"{error_msg} - brain.py:262")
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[Network error: {error_msg}]"
        except asyncio.TimeoutError:
            error_msg = "Request to Ollama timed out"
            logging.error(f"{error_msg} - brain.py:268")
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[Timeout error: {error_msg}]"
        except Exception as e:
            error_msg = f"Unexpected error in direct_chat: {e}"
            logging.error(f"{error_msg} - brain.py:274")
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[LLM error: {error_msg}]"

    def build_prompt(self, user_input: str, previous_steps: str | None = None) -> str:
        prompt = f"User: {user_input}\n"
        if previous_steps:
            prompt += f"Previous Steps: {previous_steps}\n"
        prompt += "Tools available:\n" + self.get_tool_descriptions() + "\n"
        prompt += "\nIf you want to use a tool, reply in the format: TOOL:<tool_name> PARAMS:<json_parameters>\n"
        return prompt

    def _register_tools(self):
        """Register available tools with the agent network."""
        if self.agent_network:
            tool_list = []
            for tool in self.tools:
                tool_dict = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": getattr(tool, 'parameters', {})
                    }
                }
                tool_list.append(tool_dict)
            self.agent_network.register_tools(tool_list)

    async def query_llm(self, prompt: str, progress_callback=None) -> str:
        """Query the LLM with caching and fallback mechanisms."""
        if not prompt or not prompt.strip():
            return "Empty prompt provided."
            
        # Use a more robust cache key that includes model info
        model = self.config.data.get("llm_model", "qwen2.5")
        cache_key = hash(f"{model}:{prompt}")
        
        # Check cache first
        if cache_key in self.cache:
            if progress_callback:
                progress_callback(100, "Loaded from cache.")
            logging.info("Response loaded from cache - brain.py:316")
            return self.cache[cache_key]

        try:
            response = None
            
            # Try agent network first if available
            if self.agent_network:
                try:
                    if progress_callback:
                        progress_callback(20, "Querying agent network...")
                        
                    context = {
                        "memory": self.memory.get_recent_memory() if self.memory else [],
                        "tools_available": len(self.tools) if self.tools else 0,
                        "model": model
                    }
                    
                    result = await self.agent_network.process_request(prompt, context=context)
                    response = result.get("response")
                    
                    if response:
                        logging.info("Response received from agent network - brain.py:338")
                    else:
                        logging.warning("Empty response from agent network - brain.py:340")
                        
                except Exception as e:
                    logging.error(f"Agent network query failed: {e} - brain.py:343")
                    if progress_callback:
                        progress_callback(30, "Agent network failed, trying direct chat...")

            # Fallback to direct Ollama if agent network failed or unavailable
            if not response:
                if progress_callback:
                    progress_callback(40, "Querying Ollama directly...")
                response = await self.direct_chat(prompt, progress_callback=progress_callback)

            # Cache successful responses (but not error messages)
            if response and not response.startswith("[") and not response.startswith("Error"):
                self.cache[cache_key] = response
                # Save cache periodically
                if len(self.cache) % 10 == 0:  # Save every 10 new entries
                    try:
                        self.save_cache()
                    except Exception as e:
                        logging.warning(f"Failed to save cache: {e} - brain.py:361")
                        
            return response or "[No response received from any LLM service]"

        except Exception as e:
            error_msg = f"Unexpected error in query_llm: {e}"
            logging.error(f"{error_msg} - brain.py:367")
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return f"[LLM error: {error_msg}]"

    async def plan_and_act(self, user_input: str, progress_callback=None) -> str:
        """Plan and execute actions based on user input with comprehensive error handling."""
        import re
        import json
        
        if not user_input or not user_input.strip():
            return "Please provide a valid command or question."
            
        user_input = user_input.strip()
        logging.info(f"Planning and acting on: {user_input[:100]}... - brain.py:381")
        
        try:
            # Update progress
            if progress_callback:
                progress_callback(10, "Building prompt...")
                
            # Build prompt with context
            prompt = self.build_prompt(user_input)
            
            if progress_callback:
                progress_callback(20, "Querying LLM...")
                
            # Query LLM
            reply = await self.query_llm(prompt, progress_callback=progress_callback)
            
            if not reply or reply.startswith("["):
                logging.warning(f"Invalid or error response from LLM: {reply[:100]}... - brain.py:398")
                return reply or "No response from LLM."
                
            if progress_callback:
                progress_callback(70, "Processing LLM response...")
                
            # Check for tool call in LLM reply using more robust regex
            tool_call = re.search(r'TOOL:\s*(\w+)\s+PARAMS:\s*(\{.*?\})(?=\s|$)', reply, re.DOTALL)
            
            if tool_call:
                tool_name = tool_call.group(1).strip()
                params_str = tool_call.group(2).strip()
                
                if progress_callback:
                    progress_callback(80, f"Executing tool: {tool_name}...")
                    
                try:
                    params = json.loads(params_str)
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse tool parameters: {e}\nRaw params: {params_str}"
                    logging.error(f"{error_msg} - brain.py:418")
                    return error_msg
                    
                # Find and execute the tool
                for tool in self.tools:
                    if hasattr(tool, 'name') and tool.name == tool_name:
                        try:
                            logging.info(f"Executing tool {tool_name} with params: {params} - brain.py:425")
                            result = tool.execute(**params)
                            
                            if progress_callback:
                                progress_callback(100, f"Tool {tool_name} executed successfully.")
                                
                            return result
                        except Exception as e:
                            error_msg = f"Tool '{tool_name}' execution error: {e}"
                            logging.error(f"{error_msg} - brain.py:434")
                            return error_msg
                            
                # Tool not found
                available_tools = [getattr(t, 'name', 'Unknown') for t in self.tools if hasattr(t, 'name')]
                error_msg = f"Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}"
                logging.warning(f"{error_msg} - brain.py:440")
                return error_msg
                
            if progress_callback:
                progress_callback(85, "Checking for direct tool matches...")
                
            # Fallback: try to match a tool by user input
            for tool in self.tools:
                if hasattr(tool, 'match') and tool.match(user_input):
                    try:
                        logging.info(f"Direct tool match found: {getattr(tool, 'name', tool.__class__.__name__)} - brain.py:450")
                        result = tool.execute(user_input)
                        
                        if progress_callback:
                            progress_callback(100, "Tool executed successfully.")
                            
                        return result
                    except Exception as e:
                        error_msg = f"Tool '{getattr(tool, 'name', tool.__class__.__name__)}' error: {e}"
                        logging.error(f"{error_msg} - brain.py:459")
                        return error_msg
                        
            # If user asked for functionality, list tools
            help_keywords = ["functionality", "can you do", "what can you do", "help", "tools", "capabilities"]
            if any(word in user_input.lower() for word in help_keywords):
                if progress_callback:
                    progress_callback(100, "Listing available tools.")
                return "Available tools and capabilities:\n" + self.get_tool_descriptions()
                
            # Return the LLM response as-is
            if progress_callback:
                progress_callback(100, "Response ready.")
                
            logging.info(f"Returning LLM response ({len(reply)} chars) - brain.py:473")
            return reply
            
        except Exception as e:
            error_msg = f"Unexpected error in plan_and_act: {e}"
            logging.error(f"{error_msg} - brain.py:478")
            if progress_callback:
                progress_callback(0, error_msg, error=True)
            return error_msg
