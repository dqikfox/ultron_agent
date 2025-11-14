# ULTRON ADB Manager - Developer Integration Guide

**Version**: 3.0.4
**Status**: Production Ready
**Last Updated**: October 31, 2025

---

## 🎯 Overview

This guide covers integrating the ADB Manager into your ULTRON Agent workflows, custom tools, and external applications.

---

## 🔗 Integration Methods

### 1. Web Interface Integration

Access ADB Manager at: `http://localhost:8080/adb`

**Features**:
- Real-time device status
- Screenshot and video recording
- App management
- File browser
- Shell command execution
- Wireless device discovery

### 2. REST API Integration

**Base URL**: `http://localhost:5000/api/adb`

#### Device Endpoints

```python
import requests

# List connected devices
response = requests.get('http://localhost:5000/api/adb/devices')
devices = response.json()

# Get device info
response = requests.get('http://localhost:5000/api/adb/device/device-id')
device_info = response.json()

# Example: Get device properties
# Returns: battery, storage, RAM, CPU, Android version, IMEI
```

#### Command Execution

```python
# Execute shell command
response = requests.post('http://localhost:5000/api/adb/shell', json={
    'device': 'device-id',
    'command': 'getprop ro.product.model'
})
output = response.json()

# Execute ADB command
response = requests.post('http://localhost:5000/api/adb/command', json={
    'command': 'install',
    'device': 'device-id',
    'args': '/path/to/app.apk'
})
result = response.json()
```

#### App Management

```python
# Get installed apps
response = requests.get('http://localhost:5000/api/adb/apps/device-id')
apps = response.json()

# Install app
response = requests.post('http://localhost:5000/api/adb/install', json={
    'device': 'device-id',
    'path': '/path/to/app.apk'
})

# Uninstall app
response = requests.post('http://localhost:5000/api/adb/uninstall', json={
    'device': 'device-id',
    'package': 'com.example.app'
})
```

#### File Operations

```python
# Push file to device
response = requests.post('http://localhost:5000/api/adb/push', json={
    'device': 'device-id',
    'local': 'C:\\file.txt',
    'remote': '/sdcard/file.txt'
})

# Pull file from device
response = requests.post('http://localhost:5000/api/adb/pull', json={
    'device': 'device-id',
    'remote': '/sdcard/file.txt',
    'local': 'C:\\file.txt'
})
```

#### System Control

```python
# Take screenshot
response = requests.post('http://localhost:5000/api/adb/screenshot', json={
    'device': 'device-id'
})
screenshot = response.json()

# Reboot device
response = requests.post('http://localhost:5000/api/adb/reboot', json={
    'device': 'device-id'
})
```

### 3. WebSocket Integration

**Namespace**: `adb_manager`

```javascript
// Connect to WebSocket
const socket = io('http://localhost:8080', {
    namespace: '/adb_manager'
});

// Listen for device changes
socket.on('devices_updated', (devices) => {
    console.log('Devices:', devices);
});

// Execute command
socket.emit('execute_command', {
    command: 'shell',
    device: 'device-id',
    args: 'ls /sdcard/'
}, (response) => {
    console.log('Response:', response);
});

// Listen for responses
socket.on('command_response', (data) => {
    console.log('Output:', data.output);
});
```

### 4. Python Tool Integration

Create a custom ULTRON tool for ADB operations:

```python
# tools/my_adb_tool.py
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error
import requests
import json

class MyAdbTool(ToolInterface):
    """Custom tool using ADB Manager API"""

    @property
    def name(self) -> str:
        return "My ADB Tool"

    @property
    def description(self) -> str:
        return "Custom tool for device management"

    def match(self, command: str) -> bool:
        keywords = ["my-device", "adb-custom", "test-app"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            log_info("my_adb_tool", f"Executing: {command}")

            # Get first device
            response = requests.get('http://localhost:5000/api/adb/devices')
            devices = response.json().get('devices', [])

            if not devices:
                return "No devices found"

            device_id = devices[0]['id']

            # Example: Get device model
            response = requests.post(
                'http://localhost:5000/api/adb/shell',
                json={
                    'device': device_id,
                    'command': 'getprop ro.product.model'
                }
            )

            output = response.json().get('output', 'No output')
            log_info("my_adb_tool", f"Device model: {output}")

            return f"Device: {output}"

        except Exception as e:
            log_error("my_adb_tool", f"Error: {e}")
            return f"Error: {e}"

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "my_adb_tool",
            "description": "Custom device management tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    }
                },
                "required": ["command"]
            }
        }
```

### 5. Command Line Integration

Use ADB Manager with command-line tools:

```python
# scripts/test_device.py
import subprocess
import json
import sys

def run_adb_command(device_id, shell_cmd):
    """Run ADB command via ULTRON API"""
    curl_cmd = [
        'curl', '-X', 'POST',
        'http://localhost:5000/api/adb/shell',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'device': device_id,
            'command': shell_cmd
        })
    ]

    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

if __name__ == '__main__':
    device_id = sys.argv[1] if len(sys.argv) > 1 else 'device-id'

    # Get device model
    response = run_adb_command(device_id, 'getprop ro.product.model')
    print(f"Model: {response.get('output')}")

    # Get Android version
    response = run_adb_command(device_id, 'getprop ro.build.version.release')
    print(f"Android: {response.get('output')}")
```

---

## 🔌 Event System Integration

ULTRON uses an event system for async communication:

```python
# Listen to ADB events
from utils.event_system import get_event_system
import asyncio

async def subscribe_to_adb_events():
    event_system = get_event_system()

    # Listen for device changes
    async def on_device_change(data):
        print(f"Device changed: {data}")

    await event_system.subscribe('adb_device_change', on_device_change)

    # Listen for command execution
    async def on_command_complete(data):
        print(f"Command completed: {data}")

    await event_system.subscribe('adb_command_complete', on_command_complete)

# Run event system
asyncio.run(subscribe_to_adb_events())
```

---

## 🎮 UI Component Integration

Embed ADB Manager in custom web pages:

```html
<!-- HTML -->
<div id="adb-manager-container"></div>

<!-- Load ULTRON components -->
<script src="http://localhost:8080/js/adb-manager.js"></script>
<link rel="stylesheet" href="http://localhost:8080/css/adb-manager.css">

<script>
// Initialize ADB Manager
const adbManager = new ADBManager({
    container: '#adb-manager-container',
    apiUrl: 'http://localhost:5000/api/adb',
    wsUrl: 'http://localhost:8080',
    autoRefresh: true,
    refreshInterval: 5000
});

// Listen for events
adbManager.on('device-selected', (device) => {
    console.log('Selected device:', device);
});

adbManager.on('command-executed', (result) => {
    console.log('Command result:', result);
});

// Programmatic control
adbManager.selectDevice('device-id');
adbManager.executeCommand('shell', 'getprop ro.product.model');
adbManager.takeScreenshot('device-id');
</script>
```

---

## 🧪 Testing Integration

```python
# tests/test_adb_integration.py
import pytest
import requests
from unittest.mock import patch, MagicMock

@pytest.mark.integration
def test_get_devices():
    """Test device listing"""
    response = requests.get('http://localhost:5000/api/adb/devices')
    assert response.status_code == 200

    devices = response.json()
    assert 'devices' in devices
    assert isinstance(devices['devices'], list)

@pytest.mark.integration
def test_execute_shell_command():
    """Test shell command execution"""
    # Get first device
    response = requests.get('http://localhost:5000/api/adb/devices')
    devices = response.json()['devices']

    if not devices:
        pytest.skip("No devices connected")

    device_id = devices[0]['id']

    # Execute command
    response = requests.post('http://localhost:5000/api/adb/shell', json={
        'device': device_id,
        'command': 'getprop ro.product.model'
    })

    assert response.status_code == 200
    assert 'output' in response.json()

@pytest.mark.integration
def test_screenshot():
    """Test screenshot capture"""
    response = requests.get('http://localhost:5000/api/adb/devices')
    devices = response.json()['devices']

    if not devices:
        pytest.skip("No devices connected")

    device_id = devices[0]['id']

    response = requests.post('http://localhost:5000/api/adb/screenshot', json={
        'device': device_id
    })

    assert response.status_code == 200
    assert 'path' in response.json() or 'base64' in response.json()

@pytest.mark.unit
def test_adb_command_validation():
    """Test command validation"""
    from tools.adb_integration_tool import AdbIntegrationTool

    tool = AdbIntegrationTool()

    # Valid commands
    assert tool.match("get device info")
    assert tool.match("take screenshot")
    assert tool.match("run shell command")

    # Invalid commands
    assert not tool.match("unrelated command")
```

---

## 📊 Monitoring & Logging

```python
# Check ADB Manager logs
import logging
from utils.ultron_logger import log_info, log_error

# Log ADB operations
def monitored_adb_call(device_id, operation):
    try:
        log_info("adb_integration",
                f"Starting {operation} on {device_id}")

        # Perform ADB operation
        result = perform_operation(device_id, operation)

        log_info("adb_integration",
                f"Completed {operation}",
                extra_data={'device': device_id, 'result': result})

        return result
    except Exception as e:
        log_error("adb_integration",
                 f"Failed {operation}: {e}",
                 exception=e)
        raise
```

---

## 🔐 Security Integration

### Authentication

```python
# Add API key authentication
headers = {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:5000/api/adb/devices',
                       headers=headers)
```

### Rate Limiting

```python
# Configure rate limiting in ultron_config.json
{
  "adb_manager": {
    "api_rate_limit": {
      "enabled": true,
      "requests_per_minute": 60,
      "burst_size": 10
    }
  }
}
```

### Error Handling

```python
import requests
from requests.exceptions import ConnectionError, Timeout

def safe_adb_call(endpoint, json_data=None):
    """Safe ADB API call with error handling"""
    try:
        if json_data:
            response = requests.post(
                f'http://localhost:5000/api/adb/{endpoint}',
                json=json_data,
                timeout=30
            )
        else:
            response = requests.get(
                f'http://localhost:5000/api/adb/{endpoint}',
                timeout=30
            )

        response.raise_for_status()
        return response.json()

    except ConnectionError:
        print("ADB Manager service not running")
        return None
    except Timeout:
        print("ADB Manager request timed out")
        return None
    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
```

---

## 🚀 Deployment Integration

### Docker Support

```dockerfile
FROM python:3.10-slim

# Install Android SDK Platform Tools
RUN apt-get update && apt-get install -y android-sdk-platform-tools

# Copy ULTRON Agent
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 5000 8080 8000

# Start service
CMD ["python", "main.py"]
```

### CI/CD Integration

```yaml
# .github/workflows/test-adb.yml
name: ADB Manager Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install ADB
      run: |
        apt-get update
        apt-get install -y android-sdk-platform-tools

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run ADB tests
      run: pytest tests/test_adb_integration.py -v
```

---

## 📞 Support & Resources

- **REST API Documentation**: `/api/adb` endpoint docs
- **WebSocket Events**: See web UI console for event details
- **ADB Official Docs**: https://developer.android.com/tools/adb
- **ULTRON Documentation**: See project README and guides

---

## ✅ Integration Checklist

- [ ] ADB Manager installed and running
- [ ] API endpoints accessible
- [ ] WebSocket connection working
- [ ] Device detection functioning
- [ ] REST API tested with custom requests
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Security measures in place
- [ ] Unit tests passing
- [ ] Integration tests passing

---

**Status**: ✅ Ready for Integration
**Version**: 3.0.4
**Last Updated**: October 31, 2025
