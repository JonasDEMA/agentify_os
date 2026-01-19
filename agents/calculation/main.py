"""Calculation Agent - FastAPI service."""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Add parent directory to path to import scheduler modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.calculation.calculator import CalculationError, calculate
from scheduler.core.lam_protocol import BaseMessage, InformMessage, MessageType, RequestMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Calculation Agent",
    description="Agent that performs mathematical calculations",
    version="1.0.0",
)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    agent: str = "calculation"
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
        LAM inform message with calculation result
    """
    try:
        # Parse incoming LAM request
        request_msg = RequestMessage(**message)
        logger.info(f"Received calculation request: {request_msg.id}")
        logger.debug(f"Request payload: {request_msg.payload}")

        # Extract calculation parameters
        num1 = request_msg.payload.get("num1")
        num2 = request_msg.payload.get("num2")
        operator = request_msg.payload.get("operator")

        # Validate parameters
        if num1 is None or num2 is None or operator is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: num1, num2, operator",
            )

        # Perform calculation
        try:
            result = calculate(float(num1), float(num2), operator)
            logger.info(f"Calculation successful: {num1} {operator} {num2} = {result}")

            # Create LAM inform response
            response = InformMessage(
                sender="agent://calculation/main",
                intent=request_msg.intent,
                payload={"result": result},
                correlation={
                    "in_reply_to": request_msg.id,
                    "conversation_id": request_msg.correlation.get("conversation_id"),
                },
            )

            return response.to_dict()

        except CalculationError as e:
            logger.error(f"Calculation error: {e}")
            # Return LAM failure message
            from scheduler.core.lam_protocol import FailureMessage

            failure = FailureMessage(
                sender="agent://calculation/main",
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

