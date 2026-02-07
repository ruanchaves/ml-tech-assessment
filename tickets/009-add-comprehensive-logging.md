# Add Comprehensive Logging

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready observability concerns. The assessment.md does not require logging infrastructure - it focuses on code readability, error handling, and testability. This is a future enhancement for production deployment.

**Severity:** Medium
**Category:** Observability
**Affected Files:** `app/adapters/openai.py`, `app/services/transcript_service.py`, `app/adapters/memory_repository.py`, `app/api/routes.py`, `app/api/main.py`

## Description

The application has no logging throughout the codebase. This makes debugging, monitoring, and incident response extremely difficult in production.

## Current Behavior

No logging statements anywhere in the application.

## Expected Behavior

- Log API requests and responses
- Log LLM calls with timing information
- Log errors with full context
- Log business operations (analysis created, retrieved)
- Support structured logging for log aggregation

## Acceptance Criteria

- [ ] Configure Python logging with appropriate format
- [ ] Add logging to OpenAI adapter:
  - Log API call start with model info
  - Log API call completion with duration
  - Log errors with exception details
- [ ] Add logging to service layer:
  - Log analysis start/completion
  - Log batch operation progress
- [ ] Add logging to repository:
  - Log save/retrieve operations at DEBUG level
- [ ] Add request logging middleware:
  - Log request method, path, status code, duration
- [ ] Configure log levels via environment variable
- [ ] Add correlation ID for request tracing

## Suggested Implementation

```python
# app/logging_config.py
import logging
import sys

def configure_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# app/adapters/openai.py
import logging
import time

logger = logging.getLogger(__name__)

def run_completion(self, ...):
    start_time = time.time()
    logger.info(f"Calling OpenAI API with model {self._model}")
    try:
        result = self._client.beta.chat.completions.parse(...)
        duration = time.time() - start_time
        logger.info(f"OpenAI API call completed in {duration:.2f}s")
        return result.choices[0].message.parsed
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}", exc_info=True)
        raise
```

## Configuration

Add to `EnvConfigs`:
```python
LOG_LEVEL: str = "INFO"
```
