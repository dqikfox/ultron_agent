from flask import Flask, request, jsonify
import jwt
from functools import wraps

app = Flask("UltronAgentAPI")
AGENT_INSTANCE = None


def set_agent_instance(agent):
    global AGENT_INSTANCE
    AGENT_INSTANCE = agent


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip auth if no agent or no JWT secret configured
        if not AGENT_INSTANCE or not hasattr(AGENT_INSTANCE, 'config'):
            return f(*args, **kwargs)

        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token required"}), 401

        try:
            jwt_secret = getattr(AGENT_INSTANCE.config, 'data', {}).get(
                'jwt_secret', 'default_secret')
            jwt.decode(
                token.replace("Bearer ", ""),
                jwt_secret,
                algorithms=["HS256"],
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)

    return decorated


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    status = {
        "status": "healthy",
        "agent_initialized": AGENT_INSTANCE is not None,
        "version": "3.0.0",
    }
    if AGENT_INSTANCE:
        status["agent_status"] = AGENT_INSTANCE.status
    return jsonify(status), 200


@app.route("/status", methods=["GET"])
def status():
    status_text = "online" if AGENT_INSTANCE else "uninitialized"
    return jsonify({"status": status_text}), 200


@app.route("/command", methods=["POST"])
@require_auth
def command():
    if not AGENT_INSTANCE:
        return jsonify({"error": "Agent not initialized"}), 500
    data = request.get_json(silent=True)
    if not data or "command" not in data:
        return jsonify({"error": "No command provided"}), 400
    result = AGENT_INSTANCE.handle_text(data["command"])
    return jsonify({"result": result}), 200


# Tools Integration API Endpoints
@app.route("/api/tools/status", methods=["GET"])
def get_tools_status():
    """Get overall tools status and statistics."""
    try:
        if not AGENT_INSTANCE:
            return jsonify({"error": "Agent not initialized"}), 500

        tools = AGENT_INSTANCE.list_tools()
        active_tools = len([t for t in tools if AGENT_INSTANCE.get_tool(t)])

        # Get detailed tool information
        tools_data = []
        total_usage = 0

        for tool_name in tools:
            tool_instance = AGENT_INSTANCE.get_tool(tool_name)
            if tool_instance:
                # Get tool schema for metadata
                schema = tool_instance.schema() if hasattr(
                    tool_instance, "schema") else {}

                tool_info = {
                    "name": tool_name,
                    "description": schema.get("description", "No description"),
                    "status": "active",
                    "usage_count": getattr(tool_instance, "usage_count", 0),
                    "last_used": getattr(tool_instance, "last_used", "Never"),
                    "class_name": tool_instance.__class__.__name__,
                    "module": tool_instance.__class__.__module__,
                    "parameters": schema.get("parameters", {}),
                    "is_async": hasattr(tool_instance, "execute_async"),
                    "requires_config": hasattr(tool_instance, "config")
                }
                tools_data.append(tool_info)
                total_usage += tool_info["usage_count"]

        return jsonify({
            "total": len(tools),
            "active": active_tools,
            "usage": total_usage,
            "tools": tools_data
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get tools status: {str(e)}"}), 500


@app.route("/api/tools/<tool_name>", methods=["GET"])
def get_tool_details(tool_name):
    """Get detailed information about a specific tool."""
    try:
        if not AGENT_INSTANCE:
            return jsonify({"error": "Agent not initialized"}), 500

        tool_instance = AGENT_INSTANCE.get_tool(tool_name)
        if not tool_instance:
            return jsonify({"error": f"Tool '{tool_name}' not found"}), 404

        # Get tool schema for metadata
        schema = tool_instance.schema() if hasattr(
            tool_instance, "schema") else {}

        tool_info = {
            "name": tool_name,
            "description": schema.get("description", "No description"),
            "status": "active",
            "usage_count": getattr(tool_instance, "usage_count", 0),
            "last_used": getattr(tool_instance, "last_used", "Never"),
            "success_rate": getattr(tool_instance, "success_rate", 85),
            "class_name": tool_instance.__class__.__name__,
            "module": tool_instance.__class__.__module__,
            "version": getattr(tool_instance, "version", "1.0"),
            "parameters": schema.get("parameters", {}),
            "is_async": hasattr(tool_instance, "execute_async"),
            "requires_config": hasattr(tool_instance, "config")
        }

        return jsonify(tool_info), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get tool details: {str(e)}"}), 500


@app.route("/api/tools/reload", methods=["POST"])
def reload_tools():
    """Reload all tools from the tools directory."""
    try:
        if not AGENT_INSTANCE:
            return jsonify({"error": "Agent not initialized"}), 500

        # Re-run the tool loading process
        import asyncio
        asyncio.run(AGENT_INSTANCE._load_tools())

        reloaded_count = len(AGENT_INSTANCE.list_tools())

        return jsonify({
            "success": True,
            "reloaded": reloaded_count,
            "message": f"Successfully reloaded {reloaded_count} tools"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to reload tools: {str(e)}"}), 500


@app.route("/api/tools/test", methods=["POST"])
def test_all_tools():
    """Test all loaded tools."""
    try:
        if not AGENT_INSTANCE:
            return jsonify({"error": "Agent not initialized"}), 500

        results = []
        tools = AGENT_INSTANCE.list_tools()

        for tool_name in tools:
            tool_instance = AGENT_INSTANCE.get_tool(tool_name)
            if tool_instance:
                try:
                    # Simple test - try to call match method
                    tool_instance.match("test")
                    results.append({
                        "tool": tool_name,
                        "passed": True,
                        "message": "Match method works"
                    })
                except Exception as e:
                    results.append({
                        "tool": tool_name,
                        "passed": False,
                        "error": str(e)
                    })
            else:
                results.append({
                    "tool": tool_name,
                    "passed": False,
                    "error": "Tool instance not found"
                })

        return jsonify({
            "success": True,
            "results": results,
            "total": len(results),
            "passed": len([r for r in results if r["passed"]])
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to test tools: {str(e)}"}), 500


if __name__ == "__main__":
    # Initialize a basic agent instance for testing
    try:
        print("🔄 Attempting to initialize agent...")
        from agent_core import UltronAgent
        agent = UltronAgent()
        set_agent_instance(agent)
        print("✅ Agent instance initialized successfully")
    except Exception as e:
        print(f"⚠️  Agent initialization failed: {e}")
        print("Starting API server without agent backend")
        print("Note: Some endpoints may not work without the agent")

    try:
        print("🚀 Starting Flask API server on port 5001...")
        app.run(host="0.0.0.0", port=5001, debug=False)
    except Exception as e:
        print(f"❌ Flask server failed: {e}")
        print("Trying alternative port 5002...")
        try:
            app.run(host="0.0.0.0", port=5002, debug=False)
        except Exception as e2:
            print(f"❌ Alternative port also failed: {e2}")
