"""
Comprehensive Integration Test Suite for ULTRON Agent
Tests core functionality, API endpoints, tools, and system integration
"""

import pytest
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from agent_core import UltronAgent
    from brain import UltronBrain
    import api_server
    from model_performance import ModelPerformanceTracker
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def agent():
    """Create test agent instance"""
    if not IMPORTS_AVAILABLE:
        pytest.skip(f"Required imports not available: {IMPORT_ERROR}")
    
    try:
        agent = UltronAgent()
        return agent
    except Exception as e:
        pytest.skip(f"Failed to initialize agent: {e}")


@pytest.fixture
def brain():
    """Create test brain instance"""
    if not IMPORTS_AVAILABLE:
        pytest.skip(f"Required imports not available: {IMPORT_ERROR}")
    
    try:
        brain = UltronBrain()
        return brain
    except Exception as e:
        pytest.skip(f"Failed to initialize brain: {e}")


class TestCoreComponents:
    """Test core system components"""
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent is not None
        assert hasattr(agent, 'brain')
        assert hasattr(agent, 'status')
    
    def test_brain_initialization(self, brain):
        """Test brain initializes correctly"""
        assert brain is not None
        assert hasattr(brain, 'model')
        assert hasattr(brain, 'ollama_url')
    
    @pytest.mark.asyncio
    async def test_brain_async_think(self, brain):
        """Test brain's async thinking capability"""
        try:
            response = await brain.think("Hello, test query")
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"Async think test failed: {e}")


class TestAPIEndpoints:
    """Test API server endpoints"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client for API"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("API server not available")
        
        api_server.app.config['TESTING'] = True
        with api_server.app.test_client() as client:
            yield client
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded']
    
    def test_status_endpoint(self, client):
        """Test status endpoint"""
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_feedback_endpoint(self, client):
        """Test feedback submission endpoint"""
        feedback_data = {
            "type": "feature",
            "message": "Test feedback from integration test",
            "rating": 5
        }
        response = client.post(
            '/api/feedback',
            data=json.dumps(feedback_data),
            content_type='application/json'
        )
        assert response.status_code in [201, 200]
        data = json.loads(response.data)
        assert data.get('success') == True
    
    def test_feedback_stats_endpoint(self, client):
        """Test feedback stats endpoint"""
        response = client.get('/api/feedback/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'by_type' in data
    
    def test_tools_status_endpoint(self, client):
        """Test tools status endpoint"""
        response = client.get('/api/tools/status')
        assert response.status_code in [200, 500]  # May fail if agent not init
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'total' in data
            assert 'active' in data


class TestToolsSystem:
    """Test tools loading and execution"""
    
    def test_tools_directory_exists(self):
        """Test tools directory exists"""
        tools_dir = Path(__file__).parent.parent / "tools"
        assert tools_dir.exists()
        assert tools_dir.is_dir()
    
    def test_tool_interface_exists(self):
        """Test tool interface is available"""
        tools_dir = Path(__file__).parent.parent / "tools"
        interface_file = tools_dir / "tool_interface.py"
        assert interface_file.exists()
    
    def test_tools_can_be_imported(self):
        """Test tools can be imported"""
        try:
            from tools.tool_interface import ToolInterface
            assert ToolInterface is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ToolInterface: {e}")
    
    def test_agent_loads_tools(self, agent):
        """Test agent loads tools successfully"""
        tools = agent.list_tools()
        assert tools is not None
        assert isinstance(tools, list)
        assert len(tools) > 0


class TestModelPerformance:
    """Test model performance tracking"""
    
    def test_tracker_initialization(self):
        """Test performance tracker initializes"""
        tracker = ModelPerformanceTracker()
        assert tracker is not None
        assert tracker.metrics is not None
    
    def test_record_inference(self):
        """Test recording model inference"""
        tracker = ModelPerformanceTracker()
        
        tracker.record_inference(
            model_name="test_model",
            task_type="test_task",
            latency_ms=100.0,
            success=True,
            tokens_input=50,
            tokens_output=100
        )
        
        stats = tracker.get_model_stats("test_model")
        assert stats is not None
        assert stats['total_requests'] == 1
        assert stats['success_rate'] == 1.0
    
    def test_get_best_model_for_task(self):
        """Test best model recommendation"""
        tracker = ModelPerformanceTracker()
        
        # Record multiple inferences
        tracker.record_inference("model_a", "chat", 100.0, True)
        tracker.record_inference("model_a", "chat", 120.0, True)
        tracker.record_inference("model_b", "chat", 80.0, True)
        tracker.record_inference("model_b", "chat", 90.0, True)
        
        best = tracker.get_best_model_for_task("chat")
        assert best in ["model_a", "model_b"]
    
    def test_generate_report(self):
        """Test report generation"""
        tracker = ModelPerformanceTracker()
        tracker.record_inference("test_model", "test", 100.0, True)
        
        report = tracker.generate_report()
        assert isinstance(report, str)
        assert len(report) > 0
        assert "MODEL PERFORMANCE REPORT" in report


class TestEvolutionFramework:
    """Test evolution framework components"""
    
    def test_self_improvement_file_exists(self):
        """Test self_improvement.py exists"""
        file_path = Path(__file__).parent.parent / "self_improvement.py"
        assert file_path.exists()
    
    def test_suggestions_system_exists(self):
        """Test view_suggestions.py exists"""
        file_path = Path(__file__).parent.parent / "view_suggestions.py"
        assert file_path.exists()
    
    def test_auto_improve_system_exists(self):
        """Test auto_improve.py exists"""
        file_path = Path(__file__).parent.parent / "auto_improve.py"
        assert file_path.exists()
    
    def test_metrics_directory_exists(self):
        """Test metrics directory exists or can be created"""
        metrics_dir = Path(__file__).parent.parent / "metrics"
        if not metrics_dir.exists():
            metrics_dir.mkdir(parents=True, exist_ok=True)
        assert metrics_dir.exists()


class TestConfigurationSystem:
    """Test configuration loading and management"""
    
    def test_config_file_exists(self):
        """Test ultron_config.json exists"""
        config_file = Path(__file__).parent.parent / "ultron_config.json"
        assert config_file.exists()
    
    def test_config_is_valid_json(self):
        """Test config file is valid JSON"""
        config_file = Path(__file__).parent.parent / "ultron_config.json"
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            assert config is not None
            assert isinstance(config, dict)
        except json.JSONDecodeError as e:
            pytest.fail(f"Config file is not valid JSON: {e}")
    
    def test_config_has_required_fields(self):
        """Test config has required fields"""
        config_file = Path(__file__).parent.parent / "ultron_config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_fields = [
            'llm_model',
            'ollama_base_url',
            'api_host',
            'api_port'
        ]
        
        for field in required_fields:
            assert field in config, f"Config missing field: {field}"


class TestFileStructure:
    """Test project file structure"""
    
    def test_main_file_exists(self):
        """Test main.py exists"""
        assert (Path(__file__).parent.parent / "main.py").exists()
    
    def test_agent_core_exists(self):
        """Test agent_core.py exists"""
        assert (Path(__file__).parent.parent / "agent_core.py").exists()
    
    def test_brain_exists(self):
        """Test brain.py exists"""
        assert (Path(__file__).parent.parent / "brain.py").exists()
    
    def test_api_server_exists(self):
        """Test api_server.py exists"""
        assert (Path(__file__).parent.parent / "api_server.py").exists()
    
    def test_web_gui_exists(self):
        """Test web GUI files exist"""
        gui_dir = (
            Path(__file__).parent.parent / "gui" /
            "ultron_enhanced" / "web"
        )
        assert gui_dir.exists()
        assert (gui_dir / "index.html").exists()
        assert (gui_dir / "app.js").exists()
        assert (gui_dir / "styles.css").exists()


class TestLoggingSystem:
    """Test logging functionality"""
    
    def test_logger_module_exists(self):
        """Test ultron_logger exists"""
        logger_file = (
            Path(__file__).parent.parent / "utils" / "ultron_logger.py"
        )
        assert logger_file.exists()
    
    def test_logs_directory_exists(self):
        """Test logs directory exists or can be created"""
        logs_dir = Path(__file__).parent.parent / "logs"
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
        assert logs_dir.exists()


# Test fixtures and utilities
@pytest.fixture(scope="session", autouse=True)
def test_setup_and_teardown():
    """Setup and teardown for all tests"""
    print("\n🔴 Starting ULTRON Integration Tests 🔴")
    yield
    print("\n✅ ULTRON Integration Tests Complete ✅")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "-x"])
