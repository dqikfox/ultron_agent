#!/usr/bin/env python3
"""API endpoints for autonomous operations"""

from flask import Flask, request, jsonify
import subprocess
import json
import asyncio
from autonomous_brain import get_autonomous_brain
from proactive_manager import get_proactive_manager
from utils.ultron_logger import log_info, log_ai_decision

app = Flask(__name__)

@app.route('/api/autonomous/start', methods=['POST'])
def start_autonomous():
    """Start autonomous mode"""
    try:
        log_ai_decision("autonomous_api", "Starting autonomous mode via API")
        
        # Start autonomous startup script in background
        subprocess.Popen(["python", "autonomous_startup.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        return jsonify({
            "success": True,
            "message": "Autonomous mode started"
        })
    except Exception as e:
        log_info("autonomous_api", f"Failed to start autonomous mode: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/autonomous/stop', methods=['POST'])
def stop_autonomous():
    """Stop autonomous mode"""
    try:
        log_info("autonomous_api", "Stopping autonomous mode via API")
        
        # Kill autonomous processes
        subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq autonomous*"], 
                      shell=True, capture_output=True)
        
        return jsonify({
            "success": True,
            "message": "Autonomous mode stopped"
        })
    except Exception as e:
        log_info("autonomous_api", f"Failed to stop autonomous mode: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/integration', methods=['POST'])
def run_integration_test():
    """Run integration test"""
    try:
        log_info("autonomous_api", "Running integration test via API")
        
        result = subprocess.run(["python", "test_integration.py"], 
                              capture_output=True, text=True, timeout=60)
        
        # Parse output for test results
        output = result.stdout
        if "tests passed" in output:
            # Extract numbers from "Overall: X/Y tests passed"
            import re
            match = re.search(r'Overall: (\d+)/(\d+) tests passed', output)
            if match:
                passed = int(match.group(1))
                total = int(match.group(2))
            else:
                passed, total = 0, 0
        else:
            passed, total = 0, 0
        
        return jsonify({
            "success": True,
            "passed": passed,
            "total": total,
            "output": output
        })
    except Exception as e:
        log_info("autonomous_api", f"Integration test failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/proactive/start', methods=['POST'])
def start_proactive():
    """Start proactive monitoring"""
    try:
        manager = get_proactive_manager()
        
        # Start monitoring in background thread
        import threading
        def run_monitoring():
            asyncio.run(manager.start_proactive_monitoring())
        
        thread = threading.Thread(target=run_monitoring, daemon=True)
        thread.start()
        
        log_info("autonomous_api", "Proactive monitoring started")
        
        return jsonify({
            "success": True,
            "message": "Proactive monitoring started"
        })
    except Exception as e:
        log_info("autonomous_api", f"Failed to start proactive monitoring: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/proactive/stop', methods=['POST'])
def stop_proactive():
    """Stop proactive monitoring"""
    try:
        manager = get_proactive_manager()
        manager.monitoring_enabled = False
        
        log_info("autonomous_api", "Proactive monitoring stopped")
        
        return jsonify({
            "success": True,
            "message": "Proactive monitoring stopped"
        })
    except Exception as e:
        log_info("autonomous_api", f"Failed to stop proactive monitoring: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/autonomous/evolve', methods=['POST'])
def evolve_capabilities():
    """Evolve autonomous capabilities"""
    try:
        brain = get_autonomous_brain()
        
        # Run evolution in async context
        async def run_evolution():
            return await brain.evolve_capabilities()
        
        result = asyncio.run(run_evolution())
        
        log_ai_decision("autonomous_api", f"Evolution completed: {result}")
        
        return jsonify({
            "success": True,
            **result
        })
    except Exception as e:
        log_info("autonomous_api", f"Evolution failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/autonomous/learning-data', methods=['GET'])
def get_learning_data():
    """Get learning data"""
    try:
        brain = get_autonomous_brain()
        
        return jsonify({
            "success": True,
            "total_records": len(brain.learning_data),
            "recent_decisions": len([r for r in brain.learning_data[-10:]]),
            "adaptation_rules": len(brain.adaptation_rules),
            "recent_data": brain.learning_data[-5:] if brain.learning_data else []
        })
    except Exception as e:
        log_info("autonomous_api", f"Failed to get learning data: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/autonomous/status', methods=['GET'])
def get_autonomous_status():
    """Get autonomous system status"""
    try:
        brain = get_autonomous_brain()
        manager = get_proactive_manager()
        
        return jsonify({
            "success": True,
            "brain_status": "active" if brain else "inactive",
            "learning_records": len(brain.learning_data) if brain else 0,
            "adaptation_rules": len(brain.adaptation_rules) if brain else 0,
            "proactive_status": manager.monitoring_enabled if manager else False,
            "active_tasks": len(manager.active_tasks) if manager else 0,
            "completed_tasks": len(manager.completed_tasks) if manager else 0
        })
    except Exception as e:
        log_info("autonomous_api", f"Failed to get status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    log_info("autonomous_api", "Starting autonomous API server on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=False)