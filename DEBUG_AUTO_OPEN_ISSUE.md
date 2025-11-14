# Debugging Auto-Open Menus Issue

## How to Find the Root Cause

The GUI now has **detailed logging** to show us EXACTLY where the auto-opens are coming from.

### Steps to Debug:

1. **Open Browser DevTools**
   - Press `F12` or right-click → "Inspect"
   - Click the **Console** tab

2. **Reload the Page**
   - Press `Ctrl+R` to reload at `http://localhost:8080`
   - Look for logs starting with `[ULTRON]`

3. **Click the "Initialize" Button**
   - Watch the console for output

4. **Look for These Messages**:

#### If Power Menu Opens Unexpectedly:
```
[ULTRON] showPowerMenu() called, flag=false
[ULTRON] Call stack:
  (shows file names and line numbers of where the call came from)
```

#### If Model Switcher Opens Unexpectedly:
```
[ULTRON] performModelSwitch() called
[ULTRON] Model switch call stack:
  (shows file names and line numbers of where the call came from)
```

### What the Stack Trace Tells Us:

The stack trace will show the CALL CHAIN, like:
```
handleStartupAnnouncement (app.js:405)
  → someOtherFunction (app.js:412)
    → performModelSwitch (app.js:1694)
```

This tells us that `handleStartupAnnouncement` is calling something that eventually calls `performModelSwitch`.

## Example Output on Startup

**Good startup** (no auto-opens):
```
[ULTRON] ❌ showPowerMenu() BLOCKED - powerMenuInitialized is false
```

**Bad startup** (menu opens):
```
[ULTRON] showPowerMenu() called, flag=false
[ULTRON] Call stack:
  at HTMLDocument.click (app.js:197)
  at handleStartupAnnouncement (app.js:410)
  at UltronPokedexInterface.initializeAfterStart (app.js:389)
```

## How to Share Debug Info

Once you see the stack trace:
1. Copy the console output (Ctrl+A, Ctrl+C in console)
2. Paste it in a message
3. We'll know exactly what's calling these functions!

## Expected Behavior

- ✅ No modals should open on page load
- ✅ No modals should open after clicking Initialize
- ✅ Power menu should ONLY open when you click the power button
- ✅ Model switcher should ONLY open when you click "Switch Model" button

---

*This debug output is temporary and will help us fix the issue once and for all!*
