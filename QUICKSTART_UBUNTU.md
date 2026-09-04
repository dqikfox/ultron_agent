# ULTRON Agent 3.0 - Quick Start (Ubuntu)

## 🚀 One-Command Setup

```bash
./setup_ubuntu.sh && source venv/bin/activate && ./run.sh
```

## 📋 Step-by-Step

### 1. Run Setup Script
```bash
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

This installs:
- ✅ Python dependencies
- ✅ Ollama AI backend
- ✅ llava:7b model (4.7GB)
- ✅ Virtual environment
- ✅ Required directories

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Start ULTRON
```bash
./run.sh
```

### 4. Access Web Interface
Open browser to: **http://localhost:8080**

## 🛑 Stopping ULTRON

Press `Ctrl+C` in the terminal

## 📖 Need Help?

- **Full Guide**: See `UBUNTU_SETUP.md`
- **Architecture**: See `SYSTEM_ARCHITECTURE.md`
- **Troubleshooting**: Check `logs/` directory

## 🔧 Common Issues

### "Permission denied"
```bash
chmod +x setup_ubuntu.sh run.sh
```

### "Port already in use"
```bash
sudo lsof -i :8080
sudo kill -9 <PID>
```

### "Ollama not found"
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llava:7b
```

## 💡 Daily Usage

```bash
# Always activate venv first
source venv/bin/activate

# Then run
./run.sh
```
