#!/usr/bin/env python3
"""
ULTRON AI Assistant - Voice-Enabled System Controller
A comprehensive AI assistant with voice interaction, file system access, and command execution.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import core components
try:
    from config import Config
    from utils.ultron_logger import log_info, log_error, log_ai_decision
    from utils.event_system import EventSystem
    from security_utils import sanitize_log_input
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")

    # Fallback logging
    logging.basicConfig(level=logging.INFO)
    def log_info(component, msg, **kwargs):
        logging.info(f"[{component}] {msg}")
    def log_error(component, msg, **kwargs):
        logging.error(f"[{component}] {msg}")
    def log_ai_decision(component, msg, **kwargs):
        logging.info(f"[{component}] AI: {msg}")
    def sanitize_log_input(text):
        return str(text)[:1000]


class VoiceAssistant:
    """Voice interaction handler"""

    def __init__(self):
        self.enabled = False
        self.setup_voice()

    def setup_voice(self):
        """Initialize voice capabilities"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.enabled = True
            log_info("voice", "Voice recognition initialized")
        except Exception as e:
            log_error("voice", f"Voice setup failed: {e}")
            self.enabled = False

    async def listen(self) -> Optional[str]:
        """Listen for voice input"""
        if not self.enabled:
            return None

        try:
            import speech_recognition as sr
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                log_info("voice", "Listening...")
                audio = self.recognizer.listen(source, timeout=5)

            text = self.recognizer.recognize_google(audio)
            log_info("voice", f"Heard: {text}")
            return text
        except Exception as e:
            log_error("voice", f"Listen error: {e}")
            return None

    async def speak(self, text: str):
        """Speak text using TTS"""
        try:
            # Try pyttsx3 first (offline)
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            log_info("voice", f"Spoke: {text[:50]}...")
        except Exception as e:
            log_error("voice", f"TTS error: {e}")
            print(f"[ULTRON]: {text}")  # Fallback to text


class FileSystemManager:
    """Handle file system operations safely"""

    def __init__(self):
        self.home_dir = Path.home()
        self.allowed_dirs = [
            self.home_dir / "Documents",
            self.home_dir / "Downloads",
            self.home_dir / "projects",
            Path.cwd()
        ]

    def is_safe_path(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        try:
            resolved = path.resolve()
            return any(resolved.is_relative_to(allowed) for allowed in self.allowed_dirs)
        except:
            return False

    async def read_file(self, file_path: str) -> str:
        """Read file contents safely"""
        try:
            path = Path(file_path).expanduser()

            if not self.is_safe_path(path):
                return f"❌ Access denied: Path outside allowed directories"

            if not path.exists():
                return f"❌ File not found: {file_path}"

            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                return f"❌ File too large (max 10MB)"

            content = path.read_text()
            log_ai_decision("filesystem", f"Read file: {file_path}",
                          ai_model="filesystem", confidence_score=1.0)
            return f"📄 {file_path}:\n{content[:5000]}"  # Limit output
        except Exception as e:
            log_error("filesystem", f"Read error: {e}")
            return f"❌ Error reading file: {e}"

    async def write_file(self, file_path: str, content: str) -> str:
        """Write to file safely"""
        try:
            path = Path(file_path).expanduser()

            if not self.is_safe_path(path):
                return f"❌ Access denied: Path outside allowed directories"

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            log_ai_decision("filesystem", f"Wrote file: {file_path}",
                          ai_model="filesystem", confidence_score=1.0)
            return f"✅ File written: {file_path}"
        except Exception as e:
            log_error("filesystem", f"Write error: {e}")
            return f"❌ Error writing file: {e}"

    async def list_directory(self, dir_path: str) -> str:
        """List directory contents"""
        try:
            path = Path(dir_path).expanduser()

            if not self.is_safe_path(path):
                return f"❌ Access denied: Path outside allowed directories"

            if not path.is_dir():
                return f"❌ Not a directory: {dir_path}"

            items = []
            for item in sorted(path.iterdir()):
                icon = "📁" if item.is_dir() else "📄"
                items.append(f"{icon} {item.name}")

            return f"📂 {dir_path}:\n" + "\n".join(items[:50])  # Limit to 50 items
        except Exception as e:
            log_error("filesystem", f"List error: {e}")
            return f"❌ Error listing directory: {e}"


class CommandExecutor:
    """Execute system commands safely"""

    def __init__(self):
        self.safe_commands = {
            "ls", "pwd", "whoami", "date", "uptime", "df", "free",
            "ps", "top", "cat", "echo", "mkdir", "touch", "rm",
            "cp", "mv", "grep", "find", "which", "python3", "pip",
            "git", "curl", "wget", "apt", "systemctl", "journalctl"
        }

        self.dangerous_patterns = [
            "rm -rf /", "dd if=", "mkfs", "fdisk", "parted",
            "> /dev/", "chmod 777", "chown root"
        ]

    def is_safe_command(self, command: str) -> tuple[bool, str]:
        """Check if command is safe to execute"""
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in command:
                return False, f"Dangerous pattern detected: {pattern}"

        # Get first word (command name)
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False, "Empty command"

        cmd_name = cmd_parts[0]

        # Allow safe commands
        if cmd_name in self.safe_commands:
            return True, "OK"

        # Require confirmation for unknown commands
        return False, f"Unknown command: {cmd_name}"

    async def execute(self, command: str, auto_approve: bool = False) -> str:
        """Execute command with safety checks"""
        try:
            is_safe, msg = self.is_safe_command(command)

            if not is_safe and not auto_approve:
                return f"⚠️ Safety check: {msg}\nUse auto_approve=True to override"

            log_ai_decision("command", f"Executing: {command}",
                          ai_model="command_executor", confidence_score=0.9)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout if result.returncode == 0 else result.stderr
            status = "✅" if result.returncode == 0 else "❌"

            return f"{status} Command: {command}\n{output[:2000]}"  # Limit output
        except subprocess.TimeoutExpired:
            return f"⏱️ Command timed out after 30 seconds"
        except Exception as e:
            log_error("command", f"Execution error: {e}")
            return f"❌ Error: {e}"


class AIBrain:
    """AI reasoning and decision making"""

    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model = "llava:7b"
        self.context = []

    async def think(self, prompt: str, context: str = "") -> str:
        """Process user input and generate response"""
        try:
            import requests

            full_prompt = f"""You are ULTRON, an advanced AI assistant with system access.

Context: {context}

User: {prompt}

Respond concisely and helpfully. You can:
- Read and write files
- Execute terminal commands
- List directories
- Answer questions

Response:"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                log_ai_decision("brain", f"Generated response ({len(answer)} chars)",
                              ai_model=self.model, confidence_score=0.95)
                return answer
            else:
                return "I'm having trouble thinking right now. Ollama may not be running."

        except Exception as e:
            log_error("brain", f"Think error: {e}")
            return f"Error: {e}"


class ULTRONAssistant:
    """Main AI Assistant orchestrator"""

    def __init__(self):
        self.voice = VoiceAssistant()
        self.filesystem = FileSystemManager()
        self.commander = CommandExecutor()
        self.brain = AIBrain()
        self.event_system = EventSystem()

        log_info("ultron", "ULTRON Assistant initialized")

    async def process_command(self, user_input: str) -> str:
        """Process user command and route to appropriate handler"""
        user_input = user_input.strip().lower()

        # File operations
        if "read" in user_input and "file" in user_input:
            # Extract file path (simple extraction)
            parts = user_input.split()
            if len(parts) > 2:
                file_path = parts[-1]
                return await self.filesystem.read_file(file_path)

        elif "write" in user_input and "file" in user_input:
            # Would need more complex parsing for real implementation
            return "To write a file, use: write_file <path> <content>"

        elif "list" in user_input and ("directory" in user_input or "folder" in user_input):
            parts = user_input.split()
            dir_path = parts[-1] if len(parts) > 1 else "."
            return await self.filesystem.list_directory(dir_path)

        # Command execution
        elif user_input.startswith("run ") or user_input.startswith("execute "):
            command = user_input.replace("run ", "").replace("execute ", "")
            return await self.commander.execute(command)

        # General conversation - use AI
        else:
            return await self.brain.think(user_input)

    async def voice_loop(self):
        """Main voice interaction loop"""
        await self.voice.speak("ULTRON AI Assistant activated. How can I help you?")

        while True:
            try:
                # Listen for input
                user_input = await self.voice.listen()

                if not user_input:
                    continue

                # Check for exit command
                if any(word in user_input.lower() for word in ["exit", "quit", "goodbye"]):
                    await self.voice.speak("Goodbye!")
                    break

                # Process command
                response = await self.process_command(user_input)

                # Respond
                await self.voice.speak(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                log_error("ultron", f"Loop error: {e}")
                await self.voice.speak("I encountered an error")

    async def text_loop(self):
        """Main text interaction loop"""
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║      ULTRON AI Assistant - Text Mode             ║")
        print("╚══════════════════════════════════════════════════════╝\n")
        print("Commands:")
        print("  - Chat naturally for general questions")
        print("  - 'read file <path>' - Read a file")
        print("  - 'list directory <path>' - List directory")
        print("  - 'run <command>' - Execute terminal command")
        print("  - 'quit' - Exit\n")

        while True:
            try:
                user_input = input("\n🤖 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "goodbye"]:
                    print("👋 Goodbye!")
                    break

                # Process command
                response = await self.process_command(user_input)
                print(f"\n🔵 ULTRON: {response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                log_error("ultron", f"Loop error: {e}")
                print(f"\n❌ Error: {e}")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON AI Assistant")
    parser.add_argument("--voice", action="store_true", help="Enable voice mode")
    parser.add_argument("--text", action="store_true", help="Text mode (default)")
    args = parser.parse_args()

    assistant = ULTRONAssistant()

    if args.voice:
        await assistant.voice_loop()
    else:
        await assistant.text_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
