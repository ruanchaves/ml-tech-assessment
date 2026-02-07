# Add Circuit Breaker Pattern

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready resilience patterns. The assessment.md does not require fault tolerance patterns - it focuses on basic API functionality using the provided OpenAI adapter. This is a future enhancement for production reliability.

**Severity:** Medium
**Category:** Reliability
**Affected Files:** `app/adapters/openai.py`, `pyproject.toml`

## Description

If the OpenAI service is down or experiencing issues, all requests will fail without graceful degradation. A circuit breaker would prevent cascade failures and provide better user experience during outages.

## Current Behavior

Every request attempts to call OpenAI, even if the last 100 requests failed.

## Expected Behavior

- Stop calling OpenAI after consecutive failures
- Return fast failure response while circuit is open
- Periodically test if service is recovered
- Reset circuit after successful calls

## Acceptance Criteria

- [ ] Implement circuit breaker using `pybreaker` or similar
- [ ] Configure failure threshold (e.g., 5 failures)
- [ ] Configure reset timeout (e.g., 30 seconds)
- [ ] Return appropriate error when circuit is open
- [ ] Log circuit state changes
- [ ] Add tests for circuit breaker behavior

## Suggested Implementation

```python
# app/adapters/openai.py
import pybreaker
import logging

logger = logging.getLogger(__name__)

# Circuit breaker configuration
openai_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    listeners=[pybreaker.CircuitBreakerListener()]
)

class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        logger.warning(f"Circuit breaker state: {old_state.name} -> {new_state.name}")

class OpenAIAdapter(ports.LLm):
    @openai_breaker
    def run_completion(self, system_prompt: str, user_prompt: str, dto):
        try:
            completion = self._client.beta.chat.completions.parse(...)
            return completion.choices[0].message.parsed
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection failed: {e}")
            raise  # Will trigger circuit breaker

    @openai_breaker
    async def run_completion_async(self, ...):
        # Same pattern for async
```

## Dependencies

Add to `pyproject.toml`:
```toml
pybreaker = "^1.2.0"
```

## Error Handling

When circuit is open:
```python
from pybreaker import CircuitBreakerError

try:
    result = adapter.run_completion(...)
except CircuitBreakerError:
    raise LLMUnavailableError("OpenAI service temporarily unavailable")
```

## Monitoring

Export circuit breaker state as metric:
- `circuit_breaker_state` (open/closed/half-open)
- `circuit_breaker_failures_total`
- `circuit_breaker_successes_total`
