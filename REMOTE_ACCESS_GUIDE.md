# ULTRON Agent 3.0 - Remote Access Guide

## Quick Access URLs

### Local Access (Same Computer)
- **Web GUI (ATLAS)**: http://localhost:8080
- **Frontend UI**: http://localhost:5175
- **NVIDIA Chat**: http://localhost:8002
- **API Server**: http://localhost:5000

### Local Network Access (Other Devices)
- **Web GUI (ATLAS)**: http://192.168.1.131:8080
- **Frontend UI**: http://192.168.1.131:5175
- **NVIDIA Chat**: http://192.168.1.131:8002
- **API Server**: http://192.168.1.131:5000

### Mobile/Tablet Access
Use the same local network URLs above on your mobile browser.

## Setup Steps

### 1. Configure Firewall (One-Time Setup)

**Option A: Automated (Recommended)**
```cmd
Right-click "REMOTE_ACCESS_SETUP.bat" → Run as Administrator
```

**Option B: Manual**
```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "ULTRON Web GUI" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "ULTRON Frontend" -Direction Inbound -LocalPort 5175 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "ULTRON NVIDIA" -Direction Inbound -LocalPort 8002 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "ULTRON API" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### 2. Start ULTRON Services

```cmd
run.bat
```

This will start all required services:
- ✅ Ollama LLM Backend (port 11434)
- ✅ Web GUI Server (port 8080)
- ✅ Frontend UI Server (port 5175)
- ✅ NVIDIA Chat Service (port 8002)

### 3. Verify Services Running

**Check from local machine:**
```powershell
curl http://localhost:8080
curl http://localhost:5175
curl http://localhost:8002/health
```

**Check from another device on network:**
```powershell
curl http://192.168.1.131:8080
curl http://192.168.1.131:5175
curl http://192.168.1.131:8002/health
```

## Access from Different Devices

### From Another Windows PC
1. Open browser (Chrome, Edge, Firefox)
2. Navigate to: `http://192.168.1.131:8080`

### From Mac/Linux
1. Open browser (Safari, Chrome, Firefox)
2. Navigate to: `http://192.168.1.131:8080`

### From Mobile Phone/Tablet
1. Ensure device is on same WiFi network
2. Open mobile browser (Chrome, Safari)
3. Navigate to: `http://192.168.1.131:8080`

### From Smart TV Browser
1. Open TV browser app
2. Navigate to: `http://192.168.1.131:8080`

## Internet Access (Beyond Local Network)

### Option 1: Router Port Forwarding (Permanent)

1. **Log into your router** (usually http://192.168.1.1)
2. **Find Port Forwarding settings** (may be under "Advanced" or "NAT")
3. **Add port forwarding rules**:
   - External Port 8080 → Internal IP 192.168.1.131 Port 8080 (Web GUI)
   - External Port 5175 → Internal IP 192.168.1.131 Port 5175 (Frontend)
   - External Port 8002 → Internal IP 192.168.1.131 Port 8002 (NVIDIA)
4. **Find your public IP**: Visit https://whatismyipaddress.com
5. **Access from anywhere**: `http://YOUR_PUBLIC_IP:8080`

**Security Warning**: This exposes your services to the internet. Use with caution.

### Option 2: Ngrok Tunnel (Temporary) ✅ ACTIVE

**Your Current Ngrok URL:**
```
🌐 https://brothy-yetta-nonmetallic.ngrok-free.dev
   → Forwarding to http://localhost:8080 (Web GUI)
```

**Setup:**
1. **Install ngrok**: https://ngrok.com/download
2. **Start tunnel**:
   ```cmd
   ngrok http 8080
   ```
3. **Access from anywhere**: Use the provided URL (changes each session)

**Your Stats:**
- ✅ Region: Australia (24ms latency)
- ✅ Account: DFox (Free Plan)
- ✅ Web Interface: http://127.0.0.1:4040 (local traffic inspection)
- ✅ Active connections: 179 total requests handled
- ✅ Performance: ~0.67ms p50, 2.98ms p90 response times

**Pros**: Secure HTTPS, no router config needed, working now!
**Cons**: Temporary URL (changes on restart), free tier has limits

### Option 3: Tailscale VPN (Recommended for Security)

1. **Install Tailscale**: https://tailscale.com/download
2. **Sign up and connect** your devices
3. **Access via Tailscale IP**: Each device gets a secure IP
4. **Use ULTRON**: Access via Tailscale IP from anywhere

**Pros**: Encrypted, works anywhere, no port forwarding
**Cons**: Requires Tailscale app on each device

## Troubleshooting

### Cannot Access from Another Device

**Check 1: Firewall**
```powershell
# Verify firewall rules exist
Get-NetFirewallRule -DisplayName "ULTRON*"
```

**Check 2: Services Running**
```powershell
# Check if Python processes are running
Get-Process python
```

**Check 3: Network Connection**
```powershell
# Verify devices on same network
ipconfig
# Your IP should match 192.168.1.x range
```

**Check 4: Port Availability**
```powershell
# Check if ports are listening
netstat -an | findstr "8080 5175 8002"
```

### Port 5173 vs 5175 Confusion

**Note**: The correct port is **5175** (not 5173)
- Port **5173** is Vite's default (not used by ULTRON)
- Port **5175** is ULTRON's Frontend UI server

### Services Not Starting

**Check logs**:
```cmd
type startup.log
```

**Restart all services**:
```cmd
run.bat
```

**Check Ollama**:
```powershell
curl http://localhost:11434/api/tags
```

## Security Best Practices

### For Local Network Access (Low Risk)
✅ Firewall rules configured
✅ Network is trusted (home WiFi)
✅ No additional security needed

### For Internet Access (Higher Risk)
⚠️ **Use HTTPS/SSL**: Configure reverse proxy with Let's Encrypt
⚠️ **Add Authentication**: Implement login system
⚠️ **Use VPN**: Tailscale or WireGuard recommended
⚠️ **Limit IP Access**: Configure firewall to allow specific IPs only
⚠️ **Monitor Logs**: Watch for unusual access patterns

### Recommended Security Setup
```powershell
# Allow only specific IP range (modify as needed)
New-NetFirewallRule -DisplayName "ULTRON Web GUI Restricted" `
    -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow `
    -RemoteAddress 192.168.1.0/24
```

## Network Configuration

### Current Setup
- **Host IP**: 192.168.1.131
- **Subnet**: 192.168.1.0/24
- **Network Type**: Local WiFi/Ethernet

### Services Binding
All services now bind to `0.0.0.0` which means:
- ✅ Accepts connections from any network interface
- ✅ Works with localhost (127.0.0.1)
- ✅ Works with local IP (192.168.1.131)
- ✅ Works with public IP (if port forwarded)

## Testing Remote Access

### Step-by-Step Test

1. **On Host Machine** (192.168.1.131):
   ```cmd
   run.bat
   ```

2. **On Another Device** (phone, laptop, etc.):
   - Open browser
   - Go to: `http://192.168.1.131:8080`
   - You should see the ATLAS Neural Core interface

3. **Test NVIDIA Chat**:
   - Go to: `http://192.168.1.131:8002`
   - Test chat functionality

4. **Test Frontend UI**:
   - Go to: `http://192.168.1.131:5175`
   - Verify Pokédex interface loads

### Expected Results
- ✅ ATLAS interface displays with blue/orange cyberpunk theme
- ✅ NVIDIA section shows models and status
- ✅ Chat interface responds to messages
- ✅ All animations and effects work

## Performance Tips

### Local Network
- **Speed**: Near-instant (100+ Mbps typical)
- **Latency**: <1ms
- **Best for**: Full GUI experience, AI chat, real-time updates

### Internet Access (Port Forwarding)
- **Speed**: Depends on upload speed (usually 5-20 Mbps)
- **Latency**: 20-100ms
- **Best for**: Remote monitoring, occasional access

### VPN Access (Tailscale)
- **Speed**: Depends on connection (usually 10-50 Mbps)
- **Latency**: 10-50ms
- **Best for**: Secure remote work, mobile access

## FAQ

### Q: Why can't I access from the internet?
**A**: You need to configure router port forwarding or use a tunnel service like ngrok/Tailscale.

### Q: Is it safe to expose ULTRON to the internet?
**A**: Not recommended without additional security (authentication, HTTPS, VPN). Use Tailscale for secure access.

### Q: Can I change the IP address?
**A**: The IP (192.168.1.131) is assigned by your router. To change it, configure a static IP in router settings.

### Q: What if my IP changes?
**A**: Home IPs can change. Options:
   - Configure static IP in router
   - Use Dynamic DNS (DynDNS, No-IP)
   - Use Tailscale (handles IP changes automatically)

### Q: Can multiple people access at once?
**A**: Yes! All services support multiple concurrent connections.

### Q: How do I stop remote access?
**A**: Remove firewall rules:
```powershell
Remove-NetFirewallRule -DisplayName "ULTRON*"
```

## Support

If you encounter issues:
1. Check `startup.log` for errors
2. Verify firewall rules are active
3. Ensure services are running (`Get-Process python`)
4. Test local access first (http://localhost:8080)
5. Check network connectivity between devices

---

**ULTRON Agent 3.0** - Your AI assistant, accessible anywhere! 🌐🤖
