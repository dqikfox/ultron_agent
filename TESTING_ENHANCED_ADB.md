# Testing Guide: Enhanced ADB Features

**Date**: November 1, 2025
**Status**: Ready for Testing
**Device**: Samsung Galaxy S24 (Android 14, API 34)

---

## Overview

This document provides comprehensive testing procedures for the enhanced ADB features implemented based on official Android documentation.

---

## Test Environment

### Requirements
- Python 3.8+
- Flask and Flask-SocketIO
- ADB Platform Tools 36.0.0+
- Connected Samsung Galaxy S24 or similar device
- USB Debugging enabled on device

### Setup
```bash
# 1. Start ADB server
adb start-server

# 2. Verify device connection
adb devices -l

# 3. Start enhanced backend
python adb_backend_enhanced.py

# 4. Open frontend
http://localhost:8080/adb.html
```

---

## Permission Management Tests

### Test 1: Grant Permission
**Command**: `grant_permission(device, 'com.example.app', 'android.permission.CAMERA')`

**Prerequisites**:
- Android 6.0+ (API 23+)
- App must be installed
- Permission must be "dangerous" permission

**Expected Result**:
- Permission granted without user prompt
- Logcat should show permission change
- App can access camera

**Test Steps**:
1. Select device in UI
2. Find installed app in Apps tab
3. Click "Grant Permission" button
4. Enter permission name: `android.permission.CAMERA`
5. Verify success message

### Test 2: Revoke Permission
**Command**: `revoke_permission(device, 'com.example.app', 'android.permission.CAMERA')`

**Expected Result**:
- Permission revoked
- App loses access to resource

### Test 3: List Permissions
**Command**: `list_permissions(device)`

**Expected Result**:
- Returns complete list of system permissions
- Can filter by group if specified

---

## App Management Tests

### Test 4: Clear App Data
**Command**: `clear_app_data(device, 'com.package.name')`

**Prerequisites**:
- App must be installed
- Device must allow data clearing

**Expected Result**:
- App cache/data deleted
- App preferences reset
- Storage space freed

**Verification**:
- Check app storage before/after via Settings
- Logcat should show data deletion

### Test 5: Enable/Disable App
**Commands**:
- `enable_app(device, 'com.package.name')`
- `disable_app(device, 'com.package.name')`

**Expected Result**:
- Disabled apps don't appear in launcher
- Can re-enable without reinstalling
- No uninstall occurs

### Test 6: Force Stop App
**Command**: `force_stop_app(device, 'com.package.name')`

**Expected Result**:
- App process immediately terminates
- App must be relaunched to run again
- Background services stop

### Test 7: Get App Path
**Command**: `get_app_path(device, 'com.package.name')`

**Expected Result**:
- Returns full path to APK file
- Format: `/data/app/com.package-ABC123/base.apk`

---

## System Information Tests

### Test 8: Battery Information
**Command**: `get_battery_info(device)`

**Expected Output** (parsed):
```
current: 500 (mA)
level: 17
temperature: 270 (0.1C)
voltage: 4150 (mV)
health: 2 (good)
status: 3 (charging)
```

**Verification**:
- Compare with Settings > Battery
- Verify temperature is reasonable
- Check voltage is within safe range

### Test 9: Memory Information
**Command**: `get_memory_info(device)`

**Expected Output**:
- Total memory
- Free memory
- Cached memory
- Per-app memory usage

### Test 10: Network Information
**Command**: `get_network_info(device)`

**Expected Output**:
- Wi-Fi SSID and strength
- Mobile signal strength
- IP addresses (if available)
- Network type (WiFi/Mobile)

### Test 11: Device Features
**Command**: `list_device_features(device)`

**Expected Output** (Samsung S24):
- `android.hardware.camera`
- `android.hardware.camera.front`
- `android.hardware.nfc`
- `android.hardware.sensor.accelerometer`
- `android.hardware.sensor.proximity`
- (etc.)

---

## Display Testing

### Test 12: Set Display Size
**Command**: `set_display_size(device, 1280, 720)`

**Expected Result**:
- Screen resolution appears as 1280x720
- UI scales appropriately
- Apps adjust to new size

**Verification**:
- Check Settings > Display > Resolution
- Run `adb shell wm size` to verify

### Test 13: Set Display Density
**Command**: `set_display_density(device, 420)`

**Expected Result**:
- Display density changes to 420 DPI
- UI elements scale larger/smaller
- Fonts adjust accordingly

**Verification**:
- Run `adb shell wm density` to verify
- Check system DPI setting

### Test 14: Reset Display Settings
**Commands**:
- `reset_display_size(device)`
- `reset_display_density(device)`

**Expected Result**:
- Returns to device defaults
- Original resolution/density restored

---

## Logcat Tests

### Test 15: Get Logcat by Level
**Command**: `get_logcat_by_level(device, 'E', 100)`

**Expected Result**:
- Returns 100 lines of ERROR level logs
- Filters out lower severity levels

**Levels**:
- V = Verbose
- D = Debug
- I = Info
- W = Warning
- E = Error
- F = Fatal

### Test 16: Clear Logcat
**Command**: `clear_logcat(device)`

**Expected Result**:
- All logcat buffers cleared
- `get_logcat()` returns empty
- New logs start fresh

---

## Integration Tests

### Test 17: Permission Workflow
1. Grant CAMERA permission to app
2. Verify app can access camera
3. Revoke permission
4. Verify app can no longer access camera
5. Grant again
6. Verify access restored

### Test 18: App Lifecycle
1. Launch app
2. Force stop app
3. Wait 2 seconds
4. Disable app (won't appear in launcher)
5. Enable app (reappears in launcher)
6. Clear app data
7. Launch again (fresh state)

### Test 19: System Monitoring
1. Get battery info (record level)
2. Use device for 5 minutes
3. Get battery info again (level should decrease)
4. Get memory info (check free memory)
5. Launch large app
6. Get memory info (free memory should decrease)

### Test 20: Display Customization
1. Set display to 1280x720
2. Verify UI scales correctly
3. Set density to 420 DPI
4. Verify text/icons scale
5. Reset both settings
6. Verify return to original

---

## Stress Tests

### Test 21: Rapid Permission Changes
**Steps**:
1. Grant permission
2. Immediately revoke
3. Immediately grant again
4. Verify state consistent

**Expected**: No crashes or inconsistent state

### Test 22: Concurrent Requests
**Steps**:
1. Request battery info
2. Simultaneously request memory info
3. Request network info
4. Request logcat

**Expected**: All requests complete successfully

### Test 23: Large Logcat Output
**Steps**:
1. Clear logcat
2. Generate large amount of logs
3. Request 1000 lines of logcat
4. Verify all lines returned

**Expected**: No timeout or truncation

---

## Error Handling Tests

### Test 24: Invalid Package Name
**Command**: `get_app_path(device, 'com.nonexistent.app')`

**Expected Result**:
- Graceful error message
- No crash
- No device disconnect

### Test 25: Device Disconnection
**Steps**:
1. Start operation
2. Unplug device
3. Check error handling

**Expected**:
- Timeout or clear error
- Backend remains running
- Can reconnect device

### Test 26: Permission Denied (Non-Dangerous)
**Command**: `grant_permission(device, 'app', 'android.permission.INTERNET')`

**Expected Result**:
- Permission already granted (not revocable)
- Appropriate error message

---

## Performance Tests

### Test 27: Response Time
**Measure** (in milliseconds):
- Grant permission: < 500ms
- Get battery info: < 200ms
- Get memory info: < 300ms
- List devices: < 100ms

### Test 28: Throughput
**Steps**:
1. Send 100 permission grant commands
2. Measure total time
3. Calculate commands/second

**Target**: > 50 commands/second

### Test 29: Memory Usage
**Steps**:
1. Monitor backend memory before
2. Perform 50 operations
3. Monitor memory after
4. Perform garbage collection

**Target**: < 100MB memory growth

---

## Device-Specific Tests

### Samsung Galaxy S24 Specific

#### Test 30: Samsung One UI Features
1. Get device features
2. Verify Samsung-specific features present
3. Test Knox security features (if accessible)

#### Test 31: Samsung Battery Management
1. Get battery info
2. Check Samsung battery optimization
3. Verify charging status

---

## Documentation & Verification

### Test Report Template
```
Test ID: [number]
Title: [test name]
Date: [date]
Device: Samsung Galaxy S24 (Android 14)
Backend Version: [version]

Steps Performed:
1. [step]
2. [step]
3. [step]

Expected Result:
[expected outcome]

Actual Result:
[what happened]

Status: PASS / FAIL

Notes:
[any issues or observations]
```

### Sign-Off Checklist
- [ ] All 30 tests executed
- [ ] 28+ tests passing
- [ ] No crashes observed
- [ ] Performance acceptable
- [ ] Error handling verified
- [ ] Documentation complete

---

## Known Limitations to Test

1. **Android Version**: Tests assume Android 6.0+ for permission management
2. **Rooted Devices**: Some tests may differ on rooted devices
3. **Emulators**: Different behavior on AVD emulators
4. **Wireless ADB**: Additional considerations for wireless connections

---

## Troubleshooting

### Test Failures

**"Permission denied" on grant_permission**
- Device may not support runtime permissions
- App may already have permission
- Try `adb shell pm grant <package> <permission>` manually

**"Device offline" errors**
- Check USB connection
- Run `adb kill-server && adb start-server`
- Verify device is in USB Debugging mode

**Logcat returns empty**
- Run `adb logcat -c` to clear
- Generate logs by using device
- May need to filter by package

**Display commands not working**
- Check if device allows display override
- Some devices have locked display settings
- Try `adb shell wm size` and `adb shell wm density` directly

---

## Next Steps

1. Execute all 30 tests
2. Document results
3. File bugs for failures
4. Optimize performance if needed
5. Update documentation based on findings

---

*Last Updated: November 1, 2025*
*Version: 1.0*
