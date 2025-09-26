#!/bin/bash

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="stockee"
DB_USER="stockee"
RETENTION_DAYS=30

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

# Create backup directory
create_backup_dir() {
    log_info "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
    log_success "Backup directory created: $BACKUP_DIR"
}

# Backup database
backup_database() {
    log_info "Backing up database..."
    
    # Check if database is accessible
    if ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
        log_error "Database is not accessible"
        return 1
    fi
    
    # Create database backup
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/stockee_${DATE}.sql"
    
    # Compress the backup
    gzip "$BACKUP_DIR/stockee_${DATE}.sql"
    
    log_success "Database backup completed: stockee_${DATE}.sql.gz"
}

# Backup application data
backup_application_data() {
    log_info "Backing up application data..."
    
    # Backup models directory
    if [ -d "models" ]; then
        tar -czf "$BACKUP_DIR/models_${DATE}.tar.gz" models/
        log_success "Models backup completed: models_${DATE}.tar.gz"
    else
        log_warning "Models directory not found"
    fi
    
    # Backup data directory
    if [ -d "data" ]; then
        tar -czf "$BACKUP_DIR/data_${DATE}.tar.gz" data/
        log_success "Data backup completed: data_${DATE}.tar.gz"
    else
        log_warning "Data directory not found"
    fi
    
    # Backup logs directory
    if [ -d "logs" ]; then
        tar -czf "$BACKUP_DIR/logs_${DATE}.tar.gz" logs/
        log_success "Logs backup completed: logs_${DATE}.tar.gz"
    else
        log_warning "Logs directory not found"
    fi
}

# Backup configuration files
backup_configuration() {
    log_info "Backing up configuration files..."
    
    # Create configuration backup directory
    mkdir -p "$BACKUP_DIR/config_${DATE}"
    
    # Backup environment file
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/config_${DATE}/"
        log_success "Environment file backed up"
    else
        log_warning "Environment file not found"
    fi
    
    # Backup Docker Compose files
    if [ -f "docker-compose.prod.yml" ]; then
        cp docker-compose.prod.yml "$BACKUP_DIR/config_${DATE}/"
        log_success "Docker Compose file backed up"
    fi
    
    # Backup Nginx configuration
    if [ -d "nginx" ]; then
        cp -r nginx "$BACKUP_DIR/config_${DATE}/"
        log_success "Nginx configuration backed up"
    fi
    
    # Backup monitoring configuration
    if [ -d "monitoring" ]; then
        cp -r monitoring "$BACKUP_DIR/config_${DATE}/"
        log_success "Monitoring configuration backed up"
    fi
    
    # Compress configuration backup
    tar -czf "$BACKUP_DIR/config_${DATE}.tar.gz" -C "$BACKUP_DIR" "config_${DATE}"
    rm -rf "$BACKUP_DIR/config_${DATE}"
    
    log_success "Configuration backup completed: config_${DATE}.tar.gz"
}

# Upload to cloud storage (optional)
upload_to_cloud() {
    if [ -n "$AWS_S3_BUCKET" ]; then
        log_info "Uploading backups to S3..."
        
        # Upload database backup
        if [ -f "$BACKUP_DIR/stockee_${DATE}.sql.gz" ]; then
            aws s3 cp "$BACKUP_DIR/stockee_${DATE}.sql.gz" "s3://$AWS_S3_BUCKET/database/"
            log_success "Database backup uploaded to S3"
        fi
        
        # Upload application data
        for file in "$BACKUP_DIR"/*_${DATE}.tar.gz; do
            if [ -f "$file" ]; then
                aws s3 cp "$file" "s3://$AWS_S3_BUCKET/application/"
                log_success "Application backup uploaded to S3: $(basename "$file")"
            fi
        done
        
        # Upload configuration
        if [ -f "$BACKUP_DIR/config_${DATE}.tar.gz" ]; then
            aws s3 cp "$BACKUP_DIR/config_${DATE}.tar.gz" "s3://$AWS_S3_BUCKET/configuration/"
            log_success "Configuration backup uploaded to S3"
        fi
    else
        log_info "S3 bucket not configured, skipping cloud upload"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log_info "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    # Remove old database backups
    find "$BACKUP_DIR" -name "stockee_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # Remove old application backups
    find "$BACKUP_DIR" -name "models_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "data_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "logs_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    # Remove old configuration backups
    find "$BACKUP_DIR" -name "config_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    log_success "Old backups cleaned up"
}

# Verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."
    
    # Verify database backup
    if [ -f "$BACKUP_DIR/stockee_${DATE}.sql.gz" ]; then
        if gzip -t "$BACKUP_DIR/stockee_${DATE}.sql.gz"; then
            log_success "Database backup integrity verified"
        else
            log_error "Database backup integrity check failed"
            return 1
        fi
    fi
    
    # Verify application backups
    for file in "$BACKUP_DIR"/*_${DATE}.tar.gz; do
        if [ -f "$file" ]; then
            if tar -tzf "$file" > /dev/null 2>&1; then
                log_success "Backup integrity verified: $(basename "$file")"
            else
                log_error "Backup integrity check failed: $(basename "$file")"
                return 1
            fi
        fi
    done
}

# Generate backup report
generate_report() {
    log_info "Generating backup report..."
    
    REPORT_FILE="$BACKUP_DIR/backup_report_${DATE}.txt"
    
    {
        echo "Stockee Backup Report"
        echo "===================="
        echo "Date: $(date)"
        echo "Backup ID: $DATE"
        echo ""
        echo "Backup Files:"
        echo "-------------"
        
        if [ -f "$BACKUP_DIR/stockee_${DATE}.sql.gz" ]; then
            echo "Database: stockee_${DATE}.sql.gz ($(du -h "$BACKUP_DIR/stockee_${DATE}.sql.gz" | cut -f1))"
        fi
        
        for file in "$BACKUP_DIR"/*_${DATE}.tar.gz; do
            if [ -f "$file" ]; then
                echo "Application: $(basename "$file") ($(du -h "$file" | cut -f1))"
            fi
        done
        
        if [ -f "$BACKUP_DIR/config_${DATE}.tar.gz" ]; then
            echo "Configuration: config_${DATE}.tar.gz ($(du -h "$BACKUP_DIR/config_${DATE}.tar.gz" | cut -f1))"
        fi
        
        echo ""
        echo "Total Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
        echo ""
        echo "Backup Location: $BACKUP_DIR"
        echo "Retention Policy: $RETENTION_DAYS days"
        
        if [ -n "$AWS_S3_BUCKET" ]; then
            echo "Cloud Storage: S3 bucket $AWS_S3_BUCKET"
        else
            echo "Cloud Storage: Not configured"
        fi
        
    } > "$REPORT_FILE"
    
    log_success "Backup report generated: $REPORT_FILE"
}

# Main backup function
main() {
    log_info "Starting Stockee backup process..."
    echo
    
    create_backup_dir
    backup_database
    backup_application_data
    backup_configuration
    verify_backup
    upload_to_cloud
    cleanup_old_backups
    generate_report
    
    log_success "Backup process completed successfully!"
    echo
    echo "📁 Backup Location: $BACKUP_DIR"
    echo "📊 Backup ID: $DATE"
    echo "📋 Report: backup_report_${DATE}.txt"
    echo
    echo "🔧 To restore from backup:"
    echo "   Database: gunzip -c $BACKUP_DIR/stockee_${DATE}.sql.gz | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U $DB_USER -d $DB_NAME"
    echo "   Application: tar -xzf $BACKUP_DIR/models_${DATE}.tar.gz"
    echo "   Configuration: tar -xzf $BACKUP_DIR/config_${DATE}.tar.gz"
}

# Handle script interruption
trap 'log_error "Backup interrupted"; exit 1' INT TERM

# Run main function
main "$@"
