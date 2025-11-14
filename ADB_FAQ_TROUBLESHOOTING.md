# ULTRON ADB Manager - FAQ & Troubleshooting Reference

**Version**: 3.0.4
**Status**: Production Ready
**Last Updated**: October 31, 2025

---

## 📋 Frequently Asked Questions

### General Questions

**Q: What is ADB and why do I need it?**
A: Android Debug Bridge (ADB) is a command-line tool that lets you communicate with Android devices. ULTRON uses it to control, manage, and automate Android devices remotely.

**Q: Can I use ADB Manager without USB cable?**
A: Yes! Android 11+ supports wireless debugging via WiFi. USB connection is optional but recommended for stability and speed.

**Q: Does ADB Manager work with Android emulators?**
A: Yes, ADB works with Android emulators like AVD (Android Virtual Device) and Bluestacks. They appear in the device list just like physical devices.

**Q: What Android versions are supported?**
A: Android 4.1 (API 16) and higher. Most modern features (wireless debugging, etc.) require Android 11+.

**Q: Is there a limit on how many devices I can connect?**
A: No theoretical limit, but practical limit is 3-5 devices depending on system resources and network bandwidth.

---

### Installation & Setup

**Q: Where do I download ADB?**
A: From Android Studio SDK Manager or standalone Platform Tools.

**Q: Do I need to install Android Studio to get ADB?**
A: No, you can download standalone Platform Tools. Android Studio is just one option.

**Q: How do I verify ADB is installed correctly?**
A: Run `adb version` in PowerShell/Command Prompt. It should display version information.

**Q: Can I use ADB with Chocolatey?**
A: Yes! Run `choco install adb` if you have Chocolatey installed.

**Q: What's the difference between USB and WiFi debugging?**
A: USB is faster and more reliable; WiFi is convenient for testing without cables. Start with USB, then try WiFi if needed.

---

### Device Connection

**Q: My device shows "unauthorized" in adb devices**
A: Accept the "Allow USB debugging" prompt on your device screen. Reconnect the USB cable if it doesn't appear.

**Q: Device not showing in adb devices list**
A: Try these steps:
1. Check if USB debugging is enabled (Settings → Developer Options)
2. Use a different USB cable or port
3. Update USB drivers for your device
4. Restart ADB daemon: `adb kill-server && adb start-server`

**Q: How do I enable Developer Options on Android?**
A: Go to Settings → About Phone, then tap "Build Number" 7 times rapidly.

**Q: Can I connect multiple devices at once?**
A: Yes! All devices must be enabled for USB debugging (or WiFi debugging for wireless).

**Q: WiFi pairing keeps failing**
A: Make sure:
- Device and PC are on the same WiFi network
- Wireless debugging is enabled in Developer Options
- Firewall isn't blocking port 5555

---

### Web Interface

**Q: Where do I access ADB Manager?**
A: After starting ULTRON, go to `http://localhost:8080/adb`

**Q: Can I access ADB Manager from another computer?**
A: Yes! Navigate to `http://your-pc-ip:8080/adb` from any computer on the same network.

**Q: The device list is empty in the web interface**
A: Check:
1. Device connected: `adb devices`
2. ULTRON service running: `http://localhost:5000/api/adb/devices`
3. Browser console (F12) for errors
4. Refresh devices button (refresh icon)

**Q: Can I monitor multiple devices in the web interface?**
A: Yes! Select different devices from the left panel. Each session remembers its selection.

**Q: Does the web interface work on mobile browsers?**
A: Yes, it's responsive and works on tablets/phones, though some features work better on desktop.

---

### Screenshots & Videos

**Q: Where are screenshots and videos saved?**
A: By default in `./screenshots` folder. Configurable in `ultron_config.json`.

**Q: What format are screenshots in?**
A: PNG by default. Can be configured to JPG or other formats in settings.

**Q: How long can I record videos?**
A: Default is 300 seconds (5 minutes). Maximum 180 seconds (3 minutes) for most devices. Configurable per device.

**Q: Video is very large. How can I reduce file size?**
A: In `ultron_config.json`, reduce `recording_bitrate` from "4000k" to "2000k" or lower.

**Q: Can I download screenshots/videos directly?**
A: Yes! They're stored locally and can be accessed via file manager.

---

### App Management

**Q: How do I install an APK file?**
A: Use Settings tab - Install App and select your APK file, or use API with proper endpoint.

**Q: Can I uninstall system apps?**
A: Not directly via ADB on most devices. You need a rooted device or emulator.

**Q: How do I check installed apps?**
A: Go to Apps tab in ADB Manager, or use the API endpoint.

**Q: Can I grant permissions to apps?**
A: Yes! Use Settings tab or appropriate ADB commands.

---

### File Operations

**Q: How do I transfer files to my device?**
A: Use Files tab - Push File, or appropriate API endpoint.

**Q: What's the maximum file size I can transfer?**
A: Limited by device storage, typically no hard limit. Large files take longer.

**Q: Where should I push files on the device?**
A: `/sdcard/` is usually the safest location (external storage). Some apps use app-specific directories.

**Q: Can I pull files from system directories?**
A: Only if the device is rooted. Otherwise limited to `/sdcard/` and app-specific directories.

**Q: File transfer is very slow over WiFi**
A: WiFi is slower than USB. For large files, use USB connection. Consider splitting large files.

---

### Shell Commands

**Q: How do I run custom shell commands?**
A: Use Shell tab in ADB Manager, or appropriate API endpoint.

**Q: What shell commands are available?**
A: Any command available in Android shell: `ls`, `cat`, `rm`, `mkdir`, `getprop`, `setprop`, etc.

**Q: Can I run multiple commands in sequence?**
A: Yes, but execute them individually or use shell scripts on the device.

**Q: How do I input text via ADB?**
A: Use the input command with appropriate parameters.

**Q: Command times out or takes too long**
A: Increase timeout in `ultron_config.json`: `"default_timeout_seconds": 60`

---

### Security

**Q: Is USB debugging safe?**
A: USB debugging gives full access to the device. Only enable on trusted networks and disable when not in use.

**Q: How do I disable USB debugging?**
A: Settings → Developer Options → Toggle "USB Debugging" OFF, or revoke authorization.

**Q: Can someone else access my device via ADB?**
A: Only if they're on the same network and know the IP/port. Use strong device PIN for WiFi debugging.

**Q: Should I worry about security issues?**
A: For local development: low risk. For production: use VPN, firewall rules, and authentication tokens.

---

### Performance

**Q: ADB operations are slow**
A: Try:
1. Use USB instead of WiFi
2. Close other apps on device
3. Reduce device screen brightness
4. Restart device

**Q: Taking screenshot takes 10+ seconds**
A: This is normal on older devices. Device performance matters.

**Q: Large file transfers fail or timeout**
A: Split into smaller files or use USB connection. Check device storage space.

---

## 🐛 Common Error Messages & Solutions

### "adb: command not found"

**Cause**: ADB not installed or not in PATH

**Solution**:
- Install via Chocolatey: `choco install adb`
- Or add to PATH manually

---

### "error: device not found"

**Cause**: No devices connected or daemon not running

**Solution**:
- Restart daemon: `adb kill-server && adb start-server`
- Check connection: `adb devices`
- Reconnect USB cable

---

### "error: insufficient permissions for device"

**Cause**: ADB running as non-admin or driver issues

**Solution**:
1. Run PowerShell as Administrator
2. Restart daemon: `adb kill-server && adb start-server`
3. Uninstall/reinstall USB drivers

---

### "error: device unauthorized"

**Cause**: USB debugging prompt not accepted on device

**Solution**:
1. Disconnect USB cable
2. Go to Settings → Developer Options → Revoke USB Debugging Authorization
3. Reconnect cable
4. Accept the prompt

---

### "error: Connection reset by peer"

**Cause**: Network/USB connection lost

**Solution**:
- Reconnect or restart daemon
- Check network connectivity
- Verify firewall settings

---

### "error: timeout exceeded while waiting for device"

**Cause**: Command taking too long

**Solution**:
1. Increase timeout in config
2. Try simpler command
3. Restart device

---

### "error: push failed: cannot stat '/sdcard/': Permission denied"

**Cause**: No write permission to /sdcard/

**Solution**:
- Use /sdcard/DCIM/ or /sdcard/Documents/
- Check permissions with ls -la

---

### Web Interface Shows Backend Unavailable

**Cause**: ULTRON API server not running

**Solution**:
- Restart ULTRON: `.\run.bat`
- Or manually start API: `python api_server.py`

---

### Device Detected but No Actions Working

**Cause**: ADB daemon connection lost

**Solution**:
- Full restart: `adb kill-server && adb start-server`
- Reconnect device

---

## 🔧 Advanced Troubleshooting

### Enable Verbose ADB Logging

Use `adb devices -vvv` to see detailed ADB communication.

### Check Device Connectivity

- Verify device responds with ping
- Check network connectivity
- Get network info

### Monitor Real-Time Device Activity

- Monitor logcat output
- Filter by app
- Save to file

### Diagnose Performance Issues

- CPU usage monitoring
- Memory usage checking
- Storage usage analysis
- Battery status

---

## 📊 Performance Benchmarks

| Operation | USB Speed | WiFi Speed |
|-----------|-----------|-----------|
| Simple command | <1s | 1-2s |
| Screenshot | 2-5s | 5-10s |
| File transfer (100MB) | 30-60s | 120-300s |
| Large file transfer (500MB) | 150-300s | 600-1800s |
| Device reboot | 5-15s | 5-15s |

---

## ✅ Pre-Troubleshooting Checklist

Before reporting issues, verify:

- [ ] ADB installed: `adb version`
- [ ] Device connected: `adb devices`
- [ ] USB debugging enabled on device
- [ ] ULTRON service running
- [ ] Web interface accessible
- [ ] No firewall blocking ports
- [ ] Device has sufficient storage space
- [ ] Device battery not critically low
- [ ] WiFi network has good signal (for WiFi debugging)
- [ ] No other ADB daemon running

---

## 📞 Getting Help

1. Check This Guide: Most issues are covered here
2. Review Logs: Check `logs/` directory for detailed errors
3. Search Documentation: See related guide files
4. Community: Check GitHub issues and discussions
5. Report Issues: Include device model, Android version, and error messages

---

**Status**: ✅ Comprehensive FAQ
**Last Updated**: October 31, 2025
**Maintained By**: ULTRON Development Team
