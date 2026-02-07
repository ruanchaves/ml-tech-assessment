import pydantic


class TranscriptAnalysisDTO(pydantic.BaseModel):
    """DTO for structured LLM response.

    This model is used with OpenAI's structured output feature to ensure
    the LLM returns data in the expected format.
    """

    summary: str
    action_items: list[str]
