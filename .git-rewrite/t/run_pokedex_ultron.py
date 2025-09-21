#!/usr/bin/env python3
"""
ULTRON Pokedex GUI Integration
Connects the Pokedex-style GUI with full ULTRON Agent functionality
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import ULTRON components
    from agent_core import UltronAgent
    from config import Config
    from pokedex_ultron_gui import PokedexUltronGUI
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ultron_pokedex.log'),
            logging.StreamHandler()
        ]
    )
    
    def main():
        """Main function to launch ULTRON with Pokedex GUI"""
        try:
            print("🚀 Initializing ULTRON Agent 3.0 with Pokedex Interface... - run_pokedex_ultron.py:34")
            
            # Initialize configuration
            config = Config()
            
            # Initialize ULTRON Agent
            agent = UltronAgent(config)
            
            # Initialize and run Pokedex GUI
            gui = PokedexUltronGUI(agent)
            
            print("✅ ULTRON Pokedex Interface ready! - run_pokedex_ultron.py:45")
            print("🎮 GUI launched  ready for commands - run_pokedex_ultron.py:46")
            
            gui.run()
            
        except ImportError as e:
            print(f"❌ Import Error: {e} - run_pokedex_ultron.py:51")
            print("🔧 Falling back to demo mode... - run_pokedex_ultron.py:52")
            
            # Fallback to demo mode
            from pokedex_ultron_gui import PokedexUltronGUI
            
            class DemoAgent:
                def __init__(self):
                    self.config = DemoConfig()
                
                def handle_text(self, text):
                    return f"DEMO MODE: Received '{text}' - Full ULTRON integration requires agent_core.py"
                
                def list_tools(self):
                    return [
                        {'name': 'screenshot', 'description': 'Take a screenshot (demo)'},
                        {'name': 'system_info', 'description': 'System information (demo)'},
                        {'name': 'file_browser', 'description': 'File operations (demo)'},
                        {'name': 'web_search', 'description': 'Web search (demo)'},
                        {'name': 'voice_control', 'description': 'Voice commands (demo)'}
                    ]
            
            class DemoConfig:
                def __init__(self):
                    self.data = {
                        'llm_model': 'qwen2.5:latest',
                        'voice_engine': 'pyttsx3',
                        'use_voice': True,
                        'use_vision': True,
                        'ollama_models': ['qwen2.5:latest', 'llama3.2:latest', 'hermes3:latest']
                    }
                
                def get(self, key, default=None):
                    return self.data.get(key, default)
                
                def set(self, key, value):
                    self.data[key] = value
                    print(f"Demo: Setting {key} = {value} - run_pokedex_ultron.py:88")
                
                def save_config(self):
                    print("Demo: Configuration saved (simulated) - run_pokedex_ultron.py:91")
            
            gui = PokedexUltronGUI(DemoAgent())
            gui.run()
            
        except Exception as e:
            print(f"❌ Error starting ULTRON: {e} - run_pokedex_ultron.py:97")
            logging.error(f"Startup error: {e} - run_pokedex_ultron.py:98", exc_info=True)
            return 1
        
        return 0

    if __name__ == "__main__":
        exit_code = main()
        sys.exit(exit_code)

except ImportError as e:
    print(f"❌ Critical Import Error: {e} - run_pokedex_ultron.py:108")
    print("🔧 Please ensure all ULTRON dependencies are installed - run_pokedex_ultron.py:109")
    sys.exit(1)
