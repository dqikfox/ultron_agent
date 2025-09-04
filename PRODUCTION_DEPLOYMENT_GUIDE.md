# ULTRON Agent 3.0 - Production Deployment Guide

## 🚀 Complete Production Deployment Documentation

This guide provides comprehensive instructions for deploying ULTRON Agent 3.0 in production environments with enterprise-grade security, monitoring, and reliability.

## 📋 Prerequisites

### System Requirements

#### Hardware Requirements
- **CPU**: 4+ cores (8+ recommended for AI workloads)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 20GB free space (SSD recommended)
- **Network**: Stable internet connection for AI API access

#### Operating System Support
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **Windows**: Windows 10/11, Windows Server 2019+
- **macOS**: macOS 11+ (development only)

#### Software Requirements
- **Python**: 3.10 or higher (3.11 recommended)
- **Git**: Latest version for repository management
- **OpenSSL**: For encryption and SSL/TLS support

### Optional Dependencies
- **Docker**: For containerized deployments
- **NVIDIA Drivers**: For GPU acceleration (CUDA 11.8+)
- **Ollama**: For local LLM execution
- **Redis**: For advanced caching (optional)

## 🛠️ Installation Methods

### Method 1: Automated Production Deployment (Recommended)

The automated deployment script handles all aspects of production deployment:

```bash
# 1. Clone the repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# 2. Run the production deployment script
python deploy_production.py

# 3. Follow the interactive prompts
# The script will:
# - Validate prerequisites
# - Create automatic backups
# - Deploy files securely
# - Install dependencies
# - Configure services
# - Validate deployment
```

#### Deployment Script Options

```bash
# Custom deployment directory
python deploy_production.py --target /opt/ultron

# Skip backup creation (not recommended)
python deploy_production.py --no-backup

# Force deployment without prompts (for automation)
python deploy_production.py --force

# Help and options
python deploy_production.py --help
```

### Method 2: Manual Production Deployment

For environments requiring manual control:

#### Step 1: Environment Preparation

```bash
# Create deployment directory
sudo mkdir -p /opt/ultron
sudo chown $USER:$USER /opt/ultron
cd /opt/ultron

# Download and extract
wget https://github.com/dqikfox/ultron_agent/archive/main.zip
unzip main.zip
mv ultron_agent-main/* .
rm -rf ultron_agent-main main.zip
```

#### Step 2: Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements-prod.txt
```

#### Step 3: Configuration

```bash
# Copy example configuration
cp ultron_config.json.example ultron_config_prod.json

# Edit configuration for production
nano ultron_config_prod.json
```

#### Step 4: Environment Variables

```bash
# Create environment file
cat > .env << EOF
ULTRON_ENV=production
ULTRON_SECRET_KEY=$(openssl rand -hex 32)
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-key
OLLAMA_HOST=localhost:11434
LOG_LEVEL=INFO
EOF

# Secure the environment file
chmod 600 .env
```

#### Step 5: Service Setup

**Linux (systemd):**

```bash
# Create systemd service
sudo tee /etc/systemd/system/ultron.service << EOF
[Unit]
Description=ULTRON Agent 3.0
After=network.target

[Service]
Type=simple
User=ultron
Group=ultron
WorkingDirectory=/opt/ultron
ExecStart=/opt/ultron/venv/bin/python main.py
Restart=always
RestartSec=5
Environment=ULTRON_ENV=production
EnvironmentFile=/opt/ultron/.env

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ultron
sudo systemctl start ultron
```

**Windows:**

```batch
@echo off
REM ULTRON Agent Production Service
cd /d "%~dp0"
set ULTRON_ENV=production
python main.py
```

### Method 3: Docker Deployment

Create a Docker deployment:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 ultron && chown -R ultron:ultron /app
USER ultron

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  ultron-agent:
    build: .
    ports:
      - "8080:8080"
      - "9090:9090"  # Monitoring
    environment:
      - ULTRON_ENV=production
      - ULTRON_SECRET_KEY=${ULTRON_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  monitoring:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
```

## 🔒 Security Configuration

### SSL/TLS Configuration

```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure HTTPS in ultron_config_prod.json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "ssl_keyfile": "key.pem",
    "ssl_certfile": "cert.pem"
  }
}
```

### Firewall Configuration

```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp  # API port
sudo ufw allow 9090/tcp  # Monitoring port
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --add-port=9090/tcp --permanent
sudo firewall-cmd --reload
```

### API Security

```json
{
  "security": {
    "api_key_required": true,
    "rate_limiting": {
      "requests_per_minute": 100,
      "burst_size": 10
    },
    "cors": {
      "allowed_origins": ["https://yourdomain.com"],
      "allowed_methods": ["GET", "POST"],
      "allowed_headers": ["Authorization", "Content-Type"]
    }
  }
}
```

## 📊 Monitoring & Observability

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8080/health

# Detailed health with components
curl http://localhost:8080/health/detailed

# Prometheus metrics
curl http://localhost:8080/metrics

# System metrics
curl http://localhost:8080/api/v1/system/metrics
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ultron-agent'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 10s
    metrics_path: /metrics

rule_files:
  - "alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Alert Rules

```yaml
# alerts.yml
groups:
  - name: ultron-agent
    rules:
      - alert: UltronAgentDown
        expr: up{job="ultron-agent"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ULTRON Agent is down"
          
      - alert: HighCPUUsage
        expr: ultron_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          
      - alert: HighMemoryUsage
        expr: ultron_memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
```

### Log Management

```json
{
  "logging": {
    "level": "INFO",
    "format": "json",
    "file": "/opt/ultron/logs/ultron.log",
    "max_size": "100MB",
    "backup_count": 10,
    "rotate_when": "midnight"
  }
}
```

### Grafana Dashboard

Access monitoring dashboard at: `http://localhost:9090`

Key metrics to monitor:
- System resource usage (CPU, Memory, Disk)
- API response times and error rates
- Component health status
- Active connections and throughput

## 🔧 Performance Optimization

### System Tuning

```bash
# Increase file descriptor limits
echo "ultron soft nofile 65536" >> /etc/security/limits.conf
echo "ultron hard nofile 65536" >> /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p
```

### Application Tuning

```json
{
  "performance": {
    "workers": 4,
    "worker_connections": 1000,
    "keepalive_timeout": 65,
    "client_max_body_size": "10MB",
    "async_pool_size": 100
  }
}
```

### Database Optimization (if using)

```json
{
  "database": {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600
  }
}
```

## 🚀 High Availability Setup

### Load Balancer Configuration (nginx)

```nginx
upstream ultron_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://ultron_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://ultron_backend;
        access_log off;
    }
}
```

### Multi-Instance Deployment

```bash
# Start multiple instances
python main.py --port 8080 &
python main.py --port 8081 &
python main.py --port 8082 &
```

## 🔄 Backup & Disaster Recovery

### Automated Backup

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/opt/backups/ultron"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ultron_backup_${TIMESTAMP}.tar.gz"

# Create backup
mkdir -p $BACKUP_DIR
cd /opt/ultron
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    .

# Keep only last 30 backups
find $BACKUP_DIR -name "ultron_backup_*.tar.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_DIR/$BACKUP_FILE"
```

### Restore Procedure

```bash
#!/bin/bash
# restore.sh
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop service
sudo systemctl stop ultron

# Restore files
cd /opt/ultron
tar -xzf $BACKUP_FILE

# Restart service
sudo systemctl start ultron

echo "Restore completed from: $BACKUP_FILE"
```

## 🧪 Testing & Validation

### Production Readiness Checklist

```bash
# Run production validation tests
python test_production.py --api-url http://localhost:8080

# Security validation
python test_integration.py --security-only

# Performance testing
python test_performance.py --duration 300
```

### Health Validation

```bash
#!/bin/bash
# health_check.sh
API_URL="http://localhost:8080"

# Check basic health
if curl -f $API_URL/health > /dev/null 2>&1; then
    echo "✅ Basic health check passed"
else
    echo "❌ Basic health check failed"
    exit 1
fi

# Check detailed health
if curl -f $API_URL/health/detailed > /dev/null 2>&1; then
    echo "✅ Detailed health check passed"
else
    echo "❌ Detailed health check failed"
    exit 1
fi

# Check metrics
if curl -f $API_URL/metrics > /dev/null 2>&1; then
    echo "✅ Metrics endpoint accessible"
else
    echo "❌ Metrics endpoint failed"
    exit 1
fi

echo "✅ All health checks passed"
```

## 🔧 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
sudo journalctl -u ultron -f

# Check configuration
python -c "import json; print(json.load(open('ultron_config_prod.json')))"

# Check dependencies
pip check

# Validate environment
python -c "import os; print(os.environ.get('ULTRON_SECRET_KEY', 'NOT_SET'))"
```

#### High Memory Usage

```bash
# Check memory usage
python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"

# Monitor specific process
top -p $(pgrep -f "python main.py")
```

#### Connection Issues

```bash
# Check port availability
netstat -tlnp | grep :8080

# Test connectivity
curl -v http://localhost:8080/health

# Check firewall
sudo ufw status
```

### Performance Issues

```bash
# Profile application
python -m cProfile -o profile.stats main.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"

# Monitor resources
htop
iotop
```

### Log Analysis

```bash
# Search for errors
grep -i error /opt/ultron/logs/ultron.log

# Monitor in real-time
tail -f /opt/ultron/logs/ultron.log

# Analyze patterns
awk '/ERROR/ {print $1, $2, $NF}' /opt/ultron/logs/ultron.log | sort | uniq -c
```

## 📞 Support & Maintenance

### Maintenance Schedule

- **Daily**: Monitor health checks and logs
- **Weekly**: Review security alerts and performance metrics
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full security audit and performance review

### Getting Help

- **Documentation**: [GitHub Wiki](https://github.com/dqikfox/ultron_agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/dqikfox/ultron_agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dqikfox/ultron_agent/discussions)
- **Security**: See [SECURITY_ALERT.md](./SECURITY_ALERT.md)

### Professional Support

For enterprise deployments requiring professional support:
- Custom deployment consulting
- Performance optimization services
- Security auditing and compliance
- 24/7 monitoring and support

---

## ✅ Production Deployment Checklist

- [ ] System requirements validated
- [ ] Dependencies installed and configured
- [ ] Environment variables set securely
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up
- [ ] Backup procedures implemented
- [ ] Health checks validated
- [ ] Performance testing completed
- [ ] Security scanning passed
- [ ] Documentation updated
- [ ] Team training completed

**Last Updated**: September 4, 2024  
**Version**: 3.0.0  
**Status**: 🟢 Production Ready

*This guide is maintained as part of the ULTRON Agent 3.0 production documentation suite.*