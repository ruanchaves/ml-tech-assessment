# Add Authentication to API Endpoints

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready security concerns. The assessment.md does not require authentication or authorization - it focuses on basic API functionality and architecture. This is a future enhancement for production deployment.

**Severity:** High
**Category:** Security
**Affected Files:** `app/api/main.py`, `app/api/routes.py`, `app/api/dependencies.py`

## Description

All endpoints are public with no authentication. Anyone with access to the API can analyze transcripts and consume OpenAI API quota without authorization.

## Current Behavior

```python
@router.post("/analyze")
def analyze_transcript(request: AnalyzeTranscriptRequest, ...):
    # No authentication check
```

## Expected Behavior

- Require API key or JWT token for all endpoints (except health check)
- Validate credentials before processing requests
- Return 401 Unauthorized for missing credentials
- Return 403 Forbidden for invalid credentials

## Acceptance Criteria

- [ ] Implement API key authentication via header (`X-API-Key`)
- [ ] Create API key validation dependency
- [ ] Apply authentication to all endpoints except `/health`
- [ ] Return appropriate error responses for auth failures
- [ ] Document authentication in OpenAPI spec
- [ ] Add configuration for API keys (environment variable or config file)
- [ ] Add tests for authentication scenarios

## Suggested Implementation

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@router.post("/analyze")
def analyze_transcript(
    request: AnalyzeTranscriptRequest,
    api_key: str = Depends(verify_api_key),
    ...
):
```

## Future Considerations

- JWT token support for more complex auth scenarios
- Role-based access control
- API key rotation
- Usage tracking per API key
