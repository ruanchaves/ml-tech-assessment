"""Tests for InMemoryTranscriptRepository.

This module tests the in-memory repository implementation including
thread safety and concurrent access scenarios.
"""

import asyncio
import pytest

from app.adapters.memory_repository import InMemoryTranscriptRepository
from app.domain.models import TranscriptAnalysis


class TestInMemoryTranscriptRepository:
    """Test suite for InMemoryTranscriptRepository."""

    def test_save_and_get_by_id(self) -> None:
        """Test that saved analysis can be retrieved by ID."""
        repository = InMemoryTranscriptRepository()
        analysis = TranscriptAnalysis(
            id="test-id-123",
            summary="Test summary",
            action_items=["Action 1", "Action 2"],
        )

        repository.save(analysis)
        result = repository.get_by_id("test-id-123")

        assert result is not None
        assert result.id == "test-id-123"
        assert result.summary == "Test summary"
        assert result.action_items == ["Action 1", "Action 2"]

    def test_get_by_id_not_found(self) -> None:
        """Test that get_by_id returns None for non-existent ID."""
        repository = InMemoryTranscriptRepository()

        result = repository.get_by_id("non-existent-id")

        assert result is None

    def test_save_overwrites_existing(self) -> None:
        """Test that saving with same ID overwrites existing analysis."""
        repository = InMemoryTranscriptRepository()
        analysis1 = TranscriptAnalysis(
            id="same-id",
            summary="Original summary",
            action_items=["Original action"],
        )
        analysis2 = TranscriptAnalysis(
            id="same-id",
            summary="Updated summary",
            action_items=["Updated action"],
        )

        repository.save(analysis1)
        repository.save(analysis2)
        result = repository.get_by_id("same-id")

        assert result is not None
        assert result.summary == "Updated summary"
        assert result.action_items == ["Updated action"]

    def test_multiple_analyses(self) -> None:
        """Test storing and retrieving multiple analyses."""
        repository = InMemoryTranscriptRepository()
        analyses = [
            TranscriptAnalysis(id=f"id-{i}", summary=f"Summary {i}", action_items=[])
            for i in range(5)
        ]

        for analysis in analyses:
            repository.save(analysis)

        for i, analysis in enumerate(analyses):
            result = repository.get_by_id(f"id-{i}")
            assert result is not None
            assert result.summary == f"Summary {i}"

    def test_empty_action_items(self) -> None:
        """Test saving analysis with empty action items list."""
        repository = InMemoryTranscriptRepository()
        analysis = TranscriptAnalysis(
            id="empty-actions-id",
            summary="Summary with no actions",
            action_items=[],
        )

        repository.save(analysis)
        result = repository.get_by_id("empty-actions-id")

        assert result is not None
        assert result.action_items == []


class TestInMemoryTranscriptRepositoryAsync:
    """Test suite for async operations of InMemoryTranscriptRepository."""

    @pytest.mark.asyncio
    async def test_save_async_and_get_by_id_async(self) -> None:
        """Test async save and retrieve operations."""
        repository = InMemoryTranscriptRepository()
        analysis = TranscriptAnalysis(
            id="async-test-id",
            summary="Async test summary",
            action_items=["Async action"],
        )

        await repository.save_async(analysis)
        result = await repository.get_by_id_async("async-test-id")

        assert result is not None
        assert result.id == "async-test-id"
        assert result.summary == "Async test summary"

    @pytest.mark.asyncio
    async def test_get_by_id_async_not_found(self) -> None:
        """Test async get returns None for non-existent ID."""
        repository = InMemoryTranscriptRepository()

        result = await repository.get_by_id_async("non-existent")

        assert result is None


class TestInMemoryTranscriptRepositoryConcurrency:
    """Test suite for concurrent access scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_saves_no_data_loss(self) -> None:
        """Test that concurrent saves don't lose data."""
        repository = InMemoryTranscriptRepository()

        async def save_analysis(i: int) -> None:
            analysis = TranscriptAnalysis(
                id=f"concurrent-id-{i}",
                summary=f"Concurrent summary {i}",
                action_items=[f"Action {i}"],
            )
            await repository.save_async(analysis)

        # Run 100 concurrent saves
        await asyncio.gather(*[save_analysis(i) for i in range(100)])

        # Verify all 100 analyses are stored
        for i in range(100):
            result = await repository.get_by_id_async(f"concurrent-id-{i}")
            assert result is not None, f"Analysis {i} was lost"
            assert result.summary == f"Concurrent summary {i}"

    @pytest.mark.asyncio
    async def test_concurrent_read_write(self) -> None:
        """Test concurrent read and write operations."""
        repository = InMemoryTranscriptRepository()

        # Save initial data
        initial = TranscriptAnalysis(
            id="concurrent-rw-test",
            summary="Initial",
            action_items=[],
        )
        await repository.save_async(initial)

        async def reader() -> None:
            for _ in range(50):
                result = await repository.get_by_id_async("concurrent-rw-test")
                assert result is not None
                await asyncio.sleep(0.001)

        async def writer() -> None:
            for i in range(50):
                analysis = TranscriptAnalysis(
                    id="concurrent-rw-test",
                    summary=f"Updated {i}",
                    action_items=[],
                )
                await repository.save_async(analysis)
                await asyncio.sleep(0.001)

        # Run readers and writers concurrently
        await asyncio.gather(reader(), reader(), writer())

        # Verify final state is consistent
        result = await repository.get_by_id_async("concurrent-rw-test")
        assert result is not None

    @pytest.mark.asyncio
    async def test_mixed_sync_async_access(self) -> None:
        """Test that sync and async methods access the same storage."""
        repository = InMemoryTranscriptRepository()

        # Save with sync method
        analysis = TranscriptAnalysis(
            id="mixed-access-test",
            summary="Sync saved",
            action_items=[],
        )
        repository.save(analysis)

        # Retrieve with async method
        result = await repository.get_by_id_async("mixed-access-test")
        assert result is not None
        assert result.summary == "Sync saved"

        # Update with async method
        updated = TranscriptAnalysis(
            id="mixed-access-test",
            summary="Async updated",
            action_items=[],
        )
        await repository.save_async(updated)

        # Retrieve with sync method
        result = repository.get_by_id("mixed-access-test")
        assert result is not None
        assert result.summary == "Async updated"
