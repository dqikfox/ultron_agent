"""
Example Plugin for UltronSysAgent
Demonstrates how to create custom plugins for extending functionality
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class ExamplePlugin:
    """
    Example plugin that demonstrates the plugin architecture
    
    This plugin provides:
    - Custom command handling
    - Event listening and publishing
    - Data persistence
    - Integration with other modules
    """
    
    def __init__(self, config, event_bus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        
        # Plugin state
        self.enabled = True
        self.command_count = 0
        self.last_command_time = None
        
        # Plugin configuration
        self.plugin_config = config.get('plugins.example', {
            'response_prefix': '🔌 Plugin: ',
            'max_commands_per_minute': 10
        })
        
        # Register event handlers
        self._setup_event_handlers()
        
        self.logger.info("Example plugin initialized")
    
    def _setup_event_handlers(self):
        """Setup event bus handlers for the plugin"""
        # Listen for speech recognition events
        self.event_bus.subscribe("speech_recognized", self._handle_speech)
        
        # Listen for GUI commands
        self.event_bus.subscribe("gui_command", self._handle_gui_command)
        
        # Listen for system events
        self.event_bus.subscribe("system_response", self._handle_system_response)
    
    async def _handle_speech(self, event):
        """Handle recognized speech for plugin commands"""
        try:
            text = event.data.get('text', '').lower()
            
            # Check for plugin-specific commands
            if 'example plugin' in text or 'plugin test' in text:
                await self._process_plugin_command(text, 'voice')
                
        except Exception as e:
            self.logger.error(f"Error handling speech: {e}")
    
    async def _handle_gui_command(self, event):
        """Handle GUI commands for plugin"""
        try:
            text = event.data.get('text', '').lower()
            
            # Check for plugin commands
            if text.startswith('/plugin') or 'example plugin' in text:
                await self._process_plugin_command(text, 'gui')
                
        except Exception as e:
            self.logger.error(f"Error handling GUI command: {e}")
    
    async def _handle_system_response(self, event):
        """Handle system responses that might interest the plugin"""
        try:
            # Example: React to certain system events
            response_type = event.data.get('type')
            
            if response_type == 'file_processed':
                file_path = event.data.get('file_path', '')
                if file_path.endswith('.plugin'):
                    await self._handle_plugin_file(file_path)
                    
        except Exception as e:
            self.logger.error(f"Error handling system response: {e}")
    
    async def _process_plugin_command(self, command_text: str, source: str):
        """Process plugin-specific commands"""
        try:
            # Rate limiting
            if not self._check_rate_limit():
                await self._send_response("Rate limit exceeded. Please wait.", source)
                return
            
            # Update command tracking
            self.command_count += 1
            self.last_command_time = datetime.now()
            
            # Parse and execute command
            if 'status' in command_text:
                await self._handle_status_command(source)
            
            elif 'help' in command_text:
                await self._handle_help_command(source)
            
            elif 'test' in command_text:
                await self._handle_test_command(source)
            
            elif 'config' in command_text:
                await self._handle_config_command(command_text, source)
            
            else:
                await self._handle_unknown_command(command_text, source)
                
        except Exception as e:
            self.logger.error(f"Error processing plugin command: {e}")
            await self._send_response(f"Plugin error: {e}", source)
    
    def _check_rate_limit(self) -> bool:
        """Check if command rate limit is exceeded"""
        max_commands = self.plugin_config.get('max_commands_per_minute', 10)
        
        if self.last_command_time:
            time_diff = (datetime.now() - self.last_command_time).total_seconds()
            if time_diff < 60:  # Within last minute
                return self.command_count < max_commands
        
        return True
    
    async def _handle_status_command(self, source: str):
        """Handle status command"""
        status_info = {
            'plugin_name': 'Example Plugin',
            'version': '1.0.0',
            'enabled': self.enabled,
            'commands_processed': self.command_count,
            'last_command': self.last_command_time.isoformat() if self.last_command_time else 'Never',
            'configuration': self.plugin_config
        }
        
        response = f"Plugin Status:\n"
        for key, value in status_info.items():
            response += f"  {key}: {value}\n"
        
        await self._send_response(response, source)
    
    async def _handle_help_command(self, source: str):
        """Handle help command"""
        help_text = """Example Plugin Commands:
        
• "example plugin status" - Show plugin status
• "example plugin help" - Show this help
• "example plugin test" - Run a test command
• "example plugin config <key> <value>" - Update configuration

Example usage:
• Say: "example plugin status"
• Type: "/plugin help"
• Command: "plugin test hello world"
"""
        
        await self._send_response(help_text, source)
    
    async def _handle_test_command(self, source: str):
        """Handle test command"""
        test_results = await self._run_plugin_tests()
        
        response = "Plugin Test Results:\n"
        for test_name, result in test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            response += f"  {test_name}: {status}\n"
            if not result['success']:
                response += f"    Error: {result.get('error', 'Unknown error')}\n"
        
        await self._send_response(response, source)
    
    async def _handle_config_command(self, command_text: str, source: str):
        """Handle configuration commands"""
        parts = command_text.split()
        
        if len(parts) >= 4:  # config <key> <value>
            key = parts[2]
            value = ' '.join(parts[3:])
            
            # Update plugin configuration
            self.plugin_config[key] = value
            
            # Save to main config
            config_key = f'plugins.example.{key}'
            self.config.set(config_key, value)
            
            response = f"Configuration updated: {key} = {value}"
        else:
            # Show current configuration
            response = "Current Plugin Configuration:\n"
            for key, value in self.plugin_config.items():
                response += f"  {key}: {value}\n"
        
        await self._send_response(response, source)
    
    async def _handle_unknown_command(self, command_text: str, source: str):
        """Handle unknown plugin commands"""
        response = f"Unknown plugin command: {command_text}\nSay 'example plugin help' for available commands."
        await self._send_response(response, source)
    
    async def _handle_plugin_file(self, file_path: str):
        """Handle plugin-specific files"""
        try:
            self.logger.info(f"Processing plugin file: {file_path}")
            
            # Example: Process .plugin files
            with open(file_path, 'r') as f:
                plugin_data = f.read()
            
            # Publish file processed event
            await self.event_bus.publish(
                "plugin_file_processed",
                {
                    'file_path': file_path,
                    'plugin': 'example_plugin',
                    'data': plugin_data
                },
                source="example_plugin"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing plugin file: {e}")
    
    async def _run_plugin_tests(self) -> Dict[str, Dict]:
        """Run plugin self-tests"""
        tests = {}
        
        # Test 1: Configuration access
        try:
            config_value = self.config.get('system.admin_mode')
            tests['config_access'] = {'success': True, 'result': config_value}
        except Exception as e:
            tests['config_access'] = {'success': False, 'error': str(e)}
        
        # Test 2: Event bus functionality
        try:
            await self.event_bus.publish('plugin_test_event', {'test': True}, source='example_plugin')
            tests['event_bus'] = {'success': True}
        except Exception as e:
            tests['event_bus'] = {'success': False, 'error': str(e)}
        
        # Test 3: Logging functionality
        try:
            self.logger.info("Plugin test log message")
            tests['logging'] = {'success': True}
        except Exception as e:
            tests['logging'] = {'success': False, 'error': str(e)}
        
        return tests
    
    async def _send_response(self, message: str, source: str):
        """Send response back to user"""
        try:
            prefix = self.plugin_config.get('response_prefix', '🔌 Plugin: ')
            full_message = f"{prefix}{message}"
            
            # Publish AI response event
            await self.event_bus.publish(
                "ai_response",
                {
                    'response': full_message,
                    'source': 'example_plugin',
                    'input_source': source
                },
                source="example_plugin"
            )
            
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
    
    async def start(self):
        """Start the plugin (called when plugin is loaded)"""
        self.logger.info("Example plugin started")
        self.enabled = True
    
    async def stop(self):
        """Stop the plugin (called when plugin is unloaded)"""
        self.logger.info("Example plugin stopped")
        self.enabled = False
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': 'Example Plugin',
            'version': '1.0.0',
            'description': 'Demonstrates plugin architecture and capabilities',
            'author': 'MiniMax Agent',
            'enabled': self.enabled,
            'commands_processed': self.command_count,
            'capabilities': [
                'command_handling',
                'event_listening',
                'configuration_management',
                'self_testing'
            ]
        }

# Plugin metadata (required for plugin system)
PLUGIN_CLASS = ExamplePlugin
PLUGIN_NAME = "example_plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Example plugin demonstrating UltronSysAgent plugin architecture"
PLUGIN_DEPENDENCIES = []  # List of required Python packages
PLUGIN_REQUIRES_ADMIN = False
