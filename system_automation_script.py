import ollama
import psutil
import os
import logging
import keyboard
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='system_automation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Directory for file operations
WORKING_DIR = "automated_files"
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)
    logging.info(f"Created working directory: {WORKING_DIR} - system_automation_script.py:20")

def run_diagnostics():
    """Run system diagnostics and return results."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        processes = [p.info for p in psutil.process_iter(['name', 'pid'])]
        
        diagnostic_report = (
            f"CPU Usage: {cpu_usage}%\n"
            f"Memory Usage: {memory.percent}% ({memory.used / 1024**3:.2f}/{memory.total / 1024**3:.2f} GB)\n"
            f"Disk Usage: {disk.percent}% ({disk.used / 1024**3:.2f}/{disk.total / 1024**3:.2f} GB)\n"
            f"Running Processes: {len(processes)}\n"
        )
        logging.info("Diagnostics run successfully - system_automation_script.py:36")
        return diagnostic_report
    except Exception as e:
        logging.error(f"Diagnostics error: {str(e)} - system_automation_script.py:39")
        return f"Error running diagnostics: {str(e)}"

def create_file(filename, content, extension=".txt"):
    """Create a file with the specified content and extension."""
    try:
        filepath = os.path.join(WORKING_DIR, f"{filename}{extension}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Created file: {filepath} - system_automation_script.py:48")
        return f"File created: {filepath}"
    except Exception as e:
        logging.error(f"File creation error for {filename}{extension}: {str(e)} - system_automation_script.py:51")
        return f"Error creating file: {str(e)}"

def edit_file(filename, content, extension=".txt"):
    """Edit an existing file with new content."""
    try:
        filepath = os.path.join(WORKING_DIR, f"{filename}{extension}")
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}")
        logging.info(f"Edited file: {filepath} - system_automation_script.py:62")
        return f"File edited: {filepath}"
    except Exception as e:
        logging.error(f"File edit error for {filename}{extension}: {str(e)} - system_automation_script.py:65")
        return f"Error editing file: {str(e)}"

def delete_file(filename, extension=".txt"):
    """Delete a file."""
    try:
        filepath = os.path.join(WORKING_DIR, f"{filename}{extension}")
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        os.remove(filepath)
        logging.info(f"Deleted file: {filepath} - system_automation_script.py:75")
        return f"File deleted: {filepath}"
    except Exception as e:
        logging.error(f"File deletion error for {filename}{extension}: {str(e)} - system_automation_script.py:78")
        return f"Error deleting file: {str(e)}"

def list_files():
    """List all files in the working directory."""
    try:
        files = os.listdir(WORKING_DIR)
        if not files:
            return "No files found in working directory."
        logging.info("Listed files in working directory - system_automation_script.py:87")
        return "\n".join(files)
    except Exception as e:
        logging.error(f"File listing error: {str(e)} - system_automation_script.py:90")
        return f"Error listing files: {str(e)}"

def write_to_active_window(text):
    """Write text to the active window by simulating keystrokes."""
    try:
        time.sleep(1)  # Give user time to focus the target window
        keyboard.write(text)
        keyboard.press_and_release('enter')
        logging.info(f"Wrote to active window: {text[:50]}... - system_automation_script.py:99")
        return "Text written to active window"
    except Exception as e:
        logging.error(f"Error writing to active window: {str(e)} - system_automation_script.py:102")
        return f"Error writing to active window: {str(e)}"

def process_ollama_command(command):
    """Process a natural language command using the Ollama qwen2.5 model."""
    try:
        # Always instruct the model to reply in English
        english_command = "Please reply in English. " + command
        # Send command to Ollama model
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': english_command}]
        )
        ollama_response = response['message']['content']
        logging.info(f"Ollama processed command: {command} - system_automation_script.py:116")
        
        # Parse the response to determine the action
        command_lower = command.lower()
        
        if "diagnostics" in command_lower or "system info" in command_lower:
            return run_diagnostics()
        
        elif "create file" in command_lower:
            # Extract filename and content from command or Ollama response
            filename = f"file_{int(datetime.now().timestamp())}"
            extension = ".txt" if "text" in command_lower else ".py"
            return create_file(filename, ollama_response, extension)
        
        elif "edit file" in command_lower:
            filename = command_lower.split("edit file")[-1].strip().split()[0]
            extension = ".txt" if filename.endswith(".txt") else ".py"
            return edit_file(filename.replace(extension, ""), ollama_response, extension)
        
        elif "delete file" in command_lower:
            filename = command_lower.split("delete file")[-1].strip().split()[0]
            extension = ".txt" if filename.endswith(".txt") else ".py"
            return delete_file(filename.replace(extension, ""), extension)
        
        elif "list files" in command_lower:
            return list_files()
        
        elif "write to console" in command_lower or "write to powershell" in command_lower:
            return write_to_active_window(ollama_response)
        
        else:
            # General automation: return the Ollama-generated response or code
            if "python" in command_lower and "script" in command_lower:
                filename = f"script_{int(datetime.now().timestamp())}.py"
                return create_file(filename, ollama_response, ".py")
            return ollama_response
    
    except Exception as e:
        logging.error(f"Ollama command error: {str(e)} - system_automation_script.py:154")
        return f"Error processing command: {str(e)}"

def main():
    """Main function to handle user input and process commands."""
    print("System Automation Script with Ollama (qwen2.5) - system_automation_script.py:159")
    print("Type 'exit' to quit. Enter commands to interact with the system. - system_automation_script.py:160")
    
    while True:
        command = input("> ")
        if command.lower() == 'exit':
            print("Exiting... - system_automation_script.py:165")
            logging.info("Script terminated by user - system_automation_script.py:166")
            break
        
        result = process_ollama_command(command)
        print(result)

if __name__ == "__main__":
    main()
