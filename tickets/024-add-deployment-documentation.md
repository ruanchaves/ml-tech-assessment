# Add Deployment Documentation

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production deployment concerns. The assessment.md focuses on code architecture and functionality, not deployment procedures or operational documentation. This is a future enhancement for production readiness.

**Severity:** Medium
**Category:** Documentation
**Affected Files:** `README.md`, `docs/deployment.md`

## Description

The README covers local development and Docker basics but lacks deployment guidelines, scaling recommendations, production configuration, and operational procedures.

## Current Behavior

README has:
- Quick start with Docker
- Local development setup
- API documentation
- Basic test instructions

Missing:
- Production deployment guide
- Scaling considerations
- Monitoring and alerting setup
- Backup and recovery (for persistent storage)
- Security hardening

## Expected Behavior

Comprehensive documentation for production deployment.

## Acceptance Criteria

- [ ] Create `docs/` directory
- [ ] Add production deployment guide
- [ ] Document environment variables for production
- [ ] Add scaling recommendations
- [ ] Document monitoring integration
- [ ] Add security checklist
- [ ] Document backup procedures (if persistent storage added)

## Suggested Content

```markdown
# docs/deployment.md

## Production Deployment Guide

### Prerequisites
- Docker and Docker Compose
- OpenAI API key with sufficient quota
- (Optional) Reverse proxy (nginx, traefik)
- (Optional) Monitoring stack (Prometheus, Grafana)

### Environment Configuration

| Variable | Description | Production Value |
|----------|-------------|------------------|
| OPENAI_API_KEY | API key | (from secrets manager) |
| OPENAI_MODEL | Model to use | gpt-4o-2024-08-06 |
| LOG_LEVEL | Logging verbosity | INFO |
| WORKERS | Uvicorn workers | 4 |

### Docker Production Configuration

```yaml
# docker-compose.prod.yml
services:
  api:
    build: .
    command: uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    environment:
      - LOG_LEVEL=INFO
```

### Scaling Recommendations

1. **Horizontal Scaling**: Run multiple container instances behind load balancer
2. **Connection Pooling**: OpenAI client handles this internally
3. **Rate Limiting**: Configure based on OpenAI tier limits
4. **Memory**: ~256MB per worker, scale based on batch sizes

### Monitoring

Recommended metrics to track:
- Request latency (p50, p95, p99)
- Error rate by endpoint
- OpenAI API latency
- Memory usage per worker

### Security Checklist

- [ ] API key stored in secrets manager
- [ ] HTTPS enabled via reverse proxy
- [ ] Rate limiting configured
- [ ] Authentication enabled
- [ ] Logs don't contain sensitive data
- [ ] Container runs as non-root user
```
