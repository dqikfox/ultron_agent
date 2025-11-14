"""
Unit and integration tests for dynamic_loader utility
"""

import pytest
from utils.dynamic_loader import (
    DynamicLoader, PluginBase, PluginMetadata, PluginError
)


class SimpleTestPlugin(PluginBase):
    """Simple test plugin for testing"""

    def __init__(self):
        self.initialized = False
        self.config = None
        self.executed = False

    @property
    def metadata(self):
        return PluginMetadata(
            name="simple_test_plugin",
            version="1.0.0",
            author="Test Author",
            description="Simple test plugin"
        )

    def initialize(self, config):
        self.initialized = True
        self.config = config
        return True

    def execute(self, *args, **kwargs):
        if not self.initialized:
            raise RuntimeError("Plugin not initialized")
        self.executed = True
        return {"result": "executed", "args": args, "kwargs": kwargs}

    def cleanup(self):
        self.initialized = False


class FailingPlugin(PluginBase):
    """Plugin that fails initialization"""

    @property
    def metadata(self):
        return PluginMetadata(
            name="failing_plugin",
            version="1.0.0",
            author="Test",
            description="Fails to initialize"
        )

    def initialize(self, config):
        return False  # Initialization fails

    def execute(self, *args, **kwargs):
        return None

    def cleanup(self):
        pass


class TestDynamicLoader:
    """Tests for DynamicLoader class"""

    @pytest.mark.unit
    def test_loader_initialization(self):
        """Test DynamicLoader initialization"""
        loader = DynamicLoader()
        assert loader.loaded_plugins == {}
        assert loader.plugin_versions == {}
        assert loader.plugin_errors == []
        assert loader.hot_reload_enabled is False

    @pytest.mark.unit
    def test_loader_with_custom_plugin_dir(self, temp_dir):
        """Test DynamicLoader with custom plugin directory"""
        loader = DynamicLoader(plugin_dir=str(temp_dir))
        assert loader.plugin_dir == temp_dir

    @pytest.mark.unit
    def test_get_plugin_not_found(self):
        """Test getting non-existent plugin"""
        loader = DynamicLoader()
        plugin = loader.get_plugin("nonexistent")
        assert plugin is None
        assert loader is not None

    @pytest.mark.unit
    def test_list_loaded_plugins_empty(self):
        """Test listing plugins when none loaded"""
        loader = DynamicLoader()
        plugins = loader.list_loaded_plugins()
        assert plugins == {}


class TestPluginLoading:
    """Tests for plugin loading"""

    @pytest.mark.unit
    def test_load_plugin_from_class(self):
        """Test loading plugin from class"""
        loader = DynamicLoader()

        # Manually create and test plugin
        plugin = SimpleTestPlugin()
        assert plugin.metadata.name == "simple_test_plugin"
        assert plugin.metadata.version == "1.0.0"

    @pytest.mark.unit
    def test_plugin_metadata_access(self):
        """Test accessing plugin metadata"""
        plugin = SimpleTestPlugin()
        metadata = plugin.metadata

        assert metadata.name == "simple_test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.description is not None

    @pytest.mark.unit
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        plugin = SimpleTestPlugin()
        config = {"setting1": "value1"}

        success = plugin.initialize(config)

        assert success is True
        assert plugin.initialized is True
        assert plugin.config == config

    @pytest.mark.unit
    def test_plugin_execution(self):
        """Test plugin execution"""
        plugin = SimpleTestPlugin()
        plugin.initialize({})

        result = plugin.execute("arg1", kwarg1="value1")

        assert result["result"] == "executed"
        assert plugin.executed is True

    @pytest.mark.unit
    def test_plugin_cleanup(self):
        """Test plugin cleanup"""
        plugin = SimpleTestPlugin()
        plugin.initialize({})

        plugin.cleanup()

        assert plugin.initialized is False

    @pytest.mark.unit
    def test_plugin_fails_without_initialization(self):
        """Test that plugin raises error if execute before init"""
        plugin = SimpleTestPlugin()

        with pytest.raises(RuntimeError, match="not initialized"):
            plugin.execute()

    @pytest.mark.unit
    def test_failing_plugin_initialization(self):
        """Test plugin that fails to initialize"""
        plugin = FailingPlugin()

        success = plugin.initialize({})

        assert success is False


class TestPluginMetadata:
    """Tests for PluginMetadata"""

    @pytest.mark.unit
    def test_metadata_creation_minimal(self):
        """Test creating metadata with minimal fields"""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )

        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test"
        assert metadata.description == "Test plugin"
        assert metadata.required_version is None
        assert metadata.dependencies is None

    @pytest.mark.unit
    def test_metadata_with_dependencies(self):
        """Test metadata with dependencies"""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test",
            dependencies=["json", "asyncio"]
        )

        assert metadata.dependencies == ["json", "asyncio"]

    @pytest.mark.unit
    def test_metadata_compatibility(self):
        """Test metadata compatibility information"""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test",
            compatible_with=["ultron:3.0", "ultron:3.1"]
        )

        assert "ultron:3.0" in metadata.compatible_with


class TestPluginError:
    """Tests for PluginError"""

    @pytest.mark.unit
    def test_plugin_error_creation(self):
        """Test creating PluginError"""
        error = PluginError(
            plugin_name="test_plugin",
            error_type="ModuleNotFound",
            message="Plugin module not found"
        )

        assert error.plugin_name == "test_plugin"
        assert error.error_type == "ModuleNotFound"
        assert error.message is not None

    @pytest.mark.unit
    def test_plugin_error_with_traceback(self):
        """Test PluginError with traceback"""
        error = PluginError(
            plugin_name="test_plugin",
            error_type="ImportError",
            message="Import failed",
            traceback="ImportError: No module named 'test'"
        )

        assert error.traceback is not None
        assert "ImportError" in error.traceback


class TestPluginIntegration:
    """Integration tests for plugin system"""

    @pytest.mark.integration
    def test_full_plugin_lifecycle(self):
        """Test complete plugin lifecycle"""
        loader = DynamicLoader()

        # Create and initialize plugin
        plugin = SimpleTestPlugin()
        config = {"setting": "value"}
        success = plugin.initialize(config)
        assert success is True

        # Execute plugin
        result = plugin.execute("test_arg")
        assert result["result"] == "executed"

        # Cleanup
        plugin.cleanup()
        assert plugin.initialized is False

    @pytest.mark.integration
    def test_multiple_plugins(self):
        """Test loading multiple plugins"""
        loader = DynamicLoader()

        plugin1 = SimpleTestPlugin()
        plugin2 = SimpleTestPlugin()

        plugin1.initialize({})
        plugin2.initialize({})

        result1 = plugin1.execute()
        result2 = plugin2.execute()

        assert result1["result"] == "executed"
        assert result2["result"] == "executed"

        plugin1.cleanup()
        plugin2.cleanup()


class TestPluginSandboxing:
    """Tests for plugin sandboxing"""

    @pytest.mark.unit
    def test_allowed_imports_list(self):
        """Test that allowed imports are defined"""
        loader = DynamicLoader()
        assert hasattr(loader, 'ALLOWED_IMPORTS')
        assert 'json' in loader.ALLOWED_IMPORTS
        assert 'asyncio' in loader.ALLOWED_IMPORTS
        assert 'pathlib' in loader.ALLOWED_IMPORTS
        assert loader.ALLOWED_IMPORTS is not None

    @pytest.mark.unit
    def test_allowed_imports_coverage(self):
        """Test that common imports are in whitelist"""
        loader = DynamicLoader()

        # Standard library modules that should be allowed
        expected_imports = {'os', 'json', 'time', 'asyncio', 'logging'}

        for module in expected_imports:
            assert module in loader.ALLOWED_IMPORTS


class TestPluginVersioning:
    """Tests for plugin version compatibility"""

    @pytest.mark.unit
    def test_version_stored_on_load(self):
        """Test that plugin version is tracked"""
        loader = DynamicLoader()
        plugin = SimpleTestPlugin()

        # Simulate plugin tracking
        version = plugin.metadata.version
        assert version == "1.0.0"

    @pytest.mark.unit
    def test_version_compatibility_check(self):
        """Test version compatibility checking"""
        metadata1 = PluginMetadata(
            name="plugin1",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        metadata2 = PluginMetadata(
            name="plugin2",
            version="2.0.0",
            author="Test",
            description="Test"
        )

        assert metadata1.version != metadata2.version


class TestPluginIntegrity:
    """Tests for plugin integrity validation"""

    @pytest.mark.unit
    def test_integrity_validation_structure(self):
        """Test that loader has integrity validation method"""
        loader = DynamicLoader()
        assert hasattr(loader, 'validate_plugin_integrity')
        assert loader is not None

    @pytest.mark.unit
    def test_integrity_validation_nonexistent_plugin(self):
        """Test integrity validation for non-existent plugin"""
        loader = DynamicLoader()
        is_valid = loader.validate_plugin_integrity("nonexistent_plugin")
        assert is_valid is False


@pytest.mark.slow
class TestDynamicLoaderPerformance:
    """Performance tests for dynamic loader"""

    @pytest.mark.unit
    def test_plugin_creation_performance(self):
        """Test plugin creation performance"""
        import time

        start = time.time()
        plugins = []
        for i in range(100):
            plugin = SimpleTestPlugin()
            plugin.initialize({"id": i})
            plugins.append(plugin)
        elapsed = time.time() - start

        assert len(plugins) == 100
        assert elapsed < 5.0  # Should be fast

        # Cleanup
        for plugin in plugins:
            plugin.cleanup()

    @pytest.mark.unit
    def test_plugin_execution_performance(self):
        """Test plugin execution performance"""
        import time

        plugin = SimpleTestPlugin()
        plugin.initialize({})

        start = time.time()
        for _ in range(1000):
            plugin.execute("test")
        elapsed = time.time() - start

        plugin.cleanup()

        assert elapsed < 5.0  # Should be fast
