"""Tests for TranscriptAnalysisService.

This module tests the transcript analysis service including
success scenarios and error handling.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest

from app.domain.dtos import TranscriptAnalysisDTO
from app.exceptions import (
    LLMConnectionError,
    LLMRateLimitError,
    LLMError,
    TranscriptAnalysisError,
)
from app.services.transcript_service import TranscriptAnalysisService
from tests.conftest import MockLLm, MockRepository


class TestTranscriptAnalysisService:
    """Test suite for TranscriptAnalysisService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_response = TranscriptAnalysisDTO(
            summary="Test summary from LLM",
            action_items=["Action 1", "Action 2", "Action 3"],
        )
        self.mock_llm = MockLLm(self.mock_response)
        self.mock_repository = MockRepository()
        self.service = TranscriptAnalysisService(
            llm=self.mock_llm,
            repository=self.mock_repository,
        )

    def test_analyze_returns_analysis_with_id(self) -> None:
        """Test that analyze returns an analysis with a generated ID."""
        transcript = "Test transcript content"

        result = self.service.analyze(transcript)

        assert result.id is not None
        assert len(result.id) > 0

    def test_analyze_returns_summary_from_llm(self) -> None:
        """Test that analyze returns the summary from LLM response."""
        transcript = "Test transcript content"

        result = self.service.analyze(transcript)

        assert result.summary == "Test summary from LLM"

    def test_analyze_returns_action_items_from_llm(self) -> None:
        """Test that analyze returns action items from LLM response."""
        transcript = "Test transcript content"

        result = self.service.analyze(transcript)

        assert result.action_items == ["Action 1", "Action 2", "Action 3"]

    def test_analyze_calls_llm_with_correct_prompts(self) -> None:
        """Test that analyze calls LLM with formatted prompts."""
        transcript = "Test transcript content"

        self.service.analyze(transcript)

        self.mock_llm._run_completion_mock.assert_called_once()
        call_args = self.mock_llm._run_completion_mock.call_args
        # Args are passed positionally through the mock wrapper: (system_prompt, user_prompt, dto)
        assert "Test transcript content" in call_args.args[1]
        assert call_args.args[2] == TranscriptAnalysisDTO

    def test_analyze_saves_to_repository(self) -> None:
        """Test that analyze saves the result to repository."""
        transcript = "Test transcript content"

        result = self.service.analyze(transcript)

        assert len(self.mock_repository.save_calls) == 1
        saved = self.mock_repository.save_calls[0]
        assert saved.id == result.id
        assert saved.summary == result.summary
        assert saved.action_items == result.action_items

    def test_get_by_id_returns_stored_analysis(self) -> None:
        """Test that get_by_id retrieves stored analysis."""
        transcript = "Test transcript content"
        analysis = self.service.analyze(transcript)

        result = self.service.get_by_id(analysis.id)

        assert result is not None
        assert result.id == analysis.id
        assert result.summary == analysis.summary

    def test_get_by_id_returns_none_for_unknown_id(self) -> None:
        """Test that get_by_id returns None for unknown ID."""
        result = self.service.get_by_id("unknown-id")

        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_async_returns_analysis(self) -> None:
        """Test that analyze_async returns an analysis."""
        transcript = "Test transcript content"

        result = await self.service.analyze_async(transcript)

        assert result.id is not None
        assert result.summary == "Test summary from LLM"
        assert result.action_items == ["Action 1", "Action 2", "Action 3"]

    @pytest.mark.asyncio
    async def test_analyze_async_calls_async_llm_method(self) -> None:
        """Test that analyze_async uses the async LLM method."""
        transcript = "Test transcript content"

        await self.service.analyze_async(transcript)

        self.mock_llm._run_completion_async_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_batch_processes_all_transcripts(self) -> None:
        """Test that analyze_batch processes all transcripts."""
        transcripts = ["Transcript 1", "Transcript 2", "Transcript 3"]

        results = await self.service.analyze_batch(transcripts)

        assert len(results) == 3
        assert all(r.summary == "Test summary from LLM" for r in results)

    @pytest.mark.asyncio
    async def test_analyze_batch_saves_all_to_repository(self) -> None:
        """Test that analyze_batch saves all results to repository."""
        transcripts = ["Transcript 1", "Transcript 2"]

        await self.service.analyze_batch(transcripts)

        assert len(self.mock_repository.save_calls) == 2

    @pytest.mark.asyncio
    async def test_analyze_batch_returns_unique_ids(self) -> None:
        """Test that analyze_batch returns unique IDs for each result."""
        transcripts = ["Transcript 1", "Transcript 2", "Transcript 3"]

        results = await self.service.analyze_batch(transcripts)

        ids = [r.id for r in results]
        assert len(ids) == len(set(ids))  # All IDs are unique

    @pytest.mark.asyncio
    async def test_analyze_batch_empty_list(self) -> None:
        """Test that analyze_batch handles empty list."""
        results = await self.service.analyze_batch([])

        assert results == []


class TestTranscriptAnalysisServiceErrors:
    """Test suite for error handling in TranscriptAnalysisService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_llm = MockLLm()
        self.mock_repository = MockRepository()
        self.service = TranscriptAnalysisService(
            llm=self.mock_llm,
            repository=self.mock_repository,
        )

    def test_analyze_propagates_llm_connection_error(self) -> None:
        """Test that analyze propagates LLM connection errors."""
        self.mock_llm._run_completion_mock.side_effect = LLMConnectionError(
            "Connection failed"
        )

        with pytest.raises(LLMConnectionError):
            self.service.analyze("test transcript")

    def test_analyze_propagates_llm_rate_limit_error(self) -> None:
        """Test that analyze propagates LLM rate limit errors."""
        self.mock_llm._run_completion_mock.side_effect = LLMRateLimitError(
            "Rate limit exceeded"
        )

        with pytest.raises(LLMRateLimitError):
            self.service.analyze("test transcript")

    def test_analyze_wraps_unexpected_errors(self) -> None:
        """Test that analyze wraps unexpected errors in TranscriptAnalysisError."""
        self.mock_llm._run_completion_mock.side_effect = ValueError("Unexpected error")

        with pytest.raises(TranscriptAnalysisError) as exc_info:
            self.service.analyze("test transcript")

        assert "Failed to analyze transcript" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_analyze_async_propagates_llm_connection_error(self) -> None:
        """Test that analyze_async propagates LLM connection errors."""
        self.mock_llm._run_completion_async_mock.side_effect = LLMConnectionError(
            "Connection failed"
        )

        with pytest.raises(LLMConnectionError):
            await self.service.analyze_async("test transcript")

    @pytest.mark.asyncio
    async def test_analyze_async_propagates_llm_rate_limit_error(self) -> None:
        """Test that analyze_async propagates LLM rate limit errors."""
        self.mock_llm._run_completion_async_mock.side_effect = LLMRateLimitError(
            "Rate limit exceeded"
        )

        with pytest.raises(LLMRateLimitError):
            await self.service.analyze_async("test transcript")

    @pytest.mark.asyncio
    async def test_analyze_async_wraps_unexpected_errors(self) -> None:
        """Test that analyze_async wraps unexpected errors."""
        self.mock_llm._run_completion_async_mock.side_effect = ValueError("Unexpected")

        with pytest.raises(TranscriptAnalysisError):
            await self.service.analyze_async("test transcript")

    @pytest.mark.asyncio
    async def test_analyze_batch_propagates_first_error(self) -> None:
        """Test that analyze_batch propagates errors from failed analyses."""
        self.mock_llm._run_completion_async_mock.side_effect = LLMConnectionError(
            "Connection failed"
        )

        with pytest.raises(LLMConnectionError):
            await self.service.analyze_batch(["t1", "t2"])

    def test_analyze_does_not_save_on_llm_error(self) -> None:
        """Test that analyze doesn't save to repository when LLM fails."""
        self.mock_llm._run_completion_mock.side_effect = LLMError("LLM failed")

        with pytest.raises(LLMError):
            self.service.analyze("test transcript")

        assert len(self.mock_repository.save_calls) == 0

    @pytest.mark.asyncio
    async def test_analyze_async_does_not_save_on_llm_error(self) -> None:
        """Test that analyze_async doesn't save to repository when LLM fails."""
        self.mock_llm._run_completion_async_mock.side_effect = LLMError("LLM failed")

        with pytest.raises(LLMError):
            await self.service.analyze_async("test transcript")

        assert len(self.mock_repository.save_calls) == 0
