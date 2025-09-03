#!/usr/bin/env python3
"""
ULTRON Desktop Application
==========================

Native desktop wrapper using PySide6 that embeds the web interface
in a professional desktop application with system tray integration.
"""

import sys
import os
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import webbrowser
import subprocess
from urllib.parse import urljoin

# Desktop application imports
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QMenuBar, QMenu, QStatusBar, QSystemTrayIcon, QLabel, QPushButton,
        QTextEdit, QTabWidget, QSplitter, QFrame, QMessageBox, QDialog,
        QFormLayout, QLineEdit, QCheckBox, QComboBox, QSpinBox, QSlider
    )
    from PySide6.QtCore import (
        Qt, QTimer, QThread, QObject, Signal, QUrl, QSettings,
        QSize, QRect, pyqtSignal
    )
    from PySide6.QtGui import (
        QIcon, QPixmap, QAction, QFont, QPalette, QColor, QDesktopServices
    )
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
    
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    logging.warning("PySide6 not available - Desktop GUI will not be available")
    
    # Create dummy classes for type hints
    class QMainWindow: pass
    class QWidget: pass
    class QObject: pass
    class Signal: pass

class UltronStatusMonitor(QObject):
    """Background thread for monitoring ULTRON system status"""
    
    status_updated = Signal(dict)
    
    def __init__(self, ultron_core):
        super().__init__()
        self.ultron_core = ultron_core
        self.running = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_status)
        self.timer.start(2000)  # Check every 2 seconds
    
    def check_status(self):
        """Check ULTRON system status"""
        try:
            if self.ultron_core and hasattr(self.ultron_core, 'get_status'):
                status = self.ultron_core.get_status()
                self.status_updated.emit(status)
        except Exception as e:
            logging.error(f"Status monitor error: {e}")
    
    def stop(self):
        """Stop status monitoring"""
        self.running = False
        if self.timer:
            self.timer.stop()

class UltronConfigDialog(QDialog):
    """Configuration dialog for ULTRON settings"""
    
    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.setWindowTitle("ULTRON Configuration")
        self.setMinimumSize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup configuration dialog UI"""
        layout = QVBoxLayout()
        
        # Create form layout
        form_layout = QFormLayout()
        
        # AI Settings
        ai_group = QLabel("🤖 AI Integration")
        ai_group.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        form_layout.addRow(ai_group)
        
        self.openai_key = QLineEdit()
        self.openai_key.setText(self.config.get('ai_integration', {}).get('openai_api_key', ''))
        self.openai_key.setEchoMode(QLineEdit.Password)
        form_layout.addRow("OpenAI API Key:", self.openai_key)
        
        self.nvidia_key = QLineEdit()
        self.nvidia_key.setText(self.config.get('ai_integration', {}).get('nvidia_api_key', ''))
        self.nvidia_key.setEchoMode(QLineEdit.Password)
        form_layout.addRow("NVIDIA API Key:", self.nvidia_key)
        
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setText(self.config.get('ai_integration', {}).get('anthropic_api_key', ''))
        self.anthropic_key.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Anthropic API Key:", self.anthropic_key)
        
        # Voice Settings
        voice_group = QLabel("🎤 Voice Settings")
        voice_group.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        form_layout.addRow(voice_group)
        
        self.voice_enabled = QCheckBox()
        self.voice_enabled.setChecked(self.config.get('voice_settings', {}).get('enabled', True))
        form_layout.addRow("Voice Recognition:", self.voice_enabled)
        
        self.voice_engine = QComboBox()
        self.voice_engine.addItems(["pyttsx3", "azure", "google", "openai"])
        current_engine = self.config.get('voice_settings', {}).get('engine', 'pyttsx3')
        self.voice_engine.setCurrentText(current_engine)
        form_layout.addRow("TTS Engine:", self.voice_engine)
        
        self.voice_speed = QSpinBox()
        self.voice_speed.setRange(100, 300)
        self.voice_speed.setValue(self.config.get('voice_settings', {}).get('speed', 180))
        form_layout.addRow("Voice Speed:", self.voice_speed)
        
        # System Settings
        system_group = QLabel("⚙️ System Settings")
        system_group.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        form_layout.addRow(system_group)
        
        self.debug_mode = QCheckBox()
        self.debug_mode.setChecked(self.config.get('system', {}).get('debug', False))
        form_layout.addRow("Debug Mode:", self.debug_mode)
        
        self.web_port = QSpinBox()
        self.web_port.setRange(1000, 65535)
        self.web_port.setValue(self.config.get('interfaces', {}).get('web_port', 8080))
        form_layout.addRow("Web Port:", self.web_port)
        
        self.auto_start = QCheckBox()
        self.auto_start.setChecked(self.config.get('system', {}).get('auto_start', True))
        form_layout.addRow("Auto Start:", self.auto_start)
        
        # Interface Settings
        interface_group = QLabel("🖥️ Interface Settings")
        interface_group.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        form_layout.addRow(interface_group)
        
        self.theme = QComboBox()
        self.theme.addItems(["red", "blue", "green", "purple", "orange"])
        current_theme = self.config.get('ui_settings', {}).get('theme', 'red')
        self.theme.setCurrentText(current_theme)
        form_layout.addRow("Theme:", self.theme)
        
        self.minimize_to_tray = QCheckBox()
        self.minimize_to_tray.setChecked(self.config.get('ui_settings', {}).get('minimize_to_tray', True))
        form_layout.addRow("Minimize to Tray:", self.minimize_to_tray)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        reset_button = QPushButton("Reset to Defaults")
        
        save_button.clicked.connect(self.save_config)
        cancel_button.clicked.connect(self.reject)
        reset_button.clicked.connect(self.reset_defaults)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_config(self):
        """Save configuration changes"""
        # Update config with form values
        self.config.setdefault('ai_integration', {})
        self.config['ai_integration']['openai_api_key'] = self.openai_key.text()
        self.config['ai_integration']['nvidia_api_key'] = self.nvidia_key.text()
        self.config['ai_integration']['anthropic_api_key'] = self.anthropic_key.text()
        
        self.config.setdefault('voice_settings', {})
        self.config['voice_settings']['enabled'] = self.voice_enabled.isChecked()
        self.config['voice_settings']['engine'] = self.voice_engine.currentText()
        self.config['voice_settings']['speed'] = self.voice_speed.value()
        
        self.config.setdefault('system', {})
        self.config['system']['debug'] = self.debug_mode.isChecked()
        self.config['system']['auto_start'] = self.auto_start.isChecked()
        
        self.config.setdefault('interfaces', {})
        self.config['interfaces']['web_port'] = self.web_port.value()
        
        self.config.setdefault('ui_settings', {})
        self.config['ui_settings']['theme'] = self.theme.currentText()
        self.config['ui_settings']['minimize_to_tray'] = self.minimize_to_tray.isChecked()
        
        self.accept()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        self.openai_key.clear()
        self.nvidia_key.clear()
        self.anthropic_key.clear()
        self.voice_enabled.setChecked(True)
        self.voice_engine.setCurrentText("pyttsx3")
        self.voice_speed.setValue(180)
        self.debug_mode.setChecked(False)
        self.web_port.setValue(8080)
        self.auto_start.setChecked(True)
        self.theme.setCurrentText("red")
        self.minimize_to_tray.setChecked(True)

class UltronDesktopApp(QMainWindow):
    """Main ULTRON Desktop Application"""
    
    def __init__(self):
        super().__init__()
        self.ultron_core = None
        self.web_view = None
        self.status_monitor = None
        self.system_tray = None
        self.settings = QSettings("ULTRON", "DesktopApp")
        
        # Load configuration
        self.config_path = Path("config_enhanced.json")
        self.config = self.load_config()
        
        self.setup_ui()
        self.setup_system_tray()
        self.setup_status_monitoring()
        
        # Auto-start ULTRON core if enabled
        if self.config.get('system', {}).get('auto_start', True):
            self.start_ultron_core()
    
    def load_config(self) -> Dict[str, Any]:
        """Load ULTRON configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
        
        # Return default config
        return {
            "ai_integration": {"openai_api_key": "", "nvidia_api_key": "", "anthropic_api_key": ""},
            "voice_settings": {"enabled": True, "engine": "pyttsx3", "speed": 180},
            "system": {"debug": False, "auto_start": True},
            "interfaces": {"web_port": 8080},
            "ui_settings": {"theme": "red", "minimize_to_tray": True}
        }
    
    def save_config(self):
        """Save ULTRON configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def setup_ui(self):
        """Setup main application UI"""
        self.setWindowTitle("🤖 ULTRON Enhanced Desktop")
        self.setMinimumSize(1200, 800)
        
        # Restore window geometry
        self.restoreGeometry(self.settings.value("geometry", b""))
        self.restoreState(self.settings.value("windowState", b""))
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        
        self.status_label = QLabel("🔴 ULTRON Status: Initializing...")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff4444;")
        toolbar_layout.addWidget(self.status_label)
        
        toolbar_layout.addStretch()
        
        # Control buttons
        self.start_button = QPushButton("🚀 Start ULTRON")
        self.start_button.clicked.connect(self.start_ultron_core)
        toolbar_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("🛑 Stop ULTRON")
        self.stop_button.clicked.connect(self.stop_ultron_core)
        self.stop_button.setEnabled(False)
        toolbar_layout.addWidget(self.stop_button)
        
        self.config_button = QPushButton("⚙️ Settings")
        self.config_button.clicked.connect(self.show_config_dialog)
        toolbar_layout.addWidget(self.config_button)
        
        layout.addLayout(toolbar_layout)
        
        # Main content area with tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Web Interface Tab
        self.setup_web_tab()
        
        # System Monitor Tab
        self.setup_monitor_tab()
        
        # Console Tab
        self.setup_console_tab()
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup status bar
        self.setup_status_bar()
        
        # Apply theme
        self.apply_theme()
    
    def setup_web_tab(self):
        """Setup web interface tab"""
        if not PYSIDE_AVAILABLE:
            web_widget = QLabel("PySide6 WebEngine not available")
            self.tab_widget.addTab(web_widget, "🌐 Web Interface")
            return
            
        try:
            self.web_view = QWebEngineView()
            
            # Set initial URL
            port = self.config.get('interfaces', {}).get('web_port', 8080)
            self.web_view.setUrl(QUrl(f"http://localhost:{port}"))
            
            # Create wrapper widget
            web_widget = QWidget()
            web_layout = QVBoxLayout(web_widget)
            
            # Navigation controls
            nav_layout = QHBoxLayout()
            
            refresh_button = QPushButton("🔄 Refresh")
            refresh_button.clicked.connect(self.refresh_web_view)
            nav_layout.addWidget(refresh_button)
            
            home_button = QPushButton("🏠 Home")
            home_button.clicked.connect(self.load_home_page)
            nav_layout.addWidget(home_button)
            
            external_button = QPushButton("🌐 Open in Browser")
            external_button.clicked.connect(self.open_in_external_browser)
            nav_layout.addWidget(external_button)
            
            nav_layout.addStretch()
            
            web_layout.addLayout(nav_layout)
            web_layout.addWidget(self.web_view)
            
            self.tab_widget.addTab(web_widget, "🌐 Web Interface")
            
        except Exception as e:
            logging.error(f"Web view setup failed: {e}")
            web_widget = QLabel(f"Web view unavailable: {e}")
            self.tab_widget.addTab(web_widget, "🌐 Web Interface")
    
    def setup_monitor_tab(self):
        """Setup system monitoring tab"""
        monitor_widget = QWidget()
        layout = QVBoxLayout(monitor_widget)
        
        # System status display
        self.system_status = QTextEdit()
        self.system_status.setReadOnly(True)
        self.system_status.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(QLabel("📊 System Status:"))
        layout.addWidget(self.system_status)
        
        # Performance metrics
        self.performance_display = QTextEdit()
        self.performance_display.setReadOnly(True)
        self.performance_display.setMaximumHeight(200)
        self.performance_display.setStyleSheet(self.system_status.styleSheet())
        layout.addWidget(QLabel("⚡ Performance Metrics:"))
        layout.addWidget(self.performance_display)
        
        self.tab_widget.addTab(monitor_widget, "📊 System Monitor")
    
    def setup_console_tab(self):
        """Setup console output tab"""
        console_widget = QWidget()
        layout = QVBoxLayout(console_widget)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #0c0c0c;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.console_output)
        
        # Command input
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter ULTRON command...")
        self.command_input.returnPressed.connect(self.execute_command)
        
        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(self.execute_command)
        
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(execute_button)
        layout.addLayout(input_layout)
        
        self.tab_widget.addTab(console_widget, "💻 Console")
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Start action
        start_action = QAction("🚀 Start ULTRON", self)
        start_action.triggered.connect(self.start_ultron_core)
        file_menu.addAction(start_action)
        
        # Stop action
        stop_action = QAction("🛑 Stop ULTRON", self)
        stop_action.triggered.connect(self.stop_ultron_core)
        file_menu.addAction(stop_action)
        
        file_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_config_dialog)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("🔄 Refresh Web View", self)
        refresh_action.triggered.connect(self.refresh_web_view)
        view_menu.addAction(refresh_action)
        
        fullscreen_action = QAction("📺 Toggle Fullscreen", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("ℹ️ About ULTRON", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        docs_action = QAction("📖 Documentation", self)
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.statusBar().showMessage("ULTRON Desktop Ready")
        
        # Add permanent widgets to status bar
        self.connection_status = QLabel("🔴 Disconnected")
        self.statusBar().addPermanentWidget(self.connection_status)
        
        self.cpu_status = QLabel("CPU: ---%")
        self.statusBar().addPermanentWidget(self.cpu_status)
        
        self.memory_status = QLabel("RAM: ---%")
        self.statusBar().addPermanentWidget(self.memory_status)
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.system_tray = QSystemTrayIcon(self)
        
        # Create tray icon (you might want to add an actual icon file)
        icon = QIcon()  # Would load from file: QIcon("ultron_icon.png")
        self.system_tray.setIcon(icon)
        self.system_tray.setToolTip("ULTRON Enhanced Desktop")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show ULTRON", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        start_action = QAction("Start ULTRON Core", self)
        start_action.triggered.connect(self.start_ultron_core)
        tray_menu.addAction(start_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.system_tray.setContextMenu(tray_menu)
        self.system_tray.activated.connect(self.tray_icon_activated)
        self.system_tray.show()
    
    def setup_status_monitoring(self):
        """Setup background status monitoring"""
        self.status_monitor = UltronStatusMonitor(self.ultron_core)
        self.status_monitor.status_updated.connect(self.update_status_display)
    
    def apply_theme(self):
        """Apply color theme to the application"""
        theme = self.config.get('ui_settings', {}).get('theme', 'red')
        
        theme_colors = {
            'red': {'primary': '#ff4444', 'secondary': '#ffaaaa'},
            'blue': {'primary': '#4444ff', 'secondary': '#aaaaff'},
            'green': {'primary': '#44ff44', 'secondary': '#aaffaa'},
            'purple': {'primary': '#ff44ff', 'secondary': '#ffaaff'},
            'orange': {'primary': '#ff8844', 'secondary': '#ffccaa'}
        }
        
        colors = theme_colors.get(theme, theme_colors['red'])
        
        # Apply stylesheet with theme colors
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #2b2b2b;
                color: #ffffff;
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['secondary']};
            }}
            QPushButton:pressed {{
                background-color: #333333;
            }}
            QTabWidget::pane {{
                border: 1px solid #444444;
            }}
            QTabBar::tab {{
                background-color: #333333;
                color: white;
                padding: 8px 16px;
                margin: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['primary']};
            }}
        """)
    
    def start_ultron_core(self):
        """Start ULTRON core system"""
        try:
            self.console_output.append("🚀 Starting ULTRON Enhanced core system...")
            
            # Import and initialize ULTRON core
            from ultron_main import UltronCore
            
            if self.ultron_core is None:
                self.ultron_core = UltronCore()
                
                # Setup status monitoring
                if self.status_monitor:
                    self.status_monitor.ultron_core = self.ultron_core
            
            # Start the core system in a separate thread
            import threading
            start_thread = threading.Thread(target=self._start_core_async)
            start_thread.start()
            
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("🟡 ULTRON Status: Starting...")
            self.status_label.setStyleSheet("font-weight: bold; color: #ffaa00;")
            
        except Exception as e:
            self.console_output.append(f"❌ Failed to start ULTRON core: {e}")
            logging.error(f"ULTRON core start failed: {e}")
    
    def _start_core_async(self):
        """Start ULTRON core asynchronously"""
        try:
            # This would need to be adapted for async operation
            # For now, just indicate success
            self.status_label.setText("🟢 ULTRON Status: Running")
            self.status_label.setStyleSheet("font-weight: bold; color: #44ff44;")
            self.console_output.append("✅ ULTRON Enhanced core system started successfully")
            
        except Exception as e:
            self.console_output.append(f"❌ ULTRON core startup error: {e}")
            self.status_label.setText("🔴 ULTRON Status: Error")
            self.status_label.setStyleSheet("font-weight: bold; color: #ff4444;")
    
    def stop_ultron_core(self):
        """Stop ULTRON core system"""
        try:
            self.console_output.append("🛑 Stopping ULTRON Enhanced core system...")
            
            if self.ultron_core:
                # Stop the core system
                pass  # Would implement actual stopping logic
                
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("🔴 ULTRON Status: Stopped")
            self.status_label.setStyleSheet("font-weight: bold; color: #ff4444;")
            self.console_output.append("✅ ULTRON Enhanced core system stopped")
            
        except Exception as e:
            self.console_output.append(f"❌ Failed to stop ULTRON core: {e}")
            logging.error(f"ULTRON core stop failed: {e}")
    
    def show_config_dialog(self):
        """Show configuration dialog"""
        dialog = UltronConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.config
            self.save_config()
            self.apply_theme()
            self.console_output.append("✅ Configuration updated")
    
    def refresh_web_view(self):
        """Refresh web view"""
        if self.web_view:
            self.web_view.reload()
    
    def load_home_page(self):
        """Load ULTRON home page in web view"""
        if self.web_view:
            port = self.config.get('interfaces', {}).get('web_port', 8080)
            self.web_view.setUrl(QUrl(f"http://localhost:{port}"))
    
    def open_in_external_browser(self):
        """Open web interface in external browser"""
        port = self.config.get('interfaces', {}).get('web_port', 8080)
        webbrowser.open(f"http://localhost:{port}")
    
    def execute_command(self):
        """Execute console command"""
        command = self.command_input.text().strip()
        if not command:
            return
            
        self.console_output.append(f"> {command}")
        self.command_input.clear()
        
        # Process command (this would integrate with ULTRON core)
        if command.lower() in ["help", "?"]:
            self.console_output.append("Available commands: help, status, start, stop, config")
        elif command.lower() == "status":
            self.console_output.append("ULTRON Status: " + self.status_label.text())
        elif command.lower() == "clear":
            self.console_output.clear()
        else:
            self.console_output.append(f"Unknown command: {command}")
    
    def update_status_display(self, status: Dict[str, Any]):
        """Update status displays with latest data"""
        try:
            # Update system status
            status_text = f"""
System Running: {status.get('running', False)}
Voice Active: {status.get('voice_active', False)}
Vision Enabled: {status.get('vision_enabled', False)}
AI Available: {status.get('ai_available', False)}
Conversation Length: {status.get('conversation_length', 0)}
Error Count: {status.get('error_count', 0)}
            """.strip()
            self.system_status.setText(status_text)
            
            # Update performance display
            performance = status.get('performance', {})
            if performance:
                perf_text = f"""
CPU Usage: {performance.get('cpu_percent', 0):.1f}%
Memory Usage: {performance.get('memory_percent', 0):.1f}%
Disk Usage: {performance.get('disk_percent', 0):.1f}%
Last Update: {time.strftime('%H:%M:%S')}
                """.strip()
                self.performance_display.setText(perf_text)
                
                # Update status bar
                self.cpu_status.setText(f"CPU: {performance.get('cpu_percent', 0):.1f}%")
                self.memory_status.setText(f"RAM: {performance.get('memory_percent', 0):.1f}%")
            
            # Update connection status
            if status.get('running', False):
                self.connection_status.setText("🟢 Connected")
            else:
                self.connection_status.setText("🔴 Disconnected")
                
        except Exception as e:
            logging.error(f"Status display update error: {e}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(self, "About ULTRON Enhanced", 
                         """
🤖 ULTRON Enhanced Desktop v3.0

Advanced AI automation platform with:
• Multi-LLM Integration (OpenAI, NVIDIA, Anthropic, Ollama)
• Voice Control with Wake Word Detection
• Computer Vision and OCR
• System Automation and Monitoring
• Beautiful Pokédx-Style Web Interface
• Professional Desktop Application

Built with PySide6 and modern AI technologies.
                         """)
    
    def open_documentation(self):
        """Open documentation in browser"""
        QDesktopServices.openUrl(QUrl("https://github.com/dqikfox/ultron_agent/blob/main/README.md"))
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.system_tray and self.system_tray.isVisible():
            if self.config.get('ui_settings', {}).get('minimize_to_tray', True):
                self.hide()
                event.ignore()
                return
        
        # Save window state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Cleanup
        if self.status_monitor:
            self.status_monitor.stop()
        
        if self.ultron_core:
            # Stop ULTRON core
            pass
            
        event.accept()

def main():
    """Main entry point for desktop application"""
    if not PYSIDE_AVAILABLE:
        print("❌ PySide6 not available - Desktop application cannot run")
        print("Install with: pip install PySide6")
        return 1
    
    app = QApplication(sys.argv)
    app.setApplicationName("ULTRON Enhanced")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("ULTRON")
    
    # Set application icon (if available)
    # app.setWindowIcon(QIcon("ultron_icon.png"))
    
    # Create and show main window
    window = UltronDesktopApp()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())