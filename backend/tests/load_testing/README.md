# Load Testing for Stockee Backend

This directory contains load testing scripts and configurations for the Stockee backend application.

## Overview

The load testing suite uses Locust to simulate realistic user behavior and test the performance of various components:

- **HTTP API endpoints** - Portfolio, trading, market data, AI predictions
- **WebSocket connections** - Real-time price updates and alerts
- **Cache operations** - Redis caching performance
- **Database operations** - Query performance under load

## User Classes

### 1. StockeeUser (Default)

Simulates a typical user performing various operations:

- Portfolio management
- Trading operations
- Market data requests
- AI predictions
- Technical analysis

### 2. WebSocketOnlyUser

Focuses on WebSocket performance:

- Real-time price subscriptions
- Alert notifications
- Connection stability

### 3. CacheLoadUser

Tests cache performance:

- Cache hit/miss ratios
- Cache warming
- Cache invalidation

## Quick Start

### Prerequisites

1. Install Locust:

```bash
pip install locust
```

2. Ensure the backend is running:

```bash
cd /Users/debt0n8ram/Projects/Stocke
docker-compose up -d
```

### Basic Load Test

Run a simple load test with 10 users for 5 minutes:

```bash
cd backend/tests/load_testing
python run_load_tests.py --users 10 --run-time 5m --headless
```

### Interactive Mode

Run Locust in web UI mode:

```bash
cd backend/tests/load_testing
locust -f locustfile.py --host http://localhost:8000
```

Then open <http://localhost:8089> in your browser.

## Advanced Usage

### Custom User Classes

Test specific user behavior:

```bash
# Test WebSocket performance
python run_load_tests.py --user-class WebSocketOnlyUser --users 50 --run-time 10m

# Test cache performance
python run_load_tests.py --user-class CacheLoadUser --users 20 --run-time 5m
```

### Generate Reports

Generate detailed reports:

```bash
python run_load_tests.py \
  --users 100 \
  --run-time 10m \
  --headless \
  --html-report reports/load_test_report.html \
  --csv-report reports/load_test_stats.csv \
  --json-report reports/load_test_results.json
```

### Stress Testing

Run stress tests with high user counts:

```bash
# Gradual ramp-up
python run_load_tests.py --users 500 --spawn-rate 10 --run-time 15m

# Quick ramp-up
python run_load_tests.py --users 1000 --spawn-rate 50 --run-time 5m
```

## Test Scenarios

### 1. Normal Load

- 10-50 concurrent users
- 5-10 minute duration
- Typical user behavior

### 2. Peak Load

- 100-200 concurrent users
- 15-30 minute duration
- High trading activity

### 3. Stress Test

- 500+ concurrent users
- 5-10 minute duration
- Maximum system capacity

### 4. Endurance Test

- 50-100 concurrent users
- 1-2 hour duration
- Long-term stability

## Monitoring

### Key Metrics

1. **Response Times**
   - Average response time
   - 95th percentile response time
   - Maximum response time

2. **Throughput**
   - Requests per second
   - Successful requests
   - Failed requests

3. **Error Rates**
   - HTTP error rates
   - WebSocket connection failures
   - Timeout errors

4. **Resource Usage**
   - CPU utilization
   - Memory usage
   - Database connections
   - Cache hit rates

### Real-time Monitoring

Monitor the backend during load tests:

```bash
# Monitor Docker containers
docker stats

# Monitor logs
docker-compose logs -f backend

# Monitor database
docker-compose exec postgres psql -U stockee -d stockee -c "SELECT * FROM pg_stat_activity;"
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Load testing configuration
LOAD_TEST_HOST=http://localhost:8000
LOAD_TEST_USERS=50
LOAD_TEST_SPAWN_RATE=5
LOAD_TEST_RUN_TIME=10m

# Performance thresholds
MAX_RESPONSE_TIME_MS=1000
MAX_ERROR_RATE_PERCENT=5
MIN_THROUGHPUT_RPS=100
```

### Custom Test Data

Modify `test_data.py` to customize:

- User credentials
- Stock symbols
- Trading scenarios
- Market data requests

## Results Analysis

### HTML Report

The HTML report provides:

- Interactive charts
- Response time distributions
- Error analysis
- Request statistics

### CSV Report

The CSV report contains:

- Detailed request statistics
- Response time data
- Error information
- Performance metrics

### JSON Report

The JSON report includes:

- Machine-readable results
- Detailed metrics
- Error details
- Performance data

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure backend is running
   - Check host and port configuration
   - Verify firewall settings

2. **High Error Rates**
   - Check backend logs
   - Monitor resource usage
   - Reduce user count or spawn rate

3. **WebSocket Failures**
   - Verify WebSocket endpoint
   - Check connection limits
   - Monitor WebSocket server

4. **Database Timeouts**
   - Check database connections
   - Monitor query performance
   - Optimize database queries

### Performance Tuning

1. **Backend Optimization**
   - Increase worker processes
   - Optimize database queries
   - Implement connection pooling

2. **Database Optimization**
   - Add database indexes
   - Optimize slow queries
   - Configure connection limits

3. **Cache Optimization**
   - Increase cache memory
   - Optimize cache keys
   - Implement cache warming

## Continuous Integration

### GitHub Actions

Add load testing to CI/CD pipeline:

```yaml
name: Load Testing
on: [push, pull_request]

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install locust
          pip install -r backend/requirements.txt
      - name: Start services
        run: |
          cd backend
          docker-compose up -d
          sleep 30
      - name: Run load tests
        run: |
          cd backend/tests/load_testing
          python run_load_tests.py --users 20 --run-time 5m --headless
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: load-test-reports
          path: backend/tests/load_testing/reports/
```

## Best Practices

1. **Start Small**
   - Begin with low user counts
   - Gradually increase load
   - Monitor system behavior

2. **Monitor Resources**
   - Watch CPU and memory usage
   - Monitor database performance
   - Check cache hit rates

3. **Test Realistic Scenarios**
   - Use realistic user behavior
   - Test peak usage patterns
   - Include error scenarios

4. **Document Results**
   - Save test reports
   - Track performance trends
   - Document issues and fixes

5. **Regular Testing**
   - Run load tests regularly
   - Test after major changes
   - Monitor performance regression

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review backend logs
3. Monitor system resources
4. Consult the main project documentation
