"""
ULTRON Execution Engine - Direct Python execution with PyAutoGUI control
Gives local Ollama models full autonomous desktop control
"""
import asyncio
import io
import contextlib
import traceback
import re
from typing import Optional, Dict, Any
from utils.ultron_logger import log_info, log_error, log_ai_decision

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class UltronExecutor:
    """Autonomous code execution engine for local models"""
    
    def __init__(self, brain):
        self.brain = brain
        self.execution_history = []
        
        # Safe execution environment
        self.safe_env = {
            'pyautogui': pyautogui if PYAUTOGUI_AVAILABLE else None,
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
        }
    
    def execute_code(self, code: str) -> str:
        """Execute Python code with PyAutoGUI access"""
        if not PYAUTOGUI_AVAILABLE:
            return "PyAutoGUI not available"
        
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                exec(code, self.safe_env)
            result = buffer.getvalue() or "✅ Executed successfully"
            log_info("ultron_exec", f"Code executed: {code[:100]}")
            return result
        except Exception as e:
            error = traceback.format_exc()
            log_error("ultron_exec", f"Execution failed: {error}")
            return f"❌ Error:\n{error}"
    
    def extract_code(self, text: str) -> Optional[str]:
        """Extract code from <code>...</code> or ```python...``` blocks"""
        # Try <code> tags first
        if '<code>' in text and '</code>' in text:
            return text.split('<code>')[1].split('</code>')[0].strip()
        
        # Try markdown code blocks
        pattern = r'```(?:python)?\n(.*?)\n```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    async def chat_with_execution(self, prompt: str) -> Dict[str, Any]:
        """Chat with model and execute any code it generates"""
        
        # Enhanced system prompt with PyAutoGUI knowledge
        system_context = """You are ULTRON AI with full PyAutoGUI control.

AVAILABLE FUNCTIONS:
- pyautogui.moveTo(x, y, duration=0.5) - Move mouse
- pyautogui.click(x=None, y=None, clicks=1) - Click mouse
- pyautogui.doubleClick() - Double click
- pyautogui.rightClick() - Right click
- pyautogui.write('text', interval=0.1) - Type text
- pyautogui.press('key') - Press key (enter, space, etc)
- pyautogui.hotkey('ctrl', 'c') - Key combination
- pyautogui.screenshot('path.png') - Take screenshot
- pyautogui.locateOnScreen('image.png') - Find image
- pyautogui.scroll(amount) - Scroll (positive=up, negative=down)

SCREEN INFO:
- Screen size: pyautogui.size()
- Current position: pyautogui.position()

OUTPUT FORMAT:
When you want to execute code, wrap it in <code>...</code> tags.
Example: <code>pyautogui.moveTo(500, 500)</code>

Keep explanations brief. Show code for actions."""
        
        # Build full prompt
        full_prompt = f"{system_context}\n\nUser: {prompt}\n\nULTRON:"
        
        # Get model response
        log_ai_decision("ultron_exec", f"Processing: {prompt[:80]}", 
                       self.brain.config.get('llm_model', 'llama3.1'),
                       confidence_score=0.9)
        
        response = await self.brain.direct_chat(full_prompt)
        
        # Extract and execute code
        code = self.extract_code(response)
        execution_result = None
        
        if code:
            log_info("ultron_exec", f"Executing code block:\n{code}")
            execution_result = self.execute_code(code)
            
            # Store in history
            self.execution_history.append({
                'prompt': prompt,
                'code': code,
                'result': execution_result
            })
        
        return {
            'response': response,
            'code': code,
            'execution_result': execution_result,
            'has_code': code is not None
        }
    
    def get_history(self, limit: int = 10) -> list:
        """Get recent execution history"""
        return self.execution_history[-limit:]


async def main():
    """Interactive ULTRON execution shell"""
    print("=" * 60)
    print("ULTRON Execution Engine - Autonomous Desktop Control")
    print("=" * 60)
    print("\nInitializing...")
    
    # Initialize brain
    from config import UltronConfig
    from brain import UltronBrain
    
    config = UltronConfig()
    brain = UltronBrain(config, {}, None)
    executor = UltronExecutor(brain)
    
    if not PYAUTOGUI_AVAILABLE:
        print("❌ PyAutoGUI not available. Install: pip install pyautogui")
        return
    
    print(f"✅ Model: {config.get('llm_model', 'llama3.1')}")
    print(f"✅ PyAutoGUI: Available")
    print(f"✅ Screen size: {pyautogui.size()}")
    print("\nType commands. ULTRON will execute code autonomously.")
    print("Examples:")
    print("  - 'Move mouse to center and click'")
    print("  - 'Take a screenshot'")
    print("  - 'Type hello world'")
    print("\nType 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("\n🤖 You: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Shutting down ULTRON...")
                break
            
            if not user_input.strip():
                continue
            
            # Process with execution
            result = await executor.chat_with_execution(user_input)
            
            print(f"\n💬 ULTRON:\n{result['response']}")
            
            if result['has_code']:
                print(f"\n⚡ Execution Result:\n{result['execution_result']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            log_error("ultron_exec", f"Main loop error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
