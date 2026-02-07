# Add Exception Handling to API Routes

**Severity:** Medium
**Category:** Error Handling
**Affected Files:** `app/api/routes.py`, `app/api/main.py`

## Description

The `analyze_transcript()` and `analyze_batch()` endpoints call service methods without catching exceptions. API errors result in unhandled 500 errors with generic messages, providing poor developer experience and potentially leaking implementation details.

## Current Behavior

```python
@router.post("/analyze")
def analyze_transcript(request: AnalyzeTranscriptRequest, service = Depends(...)):
    analysis = service.analyze(request.transcript)  # No error handling
    return TranscriptAnalysisResponse(...)
```

## Expected Behavior

- Catch service-layer exceptions
- Return appropriate HTTP status codes (500, 502, 503)
- Provide structured error responses
- Log errors for debugging

## Acceptance Criteria

- [ ] Add FastAPI exception handlers for custom exceptions
- [ ] Return structured `ErrorResponse` for all error cases
- [ ] Map LLM errors to appropriate HTTP status codes:
  - Rate limit → 503 Service Unavailable
  - Connection error → 502 Bad Gateway
  - Other errors → 500 Internal Server Error
- [ ] Add correlation IDs for error tracking
- [ ] Update OpenAPI documentation with error responses
- [ ] Integration tests for error responses

## Technical Notes

Use FastAPI exception handlers:
```python
@app.exception_handler(LLMRateLimitError)
async def rate_limit_handler(request: Request, exc: LLMRateLimitError):
    return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable"})
```
