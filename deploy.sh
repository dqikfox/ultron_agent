#!/bin/bash

# ULTRON Agent 3.0 - Deployment Script
# Automates deployment of Docker-based ULTRON Agent
# Usage: ./deploy.sh [environment] [action]
# Environments: development, staging, production
# Actions: deploy, stop, restart, logs, status

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="${1:-development}"
ACTION="${2:-deploy}"
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="ultron-agent"
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

# Functions
check_dependencies() {
    log "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed"
        exit 1
    fi

    log_success "Dependencies verified"
}

check_environment() {
    log "Checking environment: $ENVIRONMENT"

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "docker-compose.yml not found"
        exit 1
    fi

    if [ ! -f "ultron_config.json" ]; then
        log_error "ultron_config.json not found"
        exit 1
    fi

    log_success "Environment files verified"
}

deploy() {
    log "Starting deployment for $ENVIRONMENT environment..."

    # Validate system
    log "Running deployment validation..."
    if command -v python &> /dev/null; then
        python deployment_validator.py || log_warning "Validation completed with warnings"
    fi

    # Build image
    log "Building Docker image..."
    docker-compose -p "$PROJECT_NAME" build
    log_success "Image built"

    # Pull images
    log "Pulling latest images..."
    docker-compose -p "$PROJECT_NAME" pull ollama || true
    log_success "Images pulled"

    # Start services
    log "Starting services..."
    docker-compose -p "$PROJECT_NAME" up -d
    log_success "Services started"

    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 10

    # Health check
    log "Running health checks..."
    health_check || log_warning "Some health checks failed"

    log_success "Deployment completed successfully"
}

stop() {
    log "Stopping services..."
    docker-compose -p "$PROJECT_NAME" down
    log_success "Services stopped"
}

restart() {
    log "Restarting services..."
    stop
    sleep 5
    deploy
}

logs() {
    log "Displaying service logs..."
    docker-compose -p "$PROJECT_NAME" logs -f
}

status() {
    log "Service Status:"
    echo "═══════════════════════════════════════════════════════"
    docker-compose -p "$PROJECT_NAME" ps
    echo "═══════════════════════════════════════════════════════"

    log "Checking service health..."
    health_check
}

health_check() {
    local api_health=false
    local ollama_health=false

    log "API Server health check..."
    if curl -sf http://localhost:5000/health > /dev/null 2>&1; then
        log_success "API Server responding"
        api_health=true
    else
        log_warning "API Server not responding"
    fi

    log "Ollama health check..."
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_success "Ollama responding"
        ollama_health=true
    else
        log_warning "Ollama not responding"
    fi

    if [ "$api_health" = true ] && [ "$ollama_health" = true ]; then
        log_success "All health checks passed"
        return 0
    else
        return 1
    fi
}

backup() {
    log "Creating backup..."
    BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup configuration
    cp ultron_config.json "$BACKUP_DIR/" 2>/dev/null || true

    # Backup logs
    cp -r logs "$BACKUP_DIR/logs_backup" 2>/dev/null || true

    log_success "Backup created at: $BACKUP_DIR"
    echo "$BACKUP_DIR"
}

restore() {
    local backup_dir="$1"

    if [ -z "$backup_dir" ]; then
        log_error "Backup directory not specified"
        exit 1
    fi

    if [ ! -d "$backup_dir" ]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi

    log "Restoring from: $backup_dir"

    # Restore configuration
    if [ -f "$backup_dir/ultron_config.json" ]; then
        cp "$backup_dir/ultron_config.json" .
        log_success "Configuration restored"
    fi

    log_success "Restore completed"
}

display_help() {
    echo -e "${BLUE}ULTRON Agent 3.0 - Deployment Script${NC}"
    echo ""
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments:"
    echo "  development    - Development environment (default)"
    echo "  staging        - Staging environment"
    echo "  production     - Production environment"
    echo ""
    echo "Actions:"
    echo "  deploy         - Deploy/start services (default)"
    echo "  stop           - Stop services"
    echo "  restart        - Restart services"
    echo "  logs           - Display service logs"
    echo "  status         - Show service status"
    echo "  backup         - Create backup"
    echo "  restore <dir>  - Restore from backup"
    echo "  help           - Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 development deploy"
    echo "  $0 production restart"
    echo "  $0 development logs"
}

# Main
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}ULTRON Agent 3.0 - Deployment Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

log "Deployment starting..."
log "Environment: $ENVIRONMENT"
log "Action: $ACTION"
log "Log file: $LOG_FILE"
echo ""

# Check dependencies
check_dependencies
check_environment

# Execute action
case "$ACTION" in
    deploy)
        deploy
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    backup)
        backup
        ;;
    restore)
        restore "$3"
        ;;
    help)
        display_help
        ;;
    *)
        log_error "Unknown action: $ACTION"
        display_help
        exit 1
        ;;
esac

echo ""
log "Deployment script completed"
