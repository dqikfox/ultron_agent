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
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            jwt.decode(token.replace("Bearer ", ""), AGENT_INSTANCE.config.data["jwt_secret"], algorithms=["HS256"])
        except Exception as e:
            return jsonify({"error": f"Invalid token: {e}"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "online" if AGENT_INSTANCE else "uninitialized"}), 200

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

@app.route("/settings", methods=["PUT"])
@require_auth
def update_settings():
    if not AGENT_INSTANCE:
        return jsonify({"error": "Agent not initialized"}), 500
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No settings provided"}), 400
    for key, value in data.items():
        AGENT_INSTANCE.config.data[key] = value
    return jsonify({"status": "Settings updated"}), 200