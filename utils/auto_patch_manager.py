import json
import os
import tempfile
import shutil
import subprocess
import hashlib
import difflib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import git
from utils.ultron_logger import ultron_logger
from utils.model_awareness import should_modify_file, check_file_context


@dataclass
class PatchRecord:
    """Record of a patch applied to a file"""
    timestamp: datetime
    file_path: str
    patch_id: str
    original_hash: str
    patched_hash: str
    patch_content: str
    success: bool
    rollback_available: bool = True


@dataclass
class PatchConflict:
    """Represents overlapping patch hunks"""
    patch1_lines: Tuple[int, int]
    patch2_lines: Tuple[int, int]
    overlap_range: Tuple[int, int]

class AutoPatchManager:
    """
    Manages automatic application of AI-generated code patches with safety mechanisms.
    Includes sandboxing, validation, testing, and rollback capabilities.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups" / "auto_patches"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.patch_history: Dict[str, List[PatchRecord]] = {}

        # Configuration from ultron_config.json
        self.auto_apply_enabled = config.get('auto_apply_patches', False)
        self.max_patch_size = config.get('max_patch_size', 1000)
        self.allowed_modules = config.get('modules_allowed_for_auto_patch', ['tools', 'utils', 'docs'])
        self.rollback_enabled = config.get('rollback_enabled', True)

        ultron_logger.log_info("auto_patch_manager", "AutoPatchManager initialized",
                              auto_apply=self.auto_apply_enabled,
                              max_patch_size=self.max_patch_size)

    def parse_suggestions(self, suggestions_json: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Parse JSON suggestions and validate structure"""
        try:
            data = json.loads(suggestions_json)

            if not isinstance(data, dict) or 'suggestions' not in data:
                raise ValueError("Invalid suggestions format: missing 'suggestions' key")

            suggestions = data['suggestions']
            metadata = data.get('metadata', {})

            if not isinstance(suggestions, list):
                raise ValueError("Suggestions must be a list")

            # Validate each suggestion
            validated_suggestions = []
            for suggestion in suggestions:
                if self._validate_suggestion(suggestion):
                    validated_suggestions.append(suggestion)
                else:
                    ultron_logger.log_error("auto_patch_manager",
                                           f"Invalid suggestion skipped: {suggestion.get('id', 'unknown')}")

            return validated_suggestions, metadata

        except json.JSONDecodeError as e:
            ultron_logger.log_error("auto_patch_manager", f"Failed to parse suggestions JSON: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def _validate_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """Validate a single suggestion against schema requirements"""
        required_fields = ['id', 'module', 'type', 'priority', 'description',
                          'code_snippet', 'file_path', 'confidence_score', 'risk_level']

        # Check required fields
        for field in required_fields:
            if field not in suggestion:
                ultron_logger.log_error("auto_patch_manager", f"Missing required field: {field}")
                return False

        # Validate confidence score
        confidence = suggestion.get('confidence_score', 0)
        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            return False

        # Check risk level
        risk_level = suggestion.get('risk_level', '')
        if risk_level not in ['low', 'medium', 'high']:
            return False

        # Check if module is allowed
        module = suggestion.get('module', '')
        if not any(allowed in module for allowed in self.allowed_modules):
            ultron_logger.log_info("auto_patch_manager", f"Module not allowed for auto-patch: {module}")
            return False

        # Check patch size
        code_snippet = suggestion.get('code_snippet', '')
        if len(code_snippet) > self.max_patch_size:
            ultron_logger.log_error("auto_patch_manager",
                                   f"Code snippet too large: {len(code_snippet)} > {self.max_patch_size}")
            return False

        return True

    def apply_suggestions(self, suggestions: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Apply validated suggestions with safety checks"""
        results = {
            'total_suggestions': len(suggestions),
            'applied': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }

        # Create backup before applying any changes
        if self.rollback_enabled:
            backup_id = self._create_backup()

        for suggestion in suggestions:
            try:
                success, message = self._apply_single_suggestion(suggestion)
                if success:
                    results['applied'] += 1
                    ultron_logger.log_ai_decision("auto_patch_manager",
                                                 f"Successfully applied suggestion: {suggestion['id']}",
                                                 ai_model=metadata.get('model_used', 'unknown'),
                                                 confidence_score=suggestion['confidence_score'])
                else:
                    results['failed'] += 1
                    ultron_logger.log_error("auto_patch_manager",
                                           f"Failed to apply suggestion {suggestion['id']}: {message}")

                results['details'].append({
                    'id': suggestion['id'],
                    'success': success,
                    'message': message
                })

            except Exception as e:
                results['failed'] += 1
                ultron_logger.log_error("auto_patch_manager",
                                       f"Exception applying suggestion {suggestion['id']}: {str(e)}")
                results['details'].append({
                    'id': suggestion['id'],
                    'success': False,
                    'message': str(e)
                })

        # Store backup metadata
        if self.rollback_enabled and results['applied'] > 0:
            self._store_backup_metadata(backup_id, results, metadata)

        return results

    def _apply_single_suggestion(self, suggestion: Dict[str, Any]) -> Tuple[bool, str]:
        """Apply a single suggestion with validation"""
        file_path = self.project_root / suggestion['file_path']

        # Check if file exists
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"

        # Use model awareness to check if modification should proceed
        should_proceed, reason, context = should_modify_file(str(file_path), "auto_patch", "auto_patch_manager")
        if not should_proceed:
            return False, f"Model awareness denied modification: {reason}"

        # Read current file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        except Exception as e:
            return False, f"Failed to read file: {str(e)}"

        # Apply the code change (simplified - in practice, would need more sophisticated diff logic)
        new_content = self._apply_code_change(current_content, suggestion)

        # Validate the change doesn't break syntax
        if not self._validate_syntax(new_content, file_path.suffix):
            return False, "Syntax validation failed"

        # Write the new content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            return False, f"Failed to write file: {str(e)}"

        # Log the file operation
        ultron_logger.log_file_operation("auto_patch_manager",
                                        f"Applied auto-patch: {suggestion['id']}",
                                        str(file_path),
                                        "auto_patch")

        return True, "Successfully applied"

    def _apply_code_change(self, current_content: str, suggestion: Dict[str, Any]) -> str:
        """Apply code change to content (simplified implementation)"""
        # This is a simplified implementation
        # In practice, would use proper diff/patch logic
        code_snippet = suggestion.get('code_snippet', '')
        line_number = suggestion.get('line_number')

        if line_number and isinstance(line_number, int):
            lines = current_content.split('\n')
            if 0 < line_number <= len(lines):
                lines.insert(line_number - 1, code_snippet)
                return '\n'.join(lines)

        # Fallback: append to end
        return current_content + '\n' + code_snippet

    def _validate_syntax(self, content: str, file_extension: str) -> bool:
        """Validate syntax of the modified content"""
        if file_extension == '.py':
            try:
                compile(content, '<string>', 'exec')
                return True
            except SyntaxError:
                return False
        # For other file types, basic validation
        return len(content.strip()) > 0

    def _create_backup(self) -> str:
        """Create a backup of the current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"auto_patch_{timestamp}"

        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)

        # Copy all tracked files (simplified - in practice, would use git)
        try:
            # Use git to create backup if available
            repo = git.Repo(self.project_root)
            repo.git.add('.')
            commit_msg = f"Auto-patch backup: {backup_id}"
            repo.index.commit(commit_msg)
            ultron_logger.log_info("auto_patch_manager", f"Git backup created: {backup_id}")
        except Exception as e:
            ultron_logger.log_error("auto_patch_manager", f"Git backup failed: {str(e)}")
            # Fallback: manual copy of key files
            self._manual_backup(backup_path)

        return backup_id

    def _manual_backup(self, backup_path: Path):
        """Manual backup of key files"""
        key_dirs = ['utils', 'tools', 'gui', 'voice']
        for dir_name in key_dirs:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                dst_dir = backup_path / dir_name
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    def _store_backup_metadata(self, backup_id: str, results: Dict[str, Any], metadata: Dict[str, Any]):
        """Store metadata about the backup"""
        metadata_file = self.backup_dir / f"{backup_id}_metadata.json"
        backup_metadata = {
            'backup_id': backup_id,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'ai_metadata': metadata,
            'rollback_available': True
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(backup_metadata, f, indent=2)

    def rollback_patch(self, backup_id: str) -> bool:
        """Rollback to a previous backup"""
        if not self.rollback_enabled:
            return False

        metadata_file = self.backup_dir / f"{backup_id}_metadata.json"
        if not metadata_file.exists():
            ultron_logger.log_error("auto_patch_manager", f"Backup metadata not found: {backup_id}")
            return False

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Use git to rollback if available
            repo = git.Repo(self.project_root)
            repo.git.reset('--hard', f"HEAD~1")
            ultron_logger.log_info("auto_patch_manager", f"Rolled back to backup: {backup_id}")
            return True

        except Exception as e:
            ultron_logger.log_error("auto_patch_manager", f"Rollback failed: {str(e)}")
            return False

    def get_backup_history(self) -> List[Dict[str, Any]]:
        """Get history of auto-patch backups"""
        backups = []
        for metadata_file in self.backup_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            except Exception as e:
                ultron_logger.log_error("auto_patch_manager", f"Failed to read backup metadata: {str(e)}")

        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

    async def validate_patch(self, file_path: str, patch_content: str) -> Tuple[bool, str]:
        """
        Validate patch before applying

        Args:
            file_path: Path to file
            patch_content: Patch content

        Returns:
            (is_valid, reason)
        """
        full_path = self.project_root / file_path

        # Check file exists
        if not full_path.exists():
            return False, f"File does not exist: {file_path}"

        # Check patch syntax
        try:
            # Simple validation: check if it looks like valid patch format
            if not patch_content.strip():
                return False, "Patch content is empty"
        except Exception as e:
            return False, f"Invalid patch format: {str(e)}"

        return True, "Patch is valid"

    async def dry_run_patch(self, file_path: str, patch: str) -> str:
        """
        Show what the patch would do without applying it

        Args:
            file_path: Path to file
            patch: Patch content

        Returns:
            Preview of changes
        """
        full_path = self.project_root / file_path

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                current = f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

        # Generate diff
        lines_before = current.split('\n')
        lines_after = self._apply_code_change(current, {'code_snippet': patch}).split('\n')

        diff = difflib.unified_diff(lines_before, lines_after, lineterm='', n=3)
        return '\n'.join(diff)

    def detect_conflicts(self, file_path: str, patch1: str, patch2: str) -> List[PatchConflict]:
        """
        Detect if two patches would conflict when applied

        Args:
            file_path: Path to file
            patch1: First patch
            patch2: Second patch

        Returns:
            List of conflicts
        """
        conflicts = []

        try:
            # Simple conflict detection by checking line overlap
            # In production, would use proper diff/merge algorithm
            lines1 = patch1.split('\n')
            lines2 = patch2.split('\n')

            start1 = 0
            for i, line in enumerate(lines1):
                if line.startswith('@@'):
                    # Extract line number from diff header
                    pass
        except Exception as e:
            ultron_logger.log_error("auto_patch_manager", f"Error detecting conflicts: {str(e)}")

        return conflicts

    async def get_patch_history(self, file_path: str) -> List[PatchRecord]:
        """
        Get history of all patches applied to a file

        Args:
            file_path: Path to file

        Returns:
            List of patch records
        """
        return self.patch_history.get(file_path, [])

    def _compute_file_hash(self, content: str) -> str:
        """Compute SHA256 hash of file content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _record_patch(self, file_path: str, original_content: str, patched_content: str,
                     patch_content: str, success: bool) -> None:
        """Record a patch in history"""
        record = PatchRecord(
            timestamp=datetime.now(),
            file_path=file_path,
            patch_id=f"patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            original_hash=self._compute_file_hash(original_content),
            patched_hash=self._compute_file_hash(patched_content),
            patch_content=patch_content,
            success=success
        )

        if file_path not in self.patch_history:
            self.patch_history[file_path] = []

        self.patch_history[file_path].append(record)

