"""LAM Message Handler API.

Standardized endpoint for receiving messages from agents.
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from scheduler.api.jobs import get_job_queue
from scheduler.core.lam_protocol import MessageFactory, MessageType
from scheduler.queue.job_queue import JobQueue, JobStatus

logger = structlog.get_logger()

router = APIRouter(prefix="/lam", tags=["LAM"])


class MessageAcknowledgement(BaseModel):
    """Acknowledgement response for received messages."""

    status: str = Field("received", description="Status of the message reception")
    message_id: str = Field(..., description="The ID of the received message")


@router.post("/message", response_model=MessageAcknowledgement, status_code=status.HTTP_202_ACCEPTED)
async def handle_agent_message(
    message_dict: dict,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> MessageAcknowledgement:
    """Handle incoming agent message.

    Validates the message using Agent Communication Protocol and routes it to the appropriate handler.
    """
    try:
        # Validate and create message object
        message = MessageFactory.from_dict(message_dict)
        logger.info("received_agent_message", 
                    message_id=message.id, 
                    type=message.type, 
                    sender=message.sender,
                    intent=message.intent)

        # Route based on message type
        # In a full implementation, this would trigger more complex orchestrator logic.
        # For now, we perform basic job status updates if a job ID is present in correlation.
        
        job_id = message.correlation.get("conversationId")
        
        if job_id:
            if message.type == MessageType.INFORM:
                logger.info("job_info_received", job_id=job_id, payload=message.payload)
                # Potentially update job metadata or progress
            
            elif message.type == MessageType.DONE:
                logger.info("job_done_received", job_id=job_id)
                await job_queue.update_status(job_id, JobStatus.DONE)
            
            elif message.type == MessageType.FAILURE:
                error_msg = message.status.get("reason", "Unknown error")
                logger.warning("job_failure_received", job_id=job_id, error=error_msg)
                await job_queue.update_status(job_id, JobStatus.FAILED, error=error_msg)

        return MessageAcknowledgement(message_id=message.id)

    except ValueError as e:
        logger.error("invalid_message_received", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message format: {e}",
        )
    except Exception as e:
        logger.error("message_handling_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )
