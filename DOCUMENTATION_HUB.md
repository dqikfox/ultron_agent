# ULTRON Agent 3.0 - Documentation Hub

## 📚 Complete Documentation Index

### 🏗️ Internal Documentation (Company/Team)

#### API Documentation
**Link**: https://internal.docs/api

**Topics Covered**:
- REST API endpoints reference
- Request/response formats
- Authentication and authorization
- Rate limiting and quotas
- Error codes and handling
- API versioning strategy
- WebSocket endpoints
- GraphQL schema (if applicable)

**Integration with ULTRON**:
- ULTRON API Server: `api_server.py` (port 5000)
- Endpoints: `/health`, `/command`, `/api/tools/*`
- See: `API.md` for ULTRON-specific API documentation

#### Architecture Guide
**Link**: https://internal.docs/architecture

**Topics Covered**:
- System design principles
- Architectural patterns
- Component relationships
- Data flow diagrams
- Security architecture
- Scalability considerations
- Technology stack decisions
- Infrastructure overview

**ULTRON-Specific Architecture**:
- See: `SYSTEM_ARCHITECTURE.md` for ULTRON component details
- See: `ARCHITECTURE_DESIGN.md` for design decisions
- See: `.github/copilot-instructions.md` for implementation patterns

#### Deployment Process
**Link**: https://internal.docs/deployment

**Topics Covered**:
- CI/CD pipeline configuration
- Environment setup (dev/staging/prod)
- Deployment procedures
- Rollback strategies
- Health check validation
- Monitoring and alerting
- Incident response procedures
- Release management

**ULTRON Deployment**:
- Master launcher: `run.bat` with health checks
- Development: `python main.py`
- Docker/container deployment (if applicable)
- GitHub Actions: `.github/workflows/ultron_agent.yml`

---

## 📖 Local ULTRON Documentation

### Core Documentation Files

#### 1. Developer Guide (Primary)
**File**: `.github/copilot-instructions.md`

**Contents**:
- Project architecture overview
- Core components explanation
- Development workflows
- Coding standards and patterns
- Tool development guidelines
- Configuration management
- Testing procedures
- Troubleshooting guide

**When to Use**: Start here for all development work

---

#### 2. Voice System Documentation
**File**: `VOICE_MICROPHONE_DOCUMENTATION.md`

**Contents**:
- Voice recognition system architecture
- TTS (Text-to-Speech) queue processing
- Microphone integration
- ElevenLabs API integration
- Fallback mechanisms (pyttsx3 → console)
- Common voice issues and fixes
- Voice system critical rules

**When to Use**: Working with voice features or troubleshooting audio issues

---

#### 3. MCP Integration Guide
**File**: `MCP_INTEGRATION_GUIDE.md`

**Contents**:
- What is Model Context Protocol
- Pre-configured MCP servers (5 servers)
- Browser automation setup
- GitHub operations integration
- Filesystem access configuration
- Database integration
- Security considerations
- Troubleshooting MCP servers

**Quick Reference**: `MCP_QUICK_REFERENCE.md`

**When to Use**: Adding external tools, browser automation, or GitHub integration

---

#### 4. System Architecture
**File**: `SYSTEM_ARCHITECTURE.md`

**Contents**:
- Service connection diagrams
- Port mapping (5000, 8080, 8090, 8002, 11434)
- Component lifecycle
- Event system flow
- Data persistence
- Network architecture

**When to Use**: Understanding how components interact

---

#### 5. Setup Guide
**File**: `SETUP_CHECKLIST.md`

**Contents**:
- Installation prerequisites
- Step-by-step setup instructions
- Environment configuration
- Dependency installation
- Initial configuration
- Verification steps

**When to Use**: First-time setup or onboarding new developers

---

#### 6. Recent Fixes
**File**: `FIXES_SUMMARY_2025-10-24.md`

**Contents**:
- Voice feedback loop prevention
- GUI layout and positioning fixes
- TTS dual-playback resolution
- Voice auto-enable prevention
- Critical code comments

**When to Use**: Understanding recent changes or debugging similar issues

---

### Specialized Documentation

#### API Documentation (ULTRON-Specific)
**File**: `API.md`

**Contents**:
- ULTRON REST API endpoints
- Flask server configuration
- WebSocket integration
- Custom endpoints
- Tool API schemas

---

#### Architecture Design
**File**: `ARCHITECTURE_DESIGN.md`

**Contents**:
- Design decisions and rationale
- Component specifications
- Interface definitions
- Extension points

---

#### Component Specifications
**File**: `COMPONENT_SPECIFICATIONS.md`

**Contents**:
- Detailed component requirements
- Interface contracts
- Configuration options
- Performance characteristics

---

#### AI Toolkit Setup
**File**: `AI_TOOLKIT_SETUP.md`

**Contents**:
- AI model integration
- Evaluation frameworks
- Agent development tools
- Best practices for AI features

---

#### Contributing Guidelines
**File**: `Contributing.md`

**Contents**:
- Code contribution process
- Pull request guidelines
- Code review standards
- Branch naming conventions

---

#### Credits and Acknowledgments
**File**: `CREDITS.md`

**Contents**:
- Project contributors
- Third-party libraries
- Acknowledgments
- Licensing information

---

## 🚀 Quick Start Guides

### For New Developers
1. **Read**: `.github/copilot-instructions.md` (Developer Guide)
2. **Setup**: Follow `SETUP_CHECKLIST.md`
3. **Architecture**: Review `SYSTEM_ARCHITECTURE.md`
4. **Internal Docs**: Bookmark internal documentation links
5. **Run**: Execute `run.bat` to start ULTRON

### For Voice Feature Work
1. **Read**: `VOICE_MICROPHONE_DOCUMENTATION.md`
2. **Review**: Recent fixes in `FIXES_SUMMARY_2025-10-24.md`
3. **Test**: Enable microphone and test TTS queue
4. **Debug**: Check `logs/voice.log`

### For MCP Integration
1. **Read**: `MCP_INTEGRATION_GUIDE.md`
2. **Quick Reference**: `MCP_QUICK_REFERENCE.md`
3. **Setup**: Install Node.js and Browser MCP extension
4. **Test**: Run `list mcp servers`

### For API Development
1. **Internal**: Review https://internal.docs/api
2. **ULTRON API**: Check `API.md`
3. **Code**: See `api_server.py` implementation
4. **Test**: Use `/health` endpoint verification

---

## 🔍 Finding Specific Information

### "How do I...?"

#### "...add a new tool to ULTRON?"
- **Guide**: `.github/copilot-instructions.md` → "Tool Development Pattern"
- **Interface**: `tools/tool_interface.py`
- **Example**: Any file in `tools/` directory

#### "...configure voice settings?"
- **Guide**: `VOICE_MICROPHONE_DOCUMENTATION.md`
- **Config**: `ultron_config.json` → `voice_engine`, `stt_engine`, `tts_engine`
- **Code**: `voice.py`

#### "...integrate a new MCP server?"
- **Guide**: `MCP_INTEGRATION_GUIDE.md` → "Custom MCP Server"
- **Config**: `mcp.json`
- **Tool**: `tools/mcp_integration_tool.py`

#### "...deploy ULTRON to production?"
- **Internal**: https://internal.docs/deployment
- **Launcher**: `run.bat` with health checks
- **CI/CD**: `.github/workflows/ultron_agent.yml`

#### "...troubleshoot Ollama backend issues?"
- **Guide**: `.github/copilot-instructions.md` → "Troubleshooting Guide"
- **Logs**: `logs/brain.log`
- **Health Check**: `ultron_master_startup.log`

#### "...understand the architecture?"
- **Internal**: https://internal.docs/architecture (company-wide)
- **ULTRON**: `SYSTEM_ARCHITECTURE.md` (ULTRON-specific)
- **Design**: `ARCHITECTURE_DESIGN.md` (design decisions)

#### "...use the API?"
- **Internal**: https://internal.docs/api (full API reference)
- **ULTRON**: `API.md` (ULTRON endpoints)
- **Server Code**: `api_server.py`

---

## 📊 Documentation by Role

### Frontend Developer
- `gui/ultron_enhanced/web/` directory files
- `.github/copilot-instructions.md` → "GUI & Service Architecture"
- `VOICE_MICROPHONE_DOCUMENTATION.md` → GUI integration
- Internal: https://internal.docs/architecture

### Backend Developer
- `.github/copilot-instructions.md` → "Core Components"
- `agent_core.py`, `brain.py` documentation
- `API.md` for API development
- Internal: https://internal.docs/api

### DevOps Engineer
- `run.bat` launcher and health checks
- `SETUP_CHECKLIST.md`
- `.github/workflows/` CI/CD configs
- Internal: https://internal.docs/deployment

### AI/ML Engineer
- `AI_TOOLKIT_SETUP.md`
- `brain.py` AI reasoning engine
- `tools/` AI-powered tools
- `MCP_INTEGRATION_GUIDE.md` for external AI tools

### Tool Developer
- `.github/copilot-instructions.md` → "Tool Development Pattern"
- `tools/tool_interface.py`
- `tools/tool_loader.py`
- `MCP_INTEGRATION_GUIDE.md` for MCP tools

---

## 🔗 External Resources

### MCP (Model Context Protocol)
- **Official Spec**: https://modelcontextprotocol.io/
- **VS Code Guide**: https://code.visualstudio.com/docs/copilot/customization/mcp-servers
- **Browser MCP**: https://docs.browsermcp.io/
- **Server Registry**: https://github.com/mcp

### Python Libraries
- **Flask**: https://flask.palletsprojects.com/
- **aiohttp**: https://docs.aiohttp.org/
- **Ollama**: https://ollama.ai/
- **PyAutoGUI**: https://pyautogui.readthedocs.io/

### AI Models
- **Ollama Models**: https://ollama.ai/library
- **ElevenLabs**: https://elevenlabs.io/docs
- **GitHub Models**: https://github.com/marketplace/models

---

## 🧭 Navigation Tips

### Searching Documentation
```powershell
# Search all markdown files for a term
Get-ChildItem -Path . -Filter *.md -Recurse | Select-String "search_term"

# Search specific documentation
Get-Content DOCUMENTATION_HUB.md | Select-String "MCP"
```

### VS Code Quick Access
- Press `Ctrl+P` and type filename to open
- Press `Ctrl+Shift+F` to search across all files
- Bookmark frequently used docs in VS Code

### Git-Based Documentation
All documentation is version-controlled in Git, so you can:
- View history: `git log DOCUMENTATION_HUB.md`
- See changes: `git diff main DOCUMENTATION_HUB.md`
- Restore versions: `git checkout <commit> -- DOCUMENTATION_HUB.md`

---

## 📝 Documentation Maintenance

### Updating Documentation
When making significant changes:
1. Update relevant documentation file
2. Update this hub if adding new docs
3. Update `.github/copilot-instructions.md` if changing core patterns
4. Commit documentation with code changes

### Documentation Standards
- Use Markdown format (.md)
- Include code examples where applicable
- Add links to related documentation
- Keep internal docs links up-to-date
- Version documentation with code changes

### Review Process
- Documentation changes reviewed with code PRs
- Major architectural changes require architecture doc updates
- API changes require API documentation updates
- New features require documentation before merge

---

## 🆘 Getting Help

### Internal Resources
1. **API Questions**: Check https://internal.docs/api
2. **Architecture Questions**: Check https://internal.docs/architecture
3. **Deployment Issues**: Check https://internal.docs/deployment
4. **Team Chat**: (Add team communication channel here)

### ULTRON-Specific Help
1. **Check Documentation**: Search this hub first
2. **Review Logs**: `logs/<component>.log`
3. **GitHub Issues**: Create issue in repository
4. **Code Comments**: Many files have inline documentation

### Emergency Contacts
(Add relevant team contact information here)
- **DevOps Team**: (contact info)
- **Backend Team**: (contact info)
- **AI/ML Team**: (contact info)

---

## 📅 Last Updated

**Date**: October 25, 2025
**Version**: ULTRON Agent 3.0
**Maintainer**: Development Team

---

*This documentation hub is the central index for all ULTRON Agent documentation. Bookmark this page for quick access to all resources.*
