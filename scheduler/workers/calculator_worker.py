"""Calculator Worker - Background worker for processing calculation jobs."""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# Add scheduler directory to path to support both local and Docker execution
scheduler_dir = Path(__file__).parent.parent
if str(scheduler_dir) not in sys.path:
    sys.path.insert(0, str(scheduler_dir))

# Try importing with scheduler prefix (local), fall back to direct import (Docker)
try:
    from scheduler.core.agent_registry import AgentRegistry
    from scheduler.orchestrator.calculator_orchestrator import CalculatorOrchestrator
    from scheduler.job_queue.job_queue import JobQueue, JobStatus
except ImportError:
    from core.agent_registry import AgentRegistry
    from orchestrator.calculator_orchestrator import CalculatorOrchestrator
    from job_queue.job_queue import JobQueue, JobStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True


async def main():
    """Main worker loop."""
    global shutdown_flag

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Get agents config path (different for local vs Docker)
    agents_config = os.getenv("AGENTS_CONFIG")
    if not agents_config:
        # Try to find the config file
        possible_paths = [
            "scheduler/config/agents.yaml",  # Local execution
            "config/agents.yaml",  # Docker execution
        ]
        for path in possible_paths:
            if Path(path).exists():
                agents_config = path
                break
        if not agents_config:
            agents_config = "config/agents.yaml"  # Default to Docker path

    logger.info("Starting calculator worker...")
    logger.info(f"Redis URL: {redis_url}")
    logger.info(f"Agents config: {agents_config}")

    # Initialize components
    job_queue = JobQueue(redis_url)
    await job_queue.connect()

    agent_registry = AgentRegistry(agents_config)
    orchestrator = CalculatorOrchestrator(agent_registry, job_queue)

    logger.info(f"Loaded {len(agent_registry.list_agents())} agents")
    logger.info("Worker ready, waiting for jobs...")

    try:
        while not shutdown_flag:
            try:
                # Dequeue job
                job = await job_queue.dequeue()

                if job:
                    logger.info(f"Processing job: {job.id} (intent: {job.intent})")

                    # Only process calculate intent
                    if job.intent == "calculate":
                        await orchestrator.process_calculation_job(job)
                    else:
                        logger.warning(f"Unknown intent: {job.intent}, skipping job {job.id}")
                        await job_queue.update_status(job.id, JobStatus.FAILED)
                        job.error = f"Unknown intent: {job.intent}"
                        await job_queue._save_job(job)
                else:
                    # No job available, wait a bit
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error processing job: {e}", exc_info=True)
                await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        logger.info("Shutting down worker...")
        await orchestrator.close()
        await job_queue.close()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
        sys.exit(0)

