# Stockee Deployment Guide

## Overview

This guide covers deploying the Stockee application to production environments. The application supports multiple deployment strategies including Docker, Kubernetes, and cloud platforms.

## Prerequisites

### System Requirements

**Minimum Requirements:**

- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- Network: 1Gbps

**Recommended Requirements:**

- CPU: 8+ cores
- RAM: 16GB+
- Storage: 500GB+ SSD
- Network: 10Gbps

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.20+
- Helm 3.0+
- Nginx 1.18+
- PostgreSQL 13+
- Redis 6.0+

## Environment Configuration

### 1. Environment Variables

Create a `.env.production` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://stockee:password@postgres:5432/stockee
POSTGRES_USER=stockee
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=stockee

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=secure_redis_password

# API Keys
OPENAI_API_KEY=your_openai_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key
NEWS_API_KEY=your_news_api_key
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret

# Security
SECRET_KEY=your_super_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# External Services
ALPHA_VANTAGE_BASE_URL=https://www.alphavantage.co/query
ALPHA_VANTAGE_RATE_LIMIT=5
ALPHA_VANTAGE_DAILY_LIMIT=500
POLYGON_BASE_URL=https://api.polygon.io
NEWS_API_BASE_URL=https://newsapi.org/v2

# Performance
WORKERS=4
MAX_CONNECTIONS=100
KEEPALIVE_TIMEOUT=5
GRACEFUL_TIMEOUT=30

# Monitoring
PROMETHEUS_ENABLED=True
GRAFANA_ENABLED=True
SENTRY_DSN=your_sentry_dsn
```

### 2. SSL/TLS Configuration

**Generate SSL Certificates:**

```bash
# Using Let's Encrypt
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Or using self-signed certificates for testing
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

## Docker Deployment

### 1. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://stockee:${POSTGRES_PASSWORD}@postgres:5432/stockee
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  postgres:
    image: timescale/timescaledb:latest-pg13
    environment:
      - POSTGRES_USER=stockee
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=stockee
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A app.main.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://stockee:${POSTGRES_PASSWORD}@postgres:5432/stockee
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 2G

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A app.main.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://stockee:${POSTGRES_PASSWORD}@postgres:5432/stockee
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 2. Production Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream backend
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket endpoints
        location /api/ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }

        # Login rate limiting
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /usr/share/nginx/html/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 4. Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

set -e

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN=${2:-yourdomain.com}

echo "🚀 Deploying Stockee to $ENVIRONMENT environment..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Build backend
echo "📦 Building backend..."
cd backend
docker build -f Dockerfile.prod -t stockee-backend:latest .
cd ..

# Deploy with Docker Compose
echo "🐳 Deploying with Docker Compose..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head

# Health check
echo "🏥 Performing health check..."
curl -f http://localhost/api/health || exit 1

echo "✅ Deployment completed successfully!"
echo "🌐 Application is available at: https://$DOMAIN"
echo "📊 Monitoring: https://$DOMAIN:3000 (Grafana)"
echo "📈 Metrics: https://$DOMAIN:9090 (Prometheus)"
```

## Kubernetes Deployment

### 1. Namespace

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: stockee
  labels:
    name: stockee
```

### 2. ConfigMap

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: stockee-config
  namespace: stockee
data:
  DATABASE_URL: "postgresql://stockee:password@postgres:5432/stockee"
  REDIS_URL: "redis://redis:6379/0"
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  WORKERS: "4"
  MAX_CONNECTIONS: "100"
```

### 3. Secrets

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: stockee-secrets
  namespace: stockee
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded-password>
  REDIS_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  OPENAI_API_KEY: <base64-encoded-openai-key>
  ALPHA_VANTAGE_API_KEY: <base64-encoded-alpha-vantage-key>
  POLYGON_API_KEY: <base64-encoded-polygon-key>
  NEWS_API_KEY: <base64-encoded-news-key>
  BINANCE_API_KEY: <base64-encoded-binance-key>
  BINANCE_SECRET_KEY: <base64-encoded-binance-secret>
```

### 4. PostgreSQL Deployment

Create `k8s/postgres.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: stockee
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: timescale/timescaledb:latest-pg13
        env:
        - name: POSTGRES_USER
          value: "stockee"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: stockee-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          value: "stockee"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: stockee
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: stockee
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

### 5. Redis Deployment

Create `k8s/redis.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: stockee
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:alpine
        command: ["redis-server", "--requirepass", "$(REDIS_PASSWORD)"]
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: stockee-secrets
              key: REDIS_PASSWORD
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: stockee
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: stockee
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 6. Backend Deployment

Create `k8s/backend.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: stockee
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: stockee-backend:latest
        envFrom:
        - configMapRef:
            name: stockee-config
        - secretRef:
            name: stockee-secrets
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: stockee
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 7. Frontend Deployment

Create `k8s/frontend.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: stockee
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: frontend-storage
          mountPath: /usr/share/nginx/html
        resources:
          requests:
            memory: "128Mi"
            cpu: "0.1"
          limits:
            memory: "256Mi"
            cpu: "0.2"
      volumes:
      - name: frontend-storage
        configMap:
          name: frontend-config
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: stockee
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### 8. Ingress

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: stockee-ingress
  namespace: stockee
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: stockee-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /api/ws
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

### 9. Helm Chart

Create `helm/stockee/Chart.yaml`:

```yaml
apiVersion: v2
name: stockee
description: A Helm chart for Stockee trading application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

Create `helm/stockee/values.yaml`:

```yaml
replicaCount: 3

image:
  repository: stockee-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: stockee-tls
      hosts:
        - yourdomain.com

resources:
  limits:
    cpu: 2
    memory: 4Gi
  requests:
    cpu: 1
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    postgresPassword: "secure_password"
    username: "stockee"
    password: "secure_password"
    database: "stockee"
  primary:
    persistence:
      enabled: true
      size: 100Gi

redis:
  enabled: true
  auth:
    enabled: true
    password: "secure_redis_password"
  master:
    persistence:
      enabled: true
      size: 10Gi
```

## Cloud Deployment

### 1. AWS Deployment

**Using AWS EKS:**

```bash
# Create EKS cluster
eksctl create cluster --name stockee-cluster --region us-west-2 --nodes 3

# Deploy application
kubectl apply -f k8s/

# Create load balancer
kubectl apply -f k8s/aws-load-balancer.yaml
```

**Using AWS ECS:**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name stockee-cluster

# Deploy with ECS
aws ecs create-service --cluster stockee-cluster --service-name stockee-backend --task-definition stockee-backend
```

### 2. Google Cloud Deployment

**Using GKE:**

```bash
# Create GKE cluster
gcloud container clusters create stockee-cluster --zone us-central1-a --num-nodes 3

# Deploy application
kubectl apply -f k8s/

# Create ingress
kubectl apply -f k8s/gcp-ingress.yaml
```

### 3. Azure Deployment

**Using AKS:**

```bash
# Create AKS cluster
az aks create --resource-group stockee-rg --name stockee-cluster --node-count 3

# Deploy application
kubectl apply -f k8s/

# Create ingress
kubectl apply -f k8s/azure-ingress.yaml
```

## Monitoring and Logging

### 1. Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'stockee-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/api/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
```

### 2. Grafana Dashboards

Create `monitoring/grafana/dashboards/stockee.json`:

```json
{
  "dashboard": {
    "title": "Stockee Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### 3. Log Aggregation

**Using ELK Stack:**

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

## Backup and Recovery

### 1. Database Backup

Create `scripts/backup.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="stockee"
DB_USER="stockee"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h postgres -U $DB_USER -d $DB_NAME > $BACKUP_DIR/stockee_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/stockee_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/stockee_$DATE.sql.gz s3://stockee-backups/

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "stockee_*.sql.gz" -mtime +30 -delete

echo "Backup completed: stockee_$DATE.sql.gz"
```

### 2. Application Backup

Create `scripts/app-backup.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/stockee_app_$DATE.tar.gz \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=__pycache__ \
  /app

# Backup configuration
tar -czf $BACKUP_DIR/stockee_config_$DATE.tar.gz \
  /etc/nginx \
  /etc/ssl \
  /app/.env

echo "Application backup completed: stockee_app_$DATE.tar.gz"
```

## Security Hardening

### 1. Network Security

**Firewall Rules:**

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 8000/tcp   # Block direct backend access
ufw deny 5432/tcp   # Block direct database access
ufw deny 6379/tcp   # Block direct Redis access
ufw enable
```

### 2. Container Security

**Security Context:**

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE
```

### 3. Secrets Management

**Using Kubernetes Secrets:**

```bash
# Create secrets
kubectl create secret generic stockee-secrets \
  --from-literal=POSTGRES_PASSWORD=secure_password \
  --from-literal=REDIS_PASSWORD=secure_redis_password \
  --from-literal=SECRET_KEY=your_secret_key

# Or using external secret management
kubectl apply -f k8s/external-secrets.yaml
```

## Performance Tuning

### 1. Database Optimization

**PostgreSQL Configuration:**

```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2. Application Optimization

**FastAPI Configuration:**

```python
# app/core/config.py
class Settings(BaseSettings):
    # Performance settings
    workers: int = 4
    max_connections: int = 100
    keepalive_timeout: int = 5
    graceful_timeout: int = 30
    
    # Database settings
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
```

### 3. Caching Optimization

**Redis Configuration:**

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## Troubleshooting

### 1. Common Issues

**Database Connection Issues:**

```bash
# Check database connectivity
docker-compose exec backend python -c "from app.db.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check database logs
docker-compose logs postgres
```

**Redis Connection Issues:**

```bash
# Check Redis connectivity
docker-compose exec backend python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"

# Check Redis logs
docker-compose logs redis
```

**WebSocket Issues:**

```bash
# Check WebSocket connections
docker-compose exec backend python -c "from app.services.websocket_service import WebSocketService; print(WebSocketService.get_connection_count())"
```

### 2. Performance Issues

**High CPU Usage:**

```bash
# Check CPU usage
docker stats

# Check application logs
docker-compose logs backend | grep ERROR

# Check database queries
docker-compose exec postgres psql -U stockee -d stockee -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**High Memory Usage:**

```bash
# Check memory usage
docker stats

# Check for memory leaks
docker-compose exec backend python -c "import psutil; print(psutil.virtual_memory())"

# Check Redis memory usage
docker-compose exec redis redis-cli info memory
```

### 3. Log Analysis

**Application Logs:**

```bash
# View recent logs
docker-compose logs --tail=100 backend

# Follow logs in real-time
docker-compose logs -f backend

# Filter error logs
docker-compose logs backend | grep ERROR
```

**Database Logs:**

```bash
# View database logs
docker-compose logs postgres

# Check slow queries
docker-compose exec postgres psql -U stockee -d stockee -c "SELECT query, mean_time, calls FROM pg_stat_statements WHERE mean_time > 1000 ORDER BY mean_time DESC;"
```

## Maintenance

### 1. Regular Maintenance Tasks

**Daily Tasks:**

```bash
# Check system health
curl -f http://localhost/api/health

# Check disk space
df -h

# Check memory usage
free -h

# Check database size
docker-compose exec postgres psql -U stockee -d stockee -c "SELECT pg_size_pretty(pg_database_size('stockee'));"
```

**Weekly Tasks:**

```bash
# Update dependencies
docker-compose exec backend pip list --outdated

# Clean up old logs
find /var/log -name "*.log" -mtime +7 -delete

# Optimize database
docker-compose exec postgres psql -U stockee -d stockee -c "VACUUM ANALYZE;"
```

**Monthly Tasks:**

```bash
# Security updates
docker-compose pull
docker-compose up -d

# Database maintenance
docker-compose exec postgres psql -U stockee -d stockee -c "REINDEX DATABASE stockee;"

# Clean up old backups
find /backups -name "*.sql.gz" -mtime +30 -delete
```

### 2. Monitoring Alerts

**Health Check Alerts:**

```yaml
# monitoring/alerts.yml
groups:
- name: stockee
  rules:
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.instance }} is down"

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate on {{ $labels.instance }}"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time on {{ $labels.instance }}"
```

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Stockee application to various environments. Choose the deployment method that best fits your infrastructure and requirements.

Key deployment considerations:

- **Security**: Implement proper authentication, encryption, and access controls
- **Scalability**: Design for horizontal scaling and high availability
- **Monitoring**: Set up comprehensive monitoring and alerting
- **Backup**: Implement regular backup and recovery procedures
- **Performance**: Optimize for speed and efficiency
- **Maintenance**: Plan for regular maintenance and updates
