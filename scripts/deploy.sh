#!/bin/bash

set -e

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN=${2:-yourdomain.com}
BACKUP_BEFORE_DEPLOY=${3:-true}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        log_error ".env file not found"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p models
    mkdir -p data
    mkdir -p backups
    mkdir -p nginx/ssl
    mkdir -p nginx/logs
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p monitoring/grafana/plugins
    mkdir -p monitoring/rules
    mkdir -p postgres
    mkdir -p redis
    
    log_success "Directories created"
}

# Generate SSL certificates if they don't exist
generate_ssl_certificates() {
    log_info "Checking SSL certificates..."
    
    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
        log_warning "SSL certificates not found. Generating self-signed certificates..."
        
        openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
            -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
        
        log_success "Self-signed SSL certificates generated"
        log_warning "For production, replace with proper SSL certificates from a CA"
    else
        log_success "SSL certificates found"
    fi
}

# Build frontend
build_frontend() {
    log_info "Building frontend..."
    
    cd frontend
    
    # Install dependencies
    npm ci --production
    
    # Build the application
    npm run build
    
    cd ..
    
    log_success "Frontend built successfully"
}

# Build backend
build_backend() {
    log_info "Building backend..."
    
    cd backend
    
    # Build the Docker image
    docker build -f Dockerfile.prod -t stockee-backend:latest .
    
    cd ..
    
    log_success "Backend built successfully"
}

# Backup existing data
backup_data() {
    if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
        log_info "Creating backup of existing data..."
        
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup database if it exists
        if docker-compose ps postgres | grep -q "Up"; then
            log_info "Backing up database..."
            docker-compose exec -T postgres pg_dump -U stockee -d stockee > "$BACKUP_DIR/database.sql"
        fi
        
        # Backup application data
        if [ -d "data" ]; then
            log_info "Backing up application data..."
            tar -czf "$BACKUP_DIR/data.tar.gz" data/
        fi
        
        # Backup models
        if [ -d "models" ]; then
            log_info "Backing up models..."
            tar -czf "$BACKUP_DIR/models.tar.gz" models/
        fi
        
        log_success "Backup created in $BACKUP_DIR"
    fi
}

# Deploy with Docker Compose
deploy_services() {
    log_info "Deploying services..."
    
    # Stop existing services
    docker-compose -f docker-compose.prod.yml down
    
    # Pull latest images
    docker-compose -f docker-compose.prod.yml pull
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "Services deployed"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for database
    log_info "Waiting for database..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U stockee -d stockee > /dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Database failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Redis failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for backend
    log_info "Waiting for backend..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Backend failed to start within 120 seconds"
        exit 1
    fi
    
    log_success "All services are ready"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
    
    log_success "Database migrations completed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check API health
    if ! curl -f http://localhost/api/health > /dev/null 2>&1; then
        log_error "API health check failed"
        exit 1
    fi
    
    # Check database connectivity
    if ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U stockee -d stockee > /dev/null 2>&1; then
        log_error "Database health check failed"
        exit 1
    fi
    
    # Check Redis connectivity
    if ! docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_error "Redis health check failed"
        exit 1
    fi
    
    log_success "Health check passed"
}

# Display deployment information
display_info() {
    log_success "Deployment completed successfully!"
    echo
    echo "🌐 Application URLs:"
    echo "   Web App: https://${DOMAIN}"
    echo "   API Docs: https://${DOMAIN}/api/docs"
    echo "   Health Check: https://${DOMAIN}/health"
    echo
    echo "📊 Monitoring:"
    echo "   Grafana: https://${DOMAIN}:3000"
    echo "   Prometheus: https://${DOMAIN}:9090"
    echo "   Kibana: https://${DOMAIN}:5601"
    echo
    echo "🔧 Management:"
    echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   Scale services: docker-compose -f docker-compose.prod.yml up -d --scale backend=5"
    echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
    echo
    echo "📋 Next steps:"
    echo "   1. Update DNS records to point to this server"
    echo "   2. Replace self-signed SSL certificates with proper ones"
    echo "   3. Configure monitoring alerts"
    echo "   4. Set up automated backups"
    echo "   5. Review security settings"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove unused Docker volumes
    docker volume prune -f
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting Stockee deployment to $ENVIRONMENT environment..."
    echo
    
    check_root
    check_prerequisites
    create_directories
    generate_ssl_certificates
    build_frontend
    build_backend
    backup_data
    deploy_services
    wait_for_services
    run_migrations
    health_check
    cleanup
    display_info
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"
