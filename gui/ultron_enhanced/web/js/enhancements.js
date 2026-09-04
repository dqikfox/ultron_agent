/**
 * ULTRON GUI Enhancements - Critical Features
 */

// Notification System
class NotificationManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:10000;max-width:400px;';
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        const colors = {success: '#10b981', error: '#ef4444', warning: '#f59e0b', info: '#3b82f6'};
        const icons = {success: '✓', error: '✕', warning: '⚠', info: 'ℹ'};

        notification.style.cssText = `background:${colors[type]};color:white;padding:15px 20px;margin-bottom:10px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.3);animation:slideIn 0.3s ease;cursor:pointer;display:flex;align-items:center;gap:10px;`;
        notification.innerHTML = `<span style="font-size:20px;">${icons[type]}</span><span style="flex:1;">${message}</span><span style="opacity:0.7;">✕</span>`;

        notification.onclick = () => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        };

        this.container.appendChild(notification);
        if (duration > 0) setTimeout(() => notification.click(), duration);
    }
}

// Screenshot Manager
class ScreenshotManager {
    constructor() {
        this.history = [];
    }

    async capture(showCountdown = true) {
        if (showCountdown) await this.showCountdown();

        try {
            const response = await fetch('/api/vision/capture', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            const data = await response.json();

            if (data.success) {
                this.history.unshift(data);
                notifications.show('Screenshot captured!', 'success');
                return data;
            } else {
                notifications.show('Failed: ' + data.error, 'error');
            }
        } catch (error) {
            notifications.show('Error: ' + error.message, 'error');
        }
    }

    async showCountdown() {
        const overlay = document.createElement('div');
        overlay.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);color:white;padding:40px 60px;border-radius:20px;font-size:72px;font-weight:bold;z-index:9999;text-align:center;';
        document.body.appendChild(overlay);

        for (let i = 3; i > 0; i--) {
            overlay.textContent = i;
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        overlay.remove();
    }

    async analyze() {
        notifications.show('Analyzing...', 'info', 0);

        try {
            const response = await fetch('/api/vision/analyze', {method: 'POST', headers: {'Content-Type': 'application/json'}});
            const data = await response.json();

            if (data.success) {
                notifications.show('Analysis complete!', 'success');
                this.displayAnalysis(data);
            } else {
                notifications.show('Failed: ' + data.error, 'error');
            }
        } catch (error) {
            notifications.show('Error: ' + error.message, 'error');
        }
    }

    displayAnalysis(data) {
        const container = document.getElementById('analysis-results');
        if (!container) return;

        container.innerHTML = `
            <div style="background:rgba(255,255,255,0.05);padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #0ea5e9;">
                <h3>🤖 AI Description</h3>
                <p>${data.ai_description}</p>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #10b981;">
                <h3>📝 OCR Text</h3>
                <pre>${data.ocr_text || 'No text'}</pre>
                <button onclick="navigator.clipboard.writeText('${data.ocr_text}');notifications.show('Copied!','success')">Copy</button>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #f59e0b;">
                <h3>📊 Confidence: ${data.ocr_confidence}%</h3>
                <div style="width:100%;height:20px;background:rgba(255,255,255,0.1);border-radius:10px;overflow:hidden;">
                    <div style="height:100%;width:${data.ocr_confidence}%;background:linear-gradient(90deg,#10b981,#0ea5e9);transition:width 0.5s;"></div>
                </div>
            </div>
        `;
    }
}

// Keyboard Shortcuts
class ShortcutManager {
    constructor() {
        document.addEventListener('keydown', (e) => {
            if (!e.key) return; // Safety check for undefined key
            const key = (e.ctrlKey ? 'ctrl+' : '') + (e.altKey ? 'alt+' : '') + e.key.toLowerCase();

            const actions = {
                'ctrl+s': () => screenshot.capture(),
                'ctrl+a': () => screenshot.analyze(),
                'f1': () => alert('Shortcuts:\nCtrl+S: Screenshot\nCtrl+A: Analyze\nF1: Help')
            };

            if (actions[key]) {
                e.preventDefault();
                actions[key]();
            }
        });
    }
}

// Initialize
const notifications = new NotificationManager();
const screenshot = new ScreenshotManager();
const shortcuts = new ShortcutManager();

// Add CSS
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
@keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(400px); opacity: 0; } }
`;
document.head.appendChild(style);

window.ultronEnhancements = {notifications, screenshot, shortcuts};
console.log('🚀 ULTRON Enhancements Loaded');
