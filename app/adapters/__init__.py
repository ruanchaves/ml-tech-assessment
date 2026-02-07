"""Adapter implementations for the application.

This package contains concrete implementations of port interfaces.
"""

from app.adapters.openai import OpenAIAdapter
from app.adapters.memory_repository import InMemoryTranscriptRepository

__all__ = ["OpenAIAdapter", "InMemoryTranscriptRepository"]
