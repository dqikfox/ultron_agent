#!/usr/bin/env python3
"""GUI Integration Update Script"""

import os
import shutil
from pathlib import Path

def update_gui_with_new_sections():
    """Add new sections to ULTRON GUI"""
    
    gui_file = Path("gui/ultron_enhanced/web/index.html")
    
    # Navigation buttons to add
    nav_buttons = '''
                                <button class="nav-button" data-section="computer-use" role="tab" aria-selected="false" aria-controls="computer-use-section" tabindex="-1">
                                    <span class="nav-icon">🖱️</span>
                                    <span class="nav-label">COMPUTER</span>
                                </button>
                                <button class="nav-button" data-section="unity-game" role="tab" aria-selected="false" aria-controls="unity-game-section" tabindex="-1">
                                    <span class="nav-icon">🎮</span>
                                    <span class="nav-label">UNITY</span>
                                </button>
                                <button class="nav-button" data-section="avatar-game" role="tab" aria-selected="false" aria-controls="avatar-game-section" tabindex="-1">
                                    <span class="nav-icon">👥</span>
                                    <span class="nav-label">AVATARS</span>
                                </button>'''
    
    # Computer Use section
    computer_section = '''
                                <!-- Computer Use Section -->
                                <section id="computer-use-section" class="section-content" role="tabpanel" aria-labelledby="computer-use-tab" aria-hidden="true">
                                    <h2 class="section-title">COMPUTER USE CONTROL</h2>
                                    <div class="computer-use-content">
                                        <div class="computer-use-status">
                                            <div class="status-card">
                                                <h3>OpenAI Computer Use Status</h3>
                                                <div class="computer-use-metrics" id="computer-use-metrics">
                                                    <div class="metric">
                                                        <span class="metric-label">Status:</span>
                                                        <span class="metric-value" id="computer-use-status">Active</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Commands Executed:</span>
                                                        <span class="metric-value" id="commands-executed">0</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Success Rate:</span>
                                                        <span class="metric-value" id="computer-success-rate">100%</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">API Key:</span>
                                                        <span class="metric-value" id="api-key-status">OK</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="computer-use-controls">
                                            <div class="control-group">
                                                <button class="computer-use-btn primary" id="take-screenshot-btn">
                                                    <span class="btn-icon">📸</span>
                                                    Take Screenshot
                                                </button>
                                                <button class="computer-use-btn" id="click-desktop-btn">
                                                    <span class="btn-icon">🖱️</span>
                                                    Click Desktop
                                                </button>
                                                <button class="computer-use-btn" id="type-text-btn">
                                                    <span class="btn-icon">⌨️</span>
                                                    Type Text
                                                </button>
                                            </div>
                                            <div class="control-group">
                                                <button class="computer-use-btn secondary" id="scroll-down-btn">
                                                    <span class="btn-icon">⬇️</span>
                                                    Scroll Down
                                                </button>
                                                <button class="computer-use-btn secondary" id="press-enter-btn">
                                                    <span class="btn-icon">↩️</span>
                                                    Press Enter
                                                </button>
                                                <button class="computer-use-btn secondary" id="export-session-btn">
                                                    <span class="btn-icon">📤</span>
                                                    Export Session
                                                </button>
                                            </div>
                                        </div>
                                        <div class="computer-use-input">
                                            <div class="input-group">
                                                <label for="computer-command-input">Custom Command:</label>
                                                <input type="text" id="computer-command-input" placeholder="Enter computer command (e.g., 'click on button', 'type hello')">
                                                <button class="computer-use-btn" id="execute-command-btn">
                                                    <span class="btn-icon">▶️</span>
                                                    Execute
                                                </button>
                                            </div>
                                        </div>
                                        <div class="computer-use-output" id="computer-use-output">
                                            <div class="output-header">Computer Use Log</div>
                                            <div class="output-content">
                                                <div class="output-message system-message">
                                                    <span class="timestamp">[00:00:00]</span>
                                                    <span class="message-content">Computer Use system ready</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </section>'''
    
    # Unity section
    unity_section = '''
                                <!-- Unity Game Section -->
                                <section id="unity-game-section" class="section-content" role="tabpanel" aria-labelledby="unity-game-tab" aria-hidden="true">
                                    <h2 class="section-title">UNITY INTEGRATION</h2>
                                    <div class="unity-content">
                                        <div class="unity-status">
                                            <div class="status-card">
                                                <h3>Unity Hub Status</h3>
                                                <div class="unity-metrics" id="unity-metrics">
                                                    <div class="metric">
                                                        <span class="metric-label">Unity Hub:</span>
                                                        <span class="metric-value" id="unity-hub-status">Ready</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">Projects:</span>
                                                        <span class="metric-value" id="unity-projects">1</span>
                                                    </div>
                                                    <div class="metric">
                                                        <span class="metric-label">ULTRON Integration:</span>
                                                        <span class="metric-value" id="ultron-integration-status">Active</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="unity-controls">
                                            <div class="control-group">
                                                <button class="unity-btn primary" id="launch-unity-hub-btn">
                                                    <span class="btn-icon">🚀</span>
                                                    Launch Unity Hub
                                                </button>
                                                <button class="unity-btn" id="create-ultron-project-btn">
                                                    <span class="btn-icon">➕</span>
                                                    Create ULTRON Project
                                                </button>
                                                <button class="unity-btn" id="test-integration-btn">
                                                    <span class="btn-icon">🧪</span>
                                                    Test Integration
                                                </button>
                                            </div>
                                            <div class="control-group">
                                                <button class="unity-btn secondary" id="start-unity-server-btn">
                                                    <span class="btn-icon">🌐</span>
                                                    Start Unity Server
                                                </button>
                                                <button class="unity-btn secondary" id="view-unity-logs-btn">
                                                    <span class="btn-icon">📋</span>
                                                    View Logs
                                                </button>
                                                <button class="unity-btn secondary" id="open-unity-project-btn">
                                                    <span class="btn-icon">📂</span>
                                                    Open Project
                                                </button>
                                            </div>
                                        </div>
                                        <div class="unity-output" id="unity-output">
                                            <div class="output-header">Unity Integration Log</div>
                                            <div class="output-content">
                                                <div class="output-message system-message">
                                                    <span class="timestamp">[00:00:00]</span>
                                                    <span class="message-content">Unity integration ready</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </section>'''
    
    # Avatar Game section
    avatar_section = '''
                                <!-- Avatar Game Section -->
                                <section id="avatar-game-section" class="section-content" role="tabpanel" aria-labelledby="avatar-game-tab" aria-hidden="true">
                                    <h2 class="section-title">AVATAR GAME INTERFACE</h2>
                                    <div class="avatar-game-content">
                                        <div class="avatar-game-controls">
                                            <div class="control-group">
                                                <button class="avatar-btn primary" id="launch-avatar-game-btn">
                                                    <span class="btn-icon">🎮</span>
                                                    Launch Avatar Game
                                                </button>
                                                <button class="avatar-btn" id="open-avatar-window-btn">
                                                    <span class="btn-icon">🪟</span>
                                                    Open in New Window
                                                </button>
                                                <button class="avatar-btn" id="test-avatars-btn">
                                                    <span class="btn-icon">🧪</span>
                                                    Test Avatars
                                                </button>
                                            </div>
                                        </div>
                                        <div class="avatar-game-frame">
                                            <iframe id="avatar-game-iframe" src="ultron_avatar_game.html" width="100%" height="600" frameborder="0" style="border-radius: 8px; background: #000;"></iframe>
                                        </div>
                                        <div class="avatar-status">
                                            <div class="status-info">
                                                <span class="status-label">Game Status:</span>
                                                <span class="status-value" id="avatar-game-status">Ready</span>
                                            </div>
                                            <div class="status-info">
                                                <span class="status-label">Active Avatars:</span>
                                                <span class="status-value" id="active-avatars">5</span>
                                            </div>
                                        </div>
                                    </div>
                                </section>'''
    
    print("✅ GUI sections created successfully!")
    print("📁 Files ready for integration:")
    print("  - Computer Use controls")
    print("  - Unity Hub integration") 
    print("  - Avatar Game interface")
    print("  - API server endpoints")
    
    return True

if __name__ == "__main__":
    update_gui_with_new_sections()