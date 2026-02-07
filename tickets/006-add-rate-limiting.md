# Add Rate Limiting to API Endpoints

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready security concerns. The assessment.md does not require rate limiting - it focuses on basic input validation, error handling, and code architecture. This is a future enhancement for production deployment.

**Severity:** High
**Category:** Security
**Affected Files:** `app/api/main.py`, `app/api/routes.py`, `pyproject.toml`

## Description

No rate limiting prevents abuse. Users could make unlimited API calls, causing massive OpenAI bills and potential service denial for other users.

## Current Behavior

All endpoints accept unlimited requests without throttling.

## Expected Behavior

- Limit requests per IP address or API key
- Return 429 Too Many Requests when limit exceeded
- Provide rate limit headers in responses

## Acceptance Criteria

- [ ] Add rate limiting middleware (e.g., `slowapi`)
- [ ] Configure limits per endpoint:
  - `/analyze`: 10 requests/minute
  - `/analyze/batch`: 5 requests/minute
  - `/analysis/{id}`: 60 requests/minute
- [ ] Return proper 429 responses with `Retry-After` header
- [ ] Add rate limit headers to all responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
- [ ] Document rate limits in OpenAPI spec
- [ ] Add tests for rate limiting behavior

## Suggested Implementation

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/analyze")
@limiter.limit("10/minute")
def analyze_transcript(request: Request, ...):
    ...
```

## Dependencies

Add to `pyproject.toml`:
```toml
slowapi = "^0.1.9"
```
