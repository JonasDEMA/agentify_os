"""Tests for SQLite Repository."""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from scheduler.repository.sqlite_repository import (
    Base, 
    SQLiteJobRepository, 
    SQLiteAuditRepository,
    SQLiteTaskRepository,
    SQLiteMessageRepository
)
from scheduler.queue.job_queue import Job, JobStatus
from scheduler.core.task_graph import TaskGraph, ToDo, ActionType
from scheduler.core.lam_protocol import MessageFactory, MessageType

@pytest.fixture
async def session_factory():
    """Create a fresh in-memory database and session factory."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()

@pytest.mark.asyncio
async def test_job_repo_save_get(session_factory):
    """Test saving and retrieving a job."""
    repo = SQLiteJobRepository(session_factory)
    
    task_graph = TaskGraph()
    task_graph.add_task(ToDo(
        action=ActionType.CLICK,
        selector="button",
        text="Submit"
    ))
    
    job = Job(intent="test_intent", task_graph=task_graph)
    await repo.save(job)
    
    retrieved_job = await repo.get(job.id)
    assert retrieved_job is not None
    assert retrieved_job.id == job.id
    assert retrieved_job.intent == "test_intent"
    assert len(retrieved_job.task_graph.tasks) == 1
    assert retrieved_job.status == JobStatus.PENDING

@pytest.mark.asyncio
async def test_job_repo_list_filter(session_factory):
    """Test listing and filtering jobs."""
    repo = SQLiteJobRepository(session_factory)
    
    job1 = Job(intent="intent1", task_graph=TaskGraph(), status=JobStatus.DONE)
    job2 = Job(intent="intent2", task_graph=TaskGraph(), status=JobStatus.PENDING)
    
    await repo.save(job1)
    await repo.save(job2)
    
    all_jobs = await repo.list()
    assert len(all_jobs) == 2
    
    pending_jobs = await repo.list(status=JobStatus.PENDING)
    assert len(pending_jobs) == 1
    assert pending_jobs[0].id == job2.id

@pytest.mark.asyncio
async def test_job_repo_update_status(session_factory):
    """Test updating job status."""
    repo = SQLiteJobRepository(session_factory)
    job = Job(intent="test", task_graph=TaskGraph())
    await repo.save(job)
    
    await repo.update_status(job.id, JobStatus.RUNNING)
    updated_job = await repo.get(job.id)
    assert updated_job.status == JobStatus.RUNNING
    assert updated_job.started_at is not None

@pytest.mark.asyncio
async def test_audit_repo_log_get(session_factory):
    """Test logging and retrieving audit entries."""
    repo = SQLiteAuditRepository(session_factory)
    job_id = "test_job_1"
    
    await repo.log_action(job_id, "start_execution", "success", {"info": "started"})
    await repo.log_action(job_id, "click_button", "success", {"button": "submit"})
    
    logs = await repo.get_logs(job_id)
    assert len(logs) == 2
    assert logs[0]["action"] == "start_execution"
    assert logs[1]["action"] == "click_button"
    assert logs[0]["details"]["info"] == "started"

@pytest.mark.asyncio
async def test_task_repo_save_get(session_factory):
    """Test saving and retrieving tasks."""
    repo = SQLiteTaskRepository(session_factory)
    job_id = "test_job_task"
    
    tasks = {
        "task1": {
            "action": "click",
            "selector": "#submit",
            "depends_on": [],
            "status": "pending"
        },
        "task2": {
            "action": "type",
            "selector": "#input",
            "text": "hello",
            "depends_on": ["task1"],
            "status": "pending"
        }
    }
    
    await repo.save_tasks(job_id, tasks)
    
    retrieved_tasks = await repo.get_tasks(job_id)
    assert len(retrieved_tasks) == 2
    assert retrieved_tasks["task1"]["action"] == "click"
    assert retrieved_tasks["task2"]["depends_on"] == ["task1"]

@pytest.mark.asyncio
async def test_message_repo_save_get(session_factory):
    """Test saving and retrieving messages."""
    repo = SQLiteMessageRepository(session_factory)
    
    msg = MessageFactory.create(
        MessageType.INFORM,
        sender="agent://test",
        intent="test_intent",
        payload={"result": "success"},
        context={"job_id": "test_job_msg"}
    )
    
    await repo.save_message(msg)
    
    messages = await repo.get_messages(job_id="test_job_msg")
    assert len(messages) == 1
    assert messages[0].sender == "agent://test"
    assert messages[0].payload["result"] == "success"
