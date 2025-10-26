from flask import Flask, jsonify


app = Flask("UltronAgentAPI")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "agent_initialized": False,
        "version": "3.0.0",
        "message": "Basic API server running without agent backend"
    }), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "basic_api_online"}), 200


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "API server is working!"}), 200


if __name__ == "__main__":
    print("🚀 Starting basic Flask API server on port 5002...")
    app.run(host="0.0.0.0", port=5002, debug=False)
