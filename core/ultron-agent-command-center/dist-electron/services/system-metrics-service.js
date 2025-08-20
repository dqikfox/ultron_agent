"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SystemMetricsService = void 0;
const electron_1 = require("electron");
const os = __importStar(require("os"));
const process = __importStar(require("process"));
class SystemMetricsService {
    constructor() {
        this.cpuUsageHistory = [];
        this.networkActivity = false;
        this.lastNetworkCheck = Date.now();
        this.appStartTime = Date.now();
        this.metricsInterval = null;
        this.initializeMetrics();
    }
    initializeMetrics() {
        // Start collecting CPU usage history
        this.metricsInterval = setInterval(() => {
            this.updateCpuUsage();
            this.updateNetworkActivity();
        }, 1000);
        // Monitor network status changes
        if (electron_1.powerMonitor) {
            electron_1.powerMonitor.on('resume', () => {
                this.networkActivity = true;
            });
        }
    }
    updateCpuUsage() {
        // Calculate CPU usage based on process CPU time
        const usage = process.cpuUsage();
        const totalUsage = (usage.user + usage.system) / 1000000; // Convert to seconds
        // Simple CPU usage calculation (this is an approximation)
        const cpuPercent = Math.min(100, (totalUsage % 100));
        this.cpuUsageHistory.push(cpuPercent);
        if (this.cpuUsageHistory.length > 60) {
            this.cpuUsageHistory.shift(); // Keep last 60 seconds
        }
    }
    updateNetworkActivity() {
        // Simple network activity simulation based on time
        const now = Date.now();
        const timeSinceLastCheck = now - this.lastNetworkCheck;
        // Simulate network activity detection
        this.networkActivity = timeSinceLastCheck < 5000 && Math.random() > 0.7;
        this.lastNetworkCheck = now;
    }
    async getMetrics() {
        const cpus = os.cpus();
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;
        // Calculate average CPU usage
        const avgCpuUsage = this.cpuUsageHistory.length > 0
            ? this.cpuUsageHistory.reduce((a, b) => a + b, 0) / this.cpuUsageHistory.length
            : 0;
        return {
            cpu: {
                usage: Math.round(avgCpuUsage * 10) / 10,
                cores: cpus.length,
                model: cpus[0]?.model || 'Unknown',
                speed: cpus[0]?.speed || 0
            },
            memory: {
                usage: Math.round((usedMem / totalMem) * 100 * 10) / 10,
                total: totalMem,
                used: usedMem,
                available: freeMem
            },
            network: {
                isOnline: true, // Assume online in Electron main process
                activity: this.networkActivity
            },
            uptime: {
                system: os.uptime(),
                app: Math.floor((Date.now() - this.appStartTime) / 1000)
            },
            platform: {
                os: os.type(),
                version: os.release(),
                arch: os.arch()
            }
        };
    }
    async getCpuInfo() {
        const cpus = os.cpus();
        const loadAvg = os.loadavg();
        return {
            model: cpus[0]?.model || 'Unknown',
            cores: cpus.length,
            speed: cpus[0]?.speed || 0,
            usage: this.cpuUsageHistory.length > 0
                ? this.cpuUsageHistory[this.cpuUsageHistory.length - 1]
                : 0,
            loadAverage: loadAvg
        };
    }
    async getMemoryInfo() {
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;
        return {
            total: totalMem,
            used: usedMem,
            free: freeMem,
            usagePercent: Math.round((usedMem / totalMem) * 100 * 10) / 10,
            processMemory: process.memoryUsage()
        };
    }
    async getNetworkInfo() {
        return {
            interfaces: os.networkInterfaces(),
            isOnline: true, // Assume online in Electron main process
            activity: this.networkActivity
        };
    }
    async getPlatformInfo() {
        return {
            type: os.type(),
            platform: os.platform(),
            arch: os.arch(),
            release: os.release(),
            version: os.version(),
            hostname: os.hostname(),
            uptime: os.uptime(),
            electronVersion: process.versions.electron || 'Unknown',
            nodeVersion: process.versions.node
        };
    }
    // Real-time monitoring
    startMonitoring(callback, intervalMs = 1000) {
        return setInterval(async () => {
            const metrics = await this.getMetrics();
            callback(metrics);
        }, intervalMs);
    }
    // Resource usage alerts
    checkResourceAlerts() {
        const warnings = [];
        let cpuAlert = false;
        let memoryAlert = false;
        // Check CPU usage
        if (this.cpuUsageHistory.length > 0) {
            const recentUsage = this.cpuUsageHistory.slice(-10);
            const avgRecentUsage = recentUsage.reduce((a, b) => a + b, 0) / recentUsage.length;
            if (avgRecentUsage > 80) {
                cpuAlert = true;
                warnings.push(`High CPU usage detected: ${avgRecentUsage.toFixed(1)}%`);
            }
        }
        // Check memory usage
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const memoryUsage = ((totalMem - freeMem) / totalMem) * 100;
        if (memoryUsage > 85) {
            memoryAlert = true;
            warnings.push(`High memory usage detected: ${memoryUsage.toFixed(1)}%`);
        }
        return {
            cpu: cpuAlert,
            memory: memoryAlert,
            warnings
        };
    }
    destroy() {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
        }
    }
}
exports.SystemMetricsService = SystemMetricsService;
//# sourceMappingURL=system-metrics-service.js.map