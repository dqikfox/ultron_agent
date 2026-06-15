from flask import Flask, request, jsonify
import jwt
from functools import wraps
from typing import Dict, Any, Optional, Callable, Tuple
from datetime import datetime
from utils.error_handlers import (
    ConfigError, ValidationError, AsyncError, ResourceError,
    NetworkError, ErrorContext
)
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.rate_limiter import rate_limit

from flask_cors import CORS
app: Flask = Flask("UltronAgentAPI")
CORS(app)
# ...existing code...

# --- API STATUS ENDPOINT FOR WEB GUI ---
@app.route("/api/status", methods=["GET"])
def api_status():
    """Health/status endpoint for Web GUI availability check."""
    return {"status": "ok", "message": "ULTRON API backend online"}, 200
AGENT_INSTANCE: Optional[Any] = None


def set_agent_instance(agent: Any) -> None:
    global AGENT_INSTANCE
    AGENT_INSTANCE = agent


def require_auth(f: Callable) -> Callable:
    """Decorator to enforce JWT authentication on endpoints

    Validates Bearer token from Authorization header using configured JWT secret.
    Gracefully skips auth if no agent or secret configured.

    Args:
        f: The Flask route handler function to decorate

    Returns:
        Decorated function with auth validation
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], int]:
        try:
            with ErrorContext("jwt_authentication"):
                # Skip auth if no agent or no JWT secret configured
                if not AGENT_INSTANCE or not hasattr(AGENT_INSTANCE, 'config'):
                    log_info("api_server", "Auth skipped - no agent instance")
                    return f(*args, **kwargs)

                # Get token from headers
                token: Optional[str] = request.headers.get("Authorization")
                if not token:
                    log_error("api_server", "Authentication failed - no token provided")
                    return jsonify({
                        "error": "Token required",
                        "error_type": "missing_token",
                        "timestamp": str(datetime.now())
                    }), 401

                try:
                    # Validate JWT token
                    jwt_secret: str = getattr(AGENT_INSTANCE.config, 'data', {}).get(
                        'jwt_secret', 'default_secret')

                    if not jwt_secret or not isinstance(jwt_secret, str):
                        raise ValidationError("Invalid JWT secret configured",
                                            {"jwt_secret_type": type(jwt_secret).__name__})

                    # Decode token
                    token_clean: str = token.replace("Bearer ", "").strip()
                    if not token_clean:
                        raise ValidationError("Token is empty after Bearer prefix removal",
                                            {"token_length": len(token)})

                    jwt.decode(
                        token_clean,
                        jwt_secret,
                        algorithms=["HS256"],
                    )
                    log_info("api_server", "JWT authentication successful")
                    return f(*args, **kwargs)

                except jwt.ExpiredSignatureError as exp_err:
                    log_error("api_server", "JWT token expired")
                    return jsonify({
                        "error": "Token expired",
                        "error_type": "token_expired",
                        "timestamp": str(datetime.now())
                    }), 401

                except jwt.InvalidTokenError as inv_err:
                    log_error("api_server", f"Invalid JWT token: {str(inv_err)}")
                    return jsonify({
                        "error": "Invalid token",
                        "error_type": "invalid_token",
                        "timestamp": str(datetime.now())
                    }), 401

                except ValidationError as val_err:
                    log_error("api_server", f"Token validation error: {val_err.message}",
                             extra=val_err.to_dict())
                    return jsonify({
                        "error": "Authentication validation failed",
                        "error_type": "validation_error",
                        "timestamp": str(datetime.now())
                    }), 401

                except Exception as auth_err:
                    log_error("api_server", f"Unexpected auth error: {str(auth_err)}",
                             exception=auth_err)
                    return jsonify({
                        "error": "Authentication failed",
                        "error_type": type(auth_err).__name__,
                        "timestamp": str(datetime.now())
                    }), 401

        except ErrorContext:
            raise
        except Exception as decorator_err:
            log_error("api_server", f"Auth decorator error: {str(decorator_err)}",
                     exception=decorator_err)
            return jsonify({
                "error": "Authentication error",
                "error_type": "decorator_error",
                "timestamp": str(datetime.now())
            }), 500

    return decorated


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Dict[str, Any], int]:
    """Health check endpoint for monitoring agent status

    Returns:
        JSON response with agent health status, version, and component status
    """
    import asyncio
    try:
        with ErrorContext("health_check"):
            start_time: float = datetime.now().timestamp()
            status: Dict[str, Any] = {
                "status": "healthy",
                "agent_initialized": AGENT_INSTANCE is not None,
                "version": "3.0.0",
                "timestamp": str(datetime.now()),
            }
            # Get detailed component status if agent available
            if AGENT_INSTANCE:
                try:
                    # Await get_ultron_status (async)
                    loop = asyncio.get_event_loop()
                    agent_status = loop.run_until_complete(AGENT_INSTANCE.get_ultron_status())
                    status["ultron_status"] = agent_status
                    status["is_healthy"] = AGENT_INSTANCE.is_healthy()
                except Exception as status_err:
                    log_error("api_server", f"Error collecting component status: {status_err}")
                    status["ultron_status"] = {"status_collection_error": str(status_err)}
                    status["is_healthy"] = False
            else:
                status["ultron_status"] = {"error": "Agent not initialized"}
                status["is_healthy"] = False

            response_time: float = datetime.now().timestamp() - start_time
            status["response_time_seconds"] = response_time

            log_info("api_server", "Health check completed",
                    extra={"agent_initialized": status["agent_initialized"],
                           "response_time": f"{response_time:.3f}s"})

            return jsonify(status), 200

    except Exception as health_err:
        log_error("api_server", f"Health check failed: {str(health_err)}",
                 exception=health_err)
        return jsonify({
            "status": "error",
            "error": str(health_err),
            "error_type": type(health_err).__name__,
            "timestamp": str(datetime.now())
        }), 500


@app.route("/status", methods=["GET"])
def status() -> Tuple[Dict[str, str], int]:
    status_text: str = "online" if AGENT_INSTANCE else "uninitialized"
    return jsonify({"status": status_text}), 200


@app.route("/command", methods=["POST"])
@require_auth
@rate_limit(requests_per_hour=100, burst_size=10)
def command() -> Tuple[Dict[str, Any], int]:
    """Process a command through the agent

    Request body: {"command": "the command to process"}

    Returns:
        JSON response with command result or error
    """
    try:
        with ErrorContext("command_processing"):
            start_time: float = datetime.now().timestamp()

            # Validate agent
            if not AGENT_INSTANCE:
                error_msg = "Agent not initialized"
                log_error("api_server", error_msg)
                return jsonify({
                    "error": error_msg,
                    "error_type": "agent_not_initialized",
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 500

            # Parse request
            try:
                data: Optional[Dict[str, Any]] = request.get_json(
                    silent=False, force=True)
            except Exception as json_err:
                log_error("api_server", f"JSON parsing error: {json_err}")
                return jsonify({
                    "error": "Invalid JSON in request body",
                    "error_type": "json_parse_error",
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            # Validate command
            if not data or "command" not in data:
                log_error("api_server", "No command provided in request")
                return jsonify({
                    "error": "No command provided",
                    "error_type": "missing_command",
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            command_text: str = data.get("command", "").strip()
            if not command_text or not isinstance(command_text, str):
                error_msg = "Command must be non-empty string"
                log_error("api_server", error_msg,
                         extra={"command_type": type(command_text).__name__})
                return jsonify({
                    "error": error_msg,
                    "error_type": "invalid_command_format",
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            # Execute command with error handling
            try:
                log_info("api_server", f"Executing command: {command_text[:50]}...")

                # Check if handler exists
                if not hasattr(AGENT_INSTANCE, 'handle_text'):
                    raise ResourceError("Agent has no handle_text method",
                                      {"agent_type": type(AGENT_INSTANCE).__name__})

                result: Any = AGENT_INSTANCE.handle_text(command_text)

                response_time: float = datetime.now().timestamp() - start_time
                log_ai_decision("api_server", "Command executed successfully",
                               ai_model="api_gateway",
                               confidence_score=1.0,
                               reasoning=f"Executed in {response_time:.3f}s")

                # Return only the plain text result for user-facing output
                return (str(result) if result else ""), 200

            except ResourceError as res_err:
                log_error("api_server", f"Resource error: {res_err.message}",
                         extra=res_err.to_dict())
                # Return only the error message as plain text
                return (str(res_err.message)), 503

            except Exception as exec_err:
                log_error("api_server",
                         f"Command execution failed: {str(exec_err)}",
                         exception=exec_err)
                # Return only the error message as plain text
                return (str(exec_err)), 500

    except ErrorContext:
        raise
    except Exception as cmd_err:
        log_error("api_server", f"Command endpoint error: {str(cmd_err)}",
                 exception=cmd_err)
        # Return only the error message as plain text
        return ("Internal server error"), 500


# Tools Integration API Endpoints
@app.route("/api/tools/status", methods=["GET"])
def get_tools_status() -> Tuple[Dict[str, Any], int]:
    """Get overall tools status and statistics with comprehensive error handling

    Returns:
        JSON with tools count, status, usage metrics, and detailed tool information
    """
    try:
        with ErrorContext("tools_status"):
            start_time: float = datetime.now().timestamp()

            # Validate agent
            if not AGENT_INSTANCE:
                error_msg = "Agent not initialized"
                log_error("api_server", error_msg)
                return jsonify({
                    "error": error_msg,
                    "error_type": "agent_not_initialized",
                    "total": 0,
                    "active": 0,
                    "timestamp": str(datetime.now())
                }), 503

            # Get tools list with error handling
            try:
                tools: list = AGENT_INSTANCE.list_tools()
                if not isinstance(tools, list):
                    raise ValidationError("list_tools() returned non-list",
                                        {"type": type(tools).__name__})
            except ValidationError:
                raise
            except Exception as list_err:
                log_error("api_server", f"Error listing tools: {list_err}")
                return jsonify({
                    "error": "Failed to list tools",
                    "error_type": "list_tools_error",
                    "total": 0,
                    "active": 0,
                    "timestamp": str(datetime.now())
                }), 500

            # Count active tools with error isolation
            active_tools: int = 0
            try:
                active_tools = len([t for t in tools
                                   if AGENT_INSTANCE.get_tool(t) is not None])
            except Exception as active_err:
                log_error("api_server",
                         f"Error counting active tools: {active_err}")
                active_tools = len(tools)  # Fallback estimate

            # Get detailed tool information with per-tool error isolation
            tools_data: list = []
            total_usage: int = 0
            tools_failed: int = 0

            for tool_name in tools:
                try:
                    tool_instance = AGENT_INSTANCE.get_tool(tool_name)
                    if not tool_instance:
                        continue

                    # Get tool schema with error isolation
                    schema: Dict[str, Any] = {}
                    try:
                        if hasattr(tool_instance, "schema"):
                            schema = tool_instance.schema() or {}
                    except Exception as schema_err:
                        log_error("api_server",
                                 f"Error getting schema for {tool_name}: "
                                 f"{schema_err}")

                    tool_info: Dict[str, Any] = {
                        "name": tool_name,
                        "description": schema.get("description",
                                                 "No description"),
                        "status": "active",
                        "usage_count": getattr(tool_instance,
                                             "usage_count", 0),
                        "last_used": getattr(tool_instance,
                                           "last_used", "Never"),
                        "class_name": tool_instance.__class__.__name__,
                        "module": tool_instance.__class__.__module__,
                        "parameters": schema.get("parameters", {}),
                        "is_async": hasattr(tool_instance, "execute_async"),
                        "requires_config": hasattr(tool_instance, "config")
                    }
                    tools_data.append(tool_info)
                    total_usage += tool_info["usage_count"]

                except Exception as tool_err:
                    log_error("api_server",
                             f"Error processing tool {tool_name}: {tool_err}")
                    tools_failed += 1
                    continue

            response_time: float = datetime.now().timestamp() - start_time

            return jsonify({
                "success": True,
                "total": len(tools),
                "active": active_tools,
                "failed": tools_failed,
                "usage": total_usage,
                "tools": tools_data,
                "response_time_seconds": response_time,
                "timestamp": str(datetime.now())
            }), 200

    except ValidationError as val_err:
        log_error("api_server", f"Validation error: {val_err.message}",
                 extra=val_err.to_dict())
        return jsonify({
            "error": val_err.message,
            "error_type": "validation_error",
            "total": 0,
            "timestamp": str(datetime.now())
        }), 400

    except Exception as status_err:
        log_error("api_server",
                 f"Failed to get tools status: {str(status_err)}",
                 exception=status_err)
        return jsonify({
            "error": str(status_err),
            "error_type": type(status_err).__name__,
            "total": 0,
            "active": 0,
            "timestamp": str(datetime.now())
        }), 500


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


@app.route("/api/command/find-tool", methods=["POST"])
def find_tool_for_command():
    """Find which tool can handle a given command.

    Request: {"command": "search for python tutorials"}
    Response: {"tool": "web_search", "can_handle": true}
    """
    try:
        data = request.get_json()
        command = data.get("command", "")

        if not command:
            return jsonify({
                "error": "Command is required",
                "tool": None,
                "can_handle": False
            }), 400

        if not AGENT_INSTANCE or not AGENT_INSTANCE.brain:
            return jsonify({
                "error": "Agent brain not initialized",
                "tool": None,
                "can_handle": False
            }), 503

        # Use brain to find matching tool
        can_handle, tool_name = (
            AGENT_INSTANCE.brain.can_tool_handle_this(command)
        )

        return jsonify({
            "command": command,
            "tool": tool_name,
            "can_handle": can_handle,
            "success": True
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e),
            "tool": None,
            "can_handle": False
        }), 500


@app.route("/api/tools/list", methods=["GET"])
def list_all_tools():
    """List all available tools with descriptions.

    Response: {"tools": [...], "count": N}
    """
    try:
        if not AGENT_INSTANCE or not AGENT_INSTANCE.brain:
            return jsonify({
                "error": "Agent brain not initialized",
                "tools": [],
                "count": 0
            }), 503

        # Use brain to get tools summary
        tools_summary = (
            AGENT_INSTANCE.brain.get_available_tools_summary()
        )

        return jsonify({
            "success": True,
            **tools_summary
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e),
            "tools": [],
            "count": 0
        }), 500


@app.route("/api/tools/execute", methods=["POST"])
@rate_limit(requests_per_hour=100, burst_size=10)
def execute_tool() -> Tuple[Dict[str, Any], int]:
    """Execute a specific tool with given command

    Request: {
        "tool": "web_search",
        "command": "search for python tutorials"
    }

    Returns:
        JSON with tool execution result or error
    """
    try:
        with ErrorContext("tool_execution"):
            start_time: float = datetime.now().timestamp()

            # Parse JSON request with error handling
            try:
                data: Optional[Dict[str, Any]] = request.get_json(
                    silent=False, force=True)
            except Exception as json_err:
                log_error("api_server", f"JSON parsing error: {json_err}")
                return jsonify({
                    "error": "Invalid JSON in request",
                    "error_type": "json_parse_error",
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            # Validate required fields
            if not data:
                return jsonify({
                    "error": "Empty request body",
                    "error_type": "empty_request",
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            tool_name: Optional[str] = data.get("tool")
            command: str = data.get("command", "").strip()

            # Validate tool name
            if not tool_name or not isinstance(tool_name, str):
                error_msg = "Tool name is required and must be string"
                log_error("api_server", error_msg)
                return jsonify({
                    "error": error_msg,
                    "error_type": "invalid_tool_name",
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            # Validate command
            if not command:
                error_msg = "Command is required"
                log_error("api_server", error_msg)
                return jsonify({
                    "error": error_msg,
                    "error_type": "missing_command",
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 400

            # Validate agent and brain
            if not AGENT_INSTANCE:
                error_msg = "Agent not initialized"
                log_error("api_server", error_msg)
                return jsonify({
                    "error": error_msg,
                    "error_type": "agent_not_initialized",
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 503

            if not AGENT_INSTANCE.brain:
                error_msg = "Agent brain not initialized"
                log_error("api_server", error_msg)
                return jsonify({
                    "error": error_msg,
                    "error_type": "brain_not_initialized",
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 503

            # Execute tool with error handling
            try:
                log_info("api_server",
                        f"Executing tool: {tool_name}, command: "
                        f"{command[:40]}...")

                result: Any = AGENT_INSTANCE.brain.execute_tool(
                    tool_name, command
                )

                response_time: float = (datetime.now().timestamp() -
                                       start_time)

                log_ai_decision("api_server",
                               f"Tool {tool_name} executed successfully",
                               ai_model="api_gateway",
                               confidence_score=1.0,
                               reasoning=f"Completed in {response_time:.3f}s")

                return jsonify({
                    "success": True,
                    "tool": tool_name,
                    "command": command,
                    "result": str(result) if result else "",
                    "response_time_seconds": response_time,
                    "timestamp": str(datetime.now())
                }), 200

            except AsyncError as async_err:
                log_error("api_server",
                         f"Async error executing {tool_name}: "
                         f"{async_err.message}",
                         extra=async_err.to_dict())
                return jsonify({
                    "error": async_err.message,
                    "error_type": "async_error",
                    "tool": tool_name,
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 504

            except Exception as exec_err:
                error_msg = f"Tool execution failed: {str(exec_err)}"
                log_error("api_server", error_msg, exception=exec_err)
                return jsonify({
                    "error": str(exec_err),
                    "error_type": type(exec_err).__name__,
                    "tool": tool_name,
                    "result": None,
                    "success": False,
                    "timestamp": str(datetime.now())
                }), 500

    except ErrorContext:
        raise
    except Exception as endpoint_err:
        log_error("api_server",
                 f"Execute tool endpoint error: {str(endpoint_err)}",
                 exception=endpoint_err)
        return jsonify({
            "error": "Internal server error",
            "error_type": type(endpoint_err).__name__,
            "result": None,
            "success": False,
            "timestamp": str(datetime.now())
        }), 500


# SSH Server Management Endpoints
@app.route("/api/ssh/status", methods=["GET"])
@require_auth
@rate_limit(requests_per_hour=100, burst_size=10)
def get_ssh_status():
    """Get SSH server status"""
    try:
        with ErrorContext("ssh_status_check"):
            if not AGENT_INSTANCE:
                return jsonify({
                    "error": "Agent not initialized",
                    "error_type": "service_unavailable"
                }), 503

            # Get SSH tool from agent
            ssh_tool = None
            if hasattr(AGENT_INSTANCE, 'tools'):
                for tool in AGENT_INSTANCE.tools:
                    tool_name = getattr(tool.__class__, '__name__', '')
                    if tool_name == 'SSHServerTool':
                        ssh_tool = tool
                        break

            if ssh_tool:
                is_running = ssh_tool.is_running()
                local_ip = ssh_tool.get_local_ip()
                cmd = f"ssh -p {ssh_tool.port} anyuser@{local_ip}"
                return jsonify({
                    "running": is_running,
                    "port": ssh_tool.port,
                    "local_ip": local_ip,
                    "password": ssh_tool.password,
                    "connect_command": cmd,
                    "timestamp": str(datetime.now())
                }), 200
            else:
                return jsonify({
                    "running": False,
                    "port": 2222,
                    "error": "SSH tool not available",
                    "timestamp": str(datetime.now())
                }), 503

    except Exception as e:
        error_msg = f"SSH status check failed: {str(e)}"
        log_error("api_server", error_msg, exception=e)
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "running": False,
            "timestamp": str(datetime.now())
        }), 500


@app.route("/api/ssh/start", methods=["POST"])
@require_auth
@rate_limit(requests_per_hour=50, burst_size=5)
def start_ssh_server():
    """Start SSH server"""
    try:
        with ErrorContext("ssh_server_start"):
            if not AGENT_INSTANCE:
                return jsonify({
                    "error": "Agent not initialized",
                    "error_type": "service_unavailable"
                }), 503

            # Execute SSH start command through agent
            result = AGENT_INSTANCE.execute_command("ssh start")

            if "✅" in result or "started" in result.lower():
                log_info("api_server", "SSH server started via API")
                return jsonify({
                    "success": True,
                    "message": result,
                    "port": 2222,
                    "timestamp": str(datetime.now())
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": result,
                    "error": "Failed to start SSH server",
                    "timestamp": str(datetime.now())
                }), 500

    except Exception as e:
        error_msg = f"SSH server start failed: {str(e)}"
        log_error("api_server", error_msg, exception=e)
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": str(datetime.now())
        }), 500


@app.route("/api/ssh/stop", methods=["POST"])
@require_auth
@rate_limit(requests_per_hour=50, burst_size=5)
def stop_ssh_server():
    """Stop SSH server"""
    try:
        with ErrorContext("ssh_server_stop"):
            if not AGENT_INSTANCE:
                return jsonify({
                    "error": "Agent not initialized",
                    "error_type": "service_unavailable"
                }), 503

            # Execute SSH stop command through agent
            result = AGENT_INSTANCE.execute_command("ssh stop")

            if "✅" in result or "stopped" in result.lower():
                log_info("api_server", "SSH server stopped via API")
                return jsonify({
                    "success": True,
                    "message": result,
                    "timestamp": str(datetime.now())
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": result,
                    "error": "Failed to stop SSH server",
                    "timestamp": str(datetime.now())
                }), 500

    except Exception as e:
        error_msg = f"SSH server stop failed: {str(e)}"
        log_error("api_server", error_msg, exception=e)
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": str(datetime.now())
        }), 500


@app.route("/api/ssh/restart", methods=["POST"])
@require_auth
@rate_limit(requests_per_hour=30, burst_size=3)
def restart_ssh_server():
    """Restart SSH server"""
    try:
        with ErrorContext("ssh_server_restart"):
            if not AGENT_INSTANCE:
                return jsonify({
                    "error": "Agent not initialized",
                    "error_type": "service_unavailable"
                }), 503

            # Execute SSH restart command through agent
            result = AGENT_INSTANCE.execute_command("ssh restart")

            if "✅" in result or "started" in result.lower():
                log_info("api_server", "SSH server restarted via API")
                return jsonify({
                    "success": True,
                    "message": result,
                    "port": 2222,
                    "timestamp": str(datetime.now())
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": result,
                    "error": "Failed to restart SSH server",
                    "timestamp": str(datetime.now())
                }), 500

    except Exception as e:
        error_msg = f"SSH server restart failed: {str(e)}"
        log_error("api_server", error_msg, exception=e)
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": str(datetime.now())
        }), 500


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
            print("🚀 Starting Flask API server on port 8889...")
            app.run(host="0.0.0.0", port=8889, debug=False)
    except Exception as e:
        print(f"❌ Flask server failed: {e}")
        print("Trying alternative port 5001...")
        try:
            app.run(host="0.0.0.0", port=5001, debug=False)
        except Exception as e2:
            print(f"❌ Alternative port also failed: {e2}")
