#!/bin/bash
set -e

# ULTRON Agent Docker Entrypoint Script
echo "🚀 Starting ULTRON Agent..."

# Print version information
echo "📦 Version Information:"
python -c "
try:
    from ultron_agent.__version__ import get_version_info
    info = get_version_info()
    print(f'  Version: {info[\"version\"]}')
    print(f'  Build: {info[\"full_version\"]}')
except ImportError:
    print('  Version: Unable to determine')
"

# Check if config file exists, create from example if needed
if [ ! -f "/app/ultron_config.json" ] && [ -f "/app/ultron_config.json.example" ]; then
    echo "📝 Creating default configuration..."
    cp /app/ultron_config.json.example /app/ultron_config.json
fi

# Set default values for environment variables if not set
export ULTRON_LOG_LEVEL="${ULTRON_LOG_LEVEL:-INFO}"
export ULTRON_HOST="${ULTRON_HOST:-0.0.0.0}"
export ULTRON_PORT="${ULTRON_PORT:-8000}"

echo "⚙️  Configuration:"
echo "  Host: $ULTRON_HOST"
echo "  Port: $ULTRON_PORT"
echo "  Log Level: $ULTRON_LOG_LEVEL"
echo "  Config: $ULTRON_CONFIG_FILE"

# Create log directory if it doesn't exist
mkdir -p /app/logs

# Handle different command types
case "$1" in
    "ultron")
        echo "🎯 Running ULTRON Agent command: $*"
        exec "$@"
        ;;
    "serve"|"server")
        echo "🌐 Starting ULTRON Agent server..."
        exec ultron serve --host "$ULTRON_HOST" --port "$ULTRON_PORT"
        ;;
    "bash"|"sh")
        echo "🐚 Starting interactive shell..."
        exec "$@"
        ;;
    "version")
        echo "📋 Version information:"
        python -c "from ultron_agent.__version__ import get_version_info; import json; print(json.dumps(get_version_info(), indent=2))"
        ;;
    "help"|"--help"|"-h")
        echo "🆘 ULTRON Agent Docker Container Help"
        echo ""
        echo "Usage: docker run [OPTIONS] ultron-agent [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  serve, server    Start the ULTRON Agent server (default)"
        echo "  ultron [args]    Run ULTRON Agent with custom arguments"
        echo "  version          Show version information"
        echo "  bash, sh         Start interactive shell"
        echo "  help             Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  ULTRON_HOST      Server host (default: 0.0.0.0)"
        echo "  ULTRON_PORT      Server port (default: 8000)"
        echo "  ULTRON_LOG_LEVEL Log level (default: INFO)"
        echo "  ULTRON_CONFIG_FILE Config file path"
        echo ""
        echo "Examples:"
        echo "  docker run ultron-agent                    # Start server"
        echo "  docker run ultron-agent version            # Show version"
        echo "  docker run -p 8080:8000 ultron-agent serve # Custom port"
        ;;
    *)
        if [ $# -eq 0 ]; then
            echo "🌐 No command specified, starting server..."
            exec ultron serve --host "$ULTRON_HOST" --port "$ULTRON_PORT"
        else
            echo "🎯 Executing command: $*"
            exec "$@"
        fi
        ;;
esac