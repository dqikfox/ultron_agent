"""
Comprehensive Action Logger for Ultron Agent 2
Logs all system actions, user inputs, responses, and system status changes.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
import threading
from typing import Dict, Any, Optional

class ActionLogger:
    def __init__(self, log_file: str = "ultron_actions.log", config_file: str = "ultron_config.json"):
        self.log_file = Path(log_file)
        self.config_file = Path(config_file)
        self.lock = threading.Lock()
        
        # Setup comprehensive logging
        self.setup_logging()
        
        # Load configuration for context
        self.config = self.load_config()
        
        # Initialize session
        self.log_action("SYSTEM_START", f"Ultron Agent 2 session started - Session ID: {self.session_id}")
    
    def setup_logging(self):
        """Setup detailed logging configuration"""
        # Initialize session ID first
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create separate detailed action log
        self.action_log_file = self.log_file.parent / f"actions_{self.session_id}.json"
        self.actions = []
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration for context"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
        return {}
    
    def log_action(self, action_type: str, description: str, details: Optional[Dict[str, Any]] = None):
        """Log an action with timestamp and details"""
        with self.lock:
            timestamp = datetime.now().isoformat()
            
            action_entry = {
                "timestamp": timestamp,
                "session_id": self.session_id,
                "action_type": action_type,
                "description": description,
                "details": details or {}
            }
            
            # Add to memory
            self.actions.append(action_entry)
            
            # Log to file immediately
            self.logger.info(f"[{action_type}] {description}")
            
            # Save detailed JSON log
            self.save_action_log()
    
    def log_user_input(self, input_text: str, input_method: str = "text"):
        """Log user input"""
        self.log_action(
            "USER_INPUT",
            f"User input via {input_method}: {input_text[:100]}{'...' if len(input_text) > 100 else ''}",
            {
                "input_method": input_method,
                "full_text": input_text,
                "text_length": len(input_text)
            }
        )
    
    def log_ai_response(self, response: str, model: str = "unknown", processing_time: float = 0):
        """Log AI response"""
        self.log_action(
            "AI_RESPONSE", 
            f"AI response from {model}: {response[:100]}{'...' if len(response) > 100 else ''}",
            {
                "model": model,
                "full_response": response,
                "response_length": len(response),
                "processing_time_seconds": processing_time
            }
        )
    
    def log_voice_activity(self, activity: str, success: bool = True, details: Optional[Dict] = None):
        """Log voice-related activities"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(
            "VOICE_ACTIVITY",
            f"Voice {activity}: {status}",
            details or {}
        )
    
    def log_system_status(self, component: str, status: str, metrics: Optional[Dict] = None):
        """Log system status changes"""
        self.log_action(
            "SYSTEM_STATUS",
            f"{component} status: {status}",
            {
                "component": component,
                "status": status,
                "metrics": metrics or {}
            }
        )
    
    def log_error(self, error_type: str, error_message: str, traceback_info: str = ""):
        """Log errors with details"""
        self.log_action(
            "ERROR",
            f"{error_type}: {error_message}",
            {
                "error_type": error_type,
                "error_message": error_message,
                "traceback": traceback_info
            }
        )
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True):
        """Log file operations"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(
            "FILE_OPERATION",
            f"File {operation}: {file_path} - {status}",
            {
                "operation": operation,
                "file_path": file_path,
                "success": success
            }
        )
    
    def log_network_activity(self, activity: str, url: str = "", response_code: int = 0):
        """Log network activities"""
        self.log_action(
            "NETWORK_ACTIVITY",
            f"Network {activity}: {url}",
            {
                "activity": activity,
                "url": url,
                "response_code": response_code
            }
        )
    
    def log_gui_event(self, event: str, component: str, details: Optional[Dict] = None):
        """Log GUI events"""
        self.log_action(
            "GUI_EVENT",
            f"GUI {event} in {component}",
            {
                "event": event,
                "component": component,
                "details": details or {}
            }
        )
    
    def log_voice_action(self, action: str, message: str, engine: str = "unknown"):
        """Log voice/TTS actions"""
        self.log_action(
            "VOICE_ACTION",
            f"Voice {action}: {message[:100]}{'...' if len(message) > 100 else ''}",
            {
                "voice_action": action,
                "engine": engine,
                "full_message": message,
                "message_length": len(message)
            }
        )
    
    def log_accessibility_action(self, disability_type: str, action: str, context: str = ""):
        """Log accessibility-specific actions"""
        self.log_action(
            "ACCESSIBILITY",
            f"Accessibility support for {disability_type}: {action[:100]}{'...' if len(action) > 100 else ''}",
            {
                "disability_type": disability_type,
                "action": action,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_automation_action(self, tool_name: str, description: str, details: Optional[Dict[str, Any]] = None):
        """Log automation actions"""
        self.log_action(
            "AUTOMATION",
            f"{tool_name}: {description}",
            {
                "tool": tool_name,
                "details": details or {},
                "automation_type": "user_requested"
            }
        )
    
    def save_action_log(self):
        """Save actions to JSON file"""
        try:
            with open(self.action_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.actions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save action log: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        action_counts = {}
        for action in self.actions:
            action_type = action["action_type"]
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "total_actions": len(self.actions),
            "action_counts": action_counts,
            "session_start": self.actions[0]["timestamp"] if self.actions else None,
            "session_duration": len(self.actions)
        }
    
    def shutdown(self):
        """Shutdown logger and save final state"""
        self.log_action("SYSTEM_SHUTDOWN", "Ultron Agent 2 session ended")
        self.save_action_log()
        
        # Save session summary
        summary = self.get_session_summary()
        summary_file = self.log_file.parent / f"session_summary_{self.session_id}.json"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save session summary: {e}")

# Global logger instance
_action_logger = None

def get_action_logger() -> ActionLogger:
    """Get global action logger instance"""
    global _action_logger
    if _action_logger is None:
        _action_logger = ActionLogger()
    return _action_logger

def init_action_logger(log_file: str = "ultron_actions.log") -> ActionLogger:
    """Initialize action logger"""
    global _action_logger
    _action_logger = ActionLogger(log_file)
    return _action_logger
