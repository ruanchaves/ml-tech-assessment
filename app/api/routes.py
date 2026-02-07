"""API route definitions.

This module defines the FastAPI routes for transcript analysis endpoints.

Note on HTTP Methods:
    The /analyze endpoint supports both GET and POST methods:
    - GET: For assessment compliance, accepts transcript as query parameter.
           Limited by URL length (~2000 chars).
    - POST: Recommended for production use with longer transcripts.
           Semantically correct for creating resources.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_transcript_service
from app.api.schemas import (
    AnalyzeTranscriptRequest,
    BatchAnalysisResponse,
    BatchAnalyzeRequest,
    ErrorResponse,
    TranscriptAnalysisResponse,
)
from app.exceptions import (
    LLMConnectionError,
    LLMRateLimitError,
    LLMError,
    TranscriptAnalysisError,
)
from app.services.transcript_service import TranscriptAnalysisService

router = APIRouter(tags=["Transcript Analysis"])


@router.get(
    "/analyze",
    response_model=TranscriptAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a transcript (GET)",
    description="Analyze a plain text transcript via query parameter. "
    "Limited by URL length. Use POST for longer transcripts.",
    responses={
        201: {
            "description": "Analysis completed successfully",
            "model": TranscriptAnalysisResponse,
        },
        422: {
            "description": "Validation error (empty transcript)",
            "model": ErrorResponse,
        },
        502: {
            "description": "LLM service connection error",
            "model": ErrorResponse,
        },
        503: {
            "description": "LLM service temporarily unavailable (rate limit)",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error during analysis",
            "model": ErrorResponse,
        },
    },
)
def analyze_transcript_get(
    transcript: str = Query(
        ...,
        min_length=1,
        description="The plain text transcript to analyze",
        examples=["John: Let's discuss the project timeline..."],
    ),
    service: TranscriptAnalysisService = Depends(get_transcript_service),
) -> TranscriptAnalysisResponse:
    """Analyze a single transcript via GET request.

    Accepts a plain text transcript as a query parameter, sends it to the
    LLM for analysis, stores the result, and returns a summary with action items.
    """
    try:
        analysis = service.analyze(transcript)
        return TranscriptAnalysisResponse(
            id=analysis.id,
            summary=analysis.summary,
            action_items=analysis.action_items,
        )
    except LLMConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to connect to analysis service. Please try again.",
        ) from e
    except LLMRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily unavailable. Please try again later.",
        ) from e
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis service error. Please try again.",
        ) from e
    except TranscriptAnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze transcript. Please try again.",
        ) from e


@router.post(
    "/analyze",
    response_model=TranscriptAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a transcript (POST)",
    description="Analyze a plain text transcript and return a summary with action items. "
    "Recommended for longer transcripts.",
    responses={
        201: {
            "description": "Analysis completed successfully",
            "model": TranscriptAnalysisResponse,
        },
        422: {
            "description": "Validation error (empty or too long transcript)",
            "model": ErrorResponse,
        },
        502: {
            "description": "LLM service connection error",
            "model": ErrorResponse,
        },
        503: {
            "description": "LLM service temporarily unavailable (rate limit)",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error during analysis",
            "model": ErrorResponse,
        },
    },
)
def analyze_transcript(
    request: AnalyzeTranscriptRequest,
    service: TranscriptAnalysisService = Depends(get_transcript_service),
) -> TranscriptAnalysisResponse:
    """Analyze a single transcript via POST request.

    Accepts a plain text transcript in the request body, sends it to the LLM
    for analysis, stores the result, and returns a summary with action items.
    """
    try:
        analysis = service.analyze(request.transcript)
        return TranscriptAnalysisResponse(
            id=analysis.id,
            summary=analysis.summary,
            action_items=analysis.action_items,
        )
    except LLMConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to connect to analysis service. Please try again.",
        ) from e
    except LLMRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily unavailable. Please try again later.",
        ) from e
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis service error. Please try again.",
        ) from e
    except TranscriptAnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze transcript. Please try again.",
        ) from e


@router.get(
    "/analysis/{analysis_id}",
    response_model=TranscriptAnalysisResponse,
    summary="Get analysis by ID",
    description="Retrieve a previously created transcript analysis by its unique ID.",
    responses={
        200: {
            "description": "Analysis found",
            "model": TranscriptAnalysisResponse,
        },
        404: {
            "description": "Analysis not found",
            "model": ErrorResponse,
        },
    },
)
def get_analysis(
    analysis_id: str,
    service: TranscriptAnalysisService = Depends(get_transcript_service),
) -> TranscriptAnalysisResponse:
    """Retrieve a transcript analysis by ID.

    Returns the stored analysis result if found, or 404 if not found.
    """
    analysis = service.get_by_id(analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found",
        )
    return TranscriptAnalysisResponse(
        id=analysis.id,
        summary=analysis.summary,
        action_items=analysis.action_items,
    )


@router.post(
    "/analyze/batch",
    response_model=BatchAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze multiple transcripts",
    description="Analyze multiple transcripts concurrently using async processing.",
    responses={
        201: {
            "description": "All analyses completed successfully",
            "model": BatchAnalysisResponse,
        },
        422: {
            "description": "Validation error (empty transcripts or too many items)",
            "model": ErrorResponse,
        },
        502: {
            "description": "LLM service connection error",
            "model": ErrorResponse,
        },
        503: {
            "description": "LLM service temporarily unavailable (rate limit)",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error during analysis",
            "model": ErrorResponse,
        },
    },
)
async def analyze_batch(
    request: BatchAnalyzeRequest,
    service: TranscriptAnalysisService = Depends(get_transcript_service),
) -> BatchAnalysisResponse:
    """Analyze multiple transcripts concurrently.

    Processes all transcripts in parallel using asyncio, without blocking
    the main API thread. Returns results in the same order as input.
    """
    try:
        analyses = await service.analyze_batch(request.transcripts)
        return BatchAnalysisResponse(
            results=[
                TranscriptAnalysisResponse(
                    id=analysis.id,
                    summary=analysis.summary,
                    action_items=analysis.action_items,
                )
                for analysis in analyses
            ]
        )
    except LLMConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to connect to analysis service. Please try again.",
        ) from e
    except LLMRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily unavailable. Please try again later.",
        ) from e
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis service error. Please try again.",
        ) from e
    except TranscriptAnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze transcripts. Please try again.",
        ) from e
