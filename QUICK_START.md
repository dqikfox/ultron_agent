# ULTRON Agent 3.0 - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Verify Integration
```bash
python verify_integration.py
```
Expected output: `18/18 checks passed`

### Step 2: Start ULTRON
```bash
.\run.bat
```
Wait for: `ULTRON AGENT 3.0 - READY`

### Step 3: Test It
Open browser to: http://localhost:8080

Or try voice command: **"Hey ULTRON, take a screenshot"**

---

## ✅ What's Integrated

| Feature | Status | Command Example |
|---------|--------|-----------------|
| Autonomous Desktop Control | ✅ | "take a screenshot" |
| Cloud Integration (Cheap) | ✅ | "route to cheapest provider" |
| Proactive Assistant | ✅ | Auto-suggests after 5 min |
| Voice Control | ✅ | "Hey ULTRON, ..." |
| Web GUI | ✅ | http://localhost:8080 |
| API Server | ✅ | http://localhost:5000 |
| Avatar Game | ✅ | http://localhost:8082 |

---

## 🎯 Try These Commands

### Desktop Automation
```
"take a screenshot"
"move mouse to center"
"get screen size"
"click at current position"
"type hello world"
```

### Cloud Operations
```
"route this to Groq"
"save to cloud storage"
"use cheapest provider"
```

### System Info
```
"what tools do you have?"
"show system status"
"list available models"
```

---

## 📊 Services Running

After `run.bat` starts, you'll have:

| Service | Port | URL |
|---------|------|-----|
| Web GUI | 8080 | http://localhost:8080 |
| API Server | 5000 | http://localhost:5000 |
| Avatar Game | 8082 | http://localhost:8082 |
| ADB Backend | 5003 | http://localhost:5003 |
| Ollama | 11434 | http://localhost:11434 |

---

## 🔧 Quick Troubleshooting

### "Port already in use"
```bash
# run.bat automatically kills conflicting processes
# Just run it again
.\run.bat
```

### "Tool not loading"
```bash
# Verify integration
python verify_integration.py

# Check logs
type logs\agent_core.log
```

### "PyAutoGUI not working"
```bash
pip install pyautogui
```

### "Cloud commands fail"
```bash
# Set API keys
set GROQ_API_KEY=your_key_here

# Or run setup
.\setup_cheap_cloud.bat
```

---

## 📚 Documentation

- **Full Integration**: `INTEGRATION_COMPLETE.md`
- **Detailed Status**: `INTEGRATION_STATUS.md`
- **Autonomous Control**: `AUTONOMOUS_CONTROL_GUIDE.md`
- **Cloud Setup**: `CLOUD_CHEAP_SETUP.md`
- **Improvements**: `IMPROVEMENT_ROADMAP.md`

---

## 🎉 You're Ready!

Everything is integrated and working. Just run:

```bash
.\run.bat
```

And start using ULTRON Agent 3.0 with all new features!

---

**Questions?** Check `INTEGRATION_COMPLETE.md` for detailed info.
