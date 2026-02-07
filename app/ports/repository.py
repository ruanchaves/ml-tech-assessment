"""Repository port interface.

This module defines the abstract interface for transcript analysis storage.
All repository implementations must adhere to this contract.
"""

from abc import ABC, abstractmethod

from app.domain.models import TranscriptAnalysis


class TranscriptRepository(ABC):
    """Abstract base class for transcript analysis storage.

    Defines the contract for storing and retrieving transcript analyses.
    Implementations can use any storage mechanism (in-memory, database, etc.)
    while adhering to this interface.

    Both synchronous and asynchronous methods are defined to support
    different usage contexts.
    """

    @abstractmethod
    def save(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis synchronously.

        Args:
            analysis: The transcript analysis to store.

        Raises:
            RepositoryError: When the save operation fails.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve a transcript analysis by its ID synchronously.

        Args:
            id: The unique identifier of the analysis.

        Returns:
            The transcript analysis if found, None otherwise.

        Raises:
            RepositoryError: When the retrieval operation fails.
        """
        pass

    @abstractmethod
    async def save_async(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis asynchronously.

        Args:
            analysis: The transcript analysis to store.

        Raises:
            RepositoryError: When the save operation fails.
        """
        pass

    @abstractmethod
    async def get_by_id_async(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve a transcript analysis by its ID asynchronously.

        Args:
            id: The unique identifier of the analysis.

        Returns:
            The transcript analysis if found, None otherwise.

        Raises:
            RepositoryError: When the retrieval operation fails.
        """
        pass
