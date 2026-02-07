# Fix Thread Safety in Memory Repository

**Severity:** High
**Category:** Concurrency
**Affected Files:** `app/adapters/memory_repository.py`, `app/ports/repository.py`

## Description

The `_storage` dictionary in `InMemoryTranscriptRepository` is not thread-safe. In concurrent scenarios (e.g., batch processing with `asyncio.gather()`), multiple coroutines may simultaneously read/write to `_storage`, causing race conditions or data loss.

## Current Behavior

```python
class InMemoryTranscriptRepository(TranscriptRepository):
    def __init__(self) -> None:
        self._storage: dict[str, TranscriptAnalysis] = {}  # Not thread-safe

    def save(self, analysis: TranscriptAnalysis) -> None:
        self._storage[analysis.id] = analysis  # Race condition possible
```

## Expected Behavior

Repository operations should be atomic and safe for concurrent access from multiple coroutines or threads.

## Acceptance Criteria

- [ ] Add asyncio lock for async context safety
- [ ] Ensure all storage operations are atomic
- [ ] Add concurrent access tests
- [ ] Document thread-safety guarantees
- [ ] Consider making repository methods async

## Suggested Implementation

```python
from asyncio import Lock

class InMemoryTranscriptRepository(TranscriptRepository):
    def __init__(self) -> None:
        self._storage: dict[str, TranscriptAnalysis] = {}
        self._lock = Lock()

    async def save(self, analysis: TranscriptAnalysis) -> None:
        async with self._lock:
            self._storage[analysis.id] = analysis

    async def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        async with self._lock:
            return self._storage.get(id)
```

## Technical Notes

This change may require updating the repository port interface to use async methods, which would be a breaking change affecting the service layer.
