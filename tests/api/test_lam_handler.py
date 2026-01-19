"""Tests for LAM Message Handler API."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from scheduler.api.jobs import get_job_queue
from scheduler.main import app


@pytest.fixture
def mock_job_queue() -> MagicMock:
    """Create mock JobQueue."""
    mock = MagicMock()
    mock.update_status = AsyncMock()
    return mock


@pytest.fixture
def client(mock_job_queue: MagicMock) -> TestClient:
    """Create test client with mocked dependencies."""
    app.dependency_overrides[get_job_queue] = lambda: mock_job_queue
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_handle_done_message(client: TestClient, mock_job_queue: MagicMock):
    """Test handling a 'done' message updates job status."""
    job_id = "test-job-uuid"
    message = {
        "type": "done",
        "sender": "agent://test",
        "intent": "task_complete",
        "correlation": {
            "conversationId": job_id
        }
    }

    response = client.post("/lam/message", json=message)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "message_id" in response.json()
    
    # Verify job status was updated
    mock_job_queue.update_status.assert_called_once_with(job_id, "done")


def test_handle_failure_message(client: TestClient, mock_job_queue: MagicMock):
    """Test handling a 'failure' message updates job status."""
    job_id = "test-job-uuid"
    error_reason = "timeout"
    message = {
        "type": "failure",
        "sender": "agent://test",
        "intent": "task_failed",
        "correlation": {
            "conversationId": job_id
        },
        "status": {
            "code": "error",
            "reason": error_reason
        }
    }

    response = client.post("/lam/message", json=message)

    assert response.status_code == status.HTTP_202_ACCEPTED
    
    # Verify job status was updated with error
    mock_job_queue.update_status.assert_called_once_with(job_id, "failed", error=error_reason)


def test_handle_invalid_message(client: TestClient):
    """Test handling an invalid message returns 400."""
    message = {
        "type": "invalid_type",
        "sender": "agent://test"
        # Missing intent
    }

    response = client.post("/lam/message", json=message)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid message format" in response.json()["detail"]


def test_handle_message_without_job_id(client: TestClient, mock_job_queue: MagicMock):
    """Test message without job ID is accepted but doesn't update status."""
    message = {
        "type": "inform",
        "sender": "agent://test",
        "intent": "status_update",
        "payload": {"info": "something"}
    }

    response = client.post("/lam/message", json=message)

    assert response.status_code == status.HTTP_202_ACCEPTED
    mock_job_queue.update_status.assert_not_called()
