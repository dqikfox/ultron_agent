import { useState, useEffect } from 'react'

interface SystemStats {
  cpu: number
  memory: number
  disk: number
  network: {
    download: number
    upload: number
  }
  temperature: number
  processes: number
}

export function useSystemMonitoring() {
  const [stats, setStats] = useState<SystemStats>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: { download: 0, upload: 0 },
    temperature: 0,
    processes: 0
  })
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Simulate system monitoring data
    const interval = setInterval(() => {
      setStats({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: Math.random() * 100,
        network: {
          download: Math.random() * 1000,
          upload: Math.random() * 500
        },
        temperature: 35 + Math.random() * 30,
        processes: Math.floor(150 + Math.random() * 100)
      })
      setIsConnected(true)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return { stats, isConnected }
}