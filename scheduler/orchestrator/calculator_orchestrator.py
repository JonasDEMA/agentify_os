"""Calculator Orchestrator - Coordinates calculation and formatting agents."""

import logging
import sys
from pathlib import Path
from uuid import uuid4

import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scheduler.core.agent_registry import AgentRegistry
from scheduler.core.lam_protocol import InformMessage, MessageType, RequestMessage
from scheduler.queue.job_queue import Job, JobQueue, JobStatus

logger = logging.getLogger(__name__)


class CalculatorOrchestrator:
    """Orchestrator for calculator operations."""

    def __init__(self, agent_registry: AgentRegistry, job_queue: JobQueue):
        """Initialize calculator orchestrator.

        Args:
            agent_registry: Agent registry instance
            job_queue: Job queue instance
        """
        self.agent_registry = agent_registry
        self.job_queue = job_queue
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()

    async def process_calculation_job(self, job: Job) -> None:
        """Process a calculation job.

        Args:
            job: Job to process
        """
        try:
            logger.info(f"Processing calculation job: {job.id}")

            # Update job status to running
            await self.job_queue.update_status(job.id, JobStatus.RUNNING)

            # Extract parameters from task graph selector
            task_id = list(job.task_graph.tasks.keys())[0] if job.task_graph.tasks else None
            if not task_id:
                raise ValueError("No tasks in job")
            
            task = job.task_graph.tasks[task_id]
            # Parse selector which contains: calculator:operator:num1:num2:locale:decimals
            parts = task.selector.split(":")
            if len(parts) < 4:
                raise ValueError(f"Invalid calculator task selector: {task.selector}")
            
            operator = parts[1]
            num1 = float(parts[2])
            num2 = float(parts[3])
            locale = parts[4] if len(parts) > 4 else "en-US"
            decimals = int(parts[5]) if len(parts) > 5 else 2

            conversation_id = str(uuid4())

            # Step 1: Call calculation agent
            logger.info(f"Calling calculation agent: {num1} {operator} {num2}")
            calc_result = await self._call_calculation_agent(
                num1, num2, operator, conversation_id
            )

            # Step 2: Call formatting agent
            logger.info(f"Calling formatting agent: {calc_result} ({locale}, {decimals} decimals)")
            formatted_result = await self._call_formatting_agent(
                calc_result, locale, decimals, conversation_id
            )

            # Update job with final result
            result = {
                "num1": num1,
                "num2": num2,
                "operator": operator,
                "locale": locale,
                "decimals": decimals,
                "raw_result": calc_result,
                "formatted_result": formatted_result,
            }
            # Store result in Redis
            import json
            job_data = await self.job_queue.get_job(job.id)
            if job_data:
                job_key = self.job_queue._get_job_key(job.id)
                job_dict = job_data.model_dump()
                job_dict["result"] = result
                await self.job_queue.redis.set(job_key, json.dumps(job_dict))
            
            await self.job_queue.update_status(job.id, JobStatus.DONE)

            logger.info(
                f"Calculation job completed: {job.id} -> {formatted_result}"
            )

        except Exception as e:
            logger.error(f"Calculation job failed: {job.id} - {e}", exc_info=True)
            await self.job_queue.update_status(job.id, JobStatus.FAILED, error=str(e))

    async def _call_calculation_agent(
        self, num1: float, num2: float, operator: str, conversation_id: str
    ) -> float:
        """Call calculation agent via LAM protocol.

        Args:
            num1: First number
            num2: Second number
            operator: Operator
            conversation_id: Conversation ID for tracking

        Returns:
            Calculation result

        Raises:
            Exception: If agent call fails
        """
        # Get calculation agent from registry
        agent = self.agent_registry.get_agent_by_capability("calculate")
        if not agent:
            raise ValueError("Calculation agent not found in registry")

        # Create LAM request message
        request = RequestMessage(
            sender="agent://orchestrator/calculator",
            intent="calculate",
            payload={
                "num1": num1,
                "num2": num2,
                "operator": operator,
            },
            correlation={"conversation_id": conversation_id},
        )

        # Send request to agent
        try:
            response = await self.http_client.post(
                f"{agent.endpoint}/tasks",
                json=request.to_dict(),
            )
            response.raise_for_status()

            # Parse LAM response
            response_data = response.json()

            # Check if it's a failure message
            if response_data.get("type") == MessageType.FAILURE.value:
                error = response_data.get("payload", {}).get("error", "Unknown error")
                raise ValueError(f"Calculation agent error: {error}")

            # Extract result from inform message
            if response_data.get("type") != MessageType.INFORM.value:
                raise ValueError(f"Unexpected message type: {response_data.get('type')}")

            result = response_data.get("payload", {}).get("result")
            if result is None:
                raise ValueError("No result in agent response")

            return float(result)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling calculation agent: {e}")
            raise ValueError(f"Failed to call calculation agent: {e}") from e

    async def _call_formatting_agent(
        self, value: float, locale: str, decimals: int, conversation_id: str
    ) -> str:
        """Call formatting agent via LAM protocol.

        Args:
            value: Value to format
            locale: Locale for formatting
            decimals: Number of decimal places
            conversation_id: Conversation ID for tracking

        Returns:
            Formatted string

        Raises:
            Exception: If agent call fails
        """
        # Get formatting agent from registry
        agent = self.agent_registry.get_agent_by_capability("format")
        if not agent:
            raise ValueError("Formatting agent not found in registry")

        # Create LAM request message
        request = RequestMessage(
            sender="agent://orchestrator/calculator",
            intent="format",
            payload={
                "value": value,
                "locale": locale,
                "decimals": decimals,
            },
            correlation={"conversation_id": conversation_id},
        )

        # Send request to agent
        try:
            response = await self.http_client.post(
                f"{agent.endpoint}/tasks",
                json=request.to_dict(),
            )
            response.raise_for_status()

            # Parse LAM response
            response_data = response.json()

            # Check if it's a failure message
            if response_data.get("type") == MessageType.FAILURE.value:
                error = response_data.get("payload", {}).get("error", "Unknown error")
                raise ValueError(f"Formatting agent error: {error}")

            # Extract result from inform message
            if response_data.get("type") != MessageType.INFORM.value:
                raise ValueError(f"Unexpected message type: {response_data.get('type')}")

            formatted = response_data.get("payload", {}).get("formatted")
            if formatted is None:
                raise ValueError("No formatted result in agent response")

            return str(formatted)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling formatting agent: {e}")
            raise ValueError(f"Failed to call formatting agent: {e}") from e

