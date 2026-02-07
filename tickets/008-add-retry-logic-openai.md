# Add Retry Logic for OpenAI API Calls

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready reliability concerns. The assessment.md does not require retry logic or resilience patterns - it focuses on basic API functionality and invoking the provided OpenAI adapter. This is a future enhancement for production deployment.

**Severity:** High
**Category:** Reliability
**Affected Files:** `app/adapters/openai.py`, `pyproject.toml`

## Description

OpenAI API calls have no retry logic. Transient failures (network glitches, brief service interruptions, rate limits) cause immediate failure instead of graceful retry.

## Current Behavior

```python
def run_completion(self, ...):
    completion = self._client.beta.chat.completions.parse(...)  # Single attempt
    return completion.choices[0].message.parsed
```

## Expected Behavior

- Retry failed requests with exponential backoff
- Respect rate limit headers for backoff timing
- Limit total retry attempts
- Log retry attempts

## Acceptance Criteria

- [ ] Implement retry with exponential backoff
- [ ] Configure max retry attempts (default: 3)
- [ ] Configure initial delay and max delay
- [ ] Handle rate limit errors with appropriate backoff
- [ ] Log retry attempts with attempt number
- [ ] Add timeout configuration to prevent hanging requests
- [ ] Add tests for retry behavior

## Suggested Implementation

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai

class OpenAIAdapter(ports.LLm):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIConnectionError, openai.RateLimitError))
    )
    def run_completion(self, system_prompt: str, user_prompt: str, dto):
        # ... existing implementation
```

## Dependencies

Add to `pyproject.toml`:
```toml
tenacity = "^8.2.0"
```

## Configuration

Add to `EnvConfigs`:
```python
OPENAI_TIMEOUT: int = 30
OPENAI_MAX_RETRIES: int = 3
```
