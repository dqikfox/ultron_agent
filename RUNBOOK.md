# RUNBOOK - ULTRON Agent 3.0
**Operational Procedures & Day-to-Day Management**

## Table of Contents
- [Daily Operations](#daily-operations)
- [Service Management](#service-management)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Backup & Recovery](#backup--recovery)
- [Scaling Operations](#scaling-operations)
- [Security & Access Control](#security--access-control)
- [Performance Optimization](#performance-optimization)
- [On-Call Procedures](#on-call-procedures)

---

## Daily Operations

### Starting the System

**Development Environment:**
```bash
# Quick start (all services)
cd /app
docker-compose up -d

# Verify startup (wait 30-60 seconds)
docker-compose ps
docker-compose logs --tail 20

# Test connectivity
curl http://localhost:5000/health
curl http://localhost:8080
curl http://localhost:11434/api/tags
```

**Production Environment:**
```bash
# Use deployment script
./deploy.sh production deploy

# Monitor startup
./deploy.sh production logs

# Verify all services healthy
./deploy.sh production status
```

**Manual Startup (if needed):**
```bash
# Start Ollama first (dependency)
docker-compose up -d ollama

# Wait for Ollama to be ready
sleep 20

# Start ULTRON Agent
docker-compose up -d ultron-agent

# Verify both services
docker-compose ps
```

### Stopping the System

**Graceful Shutdown:**
```bash
# Stop services (sends SIGTERM)
docker-compose stop

# Verify stopped
docker-compose ps

# Wait for graceful shutdown (max 10 seconds per service)
sleep 15
```

**Emergency Shutdown:**
```bash
# Force stop all services
docker-compose kill

# Remove containers
docker-compose down

# Verify cleanup
docker ps
```

### Monitoring Daily Status

**Health Check Script:**
```bash
#!/bin/bash
# save as: health_check.sh

echo "[*] System Status Check"
echo "Time: $(date)"
echo ""

echo "[*] Docker Containers:"
docker-compose ps

echo ""
echo "[*] API Server:"
curl -s http://localhost:5000/health | python -m json.tool

echo ""
echo "[*] Ollama:"
curl -s http://localhost:11434/api/tags | python -m json.tool | head -20

echo ""
echo "[*] Resource Usage:"
docker stats --no-stream

echo ""
echo "[*] Recent Errors (last 5):"
grep ERROR logs/*.log 2>/dev/null | tail -5 || echo "No errors found"

echo ""
echo "[*] Status: OK"
```

**Run Daily Health Check:**
```bash
chmod +x health_check.sh
./health_check.sh > logs/daily_health_$(date +%Y%m%d).log
```

---

## Service Management

### Restarting Services

**Single Service:**
```bash
# Restart just ULTRON Agent
docker-compose restart ultron-agent

# Or with compose CLI
docker-compose up -d --force-recreate ultron-agent

# Verify
docker-compose logs -f ultron-agent
```

**All Services:**
```bash
# Graceful restart
docker-compose restart

# Full restart (recreate containers)
docker-compose down
docker-compose up -d
```

**Rolling Restart (production):**
```bash
# Restart Ollama only (may interrupt operations)
docker-compose restart ollama

# Wait for recovery
sleep 20

# Restart Agent (handles Ollama outage gracefully)
docker-compose restart ultron-agent

# Verify
./deploy.sh production status
```

### Service Health Verification

**Check Individual Services:**
```bash
# ULTRON Agent
docker-compose exec ultron-agent curl http://localhost:5000/health

# Ollama
docker-compose exec ultron-agent curl http://ollama:11434/api/tags

# Web GUI
curl -I http://localhost:8080

# All at once
for service in "http://localhost:5000/health" "http://localhost:8080" "http://localhost:11434/api/tags"; do
    echo "Testing $service"
    curl -s "$service" | head -c 100
    echo ""
done
```

**Advanced Diagnostics:**
```bash
# Check memory usage by service
docker stats --no-stream

# Check network connectivity
docker network inspect ultron_network

# Check volume health
docker volume ls
docker volume inspect ultron-agent_ultron_cache

# Check logs for errors
docker-compose logs | grep -i error
```

### Managing Containers

**View Container Details:**
```bash
# List all containers
docker ps -a

# Get container ID for service
docker-compose ps -q ultron-agent

# Inspect specific container
docker inspect <container_id>

# Get container IP
docker inspect <container_id> | grep IPAddress
```

**Execute Commands in Container:**
```bash
# Run shell command
docker-compose exec ultron-agent bash

# Run Python script
docker-compose exec ultron-agent python deployment_validator.py

# Check environment variables
docker-compose exec ultron-agent env | grep OLLAMA

# View container filesystem
docker-compose exec ultron-agent ls -la /app
```

---

## Monitoring & Maintenance

### Log Management

**View Recent Logs:**
```bash
# Follow logs in real-time
docker-compose logs -f

# Specific service
docker-compose logs -f ultron-agent

# Last N lines
docker-compose logs --tail 50

# Since specific time
docker-compose logs --since 1h

# With timestamps
docker-compose logs --timestamps
```

**Log Analysis:**
```bash
# Find errors
docker-compose logs | grep ERROR

# Find warnings
docker-compose logs | grep WARNING

# Count by level
docker-compose logs | grep -c ERROR
docker-compose logs | grep -c WARNING

# Search for specific pattern
docker-compose logs | grep "connection refused"

# Save logs to file
docker-compose logs > logs/dump_$(date +%Y%m%d_%H%M%S).log
```

**Log Rotation:**
```bash
# Configure in docker-compose.yml
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"

# Manual rotation
docker-compose logs --no-log-prefix > logs/archive_$(date +%Y%m%d).log
docker-compose restart

# Cleanup old logs
find logs/ -name "*.log" -mtime +30 -delete  # Delete logs older than 30 days
```

### Resource Monitoring

**Monitor System Resources:**
```bash
# Real-time monitoring
docker stats

# Specific service
docker stats ultron-agent

# Memory only
docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# CPU only
docker stats --format "table {{.Container}}\t{{.CPUPerc}}"
```

**Set Resource Limits:**
```yaml
# In docker-compose.yml
services:
  ultron-agent:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

**Monitor Disk Usage:**
```bash
# Total space
du -sh .

# By directory
du -sh logs/ cache/ models/

# Docker volumes
docker system df

# Cleanup
docker system prune -a
docker volume prune
```

### Performance Monitoring

**Check API Performance:**
```bash
# Response time
curl -w "@curl-format.txt" http://localhost:5000/health

# Create curl format file
cat > curl-format.txt << 'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF

# Load testing
ab -n 100 -c 10 http://localhost:5000/health

# Using wrk
wrk -t12 -c400 -d30s http://localhost:5000/health
```

---

## Backup & Recovery

### Daily Backups

**Automated Backup Script:**
```bash
#!/bin/bash
# save as: backup_daily.sh

BACKUP_DIR="backups/daily_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "[*] Creating daily backup at $BACKUP_DIR"

# Backup configuration
cp ultron_config.json "$BACKUP_DIR/"

# Backup logs
cp -r logs "$BACKUP_DIR/logs_backup"

# Backup volumes
docker run -v ultron-agent_ultron_cache:/data \
    -v "$(pwd)/$BACKUP_DIR":/backup \
    ubuntu cp -r /data /backup/cache

# Compress
tar czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

# Cleanup
rm -rf "$BACKUP_DIR"

echo "[+] Backup complete"
```

**Schedule Daily Backups:**

Linux/macOS (cron):
```bash
# Edit crontab
crontab -e

# Add entry (backup at 2 AM daily)
0 2 * * * /app/backup_daily.sh >> /app/logs/backup.log 2>&1
```

Windows (Task Scheduler):
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "C:\app\backup.bat"
$trigger = New-ScheduledTaskTrigger -At 2AM -Daily
Register-ScheduledTask -TaskName "ULTRON Backup" -Action $action -Trigger $trigger
```

### Point-in-Time Recovery

**Restore from Backup:**
```bash
# List available backups
ls -lt backups/ | head -10

# Restore specific backup
BACKUP="backups/backup_20251103_020000.tar.gz"

# Stop services
docker-compose down

# Extract backup
tar xzf "$BACKUP"

# Restore volumes
docker volume rm ultron-agent_ultron_cache
docker run -v backup_directory/cache:/backup_data \
    -v ultron-agent_ultron_cache:/data \
    ubuntu cp -r /backup_data /data

# Restore configuration
cp backups/ultron_config.json .

# Restart
docker-compose up -d

# Verify
./deploy.sh production status
```

---

## Scaling Operations

### Horizontal Scaling

**Add More Agent Instances:**
```yaml
version: '3.8'
services:
  ultron-agent-1:
    # ... existing config ...
    ports:
      - "5001:5000"
      - "8001:8080"

  ultron-agent-2:
    # ... same config ...
    ports:
      - "5002:5000"
      - "8002:8080"

  # Share Ollama backend
  ollama:
    # ... existing config ...
```

**Load Balancing:**
```nginx
# nginx.conf
upstream ultron_agents {
    server localhost:5001;
    server localhost:5002;
    server localhost:5003;
}

server {
    listen 5000;
    location / {
        proxy_pass http://ultron_agents;
        proxy_set_header Host $host;
    }
}
```

### Vertical Scaling

**Increase Resource Limits:**
```yaml
# docker-compose.yml
services:
  ultron-agent:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  ollama:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 32G
```

**Monitor Scaling Impact:**
```bash
# Before scaling
./deploy.sh production status

# After scaling
docker-compose restart ultron-agent
sleep 10
./deploy.sh production status

# Compare resource usage
docker stats
```

---

## Security & Access Control

### User Access Management

**Create Non-Root User:**
```bash
# Already in Dockerfile (ultron:1000)
# But if needed manually:
docker exec ultron-agent useradd -m -u 1000 ultron
docker exec ultron-agent usermod -aG docker ultron
```

**Restrict Access to Ports:**
```bash
# Linux firewall
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --remove-port=5000/tcp --permanent

# Windows Firewall
netsh advfirewall firewall add rule name="ULTRON API" dir=in action=allow protocol=tcp localport=5000
```

### API Authentication

**Implement API Key Auth:**
```python
# Add to API server
@app.before_request
def check_api_key():
    if request.endpoint not in ['health', 'login']:
        key = request.headers.get('X-API-Key')
        if not verify_api_key(key):
            return {'error': 'Unauthorized'}, 401
```

### SSL/TLS Configuration

**Generate Self-Signed Certificate:**
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

**Enable HTTPS in Nginx:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate cert.pem;
    ssl_certificate_key key.pem;

    location / {
        proxy_pass http://localhost:5000;
    }
}
```

---

## Performance Optimization

### Cache Management

**Clear Application Cache:**
```bash
# Remove cache directory
docker-compose exec ultron-agent rm -rf /app/.cache

# Or restart to reset
docker-compose restart ultron-agent
```

**Database Query Optimization:**
```sql
-- Create indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM sessions WHERE user_id = 123;
```

### Model Optimization

**Use Smaller Models:**
```bash
# Replace large model with smaller version
docker-compose exec ollama ollama pull llava:7b  # Smaller than default

# Or use quantized version
docker-compose exec ollama ollama pull llama2:7b-chat-q8_0  # Quantized
```

**Model Caching:**
```python
# In brain.py
from functools import lru_cache

@lru_cache(maxsize=1000)
def generate_response(prompt):
    # Cached responses
    return ollama_api.generate(prompt)
```

---

## On-Call Procedures

### Incident Response

**Level 1: Service Degradation (P3)**
```
1. Check logs for errors
   docker-compose logs | grep ERROR

2. Monitor resources
   docker stats

3. If issue persists:
   docker-compose restart ultron-agent

4. Escalate if not resolved in 5 minutes
```

**Level 2: Service Down (P2)**
```
1. Immediately assess
   docker-compose ps
   docker-compose logs --tail 100

2. Attempt recovery
   docker-compose restart
   sleep 10
   ./deploy.sh production status

3. If still down, restore from backup
   See "Point-in-Time Recovery" section

4. Escalate to L3 support
```

**Level 3: Data Loss (P1)**
```
1. STOP all operations immediately
   docker-compose kill

2. Preserve evidence
   tar czf incident_evidence_$(date +%s).tar.gz logs/ backups/

3. Contact backup team
   Initiate full recovery procedure

4. Begin incident post-mortem
```

### Escalation Procedure

**L1 → L2 Escalation:**
- After 5 minutes of troubleshooting without resolution
- Contact on-call L2 engineer
- Provide: error logs, resource usage, recent changes

**L2 → L3 Escalation:**
- After 15 minutes without resolution
- Likely needs code/architecture changes
- Contact on-call L3 architect

### Communication

**During Incident:**
```
1. Update status page (first 5 minutes)
2. Notify team leads
3. Escalate if needed
4. Update every 15 minutes
```

**Post-Incident:**
```
1. Document root cause
2. File incident report
3. Schedule post-mortem (24 hours)
4. Implement preventive measures
```

---

## Maintenance Windows

### Planned Maintenance

**Weekly Maintenance (Sundays 2-3 AM UTC):**
```bash
# Backup
./backup_daily.sh

# Log rotation
docker-compose logs --no-log-prefix > logs/archive_$(date +%Y%m%d).log

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# System health check
python deployment_validator.py

# Restart services
docker-compose restart
```

**Monthly Maintenance (First Sunday 2-4 AM UTC):**
```bash
# Full system update
docker-compose build --no-cache

# Test in staging first
docker-compose -f docker-compose.staging.yml up -d

# Smoke tests
./deploy.sh staging status

# Move to production
docker-compose down
docker-compose up -d

# Verify
./deploy.sh production status
```

### Planned Downtime Announcement

```
MAINTENANCE WINDOW ANNOUNCEMENT
====================================
Service: ULTRON Agent
Date: [DATE] [TIME] - [TIME]
Expected Duration: 1 hour
Impact: No service available during window

Reason: [System update/Database maintenance/etc]

Actions:
1. Backup will be taken before downtime
2. Services will be restarted cleanly
3. Status page will be updated
```

---

## Quick Reference

### Emergency Contacts
- L2 On-Call: [SLACK: #ultron-oncall]
- L3 Architect: [NAME] [CONTACT]
- DevOps Lead: [NAME] [CONTACT]

### Critical Command Reference
```bash
# Check status
docker-compose ps

# View errors
docker-compose logs | grep ERROR

# Emergency restart
docker-compose down && docker-compose up -d

# Backup immediately
./deploy.sh production backup

# Restore from backup
# See Backup & Recovery section
```

### Important Paths
- Configuration: `/app/ultron_config.json`
- Logs: `/app/logs/`
- Models: `/root/.ollama/models` (in Ollama container)
- Backups: `/app/backups/`

---

**Document Version:** 1.0
**Last Updated:** November 3, 2025
**Next Review:** March 3, 2026

**Maintained By:** [ULTRON Operations Team]
**Distribution:** Team Members, On-Call Engineers, DevOps Team
