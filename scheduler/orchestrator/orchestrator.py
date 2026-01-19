"""Task Orchestrator - Core logic for processing jobs and dispatching tasks."""
import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import httpx
from scheduler.config.settings import settings
from scheduler.core.task_graph import TaskStatus, ToDo
from scheduler.queue.job_queue import Job, JobQueue, JobStatus
from scheduler.security.policies import PolicyEngine
from scheduler.telemetry.telemetry import TelemetryService

logger = logging.getLogger(__name__)

class Orchestrator:
    """Task Orchestrator - Processes jobs from the queue and dispatches tasks to agents."""

    def __init__(
        self, 
        job_queue: JobQueue, 
        policy_engine: Optional[PolicyEngine] = None,
        telemetry: Optional[TelemetryService] = None
    ):
        """Initialize orchestrator.

        Args:
            job_queue: Job queue instance
            policy_engine: Security policy engine
            telemetry: Telemetry service
        """
        self.job_queue = job_queue
        self.policy_engine = policy_engine or PolicyEngine()
        self.telemetry = telemetry
        self.running = False
        self._poll_interval = 1.0  # seconds
        # Use a single httpx client for connection pooling
        self._http_client = httpx.AsyncClient(timeout=30.0)

    async def start(self):
        """Start the orchestrator polling loop."""
        self.running = True
        logger.info("Orchestrator started")
        while self.running:
            try:
                # 1. Fetch job from queue
                job = await self.job_queue.dequeue()
                if job:
                    logger.info(f"Processing job {job.id} ({job.intent})")
                    # 2. Run the job processing in the background so we can continue polling
                    asyncio.create_task(self.process_job(job))
                else:
                    await asyncio.sleep(self._poll_interval)
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}", exc_info=True)
                await asyncio.sleep(self._poll_interval)

    async def stop(self):
        """Stop the orchestrator polling loop."""
        self.running = False
        await self._http_client.aclose()
        logger.info("Orchestrator stopped")

    async def process_job(self, job: Job):
        """Process a single job through its task graph.

        Args:
            job: Job instance
        """
        try:
            # 1. Update status to RUNNING
            if job.status == JobStatus.PENDING:
                await self.job_queue.update_status(job.id, JobStatus.RUNNING)
                job.status = JobStatus.RUNNING
                if self.telemetry:
                    self.telemetry.record_job(status="started")

            # 2. Initial task status setup
            if not job.task_status:
                for task_id in job.task_graph.tasks:
                    job.task_status[task_id] = TaskStatus.PENDING
                # Persist the initial task status
                # (Ideally JobQueue.enqueue already did this, but just in case)
                await self.job_queue.update_status(job.id, JobStatus.RUNNING)

            # 3. Execution loop
            while job.status == JobStatus.RUNNING:
                # Find tasks that are ready to run (dependencies met and status is PENDING)
                ready_task_ids = self._get_ready_tasks(job)
                
                if not ready_task_ids:
                    # Check terminal conditions
                    all_status = list(job.task_status.values())
                    if all(s == TaskStatus.DONE for s in all_status):
                        logger.info(f"Job {job.id} completed successfully")
                        await self.job_queue.update_status(job.id, JobStatus.DONE)
                        if self.telemetry:
                            self.telemetry.record_job(status="success")
                        break
                    
                    if any(s == TaskStatus.FAILED for s in all_status):
                        logger.info(f"Job {job.id} failed due to task failure")
                        await self.job_queue.update_status(job.id, JobStatus.FAILED)
                        if self.telemetry:
                            self.telemetry.record_job(status="failed")
                        break
                    
                    # If we have tasks RUNNING but none ready, we must wait for them to finish
                    # The lam_handler will update Redis, so we need to refresh the Job data.
                    await asyncio.sleep(2.0)
                    fresh_job = await self.job_queue.get_job(job.id)
                    if not fresh_job:
                        logger.error(f"Job {job.id} disappeared from queue")
                        break
                    
                    job = fresh_job
                    continue

                # Dispatch ready tasks
                for task_id in ready_task_ids:
                    task = job.task_graph.get_task(task_id)
                    if not task:
                        continue
                    
                    # Pick an agent and send the task
                    success = await self.dispatch_task(job, task_id, task)
                    if success:
                        # Mark as running in Redis and locally
                        await self.job_queue.update_task_status(job.id, task_id, TaskStatus.RUNNING)
                        job.task_status[task_id] = TaskStatus.RUNNING
                    else:
                        # Dispatch failed (e.g., no agent found)
                        await self.job_queue.update_task_status(job.id, task_id, TaskStatus.FAILED)
                        await self.job_queue.update_status(
                            job.id, 
                            JobStatus.FAILED, 
                            error=f"Failed to dispatch task {task_id}"
                        )
                        job.status = JobStatus.FAILED
                        break
                
                # Small sleep before next check to avoid tight loop
                await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"Fatal error processing job {job.id}: {e}", exc_info=True)
            await self.job_queue.update_status(job.id, JobStatus.FAILED, error=str(e))

    def _get_ready_tasks(self, job: Job) -> List[str]:
        """Find tasks whose dependencies are met and are still pending."""
        ready = []
        for task_id, task in job.task_graph.tasks.items():
            if job.task_status.get(task_id) != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are DONE
            deps_met = True
            for dep_id in task.depends_on:
                if job.task_status.get(dep_id) != TaskStatus.DONE:
                    deps_met = False
                    break
            
            if deps_met:
                ready.append(task_id)
        return ready

    async def dispatch_task(self, job: Job, task_id: str, task: ToDo) -> bool:
        """Dispatch task to an available agent."""
        logger.info(f"Dispatching task {task_id} ({task.action}) for job {job.id}")
        
        # 0. Validate with PolicyEngine
        if not self.policy_engine.validate_task(task.action.value, task.selector or ""):
            logger.error(f"Task {task_id} blocked by security policy")
            return False

        # 1. Find an agent
        agent_url = await self._find_agent(task)
        if not agent_url:
            logger.error(f"No suitable agent found for task {task_id}")
            return False

        # 2. Send task request
        try:
            payload = {
                "task_id": task_id,
                "action": task.action,
                "selector": task.selector,
                "text": task.text,
                "timeout": task.timeout,
                "metadata": {
                    "job_id": job.id,
                    "conversationId": job.id  # Used by LAM messages to correlate back to this job
                }
            }
            
            response = await self._http_client.post(f"{agent_url}/tasks", json=payload)
            response.raise_for_status()
            logger.info(f"Task {task_id} successfully dispatched to {agent_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to send task {task_id} to agent {agent_url}: {e}")
            return False

    async def _find_agent(self, task: ToDo) -> Optional[str]:
        """Find an active agent that can handle the task."""
        try:
            # Query the Agent Registry (Server)
            response = await self._http_client.get(settings.agent_registry_url)
            response.raise_for_status()
            agents = response.json()
            
            for agent in agents:
                if agent.get("is_active"):
                    ip = agent.get("ip_address")
                    port = agent.get("port")
                    
                    if not ip:
                        continue
                    
                    # Construct agent URL
                    if port:
                        return f"http://{ip}:{port}"
                    return f"http://{ip}"
            
            return None
        except Exception as e:
            logger.error(f"Failed to fetch agents from registry: {e}")
            return None
