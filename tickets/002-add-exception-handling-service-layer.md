# Add Exception Handling to Service Layer

**Severity:** High
**Category:** Error Handling
**Affected Files:** `app/services/transcript_service.py`

## Description

The `analyze()` and `analyze_async()` methods call `self._llm.run_completion()` without error handling. If the LLM call fails, no error recovery or logging occurs, resulting in unhandled exceptions propagating to the API layer.

## Current Behavior

```python
def analyze(self, transcript: str) -> TranscriptAnalysis:
    llm_response = self._llm.run_completion(...)  # No error handling
    # If this fails, exception propagates unhandled
```

## Expected Behavior

- Catch LLM-related exceptions
- Log errors with transcript context (without logging full transcript content for privacy)
- Provide meaningful error messages to callers
- Consider partial success handling for batch operations

## Acceptance Criteria

- [ ] Add try-except blocks around LLM calls
- [ ] Log errors with appropriate context
- [ ] Re-raise as service-layer exceptions
- [ ] Handle `analyze_batch()` partial failures gracefully
- [ ] Unit tests for exception scenarios

## Technical Notes

The `analyze_batch()` method uses `asyncio.gather()` without `return_exceptions=True`. Consider:
```python
results = await asyncio.gather(*tasks, return_exceptions=True)
# Then filter and handle exceptions separately
```
