/**
 * Vision Integration for ULTRON GUI
 * Connects OCR screenshot analyzer to the Vision section
 */

class VisionIntegration {
    constructor() {
        this.apiBase = 'http://localhost:5001/api/vision';
        this.isCapturing = false;
        this.isAnalyzing = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkStatus();
    }

    bindEvents() {
        const captureBtn = document.getElementById('capture-btn');
        const analyzeBtn = document.getElementById('analyze-btn');

        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.captureScreenshot());
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeLatestScreenshot());
        }
    }

    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            const data = await response.json();
            
            if (data.success) {
                this.updateVisionDisplay('Vision system online - OCR ready');
                console.log('Vision system status:', data.tools);
            } else {
                this.updateVisionDisplay('Vision system offline');
            }
        } catch (error) {
            this.updateVisionDisplay('Vision API unavailable - start gui_ocr_integration.py');
            console.error('Vision status check failed:', error);
        }
    }

    async captureScreenshot() {
        if (this.isCapturing) return;

        this.isCapturing = true;
        this.updateVisionDisplay('📸 Capturing screenshot with OCR analysis...');
        this.updateCaptureButton('⏳ CAPTURING...');

        try {
            const response = await fetch(`${this.apiBase}/capture`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.displayAnalysisResult(data.result);
                this.logMessage('Screenshot captured and analyzed with OCR');
            } else {
                this.updateVisionDisplay(`❌ Capture failed: ${data.error}`);
            }
        } catch (error) {
            this.updateVisionDisplay(`❌ Capture error: ${error.message}`);
            console.error('Screenshot capture failed:', error);
        } finally {
            this.isCapturing = false;
            this.updateCaptureButton('📷 CAPTURE');
        }
    }

    async analyzeLatestScreenshot() {
        if (this.isAnalyzing) return;

        // Get latest screenshot from Pictures folder
        const screenshotsPath = `C:\\Users\\${this.getUsername()}\\OneDrive\\Pictures\\Screenshots`;
        
        this.isAnalyzing = true;
        this.updateVisionDisplay('🔍 Analyzing latest screenshot...');
        this.updateAnalyzeButton('⏳ ANALYZING...');

        try {
            // For now, just trigger a new capture since we can't easily browse files from web
            await this.captureScreenshot();
        } catch (error) {
            this.updateVisionDisplay(`❌ Analysis error: ${error.message}`);
            console.error('Screenshot analysis failed:', error);
        } finally {
            this.isAnalyzing = false;
            this.updateAnalyzeButton('🔍 ANALYZE');
        }
    }

    displayAnalysisResult(result) {
        const visionDisplay = document.getElementById('vision-display');
        if (!visionDisplay) return;

        // Parse the result to extract key information
        const lines = result.split('\n');
        const imagePath = lines.find(line => line.includes('Image:'))?.replace('Image: ', '') || '';
        const descriptionPath = lines.find(line => line.includes('Description:'))?.replace('Description: ', '') || '';

        // Create analysis display
        visionDisplay.innerHTML = `
            <div class="vision-result">
                <div class="result-header">
                    <span class="result-title">📸 OCR Screenshot Analysis Complete</span>
                    <span class="result-timestamp">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="result-content">
                    <div class="result-section">
                        <h4>📁 Files Created:</h4>
                        <div class="file-info">
                            <div class="file-item">🖼️ Screenshot: ${this.getFileName(imagePath)}</div>
                            <div class="file-item">📄 Analysis: ${this.getFileName(descriptionPath)}</div>
                        </div>
                    </div>
                    <div class="result-section">
                        <h4>🔍 Analysis Preview:</h4>
                        <div class="analysis-preview">
                            ${this.formatAnalysisPreview(result)}
                        </div>
                    </div>
                    <div class="result-actions">
                        <button class="vision-action-btn" onclick="visionIntegration.openScreenshotsFolder()">
                            📁 Open Screenshots Folder
                        </button>
                        <button class="vision-action-btn" onclick="visionIntegration.captureScreenshot()">
                            🔄 Capture New
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    formatAnalysisPreview(result) {
        // Extract key analysis points
        const lines = result.split('\n');
        const analysisStart = lines.findIndex(line => line.includes('WHAT\'S ACTUALLY ON SCREEN:'));
        
        if (analysisStart !== -1) {
            const analysisLines = lines.slice(analysisStart + 1, analysisStart + 8);
            return analysisLines
                .filter(line => line.trim().startsWith('-'))
                .map(line => `<div class="analysis-item">${line.trim()}</div>`)
                .join('');
        }
        
        return '<div class="analysis-item">✅ OCR analysis completed successfully</div>';
    }

    getFileName(fullPath) {
        if (!fullPath) return 'Unknown';
        return fullPath.split('\\').pop() || fullPath.split('/').pop() || fullPath;
    }

    getUsername() {
        // Try to get username from environment or use default
        return 'ultro'; // Default username based on your system
    }

    openScreenshotsFolder() {
        // This would need to be handled by the backend
        this.logMessage('Screenshots folder location logged to console');
        console.log('Screenshots folder: C:\\Users\\ultro\\OneDrive\\Pictures\\Screenshots');
        alert('Screenshots saved to: C:\\Users\\ultro\\OneDrive\\Pictures\\Screenshots');
    }

    updateVisionDisplay(message) {
        const visionDisplay = document.getElementById('vision-display');
        if (visionDisplay) {
            visionDisplay.innerHTML = `
                <div class="vision-status">
                    <div class="status-message">${message}</div>
                </div>
            `;
        }
    }

    updateCaptureButton(text) {
        const captureBtn = document.getElementById('capture-btn');
        if (captureBtn) {
            captureBtn.textContent = text;
            captureBtn.disabled = this.isCapturing;
        }
    }

    updateAnalyzeButton(text) {
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.textContent = text;
            analyzeBtn.disabled = this.isAnalyzing;
        }
    }

    logMessage(message) {
        console.log(`[Vision] ${message}`);
        
        // Log to main interface if available
        if (window.ultronInterface && window.ultronInterface.logMessage) {
            window.ultronInterface.logMessage(`[Vision] ${message}`);
        }
    }
}

// Initialize vision integration when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.visionIntegration = new VisionIntegration();
});

// Add CSS styles for vision integration
const visionStyles = `
<style>
.vision-result {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 0, 0, 0.3);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 0, 0, 0.2);
}

.result-title {
    color: #ff4444;
    font-weight: bold;
    font-family: 'Share Tech Mono', monospace;
}

.result-timestamp {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.9rem;
    font-family: 'Share Tech Mono', monospace;
}

.result-section {
    margin-bottom: 1rem;
}

.result-section h4 {
    color: #ff6666;
    margin-bottom: 0.5rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.9rem;
}

.file-info {
    background: rgba(0, 0, 0, 0.2);
    padding: 0.5rem;
    border-radius: 4px;
    border-left: 3px solid #ff4444;
}

.file-item {
    color: rgba(255, 255, 255, 0.8);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    margin-bottom: 0.25rem;
}

.analysis-preview {
    background: rgba(0, 0, 0, 0.2);
    padding: 0.5rem;
    border-radius: 4px;
    border-left: 3px solid #00ff00;
    max-height: 150px;
    overflow-y: auto;
}

.analysis-item {
    color: rgba(255, 255, 255, 0.8);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    margin-bottom: 0.25rem;
    padding-left: 0.5rem;
}

.result-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(255, 0, 0, 0.2);
}

.vision-action-btn {
    padding: 0.5rem 1rem;
    background: linear-gradient(45deg, #ff4444, #ff6666);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.8rem;
    transition: all 0.3s ease;
}

.vision-action-btn:hover {
    background: linear-gradient(45deg, #ff6666, #ff8888);
    transform: translateY(-1px);
}

.vision-status {
    text-align: center;
    padding: 2rem;
    color: rgba(255, 255, 255, 0.8);
    font-family: 'Share Tech Mono', monospace;
}

.status-message {
    font-size: 1rem;
    line-height: 1.5;
}
</style>
`;

// Inject styles into the document
document.head.insertAdjacentHTML('beforeend', visionStyles);