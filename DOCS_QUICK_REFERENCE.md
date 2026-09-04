# ULTRON Agent - Quick Documentation Reference

## 🔗 Internal Documentation (Bookmarks)

### Core Company Resources
- 🌐 **API Docs**: https://internal.docs/api
- 🏗️ **Architecture**: https://internal.docs/architecture
- 🚀 **Deployment**: https://internal.docs/deployment

---

## 📚 Local Documentation Files

| Purpose | File | Open With |
|---------|------|-----------|
| **Start Here** | `.github/copilot-instructions.md` | Developer guide |
| **Voice System** | `VOICE_MICROPHONE_DOCUMENTATION.md` | Voice/audio work |
| **MCP Integration** | `MCP_INTEGRATION_GUIDE.md` | External tools |
| **Architecture** | `SYSTEM_ARCHITECTURE.md` | Component details |
| **Setup** | `SETUP_CHECKLIST.md` | First-time setup |
| **Recent Fixes** | `FIXES_SUMMARY_2025-10-24.md` | Latest changes |
| **Full Index** | `DOCUMENTATION_HUB.md` | All documentation |

---

## 🎯 Quick Actions

### Open Documentation
```powershell
# In VS Code: Press Ctrl+P, type filename

# In terminal:
code .github/copilot-instructions.md
code DOCUMENTATION_HUB.md
code MCP_INTEGRATION_GUIDE.md
```

### Search Documentation
```powershell
# Search all markdown files
Get-ChildItem -Filter *.md -Recurse | Select-String "your_search_term"

# Search specific file
Get-Content DOCUMENTATION_HUB.md | Select-String "API"
```

### Access Internal Docs
```powershell
# Open in browser
Start-Process "https://internal.docs/api"
Start-Process "https://internal.docs/architecture"
Start-Process "https://internal.docs/deployment"
```

---

## 🔍 Quick Answers

### "Where is the API documentation?"
- **Company API**: https://internal.docs/api
- **ULTRON API**: `API.md` file
- **Implementation**: `api_server.py`

### "How do I deploy?"
- **Process Guide**: https://internal.docs/deployment
- **ULTRON Launcher**: `run.bat`
- **Health Checks**: `ultron_master_startup.log`

### "How is the system designed?"
- **Company Architecture**: https://internal.docs/architecture
- **ULTRON Architecture**: `SYSTEM_ARCHITECTURE.md`
- **Design Decisions**: `ARCHITECTURE_DESIGN.md`

### "How do I add a new tool?"
- **Guide**: `.github/copilot-instructions.md` → "Tool Development Pattern"
- **Interface**: `tools/tool_interface.py`
- **Examples**: Any file in `tools/` directory

### "How do I use MCP servers?"
- **Full Guide**: `MCP_INTEGRATION_GUIDE.md`
- **Quick Commands**: `MCP_QUICK_REFERENCE.md`
- **Config**: `mcp.json`

---

## 📞 Help Resources

| Need Help With | Check |
|---------------|-------|
| API questions | https://internal.docs/api |
| Architecture questions | https://internal.docs/architecture |
| Deployment issues | https://internal.docs/deployment |
| Voice system | `VOICE_MICROPHONE_DOCUMENTATION.md` |
| MCP integration | `MCP_INTEGRATION_GUIDE.md` |
| General development | `.github/copilot-instructions.md` |
| All documentation | `DOCUMENTATION_HUB.md` |

---

**Last Updated**: October 25, 2025
**ULTRON Agent**: Version 3.0

**Tip**: Bookmark this file for instant access to all documentation!
