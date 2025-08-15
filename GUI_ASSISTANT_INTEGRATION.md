# GUI-Assistant Integration

This integration links the Ultron GUI (in `gui/` folder) with the AI Assistant (in `assistant/` folder).

## Components Created

### 1. Bridge Server (`gui_assistant_bridge.py`)
- FastAPI server that serves both GUI and assistant interfaces
- Provides unified access point at `http://localhost:8000`
- Can build and start the assistant automatically

### 2. Integrated Launcher (`launch_integrated.py`)
- Interactive launcher for starting components individually or together
- Options: GUI only, Assistant only, Bridge only, or All components

### 3. Integration Module (`gui_assistant_integration.py`)
- Communication layer between GUI and assistant
- Async HTTP client for sending messages between components
- Status checking and health monitoring

## Quick Start

### Option 1: Use the Bridge Server
```bash
# Install bridge requirements
pip install -r requirements_bridge.txt

# Start the bridge server
python gui_assistant_bridge.py

# Visit http://localhost:8000 for the control center
```

### Option 2: Use the Integrated Launcher
```bash
python launch_integrated.py
# Choose option 4 for "All Components"
```

### Option 3: Manual Setup
```bash
# Terminal 1: Start Assistant
cd assistant/ai-assistant
npm run dev

# Terminal 2: Start GUI
cd gui/ultron_enhanced
python ultron_main.py

# Terminal 3: Start Bridge (optional)
python gui_assistant_bridge.py
```

## Features

### GUI Integration
- Added "AI CHAT" button in the GUI navigation
- Clicking opens the assistant in a new tab
- Maintains existing GUI functionality

### Bridge Server Features
- **Control Center**: Unified interface at `http://localhost:8000`
- **GUI Access**: Direct access to GUI at `/gui/`
- **Assistant Access**: Built assistant at `/assistant/`
- **Quick Actions**: Start/build assistant, check status

### Communication
- HTTP-based communication between components
- Status monitoring and health checks
- Message passing between GUI and assistant

## File Structure
```
ultron_agent_2/
├── gui/                          # GUI components
│   └── ultron_enhanced/
│       ├── web/                  # Web interface
│       └── ultron_main.py        # Main GUI application
├── assistant/                    # Assistant components
│   └── ai-assistant/             # React TypeScript app
├── gui_assistant_bridge.py       # Bridge server
├── launch_integrated.py          # Integrated launcher
├── gui_assistant_integration.py  # Integration module
└── requirements_bridge.txt       # Bridge dependencies
```

## Usage Examples

### From GUI
1. Start the GUI: `python gui/ultron_enhanced/ultron_main.py`
2. Click the "AI CHAT" button in the navigation
3. Assistant opens in new browser tab

### From Bridge
1. Start bridge: `python gui_assistant_bridge.py`
2. Visit `http://localhost:8000`
3. Use the control center to launch components

### Programmatic Integration
```python
from gui_assistant_integration import GuiAssistantIntegration

async def example():
    async with GuiAssistantIntegration() as integration:
        # Send message to assistant
        response = await integration.send_to_assistant("Hello from GUI")
        print(response)
        
        # Check assistant status
        status = await integration.get_assistant_status()
        print(status)
```

## Troubleshooting

### Assistant Not Starting
- Ensure Node.js and npm are installed
- Run `npm install` in `assistant/ai-assistant/`
- Check if port 5173 is available

### GUI Not Loading
- Check if Python dependencies are installed
- Verify GUI path exists: `gui/ultron_enhanced/`
- Check console for error messages

### Bridge Connection Issues
- Ensure FastAPI dependencies are installed: `pip install -r requirements_bridge.txt`
- Check if port 8000 is available
- Verify both GUI and assistant paths exist

## Next Steps

1. **Enhanced Communication**: Add WebSocket support for real-time communication
2. **Shared State**: Implement shared state management between components
3. **Plugin System**: Create plugin architecture for extending functionality
4. **Authentication**: Add user authentication and session management
5. **Deployment**: Create production deployment configurations

## Dependencies

### Bridge Requirements
- FastAPI >= 0.104.0
- uvicorn >= 0.24.0
- aiohttp >= 3.9.0
- requests >= 2.31.0

### GUI Requirements
- See `gui/ultron_enhanced/requirements.txt`

### Assistant Requirements
- See `assistant/ai-assistant/package.json`