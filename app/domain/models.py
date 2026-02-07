from dataclasses import dataclass


@dataclass
class TranscriptAnalysis:
    """Domain model representing a transcript analysis result.

    This is a pure domain entity that is independent of any infrastructure
    concerns (API, database, LLM responses).
    """

    id: str
    summary: str
    action_items: list[str]
