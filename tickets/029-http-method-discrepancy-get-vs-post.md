# HTTP Method Discrepancy: GET vs POST for Analyze Endpoint

**Severity:** Medium
**Category:** API Compliance
**Affected Files:** `app/api/routes.py`

## Description

The `assessment.md` explicitly states:

> "Create an HTTP endpoint (e.g., using FastAPI or Flask) that **accepts GET requests** containing a plain text transcript."

However, the current implementation uses `POST /analyze` instead of `GET`.

## Current Behavior

```python
@router.post("/analyze")  # Uses POST
def analyze_transcript(request: AnalyzeTranscriptRequest, ...):
```

## Assessment Requirement

The assessment explicitly requires a **GET** request for the analyze endpoint.

## Analysis

There are two perspectives on this:

### Option A: Change to GET (Literal Compliance)
- Matches assessment requirement exactly
- GET with request body is technically allowed by HTTP spec
- However, GET with body is discouraged by REST conventions
- FastAPI/OpenAPI doesn't fully support GET with request body in Swagger UI

### Option B: Keep POST (Semantic Correctness)
- POST is the correct HTTP method for operations that submit data for processing
- GET should be idempotent and cacheable - analysis is neither
- Industry standard for similar APIs (e.g., OpenAI, Claude) use POST
- Better Swagger/OpenAPI documentation support

## Acceptance Criteria

Decide on one approach:

### If changing to GET:
- [ ] Change `@router.post` to `@router.get`
- [ ] Use query parameter instead of request body: `GET /analyze?transcript=...`
- [ ] Update tests to use GET method
- [ ] Note: Long transcripts may exceed URL length limits

### If keeping POST (recommended):
- [ ] Document the deviation from assessment wording
- [ ] Add comment explaining why POST is more appropriate
- [ ] Consider this a conscious design decision

## Recommendation

**Keep POST** and document the reasoning. The assessment likely intended "accepts requests" rather than specifically "GET requests", as:
1. Sending transcript content in a GET request body violates REST conventions
2. Query parameters have length limits (~2000 chars) unsuitable for transcripts
3. All major LLM APIs use POST for similar operations

Add a comment in the code:
```python
# Note: Assessment mentions GET, but POST is used because:
# 1. POST is semantically correct for submitting data for processing
# 2. GET with body is discouraged and poorly supported
# 3. Query params have length limits unsuitable for transcripts
@router.post("/analyze")
```
