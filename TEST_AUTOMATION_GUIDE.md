# Image Generation & AutoGen Automation - Test Guide

## Overview
Complete testing guide for image generation and multi-agent automation features.

---

## 🎨 Image Generation

### Setup

#### Option 1: DALL-E 3 (OpenAI)
```bash
# Set API key
set OPENAI_API_KEY=sk-your-key-here

# Test
python test_image_generation.py
```

**Cost**: $0.040 per image (1024x1024)  
**Quality**: Excellent, best for creative/artistic images

#### Option 2: Stability AI
```bash
# Get API key from https://platform.stability.ai/
set STABILITY_API_KEY=sk-your-key-here

# Test
python test_image_generation.py
```

**Cost**: $0.002 per image (1024x1024)  
**Quality**: Very good, 20x cheaper than DALL-E

#### Option 3: Local (Free)
```bash
# Install Stable Diffusion locally
# Requires: 8GB+ GPU RAM

# Via Ollama (easiest)
ollama pull llava

# Or use Automatic1111 WebUI
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
.\webui-user.bat
```

**Cost**: FREE (uses local GPU)  
**Quality**: Good, fully private

### Usage

#### Via Tool (Auto-loads)
```python
# Voice command
"generate image of a futuristic robot"

# Or via agent
from agent_core import UltronAgent
agent = UltronAgent()
await agent.initialize()
result = await agent.process_command("generate image of a sunset")
```

#### Direct Test
```bash
python test_image_generation.py
```

### Expected Output
```
[TEST] Stability AI Image Generation
  [OK] Image saved: test_stability.png

[TEST] DALL-E Image Generation
  [OK] Image URL: https://...
  [OK] Image saved: test_dalle.png

[TEST] Local SDXL
  [OK] Image model available (llava)
```

---

## 🤖 AutoGen Multi-Agent Automation

### Setup

#### Install AutoGen
```bash
pip install pyautogen
```

#### Set API Key
```bash
set OPENAI_API_KEY=sk-your-key-here
```

#### Test Installation
```bash
python test_autogen.py
```

### Usage

#### Via Tool (Auto-loads)
```python
# Voice command
"use autogen to analyze this code and suggest improvements"

# Or via agent
from agent_core import UltronAgent
agent = UltronAgent()
await agent.initialize()
result = await agent.process_command("autogen: write a Python script to sort a list")
```

#### Direct Test
```bash
python test_autogen.py
```

### Expected Output
```
[TEST] AutoGen Basic Setup
  [OK] AutoGen installed
  [OK] Config created

[TEST] AutoGen Agent Creation
  [OK] Assistant agent created
  [OK] User proxy created

[TEST] AutoGen Conversation
  [OK] Conversation completed

[TEST] AutoGen Code Execution
  [OK] Code execution test completed
```

---

## 🧪 Test Results

### Current Status

#### Image Generation
- ❌ DALL-E: API access issue (model not available in project)
- ❌ Stability AI: API key not set
- ❌ Local SDXL: Ollama not running

**To Fix**:
1. Start Ollama: `ollama serve`
2. Set API keys (see setup above)
3. Verify OpenAI project has DALL-E access

#### AutoGen
- ❌ Not installed

**To Fix**:
```bash
pip install pyautogen
```

---

## 📋 Complete Setup Checklist

### Image Generation
- [ ] Choose provider (DALL-E, Stability AI, or Local)
- [ ] Set API key (if using cloud)
- [ ] Install dependencies: `pip install openai requests`
- [ ] Test: `python test_image_generation.py`
- [ ] Verify tool loads: `python verify_integration.py`

### AutoGen
- [ ] Install: `pip install pyautogen`
- [ ] Set OPENAI_API_KEY
- [ ] Test: `python test_autogen.py`
- [ ] Verify tool loads: `python verify_integration.py`

---

## 🎯 Integration with ULTRON

### Tools Auto-Load
Both tools automatically load when agent starts:
- `tools/image_generation_tool.py`
- `tools/autogen_automation_tool.py`

### Command Examples

#### Image Generation
```
"generate image of a robot"
"create image of a sunset over mountains"
"draw a picture of a cat"
```

#### AutoGen
```
"use autogen to write a sorting algorithm"
"autogen: analyze this code for bugs"
"multi agent: plan a project structure"
```

---

## 💰 Cost Comparison

### Image Generation

| Provider | Cost per Image | Quality | Speed | Privacy |
|----------|---------------|---------|-------|---------|
| DALL-E 3 | $0.040 | ⭐⭐⭐⭐⭐ | Fast | Cloud |
| Stability AI | $0.002 | ⭐⭐⭐⭐ | Fast | Cloud |
| Local SDXL | FREE | ⭐⭐⭐ | Slow | Private |

### AutoGen

| Usage | Cost | Notes |
|-------|------|-------|
| GPT-4 | $0.03/1K tokens | Best quality |
| GPT-3.5 | $0.002/1K tokens | 15x cheaper |
| Local (Ollama) | FREE | Requires setup |

---

## 🔧 Troubleshooting

### Image Generation

#### "API key not set"
```bash
# Windows
set OPENAI_API_KEY=sk-your-key
set STABILITY_API_KEY=sk-your-key

# Linux/Mac
export OPENAI_API_KEY=sk-your-key
export STABILITY_API_KEY=sk-your-key
```

#### "Model not found"
- DALL-E: Check OpenAI project has image generation enabled
- Stability: Verify API key is valid
- Local: Start Ollama and pull model

#### "Connection refused"
```bash
# Start Ollama
ollama serve

# Verify running
curl http://localhost:11434/api/tags
```

### AutoGen

#### "Module not found"
```bash
pip install pyautogen
```

#### "API rate limit"
- Use GPT-3.5 instead of GPT-4
- Add delays between requests
- Check OpenAI usage limits

#### "Code execution failed"
- Disable Docker: `"use_docker": False`
- Check work directory permissions
- Review generated code for errors

---

## 📊 Performance Metrics

### Image Generation
- **DALL-E**: 10-30 seconds per image
- **Stability AI**: 5-15 seconds per image
- **Local SDXL**: 30-120 seconds per image (GPU dependent)

### AutoGen
- **Simple tasks**: 5-15 seconds
- **Code generation**: 15-45 seconds
- **Complex workflows**: 1-5 minutes

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pyautogen openai requests
```

### 2. Set API Keys
```bash
set OPENAI_API_KEY=sk-your-key
set STABILITY_API_KEY=sk-your-key
```

### 3. Test Everything
```bash
python test_image_generation.py
python test_autogen.py
python verify_integration.py
```

### 4. Start ULTRON
```bash
.\run.bat
```

### 5. Try Commands
```
"generate image of a robot"
"autogen: write a hello world program"
```

---

## 📚 Additional Resources

### Image Generation
- DALL-E: https://platform.openai.com/docs/guides/images
- Stability AI: https://platform.stability.ai/docs
- Automatic1111: https://github.com/AUTOMATIC1111/stable-diffusion-webui

### AutoGen
- Documentation: https://microsoft.github.io/autogen/
- Examples: https://github.com/microsoft/autogen/tree/main/notebook
- Tutorial: https://microsoft.github.io/autogen/docs/tutorial/introduction

---

## ✅ Success Criteria

### Image Generation Working
- [ ] Test script passes (1+ provider)
- [ ] Tool loads in agent
- [ ] Voice command generates image
- [ ] Image file saved successfully

### AutoGen Working
- [ ] Test script passes (all 4 tests)
- [ ] Tool loads in agent
- [ ] Voice command triggers workflow
- [ ] Agents collaborate successfully

---

**Status**: Tools created and integrated, awaiting API keys and dependencies for testing.
