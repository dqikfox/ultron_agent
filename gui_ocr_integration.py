#!/usr/bin/env python3
"""
GUI OCR Integration Server
Connects enhanced screenshot analyzer to ULTRON GUI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.enhanced_ocr_tool import EnhancedOCRTool
from tools.windows_system_tool import WindowsSystemTool
from tools.browser_mcp_tool import BrowserMCPTool
from tools.continue_docs_tool import ContinueDocsTool

app = Flask(__name__)
CORS(app)

# Initialize enhanced tools
ocr_tool = EnhancedOCRTool()
system_tool = WindowsSystemTool()
browser_tool = BrowserMCPTool()
docs_tool = ContinueDocsTool()

@app.route('/api/vision/capture', methods=['POST'])
def capture_screenshot():
    """Enhanced screenshot with OCR analysis"""
    try:
        result = ocr_tool.execute("ocr screenshot")
        import json
        parsed_result = json.loads(result)
        
        return jsonify({
            "success": True,
            "message": "Screenshot captured with enhanced OCR",
            "image_path": parsed_result.get("image_path"),
            "text_content": parsed_result.get("raw_text"),
            "confidence": parsed_result.get("confidence"),
            "analysis": parsed_result.get("analysis"),
            "word_count": parsed_result.get("word_count"),
            "timestamp": int(time.time())
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/system/command', methods=['POST'])
def execute_system_command():
    """Execute natural language system commands"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({
                "success": False,
                "error": "No command provided"
            }), 400
        
        result = system_tool.execute(command)
        return jsonify({
            "success": True,
            "message": "Command executed",
            "result": result,
            "command": command
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/browser/action', methods=['POST'])
def browser_action():
    """Execute browser automation commands"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        result = browser_tool.execute(command)
        return jsonify({
            "success": True,
            "message": "Browser action completed",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/docs/query', methods=['POST'])
def docs_query():
    """Query documentation and codebase information"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        result = docs_tool.execute(query)
        return jsonify({
            "success": True,
            "message": "Documentation query completed",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def system_status():
    """Get enhanced system status"""
    return jsonify({
        "success": True,
        "status": "online",
        "tools": {
            "enhanced_ocr": "ready",
            "windows_system": "ready", 
            "browser_mcp": "ready",
            "continue_docs": "ready",
            "natural_language": "enabled"
        },
        "capabilities": [
            "Screenshot OCR with preprocessing",
            "Natural language system control",
            "Browser automation via MCP",
            "Application launching and management",
            "Contextual search and history",
            "Continue documentation awareness"
        ]
    })

if __name__ == '__main__':
    print("Starting Enhanced ULTRON Integration Server...")
    print("Enhanced API available at: http://localhost:5001")
    print("Features: OCR, System Control, Browser MCP, Natural Language")
    app.run(host='0.0.0.0', port=5001, debug=False)