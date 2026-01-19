"""Tests for Job Queue."""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from scheduler.core.task_graph import ActionType, TaskGraph, ToDo
from scheduler.queue.job_queue import Job, JobQueue, JobStatus


class TestJob:
    """Tests for Job model."""

    def test_create_minimal_job(self) -> None:
        """Test creating a minimal job."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        
        job = Job(
            intent="send_mail",
            task_graph=graph,
        )
        
        assert job.intent == "send_mail"
        assert job.task_graph == graph
        assert job.status == JobStatus.PENDING
        assert job.retry_count == 0
        assert job.error is None

    def test_create_full_job(self) -> None:
        """Test creating a full job with all fields."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        
        now = datetime.now(UTC)
        job = Job(
            id="test-job-123",
            intent="send_mail",
            task_graph=graph,
            status=JobStatus.RUNNING,
            created_at=now,
            started_at=now,
            completed_at=now + timedelta(seconds=5),
            error="Test error",
            retry_count=2,
            max_retries=5,
        )
        
        assert job.id == "test-job-123"
        assert job.status == JobStatus.RUNNING
        assert job.retry_count == 2
        assert job.max_retries == 5
        assert job.error == "Test error"

    def test_job_serialization(self) -> None:
        """Test job serialization."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        
        job = Job(intent="send_mail", task_graph=graph)
        data = job.model_dump()
        
        assert data["intent"] == "send_mail"
        assert data["status"] == "pending"
        assert data["retry_count"] == 0


class TestJobQueue:
    """Tests for JobQueue class."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create a mock Redis client."""
        redis_mock = MagicMock()
        redis_mock.ping = AsyncMock(return_value=True)
        redis_mock.rpush = AsyncMock(return_value=1)
        redis_mock.lpop = AsyncMock(return_value=None)
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock(return_value=True)
        redis_mock.delete = AsyncMock(return_value=1)
        redis_mock.aclose = AsyncMock()
        return redis_mock

    @pytest.mark.asyncio
    async def test_create_job_queue(self, mock_redis: MagicMock) -> None:
        """Test creating a job queue."""
        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()
            assert queue is not None
            await queue.close()

    @pytest.mark.asyncio
    async def test_enqueue_job(self, mock_redis: MagicMock) -> None:
        """Test enqueueing a job."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(intent="send_mail", task_graph=graph)

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            job_id = await queue.enqueue(job)
            assert job_id is not None
            assert isinstance(job_id, str)

            await queue.close()

    @pytest.mark.asyncio
    async def test_dequeue_job(self, mock_redis: MagicMock) -> None:
        """Test dequeueing a job."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(intent="send_mail", task_graph=graph)

        # Mock lpop to return job ID
        mock_redis.lpop = AsyncMock(return_value=job.id.encode())

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            dequeued_job = await queue.dequeue()
            assert dequeued_job is not None
            assert dequeued_job.intent == "send_mail"

            await queue.close()

    @pytest.mark.asyncio
    async def test_dequeue_empty_queue(self, mock_redis: MagicMock) -> None:
        """Test dequeueing from empty queue."""
        mock_redis.lpop = AsyncMock(return_value=None)

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            job = await queue.dequeue()
            assert job is None

            await queue.close()

    @pytest.mark.asyncio
    async def test_get_job_status(self, mock_redis: MagicMock) -> None:
        """Test getting job status."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(id="test-123", intent="send_mail", task_graph=graph, status=JobStatus.RUNNING)

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            status = await queue.get_status("test-123")
            assert status == JobStatus.RUNNING

            await queue.close()

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, mock_redis: MagicMock) -> None:
        """Test getting status of non-existent job."""
        mock_redis.get = AsyncMock(return_value=None)

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            status = await queue.get_status("nonexistent")
            assert status is None

            await queue.close()

    @pytest.mark.asyncio
    async def test_update_job_status(self, mock_redis: MagicMock) -> None:
        """Test updating job status."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(id="test-123", intent="send_mail", task_graph=graph)

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            await queue.update_status("test-123", JobStatus.DONE)

            # Verify set was called
            mock_redis.set.assert_called_once()

            await queue.close()

    @pytest.mark.asyncio
    async def test_retry_job(self, mock_redis: MagicMock) -> None:
        """Test retrying a job."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(
            id="test-123",
            intent="send_mail",
            task_graph=graph,
            status=JobStatus.FAILED,
            retry_count=1,
        )

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            success = await queue.retry("test-123")
            assert success is True

            # Verify rpush was called (job re-enqueued)
            assert mock_redis.rpush.call_count >= 1

            await queue.close()

    @pytest.mark.asyncio
    async def test_retry_job_max_retries_exceeded(self, mock_redis: MagicMock) -> None:
        """Test retrying a job that exceeded max retries."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(
            id="test-123",
            intent="send_mail",
            task_graph=graph,
            status=JobStatus.FAILED,
            retry_count=3,
            max_retries=3,
        )

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            success = await queue.retry("test-123")
            assert success is False

            await queue.close()

    @pytest.mark.asyncio
    async def test_cancel_job(self, mock_redis: MagicMock) -> None:
        """Test canceling a job."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(id="test-123", intent="send_mail", task_graph=graph)

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            await queue.cancel("test-123")

            # Verify set was called to update status
            mock_redis.set.assert_called_once()

            await queue.close()

    @pytest.mark.asyncio
    async def test_get_job(self, mock_redis: MagicMock) -> None:
        """Test getting a job by ID."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        job = Job(id="test-123", intent="send_mail", task_graph=graph)

        # Mock get to return serialized job
        job_data = json.dumps(job.model_dump())
        mock_redis.get = AsyncMock(return_value=job_data.encode())

        with patch("scheduler.queue.job_queue.Redis.from_url", return_value=mock_redis):
            queue = JobQueue(redis_url="redis://localhost:6379")
            await queue.connect()

            retrieved_job = await queue.get_job("test-123")
            assert retrieved_job is not None
            assert retrieved_job.id == "test-123"
            assert retrieved_job.intent == "send_mail"

            await queue.close()

