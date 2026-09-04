/**
 * Enhanced Vision Integration - Interactive and User-Friendly
 */

class EnhancedVisionIntegration {
    constructor() {
        this.apiBase = 'http://localhost:5001/api/vision';
        this.isCapturing = false;
        this.currentScreenshot = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupProgressIndicator();
        this.checkStatus();
    }

    bindEvents() {
        const captureBtn = document.getElementById('capture-btn');
        const analyzeBtn = document.getElementById('analyze-btn');

        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.captureWithProgress());
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.showLatestResults());
        }
    }

    setupProgressIndicator() {
        // Add progress bar to vision display
        const visionDisplay = document.getElementById('vision-display');
        if (visionDisplay) {
            visionDisplay.innerHTML = `
                <div class="vision-welcome">
                    <div class="welcome-icon">👁️</div>
                    <h3>ULTRON Vision System</h3>
                    <p>Advanced OCR Screenshot Analysis</p>
                    <div class="vision-features">
                        <div class="feature">📸 Smart Screenshot Capture</div>
                        <div class="feature">🔍 OCR Text Recognition</div>
                        <div class="feature">🧠 AI Visual Analysis</div>
                        <div class="feature">📄 Detailed Reports</div>
                    </div>
                    <button class="start-vision-btn" onclick="enhancedVision.captureWithProgress()">
                        🚀 Start Vision Analysis
                    </button>
                </div>
            `;
        }
    }

    async captureWithProgress() {
        if (this.isCapturing) return;

        this.isCapturing = true;
        this.showProgressSteps();

        try {
            // Step 1: Initialize
            this.updateProgress(1, "Initializing vision system...");
            await this.delay(500);

            // Step 2: Capture
            this.updateProgress(2, "Capturing screenshot...");
            await this.delay(1000);

            // Step 3: OCR Processing
            this.updateProgress(3, "Processing OCR analysis...");
            
            const response = await fetch(`${this.apiBase}/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success) {
                // Step 4: Complete
                this.updateProgress(4, "Analysis complete!");
                await this.delay(500);
                
                this.currentScreenshot = data;
                this.displayResults(data);
                this.showSuccessNotification();
            } else {
                throw new Error(data.error || 'Capture failed');
            }

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.isCapturing = false;
        }
    }

    showProgressSteps() {
        const visionDisplay = document.getElementById('vision-display');
        if (!visionDisplay) return;

        visionDisplay.innerHTML = `
            <div class="vision-progress">
                <div class="progress-header">
                    <h3>📸 Vision Analysis in Progress</h3>
                </div>
                <div class="progress-steps">
                    <div class="step" id="step-1">
                        <div class="step-icon">⚡</div>
                        <div class="step-text">Initialize</div>
                    </div>
                    <div class="step" id="step-2">
                        <div class="step-icon">📷</div>
                        <div class="step-text">Capture</div>
                    </div>
                    <div class="step" id="step-3">
                        <div class="step-icon">🔍</div>
                        <div class="step-text">Analyze</div>
                    </div>
                    <div class="step" id="step-4">
                        <div class="step-icon">✅</div>
                        <div class="step-text">Complete</div>
                    </div>
                </div>
                <div class="progress-status" id="progress-status">
                    Starting vision analysis...
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
            </div>
        `;
    }

    updateProgress(step, message) {
        const statusEl = document.getElementById('progress-status');
        const fillEl = document.getElementById('progress-fill');
        const stepEl = document.getElementById(`step-${step}`);

        if (statusEl) statusEl.textContent = message;
        if (fillEl) fillEl.style.width = `${(step / 4) * 100}%`;
        if (stepEl) stepEl.classList.add('active');
    }

    displayResults(data) {
        const visionDisplay = document.getElementById('vision-display');
        if (!visionDisplay) return;

        const timestamp = new Date().toLocaleString();
        const analysisLines = data.analysis ? data.analysis.split('\n').filter(line => line.trim()) : [];

        visionDisplay.innerHTML = `
            <div class="vision-results">
                <div class="results-header">
                    <div class="header-left">
                        <h3>📸 Vision Analysis Complete</h3>
                        <div class="timestamp">${timestamp}</div>
                    </div>
                    <div class="header-right">
                        <div class="status-badge success">✅ SUCCESS</div>
                    </div>
                </div>

                <div class="results-content">
                    <div class="result-section">
                        <h4>🔍 What's On Screen:</h4>
                        <div class="analysis-list">
                            ${analysisLines.map(line => `
                                <div class="analysis-item">
                                    <span class="item-icon">▶</span>
                                    <span class="item-text">${line.replace('- ', '')}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <div class="result-section">
                        <h4>📁 Files Created:</h4>
                        <div class="file-list">
                            <div class="file-item">
                                <span class="file-icon">🖼️</span>
                                <span class="file-name">${this.getFileName(data.image_path)}</span>
                                <button class="file-btn" onclick="enhancedVision.openFile('${data.image_path}')">View</button>
                            </div>
                            <div class="file-item">
                                <span class="file-icon">📄</span>
                                <span class="file-name">${this.getFileName(data.description_path)}</span>
                                <button class="file-btn" onclick="enhancedVision.openFile('${data.description_path}')">Read</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="results-actions">
                    <button class="action-btn primary" onclick="enhancedVision.captureWithProgress()">
                        🔄 Capture New
                    </button>
                    <button class="action-btn secondary" onclick="enhancedVision.openScreenshotsFolder()">
                        📁 Open Folder
                    </button>
                    <button class="action-btn secondary" onclick="enhancedVision.showFullReport()">
                        📊 Full Report
                    </button>
                    <button class="action-btn secondary" onclick="enhancedVision.exportResults()">
                        💾 Export
                    </button>
                </div>
            </div>
        `;
    }

    showSuccessNotification() {
        // Create floating notification
        const notification = document.createElement('div');
        notification.className = 'vision-notification success';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">✅</span>
                <span class="notification-text">Screenshot analyzed successfully!</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showError(message) {
        const visionDisplay = document.getElementById('vision-display');
        if (!visionDisplay) return;

        visionDisplay.innerHTML = `
            <div class="vision-error">
                <div class="error-icon">❌</div>
                <h3>Vision Analysis Failed</h3>
                <p class="error-message">${message}</p>
                <div class="error-actions">
                    <button class="retry-btn" onclick="enhancedVision.captureWithProgress()">
                        🔄 Try Again
                    </button>
                    <button class="help-btn" onclick="enhancedVision.showHelp()">
                        ❓ Get Help
                    </button>
                </div>
            </div>
        `;
    }

    showLatestResults() {
        if (this.currentScreenshot) {
            this.displayResults(this.currentScreenshot);
        } else {
            this.updateVisionDisplay('No previous analysis found. Click CAPTURE to start.');
        }
    }

    showFullReport() {
        if (!this.currentScreenshot) return;

        const modal = document.createElement('div');
        modal.className = 'vision-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>📊 Full Vision Analysis Report</h3>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">✕</button>
                </div>
                <div class="modal-body">
                    <pre class="full-report">${this.currentScreenshot.full_result}</pre>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    openFile(filePath) {
        console.log(`Opening file: ${filePath}`);
        alert(`File location: ${filePath}\n\nNote: File operations require desktop access.`);
    }

    openScreenshotsFolder() {
        const path = 'C:\\Users\\ultro\\OneDrive\\Pictures\\Screenshots';
        console.log(`Screenshots folder: ${path}`);
        alert(`Screenshots saved to:\n${path}\n\nOpen this folder in File Explorer to view your screenshots.`);
    }

    exportResults() {
        if (!this.currentScreenshot) return;

        const data = {
            timestamp: new Date().toISOString(),
            analysis: this.currentScreenshot.analysis,
            image_path: this.currentScreenshot.image_path,
            description_path: this.currentScreenshot.description_path
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vision_analysis_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showHelp() {
        const modal = document.createElement('div');
        modal.className = 'vision-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>❓ Vision System Help</h3>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="help-section">
                        <h4>🔧 Troubleshooting:</h4>
                        <ul>
                            <li>Ensure OCR server is running on port 5001</li>
                            <li>Check that Tesseract OCR is installed</li>
                            <li>Verify screenshot permissions</li>
                            <li>Try refreshing the page</li>
                        </ul>
                    </div>
                    <div class="help-section">
                        <h4>📋 Features:</h4>
                        <ul>
                            <li>Smart screenshot capture</li>
                            <li>OCR text recognition</li>
                            <li>AI visual analysis</li>
                            <li>Detailed reporting</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Vision system online');
            }
        } catch (error) {
            console.warn('⚠️ Vision API unavailable');
        }
    }

    getFileName(path) {
        if (!path) return 'Unknown';
        return path.split('\\').pop() || path.split('/').pop() || path;
    }

    updateVisionDisplay(message) {
        const visionDisplay = document.getElementById('vision-display');
        if (visionDisplay) {
            visionDisplay.innerHTML = `<div class="vision-message">${message}</div>`;
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize enhanced vision
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedVision = new EnhancedVisionIntegration();
});

// Enhanced CSS styles
const enhancedStyles = `
<style>
.vision-welcome {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(255,68,68,0.1), rgba(255,68,68,0.05));
    border: 2px solid rgba(255,68,68,0.3);
    border-radius: 12px;
}

.welcome-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.vision-features {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin: 1rem 0;
    text-align: left;
}

.feature {
    padding: 0.5rem;
    background: rgba(0,0,0,0.3);
    border-radius: 6px;
    font-size: 0.9rem;
}

.start-vision-btn {
    padding: 1rem 2rem;
    background: linear-gradient(45deg, #ff4444, #ff6666);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    cursor: pointer;
    margin-top: 1rem;
}

.vision-progress {
    text-align: center;
    padding: 2rem;
}

.progress-steps {
    display: flex;
    justify-content: space-between;
    margin: 2rem 0;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    opacity: 0.5;
    transition: opacity 0.3s;
}

.step.active {
    opacity: 1;
    color: #ff4444;
}

.step-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(0,0,0,0.3);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 1rem;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #ff4444, #ff6666);
    width: 0%;
    transition: width 0.5s ease;
}

.vision-results {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,68,68,0.3);
    border-radius: 12px;
    padding: 1.5rem;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,68,68,0.2);
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
}

.status-badge.success {
    background: rgba(0,255,0,0.2);
    color: #00ff00;
    border: 1px solid rgba(0,255,0,0.3);
}

.result-section {
    margin-bottom: 1.5rem;
}

.result-section h4 {
    color: #ff6666;
    margin-bottom: 0.8rem;
    font-size: 1rem;
}

.analysis-list {
    background: rgba(0,0,0,0.3);
    border-radius: 8px;
    padding: 1rem;
}

.analysis-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    padding: 0.3rem;
}

.item-icon {
    color: #ff4444;
    margin-right: 0.5rem;
}

.file-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem;
    background: rgba(0,0,0,0.3);
    border-radius: 6px;
}

.file-btn {
    padding: 0.3rem 0.8rem;
    background: #ff4444;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
}

.results-actions {
    display: flex;
    gap: 0.8rem;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255,68,68,0.2);
}

.action-btn {
    padding: 0.8rem 1.2rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s;
}

.action-btn.primary {
    background: linear-gradient(45deg, #ff4444, #ff6666);
    color: white;
}

.action-btn.secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.2);
}

.vision-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    z-index: 1000;
    animation: slideIn 0.3s ease;
}

.vision-notification.success {
    background: rgba(0,255,0,0.2);
    border: 1px solid rgba(0,255,0,0.3);
    color: #00ff00;
}

.vision-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: #1a1a1a;
    border: 2px solid #ff4444;
    border-radius: 12px;
    max-width: 80%;
    max-height: 80%;
    overflow: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(255,68,68,0.3);
}

.close-btn {
    background: none;
    border: none;
    color: #ff4444;
    font-size: 1.5rem;
    cursor: pointer;
}

.modal-body {
    padding: 1.5rem;
}

.full-report {
    background: rgba(0,0,0,0.5);
    padding: 1rem;
    border-radius: 6px;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    max-height: 400px;
    overflow: auto;
}

@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', enhancedStyles);