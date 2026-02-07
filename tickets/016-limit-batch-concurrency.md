# Limit Batch Processing Concurrency

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses production-ready performance optimization. The assessment.md only requires basic async processing for the optional batch endpoint - it does not require concurrency limiting or resource management. This is a future enhancement for production deployment.

**Severity:** Medium
**Category:** Performance
**Affected Files:** `app/services/transcript_service.py`, `app/configurations.py`

## Description

The `analyze_batch()` method creates concurrent tasks for all transcripts at once without limiting concurrency. Large batches could:
- Exhaust memory with too many concurrent tasks
- Overwhelm the OpenAI API and trigger rate limits
- Cause unpredictable performance

## Current Behavior

```python
async def analyze_batch(self, transcripts: list[str]) -> list[TranscriptAnalysis]:
    tasks = [self.analyze_async(transcript) for transcript in transcripts]
    results = await asyncio.gather(*tasks)  # All at once, no limit
    return list(results)
```

## Expected Behavior

- Limit maximum concurrent API calls
- Process batches efficiently within limits
- Allow concurrency limit to be configured

## Acceptance Criteria

- [ ] Add configurable concurrency limit (default: 5)
- [ ] Use semaphore to limit concurrent operations
- [ ] Maintain order of results matching input order
- [ ] Add configuration option for limit
- [ ] Add tests verifying concurrency behavior

## Suggested Implementation

```python
# app/configurations.py
class EnvConfigs(pydantic_settings.BaseSettings):
    # ... existing
    BATCH_CONCURRENCY_LIMIT: int = 5

# app/services/transcript_service.py
class TranscriptAnalysisService:
    def __init__(self, llm: LLm, repository: TranscriptRepository, concurrency_limit: int = 5):
        self._llm = llm
        self._repository = repository
        self._semaphore = asyncio.Semaphore(concurrency_limit)

    async def _analyze_with_limit(self, transcript: str) -> TranscriptAnalysis:
        async with self._semaphore:
            return await self.analyze_async(transcript)

    async def analyze_batch(self, transcripts: list[str]) -> list[TranscriptAnalysis]:
        tasks = [self._analyze_with_limit(transcript) for transcript in transcripts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions in results
        successful = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed: {result}")
                # Decide: skip or re-raise
            else:
                successful.append(result)

        return successful
```
