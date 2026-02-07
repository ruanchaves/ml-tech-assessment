# Add Exception Handling to OpenAI Adapter

**Severity:** High
**Category:** Error Handling
**Affected Files:** `app/adapters/openai.py`

## Description

The `run_completion()` and `run_completion_async()` methods directly call OpenAI API without try-catch blocks. If API calls fail (rate limits, invalid API key, network issues, malformed response), the exception propagates uncaught to the caller, potentially exposing sensitive information in error messages.

## Current Behavior

```python
def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
    completion = self._client.beta.chat.completions.parse(...)  # No error handling
    return completion.choices[0].message.parsed
```

## Expected Behavior

- Catch and handle OpenAI-specific exceptions
- Log errors with appropriate detail (without exposing API keys)
- Re-raise with meaningful error messages for upstream handling
- Handle rate limits with appropriate backoff signals

## Acceptance Criteria

- [ ] Wrap API calls in try-except blocks
- [ ] Catch `openai.APIError`, `openai.RateLimitError`, `openai.APIConnectionError`
- [ ] Log errors server-side with full context
- [ ] Return sanitized error messages (no API key exposure)
- [ ] Add custom exception types for different failure modes
- [ ] Unit tests for each error scenario

## Technical Notes

Consider creating custom exception hierarchy:
```python
class LLMError(Exception): pass
class LLMRateLimitError(LLMError): pass
class LLMConnectionError(LLMError): pass
class LLMResponseError(LLMError): pass
```
