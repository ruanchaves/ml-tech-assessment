"""Custom exceptions for the transcript analysis application.

This module defines a hierarchy of exceptions for different error scenarios,
enabling clear error handling and appropriate HTTP response mapping.
"""


class TranscriptAnalysisError(Exception):
    """Base exception for all transcript analysis errors."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class LLMError(TranscriptAnalysisError):
    """Base exception for LLM-related errors."""

    pass


class LLMConnectionError(LLMError):
    """Raised when connection to LLM service fails."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""

    pass


class LLMResponseError(LLMError):
    """Raised when LLM returns an invalid or unexpected response."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when LLM authentication fails."""

    pass


class RepositoryError(TranscriptAnalysisError):
    """Base exception for repository-related errors."""

    pass


class AnalysisNotFoundError(TranscriptAnalysisError):
    """Raised when a requested analysis is not found."""

    def __init__(self, analysis_id: str):
        super().__init__(f"Analysis with ID '{analysis_id}' not found")
        self.analysis_id = analysis_id
