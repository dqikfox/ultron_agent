# Installation Checklist - ULTRON Agent 3.0

## ✅ Phase 1: System & AWS CLI (COMPLETE)

- [x] AWS CLI v2.31.25 installed
- [x] AWS CLI command available (`aws --version` works)
- [x] Python 3.10.0 installed
- [x] Windows 11 64-bit system verified
- [x] Internet connection verified

## ✅ Phase 2: Virtual Environment (COMPLETE)

- [x] Virtual environment created (`.venv/`)
- [x] Python executable in venv: `.venv\Scripts\python.exe`
- [x] pip executable in venv: `.venv\Scripts\pip.exe`
- [x] Core tools upgraded (pip 25.3, setuptools 80.9.0, wheel 0.45.1)

## ✅ Phase 3: Setup Scripts & Documentation (COMPLETE)

- [x] `setup_requirements.bat` created (main installer)
- [x] `verify_setup.bat` created (verification tool)
- [x] `REQUIREMENTS_SETUP.md` created (12KB - full docs)
- [x] `SETUP_COMPLETE.md` created (9KB - getting started)
- [x] `AWS_CLI_SETUP_SUMMARY.md` created (11KB - quick ref)
- [x] Dependency conflict fixed (openai==1.21.0)

## ⏭️ Phase 4: Python Dependencies (PENDING - Run next)

**Command to Run**:
```powershell
.\setup_requirements.bat
```

Expected Outcomes:
- [ ] All packages from requirements.txt installed (~2.5GB)
- [ ] Installation completes successfully (15-25 min)
- [ ] `pip check` shows no conflicts
- [ ] All critical packages importable
- [ ] Verification script passes

Critical Packages to Verify:
- [ ] flask (Web framework)
- [ ] aiohttp (Async HTTP)
- [ ] openai (OpenAI API)
- [ ] langchain (LLM orchestration)
- [ ] torch (PyTorch - ML framework)
- [ ] transformers (Hugging Face models)
- [ ] elevenlabs (Voice synthesis)
- [ ] pydantic (Data validation)

## ⏭️ Phase 5: AWS Configuration (OPTIONAL - if using AWS)

**Command to Run**:
```powershell
aws configure
```

Setup Steps:
- [ ] AWS Access Key ID entered
- [ ] AWS Secret Access Key entered
- [ ] Default region set (us-east-1 recommended)
- [ ] Output format set (json)
- [ ] Credentials file created: `~\.aws\credentials`
- [ ] Config file created: `~\.aws\config`

Verification:
- [ ] `aws sts get-caller-identity` works
- [ ] AWS account information displayed
- [ ] No "credentials not found" errors

## ⏭️ Phase 6: Agent Launch (FINAL)

**Commands to Run**:
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start ULTRON Agent
python main.py
```

Expected Results:
- [ ] Virtual environment shows `(.venv)` in prompt
- [ ] Agent starts without errors
- [ ] Web server starts on port 8080
- [ ] API server starts on port 5000
- [ ] No critical exceptions in logs
- [ ] Browser can reach http://localhost:8080

## 📋 Documentation Files

| File | Size | Purpose |
|------|------|---------|
| `REQUIREMENTS_SETUP.md` | 12KB | Complete setup guide with troubleshooting |
| `SETUP_COMPLETE.md` | 9KB | Installation summary and next steps |
| `AWS_CLI_SETUP_SUMMARY.md` | 11KB | Quick reference guide |
| `setup_requirements.bat` | 5KB | Automated installer script |
| `verify_setup.bat` | 8KB | System verification tool |

## 🚀 Quick Start After Installation

```powershell
# 1. Navigate to project
cd C:\Projects\ultron_agent

# 2. Activate environment
.\.venv\Scripts\Activate.ps1

# 3. Start agent (with activated venv)
python main.py

# 4. Open browser
# http://localhost:8080
```

## 🔍 Verification Commands

```powershell
# Check AWS CLI
aws --version
aws sts get-caller-identity

# Check Python
python --version

# Check virtual environment
Test-Path .\.venv

# Check critical packages (with venv activated)
python -c "import flask, aiohttp, torch; print('OK')"

# Run full verification
.\verify_setup.bat
```

## 📍 Key Ports

- **8080**: Web GUI (Pokédex interface)
- **5000**: REST API Server
- **11434**: Ollama LLM Backend (if running)

## ⚠️ Important Notes

- **Virtual Environment**: Always activate before running agent
- **AWS Credentials**: Optional - only if using AWS services
- **First Run**: Expect setup.bat to take 15-25 minutes
- **Dependencies**: Total ~2.5GB download + installation
- **Storage**: Ensure 50GB free space (for models and cache)

## 📞 Support

If issues occur:
1. Check `REQUIREMENTS_SETUP.md` troubleshooting section
2. Run `verify_setup.bat` to diagnose
3. Review logs in `logs/` directory
4. Re-run setup script: `.\setup_requirements.bat`

## ✅ Final Verification Checklist

Before considering installation complete, verify:

- [ ] Phase 1-3 all complete (system, venv, scripts)
- [ ] `setup_requirements.bat` runs without errors
- [ ] Phase 4: All Python packages installed
- [ ] Phase 5: AWS configured (if needed)
- [ ] Phase 6: Agent launches successfully
- [ ] Web GUI accessible at http://localhost:8080
- [ ] No critical errors in logs
- [ ] `verify_setup.bat` shows "Setup Complete!"

---

**Installation Date**: October 31, 2025
**Status**: Phases 1-3 ✅ COMPLETE | Phases 4-6 ⏭️ PENDING
**Next**: Run `.\setup_requirements.bat` to proceed with Phase 4

---

*For detailed information, refer to the documentation files listed above.*
