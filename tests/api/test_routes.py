"""Tests for API routes.

This module tests the FastAPI endpoints including success scenarios,
validation errors, and error handling.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.dependencies import get_transcript_service
from app.domain.models import TranscriptAnalysis
from app.exceptions import LLMConnectionError, LLMRateLimitError, LLMError


class MockTranscriptService:
    """Mock service for API testing."""

    def __init__(self) -> None:
        self.analyze = MagicMock()
        self.get_by_id = MagicMock()
        self.analyze_batch = AsyncMock()


@pytest.fixture
def mock_service() -> MockTranscriptService:
    """Create a mock service fixture."""
    return MockTranscriptService()


@pytest.fixture
def client(mock_service: MockTranscriptService) -> TestClient:
    """Create test client with mocked dependencies."""
    app.dependency_overrides[get_transcript_service] = lambda: mock_service
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestAnalyzeEndpoint:
    """Tests for POST /analyze endpoint."""

    def test_analyze_success(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test successful transcript analysis."""
        mock_service.analyze.return_value = TranscriptAnalysis(
            id="test-uuid",
            summary="Test summary",
            action_items=["Action 1", "Action 2"],
        )

        response = client.post(
            "/analyze",
            json={"transcript": "Test transcript content"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test-uuid"
        assert data["summary"] == "Test summary"
        assert data["action_items"] == ["Action 1", "Action 2"]

    def test_analyze_empty_transcript_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that empty transcript returns validation error."""
        response = client.post(
            "/analyze",
            json={"transcript": ""},
        )

        assert response.status_code == 422

    def test_analyze_missing_transcript_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that missing transcript field returns validation error."""
        response = client.post(
            "/analyze",
            json={},
        )

        assert response.status_code == 422

    def test_analyze_calls_service(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that endpoint calls service with transcript."""
        mock_service.analyze.return_value = TranscriptAnalysis(
            id="test-uuid",
            summary="Summary",
            action_items=[],
        )

        client.post(
            "/analyze",
            json={"transcript": "My transcript"},
        )

        mock_service.analyze.assert_called_once_with("My transcript")

    def test_analyze_too_long_transcript_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that transcript exceeding max length returns validation error."""
        long_transcript = "A" * 100001  # Exceeds 100,000 char limit

        response = client.post(
            "/analyze",
            json={"transcript": long_transcript},
        )

        assert response.status_code == 422


class TestAnalyzeEndpointErrors:
    """Tests for error handling in POST /analyze endpoint."""

    def test_analyze_connection_error_returns_502(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that LLM connection error returns 502."""
        mock_service.analyze.side_effect = LLMConnectionError("Connection failed")

        response = client.post(
            "/analyze",
            json={"transcript": "Test transcript"},
        )

        assert response.status_code == 502
        assert "connect" in response.json()["detail"].lower()

    def test_analyze_rate_limit_error_returns_503(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that LLM rate limit error returns 503."""
        mock_service.analyze.side_effect = LLMRateLimitError("Rate limit exceeded")

        response = client.post(
            "/analyze",
            json={"transcript": "Test transcript"},
        )

        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()

    def test_analyze_llm_error_returns_500(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that generic LLM error returns 500."""
        mock_service.analyze.side_effect = LLMError("LLM error")

        response = client.post(
            "/analyze",
            json={"transcript": "Test transcript"},
        )

        assert response.status_code == 500


class TestAnalyzeGetEndpoint:
    """Tests for GET /analyze endpoint."""

    def test_analyze_get_success(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test successful transcript analysis via GET."""
        mock_service.analyze.return_value = TranscriptAnalysis(
            id="test-uuid",
            summary="Test summary",
            action_items=["Action 1", "Action 2"],
        )

        response = client.get("/analyze", params={"transcript": "Test transcript content"})

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test-uuid"
        assert data["summary"] == "Test summary"
        assert data["action_items"] == ["Action 1", "Action 2"]

    def test_analyze_get_empty_transcript_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that empty transcript returns validation error."""
        response = client.get("/analyze", params={"transcript": ""})

        assert response.status_code == 422

    def test_analyze_get_missing_transcript_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that missing transcript parameter returns validation error."""
        response = client.get("/analyze")

        assert response.status_code == 422

    def test_analyze_get_calls_service(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that GET endpoint calls service with transcript."""
        mock_service.analyze.return_value = TranscriptAnalysis(
            id="test-uuid",
            summary="Summary",
            action_items=[],
        )

        client.get("/analyze", params={"transcript": "My transcript"})

        mock_service.analyze.assert_called_once_with("My transcript")

    def test_analyze_get_connection_error_returns_502(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that LLM connection error returns 502 for GET."""
        mock_service.analyze.side_effect = LLMConnectionError("Connection failed")

        response = client.get("/analyze", params={"transcript": "Test transcript"})

        assert response.status_code == 502
        assert "connect" in response.json()["detail"].lower()

    def test_analyze_get_rate_limit_error_returns_503(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that LLM rate limit error returns 503 for GET."""
        mock_service.analyze.side_effect = LLMRateLimitError("Rate limit exceeded")

        response = client.get("/analyze", params={"transcript": "Test transcript"})

        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()

    def test_analyze_get_llm_error_returns_500(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that generic LLM error returns 500 for GET."""
        mock_service.analyze.side_effect = LLMError("LLM error")

        response = client.get("/analyze", params={"transcript": "Test transcript"})

        assert response.status_code == 500


class TestGetAnalysisEndpoint:
    """Tests for GET /analysis/{analysis_id} endpoint."""

    def test_get_analysis_success(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test successful retrieval of analysis."""
        mock_service.get_by_id.return_value = TranscriptAnalysis(
            id="existing-id",
            summary="Stored summary",
            action_items=["Stored action"],
        )

        response = client.get("/analysis/existing-id")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "existing-id"
        assert data["summary"] == "Stored summary"
        assert data["action_items"] == ["Stored action"]

    def test_get_analysis_not_found(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test 404 when analysis not found."""
        mock_service.get_by_id.return_value = None

        response = client.get("/analysis/non-existent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_analysis_calls_service(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that endpoint calls service with correct ID."""
        mock_service.get_by_id.return_value = TranscriptAnalysis(
            id="my-id",
            summary="Summary",
            action_items=[],
        )

        client.get("/analysis/my-id")

        mock_service.get_by_id.assert_called_once_with("my-id")


class TestBatchAnalyzeEndpoint:
    """Tests for POST /analyze/batch endpoint."""

    def test_batch_analyze_success(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test successful batch analysis."""
        mock_service.analyze_batch.return_value = [
            TranscriptAnalysis(id="id-1", summary="Summary 1", action_items=["A1"]),
            TranscriptAnalysis(id="id-2", summary="Summary 2", action_items=["A2"]),
        ]

        response = client.post(
            "/analyze/batch",
            json={"transcripts": ["Transcript 1", "Transcript 2"]},
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["id"] == "id-1"
        assert data["results"][1]["id"] == "id-2"

    def test_batch_analyze_empty_list_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that empty transcripts list returns validation error."""
        response = client.post(
            "/analyze/batch",
            json={"transcripts": []},
        )

        assert response.status_code == 422

    def test_batch_analyze_empty_transcript_in_list_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that empty transcript in list returns validation error."""
        response = client.post(
            "/analyze/batch",
            json={"transcripts": ["Valid transcript", ""]},
        )

        assert response.status_code == 422

    def test_batch_analyze_whitespace_only_transcript_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that whitespace-only transcript returns validation error."""
        response = client.post(
            "/analyze/batch",
            json={"transcripts": ["Valid transcript", "   "]},
        )

        assert response.status_code == 422

    def test_batch_analyze_too_many_transcripts_returns_422(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that more than 10 transcripts returns validation error."""
        transcripts = [f"Transcript {i}" for i in range(11)]

        response = client.post(
            "/analyze/batch",
            json={"transcripts": transcripts},
        )

        assert response.status_code == 422

    def test_batch_analyze_calls_service(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that endpoint calls service with transcripts."""
        mock_service.analyze_batch.return_value = []

        client.post(
            "/analyze/batch",
            json={"transcripts": ["T1", "T2"]},
        )

        mock_service.analyze_batch.assert_called_once_with(["T1", "T2"])


class TestBatchAnalyzeEndpointErrors:
    """Tests for error handling in POST /analyze/batch endpoint."""

    def test_batch_analyze_connection_error_returns_502(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that LLM connection error returns 502."""
        mock_service.analyze_batch.side_effect = LLMConnectionError("Connection failed")

        response = client.post(
            "/analyze/batch",
            json={"transcripts": ["Test"]},
        )

        assert response.status_code == 502

    def test_batch_analyze_rate_limit_error_returns_503(
        self, client: TestClient, mock_service: MockTranscriptService
    ) -> None:
        """Test that LLM rate limit error returns 503."""
        mock_service.analyze_batch.side_effect = LLMRateLimitError("Rate limit")

        response = client.post(
            "/analyze/batch",
            json={"transcripts": ["Test"]},
        )

        assert response.status_code == 503


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation endpoints."""

    def test_docs_endpoint_available(self, client: TestClient) -> None:
        """Test that Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint_available(self, client: TestClient) -> None:
        """Test that ReDoc is available."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json_available(self, client: TestClient) -> None:
        """Test that OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Transcript Analysis API"
        assert "/analyze" in data["paths"]
        assert "/analysis/{analysis_id}" in data["paths"]
        assert "/analyze/batch" in data["paths"]
