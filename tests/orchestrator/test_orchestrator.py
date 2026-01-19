"""Tests for Task Orchestrator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from scheduler.orchestrator.orchestrator import Orchestrator
from scheduler.queue.job_queue import Job, JobStatus
from scheduler.core.task_graph import TaskGraph, ToDo, ActionType, TaskStatus

@pytest.fixture
def mock_job_queue():
    """Mock JobQueue."""
    mock = MagicMock()
    mock.dequeue = AsyncMock()
    mock.get_job = AsyncMock()
    mock.update_status = AsyncMock()
    mock.update_task_status = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_orchestrator_process_simple_job(mock_job_queue):
    """Test processing a simple job with one task."""
    # Setup job
    graph = TaskGraph()
    task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
    job = Job(id="test-job", intent="test", task_graph=graph)
    
    orchestrator = Orchestrator(mock_job_queue)
    
    # Mock agent registry and agent task endpoint
    with patch("httpx.AsyncClient.get") as mock_get, \
         patch("httpx.AsyncClient.post") as mock_post:
        
        # Registry returns one active agent
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = [
            {"is_active": True, "ip_address": "127.0.0.1", "port": 8002}
        ]
        
        # Agent accepts the task
        mock_post.return_value = MagicMock(status_code=200)
        
        # Mocking the refresh loop
        # 1. After dispatch, task is RUNNING
        job_running = job.model_copy()
        job_running.status = JobStatus.RUNNING
        job_running.task_status = {task_id: TaskStatus.RUNNING}
        
        # 2. Simulate external update (LAM handler) to DONE
        job_done = job.model_copy()
        job_done.status = JobStatus.RUNNING
        job_done.task_status = {task_id: TaskStatus.DONE}
        
        mock_job_queue.get_job.side_effect = [job_running, job_done]
        
        await orchestrator.process_job(job)
        
        # Verify dispatch
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "http://127.0.0.1:8002/tasks" == args[0]
        assert kwargs["json"]["task_id"] == task_id
        
        # Verify status updates
        mock_job_queue.update_status.assert_any_call(job.id, JobStatus.RUNNING)
        mock_job_queue.update_task_status.assert_any_call(job.id, task_id, TaskStatus.RUNNING)
        mock_job_queue.update_status.assert_any_call(job.id, JobStatus.DONE)

@pytest.mark.asyncio
async def test_orchestrator_find_agent_failure(mock_job_queue):
    """Test behavior when no agent is found."""
    graph = TaskGraph()
    task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
    job = Job(id="test-job", intent="test", task_graph=graph)
    
    orchestrator = Orchestrator(mock_job_queue)
    
    with patch("httpx.AsyncClient.get") as mock_get:
        # Registry returns no active agents
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = []
        
        await orchestrator.process_job(job)
        
        # Verify job failure
        mock_job_queue.update_status.assert_any_call(
            job.id, JobStatus.FAILED, error=f"Failed to dispatch task {task_id}"
        )

@pytest.mark.asyncio
async def test_orchestrator_task_dependency(mock_job_queue):
    """Test that tasks are executed in correct order based on dependencies."""
    graph = TaskGraph()
    t1 = graph.add_task(ToDo(action=ActionType.OPEN_APP, selector="app"))
    t2 = graph.add_task(ToDo(action=ActionType.CLICK, selector="btn", depends_on=[t1]))
    
    job = Job(id="dependency-job", intent="test", task_graph=graph)
    orchestrator = Orchestrator(mock_job_queue)
    
    with patch("httpx.AsyncClient.get") as mock_get, \
         patch("httpx.AsyncClient.post") as mock_post:
        
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = [{"is_active": True, "ip_address": "127.0.0.1", "port": 8002}]
        mock_post.return_value = MagicMock(status_code=200)
        
        # Mocking the refresh loop
        # State 1: T1 RUNNING, T2 PENDING
        job_s1 = job.model_copy()
        job_s1.status = JobStatus.RUNNING
        job_s1.task_status = {t1: TaskStatus.RUNNING, t2: TaskStatus.PENDING}
        
        # State 2: T1 DONE, T2 PENDING (T2 should be dispatched now)
        job_s2 = job.model_copy()
        job_s2.status = JobStatus.RUNNING
        job_s2.task_status = {t1: TaskStatus.DONE, t2: TaskStatus.PENDING}
        
        # State 3: T1 DONE, T2 RUNNING
        job_s3 = job.model_copy()
        job_s3.status = JobStatus.RUNNING
        job_s3.task_status = {t1: TaskStatus.DONE, t2: TaskStatus.RUNNING}
        
        # State 4: T1 DONE, T2 DONE
        job_s4 = job.model_copy()
        job_s4.status = JobStatus.RUNNING
        job_s4.task_status = {t1: TaskStatus.DONE, t2: TaskStatus.DONE}
        
        mock_job_queue.get_job.side_effect = [job_s1, job_s2, job_s3, job_s4]
        
        await orchestrator.process_job(job)
        
        # Verify both tasks were dispatched
        assert mock_post.call_count == 2
        # T1 first, then T2
        assert mock_post.call_args_list[0][1]["json"]["task_id"] == t1
        assert mock_post.call_args_list[1][1]["json"]["task_id"] == t2
