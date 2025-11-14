# 🛡️ GUI Protection System - ULTRON AETHER NEXUS INTERFACE

## 🚨 PROBLEM IDENTIFIED

Your GUI keeps losing functionality because:

1. **File Overwrites**: AI assistants or automated tools overwrite files without preserving content
2. **No Version Control**: Changes aren't tracked before modifications
3. **Missing Backups**: No automatic backup system before edits
4. **Concurrent Edits**: Multiple tools editing simultaneously
5. **Cache Issues**: Browser/server caching old versions

## ✅ SOLUTION: 4-Layer Protection System

### Layer 1: Automatic Backup System

**File**: `backup_gui.bat`
```batch
@echo off
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=gui\ultron_enhanced\web\backups\%TIMESTAMP%

echo Creating GUI backup: %BACKUP_DIR%
mkdir "%BACKUP_DIR%" 2>nul

copy "gui\ultron_enhanced\web\index.html" "%BACKUP_DIR%\index.html" >nul
copy "gui\ultron_enhanced\web\app.js" "%BACKUP_DIR%\app.js" >nul
copy "gui\ultron_enhanced\web\styles.css" "%BACKUP_DIR%\styles.css" >nul

echo ✓ Backup created: %BACKUP_DIR%
```

**Usage**: Run `backup_gui.bat` BEFORE any edits

### Layer 2: Git Pre-Commit Hook

**File**: `.git/hooks/pre-commit`
```bash
#!/bin/bash
# Auto-backup GUI files before commit

GUI_FILES=(
    "gui/ultron_enhanced/web/index.html"
    "gui/ultron_enhanced/web/app.js"
    "gui/ultron_enhanced/web/styles.css"
)

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="gui/ultron_enhanced/web/backups/$TIMESTAMP"

for file in "${GUI_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "$file"; then
        mkdir -p "$BACKUP_DIR"
        cp "$file" "$BACKUP_DIR/"
        echo "✓ Backed up: $file"
    fi
done
```

### Layer 3: File Integrity Monitor

**File**: `monitor_gui.py`
```python
import os
import hashlib
import json
from datetime import datetime

GUI_FILES = {
    'index.html': 'gui/ultron_enhanced/web/index.html',
    'app.js': 'gui/ultron_enhanced/web/app.js',
    'styles.css': 'gui/ultron_enhanced/web/styles.css'
}

INTEGRITY_FILE = 'gui/ultron_enhanced/web/.integrity.json'

def get_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def save_integrity():
    integrity = {}
    for name, path in GUI_FILES.items():
        if os.path.exists(path):
            integrity[name] = {
                'hash': get_file_hash(path),
                'size': os.path.getsize(path),
                'modified': datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            }
    with open(INTEGRITY_FILE, 'w') as f:
        json.dump(integrity, f, indent=2)
    print("✓ Integrity baseline saved")

def check_integrity():
    if not os.path.exists(INTEGRITY_FILE):
        print("⚠ No integrity baseline found. Run with --save first.")
        return
    
    with open(INTEGRITY_FILE) as f:
        baseline = json.load(f)
    
    issues = []
    for name, path in GUI_FILES.items():
        if not os.path.exists(path):
            issues.append(f"❌ MISSING: {name}")
            continue
        
        current_hash = get_file_hash(path)
        current_size = os.path.getsize(path)
        
        if name in baseline:
            if current_hash != baseline[name]['hash']:
                issues.append(f"⚠ MODIFIED: {name}")
            if current_size < baseline[name]['size'] * 0.5:
                issues.append(f"🚨 SIZE REDUCED >50%: {name}")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("✓ All GUI files intact")
        return True

if __name__ == '__main__':
    import sys
    if '--save' in sys.argv:
        save_integrity()
    else:
        check_integrity()
```

### Layer 4: Protected File Attributes

**File**: `protect_gui.bat`
```batch
@echo off
echo Protecting GUI files from accidental modification...

attrib +r "gui\ultron_enhanced\web\index.html"
attrib +r "gui\ultron_enhanced\web\app.js"
attrib +r "gui\ultron_enhanced\web\styles.css"

echo ✓ GUI files are now READ-ONLY
echo To edit: Run unprotect_gui.bat first
```

**File**: `unprotect_gui.bat`
```batch
@echo off
echo Removing protection from GUI files...

attrib -r "gui\ultron_enhanced\web\index.html"
attrib -r "gui\ultron_enhanced\web\app.js"
attrib -r "gui\ultron_enhanced\web\styles.css"

echo ✓ GUI files are now EDITABLE
echo Remember to run protect_gui.bat after editing!
```

## 🔧 RECOVERY PROCEDURE

### Step 1: Identify Latest Good Backup
```bash
# List all backups
dir /b /od gui\ultron_enhanced\web\backups

# Or check Git history
git log --oneline -- gui/ultron_enhanced/web/index.html
```

### Step 2: Restore from Backup
```batch
# Restore from timestamped backup
copy "gui\ultron_enhanced\web\backups\20250116_143022\*" "gui\ultron_enhanced\web\" /Y

# Or restore from Git
git checkout HEAD~1 -- gui/ultron_enhanced/web/index.html
git checkout HEAD~1 -- gui/ultron_enhanced/web/app.js
git checkout HEAD~1 -- gui/ultron_enhanced/web/styles.css
```

### Step 3: Verify Restoration
```bash
python monitor_gui.py
```

## 📋 DAILY WORKFLOW

### Before Editing
```batch
1. backup_gui.bat
2. unprotect_gui.bat
3. python monitor_gui.py --save
```

### After Editing
```batch
1. python monitor_gui.py
2. protect_gui.bat
3. git add gui/ultron_enhanced/web/*
4. git commit -m "GUI: [describe changes]"
```

## 🚫 PREVENTION RULES

### For AI Assistants (Amazon Q, Copilot, etc.)

Add to `.amazonq/rules/gui_protection.md`:
```markdown
# GUI Protection Rules

## CRITICAL: ULTRON AETHER NEXUS INTERFACE

1. **NEVER** modify `gui/ultron_enhanced/web/index.html` without explicit user request
2. **NEVER** overwrite `app.js` or `styles.css` completely
3. **ALWAYS** create backup before ANY GUI modification
4. **ALWAYS** verify file size after changes (must be >50% of original)
5. **ALWAYS** ask user to confirm before GUI changes

## Protected Files
- gui/ultron_enhanced/web/index.html (ULTRON AETHER NEXUS INTERFACE)
- gui/ultron_enhanced/web/app.js (Core functionality)
- gui/ultron_enhanced/web/styles.css (Visual styling)

## Before Modifying
1. Run: `backup_gui.bat`
2. Run: `python monitor_gui.py --save`
3. Get explicit user confirmation

## After Modifying
1. Run: `python monitor_gui.py`
2. Verify functionality in browser
3. Commit changes with descriptive message
```

### For Git

Add to `.gitattributes`:
```
gui/ultron_enhanced/web/index.html merge=ours
gui/ultron_enhanced/web/app.js merge=ours
gui/ultron_enhanced/web/styles.css merge=ours
```

Add to `.git/config`:
```ini
[merge "ours"]
    name = Keep our version on merge conflicts
    driver = true
```

## 🔍 DIAGNOSTIC COMMANDS

### Check File Status
```bash
# File sizes
dir gui\ultron_enhanced\web\*.html gui\ultron_enhanced\web\*.js gui\ultron_enhanced\web\*.css

# Git status
git status gui/ultron_enhanced/web/

# Recent changes
git log -5 --oneline -- gui/ultron_enhanced/web/
```

### Verify Functionality
```bash
# Start server
python web_gui_server.py

# Open browser
start http://localhost:8080

# Check console for errors
# Press F12 in browser
```

## 🆘 EMERGENCY RECOVERY

### If GUI is Broken RIGHT NOW

```batch
# Option 1: Restore from latest backup
copy "gui\ultron_enhanced\web\backups\[LATEST]\*" "gui\ultron_enhanced\web\" /Y

# Option 2: Restore from Git (last commit)
git checkout HEAD -- gui/ultron_enhanced/web/

# Option 3: Restore from specific backup file
copy "gui\ultron_enhanced\web\index - Copy.html" "gui\ultron_enhanced\web\index.html" /Y

# Option 4: Restore from Git history (2 commits ago)
git checkout HEAD~2 -- gui/ultron_enhanced/web/index.html
```

### Verify Recovery
```bash
1. Check file size: dir gui\ultron_enhanced\web\index.html
2. Open in browser: start http://localhost:8080
3. Test functionality: Click buttons, check console
```

## 📊 MONITORING DASHBOARD

Create `gui_health_check.bat`:
```batch
@echo off
echo ═══════════════════════════════════════
echo   ULTRON GUI HEALTH CHECK
echo ═══════════════════════════════════════
echo.

echo [1] File Sizes:
dir gui\ultron_enhanced\web\index.html | findstr "index.html"
dir gui\ultron_enhanced\web\app.js | findstr "app.js"
dir gui\ultron_enhanced\web\styles.css | findstr "styles.css"
echo.

echo [2] File Attributes:
attrib gui\ultron_enhanced\web\index.html
attrib gui\ultron_enhanced\web\app.js
attrib gui\ultron_enhanced\web\styles.css
echo.

echo [3] Recent Backups:
dir /b /od gui\ultron_enhanced\web\backups | findstr /r "^20"
echo.

echo [4] Git Status:
git status --short gui/ultron_enhanced/web/
echo.

echo [5] Integrity Check:
python monitor_gui.py
echo.

echo ═══════════════════════════════════════
pause
```

## 🎯 QUICK REFERENCE

| Command | Purpose |
|---------|---------|
| `backup_gui.bat` | Create timestamped backup |
| `protect_gui.bat` | Make files read-only |
| `unprotect_gui.bat` | Make files editable |
| `python monitor_gui.py --save` | Save integrity baseline |
| `python monitor_gui.py` | Check for changes |
| `gui_health_check.bat` | Full system check |

## 🔐 BEST PRACTICES

1. **Always backup before editing** - No exceptions!
2. **Use version control** - Commit after every working change
3. **Test immediately** - Verify functionality after edits
4. **Protect when done** - Run `protect_gui.bat` after editing
5. **Monitor regularly** - Run health check daily

## 📞 SUPPORT

If GUI breaks again:
1. Run `gui_health_check.bat`
2. Check latest backup: `dir /b /od gui\ultron_enhanced\web\backups`
3. Restore from backup or Git
4. Report issue with health check output

---

**Status**: 🛡️ Protection System Active  
**Last Updated**: 2025-01-16  
**Maintainer**: ULTRON Agent Team
