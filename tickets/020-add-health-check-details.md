# Enhance Health Check Endpoint

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready observability concerns. The assessment.md does not require health check endpoints or operational monitoring - it focuses on the core API functionality. This is a future enhancement for production deployment.

**Severity:** Low
**Category:** Observability
**Affected Files:** `app/api/main.py`

## Description

The health check endpoint returns a minimal response without useful operational information like version, uptime, or dependency status.

## Current Behavior

```python
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
```

## Expected Behavior

Health check should provide actionable information for monitoring and debugging.

## Acceptance Criteria

- [ ] Include application version
- [ ] Include start time / uptime
- [ ] Add optional deep health check for dependencies
- [ ] Return appropriate status based on dependency health
- [ ] Document health check response format

## Suggested Implementation

```python
from datetime import datetime
import time

APP_START_TIME = time.time()

class HealthResponse(pydantic.BaseModel):
    status: str
    version: str
    uptime_seconds: float
    timestamp: str

class DeepHealthResponse(HealthResponse):
    dependencies: dict[str, str]

@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=time.time() - APP_START_TIME,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/health/deep", response_model=DeepHealthResponse)
async def deep_health_check(
    service: TranscriptAnalysisService = Depends(get_transcript_service)
) -> DeepHealthResponse:
    """Deep health check that verifies dependency connectivity."""
    dependencies = {}

    # Check OpenAI connectivity (lightweight call or ping)
    try:
        # Could implement a lightweight check
        dependencies["openai"] = "healthy"
    except Exception as e:
        dependencies["openai"] = f"unhealthy: {str(e)}"

    # Check repository
    dependencies["repository"] = "healthy"  # In-memory always available

    overall_status = "healthy" if all(v == "healthy" for v in dependencies.values()) else "degraded"

    return DeepHealthResponse(
        status=overall_status,
        version="1.0.0",
        uptime_seconds=time.time() - APP_START_TIME,
        timestamp=datetime.utcnow().isoformat(),
        dependencies=dependencies
    )
```

## Kubernetes Integration

For k8s, you might want separate endpoints:
- `/health/live` - Liveness probe (app is running)
- `/health/ready` - Readiness probe (app can serve traffic)
