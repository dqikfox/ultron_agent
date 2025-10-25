"""
ULTRON Diagnostics Dashboard Server
Web-based diagnostics viewer inspired by Unity Cloud dashboard
"""

from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
from pathlib import Path

from diagnostics.diagnostics_core import get_diagnostics
from utils.ultron_logger import log_info, log_error


app = Flask(__name__)
CORS(app)

# Get diagnostics instance
diagnostics = get_diagnostics()


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRON Diagnostics Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }

        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #00d9ff;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            color: #00d9ff;
            text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        }

        .header .subtitle {
            color: #aaa;
            margin-top: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 217, 255, 0.3);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }

        .stat-card.critical {
            border-color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }

        .stat-card.warning {
            border-color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
        }

        .stat-card.healthy {
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.1);
        }

        .stat-card h3 {
            color: #00d9ff;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }

        .stat-label {
            color: #aaa;
            font-size: 0.85em;
        }

        .section {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 217, 255, 0.3);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }

        .section h2 {
            color: #00d9ff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .crash-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .crash-item {
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid #ff4444;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }

        .crash-item.resolved {
            border-left-color: #00ff88;
            opacity: 0.6;
        }

        .crash-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .crash-component {
            font-weight: bold;
            color: #00d9ff;
        }

        .crash-time {
            color: #aaa;
            font-size: 0.85em;
        }

        .crash-message {
            color: #ffaa00;
            margin: 5px 0;
        }

        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .service-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #aaa;
        }

        .service-item.healthy {
            border-left-color: #00ff88;
        }

        .service-item.unhealthy {
            border-left-color: #ff4444;
        }

        .service-name {
            font-weight: bold;
            margin-bottom: 5px;
        }

        .service-port {
            color: #aaa;
            font-size: 0.85em;
        }

        .service-status {
            margin-top: 10px;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
            font-size: 0.85em;
        }

        .service-status.healthy {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }

        .service-status.unhealthy {
            background: rgba(255, 68, 68, 0.2);
            color: #ff4444;
        }

        .refresh-btn {
            background: #00d9ff;
            color: #000;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            margin-top: 10px;
            transition: all 0.3s;
        }

        .refresh-btn:hover {
            background: #00ffcc;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 217, 255, 0.4);
        }

        .auto-refresh {
            text-align: center;
            color: #aaa;
            margin-top: 20px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .loading {
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ ULTRON DIAGNOSTICS</h1>
        <p class="subtitle">Real-time System Monitoring & Crash Reporting</p>
    </div>

    <div class="stats-grid" id="statsGrid"></div>

    <div class="section">
        <h2>🔥 Recent Crashes</h2>
        <div class="crash-list" id="crashList"></div>
    </div>

    <div class="section">
        <h2>🖥️ Service Status</h2>
        <div class="service-grid" id="serviceGrid"></div>
    </div>

    <div style="text-align: center;">
        <button class="refresh-btn" onclick="loadDiagnostics()">🔄 Refresh Data</button>
    </div>

    <div class="auto-refresh">
        <p>Auto-refresh enabled (every 5 seconds)</p>
    </div>

    <script>
        async function loadDiagnostics() {
            try {
                const response = await fetch('/api/diagnostics/summary');
                const data = await response.json();

                updateStats(data);
                updateCrashes(data);
                updateServices(data);
            } catch (error) {
                console.error('Failed to load diagnostics:', error);
            }
        }

        function updateStats(data) {
            const stats = [
                {
                    label: 'Session Uptime',
                    value: data.session.uptime_formatted,
                    class: 'healthy'
                },
                {
                    label: 'Total Crashes',
                    value: data.crashes.total,
                    class: data.crashes.total > 0 ? 'warning' : 'healthy'
                },
                {
                    label: 'Crashes (Last Hour)',
                    value: data.crashes.last_hour,
                    class: data.crashes.last_hour > 0 ? 'critical' : 'healthy'
                },
                {
                    label: 'Unresolved Issues',
                    value: data.crashes.unresolved,
                    class: data.crashes.unresolved > 0 ? 'warning' : 'healthy'
                },
                {
                    label: 'CPU Usage',
                    value: data.performance.latest_health ?
                           data.performance.latest_health.cpu_percent.toFixed(1) + '%' :
                           'N/A',
                    class: 'healthy'
                },
                {
                    label: 'Memory Usage',
                    value: data.performance.latest_health ?
                           data.performance.latest_health.memory_percent.toFixed(1) + '%' :
                           'N/A',
                    class: 'healthy'
                }
            ];

            const grid = document.getElementById('statsGrid');
            grid.innerHTML = stats.map(stat => `
                <div class="stat-card ${stat.class}">
                    <h3>${stat.label}</h3>
                    <div class="stat-value">${stat.value}</div>
                </div>
            `).join('');
        }

        function updateCrashes(data) {
            // This would be populated from actual crash data
            const crashList = document.getElementById('crashList');

            if (data.crashes.total === 0) {
                crashList.innerHTML = '<p style="color: #aaa; text-align: center; padding: 20px;">✅ No crashes detected</p>';
            } else {
                crashList.innerHTML = '<p style="color: #aaa; text-align: center; padding: 20px;">📊 Crash details available via API</p>';
            }
        }

        function updateServices(data) {
            const services = data.services || {};
            const grid = document.getElementById('serviceGrid');

            const serviceItems = Object.entries(services).map(([name, info]) => {
                const isHealthy = info.status === 'healthy';
                return `
                    <div class="service-item ${isHealthy ? 'healthy' : 'unhealthy'}">
                        <div class="service-name">${name}</div>
                        <div class="service-port">Port: ${info.port}</div>
                        <span class="service-status ${isHealthy ? 'healthy' : 'unhealthy'}">
                            ${isHealthy ? '✅ Online' : '❌ Offline'}
                        </span>
                    </div>
                `;
            }).join('');

            grid.innerHTML = serviceItems || '<p style="color: #aaa;">No service data available</p>';
        }

        // Auto-refresh every 5 seconds
        setInterval(loadDiagnostics, 5000);

        // Initial load
        loadDiagnostics();
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Serve diagnostics dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/diagnostics/summary')
def get_summary():
    """Get diagnostics summary"""
    try:
        summary = diagnostics.get_diagnostics_summary()
        return jsonify(summary)
    except Exception as e:
        log_error("diagnostics_dashboard", f"Failed to get summary: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/diagnostics/crashes')
def get_crashes():
    """Get all crash reports"""
    try:
        crashes = [
            {
                "crash_id": c.crash_id,
                "timestamp": c.timestamp,
                "component": c.component,
                "exception_type": c.exception_type,
                "exception_message": c.exception_message,
                "severity": c.severity,
                "resolved": c.resolved
            }
            for c in diagnostics.crash_reports
        ]
        return jsonify({"crashes": crashes})
    except Exception as e:
        log_error("diagnostics_dashboard", f"Failed to get crashes: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/diagnostics/crash/<crash_id>')
def get_crash_detail(crash_id):
    """Get detailed crash report"""
    try:
        crash = next(
            (c for c in diagnostics.crash_reports if c.crash_id == crash_id),
            None
        )
        if crash:
            return jsonify({
                "crash_id": crash.crash_id,
                "timestamp": crash.timestamp,
                "component": crash.component,
                "exception_type": crash.exception_type,
                "exception_message": crash.exception_message,
                "stack_trace": crash.stack_trace,
                "system_info": crash.system_info,
                "severity": crash.severity,
                "resolved": crash.resolved,
                "resolution_notes": crash.resolution_notes
            })
        return jsonify({"error": "Crash not found"}), 404
    except Exception as e:
        log_error("diagnostics_dashboard", f"Failed to get crash detail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/diagnostics/health')
def get_health():
    """Get current system health"""
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        health = loop.run_until_complete(diagnostics.capture_system_health())
        loop.close()

        return jsonify({
            "timestamp": health.timestamp,
            "cpu_percent": health.cpu_percent,
            "memory_percent": health.memory_percent,
            "memory_used_mb": health.memory_used_mb,
            "memory_available_mb": health.memory_available_mb,
            "disk_usage_percent": health.disk_usage_percent,
            "active_threads": health.active_threads,
            "services": {
                "ollama": health.ollama_status,
                "api_server": health.api_server_status,
                "gui_server": health.gui_server_status
            },
            "services_healthy": health.services_healthy
        })
    except Exception as e:
        log_error("diagnostics_dashboard", f"Failed to get health: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/diagnostics/export')
def export_diagnostics():
    """Export all diagnostics data"""
    try:
        export_path = diagnostics.export_diagnostics()
        return jsonify({
            "success": True,
            "export_path": export_path,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        log_error("diagnostics_dashboard", f"Failed to export: {e}")
        return jsonify({"error": str(e)}), 500


def run_dashboard(host='127.0.0.1', port=5001):
    """Run diagnostics dashboard server"""
    log_info("diagnostics_dashboard", f"Starting dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    run_dashboard()
