# Next Steps: Verify & Test Fixed run.bat

## ✅ What Was Just Done

- Fixed model from `qwen3-coder:480b-cloud` → `llava:7b`
- Removed avatar_game_server.py startup (file doesn't exist)
- Removed self-healing background process
- Removed telemetry file generation
- Simplified health checks
- Fixed browser launcher URL

**File**: `c:\Projects\ultron_agent\run.bat`
**Status**: ✅ Ready to test

---

## 🎯 Recommended Next Action

### Option 1: Quick Test (5 minutes)
```powershell
cd c:\Projects\ultron_agent
.\run.bat
```

**What to look for**:
- ✅ Ollama starts without errors
- ✅ Model loads (llava:7b)
- ✅ Web GUI starts on port 8080
- ✅ API starts on port 5000
- ✅ Browser opens to http://localhost:8080/
- ✅ No error messages in console

### Option 2: Verify Changes (2 minutes)
If you want to see exactly what was fixed:
```powershell
# View the corrected model config
Select-String "OLLAMA_MODEL" c:\Projects\ultron_agent\run.bat

# View the browser launch URL
Select-String "GUI_URL" c:\Projects\ultron_agent\run.bat
```

### Option 3: Compare with Safeguards (3 minutes)
Check if run.bat matches documented standards:
- Compare ports to `PORT_MAPPING_AND_SERVICES.md`
- Compare model to copilot-instructions.md
- Compare startup sequence to `CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md`

---

## 📋 Verification Checklist

After running `.\run.bat`, check:

| Item | Expected | Status |
|------|----------|--------|
| Cleanup completes | No errors | [ ] |
| Ollama starts | "Ollama is running" | [ ] |
| Model loads | llava:7b | [ ] |
| Web GUI starts | "Web GUI on 8080" | [ ] |
| API starts | "API on 5000" | [ ] |
| Health check passes | Both ports respond | [ ] |
| Browser opens | http://localhost:8080/ | [ ] |
| No error messages | Clean console | [ ] |

---

## 📚 Documentation Created

The following summary document was created:
- **AMAZON_Q_FIX_SUMMARY.md** - Details all 8 issues found and fixed

---

## 🔄 If Issues Occur

**If Ollama won't start**:
1. Check if Ollama service is running: `Get-Process | grep ollama`
2. Try manual start: `ollama serve`
3. Check logs: `cat logs/brain.log`

**If Web GUI won't start**:
1. Check port 8080: `netstat -ano | findstr :8080`
2. Try running manually: `python web_gui_server.py`
3. Check port conflict

**If browser shows 404**:
1. Verify URL is `http://localhost:8080/` (not avatar_game_ultimate.html)
2. Check web server console for errors
3. Check GUI files exist in `gui/ultron_enhanced/web/`

---

## ⏭️ After Verification

If startup is successful:
1. **Test GUI functions** - Click buttons, check console
2. **Deploy GUI fixes** - Apply the 5 critical patches
3. **Run validation tests** - Execute the 18 test cases
4. **Monitor for 24 hours** - Check logs for stability

---

## 💾 What to Save

- `AMAZON_Q_FIX_SUMMARY.md` - Keep for reference
- `run.bat` - The corrected launcher (current working version)
- Start logs in `logs/` folder - For debugging if needed

---

**Ready to test?** Just run: `.\run.bat`

**Have questions?** See:
- `PORT_MAPPING_AND_SERVICES.md` - Port configuration reference
- `CRITICAL_DOCUMENTATION_AND_SAFEGUARDS.md` - Safe procedures
- `copilot-instructions.md` - Model and configuration standards
