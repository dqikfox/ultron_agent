# Phase 3B-5 Parts 3 & 4 - Next Steps

## Current Status
- **Phase 3B**: 91% complete (4,666+ of 5,141 lines)
- **Part 2**: ✅ COMPLETE (675+ lines delivered)
- **Remaining**: 475 lines across Parts 3 & 4

## Phase 3B-5 Part 3: Integration Tools (200 lines)

### Target Tools to Enhance

#### 1. **mcp_integration_tool.py**
- Primary error type: `ConnectionError`, `TimeoutError`
- Methods to enhance: 3-4
  - `initialize_mcp_servers()`
  - `execute_mcp_tool()`
  - `list_available_tools()`
- Error scenarios:
  - MCP server connection failures
  - Tool execution timeouts
  - Invalid tool parameters
- Estimated lines: 50

#### 2. **browser_mcp_tool.py**
- Primary error type: `NetworkError`, `TimeoutError`, `ValidationError`
- Methods to enhance: 3-4
  - `navigate()`, `click()`, `extract_content()`
- Error scenarios:
  - Page load timeouts
  - Navigation failures
  - Element location failures
- Estimated lines: 50

#### 3. **aws_bedrock_tool.py**
- Primary error type: `NetworkError`, `ValidationError`, `AuthenticationError`
- Methods to enhance: 2-3
  - `call_bedrock()`, `invoke_model()`
- Error scenarios:
  - API authentication failures
  - Model invocation timeouts
  - Invalid request parameters
- Estimated lines: 40

#### 4. **database_integration_tool.py**
- Primary error type: `ConnectionError`, `ValidationError`
- Methods to enhance: 2-3
  - `connect()`, `execute_query()`
- Error scenarios:
  - Database connection failures
  - Query syntax errors
  - Invalid parameters
- Estimated lines: 40

#### 5. **Additional Integration Tools** (40 lines)
- langflow_tool.py
- github_models_tool.py
- amazon_q_integration_tool.py
- voice_aws_tool.py

### Implementation Strategy for Part 3

```python
# Pattern: External Service Integration Error Handling
with ErrorContext("service_name", logger=logger) as ctx:
    try:
        # Validate input parameters
        if not param:
            raise ValidationError(...)

        # Attempt service connection
        try:
            response = service.connect(timeout=30)
        except requests.Timeout:
            raise TimeoutError(...)
        except requests.ConnectionError:
            raise NetworkError(...)

        # Execute operation with error recovery
        result = service.execute(...)
        return result

    except (NetworkError, TimeoutError, ValidationError) as e:
        log_error(..., str(e))
        ctx.error = e
        return fallback_response()
```

**Target**: 200 lines across 5-8 integration tools

---

## Phase 3B-5 Part 4: Utility Functions (423 lines)

### Target Utilities to Enhance

#### 1. **event_system.py** (97 lines)
- Error types: `EventSystemError`, `TimeoutError`
- Methods (5):
  - `emit()` - Handle event emission failures
  - `subscribe()` - Validate event subscriptions
  - `unsubscribe()` - Safe unsubscription
  - `wait_for()` - Timeout handling for event waiting
  - `clear_all()` - Cleanup error handling
- Error scenarios:
  - Event listener failures
  - Subscription conflicts
  - Timeout waiting for events
  - Cleanup failures

#### 2. **async_tool_orchestrator.py** (75 lines)
- Error types: `AsyncError`, `TimeoutError`, `ValidationError`
- Methods (4):
  - `orchestrate_async()` - Async operation coordination
  - `gather_results()` - Result collection with timeout
  - `handle_failures()` - Cascade failure handling
  - `cleanup_async()` - Async resource cleanup
- Error scenarios:
  - Async task failures
  - Timeout in async operations
  - Race condition handling
  - Resource cleanup failures

#### 3. **auto_patch_manager.py** (108 lines)
- Error types: `PatchError`, `ValidationError`, `FileError`
- Methods (5):
  - `apply_patch()` - Patch validation and application
  - `rollback_patch()` - Safe rollback with error recovery
  - `validate_patch()` - Comprehensive patch validation
  - `generate_patch()` - Patch generation with error handling
  - `verify_applied()` - Verification with fallback
- Error scenarios:
  - Invalid patch format
  - Patch application failures
  - Rollback failures
  - File operation errors

#### 4. **model_awareness.py** (47 lines)
- Error types: `ModelConfigError`, `ValidationError`
- Methods (3):
  - `check_model_compatibility()` - Model validation
  - `get_model_context()` - Context retrieval with error handling
  - `validate_model_config()` - Configuration validation
- Error scenarios:
  - Invalid model configuration
  - Model availability issues
  - Missing required parameters

#### 5. **performance_profiler.py** (39 lines)
- Error types: `ProfilingError`, `ResourceError`
- Methods (3):
  - `profile_operation()` - Profiling with resource limits
  - `get_metrics()` - Metric retrieval with error handling
  - `cleanup_profiling()` - Resource cleanup
- Error scenarios:
  - Memory exhaustion during profiling
  - Metric collection failures
  - Resource cleanup failures

#### 6. **ultron_logger.py** (57 lines)
- Error types: `LoggingError`, `FileError`
- Methods (5):
  - `log_info()` - Enhanced logging with error handling
  - `log_error()` - Error logging with context
  - `log_ai_decision()` - AI decision logging with validation
  - `log_file_operation()` - File operation logging
  - `flush_logs()` - Flush with error recovery
- Error scenarios:
  - Log file write failures
  - Directory creation failures
  - Log rotation failures
  - Invalid log data

#### 7-8. **Additional Utilities** (100 lines)
- task_scheduler.py
- cache_manager.py
- Or other high-priority utilities

### Implementation Strategy for Part 4

```python
# Pattern: Utility Function Error Handling
def utility_function(param: str) -> Dict[str, Any]:
    """Utility with comprehensive error handling

    Args: param (str) - Input parameter
    Returns: Dict with result or error info
    Raises: ValidationError, OperationError
    """
    with ErrorContext("utility_name", logger=logger) as ctx:
        try:
            # Validate input
            if not param:
                raise ValidationError(...)

            # Perform operation
            result = perform_operation(param)

            # Return with error tracking
            return {
                'success': True,
                'result': result,
                'context': ctx.to_dict()
            }

        except ValidationError as e:
            log_error(..., str(e))
            ctx.error = e
            return {
                'success': False,
                'error': str(e),
                'context': ctx.to_dict()
            }
```

**Target**: 423 lines across 6-8 utility functions

---

## Recommended Session 15 Plan

### Session 15A: Phase 3B-5 Part 3 (200 lines)
**Duration**: 2-3 hours
**Focus**: Enhance integration tools with service-level error handling
1. Start with mcp_integration_tool.py (50 lines)
2. Continue with browser_mcp_tool.py (50 lines)
3. Add aws_bedrock_tool.py (40 lines)
4. Complete database_integration_tool.py (40 lines)
5. Quick pass on additional tools (20 lines)

**Validation Checkpoints**:
- Syntax check for each file after enhancement
- Import validation for error classes
- Integration test if time permits

### Session 15B: Phase 3B-5 Part 4 (423 lines)
**Duration**: 3-4 hours
**Focus**: Enhance utility functions with operation-level error handling
1. event_system.py (97 lines)
2. async_tool_orchestrator.py (75 lines)
3. auto_patch_manager.py (108 lines)
4. model_awareness.py (47 lines)
5. performance_profiler.py (39 lines)
6. ultron_logger.py (57 lines)

**Validation Checkpoints**:
- Full syntax check after each file
- Cross-file import validation
- Final integration test

---

## Error Class Distribution

### By File Type
- **Integration Tools**: NetworkError, TimeoutError, ValidationError (primary)
- **Utility Functions**: Specific errors (EventSystemError, PatchError, etc.) + common errors

### Error Class Review Needed
Current available in error_handlers.py:
- ✅ NetworkError
- ✅ TimeoutError
- ✅ ValidationError
- ✅ FileError
- ✅ ResourceError
- ✅ UltronError
- ✅ ErrorContext
- ❓ Need to verify additional custom errors for utilities

### Recommendation
Check `utils/error_handlers.py` for:
- EventSystemError (may need to add)
- AsyncError (may need to add)
- PatchError (may need to add)
- ModelConfigError (may need to add)
- ProfilingError (may need to add)
- LoggingError (may need to add)

If any are missing, they should be added before proceeding with Part 4.

---

## Phase 3C: Test Suite (Post Phase 3B)

After completing Phase 3B-5:
- Unit tests for error handling framework
- Integration tests for enhanced files
- End-to-end tests for error recovery
- Estimated: 1000+ lines, 6-8 hours

---

## Success Criteria

### Phase 3B-5 Part 3 (200 lines)
- ✅ 5-8 integration tools enhanced
- ✅ All service-level errors handled
- ✅ All files pass syntax/import validation
- ✅ Type hints 100% compliant
- ✅ No breaking changes

### Phase 3B-5 Part 4 (423 lines)
- ✅ 6-8 utility functions enhanced
- ✅ All operation-level errors handled
- ✅ All files pass syntax/import validation
- ✅ Type hints 100% compliant
- ✅ No breaking changes

### Phase 3B Overall (5,141 lines)
- ✅ All 6 parts complete
- ✅ 100% error framework deployment
- ✅ 500+ error handlers
- ✅ 500+ type hints
- ✅ 100% backward compatible
- ✅ Ready for Phase 3C testing

---

## Key Files to Reference

- `utils/error_handlers.py` - Error class definitions
- `tools/dynamic_code_executor.py` - Reference pattern
- `tools/pyautogui_tool.py` - GUI error handling pattern
- `tools/web_scraping_tool.py` - Network error handling pattern

---

*Session 14 - November 2, 2025*
*Recommendations for Session 15*
