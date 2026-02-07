# Add Error Scenario Test Coverage

**Severity:** High
**Category:** Testing
**Affected Files:** `tests/adapters/test_openai.py`, `tests/services/test_transcript_service.py`, `tests/api/test_routes.py`

## Description

The test suite lacks coverage for error scenarios. Tests only verify happy paths but don't test behavior when:
- OpenAI API fails
- Repository raises errors
- Invalid inputs cause exceptions

This means error handling bugs won't be caught until production.

## Current Behavior

- `test_openai.py`: 1 integration test, no unit tests or error tests
- `test_transcript_service.py`: Only success scenarios tested
- `test_routes.py`: Validation errors tested, but not service failures

## Expected Behavior

Comprehensive test coverage for all failure modes.

## Acceptance Criteria

### OpenAI Adapter Tests
- [ ] Test API rate limit error handling
- [ ] Test API connection error handling
- [ ] Test invalid API key error
- [ ] Test malformed response handling
- [ ] Test timeout handling

### Service Layer Tests
- [ ] Test LLM failure propagation
- [ ] Test repository save failure
- [ ] Test partial batch failure (some succeed, some fail)
- [ ] Test empty/invalid transcript handling

### API Route Tests
- [ ] Test 500 response when service fails
- [ ] Test 502 response when LLM unavailable
- [ ] Test 503 response when rate limited
- [ ] Test error response format

## Suggested Implementation

```python
# tests/adapters/test_openai.py
import pytest
from unittest.mock import MagicMock, patch
import openai

class TestOpenAIAdapterErrors:
    def test_rate_limit_error(self):
        with patch.object(openai.OpenAI, 'beta') as mock:
            mock.chat.completions.parse.side_effect = openai.RateLimitError(...)
            with pytest.raises(LLMRateLimitError):
                adapter.run_completion(...)

    def test_connection_error(self):
        # Similar pattern

# tests/services/test_transcript_service.py
class TestTranscriptServiceErrors:
    def test_analyze_handles_llm_failure(self):
        mock_llm.run_completion.side_effect = LLMError("API failed")
        with pytest.raises(AnalysisError):
            service.analyze("transcript")

    @pytest.mark.asyncio
    async def test_batch_partial_failure(self):
        # Test that successful analyses are preserved when some fail
```
