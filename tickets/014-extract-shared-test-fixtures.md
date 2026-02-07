# Extract Shared Test Fixtures

**Severity:** Low
**Category:** Code Quality
**Affected Files:** `tests/conftest.py`, `tests/services/test_transcript_service.py`, `tests/api/test_routes.py`

## Description

Mock implementations (`MockLLm`, `MockRepository`, `MockTranscriptService`) are defined in multiple test files, creating maintenance burden. When the interface changes, mocks must be updated in multiple places.

## Current Behavior

```python
# tests/services/test_transcript_service.py
class MockLLm(LLm):
    def __init__(self, response): ...
    def run_completion(self, ...): ...

class MockRepository(TranscriptRepository):
    def __init__(self): ...
    def save(self, ...): ...

# tests/api/test_routes.py
class MockTranscriptService:
    def __init__(self): ...
    # Duplicated mock patterns
```

## Expected Behavior

Shared mocks and fixtures should be defined once in `conftest.py` and reused across test files.

## Acceptance Criteria

- [ ] Move `MockLLm` to `tests/conftest.py`
- [ ] Move `MockRepository` to `tests/conftest.py`
- [ ] Create reusable fixtures for common test scenarios
- [ ] Update test files to use shared fixtures
- [ ] Remove duplicate mock definitions

## Suggested Implementation

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.domain.dtos import TranscriptAnalysisDTO
from app.domain.models import TranscriptAnalysis
from app.ports.llm import LLm
from app.ports.repository import TranscriptRepository


class MockLLm(LLm):
    """Reusable mock LLM for testing."""
    def __init__(self, response: TranscriptAnalysisDTO = None):
        default = TranscriptAnalysisDTO(summary="Test summary", action_items=["Action 1"])
        self._response = response or default
        self.run_completion = MagicMock(return_value=self._response)
        self.run_completion_async = AsyncMock(return_value=self._response)


class MockRepository(TranscriptRepository):
    """Reusable mock repository for testing."""
    def __init__(self):
        self._storage = {}
        self.save_calls = []

    def save(self, analysis):
        self._storage[analysis.id] = analysis
        self.save_calls.append(analysis)

    def get_by_id(self, id):
        return self._storage.get(id)


@pytest.fixture
def mock_llm():
    return MockLLm()


@pytest.fixture
def mock_repository():
    return MockRepository()


@pytest.fixture
def sample_analysis():
    return TranscriptAnalysis(
        id="test-uuid",
        summary="Test summary",
        action_items=["Action 1", "Action 2"]
    )
```
