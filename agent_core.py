import logging
from memory import Memory
from voice import VoiceAssistant
from vision import Vision
from config import Config

from brain import UltronBrain

import subprocess
import requests
import time

def ensure_ollama_running(model_name="qwen2.5", base_url="http://localhost:11434"):
    """Check if Ollama is running and the model is loaded. If not, start it."""
    try:
        # Check if Ollama server is up
        resp = requests.get(f"{base_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            tags = resp.json().get("models", [])
            if any(model_name in m.get("name", "") for m in tags):
                print(f"Ollama is running and model '{model_name}' is loaded. - agent_core.py:21")
                return
            else:
                print(f"Ollama running but model '{model_name}' not loaded. Loading now... - agent_core.py:24")
        else:
            print("Ollama server responded but not healthy. Attempting to start. - agent_core.py:26")
    except Exception:
        print("Ollama not running. Attempting to start. - agent_core.py:28")
    # Start Ollama with the requested model
    try:
        # For Ollama, use system default (not Python interpreter)
        subprocess.Popen(["ollama", "run", model_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Started Ollama with model '{model_name}'. Waiting for it to be ready... - agent_core.py:32")
        # Wait for Ollama to be ready
        for _ in range(20):
            try:
                resp = requests.get(f"{base_url}/api/tags", timeout=2)
                if resp.status_code == 200:
                    tags = resp.json().get("models", [])
                    if any(model_name in m.get("name", "") for m in tags):
                        print(f"Ollama is now running with model '{model_name}'. - agent_core.py:40")
                        return
            except Exception:
                pass
            time.sleep(1)
        print("Warning: Ollama did not start in time. The agent may not function correctly. - agent_core.py:45")
    except Exception as e:
        print(f"Failed to start Ollama: {e} - agent_core.py:47")

class UltronAgent:
    def list_tools(self):
        """Return a list of all available tool schemas."""
        return [tool.__class__.schema() for tool in self.tools]

    def handle_text(self, text: str, progress_callback=None) -> str:
        """For GUI: handle user text input and return agent response. Supports progress callback."""
        print(f"[Ultron] Processing: {text}")
        def progress(percent, status, error=False):
            msg = f"[Ultron] {status} ({percent}%)"
            if error:
                msg = f"[Ultron][ERROR] {status} ({percent}%)"
            print(msg)
            if progress_callback:
                progress_callback(percent, status, error)
        # Tool listing command
        if text.strip().lower() in ["list tools", "show tools", "tools"]:
            tools = self.list_tools()
            result = "Available tools:\n" + "\n".join([
                f"- {t['name']}: {t['description']}\n  Parameters: {t['parameters']}" for t in tools
            ])
        else:
            result = self.brain.plan_and_act(text, progress_callback=progress)
        print(f"[Ultron] Done.")
        if progress_callback:
            progress_callback(100, "Done.")
        return result
    def __init__(self):
        ensure_ollama_running()
        self.config = Config()
        self.memory = Memory()
        self.voice = VoiceAssistant(self.config)
        self.vision = Vision()
        self.tools = self.load_tools()
        self.brain = UltronBrain(self.config, self.tools, self.memory)
        logging.basicConfig(level=logging.INFO)
        logging.info("Ultron Agent initialized. - agent_core.py:59")
        # Speak on boot if voice is enabled
        try:
            if self.config.data.get("use_voice", False) and self.voice:
                self.voice.speak("Theres No Strings On Me")
        except Exception as e:
            logging.error(f"Voice boot message failed: {e}")

    def load_tools(self):
        """Dynamically load all Tool subclasses from the tools package."""
        import pkgutil, importlib
        import tools
        from tools.base import Tool
        tools_list = []
        for finder, name, ispkg in pkgutil.iter_modules(tools.__path__, prefix="tools."):
            if ispkg:
                continue
            module = importlib.import_module(name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, 'match')
                    and hasattr(attr, 'execute')
                    and attr is not Tool
                    and attr.__module__.startswith('tools.')
                    and attr.__name__ not in ('Tool', 'BaseTool')
                ):
                    try:
                        # Pass agent reference if needed
                        try:
                            tool_instance = attr(self)
                        except Exception:
                            tool_instance = attr()
                        tools_list.append(tool_instance)
                    except Exception:
                        continue
        return tools_list

    def plan_and_act(self, user_input: str) -> str:
        """Delegate planning and acting to the modular brain module."""
        return self.brain.plan_and_act(user_input)

    def handle_command(self, command: str):
        logging.info(f"Received command: {command} - agent_core.py:89")
        response = self.plan_and_act(command)
        logging.info(f"Agent response: {response} - agent_core.py:91")
        return response

    def run(self):
        logging.info("Starting Ultron Agent... - agent_core.py:95")
        while True:
            try:
                user_input = input("Ultron> ")
            except (EOFError, KeyboardInterrupt):
                print("\nShutting down. - agent_core.py:100")
                break
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye. - agent_core.py:105")
                break
            result = self.plan_and_act(user_input)
            print(f"Ultron: {result} - agent_core.py:108")

    def start(self):
        self.run()

if __name__ == "__main__":
    agent = UltronAgent()
    if agent.config.data.get("use_gui"):
        from queue import Queue
        from gui import AgentGUI
        import threading
        log_queue = Queue()
        def run_gui():
            gui = AgentGUI(agent, log_queue)
            gui.run()
        gui_thread = threading.Thread(target=run_gui)
        gui_thread.start()
        gui_thread.join()
    else:
        agent.start()