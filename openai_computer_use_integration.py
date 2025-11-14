#!/usr/bin/env python3
"""OpenAI Computer Use Integration for ULTRON Agent"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from tools.openai_computer_use_tool import OpenAIComputerUseTool
from utils.ultron_logger import log_info, log_error, log_ai_decision

class UltronComputerUseManager:
    """Manages OpenAI Computer Use integration for ULTRON"""
    
    def __init__(self):
        self.computer_tool = OpenAIComputerUseTool()
        self.session_log = []
        self.enabled = True
        
    def process_computer_command(self, command: str) -> dict:
        """Process computer use command"""
        
        if not self.enabled:
            return {"status": "disabled", "message": "Computer use is disabled"}
        
        log_ai_decision("computer_use", f"Processing command: {command}", ai_model="gpt-4o")
        
        start_time = time.time()
        
        try:
            # Execute computer use command
            result = self.computer_tool.execute(command)
            
            execution_time = time.time() - start_time
            
            # Log session
            session_entry = {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "result": result,
                "execution_time": execution_time,
                "status": "success"
            }
            
            self.session_log.append(session_entry)
            
            log_info("computer_use", f"Command executed in {execution_time:.2f}s: {result}")
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            error_msg = str(e)
            log_error("computer_use", f"Command failed: {error_msg}")
            
            session_entry = {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "error": error_msg,
                "execution_time": time.time() - start_time,
                "status": "error"
            }
            
            self.session_log.append(session_entry)
            
            return {
                "status": "error",
                "error": error_msg
            }
    
    def get_session_summary(self) -> dict:
        """Get computer use session summary"""
        
        total_commands = len(self.session_log)
        successful_commands = len([entry for entry in self.session_log if entry["status"] == "success"])
        failed_commands = total_commands - successful_commands
        
        avg_execution_time = 0
        if total_commands > 0:
            total_time = sum(entry.get("execution_time", 0) for entry in self.session_log)
            avg_execution_time = total_time / total_commands
        
        return {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "failed_commands": failed_commands,
            "success_rate": successful_commands / total_commands if total_commands > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "session_start": self.session_log[0]["timestamp"] if self.session_log else None,
            "last_command": self.session_log[-1]["timestamp"] if self.session_log else None
        }
    
    def export_session_log(self, filepath: str = None) -> str:
        """Export session log to file"""
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/computer_use_session_{timestamp}.json"
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            export_data = {
                "session_summary": self.get_session_summary(),
                "session_log": self.session_log,
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            log_info("computer_use", f"Session log exported to {filepath}")
            return filepath
            
        except Exception as e:
            log_error("computer_use", f"Failed to export session log: {str(e)}")
            return None
    
    def clear_session_log(self):
        """Clear current session log"""
        self.session_log = []
        log_info("computer_use", "Session log cleared")
    
    def toggle_computer_use(self, enabled: bool = None) -> bool:
        """Toggle computer use on/off"""
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = not self.enabled
        
        log_info("computer_use", f"Computer use {'enabled' if self.enabled else 'disabled'}")
        return self.enabled

class UltronComputerUseAPI:
    """API interface for computer use"""
    
    def __init__(self):
        self.manager = UltronComputerUseManager()
    
    def handle_voice_command(self, voice_input: str) -> str:
        """Handle voice command for computer use"""
        
        # Convert voice to computer command
        computer_commands = {
            "click": ["click", "tap", "press"],
            "type": ["type", "write", "enter"],
            "scroll": ["scroll", "move"],
            "screenshot": ["screenshot", "capture", "picture"]
        }
        
        voice_lower = voice_input.lower()
        
        # Detect command type
        command_type = None
        for cmd_type, keywords in computer_commands.items():
            if any(keyword in voice_lower for keyword in keywords):
                command_type = cmd_type
                break
        
        if not command_type:
            return "Computer use command not recognized"
        
        # Process command
        result = self.manager.process_computer_command(voice_input)
        
        if result["status"] == "success":
            return f"Computer action completed: {result['result']}"
        else:
            return f"Computer action failed: {result.get('error', 'Unknown error')}"
    
    def get_status(self) -> dict:
        """Get computer use status"""
        return {
            "enabled": self.manager.enabled,
            "session_summary": self.manager.get_session_summary(),
            "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }

# Global instance
ultron_computer_use = UltronComputerUseAPI()

if __name__ == "__main__":
    print("=== ULTRON COMPUTER USE INTEGRATION ===")
    
    # Initialize
    api = UltronComputerUseAPI()
    
    # Test status
    status = api.get_status()
    print(f"Enabled: {status['enabled']}")
    print(f"API Key: {'✓' if status['api_key_configured'] else '✗'}")
    
    # Test voice command
    test_command = "take a screenshot of the screen"
    result = api.handle_voice_command(test_command)
    print(f"Voice test: {result}")
    
    # Get session summary
    summary = api.manager.get_session_summary()
    print(f"Session: {summary['total_commands']} commands")
    
    print("Computer Use integration ready")