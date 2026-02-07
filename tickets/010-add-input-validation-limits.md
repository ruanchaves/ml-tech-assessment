# Add Input Validation Limits

**Severity:** Medium
**Category:** Security / Cost Control
**Affected Files:** `app/api/schemas.py`

## Description

Input validation only checks for non-empty transcripts but has no maximum length limits. Users could submit multi-megabyte transcripts or thousands of items in batch requests, causing:
- Token limit errors from OpenAI
- Excessive API costs
- Memory exhaustion
- Denial of service

## Current Behavior

```python
class AnalyzeTranscriptRequest(pydantic.BaseModel):
    transcript: str = pydantic.Field(..., min_length=1)  # No max_length

class BatchAnalyzeRequest(pydantic.BaseModel):
    transcripts: list[str] = pydantic.Field(..., min_length=1)  # No max items
```

## Expected Behavior

- Limit transcript length to reasonable maximum
- Limit batch size to prevent resource exhaustion
- Validate analysis ID format

## Acceptance Criteria

- [ ] Add `max_length` to transcript field (e.g., 100,000 characters)
- [ ] Add `max_length` to batch transcripts list (e.g., 10 items)
- [ ] Add individual transcript length validation in batch
- [ ] Add UUID format validation for analysis_id path parameter
- [ ] Return clear error messages for validation failures
- [ ] Update OpenAPI documentation with limits
- [ ] Add tests for validation edge cases

## Suggested Implementation

```python
class AnalyzeTranscriptRequest(pydantic.BaseModel):
    transcript: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=100000,
        description="Transcript text (max 100,000 characters)"
    )

class BatchAnalyzeRequest(pydantic.BaseModel):
    transcripts: list[str] = pydantic.Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of transcripts (max 10 items)"
    )

    @pydantic.field_validator("transcripts")
    @classmethod
    def validate_transcript_lengths(cls, v):
        for i, t in enumerate(v):
            if len(t) > 100000:
                raise ValueError(f"Transcript at index {i} exceeds 100,000 characters")
        return v
```

For path parameters:
```python
from fastapi import Path

@router.get("/analysis/{analysis_id}")
def get_analysis(
    analysis_id: str = Path(..., regex=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
):
```
