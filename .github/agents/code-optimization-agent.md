# ULTRON Code Optimization Agent

Specialized agent for code quality improvements, performance optimization, and technical debt reduction.

## Focus Areas

### Performance Optimization

- Brain.py async/await patterns
- Tool discovery and loading efficiency
- Event system message routing
- Memory management in long-running services
- Response caching strategies

### Code Quality

- Type hint coverage improvements
- Error handling patterns
- Logging consistency
- Documentation generation
- Test coverage gaps

### Architecture Improvements

- Service decoupling
- Event system optimization
- Tool interface enhancements
- Configuration management
- Dependency injection patterns

## Key Files to Optimize

- **agent_core.py** (917 lines) - Tool discovery, lifecycle management
- **brain.py** (1017 lines) - AI reasoning, async operations
- **api_server.py** (246 lines) - REST API endpoints
- **web_gui_server.py** (1036 lines) - Web interface server
- **utils/ultron_logger.py** - Centralized logging
- **utils/event_system.py** - Event bus coordination

## Optimization Patterns

### Pattern 1: Async/Await Consolidation

Look for sync wrappers that block async operations. Convert to pure async pipelines where possible.

```python
# Before: sync wrapper blocks async
def start_gui(self):
    asyncio.run(self.gui.run_gui())

# After: async all the way
async def start_gui(self):
    await self.gui.run_gui()
```

### Pattern 2: Tool Discovery Caching

Cache tool schemas and metadata to avoid repeated filesystem scans.

```python
# Add to agent_core.py
self._tool_cache = {}
self._cache_timestamp = 0
```

### Pattern 3: Event System Batching

Batch event emissions for high-frequency operations to reduce message overhead.

### Pattern 4: Connection Pooling

Implement connection pools for Ollama, PostgreSQL, and other services.

## Analysis Tasks

When delegating, use prompts like:

```
Analyze agent_core.py for performance bottlenecks:
1. Tool discovery O(n) scans - suggest caching strategy
2. Async vs sync blocking - identify improvement opportunities
3. Exception handling - suggest structured error categorization
4. Logging overhead - suggest sampling for high-frequency operations
```

## Measurement Approach

1. **Baseline Metrics**: Use performance_profiler.py to establish baseline
2. **Targeted Optimization**: Focus on top 20% of execution time
3. **Validation**: Compare before/after metrics with benchmarks
4. **Regression Testing**: Ensure optimizations don't break functionality

## Integration with Auto-Run

These optimizations should integrate with the `auto_run` feature in `ultron_config.json`:

```json
"auto_run": {
  "enabled": true,
  "startup_commands": [
    "optimize performance",
    "analyze code quality",
    "suggest improvements"
  ]
}
```

## Related Documentation

- `.github/agents/ultron-automation-agent.md` - Main automation agent
- `.github/copilot-instructions.md` - Architecture reference
- `DEVELOPER_QUICK_REFERENCE.md` - Development patterns

---

**Last Updated**: October 30, 2025
