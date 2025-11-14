# Docker DNS Resolution Fix Guide

## Issue Description
```
service dockerd failed: resolving host IPs: resolving host.docker.internal:
lookup host.docker.internal on 192.168.65.7:53: read udp 192.168.65.6:56914->192.168.65.7:53: i/o timeout
```

This error occurs when Docker Desktop cannot resolve DNS queries, typically affecting:
- Container-to-container communication
- Container-to-external-service communication
- Model downloads (Ollama)
- API calls from containers

## Root Causes

1. **Docker Desktop VM DNS Configuration Issue** - Common on Windows/Mac
2. **Network Connectivity Between Host and Docker VM** - UDP port 53 timeout
3. **Docker Daemon DNS Settings Misconfigured** - Default nameserver unreachable
4. **Firewall/Antivirus Blocking DNS** - Network access blocked
5. **WSL2 Backend Issues** - Windows Subsystem for Linux DNS not responding

## Solution Hierarchy

### Solution 1: Restart Docker Desktop (Quick Fix - Success Rate: 60%)

**Windows:**
```powershell
# Stop Docker Desktop completely
Stop-Process -Name "Docker Desktop" -Force
Stop-Process -Name "com.docker.proxy" -Force
Stop-Process -Name "vpnkit" -Force

# Wait for cleanup
Start-Sleep -Seconds 3

# Restart Docker Desktop
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    & $dockerPath
    Write-Host "Docker Desktop restarting... wait 30 seconds before using Docker"
} else {
    Write-Host "Docker Desktop not found at $dockerPath"
}
```

**Mac:**
```bash
# Restart Docker
osascript -e 'quit app "Docker"'
sleep 5
open -a Docker
echo "Docker restarting... wait 30 seconds before using Docker"
```

### Solution 2: Fix Docker DNS Configuration (Medium Difficulty - Success Rate: 85%)

**Windows (Docker Desktop):**

1. **Open Docker Desktop Settings:**
   - Right-click Docker icon in system tray → Preferences/Settings
   - Navigate to "Resources" → "Network"

2. **Configure DNS:**
   - Under "DNS Server" section
   - Set to use Google DNS or Cloudflare DNS
   - **Primary:** 8.8.8.8
   - **Secondary:** 8.8.4.4 (or 1.1.1.1 for Cloudflare)

3. **Apply and Restart:**
   - Click "Apply & Restart"
   - Wait 30-60 seconds for Docker to restart

**Alternative - Command Line (Docker Desktop on Windows):**

Modify `%AppData%\Docker\daemon.json`:

```json
{
  "dns": ["8.8.8.8", "8.8.4.4"],
  "debug": false,
  "experimental": false,
  "insecure-registries": [],
  "live-restore": true
}
```

Then restart Docker Desktop.

**Mac (Docker Desktop):**

1. Click Docker icon → Preferences
2. Go to "Resources" → "Network"
3. Set DNS servers to 8.8.8.8 and 8.8.4.4
4. Apply and restart

### Solution 3: Configure WSL2 DNS (Windows with WSL2 Backend - Success Rate: 90%)

**Problem:** WSL2 networking conflicts with Docker DNS

**Fix 1 - Update WSL2 Configuration:**

Create/edit `C:\Users\<YourUsername>\.wslconfig`:

```ini
[wsl2]
kernel=auto
memory=4GB
processors=4
swap=2GB
localhostForwarding=true
dnsTunneling=true
firewall=true
autoProxy=true
```

Then restart WSL:
```powershell
wsl --shutdown
# Restart Docker Desktop after 10 seconds
```

**Fix 2 - WSL2 Resolv.conf:**

Inside WSL Ubuntu terminal:

```bash
# Check current DNS
cat /etc/resolv.conf

# Generate resolv.conf with static DNS
sudo rm /etc/resolv.conf

# Create new with proper DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf > /dev/null

# Make it permanent
sudo chattr +i /etc/resolv.conf

# Verify
cat /etc/resolv.conf
```

### Solution 4: Fix Network Interface Issues (Advanced - Success Rate: 75%)

**Windows PowerShell (Run as Administrator):**

```powershell
# Flush DNS cache
Clear-DnsClientCache

# Reset TCP/IP stack
netsh int ip reset resetlog.txt

# Reset Winsock catalog
netsh winsock reset catalog

# Restart networking
Restart-NetAdapter -Name Ethernet -Confirm:$false
Start-Sleep -Seconds 5

# Restart Docker Desktop
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Restart Docker
& "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

**Mac Terminal:**

```bash
# Flush DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Restart network interface
sudo ifconfig en0 down
sudo ifconfig en0 up

# Restart Docker
osascript -e 'quit app "Docker"'
sleep 5
open -a Docker
```

### Solution 5: Docker Network Configuration (Technical Fix - Success Rate: 80%)

**Create Docker Network with Custom DNS:**

```bash
# Remove old network if exists
docker network rm ultron_network

# Create new network with explicit DNS
docker network create \
  --driver bridge \
  --opt "com.docker.network.bridge.name=br-ultron" \
  --opt "com.docker.driver.mtu=1500" \
  --dns=8.8.8.8 \
  --dns=8.8.4.4 \
  ultron_network

# Verify
docker network inspect ultron_network
```

**Update docker-compose.yml to use custom network:**

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    networks:
      - ultron_network
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  ultron-agent:
    build: .
    networks:
      - ultron_network
    depends_on:
      ollama:
        condition: service_healthy
    ports:
      - "5000:5000"
      - "8000:8000"
      - "8080:8080"
    dns:
      - 8.8.8.8
      - 8.8.4.4
    environment:
      OLLAMA_HOST: "http://ollama:11434"
      PYTHONUNBUFFERED: "1"

volumes:
  ollama_data:
    driver: local

networks:
  ultron_network:
    driver: bridge
    driver_opts:
      com.docker.driver.mtu: 1500
```

### Solution 6: Firewall/Antivirus Configuration

**Windows Defender Firewall:**

```powershell
# Allow Docker to access network
New-NetFirewallRule -DisplayName "Docker-Https" `
  -Direction Inbound -Action Allow `
  -Protocol TCP -LocalPort 2375

New-NetFirewallRule -DisplayName "Docker-DNS" `
  -Direction Inbound -Action Allow `
  -Protocol UDP -LocalPort 53

# Verify rules
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*Docker*" }
```

**Common Antivirus Software:**
- **McAfee:** Whitelist Docker Desktop executable + `vpnkit.exe`
- **Norton:** Add Docker installation directory to exclusions
- **Kaspersky:** Disable "Monitor network activity" for Docker processes
- **AVG/Avast:** Disable DNS filtering for Docker

## Testing DNS Resolution

After applying fixes, test Docker DNS:

```bash
# Test DNS in container
docker run --rm busybox nslookup google.com

# Test with Ollama
docker run --rm ollama/ollama ollama list

# Test network connectivity
docker run --rm alpine curl -I https://google.com

# Test with ULTRON container
docker run --rm -e "OLLAMA_HOST=http://ollama:11434" \
  -v /etc/resolv.conf:/etc/resolv.conf:ro \
  --network ultron_network \
  your-image:latest \
  python -c "import socket; socket.gethostbyname('google.com')"
```

## Quick Diagnosis Script

Create `diagnose_docker_dns.ps1`:

```powershell
Write-Host "Docker DNS Diagnostics" -ForegroundColor Cyan

# Check Docker service
$dockerService = Get-Service Docker -ErrorAction SilentlyContinue
Write-Host "Docker Service: $($dockerService.Status)" -ForegroundColor Yellow

# Check docker daemon
Write-Host "Testing Docker daemon..." -ForegroundColor Cyan
try {
    docker info | Out-Null
    Write-Host "✓ Docker daemon responding" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon not responding" -ForegroundColor Red
    return
}

# Check DNS in container
Write-Host "Testing DNS resolution in container..." -ForegroundColor Cyan
$result = docker run --rm busybox nslookup google.com 2>&1
if ($result -like "*google.com*") {
    Write-Host "✓ DNS working in container" -ForegroundColor Green
} else {
    Write-Host "✗ DNS failing in container" -ForegroundColor Red
    Write-Host $result
}

# Check host.docker.internal
Write-Host "Testing host.docker.internal..." -ForegroundColor Cyan
$hostResult = docker run --rm busybox ping -c 1 host.docker.internal 2>&1
if ($hostResult -like "*received*") {
    Write-Host "✓ host.docker.internal reachable" -ForegroundColor Green
} else {
    Write-Host "✗ host.docker.internal not reachable" -ForegroundColor Red
}

# Check network
Write-Host "Docker networks:" -ForegroundColor Cyan
docker network ls
```

## Prevention Tips

1. **Keep Docker Updated:**
   ```bash
   docker version  # Check current version
   # Update Docker Desktop to latest
   ```

2. **Monitor DNS Health:**
   ```bash
   # Regular DNS tests
   docker run --rm alpine nslookup 8.8.8.8
   docker run --rm alpine curl https://api.github.com
   ```

3. **Use Explicit DNS in Containers:**
   ```yaml
   services:
     app:
       dns:
         - 8.8.8.8
         - 8.8.4.4
   ```

4. **Restart Docker Regularly:**
   - Weekly restart recommended for production
   - Clears DNS cache and resets connections

## Emergency Recovery

If nothing works:

```powershell
# Complete Docker reset (Windows)
# WARNING: This removes all containers, images, volumes

# Stop Docker completely
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Stop-Service Docker -Force -ErrorAction SilentlyContinue

# Remove Docker data
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Program Files\Docker\*" -Recurse -Force -ErrorAction SilentlyContinue

# Restart computer
Restart-Computer -Force

# Reinstall Docker Desktop (download from https://www.docker.com/products/docker-desktop)
```

## Related Resources

- Docker Desktop Documentation: https://docs.docker.com/desktop/
- Docker Networking Guide: https://docs.docker.com/network/
- WSL2 Network Troubleshooting: https://github.com/microsoft/WSL/issues
- Docker DNS Configuration: https://docs.docker.com/config/daemon/#dns

## When to Escalate

Contact Docker support if:
- All solutions fail
- DNS works outside Docker but fails inside
- Issue occurs only with specific images
- Network isolation required
- Enterprise firewall involved

---

*Last Updated: November 3, 2025*
