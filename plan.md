# Implementation Plan

## Overview

Build a Python web API using FastAPI that analyzes transcripts via OpenAI and returns summaries with action items. The implementation follows hexagonal (clean) architecture principles with clear separation between domain, application, and infrastructure layers.

## Existing Components (Provided)

- `app/ports/llm.py` - LLm abstract base class (port interface)
- `app/adapters/openai.py` - OpenAIAdapter (implements LLm port, includes async method)
- `app/prompts.py` - System and user prompts for transcript analysis
- `app/configurations.py` - Environment configuration (pydantic-settings)

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │  FastAPI Routes │  │  In-Memory Repository Adapter    │  │
│  └────────┬────────┘  └───────────────┬──────────────────┘  │
└───────────┼───────────────────────────┼─────────────────────┘
            │                           │
┌───────────┼───────────────────────────┼─────────────────────┐
│           │     Application Layer     │                      │
│  ┌────────▼───────────────────────────▼──────────────────┐  │
│  │              TranscriptAnalysisService                │  │
│  └────────┬───────────────────────────┬──────────────────┘  │
└───────────┼───────────────────────────┼─────────────────────┘
            │                           │
┌───────────┼───────────────────────────┼─────────────────────┐
│           │        Ports Layer        │                      │
│  ┌────────▼────────┐  ┌───────────────▼──────────────────┐  │
│  │    LLm Port     │  │     TranscriptRepository Port    │  │
│  │   (provided)    │  │          (to create)             │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────┐
│           │         Domain Layer                             │
│  ┌────────▼────────┐  ┌──────────────────────────────────┐  │
│  │ TranscriptAnalysis │  │     LLM Response DTO          │  │
│  │   (Domain Model)   │  │    (for OpenAI response)      │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Create Domain Models

**File:** `app/domain/models.py`

```python
# Domain model for transcript analysis result
class TranscriptAnalysis:
    id: str  # UUID
    summary: str
    action_items: list[str]
```

### Step 2: Create LLM Response DTO

**File:** `app/domain/dtos.py`

```python
# Pydantic model for structured OpenAI response
class TranscriptAnalysisDTO(pydantic.BaseModel):
    summary: str
    action_items: list[str]
```

### Step 3: Create Repository Port

**File:** `app/ports/repository.py`

```python
# Abstract interface for transcript storage
class TranscriptRepository(ABC):
    @abstractmethod
    def save(self, analysis: TranscriptAnalysis) -> None: ...

    @abstractmethod
    def get_by_id(self, id: str) -> TranscriptAnalysis | None: ...
```

### Step 4: Create In-Memory Repository Adapter

**File:** `app/adapters/memory_repository.py`

```python
# In-memory implementation of TranscriptRepository
class InMemoryTranscriptRepository(TranscriptRepository):
    # Uses dict for storage
```

### Step 5: Create Application Service

**File:** `app/services/transcript_service.py`

```python
class TranscriptAnalysisService:
    def __init__(self, llm: LLm, repository: TranscriptRepository): ...

    def analyze(self, transcript: str) -> TranscriptAnalysis: ...

    def get_by_id(self, id: str) -> TranscriptAnalysis | None: ...

    # Optional: async batch analysis
    async def analyze_batch(self, transcripts: list[str]) -> list[TranscriptAnalysis]: ...
```

### Step 6: Create API Request/Response Schemas

**File:** `app/api/schemas.py`

```python
# Request models
class AnalyzeTranscriptRequest(pydantic.BaseModel):
    transcript: str  # with validation for non-empty

class BatchAnalyzeRequest(pydantic.BaseModel):
    transcripts: list[str]

# Response models
class TranscriptAnalysisResponse(pydantic.BaseModel):
    id: str
    summary: str
    action_items: list[str]

class BatchAnalysisResponse(pydantic.BaseModel):
    results: list[TranscriptAnalysisResponse]
```

### Step 7: Create FastAPI Application

**File:** `app/api/routes.py`

```python
# Endpoints:
# POST /analyze - analyze single transcript
# GET /analysis/{id} - get analysis by ID
# POST /analyze/batch - (optional) concurrent batch analysis
```

**File:** `app/api/main.py`

```python
# FastAPI app setup with dependency injection
```

### Step 8: Create Dependencies Module

**File:** `app/api/dependencies.py`

```python
# Dependency injection for services
def get_transcript_service() -> TranscriptAnalysisService: ...
```

## File Structure (Final)

```
app/
├── __init__.py
├── configurations.py          (existing)
├── prompts.py                 (existing)
├── domain/
│   ├── __init__.py
│   ├── models.py              (domain entities)
│   └── dtos.py                (LLM response DTOs)
├── ports/
│   ├── __init__.py
│   ├── llm.py                 (existing)
│   └── repository.py          (new - storage interface)
├── adapters/
│   ├── __init__.py
│   ├── openai.py              (existing)
│   └── memory_repository.py   (new - in-memory storage)
├── services/
│   ├── __init__.py
│   └── transcript_service.py  (new - application logic)
└── api/
    ├── __init__.py
    ├── main.py                (FastAPI app)
    ├── routes.py              (endpoint definitions)
    ├── schemas.py             (request/response models)
    └── dependencies.py        (DI configuration)

tests/
├── __init__.py
├── adapters/
│   ├── test_openai.py         (existing)
│   ├── test_memory_repository.py (new)
│   └── mock_data.py           (existing)
├── services/
│   ├── __init__.py
│   └── test_transcript_service.py (new)
└── api/
    ├── __init__.py
    └── test_routes.py         (new - API integration tests)
```

## Dependencies to Add

```toml
# pyproject.toml additions
fastapi = "^0.115.0"
uvicorn = "^0.32.0"
httpx = "^0.27.0"  # for testing FastAPI
```

## API Specification

### POST /analyze

Analyze a single transcript.

**Request:**
```json
{
  "transcript": "string (non-empty)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "summary": "string",
  "action_items": ["string", "string"]
}
```

**Errors:**
- 400: Empty transcript
- 500: Internal server error

### GET /analysis/{id}

Retrieve analysis by ID.

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "summary": "string",
  "action_items": ["string", "string"]
}
```

**Errors:**
- 404: Analysis not found

### POST /analyze/batch (Optional - Point 2)

Analyze multiple transcripts concurrently.

**Request:**
```json
{
  "transcripts": ["string", "string"]
}
```

**Response (201 Created):**
```json
{
  "results": [
    {
      "id": "uuid-string",
      "summary": "string",
      "action_items": ["string"]
    }
  ]
}
```

## Key Design Decisions

1. **Separation of DTOs**: LLM response DTO (`TranscriptAnalysisDTO`) is separate from API response schema and domain model to avoid layer coupling.

2. **Repository Pattern**: Abstract storage behind a port interface, making it easy to swap in-memory for a real database later.

3. **Dependency Injection**: Use FastAPI's `Depends()` for clean service injection.

4. **UUID Generation**: Generate IDs in the service layer (domain logic), not in the API layer.

5. **Async Support**: The OpenAI adapter already has `run_completion_async()` - leverage this for batch processing.

## Testing Strategy

1. **Unit Tests**
   - `test_memory_repository.py` - test save/get operations
   - `test_transcript_service.py` - test service with mocked LLm and repository

2. **Integration Tests**
   - `test_routes.py` - test API endpoints with mocked service

3. **Existing Tests**
   - `test_openai.py` - validates adapter works (already provided)
