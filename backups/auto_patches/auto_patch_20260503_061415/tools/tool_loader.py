"""
Dynamic Tool Loader for ULTRON Agent
Discovers and loads tools at runtime with comprehensive error handling
"""

import os
import importlib
import inspect
from typing import Dict, List, Type, Optional, Tuple, Callable
from .tool_interface import ToolInterface
from utils.error_handlers import (
    ToolError, ToolNotFoundError, FileError, ValidationError, ErrorContext,
    UltronError, ErrorCategory
)
from utils.ultron_logger import log_info, log_error, log_ai_decision

class ToolLoader:
    """Dynamic tool discovery and loading with error isolation"""

    def __init__(self, tools_dir: str = "tools") -> None:
        """
        Initialize tool loader.

        Args:
            tools_dir: Directory containing tools (default: "tools")
        """
        self.tools_dir: str = tools_dir
        self.loaded_tools: Dict[str, ToolInterface] = {}
        self.tool_classes: Dict[str, Type[ToolInterface]] = {}
        self.failed_tools: Dict[str, str] = {}

    def discover_tools(self) -> List[str]:
        """
        Discover available tool files with error handling.

        Returns:
            List[str]: Discovered tool module names

        Raises:
            FileError: If tools directory inaccessible
        """
        tool_files: List[str] = []

        try:
            # Validate directory exists
            if not os.path.exists(self.tools_dir):
                raise FileError(
                    message=f"Tools directory not found: {self.tools_dir}",
                    path=self.tools_dir,
                    operation="discover_tools"
                )

            # Validate directory is readable
            if not os.access(self.tools_dir, os.R_OK):
                raise FileError(
                    message=f"Cannot read tools directory: {self.tools_dir}",
                    path=self.tools_dir,
                    operation="discover_tools",
                    reason="Permission denied"
                )

            # Scan directory for tool files
            try:
                entries: List[str] = os.listdir(self.tools_dir)
            except OSError as e:
                raise FileError(
                    message=f"Failed listing tools directory: {e}",
                    path=self.tools_dir,
                    operation="discover_tools",
                    reason=str(e)
                )

            # Filter tool files with validation
            for filename in entries:
                if (filename.endswith("_tool.py") and
                    not filename.startswith("__") and
                    filename != "tool_interface.py"):
                    tool_files.append(filename[:-3])

            log_info(
                "tool_loader",
                f"Discovered {len(tool_files)} tool files",
                count=len(tool_files)
            )

            return tool_files

        except FileError:
            raise

        except Exception as e:
            log_error("tool_loader", f"Tool discovery failed: {e}")
            raise UltronError(
                message=f"Tool discovery failed: {str(e)}",
                category=ErrorCategory.FILE_IO
            )

    def load_tool_module(self, module_name: str) -> bool:
        """
        Load a single tool module with cascading parameter discovery.

        Attempts to instantiate tools with varying parameter combinations:
        1. No parameters
        2. With config parameter
        3. With config and memory system

        Args:
            module_name: Module name to load (without .py extension)

        Returns:
            bool: True if tool loaded successfully

        Raises:
            ToolError: If module has no valid ToolInterface classes
        """
        try:
            # Import module dynamically
            module = importlib.import_module(f"{self.tools_dir}.{module_name}")

            # Find all ToolInterface subclasses
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ToolInterface) and
                    obj != ToolInterface and
                    not inspect.isabstract(obj)):

                    # Attempt tool instantiation with cascading parameters
                    tool_instance: Optional[ToolInterface] = (
                        self._try_instantiate_tool(obj, module_name)
                    )

                    if tool_instance:
                        tool_name: str = tool_instance.name
                        self.loaded_tools[tool_name] = tool_instance
                        self.tool_classes[tool_name] = obj

                        log_info(
                            "tool_loader",
                            f"Loaded tool: {tool_name}",
                            tool_class=name,
                            module=module_name
                        )
                        return True
                    else:
                        # Tool instantiation failed - record failure
                        self.failed_tools[name] = (
                            f"Could not instantiate {name} from {module_name}"
                        )

            return False

        except ImportError as e:
            msg: str = f"Failed to import {module_name}: {e}"
            log_error("tool_loader", msg, module=module_name, error=str(e))
            raise ToolError(
                tool_name=module_name,
                command="load",
                error=e
            )

        except Exception as e:
            log_error(
                "tool_loader",
                f"Module loading error: {e}",
                module=module_name
            )
            return False

    def _try_instantiate_tool(
        self,
        tool_class: Type[ToolInterface],
        module_name: str
    ) -> Optional[ToolInterface]:
        """
        Try to instantiate tool with cascading parameters.

        Attempts:
        1. No arguments: tool_class()
        2. Config only: tool_class(config=None)
        3. Config + memory: tool_class(config=None, memory=None)

        Args:
            tool_class: Tool class to instantiate
            module_name: Module name for logging

        Returns:
            Optional[ToolInterface]: Instantiated tool or None if all failed
        """
        attempts: List[Tuple[str, Callable]] = [
            ("no_args", lambda: tool_class()),
            ("config_only", lambda: tool_class(config=None)),
            ("config_memory", lambda: tool_class(config=None, memory=None)),
        ]

        for attempt_name, attempt_func in attempts:
            try:
                tool: ToolInterface = attempt_func()

                log_info(
                    "tool_loader",
                    f"Tool instantiated via {attempt_name}",
                    tool=tool_class.__name__,
                    method=attempt_name
                )

                return tool

            except TypeError:
                # This parameter combination doesn't work, try next
                continue

            except Exception as e:
                # Unexpected error during instantiation
                log_error(
                    "tool_loader",
                    f"Instantiation error ({attempt_name}): {e}",
                    tool=tool_class.__name__,
                    method=attempt_name,
                    error=str(e)
                )
                return None

        # All attempts failed
        return None

    def load_all_tools(self, memory=None, supabase=None) -> Dict[str, ToolInterface]:
        """
        Load all discovered tools with error isolation.

        Each tool failure does not affect other tools. Failed tools
        are recorded for diagnostics.
        
        Args:
            memory: Optional memory system to share with tools
            supabase: Optional SupabaseClient to share with tools

        Returns:
            Dict[str, ToolInterface]: Successfully loaded tools

        Raises:
            FileError: If tools directory not accessible
        """
        try:
            # Set shared memory on ToolInterface base class
            if memory:
                ToolInterface.shared_memory = memory
                log_info(
                    "tool_loader",
                    "Memory system shared with tools",
                    memory_type=type(memory).__name__
                )

            # Set shared Supabase client on ToolInterface base class
            if supabase:
                ToolInterface.shared_supabase = supabase
                log_info(
                    "tool_loader",
                    "Supabase client shared with tools",
                    available=supabase.available,
                )
            
            tool_files: List[str] = self.discover_tools()

            for tool_file in tool_files:
                try:
                    self.load_tool_module(tool_file)
                except ToolError as e:
                    # Record tool failure but continue with others
                    self.failed_tools[tool_file] = str(e)
                    log_error(
                        "tool_loader",
                        f"Failed to load {tool_file}: {e.message}",
                        tool=tool_file
                    )
                except Exception as e:
                    # Unexpected error - record and continue
                    self.failed_tools[tool_file] = str(e)
                    log_error(
                        "tool_loader",
                        f"Unexpected error loading {tool_file}: {e}",
                        tool=tool_file
                    )

            log_info(
                "tool_loader",
                f"Loaded {len(self.loaded_tools)} tools total",
                successful=len(self.loaded_tools),
                failed=len(self.failed_tools),
                memory_available=memory is not None
            )

            return self.loaded_tools

        except FileError:
            raise

        except Exception as e:
            log_error("tool_loader", f"Tool loading failed: {e}")
            raise UltronError(
                message=f"Failed to load tools: {str(e)}"
            )

    def reload_tool(self, tool_name: str) -> bool:
        """
        Reload a specific tool (hot-swap) with state preservation.

        Safely reloads a tool's module and re-instantiates it,
        preserving state references.

        Args:
            tool_name: Name of tool to reload

        Returns:
            bool: True if reload successful

        Raises:
            ToolError: If tool not found or reload fails
        """
        try:
            if tool_name not in self.tool_classes:
                raise ToolNotFoundError(
                    tool_name=tool_name,
                    available_tools=list(self.tool_classes.keys())
                )

            # Get tool class and module
            tool_class: Type[ToolInterface] = self.tool_classes[tool_name]
            module_name: str = tool_class.__module__.split(".")[-1]

            # Reload module from disk
            try:
                module = importlib.reload(
                    importlib.import_module(f"{self.tools_dir}.{module_name}")
                )
            except Exception as e:
                raise ToolError(
                    tool_name=tool_name,
                    command="reload",
                    error=e
                )

            # Find and re-instantiate tool class
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ToolInterface) and
                    obj != ToolInterface and
                    not inspect.isabstract(obj)):

                    tool_instance: Optional[ToolInterface] = (
                        self._try_instantiate_tool(obj, module_name)
                    )

                    if tool_instance and tool_instance.name == tool_name:
                        self.loaded_tools[tool_name] = tool_instance
                        self.tool_classes[tool_name] = obj

                        log_info(
                            "tool_loader",
                            f"Reloaded tool: {tool_name}",
                            module=module_name
                        )
                        return True

            # Tool class not found after reload
            raise ToolError(
                tool_name=tool_name,
                command="reload",
                error=Exception("Tool class not found after reload")
            )

        except ToolError:
            raise

        except Exception as e:
            log_error(
                "tool_loader",
                f"Failed to reload {tool_name}: {e}",
                tool=tool_name
            )
            return False

    def get_tool(self, tool_name: str) -> Optional[ToolInterface]:
        """
        Get a loaded tool by name.

        Args:
            tool_name: Name of tool to retrieve

        Returns:
            Optional[ToolInterface]: Tool instance or None if not found
        """
        tool: Optional[ToolInterface] = self.loaded_tools.get(tool_name)

        if not tool:
            log_error(
                "tool_loader",
                f"Tool not found: {tool_name}",
                available=list(self.loaded_tools.keys())
            )

        return tool

    def list_tools(self) -> List[str]:
        """
        List all successfully loaded tool names.

        Returns:
            List[str]: Names of all loaded tools
        """
        return list(self.loaded_tools.keys())

    def find_matching_tool(self, command: str) -> Optional[ToolInterface]:
        """
        Find tool matching the command with error isolation.

        Tests command against each loaded tool's match() method.
        Per-tool errors don't affect other tools.

        Args:
            command: Command to match against

        Returns:
            Optional[ToolInterface]: First matching tool or None

        Raises:
            ValidationError: If command is invalid
        """
        if not command or not isinstance(command, str):
            raise ValidationError(
                message="Invalid command for tool matching",
                field="command",
                value=command,
                expected_type="non-empty string"
            )

        for tool_name, tool in self.loaded_tools.items():
            try:
                if tool.match(command):
                    log_info(
                        "tool_loader",
                        f"Found matching tool: {tool_name}",
                        tool=tool_name
                    )
                    return tool

            except Exception as e:
                # Per-tool error isolation
                log_error(
                    "tool_loader",
                    f"Error matching tool {tool_name}: {e}",
                    tool=tool_name,
                    error=str(e)
                )
                continue

        # No matching tool found
        return None



# ============================================================================
# GLOBAL TOOL LOADER INSTANCE
# ============================================================================

_tool_loader: Optional[ToolLoader] = None


def get_tool_loader(memory=None) -> ToolLoader:
    """
    Get global tool loader instance (singleton).

    Creates and initializes loader on first call, then reuses instance.
    
    Args:
        memory: Optional memory system to share with tools

    Returns:
        ToolLoader: Global tool loader instance

    Raises:
        FileError: If tools directory not accessible
        UltronError: If loader initialization fails
    """
    global _tool_loader

    if _tool_loader is None:
        try:
            _tool_loader = ToolLoader()
            _tool_loader.load_all_tools(memory=memory)

            log_info(
                "tool_loader",
                "Global tool loader initialized",
                tools_count=len(_tool_loader.loaded_tools),
                failed_count=len(_tool_loader.failed_tools),
                memory_available=memory is not None
            )

        except Exception as e:
            log_error("tool_loader", f"Failed to initialize tool loader: {e}")
            raise
    elif memory and not ToolInterface.shared_memory:
        # Update memory if provided after initialization
        ToolInterface.shared_memory = memory
        log_info("tool_loader", "Memory shared with loaded tools")

    return _tool_loader
