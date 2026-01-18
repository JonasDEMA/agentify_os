"""Formatting Agent - FastAPI service."""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directory to path to import scheduler modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.formatting.formatter import FormattingError, format_number
from scheduler.core.lam_protocol import FailureMessage, InformMessage, RequestMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Formatting Agent",
    description="Agent that formats numbers for display",
    version="1.0.0",
)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    agent: str = "formatting"
    version: str = "1.0.0"


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/tasks")
async def handle_task(message: dict):
    """Handle incoming LAM task request.

    Args:
        message: LAM request message

    Returns:
        LAM inform message with formatted result
    """
    try:
        # Parse incoming LAM request
        request_msg = RequestMessage(**message)
        logger.info(f"Received formatting request: {request_msg.id}")
        logger.debug(f"Request payload: {request_msg.payload}")

        # Extract formatting parameters
        value = request_msg.payload.get("value")
        locale = request_msg.payload.get("locale", "en-US")
        decimals = request_msg.payload.get("decimals", 2)

        # Validate parameters
        if value is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter: value",
            )

        # Format number
        try:
            formatted = format_number(float(value), locale, int(decimals))
            logger.info(f"Formatting successful: {value} -> {formatted} ({locale})")

            # Create LAM inform response
            response = InformMessage(
                sender="agent://formatting/main",
                intent=request_msg.intent,
                payload={"formatted": formatted},
                correlation={
                    "in_reply_to": request_msg.id,
                    "conversation_id": request_msg.correlation.get("conversation_id"),
                },
            )

            return response.to_dict()

        except FormattingError as e:
            logger.error(f"Formatting error: {e}")
            # Return LAM failure message
            failure = FailureMessage(
                sender="agent://formatting/main",
                intent=request_msg.intent,
                payload={"error": str(e)},
                correlation={
                    "in_reply_to": request_msg.id,
                    "conversation_id": request_msg.correlation.get("conversation_id"),
                },
            )
            return failure.to_dict()

    except Exception as e:
        logger.error(f"Error processing task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

