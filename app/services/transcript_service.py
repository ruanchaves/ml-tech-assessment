"""Transcript analysis service.

This module provides the application service for transcript analysis,
orchestrating the workflow between LLM and repository ports.
"""

import asyncio
import uuid

from app.domain.dtos import TranscriptAnalysisDTO
from app.domain.models import TranscriptAnalysis
from app.exceptions import LLMError, TranscriptAnalysisError
from app.ports.llm import LLm
from app.ports.repository import TranscriptRepository
from app.prompts import RAW_USER_PROMPT, SYSTEM_PROMPT


class TranscriptAnalysisService:
    """Application service for transcript analysis.

    Orchestrates the analysis workflow by coordinating between the LLM port
    and the repository port. This service contains the core business logic
    for analyzing transcripts and managing analysis results.
    """

    def __init__(self, llm: LLm, repository: TranscriptRepository) -> None:
        """Initialize the service with required dependencies.

        Args:
            llm: The LLM port implementation for running analysis.
            repository: The repository port implementation for storage.
        """
        self._llm = llm
        self._repository = repository

    def _prepare_user_prompt(self, transcript: str) -> str:
        """Prepare the user prompt with transcript content.

        Args:
            transcript: The plain text transcript to include in the prompt.

        Returns:
            The formatted user prompt string.
        """
        return RAW_USER_PROMPT.format(transcript=transcript)

    def _create_analysis(self, llm_response: TranscriptAnalysisDTO) -> TranscriptAnalysis:
        """Create a TranscriptAnalysis from LLM response.

        Args:
            llm_response: The DTO returned by the LLM.

        Returns:
            A new TranscriptAnalysis with generated ID.
        """
        return TranscriptAnalysis(
            id=str(uuid.uuid4()),
            summary=llm_response.summary,
            action_items=llm_response.action_items,
        )

    def analyze(self, transcript: str) -> TranscriptAnalysis:
        """Analyze a transcript and store the result.

        Args:
            transcript: The plain text transcript to analyze.

        Returns:
            The analysis result containing ID, summary, and action items.

        Raises:
            LLMError: When the LLM call fails.
            TranscriptAnalysisError: When analysis fails for other reasons.
        """
        try:
            user_prompt = self._prepare_user_prompt(transcript)
            llm_response: TranscriptAnalysisDTO = self._llm.run_completion(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                dto=TranscriptAnalysisDTO,
            )
            analysis = self._create_analysis(llm_response)
            self._repository.save(analysis)
            return analysis
        except LLMError:
            raise
        except Exception as e:
            raise TranscriptAnalysisError(
                f"Failed to analyze transcript: {str(e)}", e
            ) from e

    async def analyze_async(self, transcript: str) -> TranscriptAnalysis:
        """Analyze a transcript asynchronously and store the result.

        Args:
            transcript: The plain text transcript to analyze.

        Returns:
            The analysis result containing ID, summary, and action items.

        Raises:
            LLMError: When the LLM call fails.
            TranscriptAnalysisError: When analysis fails for other reasons.
        """
        try:
            user_prompt = self._prepare_user_prompt(transcript)
            llm_response: TranscriptAnalysisDTO = await self._llm.run_completion_async(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                dto=TranscriptAnalysisDTO,
            )
            analysis = self._create_analysis(llm_response)
            await self._repository.save_async(analysis)
            return analysis
        except LLMError:
            raise
        except Exception as e:
            raise TranscriptAnalysisError(
                f"Failed to analyze transcript: {str(e)}", e
            ) from e

    async def analyze_batch(
        self, transcripts: list[str]
    ) -> list[TranscriptAnalysis]:
        """Analyze multiple transcripts concurrently.

        Uses asyncio to process all transcripts in parallel without blocking.
        If any individual analysis fails, the error is propagated.

        Args:
            transcripts: List of plain text transcripts to analyze.

        Returns:
            List of analysis results in the same order as input transcripts.

        Raises:
            LLMError: When any LLM call fails.
            TranscriptAnalysisError: When any analysis fails.
        """
        if not transcripts:
            return []

        tasks = [self.analyze_async(transcript) for transcript in transcripts]
        results = await asyncio.gather(*tasks)
        return list(results)

    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve a transcript analysis by its ID.

        Args:
            id: The unique identifier of the analysis.

        Returns:
            The transcript analysis if found, None otherwise.
        """
        return self._repository.get_by_id(id)

    async def get_by_id_async(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve a transcript analysis by its ID asynchronously.

        Args:
            id: The unique identifier of the analysis.

        Returns:
            The transcript analysis if found, None otherwise.
        """
        return await self._repository.get_by_id_async(id)
