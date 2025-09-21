"""
ULTRON Agent 3.0 - AI Model Awareness System
Coordinates file modifications between AI models to ensure system stability
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import threading
from .ultron_logger import log_info, log_error, log_ai_decision

# Thread-safe file tracking
_file_locks: Dict[str, threading.Lock] = {}
_global_lock = threading.Lock()

def get_file_lock(file_path: str) -> threading.Lock:
    """Get or create a lock for a specific file"""
    with _global_lock:
        if file_path not in _file_locks:
            _file_locks[file_path] = threading.Lock()
        return _file_locks[file_path]

def should_modify_file(file_path: str, modification_type: str, ai_model: str) -> Tuple[bool, str, Dict]:
    """
    Check if a file should be modified based on recent activity and system state
    
    Returns:
        (should_proceed, reason, context)
    """
    try:
        file_path = os.path.abspath(file_path)
        
        # Get file context
        context = check_file_context(file_path)
        
        # Check if file is currently being modified
        file_lock = get_file_lock(file_path)
        if not file_lock.acquire(blocking=False):
            return False, "File is currently being modified by another process", context
        
        try:
            # Check recent modifications (last 5 minutes)
            recent_changes = context.get("recent_changes", [])
            now = datetime.now()
            
            for change in recent_changes:
                change_time = datetime.fromisoformat(change.get("timestamp", ""))
                if now - change_time < timedelta(minutes=5):
                    if change.get("ai_model") != ai_model:
                        return False, f"File recently modified by {change.get('ai_model', 'unknown')}", context
            
            # Check for critical system files
            critical_files = [
                "agent_core.py", "brain.py", "main.py", "ultron_config.json",
                "requirements.txt", "run.bat"
            ]
            
            if any(critical in file_path for critical in critical_files):
                # Extra caution for critical files
                if len(recent_changes) > 0:
                    return False, "Critical system file has recent modifications", context
            
            # Check system stability
            error_logs = get_recent_errors()
            if len(error_logs) > 5:  # More than 5 errors in recent logs
                return False, "System instability detected - too many recent errors", context
            
            # Log the decision
            log_ai_decision(
                ai_model, 
                f"Approved modification of {file_path}",
                ai_model=ai_model,
                confidence_score=0.8
            )
            
            return True, "Modification approved", context
            
        finally:
            file_lock.release()
    
    except Exception as e:
        log_error("model_awareness", f"Error checking file modification permission: {e}")
        return False, f"Error during check: {str(e)}", {}

def check_file_context(file_path: str) -> Dict:
    """Get comprehensive context about a file"""
    try:
        file_path = os.path.abspath(file_path)
        context = {
            "file_path": file_path,
            "exists": os.path.exists(file_path),
            "recent_changes": [],
            "dependencies": [],
            "related_files": [],
            "last_modified": None,
            "size": 0
        }
        
        if context["exists"]:
            stat = os.stat(file_path)
            context["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            context["size"] = stat.st_size
        
        # Get recent changes from logs
        context["recent_changes"] = get_recent_file_changes(file_path)
        
        # Find related files (same directory, similar names)
        context["related_files"] = find_related_files(file_path)
        
        # Check for dependencies (imports, includes, etc.)
        context["dependencies"] = find_file_dependencies(file_path)
        
        return context
    
    except Exception as e:
        log_error("model_awareness", f"Error getting file context: {e}")
        return {"error": str(e)}

def get_recent_file_changes(file_path: str, hours: int = 24) -> List[Dict]:
    """Get recent changes to a specific file"""
    try:
        changes = []
        activities_file = Path("logs") / "file_changes.log"
        
        if not activities_file.exists():
            return changes
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with open(activities_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("file_path") == file_path:
                        entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if entry_time > cutoff_time:
                            changes.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return sorted(changes, key=lambda x: x.get("timestamp", ""))
    
    except Exception as e:
        log_error("model_awareness", f"Error getting recent file changes: {e}")
        return []

def find_related_files(file_path: str) -> List[str]:
    """Find files related to the given file"""
    try:
        related = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            return related
        
        # Files in same directory
        for sibling in file_path.parent.glob("*"):
            if sibling.is_file() and sibling != file_path:
                # Same base name or similar
                if (sibling.stem == file_path.stem or 
                    file_path.stem in sibling.stem or 
                    sibling.stem in file_path.stem):
                    related.append(str(sibling))
        
        return related[:10]  # Limit to 10 related files
    
    except Exception as e:
        log_error("model_awareness", f"Error finding related files: {e}")
        return []

def find_file_dependencies(file_path: str) -> List[str]:
    """Find dependencies of a file (imports, includes, etc.)"""
    try:
        dependencies = []
        
        if not os.path.exists(file_path):
            return dependencies
        
        # For Python files, find imports
        if file_path.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        dependencies.append(line)
                    if len(dependencies) > 20:  # Limit to prevent huge lists
                        break
        
        return dependencies
    
    except Exception as e:
        log_error("model_awareness", f"Error finding file dependencies: {e}")
        return []

def get_recent_errors(hours: int = 1) -> List[Dict]:
    """Get recent error logs"""
    try:
        errors = []
        activities_file = Path("logs") / "activities.jsonl"
        
        if not activities_file.exists():
            return errors
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with open(activities_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("level") == "ERROR":
                        entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if entry_time > cutoff_time:
                            errors.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return errors
    
    except Exception as e:
        log_error("model_awareness", f"Error getting recent errors: {e}")
        return []

def record_file_modification(file_path: str, ai_model: str, modification_type: str, success: bool = True):
    """Record a file modification for tracking"""
    try:
        file_path = os.path.abspath(file_path)
        
        modification_record = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "ai_model": ai_model,
            "modification_type": modification_type,
            "success": success
        }
        
        # Log to file changes
        changes_file = Path("logs") / "file_changes.log"
        changes_file.parent.mkdir(exist_ok=True)
        
        with open(changes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(modification_record) + "\n")
        
        # Also log as activity
        log_info(
            "model_awareness",
            f"File modification recorded: {file_path}",
            ai_model=ai_model,
            modification_type=modification_type,
            success=success
        )
    
    except Exception as e:
        log_error("model_awareness", f"Error recording file modification: {e}")

def get_system_stability_score() -> float:
    """Get a score (0-1) indicating system stability"""
    try:
        # Check recent errors
        recent_errors = get_recent_errors(hours=1)
        error_penalty = min(len(recent_errors) * 0.1, 0.5)
        
        # Check recent file modifications
        recent_mods = []
        changes_file = Path("logs") / "file_changes.log"
        if changes_file.exists():
            cutoff_time = datetime.now() - timedelta(hours=1)
            with open(changes_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if entry_time > cutoff_time:
                            recent_mods.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        # Penalty for too many modifications
        mod_penalty = min(len(recent_mods) * 0.05, 0.3)
        
        # Calculate stability score
        stability_score = max(0.0, 1.0 - error_penalty - mod_penalty)
        
        return stability_score
    
    except Exception as e:
        log_error("model_awareness", f"Error calculating stability score: {e}")
        return 0.5  # Default to moderate stability

def cleanup_old_tracking_data(days: int = 7):
    """Clean up old tracking data"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Clean file changes log
        changes_file = Path("logs") / "file_changes.log"
        if changes_file.exists():
            temp_file = changes_file.with_suffix('.tmp')
            
            with open(changes_file, "r", encoding="utf-8") as infile, \
                 open(temp_file, "w", encoding="utf-8") as outfile:
                
                for line in infile:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if entry_time > cutoff_time:
                            outfile.write(line)
                    except json.JSONDecodeError:
                        continue
            
            temp_file.replace(changes_file)
            log_info("model_awareness", f"Cleaned up tracking data older than {days} days")
    
    except Exception as e:
        log_error("model_awareness", f"Error cleaning up tracking data: {e}")

# Initialize tracking on import
def initialize_model_awareness():
    """Initialize the model awareness system"""
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Log initialization
        log_info("model_awareness", "Model awareness system initialized")
        
        # Clean up old data
        cleanup_old_tracking_data()
        
    except Exception as e:
        log_error("model_awareness", f"Error initializing model awareness: {e}")

# Initialize on import
initialize_model_awareness()