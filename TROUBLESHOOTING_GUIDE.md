# TROUBLESHOOTING GUIDE - ULTRON Agent 3.0
**Production Deployment & Operations**

## Table of Contents
- [Deployment Issues](#deployment-issues)
- [Service Issues](#service-issues)
- [Docker Issues](#docker-issues)
- [Performance Issues](#performance-issues)
- [Network Issues](#network-issues)
- [Configuration Issues](#configuration-issues)
- [Data & Persistence Issues](#data--persistence-issues)
- [Emergency Recovery](#emergency-recovery)

---

## Deployment Issues

### Issue: Pre-Deployment Validation Fails

**Symptoms:**
- `pre_deployment_checklist.py` shows failed checks
- "System not ready for deployment"

**Diagnostic Steps:**
```bash
# Run detailed validator
python deployment_validator.py

# Check specific category
python -c "from deployment_validator import DeploymentValidator; v = DeploymentValidator(); v.validate_python_version()"

# View full validation log
grep ERROR logs/deployment.log
```

**Solutions:**

**Python Version Issue:**
```bash
# Check current version
python --version  # Should be 3.10+

# List available Python versions
py --list-paths  # Windows
which python3.10  # Linux/macOS

# Switch Python version
# Edit deployment_validator.py to use python3.10
```

**Dependencies Missing:**
```bash
# Install required dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "flask|aiohttp|psutil"

# Reinstall specific package
pip install --force-reinstall flask==3.0.0
```

**Virtual Environment Issue:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Verify environment
which python  # Should point to venv
```

**Configuration File Issue:**
```bash
# Validate JSON
python -m json.tool ultron_config.json

# Check required keys
python -c "import json; c=json.load(open('ultron_config.json')); print([k for k in ['ollama_base_url','api_port','web_gui_port'] if k not in c])"

# Fix invalid JSON (remove comments, trailing commas)
# Use online JSON validator: https://jsonlint.com/
```

---

### Issue: Docker Build Fails

**Symptoms:**
- `docker build` command fails
- Error during layer build

**Diagnostic Steps:**
```bash
# Check Docker daemon
docker ps  # Should list containers

# Check Dockerfile syntax
docker build --dry-run .

# Build with verbose output
docker build --progress=plain .

# Check logs
tail -f /var/log/docker.log  # Linux
Get-EventLog -LogName Application | findstr Docker  # Windows
```

**Solutions:**

**Dockerfile Not Found:**
```bash
# Verify file exists
ls -la Dockerfile

# Check encoding (should be UTF-8)
file Dockerfile

# Recreate from template
# Copy Dockerfile from repository
```

**Build Context Too Large:**
```bash
# Check .dockerignore
cat .dockerignore

# Add common exclusions
echo "__pycache__/" >> .dockerignore
echo "*.pyc" >> .dockerignore
echo ".git/" >> .dockerignore
echo "logs/*.log" >> .dockerignore

# Reduce context size
rm -rf __pycache__ .git
```

**Out of Disk Space:**
```bash
# Check available space
df -h  # Linux/macOS
Get-PSDrive C  # Windows PowerShell

# Clean Docker images
docker system prune -a

# Free space (50GB needed minimum)
rm -rf large_files/
```

**Base Image Not Available:**
```bash
# Pull base image manually
docker pull python:3.10-slim

# Verify image
docker images python

# Check internet connectivity
ping docker.io
```

---

## Service Issues

### Issue: API Server Not Responding

**Symptoms:**
- `curl http://localhost:5000/health` returns connection refused
- Web GUI cannot connect to backend

**Diagnostic Steps:**
```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs ultron-agent

# Check if port is listening
netstat -tuln | grep 5000  # Linux
Get-NetTCPConnection -LocalPort 5000  # Windows

# Test connection from inside container
docker-compose exec ultron-agent curl http://localhost:5000/health
```

**Solutions:**

**Container Not Started:**
```bash
# Start container
docker-compose up -d ultron-agent

# Check startup logs
docker-compose logs -f ultron-agent

# Wait for startup (60s grace period)
sleep 60
curl http://localhost:5000/health
```

**Port Conflict:**
```bash
# Find process using port
lsof -i :5000  # Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess  # Windows

# Kill conflicting process
kill <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Change port in docker-compose.yml
# Edit: ports: - "5001:5000"
```

**Application Crash:**
```bash
# View crash logs
docker-compose logs --tail 50 ultron-agent

# Check error messages
grep -i error logs/agent_core.log

# Restart with verbose logging
docker-compose up ultron-agent  # (no -d, shows output)
```

**Network Connectivity:**
```bash
# Check service network
docker network ls

# Inspect network
docker network inspect ultron_network

# Verify Ollama is accessible
docker-compose exec ultron-agent curl http://ollama:11434/api/tags
```

---

### Issue: Ollama Service Not Working

**Symptoms:**
- "Chat backend unavailable" warning
- Model list is empty

**Diagnostic Steps:**
```bash
# Check Ollama container
docker-compose ps ollama

# Check Ollama logs
docker-compose logs ollama

# Test Ollama API
curl http://localhost:11434/api/tags

# List models in container
docker-compose exec ollama ollama list
```

**Solutions:**

**Ollama Not Started:**
```bash
# Start Ollama
docker-compose up -d ollama

# Wait for startup
sleep 30

# Verify
docker-compose ps ollama
```

**Models Not Loaded:**
```bash
# Pull required model
docker-compose exec ollama ollama pull llava:7b

# Check available models
docker-compose exec ollama ollama list

# Verify model file exists
docker volume inspect ultron_ollama_data
```

**Out of Memory:**
```bash
# Check Ollama process memory
docker stats ollama

# Reduce model size
docker-compose exec ollama ollama pull llava:latest  # Try latest tag

# Increase Docker memory limit
# Edit docker-compose.yml: deploy.resources.limits.memory: 8G
```

**Port Conflict:**
```bash
# Check port 11434
netstat -tuln | grep 11434  # Linux
Get-NetTCPConnection -LocalPort 11434  # Windows

# Change port if needed
# Edit docker-compose.yml: ports: - "11435:11434"
# Update OLLAMA_BASE_URL in ultron-agent config
```

---

## Docker Issues

### Issue: Docker Compose Up Fails

**Symptoms:**
- `docker-compose up -d` returns error
- Containers don't start

**Diagnostic Steps:**
```bash
# Check docker-compose.yml syntax
docker-compose config

# Check compose version
docker-compose --version

# Run in foreground to see errors
docker-compose up

# Check specific service
docker-compose up ultron-agent
```

**Solutions:**

**Invalid YAML Syntax:**
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"

# Common issues:
# - Indentation (use spaces, not tabs)
# - Missing colons or quotes
# - Trailing commas

# Use online validator: https://www.yamllint.com/
```

**Version Incompatibility:**
```bash
# Check compose version (need 1.25+)
docker-compose --version

# Update docker-compose
pip install --upgrade docker-compose

# Or use Docker Compose V2
docker compose version  # V2 syntax
```

**Missing Services:**
```bash
# Check all services defined
docker-compose ps -a

# Remove orphaned containers
docker-compose up -d --remove-orphans

# Rebuild services
docker-compose build --no-cache
```

---

### Issue: Docker Container Keeps Crashing

**Symptoms:**
- Container exits immediately after starting
- Status shows "Exit Code 1" or "Exit Code 127"

**Diagnostic Steps:**
```bash
# Check container status
docker ps -a

# View crash logs
docker logs <container_id>

# Check last exit code
docker inspect <container_id> | grep ExitCode

# Run container interactively
docker run -it <image_id> /bin/bash
```

**Solutions:**

**Entry Point Error:**
```bash
# Check Dockerfile CMD
grep CMD Dockerfile

# Test command manually
docker run python:3.10-slim python main.py

# Fix: Ensure main.py exists and is executable
ls -la main.py
chmod +x main.py
```

**Missing Dependencies:**
```bash
# Check requirements
docker run python:3.10-slim pip install -r requirements.txt

# Verify all imports
docker run python:3.10-slim python -c "import aiohttp; import flask"
```

**Environment Issues:**
```bash
# Check environment variables
docker-compose config | grep environment

# Verify variables are set
docker-compose exec ultron-agent env | grep OLLAMA

# Update .env file
cat > .env << EOF
OLLAMA_BASE_URL=http://ollama:11434
API_PORT=5000
EOF
```

---

## Performance Issues

### Issue: Slow Response Times

**Symptoms:**
- API responses take >5 seconds
- Web GUI is sluggish
- Database queries are slow

**Diagnostic Steps:**
```bash
# Monitor container resources
docker stats

# Check CPU/Memory usage
top  # Linux
Get-Process python | Select-Object name, workingset  # Windows

# Monitor network
nethogs  # Linux
Get-NetAdapterStatistics  # Windows

# Check logs for slow operations
grep "elapsed\|duration" logs/*.log
```

**Solutions:**

**High CPU Usage:**
```bash
# Identify CPU-consuming process
ps aux | sort -k3 -rn | head

# Profile with py-spy
pip install py-spy
py-spy record -o profile.svg -- python main.py

# Optimize hot paths
# Check logs for performance-critical operations
```

**High Memory Usage:**
```bash
# Check memory leaks
docker stats --no-stream

# Restart service (releases memory)
docker-compose restart ultron-agent

# Increase available memory
# Edit docker-compose.yml: deploy.resources.limits.memory
```

**Disk I/O Bottleneck:**
```bash
# Monitor disk I/O
iostat -x 1  # Linux
Get-Disk  # Windows

# Check log file size
ls -lh logs/

# Rotate logs
docker-compose exec ultron-agent logrotate /etc/logrotate.d/ultron

# Move logs to faster disk
# Edit docker-compose.yml: volumes: - /fast-disk/logs:/app/logs
```

**Network Latency:**
```bash
# Test network connectivity
ping ollama
ping localhost

# Check DNS resolution
nslookup ollama
getent hosts ollama

# Verify service accessibility
curl -w "@curl-format.txt" http://localhost:5000/health
```

---

## Network Issues

### Issue: Service Cannot Connect to Ollama

**Symptoms:**
- "Connection refused" errors
- "Name or service not known"
- Timeouts when calling Ollama

**Diagnostic Steps:**
```bash
# Check network connectivity
docker-compose exec ultron-agent ping ollama

# Check DNS resolution
docker-compose exec ultron-agent nslookup ollama

# Test port connectivity
docker-compose exec ultron-agent curl http://ollama:11434/api/tags

# Check firewall rules
iptables -L | grep 11434  # Linux
Get-NetFirewallRule | findstr 11434  # Windows
```

**Solutions:**

**Service Not on Same Network:**
```bash
# Verify network configuration
docker network inspect ultron_network

# Check if services connected
docker network inspect ultron_network | grep -A 5 "Containers"

# Reconnect service to network
docker network connect ultron_network ultron-agent
```

**Hostname Resolution Failed:**
```bash
# Use IP instead of hostname
# Edit docker-compose.yml:
# OLLAMA_BASE_URL=http://172.20.0.2:11434

# Or configure service discovery
docker-compose exec ultron-agent cat /etc/hosts
```

**Firewall Blocking:**
```bash
# Check firewall rules
firewall-cmd --list-all  # Linux
Get-NetFirewallProfile  # Windows

# Allow port
firewall-cmd --add-port=11434/tcp  # Linux
netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=tcp localport=11434  # Windows

# Disable firewall (development only!)
sudo ufw disable  # Linux
Set-NetFirewallProfile -Enabled $false  # Windows
```

---

## Configuration Issues

### Issue: Invalid Configuration

**Symptoms:**
- Application fails to start with config error
- Settings not being applied

**Diagnostic Steps:**
```bash
# Validate configuration
python -c "import json; json.load(open('ultron_config.json'))"

# Check loaded configuration
docker-compose exec ultron-agent python -c "import ultron_config; print(ultron_config.__dict__)"

# Compare with defaults
diff ultron_config.json ultron_config.json.default
```

**Solutions:**

**Invalid JSON:**
```bash
# Use JSON validator
python -m json.tool ultron_config.json > /tmp/test.json

# Fix common issues
# Remove comments (JSON doesn't support them)
# Remove trailing commas
# Ensure all strings are quoted
# Validate with: https://jsonlint.com/
```

**Missing Required Keys:**
```bash
# Check required keys
python << 'EOF'
import json
required = ['ollama_base_url', 'api_port', 'web_gui_port']
config = json.load(open('ultron_config.json'))
missing = [k for k in required if k not in config]
print(f"Missing keys: {missing}")
EOF

# Add missing keys
# Copy from ultron_config.json.example
```

**Invalid Values:**
```bash
# Validate specific settings
python << 'EOF'
import json
config = json.load(open('ultron_config.json'))
assert isinstance(config['api_port'], int), "api_port must be integer"
assert 1000 <= config['api_port'] <= 65535, "api_port out of range"
print("Configuration valid")
EOF
```

---

## Data & Persistence Issues

### Issue: Data Lost After Container Restart

**Symptoms:**
- Logs are empty after restart
- Models disappear
- Configuration changes lost

**Diagnostic Steps:**
```bash
# Check volume mounts
docker-compose config | grep volumes

# Verify volumes exist
docker volume ls | grep ultron

# Check volume contents
docker volume inspect ultron-agent_ultron_cache
docker run -it -v ultron-agent_ultron_cache:/data ubuntu ls -la /data
```

**Solutions:**

**Volumes Not Mounted:**
```bash
# Update docker-compose.yml
services:
  ultron-agent:
    volumes:
      - ./logs:/app/logs
      - ./ultron_config.json:/app/ultron_config.json:ro
      - ultron_cache:/app/.cache
      - ollama_data:/root/.ollama  # Add if missing

# Recreate containers
docker-compose down
docker-compose up -d
```

**Volume Permissions Issue:**
```bash
# Check volume ownership
docker run -it -v ultron-agent_logs:/logs ubuntu ls -la /logs

# Fix ownership
docker volume inspect ultron-agent_logs

# Recreate with correct permissions
docker-compose down -v
docker-compose up -d
```

**Insufficient Disk Space:**
```bash
# Check available space
df -h
Get-PSDrive

# Clean up old logs
find logs/ -mtime +30 -delete  # Delete logs older than 30 days
du -sh .  # Check total size

# Move to larger disk
# Edit docker-compose.yml volumes to point to larger disk
```

---

## Emergency Recovery

### Issue: Complete System Failure

**Symptoms:**
- Multiple services down
- Data corruption suspected
- Cannot access any services

**Emergency Steps:**

**Step 1: Stop All Services**
```bash
# Stop gracefully
docker-compose down

# Kill if necessary
docker-compose kill

# Force remove if needed
docker-compose rm -f
```

**Step 2: Check System Health**
```bash
# Check available resources
df -h
free -h

# Check Docker daemon
docker ps

# Check system logs
journalctl -xe  # Linux
Get-EventLog -LogName System -Newest 50  # Windows
```

**Step 3: Backup Existing Data**
```bash
# Create emergency backup
mkdir emergency_backup_$(date +%s)
docker run -v ultron-agent_ultron_cache:/data -v $(pwd)/emergency_backup:/backup ubuntu \
  cp -r /data /backup/

# Archive logs
tar czf logs_backup_$(date +%s).tar.gz logs/
```

**Step 4: Restore from Backup**
```bash
# Locate latest backup
ls -lt backups/ | head

# Restore volumes from backup
docker-compose down -v
docker volume create ultron_cache
docker run -v backup_ultron_cache:/backup -v ultron_cache:/data ubuntu \
  cp -r /backup/* /data/

# Restart services
docker-compose up -d
```

**Step 5: Verify Recovery**
```bash
# Run validation
python deployment_validator.py

# Check services
docker-compose ps

# Monitor logs
docker-compose logs -f
```

---

### Issue: Database Corruption

**Symptoms:**
- Database errors in logs
- Queries failing
- Data inconsistency

**Recovery Steps:**

```bash
# Stop all services
docker-compose down

# Backup corrupted database
docker volume inspect postgres_data
tar czf postgres_backup_corrupted.tar.gz postgres_data/

# Remove corrupted volume
docker volume rm ultron-agent_postgres_data

# Restore from clean backup
tar xzf postgres_backup_clean.tar.gz

# Reinitialize database
docker-compose up postgres -d
docker-compose exec postgres psql -U ultron -d ultron < backup.sql

# Restart all services
docker-compose up -d
```

---

### Issue: Network Isolation

**Symptoms:**
- Services cannot communicate
- All containers on separate networks
- DNS resolution fails

**Recovery Steps:**

```bash
# Inspect current network
docker network inspect ultron_network

# Disconnect and reconnect services
docker network disconnect ultron_network ultron-agent
docker network connect ultron_network ultron-agent

# Or recreate network
docker-compose down
docker network prune
docker-compose up -d
```

---

## Quick Reference: Command Cheatsheet

```bash
# Basic Operations
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose ps                 # Show status
docker-compose logs -f            # View logs
docker-compose restart            # Restart services

# Debugging
docker-compose exec ultron-agent bash          # Enter container
docker logs <container_id>                     # View container logs
docker inspect <container_id>                  # Get detailed info
docker network inspect ultron_network          # Check network

# Maintenance
docker system prune                # Clean up images/containers
docker volume prune                # Clean up unused volumes
docker-compose build --no-cache    # Rebuild without cache

# Health Checks
curl http://localhost:5000/health              # API health
curl http://localhost:11434/api/tags           # Ollama health
curl http://localhost:8080                     # Web GUI

# Emergency
docker-compose kill                # Force stop
docker-compose rm -f               # Force remove
docker volume rm <volume_id>       # Delete volume
```

---

**For additional help:**
1. Check logs in `logs/` directory
2. Review `DEPLOYMENT_GUIDE.md` for setup procedures
3. Run `python deployment_validator.py` for system diagnostics
4. Contact support with logs attached

**Last Updated:** November 3, 2025
**Version:** 1.0
