# Transcript Analysis API

A Python web API that analyzes plain text transcripts using OpenAI and returns summaries with recommended action items. Built with FastAPI following hexagonal (clean) architecture principles.

## Features

- **Single Transcript Analysis**: Analyze one transcript and receive a summary with action items
- **Batch Analysis**: Process multiple transcripts concurrently for improved performance
- **Retrieval**: Fetch previously analyzed transcripts by their unique ID
- **OpenAPI Documentation**: Interactive Swagger UI and ReDoc documentation
- **Docker Support**: Fully containerized with Docker Compose

## Documentation

- **[plan.md](plan.md)** - Implementation plan detailing the architecture, design decisions, and step-by-step build approach
- **[demonstration.md](demonstration.md)** - Full API demonstration output showing all endpoints in action
- **[tickets/](tickets/)** - Collection of 29 improvement tickets for future enhancements (error handling, authentication, rate limiting, caching, and more)

## Architecture

This project follows hexagonal (clean) architecture with clear separation of concerns:

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
│  └─────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
app/
├── api/                    # Infrastructure: FastAPI endpoints
│   ├── main.py            # FastAPI application setup
│   ├── routes.py          # API endpoint definitions
│   ├── schemas.py         # Request/response models
│   └── dependencies.py    # Dependency injection
├── domain/                 # Domain layer
│   ├── models.py          # Domain entities
│   └── dtos.py            # LLM response DTOs
├── ports/                  # Port interfaces (abstractions)
│   ├── llm.py             # LLM port interface
│   └── repository.py      # Repository port interface
├── adapters/               # Adapter implementations
│   ├── openai.py          # OpenAI LLM adapter
│   └── memory_repository.py  # In-memory storage adapter
├── services/               # Application layer
│   └── transcript_service.py  # Business logic orchestration
├── configurations.py       # Environment configuration
└── prompts.py             # LLM prompts
```

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### Running the Application

1. **Clone and configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Start the application:**

   ```bash
   docker compose up --build
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

4. **Run the API demo (optional):**

   With the Docker container running, test all endpoints:

   ```bash
   python demo_api.py
   ```

## Local Development Setup

### Using Conda (Recommended)

1. **Create and activate a conda environment:**

   ```bash
   conda create -n ml-assessment python=3.12
   conda activate ml-assessment
   ```

2. **Install Poetry and dependencies:**

   ```bash
   pip install poetry
   poetry install
   ```

3. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application:**

   ```bash
   poetry run uvicorn app.api.main:app --reload
   ```

5. **Run the API demo (optional):**

   With the server running, execute the demo script in another terminal to test all endpoints:

   ```bash
   poetry run python demo_api.py
   ```

   This will exercise all API endpoints and display the results step by step.

## API Endpoints

### POST /analyze

Analyze a single transcript.

**Request:**
```json
{
  "transcript": "John: Let's discuss the project timeline..."
}
```W

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": "Discussion about project timeline and deliverables...",
  "action_items": [
    "Schedule follow-up meeting",
    "Create project roadmap document"
  ]
}
```

### GET /analysis/{analysis_id}

Retrieve a previously created analysis.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": "Discussion about project timeline...",
  "action_items": ["Schedule follow-up meeting"]
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Analysis with ID 'xxx' not found"
}
```

### POST /analyze/batch

Analyze multiple transcripts concurrently.

**Request:**
```json
{
  "transcripts": [
    "Transcript 1 content...",
    "Transcript 2 content..."
  ]
}
```

**Response (201 Created):**
```json
{
  "results": [
    {
      "id": "uuid-1",
      "summary": "Summary 1...",
      "action_items": ["Action 1"]
    },
    {
      "id": "uuid-2",
      "summary": "Summary 2...",
      "action_items": ["Action 2"]
    }
  ]
}
```

### GET /health

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

## Running Tests

### Using Docker (Recommended)

Run all tests in a Docker container:

```bash
docker compose -f docker-compose.test.yml up --build
```

### API Key Requirements

Most tests **do not require an OpenAI API key** — they use mocks for the LLM adapter. The only exception is `tests/adapters/test_openai.py`, which performs a live integration test against the OpenAI API.

To run all tests **without** an API key, exclude the OpenAI adapter test:

```bash
pytest --ignore=tests/adapters/test_openai.py
```

### Local Development

If you have Poetry installed locally:

```bash
# All tests
pytest

# With verbose output
pytest -v

# Specific test files
pytest tests/adapters/test_memory_repository.py
pytest tests/services/test_transcript_service.py
pytest tests/api/test_routes.py

# With coverage report
pytest --cov=app --cov-report=html
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-2024-08-06` |

## Error Handling

The API returns appropriate HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success (GET requests) |
| 201 | Created (POST requests) |
| 400 | Bad Request (validation errors) |
| 404 | Not Found (analysis ID not found) |
| 422 | Unprocessable Entity (invalid input) |
| 500 | Internal Server Error |

## Design Decisions

1. **Separation of DTOs**: LLM response DTO (`TranscriptAnalysisDTO`) is separate from API response schema and domain model to avoid layer coupling.

2. **Repository Pattern**: Storage is abstracted behind a port interface, making it easy to swap in-memory for a real database.

3. **Dependency Injection**: FastAPI's `Depends()` provides clean service injection.

4. **Async Support**: The batch endpoint uses `asyncio.gather()` for concurrent processing.

5. **UUID Generation**: IDs are generated in the service layer as part of domain logic.
