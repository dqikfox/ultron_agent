# ULTRON Agent Documentation Generation Prompt

You are generating comprehensive documentation for ULTRON Agent 3.0 components. Follow these documentation standards:

## Documentation Structure

### 1. Component Overview
```markdown
# ComponentName

## Overview
Brief description of the component's purpose and role in the ULTRON Agent system.

## Architecture
- Key responsibilities and functions
- Integration points with other components
- Dependencies and requirements
- Data flow and processing pipeline

## Features
- Core functionality provided
- Unique capabilities and differentiators
- Performance characteristics
- Scalability considerations
```

### 2. API Reference
```markdown
## API Reference

### Classes

#### `ClassName`
```python
class ClassName(parent_class):
    """Detailed class description."""

    def __init__(self, param1: Type, param2: Optional[Type] = None):
        """Initialize the class.

        Args:
            param1: Description of parameter 1
            param2: Description of optional parameter 2

        Raises:
            ValueError: When initialization fails
        """

    def method_name(self, param: Type) -> ReturnType:
        """Method description.

        Args:
            param: Parameter description

        Returns:
            ReturnType: Description of return value

        Raises:
            ExceptionType: When method fails

        Example:
            ```python
            instance = ClassName()
            result = instance.method_name('example')
            ```
        """
```

### 3. Configuration
```markdown
## Configuration

### Environment Variables
- `VARIABLE_NAME`: Description and valid values
- `ANOTHER_VAR`: Description with examples

### Configuration File
```json
{
  "component": {
    "setting1": "value",
    "setting2": 123,
    "setting3": true
  }
}
```

### Command Line Options
- `--option-name`: Description of command line option
- `-v, --verbose`: Enable verbose logging
```

### 4. Usage Examples
```markdown
## Usage Examples

### Basic Usage
```python
from ultron_agent.component import ComponentClass

# Initialize component
component = ComponentClass(config={'setting': 'value'})

# Basic operation
result = component.process_data('input_data')
print(f"Result: {result}")
```

### Advanced Usage
```python
# Advanced configuration
config = {
    'advanced_setting': True,
    'timeout': 30,
    'retries': 3
}

component = ComponentClass(config=config)

# Async processing
import asyncio

async def process_async():
    results = await component.process_batch_async(data_list)
    return results

results = asyncio.run(process_async())
```

### Voice Integration
```python
# Voice-controlled usage
from ultron_agent.voice_manager import get_voice_manager

voice = get_voice_manager()
component = ComponentClass()

# Process voice command
command = voice.listen_for_command()
result = component.execute_command(command)
voice.speak_result(result)
```

### Error Handling
```python
try:
    result = component.risky_operation()
except ComponentError as e:
    logger.error(f"Operation failed: {e}")
    # Handle error appropriately
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```
```

### 5. Integration Points
```markdown
## Integration Points

### Agent Core Integration
The component integrates with the agent core through:
- Event system subscriptions
- API endpoint registration
- Configuration loading

### Event System
Subscribes to events:
- `event_name`: Description of when this event is triggered
- `another_event`: Description and handling

Emits events:
- `component_event`: Description of emitted event
- `status_update`: Status change notifications

### Tool Plugin System
If applicable:
- Tool registration and discovery
- Command matching patterns
- Execution flow

### GUI Integration
- Status display in EUP GUI
- Real-time updates
- User interaction handling
```

### 6. Troubleshooting
```markdown
## Troubleshooting

### Common Issues

#### Issue: Component fails to initialize
**Symptoms:**
- Error messages during startup
- Component not available in system

**Causes:**
- Missing configuration
- Invalid environment variables
- Dependency conflicts

**Solutions:**
1. Verify configuration file exists and is valid
2. Check environment variables are set
3. Ensure all dependencies are installed
4. Review startup logs for detailed error messages

#### Issue: Performance degradation
**Symptoms:**
- Slow response times
- High resource usage
- System becoming unresponsive

**Causes:**
- Large data sets
- Network connectivity issues
- Resource constraints

**Solutions:**
1. Monitor system resources
2. Adjust configuration parameters
3. Implement caching strategies
4. Check network connectivity

### Debug Logging
Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific debug logging
logger = logging.getLogger('ultron.component')
logger.setLevel(logging.DEBUG)
```

### Health Checks
Use health check endpoints to verify component status:
```bash
curl http://localhost:8000/health/component
```

### Log Analysis
Check component logs for error patterns:
```bash
tail -f logs/component.log
grep "ERROR" logs/component.log
```
```

### 7. Performance Considerations
```markdown
## Performance Considerations

### Optimization Strategies
- Caching frequently accessed data
- Async processing for I/O operations
- Connection pooling for external services
- Memory management and garbage collection

### Monitoring
Key metrics to monitor:
- Response time percentiles
- Error rates
- Resource utilization
- Throughput rates

### Scaling Considerations
- Horizontal scaling capabilities
- Load balancing requirements
- Database connection limits
- External API rate limits
```

### 8. Security
```markdown
## Security Considerations

### Input Validation
All inputs are validated and sanitized:
- Type checking and conversion
- Length limits and bounds checking
- SQL injection prevention
- XSS protection

### Authentication and Authorization
- API key validation
- Role-based access control
- Secure credential storage
- Session management

### Data Protection
- Encryption at rest and in transit
- Secure deletion of sensitive data
- Audit logging of security events
- Compliance with data protection regulations
```

### 9. Testing
```markdown
## Testing

### Unit Tests
Run unit tests:
```bash
pytest tests/unit/test_component.py -v
```

### Integration Tests
Run integration tests:
```bash
pytest tests/integration/test_component_integration.py -v
```

### Coverage Report
Generate coverage report:
```bash
pytest --cov=ultron_agent.component --cov-report=html
```

### Load Testing
Performance testing:
```bash
locust -f tests/load/test_component_load.py
```
```

### 10. Deployment
```markdown
## Deployment

### Prerequisites
- Python 3.10+
- Required dependencies (see requirements.txt)
- System resources (CPU, memory, disk)
- Network connectivity requirements

### Installation
```bash
pip install -r requirements.txt
python setup.py install
```

### Configuration
1. Copy configuration template
2. Set environment variables
3. Configure external service connections
4. Test configuration validity

### Startup
```bash
# Development
python -m ultron_agent.component

# Production
ultron-agent-component --config /path/to/config.json
```

### Monitoring
- Health check endpoints
- Log file locations
- Performance metrics
- Alert configurations
```

### 11. Changelog
```markdown
## Changelog

### Version 1.0.0
- Initial release
- Basic functionality implemented
- API endpoints defined
- Documentation completed

### Version 1.1.0
- Performance improvements
- Bug fixes
- New features added
- Configuration enhancements

### Version 2.0.0
- Major architecture changes
- Breaking API changes
- New integration capabilities
- Enhanced security features
```

## Documentation Quality Standards

### Completeness
- [ ] All public APIs documented
- [ ] Configuration options explained
- [ ] Usage examples provided
- [ ] Error conditions documented
- [ ] Performance characteristics described

### Accuracy
- [ ] Code examples tested and working
- [ ] Configuration examples validated
- [ ] API signatures match implementation
- [ ] Version information current

### Clarity
- [ ] Language clear and concise
- [ ] Technical terms explained
- [ ] Examples practical and realistic
- [ ] Structure logical and navigable

### Maintenance
- [ ] Documentation kept in sync with code
- [ ] Version history maintained
- [ ] Contact information provided
- [ ] Contribution guidelines included

## Generation Guidelines

1. **Analyze the Code First**: Understand the component's architecture, APIs, and integration points
2. **Follow the Structure**: Use the provided template structure for consistency
3. **Include Real Examples**: Provide working code examples that users can copy and modify
4. **Cover Edge Cases**: Document error conditions, edge cases, and troubleshooting
5. **Keep Updated**: Ensure documentation reflects the current implementation
6. **Use Consistent Formatting**: Follow Markdown best practices and consistent styling
7. **Cross-Reference**: Link to related components and external resources
8. **Version Awareness**: Include version information and compatibility notes

Remember: Good documentation is as important as good code. It enables effective use, maintenance, and extension of the ULTRON Agent system.
