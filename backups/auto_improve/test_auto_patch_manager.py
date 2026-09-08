import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from utils.auto_patch_manager import AutoPatchManager

class TestAutoPatchManager:
    """Test cases for AutoPatchManager functionality"""

    @pytest.fixture
    def config(self):
        return {
            'auto_apply_patches': False,
            'max_patch_size': 1000,
            'modules_allowed_for_auto_patch': ['tools', 'utils'],
            'rollback_enabled': True
        }

    @pytest.fixture
    def patch_manager(self, config):
        return AutoPatchManager(config)

    def test_initialization(self, patch_manager, config):
        """Test that AutoPatchManager initializes correctly"""
        assert patch_manager.config == config
        assert patch_manager.auto_apply_enabled == config['auto_apply_patches']
        assert patch_manager.max_patch_size == config['max_patch_size']
        assert patch_manager.allowed_modules == config['modules_allowed_for_auto_patch']
        assert patch_manager.rollback_enabled == config['rollback_enabled']

    def test_parse_suggestions_valid(self, patch_manager):
        """Test parsing valid JSON suggestions"""
        valid_json = {
            "suggestions": [
                {
                    "id": "test_001",
                    "module": "utils",
                    "type": "refactor",
                    "priority": "medium",
                    "description": "Test suggestion",
                    "code_snippet": "print('test')",
                    "file_path": "utils/test.py",
                    "confidence_score": 0.85,
                    "risk_level": "low",
                    "dependencies": [],
                    "test_required": True,
                    "rollback_plan": "Revert changes"
                }
            ],
            "metadata": {
                "analysis_timestamp": "2025-09-20T10:00:00Z",
                "model_used": "test-model",
                "analysis_scope": "utils",
                "total_suggestions": 1,
                "estimated_effort": "1 hour"
            }
        }

        suggestions, metadata = patch_manager.parse_suggestions(json.dumps(valid_json))

        assert len(suggestions) == 1
        assert suggestions[0]['id'] == 'test_001'
        assert metadata['model_used'] == 'test-model'

    def test_parse_suggestions_invalid_json(self, patch_manager):
        """Test parsing invalid JSON"""
        with pytest.raises(ValueError, match="Invalid JSON format"):
            patch_manager.parse_suggestions("invalid json")

    def test_parse_suggestions_missing_suggestions(self, patch_manager):
        """Test parsing JSON without suggestions key"""
        invalid_json = {"metadata": {}}
        with pytest.raises(ValueError, match="Invalid suggestions format"):
            patch_manager.parse_suggestions(json.dumps(invalid_json))

    def test_validate_suggestion_valid(self, patch_manager):
        """Test validating a valid suggestion"""
        valid_suggestion = {
            "id": "test_001",
            "module": "utils",
            "type": "refactor",
            "priority": "medium",
            "description": "Test suggestion",
            "code_snippet": "print('test')",
            "file_path": "utils/test.py",
            "confidence_score": 0.85,
            "risk_level": "low",
            "dependencies": [],
            "test_required": True,
            "rollback_plan": "Revert changes"
        }

        assert patch_manager._validate_suggestion(valid_suggestion)

    def test_validate_suggestion_missing_field(self, patch_manager):
        """Test validating suggestion with missing required field"""
        invalid_suggestion = {
            "module": "utils",
            "type": "refactor",
            # Missing 'id'
        }

        assert not patch_manager._validate_suggestion(invalid_suggestion)

    def test_validate_suggestion_invalid_confidence(self, patch_manager):
        """Test validating suggestion with invalid confidence score"""
        invalid_suggestion = {
            "id": "test_001",
            "module": "utils",
            "type": "refactor",
            "priority": "medium",
            "description": "Test suggestion",
            "code_snippet": "print('test')",
            "file_path": "utils/test.py",
            "confidence_score": 1.5,  # Invalid: > 1.0
            "risk_level": "low"
        }

        assert not patch_manager._validate_suggestion(invalid_suggestion)

    def test_validate_suggestion_invalid_risk_level(self, patch_manager):
        """Test validating suggestion with invalid risk level"""
        invalid_suggestion = {
            "id": "test_001",
            "module": "utils",
            "type": "refactor",
            "priority": "medium",
            "description": "Test suggestion",
            "code_snippet": "print('test')",
            "file_path": "utils/test.py",
            "confidence_score": 0.85,
            "risk_level": "invalid"  # Invalid risk level
        }

        assert not patch_manager._validate_suggestion(invalid_suggestion)

    def test_validate_suggestion_disallowed_module(self, patch_manager):
        """Test validating suggestion for disallowed module"""
        invalid_suggestion = {
            "id": "test_001",
            "module": "core",  # Not in allowed modules
            "type": "refactor",
            "priority": "medium",
            "description": "Test suggestion",
            "code_snippet": "print('test')",
            "file_path": "core/test.py",
            "confidence_score": 0.85,
            "risk_level": "low"
        }

        assert not patch_manager._validate_suggestion(invalid_suggestion)

    def test_validate_suggestion_code_too_large(self, patch_manager):
        """Test validating suggestion with code snippet too large"""
        large_code = "x" * 2000  # Larger than max_patch_size (1000)
        invalid_suggestion = {
            "id": "test_001",
            "module": "utils",
            "type": "refactor",
            "priority": "medium",
            "description": "Test suggestion",
            "code_snippet": large_code,
            "file_path": "utils/test.py",
            "confidence_score": 0.85,
            "risk_level": "low"
        }

        assert not patch_manager._validate_suggestion(invalid_suggestion)

    @patch('utils.auto_patch_manager.should_modify_file')
    @patch('builtins.open', new_callable=mock_open, read_data="original content")
    def test_apply_single_suggestion_success(self, mock_file, mock_should_modify, patch_manager):
        """Test successfully applying a single suggestion"""
        mock_should_modify.return_value = (True, "OK", {})

        suggestion = {
            "id": "test_001",
            "module": "utils",
            "type": "refactor",
            "description": "Test suggestion",
            "code_snippet": "print('test')",
            "file_path": "utils/test.py",
            "confidence_score": 0.85,
            "risk_level": "low"
        }

        success, message = patch_manager._apply_single_suggestion(suggestion)

        assert success
        assert "Successfully applied" in message
        mock_file.assert_called()

    @patch('utils.auto_patch_manager.should_modify_file')
    def test_apply_single_suggestion_denied(self, mock_should_modify, patch_manager):
        """Test applying suggestion when modification is denied"""
        mock_should_modify.return_value = (False, "File locked", {})

        suggestion = {
            "id": "test_001",
            "module": "utils",
            "type": "refactor",
            "description": "Test suggestion",
            "code_snippet": "print('test')",
            "file_path": "utils/test.py",
            "confidence_score": 0.85,
            "risk_level": "low"
        }

        success, message = patch_manager._apply_single_suggestion(suggestion)

        assert not success
        assert "denied" in message.lower()

    @patch('utils.auto_patch_manager.git.Repo')
    def test_create_backup_git(self, mock_repo, patch_manager):
        """Test creating backup using git"""
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance

        backup_id = patch_manager._create_backup()

        assert backup_id.startswith("auto_patch_")
        mock_repo_instance.git.add.assert_called_with('.')
        mock_repo_instance.index.commit.assert_called()

    def test_get_backup_history(self, patch_manager):
        """Test retrieving backup history"""
        # Create a mock backup metadata file
        backup_dir = patch_manager.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)

        mock_metadata = {
            "backup_id": "test_backup",
            "timestamp": "2025-09-20T10:00:00Z",
            "results": {"applied": 1},
            "ai_metadata": {"model_used": "test"}
        }

        metadata_file = backup_dir / "test_backup_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(mock_metadata, f)

        history = patch_manager.get_backup_history()

        assert len(history) >= 1
        assert history[0]['backup_id'] == 'test_backup'

        # Cleanup
        metadata_file.unlink()
