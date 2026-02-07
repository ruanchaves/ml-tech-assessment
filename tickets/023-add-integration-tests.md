# Add Integration Tests

**Severity:** Medium
**Category:** Testing
**Affected Files:** `tests/integration/`

## Description

The test suite only has unit tests and one OpenAI integration test. Missing end-to-end scenario tests that verify the complete workflow from API request to response.

## Current Behavior

- Unit tests mock all dependencies
- No tests verify real component integration
- No tests for full analyze → retrieve workflow

## Expected Behavior

Integration tests that verify components work together correctly.

## Acceptance Criteria

- [ ] Create integration test directory
- [ ] Add full workflow tests (analyze then retrieve)
- [ ] Add batch processing integration tests
- [ ] Test with mocked OpenAI (not real API)
- [ ] Test error propagation through layers
- [ ] Document how to run integration tests separately

## Suggested Implementation

```python
# tests/integration/__init__.py

# tests/integration/test_full_workflow.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.api.main import app
from app.domain.dtos import TranscriptAnalysisDTO


class TestFullWorkflow:
    """Integration tests for complete API workflows."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI API for integration tests."""
        with patch("app.adapters.openai.openai.OpenAI") as mock:
            instance = MagicMock()
            mock.return_value = instance

            # Configure mock response
            mock_response = MagicMock()
            mock_response.choices[0].message.parsed = TranscriptAnalysisDTO(
                summary="Integration test summary",
                action_items=["Action 1", "Action 2"]
            )
            instance.beta.chat.completions.parse.return_value = mock_response

            yield instance

    def test_analyze_then_retrieve(self, client, mock_openai):
        """Test analyzing a transcript and then retrieving it."""
        # Analyze
        response = client.post(
            "/analyze",
            json={"transcript": "Test transcript for integration"}
        )
        assert response.status_code == 201
        analysis_id = response.json()["id"]

        # Retrieve
        response = client.get(f"/analysis/{analysis_id}")
        assert response.status_code == 200
        assert response.json()["id"] == analysis_id
        assert response.json()["summary"] == "Integration test summary"

    def test_batch_analyze_then_retrieve_all(self, client, mock_openai):
        """Test batch analysis and retrieval of all results."""
        # Batch analyze
        response = client.post(
            "/analyze/batch",
            json={"transcripts": ["Transcript 1", "Transcript 2"]}
        )
        assert response.status_code == 201
        results = response.json()["results"]
        assert len(results) == 2

        # Retrieve each
        for result in results:
            response = client.get(f"/analysis/{result['id']}")
            assert response.status_code == 200

    def test_retrieve_nonexistent_returns_404(self, client):
        """Test that retrieving non-existent analysis returns 404."""
        response = client.get("/analysis/nonexistent-id")
        assert response.status_code == 404
```

## Running Integration Tests

```bash
# Run only integration tests
pytest tests/integration/ -v

# Run all tests except integration
pytest tests/ --ignore=tests/integration/ -v
```
