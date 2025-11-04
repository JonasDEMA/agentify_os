"""Data models for cognitive layer."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ActionSuggestion(BaseModel):
    """Suggested action from LLM."""

    action_type: str = Field(..., description="Type of action (click, type, wait_for, screenshot)")
    selector: str | None = Field(None, description="Selector for the action (coordinates, element, etc.)")
    value: str | None = Field(None, description="Value for the action (text to type, etc.)")
    reasoning: str = Field(..., description="Reasoning behind the action")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0.0 - 1.0)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMRequest(BaseModel):
    """Request to LLM for next action."""

    goal: str = Field(..., description="The goal to achieve")
    current_state: str = Field(..., description="Current state description")
    screenshot_base64: str | None = Field(None, description="Base64 encoded screenshot")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    previous_actions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Previous actions taken",
    )
    obstacles: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Obstacles encountered",
    )


class LLMResponse(BaseModel):
    """Response from LLM."""

    suggestion: ActionSuggestion = Field(..., description="Suggested action")
    alternative_actions: list[ActionSuggestion] = Field(
        default_factory=list,
        description="Alternative actions",
    )
    state_assessment: str = Field(..., description="Assessment of current state")
    next_state_prediction: str | None = Field(
        None,
        description="Predicted next state after action",
    )
    warnings: list[str] = Field(default_factory=list, description="Warnings or concerns")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    model_used: str = Field(..., description="LLM model used")
    tokens_used: int | None = Field(None, description="Tokens used in the request")


class StrategyRequest(BaseModel):
    """Request to LLM for strategy creation."""

    goal: str = Field(..., description="The goal to achieve")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    known_states: list[str] = Field(default_factory=list, description="Known states")
    known_transitions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Known transitions",
    )


class StrategyResponse(BaseModel):
    """Response from LLM with strategy."""

    strategy_name: str = Field(..., description="Name of the strategy")
    goal: str = Field(..., description="Goal of the strategy")
    preconditions: list[str] = Field(default_factory=list, description="Preconditions")
    steps: list[dict[str, Any]] = Field(..., description="Steps to execute")
    expected_states: list[str] = Field(
        default_factory=list,
        description="Expected states during execution",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    reasoning: str = Field(..., description="Reasoning behind the strategy")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    model_used: str = Field(..., description="LLM model used")

