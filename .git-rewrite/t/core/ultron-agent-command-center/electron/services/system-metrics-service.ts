import { app, powerMonitor } from 'electron'
import * as os from 'os'
import * as process from 'process'

export interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
    model: string
    speed: number
  }
  memory: {
    usage: number
    total: number
    used: number
    available: number
  }
  network: {
    isOnline: boolean
    activity: boolean
  }
  uptime: {
    system: number
    app: number
  }
  platform: {
    os: string
    version: string
    arch: string
  }
}

export class SystemMetricsService {
  private cpuUsageHistory: number[] = []
  private networkActivity = false
  private lastNetworkCheck = Date.now()
  private appStartTime = Date.now()
  private metricsInterval: NodeJS.Timeout | null = null

  constructor() {
    this.initializeMetrics()
  }

  private initializeMetrics(): void {
    // Start collecting CPU usage history
    this.metricsInterval = setInterval(() => {
      this.updateCpuUsage()
      this.updateNetworkActivity()
    }, 1000)

    // Monitor network status changes
    if (powerMonitor) {
      powerMonitor.on('resume', () => {
        this.networkActivity = true
      })
    }
  }

  private updateCpuUsage(): void {
    // Calculate CPU usage based on process CPU time
    const usage = process.cpuUsage()
    const totalUsage = (usage.user + usage.system) / 1000000 // Convert to seconds
    
    // Simple CPU usage calculation (this is an approximation)
    const cpuPercent = Math.min(100, (totalUsage % 100))
    
    this.cpuUsageHistory.push(cpuPercent)
    if (this.cpuUsageHistory.length > 60) {
      this.cpuUsageHistory.shift() // Keep last 60 seconds
    }
  }

  private updateNetworkActivity(): void {
    // Simple network activity simulation based on time
    const now = Date.now()
    const timeSinceLastCheck = now - this.lastNetworkCheck
    
    // Simulate network activity detection
    this.networkActivity = timeSinceLastCheck < 5000 && Math.random() > 0.7
    this.lastNetworkCheck = now
  }

  async getMetrics(): Promise<SystemMetrics> {
    const cpus = os.cpus()
    const totalMem = os.totalmem()
    const freeMem = os.freemem()
    const usedMem = totalMem - freeMem
    
    // Calculate average CPU usage
    const avgCpuUsage = this.cpuUsageHistory.length > 0
      ? this.cpuUsageHistory.reduce((a, b) => a + b, 0) / this.cpuUsageHistory.length
      : 0

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
    }
  }

  async getCpuInfo(): Promise<{
    model: string
    cores: number
    speed: number
    usage: number
    loadAverage: number[]
  }> {
    const cpus = os.cpus()
    const loadAvg = os.loadavg()
    
    return {
      model: cpus[0]?.model || 'Unknown',
      cores: cpus.length,
      speed: cpus[0]?.speed || 0,
      usage: this.cpuUsageHistory.length > 0
        ? this.cpuUsageHistory[this.cpuUsageHistory.length - 1]
        : 0,
      loadAverage: loadAvg
    }
  }

  async getMemoryInfo(): Promise<{
    total: number
    used: number
    free: number
    usagePercent: number
    processMemory: NodeJS.MemoryUsage
  }> {
    const totalMem = os.totalmem()
    const freeMem = os.freemem()
    const usedMem = totalMem - freeMem
    
    return {
      total: totalMem,
      used: usedMem,
      free: freeMem,
      usagePercent: Math.round((usedMem / totalMem) * 100 * 10) / 10,
      processMemory: process.memoryUsage()
    }
  }

  async getNetworkInfo(): Promise<{
    interfaces: NodeJS.Dict<os.NetworkInterfaceInfo[]>
    isOnline: boolean
    activity: boolean
  }> {
    return {
      interfaces: os.networkInterfaces(),
      isOnline: true, // Assume online in Electron main process
      activity: this.networkActivity
    }
  }

  async getPlatformInfo(): Promise<{
    type: string
    platform: string
    arch: string
    release: string
    version: string
    hostname: string
    uptime: number
    electronVersion: string
    nodeVersion: string
  }> {
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
    }
  }

  // Real-time monitoring
  startMonitoring(callback: (metrics: SystemMetrics) => void, intervalMs = 1000): NodeJS.Timeout {
    return setInterval(async () => {
      const metrics = await this.getMetrics()
      callback(metrics)
    }, intervalMs)
  }

  // Resource usage alerts
  checkResourceAlerts(): {
    cpu: boolean
    memory: boolean
    warnings: string[]
  } {
    const warnings: string[] = []
    let cpuAlert = false
    let memoryAlert = false

    // Check CPU usage
    if (this.cpuUsageHistory.length > 0) {
      const recentUsage = this.cpuUsageHistory.slice(-10)
      const avgRecentUsage = recentUsage.reduce((a, b) => a + b, 0) / recentUsage.length
      
      if (avgRecentUsage > 80) {
        cpuAlert = true
        warnings.push(`High CPU usage detected: ${avgRecentUsage.toFixed(1)}%`)
      }
    }

    // Check memory usage
    const totalMem = os.totalmem()
    const freeMem = os.freemem()
    const memoryUsage = ((totalMem - freeMem) / totalMem) * 100
    
    if (memoryUsage > 85) {
      memoryAlert = true
      warnings.push(`High memory usage detected: ${memoryUsage.toFixed(1)}%`)
    }

    return {
      cpu: cpuAlert,
      memory: memoryAlert,
      warnings
    }
  }

  destroy(): void {
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval)
      this.metricsInterval = null
    }
  }
}
