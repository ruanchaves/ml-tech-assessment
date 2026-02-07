# Add Concurrent Access Tests

**Severity:** Medium
**Category:** Testing
**Affected Files:** `tests/adapters/test_memory_repository.py`, `tests/services/test_transcript_service.py`

## Description

No tests verify behavior under concurrent access. Thread safety issues in the in-memory repository won't be caught by the current test suite.

## Current Behavior

All tests run sequentially with no concurrent operations.

## Expected Behavior

Tests should verify data integrity when multiple operations happen simultaneously.

## Acceptance Criteria

- [ ] Add concurrent write test for repository
- [ ] Add concurrent read/write test for repository
- [ ] Add concurrent batch analysis test for service
- [ ] Verify no data loss or corruption under load
- [ ] Test with realistic concurrency levels

## Suggested Implementation

```python
# tests/adapters/test_memory_repository.py
import asyncio
import pytest

class TestInMemoryRepositoryConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_saves_no_data_loss(self):
        repository = InMemoryTranscriptRepository()

        async def save_analysis(i: int):
            analysis = TranscriptAnalysis(
                id=f"id-{i}",
                summary=f"Summary {i}",
                action_items=[]
            )
            await repository.save(analysis)

        # Run 100 concurrent saves
        await asyncio.gather(*[save_analysis(i) for i in range(100)])

        # Verify all 100 analyses are stored
        for i in range(100):
            result = await repository.get_by_id(f"id-{i}")
            assert result is not None
            assert result.summary == f"Summary {i}"

    @pytest.mark.asyncio
    async def test_concurrent_read_write(self):
        repository = InMemoryTranscriptRepository()
        # Save initial data
        await repository.save(TranscriptAnalysis(id="test", summary="v1", action_items=[]))

        async def reader():
            for _ in range(50):
                result = await repository.get_by_id("test")
                assert result is not None
                await asyncio.sleep(0.001)

        async def writer():
            for i in range(50):
                await repository.save(TranscriptAnalysis(id="test", summary=f"v{i}", action_items=[]))
                await asyncio.sleep(0.001)

        # Run readers and writers concurrently
        await asyncio.gather(reader(), reader(), writer())
```
