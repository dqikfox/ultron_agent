from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import jwt
from functools import wraps

app = Flask("UltronAgentAPI")
socketio = SocketIO(app, cors_allowed_origins="*")
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
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated

@socketio.on('connect')
def handle_connect():
    emit('status', {'status': 'connected', 'agent_status': 'ready' if AGENT_INSTANCE else 'not initialized'})

@socketio.on('command')
def handle_command(data):
    try:
        if not AGENT_INSTANCE:
            emit('response', {'error': 'Agent not initialized'})
            return
        
        command = data.get('command')
        if not command:
            emit('response', {'error': 'No command provided'})
            return

        response = AGENT_INSTANCE.process_command(command)
        emit('response', {'result': response})
    except Exception as e:
        emit('response', {'error': str(e)})

@socketio.on('start_voice')
def handle_start_voice():
    try:
        if not AGENT_INSTANCE:
            emit('response', {'error': 'Agent not initialized'})
            return
        
        AGENT_INSTANCE.voice.start_listening()
        emit('status', {'status': 'listening'})
    except Exception as e:
        emit('response', {'error': f'Failed to start voice input: {str(e)}'})

@socketio.on('stop_voice')
def handle_stop_voice():
    try:
        if not AGENT_INSTANCE:
            emit('response', {'error': 'Agent not initialized'})
            return
        
        text = AGENT_INSTANCE.voice.stop_listening()
        if text:
            emit('voice_text', {'text': text})
    except Exception as e:
        emit('response', {'error': f'Failed to stop voice input: {str(e)}'})

@socketio.on('disconnect')
def handle_disconnect():
    emit('status', {'status': 'disconnected'})

# Task Management WebSocket Events
@socketio.on('list_tasks')
def handle_list_tasks():
    """List all scheduled tasks with their details."""
    try:
        if not AGENT_INSTANCE:
            emit('tasks_list', {'error': 'Agent not initialized'})
            return
        
        tasks = AGENT_INSTANCE.task_scheduler.list_tasks()
        emit('tasks_list', {'tasks': tasks})
    except Exception as e:
        emit('tasks_list', {'error': str(e)})

@socketio.on('create_task')
def handle_create_task(data):
    """Create a new scheduled task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_created', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        command = data.get('command')
        schedule = data.get('schedule')
        description = data.get('description', '')
        
        if not all([task_id, command, schedule]):
            emit('task_created', {'error': 'Missing required fields'})
            return
        
        success = AGENT_INSTANCE.task_scheduler.schedule_task(
            task_id, command, schedule, description
        )
        
        if success:
            emit('task_created', {'success': True, 'task_id': task_id})
        else:
            emit('task_created', {'error': 'Failed to create task'})
    except Exception as e:
        emit('task_created', {'error': str(e)})

@socketio.on('update_task')
def handle_update_task(data):
    """Update an existing task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_updated', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        updates = data.get('updates')
        
        if not all([task_id, updates]):
            emit('task_updated', {'error': 'Missing required fields'})
            return
        
        success = AGENT_INSTANCE.task_scheduler.update_task(task_id, updates)
        
        if success:
            emit('task_updated', {'success': True, 'task_id': task_id})
        else:
            emit('task_updated', {'error': 'Failed to update task'})
    except Exception as e:
        emit('task_updated', {'error': str(e)})

@socketio.on('delete_task')
def handle_delete_task(data):
    """Delete a scheduled task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_deleted', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        
        if not task_id:
            emit('task_deleted', {'error': 'Missing task_id'})
            return
        
        success = AGENT_INSTANCE.task_scheduler.delete_task(task_id)
        
        if success:
            emit('task_deleted', {'success': True, 'task_id': task_id})
        else:
            emit('task_deleted', {'error': 'Failed to delete task'})
    except Exception as e:
        emit('task_deleted', {'error': str(e)})

@socketio.on('get_task_details')
def handle_get_task_details(data):
    """Get detailed information about a specific task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_details', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        
        if not task_id:
            emit('task_details', {'error': 'Missing task_id'})
            return
        
        task = AGENT_INSTANCE.task_scheduler.get_task(task_id)
        
        if task:
            emit('task_details', {'task': task})
        else:
            emit('task_details', {'error': 'Task not found'})
    except Exception as e:
        emit('task_details', {'error': str(e)})

@socketio.on('get_task_analytics')
def handle_get_task_analytics(data):
    """Get detailed analytics for a specific task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_analytics', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        
        if not task_id:
            emit('task_analytics', {'error': 'Missing task_id'})
            return
        
        analytics = AGENT_INSTANCE.task_scheduler.get_task_analytics(task_id)
        
        if analytics:
            emit('task_analytics', {'analytics': analytics})
        else:
            emit('task_analytics', {'error': 'Task not found'})
    except Exception as e:
        emit('task_analytics', {'error': str(e)})

@socketio.on('get_system_analytics')
def handle_get_system_analytics():
    """Get system-wide task analytics."""
    try:
        if not AGENT_INSTANCE:
            emit('system_analytics', {'error': 'Agent not initialized'})
            return
        
        analytics = AGENT_INSTANCE.task_scheduler.get_system_analytics()
        emit('system_analytics', {'analytics': analytics})
    except Exception as e:
        emit('system_analytics', {'error': str(e)})

@socketio.on('enable_task')
def handle_enable_task(data):
    """Enable a task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_enabled', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        
        if not task_id:
            emit('task_enabled', {'error': 'Missing task_id'})
            return
        
        success = AGENT_INSTANCE.task_scheduler.enable_task(task_id)
        
        if success:
            emit('task_enabled', {'success': True, 'task_id': task_id})
        else:
            emit('task_enabled', {'error': 'Failed to enable task'})
    except Exception as e:
        emit('task_enabled', {'error': str(e)})

@socketio.on('disable_task')
def handle_disable_task(data):
    """Disable a task."""
    try:
        if not AGENT_INSTANCE:
            emit('task_disabled', {'error': 'Agent not initialized'})
            return
        
        task_id = data.get('task_id')
        
        if not task_id:
            emit('task_disabled', {'error': 'Missing task_id'})
            return
        
        success = AGENT_INSTANCE.task_scheduler.disable_task(task_id)
        
        if success:
            emit('task_disabled', {'success': True, 'task_id': task_id})
        else:
            emit('task_disabled', {'error': 'Failed to disable task'})
    except Exception as e:
        emit('task_disabled', {'error': str(e)})

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