import * as os from 'os';
export interface SystemMetrics {
    cpu: {
        usage: number;
        cores: number;
        model: string;
        speed: number;
    };
    memory: {
        usage: number;
        total: number;
        used: number;
        available: number;
    };
    network: {
        isOnline: boolean;
        activity: boolean;
    };
    uptime: {
        system: number;
        app: number;
    };
    platform: {
        os: string;
        version: string;
        arch: string;
    };
}
export declare class SystemMetricsService {
    private cpuUsageHistory;
    private networkActivity;
    private lastNetworkCheck;
    private appStartTime;
    private metricsInterval;
    constructor();
    private initializeMetrics;
    private updateCpuUsage;
    private updateNetworkActivity;
    getMetrics(): Promise<SystemMetrics>;
    getCpuInfo(): Promise<{
        model: string;
        cores: number;
        speed: number;
        usage: number;
        loadAverage: number[];
    }>;
    getMemoryInfo(): Promise<{
        total: number;
        used: number;
        free: number;
        usagePercent: number;
        processMemory: NodeJS.MemoryUsage;
    }>;
    getNetworkInfo(): Promise<{
        interfaces: NodeJS.Dict<os.NetworkInterfaceInfo[]>;
        isOnline: boolean;
        activity: boolean;
    }>;
    getPlatformInfo(): Promise<{
        type: string;
        platform: string;
        arch: string;
        release: string;
        version: string;
        hostname: string;
        uptime: number;
        electronVersion: string;
        nodeVersion: string;
    }>;
    startMonitoring(callback: (metrics: SystemMetrics) => void, intervalMs?: number): NodeJS.Timeout;
    checkResourceAlerts(): {
        cpu: boolean;
        memory: boolean;
        warnings: string[];
    };
    destroy(): void;
}
