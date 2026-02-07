from functools import lru_cache

from app.adapters.memory_repository import InMemoryTranscriptRepository
from app.adapters.openai import OpenAIAdapter
from app.configurations import EnvConfigs
from app.ports.repository import TranscriptRepository
from app.services.transcript_service import TranscriptAnalysisService


@lru_cache
def get_settings() -> EnvConfigs:
    """Get cached application settings."""
    return EnvConfigs()


@lru_cache
def get_repository() -> TranscriptRepository:
    """Get singleton in-memory repository instance.

    Uses lru_cache to ensure the same repository instance is used
    throughout the application lifetime, preserving stored data.
    """
    return InMemoryTranscriptRepository()


def get_transcript_service() -> TranscriptAnalysisService:
    """Get transcript analysis service with injected dependencies.

    Returns:
        Configured TranscriptAnalysisService instance.
    """
    settings = get_settings()
    repository = get_repository()
    llm = OpenAIAdapter(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
    )
    return TranscriptAnalysisService(llm=llm, repository=repository)
