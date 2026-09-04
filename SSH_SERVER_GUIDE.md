# ULTRON Agent SSH Server - Quick Reference Guide

## Overview
The ULTRON Agent SSH server provides secure remote access to the agent via SSH protocol, enabling control from Android/Termux, Linux, macOS, and other SSH clients.

## Configuration

### Default Settings
- **Port**: 2222
- **Password**: "password" (configurable)
- **Username**: Any username is accepted
- **Server**: Paramiko-based SSH server
- **Host**: Binds to all interfaces (0.0.0.0)

### Configuration File (`ultron_config.json`)
```json
{
  "ssh_server": {
    "enabled": true,
    "port": 2222,
    "password": "password",
    "max_connections": 10,
    "timeout_seconds": 300,
    "security": {
      "allow_password_auth": true,
      "require_key_auth": false,
      "allowed_users": ["*"],
      "rate_limit_per_ip": 5
    },
    "logging": {
      "enabled": true,
      "log_connections": true,
      "log_commands": true
    }
  }
}
```

## Getting Started

### 1. Start SSH Server
```bash
# Via run.bat (recommended - starts all services)
.\run.bat

# Via agent command
python main.py
> ssh start

# Via API
curl -X POST http://localhost:5000/api/ssh/start
```

### 2. Find Your Connection Details
The server automatically detects your local IP address. Check:
- **Web GUI**: http://localhost:8080 → System → SSH Control Panel
- **Agent Command**: `ssh info`
- **API Endpoint**: `GET http://localhost:5000/api/ssh/status`

### 3. Connect from Remote Device

#### Android/Termux
```bash
# Install SSH client
pkg install openssh

# Connect to ULTRON
ssh -p 2222 anyuser@<YOUR_LOCAL_IP>
# Enter password: password
```

#### Linux/macOS/Windows
```bash
ssh -p 2222 anyuser@<YOUR_LOCAL_IP>
# Enter password: password
```

#### Example Connection
```bash
ssh -p 2222 user@192.168.1.100
# Password: password
```

## Available Commands

Once connected via SSH, you have full access to ULTRON agent commands:

### System Commands
```bash
# Get system status
system status

# List available tools
tools list

# Get agent information
agent info

# Check service health
health check
```

### AI Commands
```bash
# Ask the AI
ask "What is the weather today?"

# Generate code
generate "Python function to calculate fibonacci"

# Analyze text
analyze "This is sample text to analyze"
```

### Web & Search
```bash
# Web search
search "latest AI news"

# Visit webpage
web visit "https://example.com"

# Web scraping
scrape "https://news.ycombinator.com"
```

### Tool Management
```bash
# Execute specific tool
tool pyautogui "click 100 200"

# MCP operations
mcp browser "navigate to google.com"

# GitHub operations
github "list repositories"
```

## GUI Controls

Access the web interface at http://localhost:8080:

### SSH Control Panel
- **Status Indicator**: Green (running) / Red (stopped)
- **Connection Info**: Shows local IP and connection command
- **Control Buttons**:
  - Start Server
  - Stop Server
  - Restart Server
  - Copy SSH Command

### System Monitoring
The SSH server status is integrated into the main system monitoring dashboard.

## API Endpoints

### GET /api/ssh/status
```bash
curl http://localhost:5000/api/ssh/status
```
Returns:
```json
{
  "running": true,
  "port": 2222,
  "local_ip": "192.168.1.100",
  "password": "password",
  "connect_command": "ssh -p 2222 anyuser@192.168.1.100",
  "timestamp": "2025-01-29T..."
}
```

### POST /api/ssh/start
```bash
curl -X POST http://localhost:5000/api/ssh/start
```

### POST /api/ssh/stop
```bash
curl -X POST http://localhost:5000/api/ssh/stop
```

### POST /api/ssh/restart
```bash
curl -X POST http://localhost:5000/api/ssh/restart
```

## Security Considerations

### Default Security (Basic)
- Password authentication only
- Fixed password ("password")
- No encryption beyond SSH protocol
- Suitable for local network use

### Enhanced Security (Recommended for Production)
Modify `ultron_config.json`:
```json
{
  "ssh_server": {
    "password": "USE_ENV_SSH_PASSWORD",
    "security": {
      "require_key_auth": true,
      "allowed_users": ["admin", "user"],
      "rate_limit_per_ip": 3
    }
  }
}
```

Then set environment variable:
```bash
export SSH_PASSWORD="your_secure_password"
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
```bash
# Check if SSH server is running
curl http://localhost:5000/api/ssh/status

# Check port availability
netstat -an | findstr :2222

# Start the server
python main.py
> ssh start
```

#### 2. Wrong IP Address
```bash
# Get current IP from agent
python main.py
> ssh info

# Or check network interfaces
ipconfig  # Windows
ifconfig  # Linux/macOS
```

#### 3. Authentication Failed
- Verify password is "password" (default)
- Try any username (e.g., "user", "admin", "guest")
- Check SSH client syntax: `ssh -p 2222 username@ip`

#### 4. PTY Allocation Failed
This was resolved in recent updates. If you encounter:
- Ensure you're using the latest `ssh_server.py`
- Try reconnecting after server restart
- Check server logs in `logs/ssh_server.log`

### Logs
SSH server logs are available in:
- **File**: `logs/ssh_server.log`
- **Agent Logs**: `logs/agent_core.log`
- **API Logs**: `logs/api_server.log`

### Network Diagnostics
```bash
# Test SSH server connectivity
telnet <your_ip> 2222

# Check if port is open
nmap -p 2222 <your_ip>

# Test from same machine
ssh -p 2222 test@localhost
```

## Integration Examples

### Android Automation Script
```bash
#!/data/data/com.termux/files/usr/bin/bash
# Connect to ULTRON and execute commands

ssh -p 2222 user@192.168.1.100 << 'EOF'
system status
search "latest tech news"
ask "Summarize the current system load"
EOF
```

### Remote Code Execution
```bash
# Execute Python code remotely
ssh -p 2222 user@192.168.1.100 \
  'execute "print(\"Hello from ULTRON!\")"'
```

### Monitoring Script
```bash
# Check ULTRON status from remote
ssh -p 2222 user@192.168.1.100 'health check' | \
  grep -E "(CPU|Memory|Disk)"
```

## Performance Notes

- **Memory Usage**: ~50MB additional RAM when running
- **CPU Impact**: Minimal (event-driven architecture)
- **Network**: Uses standard SSH protocol (port 2222)
- **Concurrent Connections**: Supports up to 10 simultaneous connections (configurable)

## Updates & Maintenance

### Updating SSH Server
1. Stop the server: `ssh stop`
2. Update configuration if needed
3. Restart: `ssh restart`

### Backup Configuration
```bash
# Backup SSH settings
cp ultron_config.json ultron_config.backup.json
```

### Reset to Defaults
Delete the `ssh_server` section from `ultron_config.json` and restart the agent.

---

**Quick Commands Summary**:
- **Start**: `ssh start` or `.\run.bat`
- **Stop**: `ssh stop`
- **Status**: `ssh info` or Web GUI
- **Connect**: `ssh -p 2222 anyuser@<your_ip>`
- **Password**: `password`

For additional help, use `ssh help` in the agent or visit the web GUI at http://localhost:8080.
