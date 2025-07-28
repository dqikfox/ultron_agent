CREATE TABLE system_stats (
    id SERIAL PRIMARY KEY,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    memory_total_gb DECIMAL(10,2),
    disk_usage DECIMAL(5,2),
    disk_total_gb DECIMAL(10,2),
    ollama_status VARCHAR(20) DEFAULT 'unknown' CHECK (ollama_status IN ('running',
    'stopped',
    'error',
    'unknown')),
    active_model VARCHAR(100),
    gpu_usage DECIMAL(5,2) DEFAULT 0,
    temperature DECIMAL(5,2) DEFAULT 0,
    uptime_seconds INTEGER DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);