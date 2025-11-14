# ULTRON ADB Manager - Quick Reference Card

**Access**: `http://localhost:8080/adb`

---

## ⚡ Quick Commands

### Device Connection
```powershell
adb devices                          # List devices
adb connect 192.168.1.100:5555      # Connect WiFi
adb disconnect                       # Disconnect
adb kill-server && adb start-server  # Restart daemon
```

### Screenshot & Recording
```bash
adb shell screencap -p /sdcard/ss.png    # Screenshot
adb pull /sdcard/ss.png C:\              # Download
adb shell screenrecord /sdcard/video.mp4 # Record (30s)
adb pull /sdcard/video.mp4 C:\           # Download video
```

### App Management
```bash
adb shell pm list packages           # List all apps
adb shell pm list packages -3        # Third-party only
adb install app.apk                  # Install
adb uninstall com.example.app        # Uninstall
adb shell pm grant com.app PERMISSION # Grant permission
```

### System Control
```bash
adb shell getprop ro.product.model   # Device model
adb shell getprop ro.build.version.release  # Android version
adb shell dumpsys battery            # Battery status
adb shell df /data                   # Storage usage
adb reboot                           # Restart device
adb shell settings put global airplane_mode_on 1  # Airplane mode
```

### File Management
```bash
adb push C:\file.txt /sdcard/        # Upload file
adb pull /sdcard/file.txt C:\        # Download file
adb shell ls -la /sdcard/            # List directory
adb shell mkdir /sdcard/folder       # Create directory
adb shell rm /sdcard/file.txt        # Delete file
```

### Screen Input
```bash
adb shell input tap 500 500          # Tap coordinates
adb shell input text "Hello"         # Type text
adb shell input swipe 100 500 900 500 500  # Swipe
adb shell input keyevent 3           # Press HOME
adb shell input keyevent 4           # Press BACK
adb shell input keyevent 26          # Press POWER
```

---

## 🎯 GUI Quick Actions

| Icon | Action | Purpose |
|------|--------|---------|
| 🔄 | Refresh | Rescan connected devices |
| 🔄 | Reboot | Restart device |
| ⌨️ | Type Text | Input text on screen |
| 📸 | Screenshot | Capture device screen |
| 🎥 | Record | Record video (300s default) |
| 👆 | Tap | Tap center of screen |
| 🔋 | Battery | Show battery info |
| ⚠️ | Factory Reset | Wipe device data |
| ❌ | Disconnect | End ADB connection |

---

## 🔑 Key ADB Keycodes

| Keycode | Event |
|---------|-------|
| 3 | HOME |
| 4 | BACK |
| 5 | CALL |
| 6 | ENDCALL |
| 24 | VOLUME_UP |
| 25 | VOLUME_DOWN |
| 26 | POWER |
| 27 | CAMERA |
| 82 | MENU |
| 84 | SEARCH |

---

## 📊 Device Info Properties

```bash
# Get any property:
adb shell getprop <property-name>

# Common properties:
ro.product.model              # Device model
ro.product.brand              # Manufacturer
ro.build.version.release      # Android version (13, 14, etc)
ro.build.version.sdk          # API level
ro.serialno                   # Serial number
ro.telephony.use_old_mnc_mcc  # IMEI
ro.product.cpu.abi            # Processor architecture
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Device not found | `adb kill-server && adb start-server` |
| Unauthorized | Accept USB debug prompt on device |
| Connection timeout | Restart device, check USB cable |
| Permission denied | Run as administrator, reinstall ADB |
| WiFi disconnect | Use `adb connect <ip>:5555` again |

---

## 🔗 API Endpoints Quick

```bash
GET    /api/adb/devices                    # List devices
GET    /api/adb/device/{id}                # Device info
POST   /api/adb/shell                      # Run command
POST   /api/adb/screenshot                 # Take screenshot
POST   /api/adb/install                    # Install APK
POST   /api/adb/uninstall                  # Uninstall app
POST   /api/adb/push                       # Upload file
POST   /api/adb/pull                       # Download file
POST   /api/adb/reboot                     # Restart device
```

---

## ⚠️ Safety Checklist

- [ ] Device connected and recognized (`adb devices`)
- [ ] USB debugging enabled on device
- [ ] Backup important data before factory reset
- [ ] Only run trusted commands
- [ ] Test on non-production device first
- [ ] Disable wireless debugging after use

---

## 🚀 Common Workflows

### Backup Device Data
```bash
adb backup -apk -shared -all -f backup.ab
# Restores with: adb restore backup.ab
```

### Logcat Debugging
```bash
adb logcat                          # View all logs
adb logcat -c                       # Clear logs
adb logcat | grep MyApp             # Filter by app
adb logcat *:E                      # Errors only
```

### Port Forwarding
```bash
adb forward tcp:8888 tcp:8080       # Local:Device
adb forward --list                  # Show all
adb forward --remove tcp:8888       # Remove
```

### Performance Analysis
```bash
adb shell top                       # CPU/memory usage
adb shell dumpsys meminfo          # Memory details
adb shell dumpsys battery          # Battery stats
adb shell dumpsys cpuinfo          # CPU info
```

---

**📚 Full Guide**: See `ADB_MANAGER_GUIDE.md`
**Status**: ✅ Ready to Use
**Updated**: October 31, 2025
