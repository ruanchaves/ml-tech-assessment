# Add Request Timeout Configuration

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready reliability concerns. The assessment.md does not require timeout configuration - it focuses on basic API functionality using the provided OpenAI adapter. This is a future enhancement for production deployment.

**Severity:** Medium
**Category:** Reliability
**Affected Files:** `app/adapters/openai.py`, `app/configurations.py`

## Description

OpenAI API calls have no timeout configuration. Requests could hang indefinitely, causing resource leaks, degraded user experience, and potential cascade failures.

## Current Behavior

```python
class OpenAIAdapter(ports.LLm):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = openai.OpenAI(api_key=api_key)  # No timeout
```

## Expected Behavior

- Configure reasonable default timeout
- Allow timeout to be customized via environment
- Timeout errors should be handled gracefully

## Acceptance Criteria

- [ ] Add `OPENAI_TIMEOUT` to configuration (default: 30 seconds)
- [ ] Pass timeout to OpenAI client initialization
- [ ] Handle timeout errors with appropriate exception
- [ ] Log timeout occurrences
- [ ] Add tests for timeout behavior

## Suggested Implementation

```python
# app/configurations.py
class EnvConfigs(pydantic_settings.BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"
    OPENAI_TIMEOUT: float = 30.0
    OPENAI_MAX_RETRIES: int = 3

# app/adapters/openai.py
class OpenAIAdapter(ports.LLm):
    def __init__(self, api_key: str, model: str, timeout: float = 30.0) -> None:
        self._model = model
        self._client = openai.OpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=0  # Handle retries ourselves for better control
        )
        self._aclient = openai.AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=0
        )
```

## Documentation

Update README with timeout configuration options.
