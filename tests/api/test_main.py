"""Tests for FastAPI application (scheduler/main.py)."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from scheduler.api.jobs import get_job_queue
from scheduler.main import app


@pytest.fixture
def mock_redis() -> MagicMock:
    """Create mock Redis client."""
    mock = MagicMock()
    mock.ping = AsyncMock(return_value=True)
    mock.aclose = AsyncMock()
    return mock


@pytest.fixture
def mock_job_queue(mock_redis: MagicMock) -> MagicMock:
    """Create mock JobQueue."""
    mock = MagicMock()
    mock.redis = mock_redis
    mock.connect = AsyncMock()
    mock.close = AsyncMock()
    mock.enqueue = AsyncMock()  # Add enqueue method for job API tests
    return mock


@pytest.fixture
def client(mock_job_queue: MagicMock) -> Generator[TestClient, None, None]:
    """Create test client with mocked dependencies."""
    with patch("scheduler.main.JobQueue", return_value=mock_job_queue):
        # Override the dependency for jobs router
        app.dependency_overrides[get_job_queue] = lambda: mock_job_queue

        with TestClient(app) as test_client:
            yield test_client

        # Don't clear overrides - let other tests override them if needed


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns welcome message."""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["version"] == "0.1.0"


def test_health_check_healthy(client: TestClient, mock_redis: MagicMock) -> None:
    """Test health check endpoint when all components are healthy."""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "cpa-scheduler"
    assert data["version"] == "0.1.0"
    assert "components" in data
    assert "redis" in data["components"]
    assert data["components"]["redis"]["status"] == "healthy"

    # Verify Redis ping was called
    mock_redis.ping.assert_called_once()


def test_health_check_redis_unhealthy(client: TestClient, mock_redis: MagicMock) -> None:
    """Test health check endpoint when Redis is unhealthy."""
    # Make Redis ping fail
    mock_redis.ping.side_effect = Exception("Connection refused")

    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["redis"]["status"] == "unhealthy"
    assert "error" in data["components"]["redis"]


def test_health_check_redis_not_connected(client: TestClient) -> None:
    """Test health check endpoint when Redis is not connected."""
    with patch("scheduler.main.job_queue", None):
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["redis"]["status"] == "not_connected"


def test_cors_headers(client: TestClient) -> None:
    """Test CORS headers are present."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


def test_validation_error_handler(client: TestClient) -> None:
    """Test validation error handler returns proper error response."""
    # This will trigger a validation error on the /jobs endpoint
    response = client.post(
        "/jobs",
        json={"invalid": "data"},  # Missing required fields
    )

    # Should return 422 for validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "details" in data  # Custom error handler uses "details"
    assert "error" in data
    assert data["error"] == "validation_error"


def test_openapi_docs_available(client: TestClient) -> None:
    """Test OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK

    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK

    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["info"]["title"] == "cpa-scheduler"
    assert data["info"]["version"] == "0.1.0"


def test_global_exception_handler(client: TestClient, mock_redis: MagicMock) -> None:
    """Test global exception handler catches unhandled exceptions."""
    # Make Redis ping raise an exception that's not caught
    mock_redis.ping.side_effect = RuntimeError("Unexpected error")

    # Patch the logger to not raise, but the exception should still be caught
    with patch("scheduler.main.logger"):
        response = client.get("/health")

        # The exception should be caught and health should be degraded
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["redis"]["status"] == "unhealthy"


def test_lifespan_startup_shutdown(mock_job_queue: MagicMock) -> None:
    """Test application lifespan (startup and shutdown)."""
    with patch("scheduler.main.JobQueue", return_value=mock_job_queue):
        from scheduler.main import app

        # Simulate startup and shutdown using context manager
        with TestClient(app):
            # Verify JobQueue was connected
            mock_job_queue.connect.assert_called_once()

        # Verify JobQueue was closed on shutdown
        mock_job_queue.close.assert_called_once()


def test_lifespan_redis_connection_failure(mock_job_queue: MagicMock) -> None:
    """Test application handles Redis connection failure gracefully."""
    # Make connect fail
    mock_job_queue.connect.side_effect = Exception("Connection failed")

    with patch("scheduler.main.JobQueue", return_value=mock_job_queue):
        from scheduler.main import app

        # Should not raise exception, just log error
        with TestClient(app) as test_client:
            response = test_client.get("/health")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            # Should be degraded because Redis connection failed
            assert data["status"] == "degraded"

