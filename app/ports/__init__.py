"""Port interfaces for the application.

This package defines abstract interfaces (ports) that adapters must implement.
"""

from app.ports.llm import LLm
from app.ports.repository import TranscriptRepository

__all__ = ["LLm", "TranscriptRepository"]