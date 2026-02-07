"""API request and response schemas.

This module defines the Pydantic models for API requests and responses,
including validation rules and OpenAPI documentation.
"""

import pydantic


class AnalyzeTranscriptRequest(pydantic.BaseModel):
    """Request model for analyzing a single transcript."""

    transcript: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=100000,
        description="The plain text transcript to analyze. Must not be empty. Maximum 100,000 characters.",
    )

    model_config = pydantic.ConfigDict(
        json_schema_extra={
            "example": {
                "transcript": "John: Let's discuss the Q4 roadmap. Sarah: I think we should focus on user retention..."
            }
        }
    )


class BatchAnalyzeRequest(pydantic.BaseModel):
    """Request model for analyzing multiple transcripts concurrently."""

    transcripts: list[str] = pydantic.Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of plain text transcripts to analyze. Must contain 1-10 transcripts.",
    )

    @pydantic.field_validator("transcripts")
    @classmethod
    def validate_transcripts_not_empty(cls, v: list[str]) -> list[str]:
        """Validate that no transcript is empty or exceeds length limit."""
        for i, transcript in enumerate(v):
            if not transcript or not transcript.strip():
                raise ValueError(f"Transcript at index {i} must not be empty")
            if len(transcript) > 100000:
                raise ValueError(
                    f"Transcript at index {i} exceeds maximum length of 100,000 characters"
                )
        return v

    model_config = pydantic.ConfigDict(
        json_schema_extra={
            "example": {
                "transcripts": [
                    "Meeting 1 transcript content...",
                    "Meeting 2 transcript content...",
                ]
            }
        }
    )


class TranscriptAnalysisResponse(pydantic.BaseModel):
    """Response model for a transcript analysis result."""

    id: str = pydantic.Field(
        ...,
        description="Unique identifier for this analysis.",
    )
    summary: str = pydantic.Field(
        ...,
        description="A brief, insightful summary of the transcript.",
    )
    action_items: list[str] = pydantic.Field(
        ...,
        description="List of recommended next actions based on the transcript.",
    )

    model_config = pydantic.ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "summary": "The team discussed Q4 roadmap priorities focusing on user retention strategies.",
                "action_items": [
                    "Schedule follow-up meeting for retention metrics review",
                    "Create user survey draft by next week",
                ],
            }
        }
    )


class BatchAnalysisResponse(pydantic.BaseModel):
    """Response model for batch transcript analysis."""

    results: list[TranscriptAnalysisResponse] = pydantic.Field(
        ...,
        description="List of analysis results for each transcript.",
    )


class ErrorResponse(pydantic.BaseModel):
    """Response model for error responses."""

    detail: str = pydantic.Field(
        ...,
        description="Error message describing what went wrong.",
    )
