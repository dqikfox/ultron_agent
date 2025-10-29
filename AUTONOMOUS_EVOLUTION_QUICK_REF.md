# Autonomous Evolution - Quick Reference

## Quick Start

```python
# Start autonomous evolution
agent.execute_command("evolution start")

# Check status
agent.execute_command("evolution status")

# Stop evolution
agent.execute_command("evolution stop")
```

## Commands

| Command | Description |
|---------|-------------|
| `evolution start` | Start autonomous improvement mode |
| `evolution stop` | Stop autonomous improvement mode |
| `evolution status` | Show current status and stats |
| `manual cycle` | Run a single cycle immediately |
| `evolution history` | View improvement history |

## Configuration

```json
{
  "autonomous_evolution": {
    "enabled": false,
    "cycle_interval": 1800,
    "max_improvements_per_cycle": 3,
    "safety_mode": true
  }
}
```

## Improvement Areas (Priority Order)

1. **Security** (10) - Input validation, auth, secrets
2. **Performance** (9) - Optimization, memory, caching
3. **Error Handling** (8) - Exceptions, recovery, logging
4. **New Features** (7) - User features, integrations
5. **User Experience** (7) - GUI, voice, usability
6. **Testing** (6) - Coverage, edge cases, integration
7. **Code Quality** (6) - Refactoring, patterns, cleanup
8. **Integration** (5) - AI models, services, APIs
9. **Monitoring** (5) - Metrics, health, diagnostics
10. **Documentation** (4) - Docstrings, guides, examples

## Safety Features

- ✅ **Safety Mode**: Changes simulated by default
- ✅ **Rollback**: Automatic on validation failure
- ✅ **Validation**: Config, imports, tools checked
- ✅ **Rate Limiting**: Max 3 improvements per cycle
- ✅ **Audit Trail**: All actions logged

## Log Files

- `logs/autonomous_improvements.log` - All improvements
- `data/autonomous_evolution_state.json` - State/history
- `logs/ai_activities.log` - AI decisions

## Metrics

```python
# View statistics
stats = tool._get_cycle_statistics()
# Returns: total_cycles, successful_improvements, 
#          failed_attempts, success_rate, uptime
```

## Example Output

```
✅ Autonomous Evolution Mode ACTIVATED

ULTRON will now continuously:
- Analyze the project for improvement opportunities
- Generate enhancement proposals
- Validate and test improvements
- Safely implement changes with rollback capability
- Track improvement metrics

Cycle Interval: 30 minutes
Safety Mode: Enabled
Max Improvements per Cycle: 3
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Loop not starting | Check event loop, try `manual cycle` |
| No improvements | Verify brain connection, check logs |
| Validation failures | Test individual validators |
| State corruption | Backup and reset state file |

## Best Practices

1. ⚠️ Always use safety mode in production
2. 📊 Monitor logs regularly
3. 📝 Review simulated improvements
4. 🔄 Start conservatively (30-min cycles)
5. ✅ Validate before disabling safety mode

## Advanced Usage

```python
# Customize improvement areas
tool.improvement_areas = ["security", "performance"]

# Adjust cycle interval (1 hour)
tool.cycle_interval = 3600

# Disable safety mode (⚠️ caution!)
tool.safety_mode = False
```

## Integration

```python
# Auto-discover and start with agent
from tools.autonomous_evolution_tool import AutonomousEvolutionTool

tool = AutonomousEvolutionTool(config=config, brain=brain)
if config.autonomous_evolution.enabled:
    tool.execute("evolution start")
```

## Support

- Docs: `AUTONOMOUS_EVOLUTION_GUIDE.md`
- Tests: `tests/test_autonomous_evolution_tool.py`
- Code: `tools/autonomous_evolution_tool.py`
