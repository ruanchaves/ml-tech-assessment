from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Transcript Analysis API",
    description="""
## Overview

This API analyzes plain text transcripts and returns summaries with recommended action items.

## Features

- **Single Analysis**: Analyze one transcript and get a summary with action items
- **Batch Analysis**: Analyze multiple transcripts concurrently for improved performance
- **Retrieval**: Fetch previously analyzed transcripts by their unique ID

## Architecture

This API follows hexagonal (clean) architecture principles:

- **Domain Layer**: Core business entities independent of infrastructure
- **Ports**: Abstract interfaces defining contracts
- **Adapters**: Implementations of ports (OpenAI for LLM, in-memory for storage)
- **Application Layer**: Services orchestrating business logic
- **Infrastructure Layer**: FastAPI endpoints and dependency injection

## Usage

1. Send a POST request to `/analyze` with your transcript
2. Receive a unique ID, summary, and action items
3. Use the ID to retrieve the analysis later via GET `/analysis/{id}`
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Transcript Analysis",
            "description": "Endpoints for analyzing transcripts and retrieving results",
        }
    ],
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestration."""
    return {"status": "healthy"}
