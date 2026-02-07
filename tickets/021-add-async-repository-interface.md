# Add Async Methods to Repository Interface

**Severity:** Medium
**Category:** Architecture
**Affected Files:** `app/ports/repository.py`, `app/adapters/memory_repository.py`, `app/services/transcript_service.py`

## Description

The repository interface has synchronous methods but they're called from async context. This architectural mismatch could cause issues with future database implementations that require async I/O.

## Current Behavior

```python
# app/ports/repository.py
class TranscriptRepository(ABC):
    @abstractmethod
    def save(self, analysis: TranscriptAnalysis) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        pass
```

## Expected Behavior

Repository interface should support async operations for compatibility with async database drivers.

## Acceptance Criteria

- [ ] Add async method signatures to repository port
- [ ] Update in-memory adapter with async implementations
- [ ] Update service to use async repository methods
- [ ] Maintain backward compatibility for sync usage
- [ ] Update tests for async repository

## Suggested Implementation

```python
# app/ports/repository.py
class TranscriptRepository(ABC):
    @abstractmethod
    def save(self, analysis: TranscriptAnalysis) -> None:
        """Synchronous save operation."""
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        """Synchronous get operation."""
        pass

    @abstractmethod
    async def save_async(self, analysis: TranscriptAnalysis) -> None:
        """Asynchronous save operation."""
        pass

    @abstractmethod
    async def get_by_id_async(self, id: str) -> TranscriptAnalysis | None:
        """Asynchronous get operation."""
        pass

# app/adapters/memory_repository.py
class InMemoryTranscriptRepository(TranscriptRepository):
    async def save_async(self, analysis: TranscriptAnalysis) -> None:
        async with self._lock:
            self._storage[analysis.id] = analysis

    async def get_by_id_async(self, id: str) -> TranscriptAnalysis | None:
        async with self._lock:
            return self._storage.get(id)
```

## Migration Path

1. Add async methods alongside existing sync methods
2. Update async service methods to use async repository methods
3. Keep sync methods for backward compatibility
4. Eventually deprecate sync methods if not needed
