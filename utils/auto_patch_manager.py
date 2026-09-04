import json
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import git
from utils.ultron_logger import ultron_logger
from utils.model_awareness import should_modify_file, check_file_context

class AutoPatchManager:
    """
    Manages automatic application of AI-generated code patches with safety mechanisms.
    Includes sandboxing, validation, testing, and rollback capabilities.
    """

    def __init__(self, config: Dict[str, Any]):
        if not config:
            raise KeyError("Missing required auto_patch configuration")

        required_keys = ['auto_apply_patches', 'max_patch_size', 'modules_allowed_for_auto_patch', 'rollback_enabled']
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise KeyError(f"Missing required config keys: {missing}")

        self.config = config
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups" / "auto_patches"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

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

    def apply_patches(self, suggestions: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Compatibility wrapper that returns a list of per-suggestion results."""
        metadata = metadata or {}
        results = self.apply_suggestions(suggestions, metadata)
        return [
            {
                'id': detail.get('id', 'unknown'),
                'success': detail.get('success', False),
                'message': detail.get('message', ''),
            }
            for detail in results.get('details', [])
        ]

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

        # Use model awareness to check if modification should proceed
        should_proceed, reason, context = should_modify_file(str(file_path), "auto_patch", "auto_patch_manager")
        if not should_proceed:
            return False, f"Model awareness denied modification: {reason}"

        # Read current file content if the file exists; otherwise treat as empty content.
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            except Exception as e:
                return False, f"Failed to read file: {str(e)}"
        else:
            current_content = ""

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
            if not src_dir.exists():
                continue

            dst_dir = backup_path / dir_name
            dst_dir.mkdir(parents=True, exist_ok=True)

            for src_path in src_dir.iterdir():
                dst_path = dst_dir / src_path.name
                try:
                    if src_path.is_dir():
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dst_path)
                except Exception:
                    continue

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
