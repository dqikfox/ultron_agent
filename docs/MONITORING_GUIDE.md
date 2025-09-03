# ULTRON Agent Monitoring & Observability Guide

## Overview

The ULTRON Agent includes comprehensive monitoring and observability features designed for production deployments, development debugging, and performance optimization. This guide covers the enhanced monitoring capabilities implemented to track usage patterns, performance metrics, and system health.

## Features

### 1. Health Monitoring

#### Health Endpoints
- **`/healthz`** - Basic health check for load balancers (always fast)
- **`/readyz`** - Comprehensive readiness check with dependency validation
- **`/metrics`** - Prometheus-compatible metrics endpoint

#### Component Health Checks
- **Voice System** - TTS/STT availability and configuration
- **Ollama** - AI model server connectivity and status  
- **GUI** - User interface subsystem availability
- **System Resources** - CPU, memory, disk usage with thresholds

### 2. System Metrics

#### Resource Monitoring
```prometheus
# CPU, memory, and disk usage
ultron_cpu_percent
ultron_memory_percent
ultron_memory_used_bytes
ultron_disk_percent

# GPU metrics (if available)
ultron_gpu_percent
ultron_gpu_memory_percent
ultron_gpu_temperature_celsius
```

#### Component Health Status
```prometheus
# Component health (1=healthy, 0=unhealthy)
ultron_component_health{component="voice"}
ultron_component_health{component="ollama"}
ultron_component_health{component="gui"}
ultron_component_health{component="system"}
```

### 3. Usage & Performance Metrics

#### Command Execution Tracking
```prometheus
# Total commands executed
ultron_commands_total

# Command execution errors
ultron_command_errors_total

# Error rate percentage
ultron_error_rate
```

#### Response Time Analysis
```prometheus
# Average response time
ultron_response_time_seconds

# Performance percentiles
ultron_response_time_p95_seconds
ultron_response_time_p99_seconds
```

#### Feature Usage Statistics
```prometheus
# Voice command usage
ultron_voice_commands_total

# GUI interaction tracking  
ultron_gui_interactions_total

# API request metrics
ultron_api_requests_total
ultron_api_errors_total

# Session tracking
ultron_sessions_total
```

### 4. Custom Metrics

The monitoring system supports custom business logic metrics:

```python
from ultron_agent.health import get_health_checker

health = get_health_checker()

# Set custom metrics
health.set_custom_metric("custom_workflow_count", 42)
health.set_custom_metric("processing_queue_size", queue.size())

# Record specific events
health.record_command_execution("my_command", 0.5, success=True)
health.record_voice_command()
health.record_gui_interaction()
```

## Structured Logging

### JSON Log Format
```json
{
  "timestamp": "2025-09-03T16:42:36.219782",
  "name": "ultron.health",
  "levelname": "INFO", 
  "message": "Command executed: test_command",
  "correlation_id": "7c24e5ab",
  "source": "core",
  "command": "test_command",
  "execution_time_ms": 500,
  "success": true
}
```

### Log Correlation
- **Correlation IDs** - Track related log entries across components
- **Source Tagging** - Identify log origin (gui|api|voice|core)
- **Context Managers** - Automatic correlation for operations
- **Performance Tracking** - Built-in duration logging

### Log Configuration
```python
from ultron_agent.logging_config import setup_logging, LogContext

# Initialize structured logging
setup_logging(
    log_level="INFO",
    enable_json=True,
    enable_console=True
)

# Use context for correlated logging
with LogContext("user_command", command="example") as ctx:
    ctx.log("Processing started")
    # ... do work ...
    ctx.log("Processing completed")
```

## Integration Examples

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ultron-agent'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Grafana Dashboard

Import the provided dashboard configuration from `docs/grafana-dashboard.json` or create custom dashboards using these key metrics:

**Performance Dashboard:**
- Response time percentiles: `ultron_response_time_p95_seconds`
- Error rate: `ultron_error_rate`
- Request rate: `rate(ultron_commands_total[5m])`

**System Health Dashboard:**
- Component status: `ultron_component_health`
- Resource usage: `ultron_cpu_percent`, `ultron_memory_percent`
- GPU metrics: `ultron_gpu_percent`, `ultron_gpu_temperature_celsius`

**Usage Analytics:**
- Feature adoption: `ultron_voice_commands_total`, `ultron_gui_interactions_total`
- Session analytics: `ultron_sessions_total`
- API usage: `rate(ultron_api_requests_total[5m])`

### Alert Rules

Example Prometheus alerting rules:

```yaml
groups:
  - name: ultron_agent_alerts
    rules:
      - alert: UltronAgentDown
        expr: up{job="ultron-agent"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ULTRON Agent is down"
          
      - alert: UltronHighErrorRate
        expr: ultron_error_rate > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ULTRON Agent error rate is high: {{ $value }}%"
          
      - alert: UltronComponentUnhealthy
        expr: ultron_component_health{component!="gui"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "ULTRON Agent component {{ $labels.component }} is unhealthy"
```

## Development Usage

### Testing Monitoring Features

Run the monitoring demonstration:
```bash
python monitoring_demo.py
```

### Manual Testing
```python
import asyncio
from ultron_agent.health import get_health_checker

async def test_monitoring():
    health = get_health_checker()
    
    # Simulate some activity
    health.record_command_execution("test", 0.1, success=True)
    health.record_voice_command()
    health.set_custom_metric("test_metric", 42)
    
    # Get metrics
    metrics = await health.get_metrics()
    print(metrics["body"])

asyncio.run(test_monitoring())
```

### API Testing
```bash
# Health check
curl http://localhost:8000/healthz

# Readiness check  
curl http://localhost:8000/readyz

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Production Deployment

### Monitoring Stack Setup

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboards
3. **AlertManager** - Alert routing and management
4. **Log Aggregation** - ELK Stack or similar for structured logs

### Configuration

#### Environment Variables
```bash
# Logging configuration
ULTRON_LOG_LEVEL=INFO
ULTRON_LOG_JSON=true
ULTRON_LOG_CONSOLE=false

# Health check intervals
ULTRON_HEALTH_CHECK_INTERVAL=30
```

#### Docker Compose Example
```yaml
version: '3.8'
services:
  ultron-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ULTRON_LOG_JSON=true
      - ULTRON_LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./dashboards:/etc/grafana/provisioning/dashboards
```

### Performance Considerations

- **Metrics Retention** - Response time history limited to 1000 entries
- **Log Rotation** - Automatic rotation at 10MB with 5 backup files
- **Health Check Caching** - Component health cached to reduce overhead
- **Async Operations** - Non-blocking metrics collection

## Troubleshooting

### Common Issues

**High Memory Usage:**
- Check `ultron_memory_percent` metric
- Review log retention settings
- Monitor metrics history size

**Missing GPU Metrics:**
- Verify GPU drivers and GPUtil installation
- Check component health for GPU availability

**Health Check Failures:**
- Review `/readyz` endpoint for detailed component status
- Check individual component health in metrics
- Verify Ollama service availability

### Debug Mode
```python
# Enable debug logging for monitoring
setup_logging(log_level="DEBUG")

# Check specific component health
health = get_health_checker()
components = await health._check_all_components()
for comp in components:
    print(f"{comp.name}: {comp.status} - {comp.message}")
```

## Security Considerations

- **API Keys** - Never logged in structured logs (automatic sanitization)
- **Sensitive Data** - Custom metrics should not contain secrets
- **Access Control** - Consider authentication for metrics endpoints in production
- **Log Access** - Restrict access to log files containing correlation data

## Contributing

To extend monitoring capabilities:

1. Add custom metrics via `health.set_custom_metric()`
2. Create custom health checks with `health.register_check()`
3. Extend Prometheus metrics in `health.get_metrics()`
4. Add structured logging contexts for new operations

For questions or contributions, see the main project documentation.