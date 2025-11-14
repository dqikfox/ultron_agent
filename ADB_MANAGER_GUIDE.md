# ULTRON ADB Manager - Android Device Control Integration

**Version**: 3.0.4
**Last Updated**: October 31, 2025

---

## 🎯 Overview

The ULTRON ADB Manager provides a comprehensive web-based interface for controlling and managing Android devices via ADB (Android Debug Bridge). Access it at **`http://localhost:8080/adb`** once the system is running.

---

## 📋 Prerequisites

### 1. **Android Debug Bridge (ADB)**
```powershell
# Download Android Platform Tools from
# https://developer.android.com/tools/adb

# Add to PATH or set ANDROID_HOME
$env:ANDROID_HOME = "C:\Users\YourUsername\AppData\Local\Android\Sdk"
$env:Path += ";$env:ANDROID_HOME\platform-tools"

# Verify installation
adb version
```

### 2. **Android Device Requirements**

Enable USB debugging on your device:
1. Go to **Settings → About Phone**
2. Tap **Build Number** 7 times (until "Developer options" appears)
3. Go to **Settings → Developer Options**
4. Enable **USB Debugging**
5. Enable **USB Debugging (Security Settings)** if available

### 3. **Connection Setup**

**Via USB Cable:**
```powershell
# Connect device with USB cable
# Accept the "Allow USB debugging" prompt on device

# Verify connection
adb devices

# Expected output:
# List of devices attached
# adb-R5CT434Q34Z-A03eir._adb-tls-connect._tcp    device
```

**Via WiFi (Wireless Debugging - Android 11+):**
```powershell
# On Android device:
# Settings → Developer Options → Wireless debugging → Enable

# Pair device (first time only):
adb pair <device-ip>:<pairing-port>
# Enter pairing code from device

# Connect:
adb connect <device-ip>:<port>

# Verify:
adb devices
```

---

## 🚀 Usage

### **Quick Start**

1. **Open ULTRON System**:
   ```powershell
   .\run.bat
   ```

2. **Navigate to ADB Manager**:
   - Open browser: `http://localhost:8080`
   - Click → **ADB Manager** or go to `http://localhost:8080/adb`

3. **Select Your Device**:
   - Click **"🔄 Refresh Devices"**
   - Click device card to select

4. **Execute Actions**:
   - Use quick buttons: Reboot, Screenshot, Record, etc.
   - Or use Shell tab for custom commands

---

## 📚 Interface Guide

### **Left Panel: Device Management**

| Button | Function |
|--------|----------|
| 🔄 Refresh Devices | Re-scan connected devices |
| 🔄 Reboot | Restart device |
| ⌨️ Type Text | Input text on device screen |
| 📸 Screenshot | Capture device screen |
| 🎥 Record | Record screen (300s default) |
| 👆 Tap Screen | Tap at center coordinates |
| 🔋 Battery | Get battery status |
| ⚠️ Factory Reset | Factory reset device |
| ❌ Disconnect | Disconnect from device |

### **Right Panel: Tabs**

#### **📊 Status Tab**
- Battery level percentage
- Storage usage
- RAM usage
- CPU information
- Device properties (name, model, Android version, API level, serial, IMEI)

#### **📦 Apps Tab**
- List all installed applications
- Package names and versions
- Install/uninstall apps
- Grant permissions

#### **⌨️ Shell Tab**
- Execute arbitrary shell commands
- Real-time command output
- Command history
- Error logging

#### **📁 Files Tab**
- Browse device file system
- Default path: `/sdcard/`
- Pull files to computer
- Push files to device

#### **⚙️ Settings Tab**
- **Port Forwarding**: Forward local port to device
  ```
  Local Port: 8888 → Remote Port: 8080
  ```
- **Pull File**: Download file from device
  ```
  Remote: /sdcard/document.pdf
  ```
- **Push File**: Upload file to device
- **Enable Debugging**: Activate USB debugging
- **Grant Permissions**: Allow app permissions
- **Install App**: Install APK file

---

## 🔧 Common Commands

### **Device Information**
```bash
# Get device model
adb shell getprop ro.product.model

# Get Android version
adb shell getprop ro.build.version.release

# Get API level
adb shell getprop ro.build.version.sdk

# Get battery status
adb shell dumpsys battery

# Get disk usage
adb shell df /data /cache /sdcard
```

### **App Management**
```bash
# List all apps
adb shell pm list packages

# List third-party apps only
adb shell pm list packages -3

# Install APK
adb install -r /path/to/app.apk

# Uninstall app
adb uninstall com.example.app

# Grant permission
adb shell pm grant com.example.app android.permission.CAMERA
```

### **Screen Control**
```bash
# Take screenshot
adb shell screencap -p /sdcard/screenshot.png

# Record screen (30 seconds)
adb shell screenrecord --time-limit 30 /sdcard/video.mp4

# Tap screen at coordinates
adb shell input tap 500 500

# Swipe screen
adb shell input swipe 100 500 900 500 500

# Input text
adb shell input text "Hello World"

# Press key (HOME)
adb shell input keyevent 3
```

### **File Management**
```bash
# Push file to device
adb push C:\file.txt /sdcard/

# Pull file from device
adb pull /sdcard/file.txt C:\

# List directory
adb shell ls -la /sdcard/

# Create directory
adb shell mkdir /sdcard/ULTRON

# Delete file
adb shell rm /sdcard/file.txt
```

### **System Control**
```bash
# Reboot device
adb reboot

# Reboot to bootloader
adb reboot bootloader

# Reboot to recovery
adb reboot recovery

# Factory reset
adb shell am broadcast -a android.intent.action.MASTER_CLEAR

# Enable airplane mode
adb shell settings put global airplane_mode_on 1

# Disable airplane mode
adb shell settings put global airplane_mode_on 0
```

### **Port Forwarding**
```bash
# Forward local 8888 to device 8080
adb forward tcp:8888 tcp:8080

# Forward to device app
adb forward tcp:8888 localabstract:app_socket

# List all forwards
adb forward --list

# Remove forward
adb forward --remove tcp:8888
```

---

## 📡 API Endpoints

### **Device Management**

**GET** `/api/adb/devices`
```bash
curl http://localhost:5000/api/adb/devices
```
Returns: List of connected devices

**GET** `/api/adb/device/{device-id}`
```bash
curl http://localhost:5000/api/adb/device/adb-R5CT434Q34Z-A03eir._adb-tls-connect._tcp
```
Returns: Device information (properties, battery, storage)

### **Command Execution**

**POST** `/api/adb/command`
```bash
curl -X POST http://localhost:5000/api/adb/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "shell",
    "device": "device-id",
    "args": "getprop ro.product.model"
  }'
```

**POST** `/api/adb/shell`
```bash
curl -X POST http://localhost:5000/api/adb/shell \
  -H "Content-Type: application/json" \
  -d '{
    "device": "device-id",
    "command": "dumpsys battery"
  }'
```

### **App Management**

**GET** `/api/adb/apps/{device-id}`
```bash
curl http://localhost:5000/api/adb/apps/device-id
```

**POST** `/api/adb/install`
```bash
curl -X POST http://localhost:5000/api/adb/install \
  -H "Content-Type: application/json" \
  -d '{
    "device": "device-id",
    "path": "/path/to/app.apk"
  }'
```

**POST** `/api/adb/uninstall`
```bash
curl -X POST http://localhost:5000/api/adb/uninstall \
  -H "Content-Type: application/json" \
  -d '{
    "device": "device-id",
    "package": "com.example.app"
  }'
```

### **File Operations**

**POST** `/api/adb/push`
```bash
curl -X POST http://localhost:5000/api/adb/push \
  -H "Content-Type: application/json" \
  -d '{
    "device": "device-id",
    "local": "C:\\file.txt",
    "remote": "/sdcard/file.txt"
  }'
```

**POST** `/api/adb/pull`
```bash
curl -X POST http://localhost:5000/api/adb/pull \
  -H "Content-Type: application/json" \
  -d '{
    "device": "device-id",
    "remote": "/sdcard/file.txt",
    "local": "C:\\file.txt"
  }'
```

### **System Control**

**POST** `/api/adb/reboot`
```bash
curl -X POST http://localhost:5000/api/adb/reboot \
  -H "Content-Type: application/json" \
  -d '{"device": "device-id"}'
```

**POST** `/api/adb/screenshot`
```bash
curl -X POST http://localhost:5000/api/adb/screenshot \
  -H "Content-Type: application/json" \
  -d '{"device": "device-id"}'
```

---

## ⚠️ Safety Considerations

### **Critical Operations**

| Action | Warning | Precaution |
|--------|---------|-----------|
| Factory Reset | 🔴 Irreversible | Backup device first |
| Uninstall System App | 🟡 May break device | Only remove known apps |
| Shell Commands | 🟡 Full access | Test on non-production device |
| Permission Grant | 🟡 Security risk | Only grant necessary permissions |

### **Security Best Practices**

1. **Device Protection**
   - Enable USB debugging on trusted networks only
   - Disable wireless debugging after use
   - Revoke ADB authorization periodically

2. **Data Protection**
   - Use strong device PINs/patterns
   - Avoid pushing sensitive files
   - Clear shell history

3. **Network Security**
   - Use ADB over USB (not WiFi) for sensitive operations
   - Keep Android and ADB up to date
   - Use VPN for remote ADB access

---

## 🐛 Troubleshooting

### **Device Not Detected**

```powershell
# Verify ADB is installed
adb version

# Restart ADB daemon
adb kill-server
adb start-server

# Reconnect USB cable

# Check device authorization
adb devices
# If "unauthorized", accept prompt on device

# For WiFi debugging
adb connect <device-ip>:5555
```

### **Permission Denied Errors**

```bash
# Restart daemon with higher privileges
adb kill-server
adb start-server

# Grant permissions
adb shell pm grant com.example.app android.permission.INTERNET
```

### **Connection Timeout**

```bash
# Increase timeout
adb shell -command timeout 60s getprop

# Check network connectivity
adb shell ping google.com

# Restart device
adb reboot
```

### **Push/Pull File Errors**

```bash
# Check path exists on device
adb shell ls -la /sdcard/

# Create directory if needed
adb shell mkdir -p /sdcard/ULTRON

# Verify file permissions
adb shell chmod 644 /sdcard/file.txt

# Try with full path
adb push C:\Users\YourName\file.txt /sdcard/
```

---

## 🔗 Integration Points

### **WebSocket Events**
```javascript
// Listen for ADB responses
socketio.on('adb_response', (data) => {
    console.log('ADB Output:', data.output);
});

// Send ADB command
socketio.emit('adb_command', {
    command: 'shell',
    device: 'device-id',
    args: 'ls /sdcard/'
});
```

### **REST API Integration**
```python
import requests

# Get devices
response = requests.get('http://localhost:5000/api/adb/devices')
devices = response.json()

# Execute command
response = requests.post('http://localhost:5000/api/adb/shell', json={
    'device': 'device-id',
    'command': 'getprop ro.product.model'
})
output = response.json()
```

---

## 📊 Performance Tips

- **Large File Transfer**: Use USB cable for faster speed
- **Multiple Devices**: Connect to single device for better performance
- **Frequent Commands**: Use persistent shell connection
- **Network Debugging**: Minimize latency with local WiFi

---

## 🔄 Updates & Maintenance

### **Keep ADB Updated**
```powershell
# Download latest from
# https://developer.android.com/tools/adb

# Update Android SDK platform tools
# Via Android Studio: SDK Manager → Android SDK → SDK Tools
```

### **Device Maintenance**
```bash
# Clear app cache
adb shell pm clear com.example.app

# Optimize storage
adb shell fstrim -v /data

# Update system
adb shell pm update # via Play Store
```

---

## 📞 Support & Resources

- **ADB Documentation**: https://developer.android.com/tools/adb
- **Android Developer Docs**: https://developer.android.com/
- **ULTRON Agent Docs**: See `README.md` and documentation files
- **Report Issues**: GitHub issues or project documentation

---

## 🎮 Advanced Usage

### **Debugging & Development**

```bash
# Enable verbose logging
adb logcat

# Filter logs
adb logcat | grep "app-name"

# Clear logcat
adb logcat -c

# ANR debugging
adb shell dumpsys anr

# Memory analysis
adb shell dumpsys meminfo com.example.app
```

### **Performance Analysis**

```bash
# CPU usage
adb shell top

# Battery drain analysis
adb shell dumpsys batterystats

# Network traffic
adb shell dumpsys netstat
```

### **Testing & Automation**

```bash
# Device emulation
adb emu <command>

# Simulate calls/SMS
adb emu gsm call 1234567890

# Inject touch events
adb shell input tap 500 500
```

---

**Status**: ✅ Production Ready
**Last Updated**: October 31, 2025
**Maintained By**: ULTRON Agent Development Team
