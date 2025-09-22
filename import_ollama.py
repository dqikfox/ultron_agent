import ollama
import pyautogui
import speech_recognition as sr
import pyttsx3
import subprocess
import psutil
import platform
import webbrowser
import time
import threading
import json
import os
from datetime import datetime

class AIAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.system_info = self.get_system_info()
        self.conversation_history = []

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def get_system_info(self):
        """Gather system information"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "ram": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
        }

    def speak(self, text):
        """Convert text to speech"""
        print(f"AI: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for voice input"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                query = self.recognizer.recognize_google(audio)
                print(f"You: {query}")
                return query.lower()
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Sorry, speech service is unavailable."

    def get_diagnostics(self):
        """Perform system diagnostics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        diagnostics = {
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "memory_available": f"{round(memory.available / (1024**3), 2)} GB",
            "disk_usage": f"{disk.percent}%",
            "disk_free": f"{round(disk.free / (1024**3), 2)} GB"
        }

        return diagnostics

    def execute_command(self, command):
        """Execute system commands"""
        try:
            if command.startswith("open "):
                app = command[5:].strip()
                if app in ["notepad", "calculator", "paint"]:
                    subprocess.run(app, shell=True)
                else:
                    webbrowser.open(app)
                return f"Opening {app}"

            elif command.startswith("type "):
                text = command[5:]
                pyautogui.typewrite(text, interval=0.05)
                return f"Typed: {text}"

            elif command == "take screenshot":
                screenshot = pyautogui.screenshot()
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(filename)
                return f"Screenshot saved as {filename}"

            elif command.startswith("move mouse to "):
                coords = command[14:].split(",")
                x, y = int(coords[0]), int(coords[1])
                pyautogui.moveTo(x, y)
                return f"Moved mouse to ({x}, {y})"

            elif command == "click":
                pyautogui.click()
                return "Clicked"

            elif command == "right click":
                pyautogui.rightClick()
                return "Right clicked"

            elif command.startswith("press "):
                key = command[6:]
                pyautogui.press(key)
                return f"Pressed {key}"

            elif command == "diagnostics":
                diag = self.get_diagnostics()
                return json.dumps(diag, indent=2)

            else:
                return "Command not recognized"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def chat_with_ai(self, user_input):
        """Interact with Ollama model"""
        # Add system context to the conversation
        context = f"""
        System Information: {json.dumps(self.system_info)}
        Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Available Commands:
        - diagnostics: Get system diagnostics
        - open [app/website]: Open application or website
        - type [text]: Type text at cursor position
        - take screenshot: Capture screen
        - move mouse to [x,y]: Move mouse to coordinates
        - click: Left click at current position
        - right click: Right click at current position
        - press [key]: Press a keyboard key
        """

        # Prepare conversation history
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful AI assistant with system control capabilities. {context}"
            }
        ] + self.conversation_history + [
            {
                "role": "user",
                "content": user_input
            }
        ]

        try:
            response = ollama.chat(model='qwen3-coder:480b-cloud', messages=messages)
            ai_response = response['message']['content']

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            # Keep history to last 10 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return ai_response
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"

    def process_request(self, user_input):
        """Process user request and determine action"""
        if any(keyword in user_input for keyword in ["diagnostics", "system status", "performance"]):
            diag_info = self.get_diagnostics()
            response = f"System Diagnostics:\n"
            for key, value in diag_info.items():
                response += f"- {key.replace('_', ' ').title()}: {value}\n"
            return response

        elif user_input.startswith(("open", "type", "take screenshot", "move mouse", "click", "press")):
            return self.execute_command(user_input)

        else:
            # Send to AI for processing
            return self.chat_with_ai(user_input)

    def run(self):
        """Main assistant loop"""
        self.speak("AI Assistant initialized. How can I help you today?")

        while True:
            try:
                user_input = self.listen()

                if "exit" in user_input or "quit" in user_input:
                    self.speak("Goodbye!")
                    break

                if user_input:
                    response = self.process_request(user_input)
                    self.speak(response)

            except KeyboardInterrupt:
                self.speak("Assistant shutting down.")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("An error occurred. Please try again.")

if __name__ == "__main__":
    # Verify Ollama is running
    try:
        ollama.list()
    except Exception as e:
        print("Error connecting to Ollama. Make sure it's running.")
        exit(1)

    assistant = AIAssistant()
    assistant.run()
