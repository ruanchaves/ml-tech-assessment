"""In-memory repository implementation.

This module provides a thread-safe in-memory implementation of the
TranscriptRepository port interface.
"""

import asyncio
import threading

from app.domain.models import TranscriptAnalysis
from app.ports.repository import TranscriptRepository


class InMemoryTranscriptRepository(TranscriptRepository):
    """Thread-safe in-memory implementation of TranscriptRepository.

    Stores transcript analyses in a dictionary with proper locking for
    concurrent access. Suitable for development and testing.
    Data is lost when the application restarts.
    """

    def __init__(self) -> None:
        """Initialize the repository with empty storage and locks."""
        self._storage: dict[str, TranscriptAnalysis] = {}
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def save(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis to memory (thread-safe).

        Args:
            analysis: The transcript analysis to store.
        """
        with self._lock:
            self._storage[analysis.id] = analysis

    def get_by_id(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve a transcript analysis by its ID (thread-safe).

        Args:
            id: The unique identifier of the analysis.

        Returns:
            The transcript analysis if found, None otherwise.
        """
        with self._lock:
            return self._storage.get(id)

    async def save_async(self, analysis: TranscriptAnalysis) -> None:
        """Save a transcript analysis to memory asynchronously (async-safe).

        Args:
            analysis: The transcript analysis to store.
        """
        async with self._async_lock:
            self._storage[analysis.id] = analysis

    async def get_by_id_async(self, id: str) -> TranscriptAnalysis | None:
        """Retrieve a transcript analysis by its ID asynchronously (async-safe).

        Args:
            id: The unique identifier of the analysis.

        Returns:
            The transcript analysis if found, None otherwise.
        """
        async with self._async_lock:
            return self._storage.get(id)
