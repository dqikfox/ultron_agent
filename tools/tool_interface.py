"""
Standardized Tool Interface for ULTRON Agent
Provides abstract base class with comprehensive error handling for all tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from diagnostics import diagnostic_wrapper
from utils.error_handlers import (
    ToolError, ValidationError, ResourceError, ErrorContext
)
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.circuit_breaker import get_circuit_breaker, CircuitOpenError


class ToolInterface(ABC):
    """Abstract base class for all ULTRON Agent tools"""
    
    # Class variable for optional memory system (set by tool_loader when available)
    shared_memory = None
    # Class variable for optional Supabase client (set by agent_core when available)
    shared_supabase = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    def memory(self):
        """Get access to shared agent memory for context-aware tool execution."""
        return self.__class__.shared_memory

    @property
    def supabase(self):
        """Get access to shared Supabase client for persistence."""
        return self.__class__.shared_supabase

    @abstractmethod
    def match(self, command: str) -> bool:
        """
        Check if command matches this tool.

        Args:
            command: Command string to evaluate

        Returns:
            bool: True if command should route to this tool

        Raises:
            ToolError: If matching logic fails
        """
        pass

    @abstractmethod
    def execute(self, command: str, **kwargs) -> str:
        """
        Execute tool operation with error handling.

        Args:
            command: Command to execute
            **kwargs: Additional parameters (may include 'memory' for context)

        Returns:
            str: Execution result or error message

        Raises:
            ValidationError: If input validation fails
            ResourceError: If required resources unavailable
            ToolError: If execution fails

        NOTE: For automatic crash tracking, decorate with:
        @diagnostic_wrapper("tool_name", track_performance=True)
        
        NOTE: Tools can now access shared memory via:
        - self.memory property
        - kwargs.get('memory') parameter
        - For context-aware execution that learns from past
        """
        pass

    @classmethod
    @abstractmethod
    def schema(cls) -> Dict[str, Any]:
        """
        Return tool schema for registration.

        Returns:
            Dict with structure:
            {
                "name": "tool_name",
                "description": "tool description",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }

        Raises:
            ValidationError: If schema is invalid
        """
        pass

    def self_test(self) -> Dict[str, Any]:
        """
        Run a basic self-diagnostic for the tool.

        Returns:
            Dict: Diagnostic results (status, message, errors)
        """
        result = {
            "tool": self.name,
            "status": "ok",
            "message": "Self-test passed (default implementation)",
            "errors": []
        }
        try:
            # Optionally, subclasses can override for deeper checks
            _ = self.match("diagnostic_test")
            _ = self.schema()
        except Exception as e:
            result["status"] = "fail"
            result["message"] = f"Self-test failed: {e}"
            result["errors"].append(str(e))
        return result

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get tool metadata with validation.

        Returns:
            Dict: Tool metadata with name, description, schema

        Raises:
            ToolError: If metadata retrieval fails
        """
        context: ErrorContext = ErrorContext("tool_interface", "get_metadata")

        try:
            # Validate basic properties
            name: str = self.name
            description: str = self.description

            if not name or not isinstance(name, str):
                raise ValidationError("name", "non-empty string", type(name))
            if not description or not isinstance(description, str):
                raise ValidationError(
                    "description", "non-empty string", type(description)
                )

            # Get and validate schema
            schema: Dict[str, Any] = self.schema()

            if not isinstance(schema, dict):
                raise ValidationError("schema", "dict", type(schema))

            required_schema_keys: List[str] = ["name", "description"]
            for key in required_schema_keys:
                if key not in schema:
                    raise ValidationError(
                        f"schema.{key}", "required", "missing"
                    )

            # Return validated metadata
            metadata: Dict[str, Any] = {
                "name": name,
                "description": description,
                "schema": schema
            }

            log_info(
                "tool_interface",
                f"Generated metadata for tool: {name}",
                tool_name=name
            )

            return metadata

        except ValidationError as e:
            log_error(
                "tool_interface",
                f"Schema validation failed: {e.message}",
                field=e.field
            )
            raise ToolError(f"Invalid tool schema: {e.message}")

        except Exception as e:
            log_error(
                "tool_interface",
                f"Metadata retrieval failed: {e}"
            )
            raise ToolError(f"Failed to get metadata: {str(e)}")

        finally:
            context.end()

    def execute_safe(
        self,
        command: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        **kwargs,
    ) -> str:
        """
        Execute the tool with automatic circuit-breaker protection.

        The circuit breaker is keyed on the tool name, so repeated failures
        cause the circuit to OPEN and prevent further calls until the
        recovery window elapses — protecting the rest of the system from a
        malfunctioning or unreachable tool.

        Args:
            command: Command string passed to ``execute()``.
            failure_threshold: Failures before the circuit opens (default 5).
            recovery_timeout: Seconds to wait before attempting recovery (default 60).
            **kwargs: Extra keyword arguments forwarded to ``execute()``.

        Returns:
            str: Result from ``execute()``.

        Raises:
            CircuitOpenError: When the circuit is open and recovery has not started.
            ToolError / any exception: Propagated from ``execute()`` on failure.
        """
        cb = get_circuit_breaker(
            name=f"tool:{self.name}",
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
        try:
            return cb.call_sync(self.execute, command, **kwargs)
        except CircuitOpenError:
            log_error(
                "tool_interface",
                f"Circuit open for tool '{self.name}' — call rejected",
                tool=self.name,
            )
            raise
        except Exception as exc:
            log_error(
                "tool_interface",
                f"execute_safe caught exception from '{self.name}': {exc}",
                tool=self.name,
            )
            raise

    async def execute_safe_async(
        self,
        command: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        **kwargs,
    ) -> str:
        """
        Async version of ``execute_safe``.

        Use this when the tool's ``execute`` implementation is a coroutine
        or when the caller is already in an async context.
        """
        import asyncio

        cb = get_circuit_breaker(
            name=f"tool:{self.name}",
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )

        async def _run():
            if asyncio.iscoroutinefunction(self.execute):
                return await self.execute(command, **kwargs)
            return self.execute(command, **kwargs)

        try:
            return await cb.call(_run)
        except CircuitOpenError:
            log_error(
                "tool_interface",
                f"Circuit open for tool '{self.name}' — async call rejected",
                tool=self.name,
            )
            raise
        except Exception as exc:
            log_error(
                "tool_interface",
                f"execute_safe_async caught exception from '{self.name}': {exc}",
                tool=self.name,
            )
            raise

    def get_circuit_stats(self) -> Dict[str, Any]:
        """Return circuit-breaker statistics for this tool."""
        cb = get_circuit_breaker(name=f"tool:{self.name}")
        return cb.get_stats()

