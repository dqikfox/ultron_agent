# ULTRON ADB Manager - Setup & Installation Guide

**Version**: 3.0.4
**Status**: Production Ready
**Last Updated**: October 31, 2025

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Device Setup](#device-setup)
4. [Verification](#verification)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Windows System Requirements

- **OS**: Windows 10 or later (64-bit recommended)
- **RAM**: 8GB minimum
- **Storage**: 500MB free space
- **Python**: 3.8+
- **Node.js**: 14+ (for web interface)

### Required Software

- **Android Debug Bridge (ADB)**: Latest version
- **ULTRON Agent**: 3.0+
- **Web Browser**: Chrome, Firefox, Edge, or Safari (latest)
- **USB Drivers**: Android USB drivers (auto-install recommended)

### Device Requirements

- **Android Version**: 4.1 (API 16) or higher
- **USB Connectivity**: USB 2.0+ or WiFi (optional)
- **Developer Mode**: Enabled on device
- **Storage**: 50MB minimum free space

---

## 🚀 Installation Steps

### Step 1: Install Android Debug Bridge (ADB)

#### Option A: Using Android Studio (Recommended)

1. Download **Android Studio** from https://developer.android.com/studio
2. Install Android Studio
3. Open **SDK Manager** (Tools → SDK Manager)
4. Go to **SDK Tools** tab
5. Check **Android SDK Platform-Tools**
6. Click **Apply** and wait for installation

#### Option B: Download Standalone ADB

1. Download **Platform Tools** from https://developer.android.com/tools/adb
2. Extract to a folder (e.g., `C:\Android\platform-tools`)
3. Note the path for later

#### Option C: Using Chocolatey (Windows)

```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; `
  [System.Net.ServicePointManager]::SecurityProtocol = `
  [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install ADB
choco install adb
```

### Step 2: Add ADB to System PATH

#### For Android Studio Installation

1. Open **PowerShell** as Administrator
2. Run the following commands:

```powershell
# Set ANDROID_HOME
[Environment]::SetEnvironmentVariable('ANDROID_HOME', `
  "$env:USERPROFILE\AppData\Local\Android\Sdk", 'User')

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = "$currentPath;$env:ANDROID_HOME\platform-tools"
[Environment]::SetEnvironmentVariable('Path', $newPath, 'User')

# Verify (restart PowerShell first)
adb version
```

#### For Standalone Installation

```powershell
# Set custom path
[Environment]::SetEnvironmentVariable('ANDROID_HOME', `
  'C:\Android\platform-tools', 'User')

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = "$currentPath;C:\Android\platform-tools"
[Environment]::SetEnvironmentVariable('Path', $newPath, 'User')

# Restart PowerShell and verify
adb version
```

### Step 3: Verify ADB Installation

```powershell
# Restart PowerShell
adb version

# Expected output:
# Android Debug Bridge version 1.0.41
# Version 34.0.X
# ...
```

### Step 4: ULTRON Agent Integration

ADB Manager is automatically included with ULTRON Agent 3.0+. No additional installation needed.

Verify by accessing: `http://localhost:8080/adb` after starting ULTRON.

---

## 📱 Device Setup

### USB Debugging (All Android Versions)

#### Step 1: Enable Developer Options

On your Android device:

1. Open **Settings**
2. Scroll to **About Phone**
3. Tap **Build Number** 7 times rapidly
   - You'll see: "You are now a developer!"
4. Go back to **Settings**
5. Find **Developer Options** (usually under System or Advanced)

#### Step 2: Enable USB Debugging

In **Settings → Developer Options**:

1. Find **USB Debugging**
2. Toggle **ON**
3. If prompted, accept the warning

#### Step 3: Connect via USB

1. Connect Android device to Windows PC with USB cable
2. Select **"Allow USB debugging"** on device when prompted
3. On Windows, verify connection:

```powershell
adb devices

# Expected output:
# List of devices attached
# emulator-5554             device
# OR
# 192.168.1.100:5555        device
```

### Wireless Debugging (Android 11+)

#### First-Time Pairing

On your Android device:

1. Go to **Settings → Developer Options → Wireless Debugging**
2. Toggle **ON**
3. Tap **Pair using QR code** or **Pair device manually**
4. Note the **pairing code** and **IP:Port**

On Windows (PowerShell):

```powershell
# Using pairing code (recommended)
adb pair <device-ip>:<pairing-port>
# Enter pairing code when prompted

# Or pair with code
adb pair 192.168.1.100:59659
# Enter code: 123456

# Expected output:
# Successfully paired to 192.168.1.100:5555
```

#### Connecting After Pairing

```powershell
adb connect <device-ip>:5555

# Example:
adb connect 192.168.1.100:5555

# Expected output:
# connected to 192.168.1.100:5555
```

#### Verify Connection

```powershell
adb devices

# Expected output:
# List of devices attached
# 192.168.1.100:5555        device
```

---

## ✅ Verification

### Test ADB Connection

```powershell
# Get device model
adb shell getprop ro.product.model
# Expected: Device model name

# Get Android version
adb shell getprop ro.build.version.release
# Expected: Version number (13, 14, etc)

# Get battery status
adb shell dumpsys battery
# Expected: Battery information
```

### Test Web Interface

1. Start ULTRON Agent: `.\run.bat` or `python main.py`
2. Open browser: `http://localhost:8080`
3. Navigate to **ADB Manager** or `http://localhost:8080/adb`
4. Click **🔄 Refresh Devices**
5. Device should appear in left panel

### Test API Endpoints

```powershell
# Get devices via API
curl http://localhost:5000/api/adb/devices

# Expected JSON response:
# {
#   "devices": [
#     {
#       "id": "device-id",
#       "status": "device",
#       "model": "Phone Model",
#       "android_version": "14"
#     }
#   ]
# }
```

---

## ⚙️ Configuration

### ULTRON Config File

Edit `ultron_config.json` to customize ADB settings:

```json
{
  "adb_manager": {
    "enabled": true,
    "auto_detect_devices": true,
    "refresh_interval_seconds": 5,
    "default_timeout_seconds": 30,
    "screenshot_format": "png",
    "screenshot_path": "./screenshots",
    "recording_bitrate": "4000k",
    "recording_duration_default": 300,
    "max_concurrent_commands": 3,
    "log_commands": true,
    "use_wireless_first": false
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | true | Enable/disable ADB manager |
| `auto_detect_devices` | boolean | true | Scan for devices on startup |
| `refresh_interval_seconds` | int | 5 | Device list refresh rate |
| `default_timeout_seconds` | int | 30 | Command execution timeout |
| `screenshot_format` | string | "png" | Screenshot file format |
| `screenshot_path` | string | "./screenshots" | Download directory |
| `recording_bitrate` | string | "4000k" | Video bitrate for recording |
| `recording_duration_default` | int | 300 | Default recording length (seconds) |
| `max_concurrent_commands` | int | 3 | Max parallel command executions |
| `log_commands` | boolean | true | Log all executed commands |
| `use_wireless_first` | boolean | false | Prefer WiFi over USB |

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### ADB Not Found

**Error**: `'adb' is not recognized as an internal or external command`

**Solutions**:

1. Verify installation:
   ```powershell
   Get-Command adb
   ```

2. Add to PATH manually:
   ```powershell
   $env:Path += ";C:\Android\platform-tools"
   adb version
   ```

3. Restart PowerShell and try again

#### Device Not Detected

**Error**: `List of devices attached` shows empty

**Solutions**:

```powershell
# 1. Restart ADB daemon
adb kill-server
adb start-server

# 2. Check USB connection
adb devices -l

# 3. Reconnect USB cable

# 4. Check Windows Device Manager for "Android" device

# 5. Accept "Allow USB debugging" prompt on device

# 6. Check if device is in "File Transfer Mode" (not charge-only)
```

#### Permission Denied

**Error**: `error: insufficient permissions for device`

**Solutions**:

```powershell
# 1. Run as Administrator
Start-Process powershell -Verb RunAs

# 2. Restart daemon with admin privileges
adb kill-server
adb start-server

# 3. Restart device
adb reboot

# 4. Update USB drivers
# Device Manager → Android Device → Update Driver
```

#### Timeout Errors

**Error**: `error: (104) Connection reset by peer`

**Solutions**:

```powershell
# 1. Increase timeout in config
# Edit ultron_config.json: "default_timeout_seconds": 60

# 2. Restart device
adb reboot

# 3. Disconnect and reconnect
adb disconnect
adb connect <device-ip>:5555

# 4. Check network connectivity
adb shell ping google.com
```

#### WiFi Connection Issues

**Error**: Connection fails or keeps disconnecting

**Solutions**:

```powershell
# 1. Verify device is on same network
# Device Settings → WiFi → Connected to same SSID

# 2. Pair again
adb kill-server
adb start-server
adb pair <device-ip>:<pairing-port>
adb connect <device-ip>:5555

# 3. Check firewall settings
# Windows Firewall → Allow an app through firewall → Add ADB

# 4. Restart both device and PC
```

#### Web Interface Not Showing Devices

**Error**: Device list is empty in web UI

**Solutions**:

```powershell
# 1. Check API is running
curl http://localhost:5000/api/adb/devices

# 2. Check browser console for errors
# Press F12 in browser → Console tab

# 3. Verify device connection
adb devices

# 4. Restart ULTRON
# Ctrl+C to stop, then: python main.py

# 5. Clear browser cache and refresh
# Ctrl+Shift+Delete in browser
```

### Diagnostic Commands

```powershell
# Full device information
adb devices -l

# Verbose output
adb devices -vvv

# Check daemon status
adb status-window

# View log output
adb logcat

# Device properties
adb shell getprop

# Check storage
adb shell df -h

# Monitor running processes
adb shell top
```

---

## 🔐 Security Considerations

### Best Practices

1. **USB Debugging**
   - Only enable on trusted networks
   - Disable after use
   - Revoke authorization in Settings

2. **Wireless Debugging**
   - Use strong device PIN
   - Pair with specific devices only
   - Disable when not in use

3. **Credential Management**
   - Never commit device IDs to version control
   - Use environment variables for sensitive data
   - Rotate device pairs periodically

### Revoke Authorization

```bash
# On device: Settings → Developer Options → Revoke USB Debug Authorization

# Or via ADB:
adb shell am broadcast -a android.intent.action.MASTER_CLEAR
```

---

## 📊 Performance Optimization

### For Large File Transfers

```powershell
# Use USB cable (faster than WiFi)
# USB 3.0 speeds: 100-200 MB/s
# WiFi 5GHz: 20-50 MB/s
```

### For Multiple Device Management

```powershell
# Monitor multiple devices
adb devices

# Execute command on specific device
adb -s <device-id> shell getprop ro.product.model

# Simultaneous operations
# Best practice: 1 device at a time
```

### Network Optimization

```powershell
# For WiFi connectivity
# Position device and PC close together
# Use 5GHz WiFi band (faster, shorter range)
# Minimize interference from other devices
```

---

## 📚 Additional Resources

- **Android Debug Bridge Docs**: https://developer.android.com/tools/adb
- **Android Developer Docs**: https://developer.android.com/
- **ULTRON Agent Docs**: See project documentation
- **ADB Manager Guide**: `ADB_MANAGER_GUIDE.md`
- **ADB Quick Reference**: `ADB_QUICK_REFERENCE.md`

---

## ✅ Checklist

- [ ] Android Debug Bridge installed
- [ ] ADB added to system PATH
- [ ] `adb version` command works
- [ ] Device USB debugging enabled
- [ ] Device connected and showing in `adb devices`
- [ ] ULTRON Agent running (`./run.bat`)
- [ ] Web interface accessible (`http://localhost:8080`)
- [ ] ADB Manager showing devices
- [ ] Test screenshot successful
- [ ] Configuration customized (if needed)

---

**Questions?** See `ADB_MANAGER_GUIDE.md` for complete documentation.

**Status**: ✅ Ready for Production
**Support**: Community documentation and GitHub issues
**Last Updated**: October 31, 2025
