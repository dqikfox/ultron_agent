# ULTRON AGENT 3.0 - QUICK REFERENCE SAFEGUARDS

**Keep this handy while developing**

---

## 🚨 5 CRITICAL RULES (NEVER BREAK THESE)

1. **NEVER change ports** without reading PORT_MAPPING_AND_SERVICES.md
2. **NEVER delete core files** without understanding consequences
3. **ALWAYS test** before deploying
4. **ALWAYS backup** before changing
5. **ALWAYS document** your changes

---

## 🔴 CORE FILES - DO NOT TOUCH

```
❌ main.py              → System entry point
❌ agent_core.py        → Service initialization
❌ brain.py             → AI engine (Ollama integration)
❌ web_gui_server.py    → Web interface (port 8080)
❌ api_server.py        → REST API (port 5000)
```

**Edit Only If**:
- [ ] You understand the full consequences
- [ ] You have a backup
- [ ] You will test thoroughly
- [ ] You have a rollback plan

---

## 🟡 CAREFUL FILES - EDIT WITH EXTREME CARE

```
⚠️ ultron_config.json   → ALL ports defined here
⚠️ run.bat              → Service startup sequence
```

**Before Editing**:
- [ ] Read PORT_MAPPING_AND_SERVICES.md
- [ ] Understand all references to this value
- [ ] Search for hardcoded duplicates
- [ ] Update changelog
- [ ] Test full startup

---

## 🟢 SAFE FILES - GENERALLY OK TO EDIT

```
✅ Documentation files (.md)
✅ Logging files (auto-generated)
✅ GUI assets (CSS, HTML basic structure)
```

---

## 📊 PORT QUICK REFERENCE

| Port | Service | Status | What It Does |
|------|---------|--------|-------------|
| **11434** | Ollama | PRIMARY | AI inference engine |
| **8080** | Web GUI | PRIMARY | Pokédex interface |
| **5000** | API Server | CRITICAL | Command execution |
| 7861 | LangFlow | Optional | Workflow automation |
| 8081 | AutoGen | Optional | Multi-agent orchestration |
| 5001 | Diagnostics | Optional | Performance monitoring |
| 5003 | ADB | Optional | Android device control |

**Key Fact**: Ollama (11434) must start first. Everything depends on it.

---

## ⚡ 10-ITEM PRE-CHANGE CHECKLIST

Before modifying ANY code:

- [ ] 1. What file(s) will I change?
- [ ] 2. What port(s) are involved?
- [ ] 3. What service(s) will be affected?
- [ ] 4. Will startup sequence change?
- [ ] 5. Do I have dependencies documented?
- [ ] 6. Is there a backup ready?
- [ ] 7. Do I know how to test this?
- [ ] 8. Do I have a rollback plan?
- [ ] 9. Can I explain this change in 2 sentences?
- [ ] 10. Will I document this in changelog?

**If you can't check all 10**: STOP - Read documentation first

---

## 🔄 8-STEP SAFE CHANGE PROCEDURE

1. **Read**: SAFETY_AND_DOCUMENTATION_GUIDE.md
2. **Plan**: Write down exactly what you're changing and why
3. **Backup**: `Copy-Item "file.py" "file.py.backup"` or `git commit`
4. **Change**: Make MINIMAL, FOCUSED changes only
5. **Document**: Add comments + changelog entry
6. **Test**: Run verification checklist (13 items)
7. **Verify**: All tests pass, no console errors
8. **Commit**: `git add . && git commit -m "feat: description"`

---

## 🆘 QUICK TROUBLESHOOTING

### "GUI won't load"
→ Check: `curl http://localhost:8080`
→ Fix: CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md → Emergency Procedures

### "AI doesn't respond"
→ Check: `curl http://localhost:11434/api/tags`
→ Fix: PORT_MAPPING_AND_SERVICES.md → Common Failures

### "Port already in use"
→ Find: `netstat -ano | findstr "8080"` (replace with your port)
→ Kill: `Stop-Process -Id [PID] -Force`

### "System won't start"
→ Check: `Get-Content logs/agent_core.log -Tail 50`
→ Fix: SAFETY_AND_DOCUMENTATION_GUIDE.md → Emergency Procedures

### "My change broke something"
→ Rollback: `git checkout HEAD -- [file]`
→ Or: Copy from backup: `Copy-Item "file.backup" "file"`

---

## 📋 13-ITEM VERIFICATION CHECKLIST

After making a change, verify:

- [ ] Syntax: `python -m py_compile file.py`
- [ ] Imports: All imports resolve
- [ ] Ports: No conflicts, correct ports used
- [ ] Config: Configuration reads correctly
- [ ] Startup: `.\run.bat` completes without errors
- [ ] GUI: `http://localhost:8080` loads
- [ ] API: `curl http://localhost:5000/health` responds
- [ ] AI: Ollama responds to requests
- [ ] Tests: `pytest -m unit` passes
- [ ] Logs: No error messages in logs/
- [ ] Backup: Can restore from backup
- [ ] Rollback: Git rollback works
- [ ] Documentation: All docs updated

**All must pass before deployment**

---

## 📁 DOCUMENTATION QUICK LINKS

| Need | File |
|------|------|
| System overview | SAFETY_AND_DOCUMENTATION_GUIDE.md |
| Port questions | PORT_MAPPING_AND_SERVICES.md |
| Critical files | CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md |
| Emergency procedures | CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md |
| Documentation | CHANGELOG_TEMPLATE.md |
| Navigation | SAFEGUARD_AND_DOCUMENTATION_INDEX.md |
| Scenarios | SAFEGUARD_AND_DOCUMENTATION_INDEX.md |

---

## ✅ BEFORE YOU CODE

Ask yourself:

1. Have I read the relevant documentation? **YES / NO**
2. Do I understand the consequences? **YES / NO**
3. Do I have a backup? **YES / NO**
4. Do I know how to test this? **YES / NO**
5. Do I have a rollback plan? **YES / NO**

**If ANY is NO**: Stop and read documentation first

---

## 🎯 MOST COMMON MISTAKES

❌ Changing port without updating all references
❌ Editing core files without understanding
❌ Not testing before deploying
❌ Not backing up before changing
❌ Not documenting changes
❌ Deleting files instead of disabling features
❌ Hardcoding values instead of using config
❌ Not checking logs when something fails

✅ Do the opposite of all these

---

## 🚀 AFTER YOUR CHANGE

1. **Test**: Run verification checklist
2. **Document**: Add changelog entry
3. **Commit**: `git commit -m "feat: description"`
4. **Verify**: No errors in deployment
5. **Monitor**: Check logs for 24 hours

---

## 📞 IF YOU'RE STUCK

1. Read the relevant documentation file (see Quick Links)
2. Check emergency procedures in CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md
3. Look at logs in logs/ directory
4. Try rollback: `git checkout HEAD -- [file]`
5. Restore from backup if available
6. If completely stuck: Full system restart `.\run.bat`

---

**Remember**: A working system is better than a broken "improvement"

Keep this guide accessible while coding.
