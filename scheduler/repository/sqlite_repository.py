"""SQLite Repository implementation - Concrete repository for Job and Audit data."""
import json
from datetime import datetime, UTC
from typing import List, Optional, Any, Dict
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from scheduler.queue.job_queue import Job, JobStatus
from scheduler.repository.repository_interface import (
    JobRepository, 
    AuditRepository, 
    TaskRepository, 
    MessageRepository
)
from scheduler.core.task_graph import TaskGraph, ToDo, ActionType
from scheduler.core.lam_protocol import BaseMessage, MessageFactory

Base = declarative_base()

class JobModel(Base):
    """SQLAlchemy model for Jobs."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    intent = Column(String, nullable=False)
    task_graph = Column(JSON, nullable=False)
    status = Column(String, nullable=False)
    task_status = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

class AuditModel(Base):
    """SQLAlchemy model for Audit Logs."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(JSON, nullable=True)

class TaskModel(Base):
    """SQLAlchemy model for Tasks."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    action = Column(String, nullable=False)
    selector = Column(String, nullable=False)
    text = Column(String, nullable=True)
    timeout = Column(Integer, default=30)
    depends_on = Column(JSON, nullable=True)
    status = Column(String, default="pending")

class MessageModel(Base):
    """SQLAlchemy model for Agent Messages."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    job_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    type = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    intent = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    context = Column(JSON, nullable=False)

class SQLiteJobRepository(JobRepository):
    """SQLite implementation of JobRepository using SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def save(self, job: Job) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                job_dict = job.model_dump()
                # Ensure JSON fields are serializable
                db_job = JobModel(
                    id=job.id,
                    intent=job.intent,
                    task_graph=job_dict["task_graph"],
                    status=job.status.value,
                    task_status=job.task_status,
                    created_at=job.created_at,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    error=job.error,
                    retry_count=job.retry_count,
                    max_retries=job.max_retries
                )
                await session.merge(db_job)

    async def get(self, job_id: str) -> Optional[Job]:
        async with self.session_factory() as session:
            result = await session.execute(select(JobModel).where(JobModel.id == job_id))
            db_job = result.scalar_one_or_none()
            if not db_job:
                return None
            
            # Reconstruct TaskGraph
            task_graph = TaskGraph()
            tasks_data = db_job.task_graph.get("tasks", {})
            for task_id, task_data in tasks_data.items():
                task_graph.tasks[task_id] = ToDo(
                    action=ActionType(task_data["action"]),
                    selector=task_data["selector"],
                    text=task_data.get("text"),
                    timeout=task_data.get("timeout", 30.0),
                    depends_on=task_data.get("depends_on", [])
                )
            
            return Job(
                id=db_job.id,
                intent=db_job.intent,
                task_graph=task_graph,
                status=JobStatus(db_job.status),
                task_status=db_job.task_status,
                created_at=db_job.created_at,
                started_at=db_job.started_at,
                completed_at=db_job.completed_at,
                error=db_job.error,
                retry_count=db_job.retry_count,
                max_retries=db_job.max_retries
            )

    async def list(
        self, 
        limit: int = 100, 
        offset: int = 0, 
        status: Optional[JobStatus] = None
    ) -> List[Job]:
        async with self.session_factory() as session:
            query = select(JobModel).offset(offset).limit(limit)
            if status:
                query = query.where(JobModel.status == status.value)
            
            result = await session.execute(query)
            db_jobs = result.scalars().all()
            
            jobs = []
            for db_job in db_jobs:
                # Reconstruct TaskGraph (simplified for list)
                task_graph = TaskGraph()
                jobs.append(Job(
                    id=db_job.id,
                    intent=db_job.intent,
                    task_graph=task_graph, # Partial load or full load? Full for now.
                    status=JobStatus(db_job.status),
                    task_status=db_job.task_status,
                    created_at=db_job.created_at,
                    started_at=db_job.started_at,
                    completed_at=db_job.completed_at,
                    error=db_job.error,
                    retry_count=db_job.retry_count,
                    max_retries=db_job.max_retries
                ))
            return jobs

    async def update_status(self, job_id: str, status: JobStatus, error: Optional[str] = None) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                update_data = {"status": status.value}
                if error:
                    update_data["error"] = error
                
                if status == JobStatus.RUNNING:
                    update_data["started_at"] = datetime.now(UTC)
                elif status in (JobStatus.DONE, JobStatus.FAILED, JobStatus.CANCELLED):
                    update_data["completed_at"] = datetime.now(UTC)
                
                await session.execute(
                    update(JobModel).where(JobModel.id == job_id).values(**update_data)
                )

    async def delete(self, job_id: str) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                await session.execute(delete(JobModel).where(JobModel.id == job_id))

class SQLiteAuditRepository(AuditRepository):
    """SQLite implementation of AuditRepository."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def log_action(
        self, 
        job_id: str, 
        action: str, 
        status: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                db_audit = AuditModel(
                    job_id=job_id,
                    action=action,
                    status=status,
                    details=details
                )
                session.add(db_audit)

    async def get_logs(self, job_id: str) -> List[Dict[str, Any]]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(AuditModel).where(AuditModel.job_id == job_id).order_by(AuditModel.timestamp)
            )
            db_logs = result.scalars().all()
            return [
                {
                    "id": log.id,
                    "job_id": log.job_id,
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "status": log.status,
                    "details": log.details
                }
                for log in db_logs
            ]

class SQLiteTaskRepository(TaskRepository):
    """SQLite implementation of TaskRepository."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def save_tasks(self, job_id: str, tasks: Dict[str, Any]) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                for task_id, task_data in tasks.items():
                    db_task = TaskModel(
                        id=task_id,
                        job_id=job_id,
                        action=task_data["action"],
                        selector=task_data["selector"],
                        text=task_data.get("text"),
                        timeout=task_data.get("timeout", 30),
                        depends_on=task_data.get("depends_on", []),
                        status=task_data.get("status", "pending")
                    )
                    await session.merge(db_task)

    async def get_tasks(self, job_id: str) -> Dict[str, Any]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(TaskModel).where(TaskModel.job_id == job_id)
            )
            db_tasks = result.scalars().all()
            return {
                task.id: {
                    "action": task.action,
                    "selector": task.selector,
                    "text": task.text,
                    "timeout": task.timeout,
                    "depends_on": task.depends_on,
                    "status": task.status
                }
                for task in db_tasks
            }

class SQLiteMessageRepository(MessageRepository):
    """SQLite implementation of MessageRepository."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def save_message(self, message: BaseMessage) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                job_id = message.context.get("job_id") if message.context else None
                db_message = MessageModel(
                    id=message.id,
                    job_id=job_id,
                    timestamp=message.ts,
                    type=message.type,
                    sender=message.sender,
                    intent=message.intent,
                    payload=message.payload,
                    context=message.context
                )
                await session.merge(db_message)

    async def get_messages(self, job_id: Optional[str] = None) -> List[BaseMessage]:
        async with self.session_factory() as session:
            query = select(MessageModel)
            if job_id:
                query = query.where(MessageModel.job_id == job_id)
            
            result = await session.execute(query.order_by(MessageModel.timestamp))
            db_messages = result.scalars().all()
            
            return [
                MessageFactory.from_dict({
                    "id": msg.id,
                    "ts": msg.timestamp.isoformat(),
                    "type": msg.type,
                    "sender": msg.sender,
                    "intent": msg.intent,
                    "payload": msg.payload,
                    "context": msg.context
                })
                for msg in db_messages
            ]
