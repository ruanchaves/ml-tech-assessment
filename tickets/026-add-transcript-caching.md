# Add Transcript Content Caching

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses performance optimization. The assessment.md does not require caching - it focuses on basic API functionality and architecture. This is a future enhancement for production cost optimization.

**Severity:** Low
**Category:** Performance
**Affected Files:** `app/services/transcript_service.py`, `app/adapters/`

## Description

Identical transcripts are analyzed multiple times, wasting API calls and money. A caching layer could store results for duplicate content.

## Current Behavior

Every call to `analyze()` makes a new OpenAI API call, even if the same transcript was analyzed before.

## Expected Behavior

- Cache analysis results by transcript content hash
- Return cached result for identical transcripts
- Allow cache to be bypassed when needed
- Configure cache TTL

## Acceptance Criteria

- [ ] Implement content-based caching using hash of transcript
- [ ] Add cache TTL configuration
- [ ] Add cache bypass option in API request
- [ ] Track cache hit/miss metrics
- [ ] Add tests for caching behavior

## Suggested Implementation

```python
# app/services/transcript_service.py
import hashlib
from functools import lru_cache

class TranscriptAnalysisService:
    def __init__(self, llm: LLm, repository: TranscriptRepository,
                 cache_enabled: bool = True):
        self._llm = llm
        self._repository = repository
        self._cache_enabled = cache_enabled
        self._cache: dict[str, TranscriptAnalysis] = {}

    def _hash_transcript(self, transcript: str) -> str:
        """Generate hash of transcript content."""
        return hashlib.sha256(transcript.encode()).hexdigest()

    def analyze(self, transcript: str, use_cache: bool = True) -> TranscriptAnalysis:
        if self._cache_enabled and use_cache:
            cache_key = self._hash_transcript(transcript)
            if cache_key in self._cache:
                logger.info(f"Cache hit for transcript hash {cache_key[:8]}")
                # Return copy with new ID for unique tracking
                cached = self._cache[cache_key]
                return TranscriptAnalysis(
                    id=str(uuid.uuid4()),
                    summary=cached.summary,
                    action_items=cached.action_items.copy()
                )

        # Normal analysis
        result = self._do_analyze(transcript)

        if self._cache_enabled:
            cache_key = self._hash_transcript(transcript)
            self._cache[cache_key] = result
            logger.info(f"Cached result for transcript hash {cache_key[:8]}")

        return result
```

## API Extension

```python
class AnalyzeTranscriptRequest(pydantic.BaseModel):
    transcript: str
    use_cache: bool = True  # Allow client to bypass cache
```

## Future Considerations

- Use Redis for distributed caching
- Add cache eviction policy (LRU, TTL-based)
- Add cache statistics endpoint
