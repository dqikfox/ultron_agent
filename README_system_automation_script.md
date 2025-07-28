# Add this to your README.md for the new system_automation_script.py

## System Automation Script with Ollama (qwen2.5)

This script allows you to interact with your system using natural language commands, powered by the Ollama LLM (qwen2.5). It supports diagnostics, file operations, and writing to the active window.

### Features
- Run system diagnostics (CPU, memory, disk, process count)
- Create, edit, delete, and list files in a dedicated directory
- Write text to the active window (simulate keystrokes)
- Use natural language commands interpreted by Ollama
- All actions are logged to `system_automation.log`

### Requirements
- Python 3.10+
- [Ollama Python package](https://pypi.org/project/ollama/) and Ollama server running with the `qwen2.5` model
- `psutil` and `keyboard` Python packages

### Usage
1. Ensure Ollama server is running and the `qwen2.5` model is available.
2. Install dependencies:
   ```
   pip install ollama psutil keyboard
   ```
3. Run the script:
   ```
   C:/Python310/python.exe system_automation_script.py
   ```
4. Enter commands such as:
   - `run diagnostics`
   - `create file with text ...`
   - `edit file myfile.txt ...`
   - `delete file myfile.txt`
   - `list files`
   - `write to console ...`
   - Or any other automation command

### Notes
- Files are managed in the `automated_files` directory.
- The script is Windows-focused (uses `keyboard` library).
- All actions are logged for auditing and debugging.

---
