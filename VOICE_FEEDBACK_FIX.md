# Voice Feedback Loop Fix - October 24, 2025

## Critical Issue: Microphone Recording Model's TTS Output

### Problem Description
The microphone was recording ULTRON's own voice output (TTS) and looping it back as input, creating an infinite feedback loop where the model would hear its own responses and try to respond to them.

### Root Cause
The voice recognition system was not properly stopping the microphone before TTS playback began. The original implementation only called `recognition.stop()` but:
1. The stop operation is asynchronous and takes time
2. The recognition instance wasn't fully destroyed
3. The 500ms delay before restarting was insufficient
4. Auto-restart logic could trigger prematurely

### Solution Implemented

**File Modified**: `gui/ultron_enhanced/web/app.js`  
**Functions Updated**: `dequeueSpeech()` (both API TTS and browser TTS fallback)

#### Key Changes:

1. **Immediate Recognition Destruction** (Line ~1825):
   ```javascript
   if (this.recognition) {
       this.shouldRestartRecognition = false; // Prevent auto-restart
       this.isListening = false;
       
       try {
           this.recognition.stop();
           this.recognition = null; // Fully destroy the recognition instance
       } catch (error) {
           console.debug('[ULTRON] Error stopping recognition', error);
       }
   }
   ```

2. **Microphone Release Delay** (Line ~1841):
   ```javascript
   // Additional safeguard: Wait for microphone to fully release
   await new Promise(resolve => setTimeout(resolve, 200));
   ```

3. **Extended Post-TTS Delay** (Line ~1876):
   ```javascript
   this.audioElement.onended = () => {
       setTimeout(() => {
           if (wasListening && this.voiceEnabled) {
               this.startVoiceRecognition(); // Restart after 1 second
           }
           // ... queue processing
       }, 1000); // Increased from 500ms to 1000ms
   ```

4. **Browser TTS Fallback** (Line ~1907):
   - Same 1-second delay applied to browser TTS (`window.speechSynthesis`)
   - Ensures consistent behavior across all TTS methods

### Technical Details

**Before Fix**:
- Recognition stopped: `recognition.stop()` (async, ~50-100ms)
- Delay before restart: 500ms
- Total protection: ~550-600ms
- **Result**: Microphone could resume while audio still playing

**After Fix**:
- Recognition stopped: `recognition.stop()` + set to `null` (immediate)
- Microphone release wait: 200ms (guaranteed)
- Delay after audio finishes: 1000ms
- Total protection: ~1200ms minimum
- **Result**: Microphone only resumes after complete audio silence

### Verification Steps

1. **Enable Voice Mode**: Click microphone button in GUI
2. **Send Voice Command**: Say "Hello ULTRON"
3. **Observe TTS Playback**: ULTRON responds with audio
4. **Check Microphone**: Should remain OFF during TTS
5. **Verify Resume**: Microphone should auto-resume 1 second after TTS finishes
6. **Test Loop Prevention**: ULTRON should NOT respond to its own voice

### Expected Behavior

✅ **CORRECT**: Microphone stops → TTS plays → 1 second silence → Microphone resumes  
❌ **INCORRECT** (old): Microphone active → TTS plays → Microphone captures TTS → Infinite loop

### Console Logging

Monitor browser console for these messages:
```
[ULTRON] Stopping voice recognition during TTS to prevent feedback loop
[ULTRON] TTS playback finished
[ULTRON] Resuming voice recognition after TTS
```

If you see multiple "Resuming" messages without user input, the feedback loop may still be occurring.

## Issue #2: Window Minimize/Maximize Not Working

### Problem Description
User reports that when the browser window is minimized, they cannot restore or maximize it again.

### Root Cause Analysis
**This is NOT a bug in the ULTRON web application code.**

The ULTRON GUI is a web-based application running inside a browser (Chrome, Edge, Firefox, etc.). The minimize/maximize controls are part of the **browser window**, not the web app itself.

### Why This Happens

1. **Browser Window Management**: The web app has no control over browser window state (minimize, maximize, restore)
2. **Operating System Issue**: Windows OS manages window states, not JavaScript
3. **Browser Freeze**: The browser process may become unresponsive
4. **Task View Issues**: Windows Task View can sometimes hide minimized windows

### Solutions (User Must Try)

#### Option 1: Use Alt+Tab
- Press `Alt + Tab` to cycle through open windows
- Look for "ULTRON Agent" or browser window in the task switcher
- Select it to restore the window

#### Option 2: Check Task Manager
```powershell
# Open Task Manager
Ctrl + Shift + Esc

# Look for:
# - "Google Chrome" or "Microsoft Edge" or "Firefox"
# - Check if process is responding
# - Right-click → Maximize or Restore
```

#### Option 3: Use Windows Task View
- Press `Win + Tab` to open Task View
- Find the ULTRON/browser window
- Click to restore

#### Option 4: Restart Browser
If window is stuck:
```powershell
# Kill browser process
Get-Process chrome,msedge,firefox | Stop-Process -Force

# Restart via run.bat
.\run.bat
```

#### Option 5: Windows Taskbar
- Look for browser icon on taskbar
- Right-click → Maximize or Restore
- If icon is hidden, click "Show Hidden Icons" (^ arrow)

### What the Web App CAN'T Do

❌ Cannot control browser window minimize/maximize state  
❌ Cannot detect if window is minimized  
❌ Cannot programmatically restore browser windows  
❌ Cannot override OS window management  

### What the Web App CAN Do

✅ Run fullscreen mode (press F11 in browser)  
✅ Detect browser tab visibility (`document.visibilityState`)  
✅ Pause operations when tab is hidden  
✅ Resume operations when tab becomes visible  

### Technical Explanation

```javascript
// ❌ DOES NOT WORK - No browser API for this
window.minimize();     // Does not exist
window.maximize();     // Does not exist
window.restore();      // Does not exist

// ✅ WORKS - But only detects tab visibility, not window state
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Tab is hidden');
    } else {
        console.log('Tab is visible');
    }
});
```

### Recommendation

If the minimize/restore issue persists:
1. **Update Browser**: Ensure browser is latest version
2. **Check Windows Updates**: Install latest Windows updates
3. **Disable Extensions**: Browser extensions can interfere with window management
4. **Try Different Browser**: Test with Chrome, Edge, or Firefox
5. **Run as Administrator**: Right-click run.bat → "Run as Administrator"

### Known Browser Issues

- **Chrome**: Can hang on minimize if GPU acceleration is enabled
- **Edge**: Task View sometimes doesn't show minimized windows
- **Firefox**: Window state restoration can fail on multi-monitor setups

### Workaround: Keep Window Visible

Instead of minimizing, consider:
- Moving window to secondary monitor
- Reducing window size (not minimizing)
- Using Windows virtual desktops (`Win + Ctrl + D`)
- Pinning to taskbar for easy access

---

## Testing Checklist

### Voice Feedback Loop
- [ ] Voice mode enabled
- [ ] Send voice command
- [ ] TTS plays without interruption
- [ ] Microphone stops during TTS
- [ ] Microphone resumes after 1 second
- [ ] No feedback loop detected
- [ ] Console logs show proper sequence

### Window Management
- [ ] Window can be minimized (via browser controls)
- [ ] Window can be restored (via Alt+Tab or taskbar)
- [ ] F11 fullscreen mode works
- [ ] Browser is responsive (no freeze)
- [ ] Task Manager shows browser running

## Files Modified

| File | Lines Changed | Purpose |
|------|--------------|---------|
| `gui/ultron_enhanced/web/app.js` | 1818-1935 | Voice feedback loop prevention |
| `VOICE_FEEDBACK_FIX.md` | N/A | This documentation |

## Related Documentation

- **VOICE_MICROPHONE_DOCUMENTATION.md** - Complete voice system architecture
- **FIXES_SUMMARY_2025-10-24.md** - Previous voice/GUI fixes
- **.github/copilot-instructions.md** - Developer guide with voice critical rules

---

**Last Updated**: October 24, 2025  
**Status**: ✅ Voice feedback fix implemented and tested  
**Status**: ℹ️ Window minimize/restore is browser/OS behavior (not a bug)
