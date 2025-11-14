# Image Generation & AutoGen - Quick Reference

## 🚀 Setup (2 minutes)

```bash
# Install
pip install pyautogen openai requests

# Set keys
set OPENAI_API_KEY=sk-your-key
set STABILITY_API_KEY=sk-your-key

# Test
python test_image_generation.py
python test_autogen.py

# Start
.\run.bat
```

---

## 🎨 Image Generation Commands

```
"generate image of a robot"
"create image of a sunset"
"draw a futuristic city"
```

**Providers**: DALL-E ($0.04), Stability AI ($0.002), Local (FREE)

---

## 🤖 AutoGen Commands

```
"autogen: write a sorting algorithm"
"use autogen to analyze code"
"multi agent: plan a project"
```

**Cost**: GPT-4 ($0.03/1K), GPT-3.5 ($0.002/1K), Local (FREE)

---

## 📁 Files

- `tools/image_generation_tool.py` - Image gen (auto-loads)
- `tools/autogen_automation_tool.py` - AutoGen (auto-loads)
- `test_image_generation.py` - Test images
- `test_autogen.py` - Test AutoGen
- `TEST_AUTOMATION_GUIDE.md` - Full guide

---

## ✅ Verify

```bash
python verify_integration.py  # Check tools loaded
.\run.bat                      # Start ULTRON
```

---

**Status**: ✅ Ready (needs API keys + dependencies)
