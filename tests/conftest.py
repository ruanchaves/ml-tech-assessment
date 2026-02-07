"""Shared test fixtures and mocks.

This module provides reusable fixtures and mock implementations
for testing across the application.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.domain.dtos import TranscriptAnalysisDTO
from app.domain.models import TranscriptAnalysis
from app.ports.llm import LLm
from app.ports.repository import TranscriptRepository


class MockLLm(LLm):
    """Mock LLM implementation for testing.

    Provides configurable responses and call tracking for unit tests.
    """

    def __init__(self, response: TranscriptAnalysisDTO | None = None) -> None:
        """Initialize the mock with optional custom response.

        Args:
            response: Optional custom response. Defaults to a standard test response.
        """
        default = TranscriptAnalysisDTO(
            summary="Test summary from LLM",
            action_items=["Action 1", "Action 2", "Action 3"],
        )
        self._response = response or default
        self._run_completion_mock = MagicMock(return_value=self._response)
        self._run_completion_async_mock = AsyncMock(return_value=self._response)

    def run_completion(
        self, system_prompt: str, user_prompt: str, dto: type
    ) -> TranscriptAnalysisDTO:
        """Execute a synchronous completion request (mock implementation)."""
        return self._run_completion_mock(system_prompt, user_prompt, dto)

    async def run_completion_async(
        self, system_prompt: str, user_prompt: str, dto: type
    ) -> TranscriptAnalysisDTO:
        """Execute an asynchronous completion request (mock implementation)."""
        return await self._run_completion_async_mock(system_prompt, user_prompt, dto)


class MockRepository(TranscriptRepository):
    """Mock repository implementation for testing.

    Provides in-memory storage with call tracking for unit tests.
    """

    def __init__(self) -> None:
        """Initialize the mock repository."""
        self._storage: dict[str, TranscriptAnalysis] = {}
        self.save_calls: list[TranscriptAnalysis] = []

    def save(self, analysis: TranscriptAnalysis) -> None:
        """Save analysis and track the call."""
        self._storage[analysis.id] = analysis
        self.save_calls.append(analysis)

    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve analysis by ID."""
        return self._storage.get(id)

    async def save_async(self, analysis: TranscriptAnalysis) -> None:
        """Async save operation."""
        self._storage[analysis.id] = analysis
        self.save_calls.append(analysis)

    async def get_by_id_async(self, id: str) -> TranscriptAnalysis | None:
        """Async get by ID operation."""
        return self._storage.get(id)


@pytest.fixture
def mock_llm() -> MockLLm:
    """Create a mock LLM fixture."""
    return MockLLm()


@pytest.fixture
def mock_llm_with_custom_response() -> type[MockLLm]:
    """Factory fixture for creating mock LLM with custom response."""
    return MockLLm


@pytest.fixture
def mock_repository() -> MockRepository:
    """Create a mock repository fixture."""
    return MockRepository()


@pytest.fixture
def sample_transcript() -> str:
    """Sample transcript for testing."""
    return """
    John: Let's discuss the Q4 roadmap.
    Sarah: I think we should focus on user retention.
    John: Good point. What specific metrics should we track?
    Sarah: Monthly active users and churn rate would be key.
    John: Let's set up a meeting next week to define our targets.
    """


@pytest.fixture
def empty_transcript() -> str:
    """Empty transcript for validation testing."""
    return ""


@pytest.fixture
def sample_summary() -> str:
    """Sample summary for testing."""
    return "Discussion about Q4 roadmap focusing on user retention metrics."


@pytest.fixture
def sample_action_items() -> list[str]:
    """Sample action items for testing."""
    return [
        "Schedule meeting to define Q4 targets",
        "Set up tracking for MAU and churn rate",
    ]


@pytest.fixture
def sample_analysis() -> TranscriptAnalysis:
    """Sample analysis result for testing."""
    return TranscriptAnalysis(
        id="test-uuid-12345",
        summary="Test summary",
        action_items=["Action 1", "Action 2"],
    )


@pytest.fixture
def sample_dto() -> TranscriptAnalysisDTO:
    """Sample DTO for testing."""
    return TranscriptAnalysisDTO(
        summary="Test summary from LLM",
        action_items=["Action 1", "Action 2"],
    )
