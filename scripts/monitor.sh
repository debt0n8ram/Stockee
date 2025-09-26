#!/bin/bash

set -e

# Configuration
LOG_FILE="/var/log/stockee-monitor.log"
ALERT_EMAIL="admin@yourdomain.com"
THRESHOLD_CPU=80
THRESHOLD_MEMORY=85
THRESHOLD_DISK=90
THRESHOLD_RESPONSE_TIME=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$LOG_FILE"
}

# Send alert email
send_alert() {
    local subject="$1"
    local message="$2"
    
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
        log_info "Alert email sent: $subject"
    else
        log_warning "Mail command not available, cannot send alert email"
    fi
}

# Check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    if (( $(echo "$CPU_USAGE > $THRESHOLD_CPU" | bc -l) )); then
        log_warning "High CPU usage: ${CPU_USAGE}%"
        send_alert "Stockee Alert: High CPU Usage" "CPU usage is ${CPU_USAGE}%, which exceeds the threshold of ${THRESHOLD_CPU}%"
    else
        log_success "CPU usage normal: ${CPU_USAGE}%"
    fi
    
    # Memory usage
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEMORY_USAGE" -gt "$THRESHOLD_MEMORY" ]; then
        log_warning "High memory usage: ${MEMORY_USAGE}%"
        send_alert "Stockee Alert: High Memory Usage" "Memory usage is ${MEMORY_USAGE}%, which exceeds the threshold of ${THRESHOLD_MEMORY}%"
    else
        log_success "Memory usage normal: ${MEMORY_USAGE}%"
    fi
    
    # Disk usage
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt "$THRESHOLD_DISK" ]; then
        log_warning "High disk usage: ${DISK_USAGE}%"
        send_alert "Stockee Alert: High Disk Usage" "Disk usage is ${DISK_USAGE}%, which exceeds the threshold of ${THRESHOLD_DISK}%"
    else
        log_success "Disk usage normal: ${DISK_USAGE}%"
    fi
}

# Check Docker containers
check_docker_containers() {
    log_info "Checking Docker containers..."
    
    # Get list of containers
    CONTAINERS=$(docker-compose -f docker-compose.prod.yml ps -q)
    
    for container in $CONTAINERS; do
        # Check if container is running
        if [ "$(docker inspect -f '{{.State.Running}}' "$container")" = "true" ]; then
            log_success "Container $container is running"
        else
            log_error "Container $container is not running"
            send_alert "Stockee Alert: Container Down" "Container $container is not running"
        fi
        
        # Check container health
        HEALTH=$(docker inspect -f '{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
        if [ "$HEALTH" = "unhealthy" ]; then
            log_error "Container $container is unhealthy"
            send_alert "Stockee Alert: Container Unhealthy" "Container $container is unhealthy"
        elif [ "$HEALTH" = "healthy" ]; then
            log_success "Container $container is healthy"
        fi
    done
}

# Check application health
check_application_health() {
    log_info "Checking application health..."
    
    # Check API health endpoint
    if curl -f -s http://localhost:8000/api/health > /dev/null; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        send_alert "Stockee Alert: API Health Check Failed" "The API health check endpoint is not responding"
    fi
    
    # Check response time
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/api/health)
    if (( $(echo "$RESPONSE_TIME > $THRESHOLD_RESPONSE_TIME" | bc -l) )); then
        log_warning "High response time: ${RESPONSE_TIME}s"
        send_alert "Stockee Alert: High Response Time" "API response time is ${RESPONSE_TIME}s, which exceeds the threshold of ${THRESHOLD_RESPONSE_TIME}s"
    else
        log_success "Response time normal: ${RESPONSE_TIME}s"
    fi
    
    # Check WebSocket connection
    if curl -f -s http://localhost:8000/api/ws/health > /dev/null; then
        log_success "WebSocket health check passed"
    else
        log_warning "WebSocket health check failed"
        send_alert "Stockee Alert: WebSocket Health Check Failed" "The WebSocket health check endpoint is not responding"
    fi
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U stockee -d stockee > /dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        send_alert "Stockee Alert: Database Connection Failed" "Cannot connect to the PostgreSQL database"
    fi
    
    # Check database size
    DB_SIZE=$(docker-compose -f docker-compose.prod.yml exec -T postgres psql -U stockee -d stockee -t -c "SELECT pg_size_pretty(pg_database_size('stockee'));" | tr -d ' ')
    log_info "Database size: $DB_SIZE"
    
    # Check active connections
    ACTIVE_CONNECTIONS=$(docker-compose -f docker-compose.prod.yml exec -T postgres psql -U stockee -d stockee -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" | tr -d ' ')
    log_info "Active database connections: $ACTIVE_CONNECTIONS"
    
    if [ "$ACTIVE_CONNECTIONS" -gt 50 ]; then
        log_warning "High number of active database connections: $ACTIVE_CONNECTIONS"
        send_alert "Stockee Alert: High Database Connections" "Number of active database connections is $ACTIVE_CONNECTIONS, which is unusually high"
    fi
}

# Check Redis connectivity
check_redis() {
    log_info "Checking Redis connectivity..."
    
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis connectivity check passed"
    else
        log_error "Redis connectivity check failed"
        send_alert "Stockee Alert: Redis Connection Failed" "Cannot connect to the Redis cache"
    fi
    
    # Check Redis memory usage
    REDIS_MEMORY=$(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    log_info "Redis memory usage: $REDIS_MEMORY"
    
    # Check Redis hit rate
    REDIS_HIT_RATE=$(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli info stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
    REDIS_MISS_RATE=$(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli info stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
    
    if [ "$REDIS_HIT_RATE" -gt 0 ] && [ "$REDIS_MISS_RATE" -gt 0 ]; then
        HIT_RATIO=$(echo "scale=2; $REDIS_HIT_RATE / ($REDIS_HIT_RATE + $REDIS_MISS_RATE) * 100" | bc)
        log_info "Redis hit ratio: ${HIT_RATIO}%"
        
        if (( $(echo "$HIT_RATIO < 80" | bc -l) )); then
            log_warning "Low Redis hit ratio: ${HIT_RATIO}%"
            send_alert "Stockee Alert: Low Redis Hit Ratio" "Redis hit ratio is ${HIT_RATIO}%, which is below the recommended 80%"
        fi
    fi
}

# Check log files for errors
check_logs() {
    log_info "Checking log files for errors..."
    
    # Check application logs for errors
    ERROR_COUNT=$(docker-compose -f docker-compose.prod.yml logs --tail=100 backend | grep -i error | wc -l)
    if [ "$ERROR_COUNT" -gt 10 ]; then
        log_warning "High number of errors in application logs: $ERROR_COUNT"
        send_alert "Stockee Alert: High Error Count" "Found $ERROR_COUNT errors in the last 100 log entries"
    else
        log_success "Error count in logs is normal: $ERROR_COUNT"
    fi
    
    # Check for critical errors
    CRITICAL_ERRORS=$(docker-compose -f docker-compose.prod.yml logs --tail=100 backend | grep -i "critical\|fatal" | wc -l)
    if [ "$CRITICAL_ERRORS" -gt 0 ]; then
        log_error "Critical errors found in logs: $CRITICAL_ERRORS"
        send_alert "Stockee Alert: Critical Errors" "Found $CRITICAL_ERRORS critical errors in the application logs"
    fi
}

# Check external API connectivity
check_external_apis() {
    log_info "Checking external API connectivity..."
    
    # Check Alpha Vantage API
    if curl -f -s "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&apikey=demo" > /dev/null; then
        log_success "Alpha Vantage API connectivity check passed"
    else
        log_warning "Alpha Vantage API connectivity check failed"
        send_alert "Stockee Alert: Alpha Vantage API Down" "Cannot connect to Alpha Vantage API"
    fi
    
    # Check News API
    if curl -f -s "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo" > /dev/null; then
        log_success "News API connectivity check passed"
    else
        log_warning "News API connectivity check failed"
        send_alert "Stockee Alert: News API Down" "Cannot connect to News API"
    fi
}

# Generate monitoring report
generate_report() {
    log_info "Generating monitoring report..."
    
    REPORT_FILE="/var/log/stockee-monitor-report-$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Stockee Monitoring Report"
        echo "========================"
        echo "Date: $(date)"
        echo ""
        echo "System Resources:"
        echo "-----------------"
        echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
        echo "Memory Usage: $(free | grep Mem | awk '{printf "%.0f%%", $3/$2 * 100.0}')"
        echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        echo "Application Status:"
        echo "------------------"
        echo "API Health: $(curl -f -s http://localhost:8000/api/health > /dev/null && echo "OK" || echo "FAILED")"
        echo "Response Time: $(curl -o /dev/null -s -w '%{time_total}s' http://localhost:8000/api/health)"
        echo ""
        echo "Database Status:"
        echo "---------------"
        echo "Connectivity: $(docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U stockee -d stockee > /dev/null 2>&1 && echo "OK" || echo "FAILED")"
        echo "Size: $(docker-compose -f docker-compose.prod.yml exec -T postgres psql -U stockee -d stockee -t -c "SELECT pg_size_pretty(pg_database_size('stockee'));" | tr -d ' ')"
        echo "Active Connections: $(docker-compose -f docker-compose.prod.yml exec -T postgres psql -U stockee -d stockee -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" | tr -d ' ')"
        echo ""
        echo "Redis Status:"
        echo "------------"
        echo "Connectivity: $(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1 && echo "OK" || echo "FAILED")"
        echo "Memory Usage: $(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')"
        echo ""
        echo "Docker Containers:"
        echo "-----------------"
        docker-compose -f docker-compose.prod.yml ps
        
    } > "$REPORT_FILE"
    
    log_success "Monitoring report generated: $REPORT_FILE"
}

# Main monitoring function
main() {
    log_info "Starting Stockee monitoring check..."
    echo
    
    check_system_resources
    check_docker_containers
    check_application_health
    check_database
    check_redis
    check_logs
    check_external_apis
    generate_report
    
    log_success "Monitoring check completed successfully!"
}

# Handle script interruption
trap 'log_error "Monitoring interrupted"; exit 1' INT TERM

# Run main function
main "$@"
