"""Tests for Job API endpoints."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from scheduler.api.jobs import get_job_queue
from scheduler.core.task_graph import ActionType, TaskGraph, ToDo
from scheduler.main import app
from scheduler.queue.job_queue import Job, JobStatus


@pytest.fixture
def mock_redis() -> MagicMock:
    """Create mock Redis client."""
    mock = MagicMock()
    mock.ping = AsyncMock(return_value=True)
    mock.close = AsyncMock()
    mock.keys = AsyncMock(return_value=[])
    mock.get = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_job_queue(mock_redis: MagicMock) -> MagicMock:
    """Create mock JobQueue."""
    mock = MagicMock()
    mock.redis = mock_redis
    mock.connect = AsyncMock()
    mock.close = AsyncMock()
    mock.enqueue = AsyncMock()
    mock.get_job = AsyncMock(return_value=None)
    mock.list_jobs = AsyncMock(return_value=[])
    mock.cancel = AsyncMock()
    mock.retry = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def client(mock_job_queue: MagicMock) -> Generator[TestClient, None, None]:
    """Create test client with mocked JobQueue."""
    # Override the dependency using FastAPI's dependency_overrides
    app.dependency_overrides[get_job_queue] = lambda: mock_job_queue

    with TestClient(app) as test_client:
        yield test_client

    # Don't clear overrides - let other tests override them if needed


@pytest.fixture
def sample_task_graph() -> TaskGraph:
    """Create sample task graph."""
    graph = TaskGraph()
    task1_id = graph.add_task(
        ToDo(
            action=ActionType.OPEN_APP,
            selector="notepad.exe",
            timeout=10.0,
        )
    )
    graph.add_task(
        ToDo(
            action=ActionType.TYPE,
            selector="input",
            text="Hello World",
            depends_on=[task1_id],
        )
    )
    return graph


@pytest.fixture
def sample_job(sample_task_graph: TaskGraph) -> Job:
    """Create sample job."""
    return Job(
        id="test-job-123",
        intent="test_intent",
        task_graph=sample_task_graph,
        status=JobStatus.PENDING,
        max_retries=3,
    )


def test_create_job_success(client: TestClient, mock_job_queue: MagicMock) -> None:
    """Test successful job creation."""
    request_data = {
        "intent": "test_intent",
        "tasks": {
            "task1": {
                "action": "open_app",
                "selector": "notepad.exe",
                "timeout": 10.0,
                "depends_on": [],
            },
            "task2": {
                "action": "type",
                "selector": "input",
                "text": "Hello World",
                "timeout": 30.0,
                "depends_on": ["task1"],
            },
        },
        "max_retries": 3,
    }

    response = client.post("/jobs", json=request_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["intent"] == "test_intent"
    assert data["status"] == "pending"
    assert data["task_count"] == 2
    assert data["max_retries"] == 3
    assert "id" in data
    assert "created_at" in data

    # Verify enqueue was called
    mock_job_queue.enqueue.assert_called_once()


def test_create_job_invalid_task_graph(client: TestClient) -> None:
    """Test job creation with invalid task graph (circular dependency)."""
    request_data = {
        "intent": "test_intent",
        "tasks": {
            "task1": {
                "action": "open_app",
                "selector": "notepad.exe",
                "depends_on": ["task2"],  # Circular dependency
            },
            "task2": {
                "action": "type",
                "selector": "input",
                "text": "Hello",
                "depends_on": ["task1"],  # Circular dependency
            },
        },
    }

    response = client.post("/jobs", json=request_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid task graph" in response.json()["detail"]


def test_create_job_missing_intent(client: TestClient) -> None:
    """Test job creation with missing intent."""
    request_data = {
        "tasks": {
            "task1": {
                "action": "open_app",
                "selector": "notepad.exe",
            },
        },
    }

    response = client.post("/jobs", json=request_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_jobs_empty(client: TestClient, mock_redis: MagicMock) -> None:
    """Test listing jobs when queue is empty."""
    mock_redis.keys.return_value = []

    response = client.get("/jobs")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["jobs"] == []
    assert data["total"] == 0


def test_list_jobs_with_results(
    client: TestClient, mock_redis: MagicMock, sample_job: Job
) -> None:
    """Test listing jobs with results."""
    # Mock Redis to return job data
    # Create a JSON representation manually (without TaskGraph)
    import json

    job_json = json.dumps(
        {
            "id": "test-job-123",
            "intent": "test_intent",
            "task_graph": {"tasks": {}},
            "status": "pending",
            "created_at": sample_job.created_at.isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "retry_count": 0,
            "max_retries": 3,
        }
    )

    mock_redis.keys.return_value = [b"job:test-job-123"]
    mock_redis.get.return_value = job_json

    response = client.get("/jobs")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["id"] == "test-job-123"
    assert data["jobs"][0]["intent"] == "test_intent"


def test_list_jobs_with_status_filter(
    client: TestClient, mock_redis: MagicMock, sample_job: Job
) -> None:
    """Test listing jobs with status filter."""
    # Create jobs with different statuses
    import json

    job1_json = json.dumps(
        {
            "id": "job1",
            "intent": "test_intent",
            "task_graph": {"tasks": {}},
            "status": "pending",
            "created_at": sample_job.created_at.isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "retry_count": 0,
            "max_retries": 3,
        }
    )

    job2_json = json.dumps(
        {
            "id": "job2",
            "intent": "test_intent",
            "task_graph": {"tasks": {}},
            "status": "running",
            "created_at": sample_job.created_at.isoformat(),
            "started_at": sample_job.created_at.isoformat(),
            "completed_at": None,
            "error": None,
            "retry_count": 0,
            "max_retries": 3,
        }
    )

    mock_redis.keys.return_value = [b"job:job1", b"job:job2"]
    mock_redis.get.side_effect = [job1_json, job2_json]

    response = client.get("/jobs?status_filter=pending")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["jobs"][0]["status"] == "pending"


def test_list_jobs_with_pagination(
    client: TestClient, mock_redis: MagicMock, sample_job: Job
) -> None:
    """Test listing jobs with pagination."""
    # Create 5 jobs
    import json

    jobs_json = []
    for i in range(5):
        job_json = json.dumps(
            {
                "id": f"job{i}",
                "intent": "test_intent",
                "task_graph": {"tasks": {}},
                "status": "pending",
                "created_at": sample_job.created_at.isoformat(),
                "started_at": None,
                "completed_at": None,
                "error": None,
                "retry_count": 0,
                "max_retries": 3,
            }
        )
        jobs_json.append(job_json)

    mock_redis.keys.return_value = [f"job:job{i}".encode() for i in range(5)]
    mock_redis.get.side_effect = jobs_json

    response = client.get("/jobs?limit=2&offset=1")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 5
    assert len(data["jobs"]) == 2


def test_get_job_success(client: TestClient, mock_job_queue: MagicMock, sample_job: Job) -> None:
    """Test getting job by ID."""
    mock_job_queue.get_job.return_value = sample_job

    response = client.get(f"/jobs/{sample_job.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_job.id
    assert data["intent"] == sample_job.intent
    assert data["status"] == sample_job.status.value


def test_get_job_not_found(client: TestClient, mock_job_queue: MagicMock) -> None:
    """Test getting non-existent job."""
    mock_job_queue.get_job.return_value = None

    response = client.get("/jobs/nonexistent")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_cancel_job_success(client: TestClient, mock_job_queue: MagicMock, sample_job: Job) -> None:
    """Test cancelling a job."""
    mock_job_queue.get_job.return_value = sample_job

    response = client.delete(f"/jobs/{sample_job.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_job_queue.cancel.assert_called_once_with(sample_job.id)


def test_cancel_job_not_found(client: TestClient, mock_job_queue: MagicMock) -> None:
    """Test cancelling non-existent job."""
    mock_job_queue.get_job.return_value = None

    response = client.delete("/jobs/nonexistent")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cancel_job_already_done(
    client: TestClient, mock_job_queue: MagicMock, sample_job: Job
) -> None:
    """Test cancelling already completed job."""
    sample_job.status = JobStatus.DONE
    mock_job_queue.get_job.return_value = sample_job

    response = client.delete(f"/jobs/{sample_job.id}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already done" in response.json()["detail"]


def test_retry_job_success(client: TestClient, mock_job_queue: MagicMock, sample_job: Job) -> None:
    """Test retrying a failed job."""
    sample_job.status = JobStatus.FAILED
    sample_job.error = "Test error"
    mock_job_queue.get_job.side_effect = [sample_job, sample_job]  # Called twice
    mock_job_queue.retry.return_value = True

    response = client.post(f"/jobs/{sample_job.id}/retry")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_job.id
    mock_job_queue.retry.assert_called_once_with(sample_job.id)


def test_retry_job_not_failed(
    client: TestClient, mock_job_queue: MagicMock, sample_job: Job
) -> None:
    """Test retrying a job that is not in failed state."""
    sample_job.status = JobStatus.RUNNING
    mock_job_queue.get_job.return_value = sample_job

    response = client.post(f"/jobs/{sample_job.id}/retry")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not in failed state" in response.json()["detail"]


def test_retry_job_max_retries_exceeded(
    client: TestClient, mock_job_queue: MagicMock, sample_job: Job
) -> None:
    """Test retrying a job that has exceeded max retries."""
    sample_job.status = JobStatus.FAILED
    mock_job_queue.get_job.return_value = sample_job
    mock_job_queue.retry.return_value = False  # Max retries exceeded

    response = client.post(f"/jobs/{sample_job.id}/retry")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceeded maximum retries" in response.json()["detail"]


def test_retry_job_not_found(client: TestClient, mock_job_queue: MagicMock) -> None:
    """Test retrying non-existent job."""
    mock_job_queue.get_job.return_value = None

    response = client.post("/jobs/nonexistent/retry")

    assert response.status_code == status.HTTP_404_NOT_FOUND

