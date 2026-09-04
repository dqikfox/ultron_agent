#!/bin/bash
# ULTRON AI Assistant - Interactive Demo

source venv/bin/activate 2>/dev/null || true

cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║          🤖 ULTRON AI ASSISTANT - DEMO                     ║
╚══════════════════════════════════════════════════════════════╝

This is your advanced AI assistant that can:

✅ Chat using AI (powered by Ollama)
✅ Access your file system safely
✅ Execute terminal commands
✅ Interact via voice (optional)

Let's see it in action!

═══════════════════════════════════════════════════════════════
DEMO 1: File System Access
═══════════════════════════════════════════════════════════════
EOF

echo "📂 Listing current directory..."
python3 ultron_ai_assistant.py --text << 'DEMO1'
list directory .
quit
DEMO1

cat << 'EOF'

═══════════════════════════════════════════════════════════════
DEMO 2: Command Execution
═══════════════════════════════════════════════════════════════
EOF

echo "💻 Running system command: whoami..."
python3 ultron_ai_assistant.py --text << 'DEMO2'
run whoami
quit
DEMO2

cat << 'EOF'

═══════════════════════════════════════════════════════════════
DEMO 3: AI Conversation (if Ollama is running)
═══════════════════════════════════════════════════════════════
EOF

echo "🧠 Asking AI a question..."
python3 ultron_ai_assistant.py --text << 'DEMO3'
What is Python programming?
quit
DEMO3

cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                  ✅ DEMO COMPLETE!                          ║
╚══════════════════════════════════════════════════════════════╝

To use the assistant interactively:

  Text Mode:   python3 ultron_ai_assistant.py
  Voice Mode:  python3 ultron_ai_assistant.py --voice

Try these commands:
  - "list directory ~/Documents"
  - "run python3 --version"
  - "What can you do?"
  - "read file README.md"

See AI_ASSISTANT_GUIDE.md for full documentation!

EOF
