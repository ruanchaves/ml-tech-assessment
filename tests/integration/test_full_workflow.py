"""Integration tests for complete API workflows.

This module tests end-to-end scenarios from API request to response,
verifying that all components work together correctly.
"""

from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.dependencies import get_transcript_service
from app.domain.dtos import TranscriptAnalysisDTO
from app.exceptions import LLMConnectionError, LLMRateLimitError


class TestAnalyzeAndRetrieveWorkflow:
    """Integration tests for analyze then retrieve workflow."""

    @pytest.fixture
    def mock_openai_response(self) -> MagicMock:
        """Create a mock OpenAI response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.parsed = TranscriptAnalysisDTO(
            summary="Integration test summary",
            action_items=["Action 1", "Action 2"],
        )
        return mock_response

    @pytest.fixture
    def client_with_mocked_openai(self, mock_openai_response: MagicMock) -> TestClient:
        """Create test client with mocked OpenAI API."""
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-test"

        with patch("app.adapters.openai.openai.OpenAI") as mock_sync, \
             patch("app.adapters.openai.openai.AsyncOpenAI") as mock_async, \
             patch("app.api.dependencies.get_settings", return_value=mock_settings):
            # Configure sync mock
            sync_instance = MagicMock()
            mock_sync.return_value = sync_instance
            sync_instance.beta.chat.completions.parse.return_value = mock_openai_response

            # Configure async mock
            async_instance = MagicMock()
            mock_async.return_value = async_instance
            async_instance.beta.chat.completions.parse = AsyncMock(
                return_value=mock_openai_response
            )

            # Clear any existing overrides and create fresh client
            app.dependency_overrides.clear()
            yield TestClient(app)
            app.dependency_overrides.clear()

    def test_analyze_then_retrieve(
        self, client_with_mocked_openai: TestClient
    ) -> None:
        """Test analyzing a transcript and then retrieving it."""
        # Step 1: Analyze transcript
        analyze_response = client_with_mocked_openai.post(
            "/analyze",
            json={"transcript": "Test transcript for integration testing"},
        )
        assert analyze_response.status_code == 201
        analysis_data = analyze_response.json()
        assert "id" in analysis_data
        assert analysis_data["summary"] == "Integration test summary"
        assert analysis_data["action_items"] == ["Action 1", "Action 2"]

        # Step 2: Retrieve the same analysis by ID
        analysis_id = analysis_data["id"]
        retrieve_response = client_with_mocked_openai.get(f"/analysis/{analysis_id}")
        assert retrieve_response.status_code == 200
        retrieved_data = retrieve_response.json()
        assert retrieved_data["id"] == analysis_id
        assert retrieved_data["summary"] == "Integration test summary"
        assert retrieved_data["action_items"] == ["Action 1", "Action 2"]

    def test_multiple_analyses_independently_stored(
        self, client_with_mocked_openai: TestClient
    ) -> None:
        """Test that multiple analyses are stored and retrieved independently."""
        # Analyze two different transcripts
        response1 = client_with_mocked_openai.post(
            "/analyze",
            json={"transcript": "First transcript"},
        )
        response2 = client_with_mocked_openai.post(
            "/analyze",
            json={"transcript": "Second transcript"},
        )

        assert response1.status_code == 201
        assert response2.status_code == 201

        id1 = response1.json()["id"]
        id2 = response2.json()["id"]

        # IDs should be different
        assert id1 != id2

        # Both should be retrievable
        retrieve1 = client_with_mocked_openai.get(f"/analysis/{id1}")
        retrieve2 = client_with_mocked_openai.get(f"/analysis/{id2}")

        assert retrieve1.status_code == 200
        assert retrieve2.status_code == 200
        assert retrieve1.json()["id"] == id1
        assert retrieve2.json()["id"] == id2


class TestBatchAnalyzeWorkflow:
    """Integration tests for batch analysis workflow."""

    @pytest.fixture
    def mock_openai_response(self) -> MagicMock:
        """Create a mock OpenAI response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.parsed = TranscriptAnalysisDTO(
            summary="Batch test summary",
            action_items=["Batch action"],
        )
        return mock_response

    @pytest.fixture
    def client_with_mocked_openai(self, mock_openai_response: MagicMock) -> TestClient:
        """Create test client with mocked OpenAI API."""
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-test"

        with patch("app.adapters.openai.openai.OpenAI") as mock_sync, \
             patch("app.adapters.openai.openai.AsyncOpenAI") as mock_async, \
             patch("app.api.dependencies.get_settings", return_value=mock_settings):
            sync_instance = MagicMock()
            mock_sync.return_value = sync_instance
            sync_instance.beta.chat.completions.parse.return_value = mock_openai_response

            async_instance = MagicMock()
            mock_async.return_value = async_instance
            async_instance.beta.chat.completions.parse = AsyncMock(
                return_value=mock_openai_response
            )

            app.dependency_overrides.clear()
            yield TestClient(app)
            app.dependency_overrides.clear()

    def test_batch_analyze_then_retrieve_all(
        self, client_with_mocked_openai: TestClient
    ) -> None:
        """Test batch analysis and retrieval of all results."""
        # Step 1: Batch analyze
        batch_response = client_with_mocked_openai.post(
            "/analyze/batch",
            json={"transcripts": ["Transcript 1", "Transcript 2", "Transcript 3"]},
        )
        assert batch_response.status_code == 201
        results = batch_response.json()["results"]
        assert len(results) == 3

        # Step 2: Retrieve each analysis by ID
        for result in results:
            retrieve_response = client_with_mocked_openai.get(
                f"/analysis/{result['id']}"
            )
            assert retrieve_response.status_code == 200
            assert retrieve_response.json()["id"] == result["id"]
            assert retrieve_response.json()["summary"] == "Batch test summary"

    def test_batch_analyze_unique_ids(
        self, client_with_mocked_openai: TestClient
    ) -> None:
        """Test that batch analysis generates unique IDs for each result."""
        batch_response = client_with_mocked_openai.post(
            "/analyze/batch",
            json={"transcripts": ["T1", "T2", "T3", "T4", "T5"]},
        )
        assert batch_response.status_code == 201
        results = batch_response.json()["results"]

        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids)), "All IDs should be unique"


class TestRetrieveNonexistent:
    """Integration tests for retrieving non-existent analyses."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-test"

        with patch("app.api.dependencies.get_settings", return_value=mock_settings):
            app.dependency_overrides.clear()
            yield TestClient(app)
            app.dependency_overrides.clear()

    def test_retrieve_nonexistent_returns_404(self, client: TestClient) -> None:
        """Test that retrieving non-existent analysis returns 404."""
        response = client.get("/analysis/nonexistent-id-12345")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_retrieve_empty_id_returns_404(self, client: TestClient) -> None:
        """Test that retrieving with empty-like ID returns 404."""
        response = client.get("/analysis/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestErrorPropagation:
    """Integration tests for error propagation through layers."""

    @pytest.fixture
    def client_with_connection_error(self) -> TestClient:
        """Create test client that simulates connection error."""
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-test"

        with patch("app.adapters.openai.openai.OpenAI") as mock_sync, \
             patch("app.adapters.openai.openai.AsyncOpenAI") as mock_async, \
             patch("app.api.dependencies.get_settings", return_value=mock_settings):
            import openai

            sync_instance = MagicMock()
            mock_sync.return_value = sync_instance
            sync_instance.beta.chat.completions.parse.side_effect = openai.APIConnectionError(
                request=MagicMock()
            )

            async_instance = MagicMock()
            mock_async.return_value = async_instance
            async_instance.beta.chat.completions.parse = AsyncMock(
                side_effect=openai.APIConnectionError(request=MagicMock())
            )

            app.dependency_overrides.clear()
            yield TestClient(app)
            app.dependency_overrides.clear()

    @pytest.fixture
    def client_with_rate_limit_error(self) -> TestClient:
        """Create test client that simulates rate limit error."""
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-test"

        with patch("app.adapters.openai.openai.OpenAI") as mock_sync, \
             patch("app.adapters.openai.openai.AsyncOpenAI") as mock_async, \
             patch("app.api.dependencies.get_settings", return_value=mock_settings):
            import openai

            sync_instance = MagicMock()
            mock_sync.return_value = sync_instance
            sync_instance.beta.chat.completions.parse.side_effect = openai.RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )

            async_instance = MagicMock()
            mock_async.return_value = async_instance
            async_instance.beta.chat.completions.parse = AsyncMock(
                side_effect=openai.RateLimitError(
                    message="Rate limit exceeded",
                    response=MagicMock(status_code=429),
                    body=None,
                )
            )

            app.dependency_overrides.clear()
            yield TestClient(app)
            app.dependency_overrides.clear()

    def test_connection_error_returns_502(
        self, client_with_connection_error: TestClient
    ) -> None:
        """Test that connection errors propagate as 502 Bad Gateway."""
        response = client_with_connection_error.post(
            "/analyze",
            json={"transcript": "Test transcript"},
        )
        assert response.status_code == 502
        assert "connect" in response.json()["detail"].lower()

    def test_rate_limit_error_returns_503(
        self, client_with_rate_limit_error: TestClient
    ) -> None:
        """Test that rate limit errors propagate as 503 Service Unavailable."""
        response = client_with_rate_limit_error.post(
            "/analyze",
            json={"transcript": "Test transcript"},
        )
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()

    def test_batch_connection_error_returns_502(
        self, client_with_connection_error: TestClient
    ) -> None:
        """Test that batch endpoint propagates connection errors as 502."""
        response = client_with_connection_error.post(
            "/analyze/batch",
            json={"transcripts": ["Test"]},
        )
        assert response.status_code == 502


class TestHealthCheck:
    """Integration tests for health check endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_health_check_returns_healthy(self, client: TestClient) -> None:
        """Test that health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_check_independent_of_openai(self, client: TestClient) -> None:
        """Test that health check works even without OpenAI configuration."""
        # Health check should work regardless of OpenAI status
        response = client.get("/health")
        assert response.status_code == 200
