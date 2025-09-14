"""
AI MODEL AWARENESS SYSTEM for ULTRON Agent 3.0
All AI models must check this before file modifications to ensure system stability
and coordinate concurrent changes.

Following copilot instructions architecture patterns.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import os
import hashlib
from dataclasses import dataclass, asdict
from utils.ultron_logger import log_info, log_error, log_ai_decision


@dataclass
class FileModification:
    """Record of a file modification."""
    file_path: str
    timestamp: str
    ai_model: str
    action: str
    component: str
    reason: str
    hash_before: Optional[str] = None
    hash_after: Optional[str] = None


@dataclass
class FileContext:
    """Context information about a file."""
    file_path: str
    recent_changes: List[FileModification]
    dependencies: List[str]
    related_files: List[str]
    last_modified: str
    stability_score: float
    concurrent_changes: List[FileModification]


class ModelAwareness:
    """AI Model Awareness System for coordinating file modifications."""
    
    def __init__(self):
        self.data_dir = Path("logs")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.modifications_file = self.data_dir / "file_modifications.json"
        self.system_status_file = self.data_dir / "system_status.json"
        
        # File modification tracking
        self.recent_modifications = self._load_modifications()
        self.system_status = self._load_system_status()
        
        # Critical files that require extra caution
        self.critical_files = {
            "agent_core.py", "brain.py", "config.py", "voice_manager.py", 
            "ollama_manager.py", "utils/ultron_logger.py", "utils/model_awareness.py"
        }
        
        # Dependencies mapping
        self.file_dependencies = {
            "agent_core.py": ["brain.py", "config.py", "voice_manager.py", "utils/ultron_logger.py"],
            "brain.py": ["config.py", "ollama_manager.py", "utils/ultron_logger.py"],
            "gui/ultron_enhanced/web/index.html": ["voice_manager.py", "agent_core.py"],
            "config.py": ["ultron_config.json"],
            "voice_manager.py": ["config.py"]
        }
    
    def _load_modifications(self) -> List[FileModification]:
        """Load recent file modifications from storage."""
        if not self.modifications_file.exists():
            return []
        
        try:
            with open(self.modifications_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [FileModification(**mod) for mod in data]
        except Exception as e:
            log_error("model_awareness", f"Failed to load modifications: {e}")
            return []
    
    def _save_modifications(self):
        """Save file modifications to storage."""
        try:
            # Keep only last 7 days of modifications
            cutoff = datetime.now() - timedelta(days=7)
            recent_mods = [
                mod for mod in self.recent_modifications
                if datetime.fromisoformat(mod.timestamp) > cutoff
            ]
            self.recent_modifications = recent_mods
            
            with open(self.modifications_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(mod) for mod in recent_mods], f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error("model_awareness", f"Failed to save modifications: {e}")
    
    def _load_system_status(self) -> Dict:
        """Load system status information."""
        if not self.system_status_file.exists():
            return {
                "last_error": None,
                "stability_score": 1.0,
                "active_sessions": [],
                "locked_files": []
            }
        
        try:
            with open(self.system_status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_error("model_awareness", f"Failed to load system status: {e}")
            return {"last_error": str(e), "stability_score": 0.5, "active_sessions": [], "locked_files": []}
    
    def _save_system_status(self):
        """Save system status to storage."""
        try:
            with open(self.system_status_file, 'w', encoding='utf-8') as f:
                json.dump(self.system_status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error("model_awareness", f"Failed to save system status: {e}")
    
    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """Get MD5 hash of file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    def _calculate_stability_score(self, file_path: str) -> float:
        """Calculate stability score for a file based on recent changes."""
        recent_changes = self._get_recent_changes(file_path, hours=24)
        
        # Base stability score
        score = 1.0
        
        # Reduce score based on recent changes
        score -= len(recent_changes) * 0.1
        
        # Critical files have lower base score
        if any(critical in file_path for critical in self.critical_files):
            score -= 0.2
        
        # Recent errors reduce score
        if self.system_status.get("last_error"):
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _get_recent_changes(self, file_path: str, hours: int = 24) -> List[FileModification]:
        """Get recent changes for a specific file."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            mod for mod in self.recent_modifications
            if mod.file_path == file_path and datetime.fromisoformat(mod.timestamp) > cutoff
        ]
    
    def _get_concurrent_changes(self, file_path: str, minutes: int = 10) -> List[FileModification]:
        """Get concurrent changes that might conflict."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        # Get changes to this file or its dependencies
        dependencies = self.file_dependencies.get(file_path, [])
        related_files = [file_path] + dependencies
        
        return [
            mod for mod in self.recent_modifications
            if mod.file_path in related_files and datetime.fromisoformat(mod.timestamp) > cutoff
        ]
    
    def should_modify_file(self, file_path: str, modification_type: str, 
                          ai_model: str) -> Tuple[bool, str, FileContext]:
        """
        Check if a file should be modified by an AI model.
        
        Args:
            file_path: Path to the file to modify
            modification_type: Type of modification (edit, create, delete, move)
            ai_model: Name of the AI model requesting modification
        
        Returns:
            Tuple of (should_proceed, reason, context)
        """
        log_ai_decision(
            "model_awareness", 
            f"Checking modification permission for {file_path}",
            ai_model=ai_model
        )
        
        # Get file context
        context = self.check_file_context(file_path)
        
        # Check for locked files
        if file_path in self.system_status.get("locked_files", []):
            reason = f"File {file_path} is currently locked by another process"
            log_ai_decision("model_awareness", reason, ai_model=ai_model, confidence_score=0.0)
            return False, reason, context
        
        # Check for recent concurrent changes
        if context.concurrent_changes:
            reason = f"File {file_path} has concurrent changes in progress. Wait for stability."
            log_ai_decision("model_awareness", reason, ai_model=ai_model, confidence_score=0.2)
            return False, reason, context
        
        # Check stability score
        if context.stability_score < 0.3:
            reason = f"File {file_path} has low stability score ({context.stability_score:.2f}). System may be unstable."
            log_ai_decision("model_awareness", reason, ai_model=ai_model, confidence_score=0.3)
            return False, reason, context
        
        # Check critical files
        if any(critical in file_path for critical in self.critical_files):
            if len(context.recent_changes) > 0:
                reason = f"Critical file {file_path} was recently modified. Allow stabilization time."
                log_ai_decision("model_awareness", reason, ai_model=ai_model, confidence_score=0.4)
                return False, reason, context
        
        # Check for deletion of critical files
        if modification_type == "delete" and any(critical in file_path for critical in self.critical_files):
            reason = f"Cannot delete critical file {file_path}"
            log_ai_decision("model_awareness", reason, ai_model=ai_model, confidence_score=0.0)
            return False, reason, context
        
        # All checks passed
        reason = f"File {file_path} is safe to modify (stability: {context.stability_score:.2f})"
        log_ai_decision("model_awareness", reason, ai_model=ai_model, confidence_score=0.9)
        return True, reason, context
    
    def check_file_context(self, file_path: str) -> FileContext:
        """
        Get comprehensive context information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileContext with detailed information
        """
        recent_changes = self._get_recent_changes(file_path, hours=168)  # 7 days
        dependencies = self.file_dependencies.get(file_path, [])
        
        # Find related files (files that depend on this one)
        related_files = []
        for dep_file, deps in self.file_dependencies.items():
            if file_path in deps:
                related_files.append(dep_file)
        
        # Get file modification time
        try:
            path = Path(file_path)
            last_modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat() if path.exists() else None
        except Exception:
            last_modified = None
        
        stability_score = self._calculate_stability_score(file_path)
        concurrent_changes = self._get_concurrent_changes(file_path)
        
        return FileContext(
            file_path=file_path,
            recent_changes=recent_changes,
            dependencies=dependencies,
            related_files=related_files,
            last_modified=last_modified,
            stability_score=stability_score,
            concurrent_changes=concurrent_changes
        )
    
    def record_modification(self, file_path: str, ai_model: str, action: str, 
                           component: str, reason: str):
        """
        Record a file modification.
        
        Args:
            file_path: Path to the modified file
            ai_model: AI model that made the modification
            action: Type of action (edit, create, delete, move)
            component: Component that requested the modification
            reason: Reason for the modification
        """
        hash_before = self._get_file_hash(file_path)
        
        modification = FileModification(
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            ai_model=ai_model,
            action=action,
            component=component,
            reason=reason,
            hash_before=hash_before
        )
        
        self.recent_modifications.append(modification)
        self._save_modifications()
        
        log_ai_decision(
            "model_awareness",
            f"Recorded modification: {action} on {file_path} by {ai_model}",
            ai_model=ai_model
        )
    
    def finalize_modification(self, file_path: str):
        """
        Finalize a modification by updating the hash.
        
        Args:
            file_path: Path to the modified file
        """
        # Find the most recent modification for this file
        for mod in reversed(self.recent_modifications):
            if mod.file_path == file_path and mod.hash_after is None:
                mod.hash_after = self._get_file_hash(file_path)
                self._save_modifications()
                break
    
    def lock_file(self, file_path: str, ai_model: str):
        """
        Lock a file to prevent concurrent modifications.
        
        Args:
            file_path: Path to the file to lock
            ai_model: AI model requesting the lock
        """
        if file_path not in self.system_status.get("locked_files", []):
            self.system_status.setdefault("locked_files", []).append(file_path)
            self._save_system_status()
            log_info("model_awareness", f"Locked file {file_path} for {ai_model}")
    
    def unlock_file(self, file_path: str, ai_model: str):
        """
        Unlock a file to allow modifications.
        
        Args:
            file_path: Path to the file to unlock
            ai_model: AI model releasing the lock
        """
        locked_files = self.system_status.get("locked_files", [])
        if file_path in locked_files:
            locked_files.remove(file_path)
            self._save_system_status()
            log_info("model_awareness", f"Unlocked file {file_path} by {ai_model}")
    
    def update_system_status(self, error: str = None, stability_score: float = None):
        """
        Update system status information.
        
        Args:
            error: Recent error message if any
            stability_score: Overall system stability score
        """
        if error:
            self.system_status["last_error"] = {
                "message": error,
                "timestamp": datetime.now().isoformat()
            }
        
        if stability_score is not None:
            self.system_status["stability_score"] = stability_score
        
        self._save_system_status()
    
    def get_system_health(self) -> Dict:
        """Get overall system health information."""
        recent_errors = len([
            mod for mod in self.recent_modifications 
            if "error" in mod.reason.lower() or "fail" in mod.reason.lower()
        ])
        
        recent_changes = len([
            mod for mod in self.recent_modifications
            if datetime.fromisoformat(mod.timestamp) > datetime.now() - timedelta(hours=24)
        ])
        
        return {
            "stability_score": self.system_status.get("stability_score", 1.0),
            "recent_errors": recent_errors,
            "recent_changes": recent_changes,
            "locked_files": len(self.system_status.get("locked_files", [])),
            "last_error": self.system_status.get("last_error"),
            "system_status": "healthy" if self.system_status.get("stability_score", 1.0) > 0.7 else "unstable"
        }


# Global model awareness instance following copilot patterns
model_awareness = ModelAwareness()

# Convenience functions for direct import
def should_modify_file(file_path: str, modification_type: str, ai_model: str) -> Tuple[bool, str, FileContext]:
    """Check if file should be modified."""
    return model_awareness.should_modify_file(file_path, modification_type, ai_model)

def check_file_context(file_path: str) -> FileContext:
    """Get file context information."""
    return model_awareness.check_file_context(file_path)

def record_modification(file_path: str, ai_model: str, action: str, component: str, reason: str):
    """Record a file modification."""
    model_awareness.record_modification(file_path, ai_model, action, component, reason)

def finalize_modification(file_path: str):
    """Finalize a modification."""
    model_awareness.finalize_modification(file_path)

def lock_file(file_path: str, ai_model: str):
    """Lock a file."""
    model_awareness.lock_file(file_path, ai_model)

def unlock_file(file_path: str, ai_model: str):
    """Unlock a file."""
    model_awareness.unlock_file(file_path, ai_model)

def get_system_health() -> Dict:
    """Get system health information."""
    return model_awareness.get_system_health()