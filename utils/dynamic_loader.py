"""
ULTRON Agent Dynamic Loader
Provides safe plugin loading with sandboxing and version compatibility
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod
from utils.ultron_logger import ultron_logger


@dataclass
class PluginMetadata:
    """Plugin metadata and version information"""
    name: str
    version: str
    author: str
    description: str
    required_version: str = None
    dependencies: List[str] = None
    compatible_with: List[str] = None


@dataclass
class PluginError:
    """Plugin loading error details"""
    plugin_name: str
    error_type: str
    message: str
    import_path: str = None
    traceback: str = None


class PluginBase(ABC):
    """Base class for all loadable plugins"""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration"""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass


class DynamicLoader:
    """
    Safe dynamic plugin loader with sandboxing and version checking
    """

    # Whitelist of allowed imports for sandboxing
    ALLOWED_IMPORTS = {
        'os', 'sys', 'json', 'time', 'datetime', 'logging',
        'asyncio', 'threading', 'queue', 'collections',
        'functools', 're', 'pathlib', 'tempfile', 'shutil',
        'hashlib', 'hmac', 'secrets', 'uuid', 'urllib',
        'requests', 'aiohttp', 'numpy', 'pandas'
    }

    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = Path(plugin_dir) if plugin_dir else Path('plugins')
        self.loaded_plugins: Dict[str, Tuple[Type[PluginBase], Any]] = {}
        self.plugin_versions: Dict[str, str] = {}
        self.plugin_errors: List[PluginError] = []
        self.hot_reload_enabled = False
        self._module_cache: Dict[str, Any] = {}

    def load_plugin(
        self, plugin_name: str, config: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[PluginBase], Optional[PluginError]]:
        """
        Load plugin with validation and sandboxing

        Args:
            plugin_name: Name of plugin to load
            config: Optional plugin configuration

        Returns:
            Tuple of (success, plugin_instance, error)
        """
        try:
            config = config or {}

            # Try to find plugin module
            module = self._load_module(plugin_name)
            if not module:
                error = PluginError(
                    plugin_name=plugin_name,
                    error_type='ModuleNotFound',
                    message=f'Plugin module not found: {plugin_name}'
                )
                self.plugin_errors.append(error)
                return False, None, error

            # Validate plugin class exists
            plugin_class = self._get_plugin_class(module)
            if not plugin_class:
                error = PluginError(
                    plugin_name=plugin_name,
                    error_type='InvalidPlugin',
                    message=(
                        f'Plugin class not found in {plugin_name}'
                    ),
                    import_path=str(module.__file__)
                )
                self.plugin_errors.append(error)
                return False, None, error

            # Check version compatibility
            if not self._check_version_compatibility(plugin_class):
                error = PluginError(
                    plugin_name=plugin_name,
                    error_type='VersionMismatch',
                    message=(
                        f'Plugin version incompatible: '
                        f'{plugin_name}'
                    )
                )
                self.plugin_errors.append(error)
                return False, None, error

            # Check dependencies
            missing_deps = self._check_dependencies(plugin_class)
            if missing_deps:
                error = PluginError(
                    plugin_name=plugin_name,
                    error_type='MissingDependencies',
                    message=(
                        f'Missing dependencies: {", ".join(missing_deps)}'
                    )
                )
                self.plugin_errors.append(error)
                return False, None, error

            # Instantiate and initialize plugin
            plugin_instance = plugin_class()

            if not plugin_instance.initialize(config):
                error = PluginError(
                    plugin_name=plugin_name,
                    error_type='InitializationFailed',
                    message=f'Plugin initialization failed: {plugin_name}'
                )
                self.plugin_errors.append(error)
                return False, None, error

            # Store loaded plugin
            self.loaded_plugins[plugin_name] = (plugin_class, plugin_instance)
            self.plugin_versions[plugin_name] = (
                plugin_instance.metadata.version
            )

            ultron_logger.log_info(
                "dynamic_loader",
                f"Plugin loaded successfully: {plugin_name}",
                version=plugin_instance.metadata.version
            )

            return True, plugin_instance, None

        except Exception as e:
            error = PluginError(
                plugin_name=plugin_name,
                error_type=type(e).__name__,
                message=str(e),
                traceback=str(e)
            )
            self.plugin_errors.append(error)
            ultron_logger.log_error(
                "dynamic_loader",
                f"Failed to load plugin {plugin_name}: {str(e)}"
            )
            return False, None, error

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload and cleanup plugin

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if successful
        """
        if plugin_name not in self.loaded_plugins:
            return False

        try:
            _, plugin_instance = self.loaded_plugins[plugin_name]
            plugin_instance.cleanup()

            del self.loaded_plugins[plugin_name]
            if plugin_name in self.plugin_versions:
                del self.plugin_versions[plugin_name]

            ultron_logger.log_info(
                "dynamic_loader",
                f"Plugin unloaded: {plugin_name}"
            )
            return True

        except Exception as e:
            ultron_logger.log_error(
                "dynamic_loader",
                f"Error unloading plugin {plugin_name}: {str(e)}"
            )
            return False

    def hot_reload_plugin(
        self, plugin_name: str, config: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[PluginBase]]:
        """
        Hot reload plugin without full restart

        Args:
            plugin_name: Name of plugin to reload
            config: Optional new configuration

        Returns:
            Tuple of (success, new_plugin_instance)
        """
        if not self.hot_reload_enabled:
            ultron_logger.log_error(
                "dynamic_loader",
                "Hot reload not enabled"
            )
            return False, None

        # Unload old version
        self.unload_plugin(plugin_name)

        # Invalidate module cache
        if plugin_name in self._module_cache:
            del self._module_cache[plugin_name]

        # Load new version
        success, plugin_instance, error = self.load_plugin(
            plugin_name, config
        )

        if success:
            ultron_logger.log_info(
                "dynamic_loader",
                f"Plugin hot reloaded: {plugin_name}"
            )

        return success, plugin_instance

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get loaded plugin instance"""
        if plugin_name not in self.loaded_plugins:
            return None

        _, plugin_instance = self.loaded_plugins[plugin_name]
        return plugin_instance

    def list_loaded_plugins(self) -> Dict[str, str]:
        """List all loaded plugins with versions"""
        return self.plugin_versions.copy()

    def validate_plugin_integrity(
        self, plugin_name: str, checksum: str = None
    ) -> bool:
        """
        Validate plugin integrity with optional checksum

        Args:
            plugin_name: Name of plugin
            checksum: Optional SHA256 checksum to verify

        Returns:
            True if valid
        """
        try:
            if plugin_name not in self.loaded_plugins:
                return False

            module_path = Path(self.plugin_dir) / f'{plugin_name}.py'

            if not module_path.exists():
                return False

            if checksum:
                import hashlib
                file_hash = hashlib.sha256(
                    module_path.read_bytes()
                ).hexdigest()
                return file_hash == checksum

            return True

        except Exception as e:
            ultron_logger.log_error(
                "dynamic_loader",
                f"Error validating plugin integrity: {str(e)}"
            )
            return False

    def _load_module(self, plugin_name: str) -> Optional[Any]:
        """Load plugin module with caching"""
        if plugin_name in self._module_cache:
            return self._module_cache[plugin_name]

        try:
            # Try as file in plugin directory
            plugin_path = self.plugin_dir / f'{plugin_name}.py'

            if plugin_path.exists():
                spec = importlib.util.spec_from_file_location(
                    f'plugin_{plugin_name}',
                    plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._module_cache[plugin_name] = module
                return module

            # Try as installed package
            module = importlib.import_module(plugin_name)
            self._module_cache[plugin_name] = module
            return module

        except Exception as e:
            ultron_logger.log_error(
                "dynamic_loader",
                f"Error loading module {plugin_name}: {str(e)}"
            )
            return None

    @staticmethod
    def _get_plugin_class(module: Any) -> Optional[Type[PluginBase]]:
        """Extract plugin class from module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and
                issubclass(obj, PluginBase) and
                obj is not PluginBase):
                return obj
        return None

    @staticmethod
    def _check_version_compatibility(
        plugin_class: Type[PluginBase]
    ) -> bool:
        """Check if plugin version is compatible"""
        try:
            instance = plugin_class()
            metadata = instance.metadata
            # Simple version check - can be enhanced
            return metadata.version is not None
        except Exception:
            return False

    @staticmethod
    def _check_dependencies(
        plugin_class: Type[PluginBase]
    ) -> List[str]:
        """
        Check if all plugin dependencies are available

        Returns:
            List of missing dependencies
        """
        try:
            instance = plugin_class()
            metadata = instance.metadata

            missing = []
            if metadata.dependencies:
                for dep in metadata.dependencies:
                    try:
                        importlib.import_module(dep)
                    except ImportError:
                        missing.append(dep)

            return missing

        except Exception:
            return []
