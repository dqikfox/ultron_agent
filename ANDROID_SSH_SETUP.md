# Android/Termux SSH Connection Setup

## Server Status

✅ **SSH Server Running**
- **Host**: Windows PC at `192.168.1.104`
- **Port**: `2222`
- **Status**: Active and listening on port 2222
- **Started**: Background process (Terminal ID: fdd82fc2-f135-40ed-9eb5-b033fcea3d2c)
- **Process**: `c:/Projects/ultron_agent/.venv/Scripts/python.exe ssh_clean.py`

---

## Instructions for Termux Connection

### Step 1: Verify Network Connectivity
From your Android/Termux device, first ensure network connectivity to your Windows PC:

```bash
# Ping the Windows PC
ping -c 1 192.168.1.104

# You should see:
# PING 192.168.1.104 (192.168.1.104): 56 data bytes
# 64 bytes from 192.168.1.104: ...
```

**If ping fails:**
- Ensure both devices are on the same WiFi network
- Verify Windows firewall allows port 2222 (see "Firewall Setup" below)
- Check Android device IP is in same subnet (e.g., 192.168.1.*)

### Step 2: Connect via SSH (First Time)

On your Termux device, run:

```bash
ssh -p 2222 anyuser@192.168.1.104
```

**What to expect:**

1. **First time connection** - you'll see a host key prompt:
   ```
   The authenticity of host '[192.168.1.104]:2222 ([192.168.1.104]:2222)' can't be established.
   RSA key fingerprint is SHA256:xxxxxxxxxx
   Are you sure you want to continue connecting (yes/no)?
   ```
   Type: `yes` and press Enter

2. **Password prompt:**
   ```
   anyuser@192.168.1.104's password:
   ```
   Type any password (any password is accepted for testing) and press Enter

3. **Connected!** You should see a Windows command prompt or shell:
   ```
   Microsoft Windows [Version 10.0.xxxxx]
   ...
   C:\...>
   ```

### Step 3: Test Interactive Commands

Once connected, test basic commands:

```bash
# Check who you are
whoami

# List files
dir

# Check current directory
cd

# Create a test file
echo test > test.txt

# Verify it was created
dir test.txt
```

### Step 4: Exit SSH Session

Type `exit` or press `Ctrl+D` to disconnect:

```bash
exit
```

---

## Connection Command Reference

### Basic Connection (with password)
```bash
ssh -p 2222 anyuser@192.168.1.104
```

### Non-interactive Command Execution
```bash
# Run a single command and exit
ssh -p 2222 anyuser@192.168.1.104 "whoami"

# Run multiple commands
ssh -p 2222 anyuser@192.168.1.104 "dir && echo OK"
```

### Disable Host Key Checking (for automation, not recommended for production)
```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 anyuser@192.168.1.104
```

### Verbose Mode (for debugging connection issues)
```bash
ssh -vvv -p 2222 anyuser@192.168.1.104
```

---

## Windows Firewall Setup

If you cannot connect from Termux, allow port 2222 through Windows Firewall:

### Option 1: PowerShell (Recommended)
Run from **Administrator** PowerShell:

```powershell
New-NetFirewallRule -DisplayName "SSH Server 2222" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 2222 -RemoteAddress 192.168.1.122
```

This allows connections only from Android device at `192.168.1.122`.

### Option 2: Windows Defender Firewall GUI
1. Open "Windows Defender Firewall with Advanced Security"
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → Next
4. Select "TCP" and specify port `2222` → Next
5. Select "Allow the connection" → Next
6. Check "Private" (and "Domain" if needed) → Next
7. Name: "SSH Server 2222" → Finish

---

## What I Need From You

To confirm the connection works:

1. **Connect from Termux:**
   ```bash
   ssh -p 2222 anyuser@192.168.1.104
   ```

2. **Run a test command:**
   ```bash
   whoami
   ```

3. **Tell me:**
   - ✅ Did you see the host key prompt?
   - ✅ Did authentication succeed?
   - ✅ Can you see the Windows command prompt?
   - ✅ Did `whoami` return output?
   - Any error messages?

---

## Current Server Configuration

### Authentication
- **Type**: Password-based (any password accepted for testing)
- **Upgrade Path**: Will switch to SSH key-based auth after this test

### Shell
- **Windows**: `cmd.exe` (standard Windows command prompt)
- **Other OS**: `/bin/bash` (if testing from Linux)

### Security Status
- ⚠️ **Development Mode**: No IP restrictions yet (any client can connect)
- ⏳ **Next Step**: Will restrict to `192.168.1.122` (Android device only) after verification

---

## Troubleshooting

### "Connection refused"
- **Cause**: Server not running on Windows
- **Fix**: Check terminal `fdd82fc2-f135-40ed-9eb5-b033fcea3d2c` is still active; restart if needed

### "Permission denied (publickey,password)"
- **Cause**: Password not accepted (shouldn't happen with current config)
- **Fix**: Try any random password (e.g., `test`, `password`, `1234`)

### "Network is unreachable"
- **Cause**: No connectivity between devices
- **Fix**:
  - Both on same WiFi network?
  - Windows IP correct? (Run `ipconfig` on Windows to verify)
  - Firewall blocking port 2222?

### "ssh: command not found" in Termux
- **Cause**: OpenSSH not installed
- **Fix**:
  ```bash
  pkg install openssh
  ```

---

## Next Steps After Verification

Once you confirm the connection works:

1. ✅ Local connection test on Windows (automated)
2. ✅ Remote connection test from Termux (your test)
3. 🔄 Switch to SSH key-based authentication (more secure)
4. 🔄 Restrict access to 192.168.1.122 only
5. 🔄 Add session logging
6. 🔄 Create persistent startup task

---

**Ready when you are! Let me know the results of your Termux connection test.**
