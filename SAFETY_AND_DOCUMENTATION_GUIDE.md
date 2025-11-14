# ULTRON AGENT 3.0 - SAFETY AND DOCUMENTATION GUIDE

**Last Updated**: October 29, 2025
**Purpose**: Master guide for making changes safely and keeping system stable

---

## 🚨 CRITICAL: READ THIS FIRST

**ULTRON Agent 3.0 is a complex multi-service system with interdependencies.** Incorrect changes can:
- Break the GUI (port 8080 becomes inaccessible)
- Break the AI engine (Ollama at port 11434 stops responding)
- Break the API (port 5000 becomes unreachable)
- Cause port conflicts that prevent startup
- Create circular dependencies that crash the system

**This guide prevents all of those problems.**

---

## 📋 BEFORE YOU MAKE ANY CHANGE

### Pre-Change Checklist (MANDATORY)

1. **Read the relevant documentation**:
   - PORT_MAPPING_AND_SERVICES.md (if changing ports)
   - CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md (if changing core files)
   - DEPLOYMENT_SCRIPT_STEP_BY_STEP.md (if deploying GUI fixes)

2. **Identify what you're changing**:
   - [ ] What file(s) will be modified?
   - [ ] What port(s) are involved?
   - [ ] What service(s) will be affected?
   - [ ] Will startup sequence change?

3. **Check dependencies**:
   - Does Ollama (port 11434) depend on this?
   - Does Web GUI (port 8080) depend on this?
   - Does API Server (port 5000) depend on this?
   - Are there circular dependencies?

4. **Create a backup**:
   ```powershell
   # Backup the file you're changing
   Copy-Item -Path "path/to/file.py" -Destination "path/to/file.py.backup"

   # Or use Git
   git add .
   git commit -m "backup: snapshot before [change name]"
   ```

5. **Create a changelog entry**:
   - Open CHANGELOG_TEMPLATE.md
   - Copy the template
   - Fill in all required fields
   - Add to changelog at top of "Recent Changes"

6. **Plan your verification**:
   - What tests will you run after the change?
   - How will you verify it works?
   - How will you know if it breaks?

7. **Plan your rollback**:
   - Can you just restore the backup?
   - Do you need to restart services?
   - Will you need to clear any caches?

8. **Check for conflicts**:
   - Does this port conflict with another service?
   - Does this change conflict with existing functionality?
   - Are there hardcoded references elsewhere?

9. **Document your changes**:
   - Add inline comments in code
   - Update the changelog
   - Note any manual steps required

10. **Get approval** (if team environment):
    - Code review from another team member
    - Approval to deploy to production

---

## 🔒 CORE FILES - DO NOT EDIT

These files are **critical to system operation**. Only edit if you fully understand the consequences.

### CRITICAL - Do Not Touch Without Full Understanding

| File | Why Critical | Who Can Edit |
|------|-------------|-------------|
| **main.py** | System entry point, signal handlers | Only senior developers |
| **agent_core.py** | Service initialization, component lifecycle | Only senior developers |
| **brain.py** | AI reasoning, Ollama integration | Only AI specialists |
| **web_gui_server.py** | Web interface, port 8080 binding | UI specialists + code review |
| **api_server.py** | REST API, port 5000 binding | API specialists + code review |

### CAREFUL - Edit With Extreme Caution

| File | Why Important | Change Impact |
|------|--------------|----------------|
| **ultron_config.json** | ALL ports defined here | Entire system may not start |
| **run.bat** | Service startup sequence | System may fail to boot |

### SAFE - Generally Safe to Edit

| File | Why Safe | Can Edit |
|------|----------|----------|
| **Documentation files** | No runtime impact | Anyone |
| **Logging files** | Generated at runtime | System clears |
| **GUI assets** (CSS, HTML basic structure) | Non-core functionality | UI developers |

---

## 🎯 HOW TO MAKE A SAFE CHANGE

### Step 1: Understand The System

Read PORT_MAPPING_AND_SERVICES.md and understand:
- What ports are used (11434, 8080, 5000, etc.)
- What services depend on what
- What the startup sequence is
- What could break if you change this

### Step 2: Plan Your Change

Fill out this form:

```markdown
## My Planned Change

**What am I changing?**
[File name and what part]

**Why am I changing it?**
[The problem or feature]

**What ports are involved?**
[List all ports affected]

**What services are affected?**
[GUI? AI? API?]

**Will startup change?**
[Yes/No - if yes, how?]

**What could break?**
[Worst-case scenarios]

**How will I verify it works?**
[Test steps]

**How will I rollback if it breaks?**
[Rollback procedure]
```

### Step 3: Create A Backup

```powershell
# Option 1: Simple file backup
Copy-Item "file.py" "file.py.backup"

# Option 2: Git commit
git add .
git commit -m "backup: before making [change]"

# Option 3: Timestamp backup
$date = Get-Date -Format "yyyy-MM-dd_HHmmss"
Copy-Item "file.py" "file.py.backup.$date"
```

### Step 4: Make The Change

- Keep changes **minimal and focused**
- Add comments explaining why
- Don't refactor unrelated code
- Update all related files
- Check for hardcoded values

### Step 5: Update Documentation

1. Update CHANGELOG_TEMPLATE.md with entry
2. Add inline comments in code
3. Update any related documentation
4. List all files modified

### Step 6: Test Thoroughly

```powershell
# 1. Check syntax
python -m py_compile file.py

# 2. Start the system
.\run.bat

# 3. Run specific tests
pytest -m unit -v

# 4. Manual testing
# - Open GUI at http://localhost:8080
# - Try affected features
# - Check browser console (F12) for errors
# - Check service logs in logs/ directory

# 5. Verify ports
netstat -ano | findstr "11434\|8080\|5000"
```

### Step 7: If It Works

```powershell
# Commit your change
git add .
git commit -m "feat: [your change] - [brief description]"

# Clean up backups
Remove-Item "file.py.backup*"

# Document in CHANGELOG
# [Add entry to CHANGELOG_TEMPLATE.md]
```

### Step 8: If It Breaks

```powershell
# Option 1: Restore from backup
Copy-Item "file.py.backup" "file.py"

# Option 2: Git rollback
git checkout HEAD -- file.py

# Option 3: Git revert (if already committed)
git revert HEAD

# Restart services
Stop-Process -Name "python" -Force
Start-Sleep -Seconds 2
.\run.bat
```

---

## 🚨 EMERGENCY PROCEDURES

### If The System Won't Start

1. **Check service logs**:
   ```powershell
   Get-Content logs/agent_core.log -Tail 50
   Get-Content logs/brain.log -Tail 50
   ```

2. **Check if ports are available**:
   ```powershell
   netstat -ano | findstr "11434\|8080\|5000"
   ```

3. **Kill existing processes**:
   ```powershell
   Stop-Process -Name "ollama", "python" -Force
   Start-Sleep -Seconds 3
   ```

4. **Restore last known good version**:
   ```powershell
   git status  # See what changed
   git diff    # See specific changes
   git checkout HEAD -- .  # Restore everything
   ```

5. **Restart from scratch**:
   ```powershell
   .\run.bat  # Fresh start
   ```

### If Port Is Already In Use

```powershell
# Find what's using the port
$port = 8080
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
           Select-Object OwningProcess
Stop-Process -Id $process.OwningProcess -Force

# Then restart services
.\run.bat
```

### If GUI Won't Load

1. Check web server is running:
   ```powershell
   curl http://localhost:8080/
   ```

2. Check browser console (F12) for errors

3. Check web server logs:
   ```powershell
   Get-Content logs/web_gui_server.log -Tail 50
   ```

4. Restart web server:
   ```powershell
   python web_gui_server.py
   ```

### If AI Doesn't Respond

1. Check Ollama is running:
   ```powershell
   curl http://localhost:11434/api/tags
   ```

2. Check model is loaded:
   ```powershell
   ollama list | findstr "llava"
   ```

3. Pull model if missing:
   ```powershell
   ollama pull llava:7b
   ```

4. Restart Ollama:
   ```powershell
   Stop-Process -Name "ollama" -Force
   ollama serve
   ```

---

## 📝 DOCUMENTATION CHECKLIST

Every change should have:

- [ ] **Changelog entry** - What changed and why
- [ ] **Inline comments** - Explain tricky logic
- [ ] **Port documentation** - If ports affected
- [ ] **Dependency documentation** - If dependencies changed
- [ ] **Rollback procedure** - How to undo the change
- [ ] **Verification steps** - How to test it works
- [ ] **Test cases** - What tests cover the change

---

## 🔄 KEEPING THINGS IN SYNC

### When Changing Ports

1. Update **ultron_config.json** (source of truth):
   ```json
   {
     "api_port": 5000,
     "ollama_base_url": "http://localhost:11434"
   }
   ```

2. Update **run.bat** (startup script):
   ```batch
   set API_SERVER_PORT=5000
   set OLLAMA_PORT=11434
   ```

3. Update **PORT_MAPPING_AND_SERVICES.md** (documentation)

4. Update **CHANGELOG_TEMPLATE.md** (change history)

5. Search for hardcoded values:
   ```powershell
   grep -r "localhost:8080" --include="*.py" --include="*.js"
   grep -r "localhost:11434" --include="*.py" --include="*.js"
   ```

6. Update any found hardcoded references

### When Changing Configuration

1. Change value in **ultron_config.json**
2. Verify in code it reads from config (not hardcoded)
3. Test that startup picks up the new value
4. Document in changelog
5. Update relevant .md files

### When Changing Service Startup

1. Update **run.bat** startup sequence
2. Verify new sequence doesn't create circular dependencies
3. Test full startup with `.\run.bat`
4. Document in PORT_MAPPING_AND_SERVICES.md
5. Update startup sequence diagram
6. Document in changelog

---

## 📊 VERIFICATION CHECKLIST

After making a change, verify:

- [ ] **Syntax**: `python -m py_compile file.py` passes
- [ ] **Imports**: All imports resolve, no missing modules
- [ ] **Ports**: Correct ports are used, no conflicts
- [ ] **Config**: Configuration reads correctly
- [ ] **Startup**: System starts without errors
- [ ] **GUI**: http://localhost:8080 loads
- [ ] **API**: `curl http://localhost:5000/health` responds
- [ ] **AI**: Ollama responds to requests
- [ ] **Tests**: `pytest` passes (at least unit tests)
- [ ] **Logs**: No error messages in logs/
- [ ] **Rollback**: Backup file/git works
- [ ] **Documentation**: All docs updated

---

## 📚 RELATED DOCUMENTATION

- **PORT_MAPPING_AND_SERVICES.md** - Complete port reference
- **CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md** - Non-negotiable rules
- **CHANGELOG_TEMPLATE.md** - How to document changes
- **DEPLOYMENT_SCRIPT_STEP_BY_STEP.md** - For GUI fixes
- **FIXES_SUMMARY_2025-10-24.md** - Recent fixes and improvements

---

## ✅ SUMMARY

**Safe changes follow this pattern**:

1. Read documentation → 2. Understand impact → 3. Create backup → 4. Make change
5. → 6. Update docs → 7. Test thoroughly → 8. Commit

**Dangerous changes are**:
- Editing core files without understanding
- Changing ports without updating all references
- Not documenting changes
- Not creating backups
- Not testing before deploying

**Emergency procedures exist for when things break:**
- Restore from backup
- Use `git checkout` to undo
- Restart services
- Check logs for errors

---

**Remember**: A change that works but nobody understands is a liability. A change that's well-documented and tested is an asset.
