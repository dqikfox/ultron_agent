#!/bin/bash
echo "Setting up Ultron Agent 2.0..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434 > /dev/null; then
    echo "Ollama is not running. Please start Ollama with 'ollama run llama3.2:latest' (install from https://ollama.ai)."
    exit 1
fi

# Run setup script
echo "Running setup script..."
python3 setup.py
if [ $? -ne 0 ]; then
    echo "Setup failed. Check setup.log for details."
    exit 1
fi

# Run the agent
echo "Starting Ultron Agent..."
cd ultron_agent_2
python3 agent_core.py
if [ $? -ne 0 ]; then
    echo "Failed to start Ultron Agent. Check logs/ultron.log for details."
    exit 1
fi