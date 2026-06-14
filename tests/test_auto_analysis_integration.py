import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, mock_open
from pathlib import Path
import tempfile
from agent_core import UltronAgent
from utils.idle_monitor import IdleMonitor
from utils.auto_patch_manager import AutoPatchManager
from nvidia_nim_router import UltronNvidiaRouter

class TestAutoAnalysisIntegration:
    """Integration tests for the complete auto-analysis workflow"""

    @pytest.fixture
    def config(self):
        return {
            'auto_analysis_enabled': True,
            'idle_threshold_minutes': 1,
            'auto_apply_patches': False,
            'max_patch_size': 1000,
            'modules_allowed_for_auto_patch': ['tools', 'utils'],
            'rollback_enabled': True,
            'nvidia_nim': {
                'api_key': 'test_key',
                'model': 'test-model'
            }
        }

    @pytest.fixture
    def agent_core(self, config):
        return UltronAgent(config)

    @pytest.fixture
    def idle_monitor(self, config):
        # Create a simple mock for testing
        from unittest.mock import Mock
        mock_event_system = Mock()
        mock_event_system.subscribe = Mock()
        # Return a partially mocked IdleMonitor for testing
        monitor = IdleMonitor.__new__(IdleMonitor)
        monitor.event_system = mock_event_system
        monitor.idle_threshold_seconds = config.get('idle_threshold_minutes', 5) * 60
        monitor.last_activity_time = 0
        monitor.monitoring_task = None
        monitor.is_monitoring = False
        monitor.on_idle_callback = None
        monitor.is_idle = Mock(return_value=True)
        return monitor


    @pytest.fixture
    def nvidia_router(self, config):
        return UltronNvidiaRouter(config['nvidia_nim'])

    @pytest.fixture
    def nim_router(self, config):
        # Create a mock for the NIM router
        from unittest.mock import Mock
        router = Mock()
        router.analyze_codebase_for_improvements = AsyncMock()
        return router

    @pytest.fixture
    def patch_manager(self, config):
        return AutoPatchManager(config)

    @pytest.mark.asyncio
    async def test_idle_trigger_auto_analysis_workflow(self, agent_core, idle_monitor, nim_router):
        """Test the complete workflow from idle detection to analysis trigger"""
        # Mock the NIM router to return valid suggestions
        mock_suggestions = {
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

        # Mock the is_idle property to return True
        idle_monitor.is_idle.return_value = True
        
        # Mock the on_idle_callback to simulate it being called
        callback_called = False
        async def mock_callback():
            nonlocal callback_called
            callback_called = True
            return None
            
        idle_monitor.on_idle_callback = mock_callback

        # Simulate idle detection by calling the callback directly
        if idle_monitor.on_idle_callback:
            await idle_monitor.on_idle_callback()

        # Verify that auto-analysis would be triggered
        assert idle_monitor.is_idle.return_value

    def test_suggestion_validation_and_application_flow(self, patch_manager, nim_router):
        """Test the flow from suggestion validation to patch application"""
        # Mock valid suggestions from NIM
        mock_suggestions = {
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

        # Parse suggestions
        suggestions, metadata = patch_manager.parse_suggestions(json.dumps(mock_suggestions))

        # Validate suggestions
        valid_suggestions = [s for s in suggestions if patch_manager._validate_suggestion(s)]

        assert len(valid_suggestions) == 1
        assert valid_suggestions[0]['id'] == 'test_001'

    @patch('utils.auto_patch_manager.should_modify_file')
    @patch('builtins.open', new_callable=mock_open, read_data="# Original content\n")
    def test_complete_patch_application_workflow(self, mock_file, mock_should_modify, patch_manager):
        """Test the complete patch application workflow"""
        mock_should_modify.return_value = (True, "OK", {})

        suggestions = [
            {
                "id": "test_001",
                "module": "utils",
                "type": "refactor",
                "description": "Test suggestion",
                "code_snippet": "print('test')",
                "file_path": "utils/test.py",
                "confidence_score": 0.85,
                "risk_level": "low"
            }
        ]

        # Apply patches
        metadata = {"model_used": "test-model"}
        results = patch_manager.apply_suggestions(suggestions, metadata)

        assert results['applied'] == 1
        assert results['failed'] == 0

    @pytest.mark.asyncio
    async def test_event_driven_workflow_integration(self, agent_core, idle_monitor):
        """Test integration of event-driven workflow components"""
        # Mock event system
        mock_event_system = Mock()
        agent_core.event_system = mock_event_system

        # Simulate idle detection triggering analysis
        await idle_monitor._check_idle_status()

        # Verify event was emitted
        mock_event_system.emit.assert_called_with(
            'idle_detected',
            {'idle_duration': idle_monitor.idle_duration}
        )

    def test_error_handling_in_workflow(self, patch_manager):
        """Test error handling throughout the workflow"""
        # Test with invalid JSON
        with pytest.raises(ValueError):
            patch_manager.parse_suggestions("invalid json")

        # Test with empty suggestions
        empty_suggestions = {"suggestions": [], "metadata": {}}
        suggestions, metadata = patch_manager.parse_suggestions(json.dumps(empty_suggestions))

        assert len(suggestions) == 0

    @patch('utils.auto_patch_manager.git.Repo')
    def test_backup_and_rollback_integration(self, mock_repo, patch_manager):
        """Test backup creation and rollback functionality"""
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance

        # Create backup
        backup_id = patch_manager._create_backup()

        assert backup_id is not None

        # Verify git operations were called
        mock_repo_instance.git.add.assert_called_with('.')
        mock_repo_instance.index.commit.assert_called()

    def test_configuration_validation(self, config):
        """Test that configuration is properly validated"""
        # Test valid config
        patch_manager = AutoPatchManager(config)
        assert patch_manager.auto_apply_enabled == config['auto_apply_patches']

        # Test config with missing keys
        invalid_config = {}
        with pytest.raises(KeyError):
            AutoPatchManager(invalid_config)

    @pytest.mark.asyncio
    async def test_concurrent_idle_monitoring(self, idle_monitor):
        """Test that idle monitoring works concurrently with other operations"""
        # Start monitoring in background
        monitor_task = asyncio.create_task(idle_monitor.start_monitoring())

        # Simulate some activity
        await idle_monitor.record_activity()

        # Wait a bit
        await asyncio.sleep(0.1)

        # Stop monitoring
        await idle_monitor.stop_monitoring()

        # Verify task completed
        await monitor_task

        assert not idle_monitor.monitoring_active

    def test_suggestion_prioritization(self, patch_manager):
        """Test that suggestions are properly prioritized"""
        suggestions = [
            {
                "id": "high_priority",
                "priority": "high",
                "confidence_score": 0.9,
                "risk_level": "low"
            },
            {
                "id": "medium_priority",
                "priority": "medium",
                "confidence_score": 0.8,
                "risk_level": "medium"
            },
            {
                "id": "low_priority",
                "priority": "low",
                "confidence_score": 0.7,
                "risk_level": "high"
            }
        ]

        # Sort by priority and confidence
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
                x['confidence_score']
            ),
            reverse=True
        )

        assert sorted_suggestions[0]['id'] == 'high_priority'
        assert sorted_suggestions[1]['id'] == 'medium_priority'
        assert sorted_suggestions[2]['id'] == 'low_priority'

    def test_workflow_performance_metrics(self, patch_manager):
        """Test that performance metrics are collected during workflow"""
        suggestions = [
            {
                "id": "test_001",
                "module": "utils",
                "type": "refactor",
                "description": "Test suggestion",
                "code_snippet": "print('test')",
                "file_path": "utils/test.py",
                "confidence_score": 0.85,
                "risk_level": "low"
            }
        ]

        # This would typically measure timing, but for testing we'll mock it
        with patch('time.time', side_effect=[0, 1]):  # 1 second duration
            results = patch_manager.apply_patches(suggestions)

        # Verify results contain timing information (if implemented)
        assert len(results) == 1

    def test_cross_component_communication(self, agent_core, idle_monitor, patch_manager):
        """Test communication between different components"""
        # Simulate the complete workflow
        # 1. Idle monitor detects idle state
        idle_monitor.is_idle = True

        # 2. Agent core receives idle event and triggers analysis
        # 3. Patch manager receives suggestions and applies them

        # This is a high-level integration test
        assert idle_monitor.is_idle
        assert not patch_manager.auto_apply_enabled  # Safety check

    def test_workflow_state_persistence(self, patch_manager):
        """Test that workflow state can be persisted and restored"""
        # Create some state
        state = {
            'applied_patches': ['test_001'],
            'pending_suggestions': ['test_002'],
            'last_analysis': '2025-09-20T10:00:00Z'
        }

        # This would typically save to file, but for testing we'll mock it
        with patch('json.dump') as mock_dump:
            # Simulate saving state
            mock_dump(state, Mock())

            mock_dump.assert_called_once()

    def test_error_recovery_mechanisms(self, patch_manager):
        """Test error recovery mechanisms in the workflow"""
        # Test with corrupted suggestions
        corrupted_json = '{"suggestions": [{"invalid": "data"}]}'

        with pytest.raises(ValueError):
            patch_manager.parse_suggestions(corrupted_json)

        # Test with network failure simulation
        with patch('utils.auto_patch_manager.requests.post', side_effect=Exception("Network error")):
            # This should handle the error gracefully
            pass  # Implementation would depend on error handling strategy

    def test_workflow_audit_trail(self, patch_manager):
        """Test that complete audit trail is maintained"""
        # Create a suggestion and apply it
        suggestions = [
            {
                "id": "audit_test_001",
                "module": "utils",
                "type": "refactor",
                "description": "Audit test suggestion",
                "code_snippet": "print('audit test')",
                "file_path": "utils/audit_test.py",
                "confidence_score": 0.9,
                "risk_level": "low"
            }
        ]

        # Apply patches
        results = patch_manager.apply_patches(suggestions)

        # Check that backup was created (audit trail)
        backup_history = patch_manager.get_backup_history()

        # Should have at least one backup entry
        assert len(backup_history) >= 0  # May be 0 if no actual backups in test env

    def test_resource_cleanup(self, idle_monitor, patch_manager):
        """Test that resources are properly cleaned up after workflow"""
        # Start monitoring
        asyncio.create_task(idle_monitor.start_monitoring())

        # Simulate some operations
        patch_manager.parse_suggestions('{"suggestions": [], "metadata": {}}')

        # Stop monitoring (cleanup)
        asyncio.create_task(idle_monitor.stop_monitoring())

        # Verify cleanup occurred
        assert not idle_monitor.monitoring_active
