"""Tests for Agent Communication Protocol Protocol."""

import json
from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from scheduler.core.agent_protocol import (
    AgreeMessage,
    AssignMessage,
    BaseMessage,
    ConfirmMessage,
    DiscoverMessage,
    DoneMessage,
    FailureMessage,
    InformMessage,
    MessageFactory,
    MessageType,
    OfferMessage,
    ProposeMessage,
    RefuseMessage,
    RequestMessage,
)


class TestBaseMessage:
    """Test BaseMessage model."""

    def test_create_minimal_message(self):
        """Test creating a message with minimal required fields."""
        msg = BaseMessage(
            type=MessageType.REQUEST,
            sender="agent://orchestrator/test",
            intent="test_intent",
        )
        
        assert msg.type == MessageType.REQUEST
        assert msg.sender == "agent://orchestrator/test"
        assert msg.intent == "test_intent"
        assert isinstance(UUID(msg.id), UUID)  # Valid UUID
        assert isinstance(msg.ts, datetime)
        assert msg.to == []
        assert msg.task is None
        assert msg.payload == {}

    def test_create_full_message(self):
        """Test creating a message with all fields."""
        msg = BaseMessage(
            type=MessageType.REQUEST,
            sender="agent://orchestrator/Marketing",
            to=["agent://worker/Analysis"],
            intent="analyse",
            task="Analysiere Q3 Churn",
            payload={"datasetRef": "s3://acme/crm/q3.parquet"},
            context={
                "tenant": "acme",
                "domain": "crm",
                "locale": "de-DE",
            },
            correlation={
                "conversationId": "conv-123",
                "inReplyTo": "uuid-xyz",
                "ttlSec": 60,
            },
            expected={
                "type": "inform",
                "deadline": "2025-10-30T09:46:00Z",
            },
            status={
                "code": "ok",
                "progressPct": 20,
            },
            security={
                "auth": "jwt",
                "scope": ["crm.read", "analytics.run"],
                "sensitivity": "confidential",
            },
        )
        
        assert msg.sender == "agent://orchestrator/Marketing"
        assert msg.to == ["agent://worker/Analysis"]
        assert msg.task == "Analysiere Q3 Churn"
        assert msg.payload["datasetRef"] == "s3://acme/crm/q3.parquet"
        assert msg.context["tenant"] == "acme"
        assert msg.correlation["conversationId"] == "conv-123"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            BaseMessage()  # Missing type, sender, intent

    def test_to_dict(self):
        """Test serialization to dict."""
        msg = BaseMessage(
            type=MessageType.REQUEST,
            sender="agent://test",
            intent="test",
        )
        
        data = msg.to_dict()
        
        assert isinstance(data, dict)
        assert data["type"] == "request"
        assert data["sender"] == "agent://test"
        assert data["intent"] == "test"
        assert "id" in data
        assert "ts" in data

    def test_to_json(self):
        """Test serialization to JSON."""
        msg = BaseMessage(
            type=MessageType.REQUEST,
            sender="agent://test",
            intent="test",
        )
        
        json_str = msg.to_json()
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["type"] == "request"
        assert data["sender"] == "agent://test"

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "id": "6f7b9c1e-3b2c-4f07-8d10-9c3e7a20c1b2",
            "ts": "2025-10-30T09:45:00Z",
            "type": "request",
            "sender": "agent://test",
            "intent": "test",
        }
        
        msg = BaseMessage.from_dict(data)
        
        assert msg.id == "6f7b9c1e-3b2c-4f07-8d10-9c3e7a20c1b2"
        assert msg.type == MessageType.REQUEST
        assert msg.sender == "agent://test"

    def test_from_json(self):
        """Test deserialization from JSON."""
        json_str = json.dumps({
            "id": "6f7b9c1e-3b2c-4f07-8d10-9c3e7a20c1b2",
            "ts": "2025-10-30T09:45:00Z",
            "type": "request",
            "sender": "agent://test",
            "intent": "test",
        })
        
        msg = BaseMessage.from_json(json_str)
        
        assert msg.type == MessageType.REQUEST
        assert msg.sender == "agent://test"


class TestRequestMessage:
    """Test RequestMessage model."""

    def test_create_request_message(self):
        """Test creating a request message."""
        msg = RequestMessage(
            sender="agent://orchestrator/Marketing",
            to=["agent://worker/Analysis"],
            intent="analyse",
            task="Analysiere Churn-Risiko für Q3",
            payload={"datasetRef": "s3://acme/crm/q3.parquet"},
        )
        
        assert msg.type == MessageType.REQUEST
        assert msg.sender == "agent://orchestrator/Marketing"
        assert msg.task == "Analysiere Churn-Risiko für Q3"


class TestInformMessage:
    """Test InformMessage model."""

    def test_create_inform_message(self):
        """Test creating an inform message."""
        msg = InformMessage(
            sender="agent://worker/Analysis",
            to=["agent://orchestrator/Marketing"],
            intent="analysis_result",
            payload={
                "churnRate": 0.083,
                "topDrivers": ["low_engagement", "support_tickets"],
            },
            correlation={
                "conversationId": "conv-123",
                "inReplyTo": "6f7b9c1e-3b2c-4f07-8d10-9c3e7a20c1b2",
            },
        )
        
        assert msg.type == MessageType.INFORM
        assert msg.payload["churnRate"] == 0.083
        assert msg.correlation["inReplyTo"] == "6f7b9c1e-3b2c-4f07-8d10-9c3e7a20c1b2"


class TestFailureMessage:
    """Test FailureMessage model."""

    def test_create_failure_message(self):
        """Test creating a failure message."""
        msg = FailureMessage(
            sender="agent://worker/Analysis",
            to=["agent://orchestrator/Marketing"],
            intent="analysis_result",
            correlation={
                "conversationId": "conv-123",
                "inReplyTo": "6f7b9c1e-3b2c-4f07-8d10-9c3e7a20c1b2",
            },
            status={
                "code": "error",
                "reason": "dataset_not_found",
            },
        )
        
        assert msg.type == MessageType.FAILURE
        assert msg.status["code"] == "error"
        assert msg.status["reason"] == "dataset_not_found"


class TestDiscoveryMessages:
    """Test Discovery-related messages (Discover, Offer, Assign)."""

    def test_create_discover_message(self):
        """Test creating a discover message."""
        msg = DiscoverMessage(
            sender="agent://orchestrator/Marketing",
            intent="help_needed",
            task="Wer kann kurzfristig eine Vertriebs-Scorecard bauen?",
            context={"tenant": "acme", "domain": "sales"},
        )
        
        assert msg.type == MessageType.DISCOVER
        assert msg.task == "Wer kann kurzfristig eine Vertriebs-Scorecard bauen?"

    def test_create_offer_message(self):
        """Test creating an offer message."""
        msg = OfferMessage(
            sender="agent://worker/BIComposer",
            to=["agent://router/Core"],
            intent="capability_ad",
            payload={
                "capabilities": ["kpi_design", "scorecards"],
                "etaMin": 3,
                "costUnit": "credits:5",
            },
            correlation={
                "conversationId": "disc-42",
                "inReplyTo": "d-001",
            },
        )
        
        assert msg.type == MessageType.OFFER
        assert msg.payload["capabilities"] == ["kpi_design", "scorecards"]

    def test_create_assign_message(self):
        """Test creating an assign message."""
        msg = AssignMessage(
            sender="agent://router/Core",
            to=["agent://worker/BIComposer"],
            intent="assign_task",
            task="Baue Sales-Scorecard (MRR, WinRate, CycleTime) für Q3",
            payload={"dataRef": "s3://acme/sales/q3.parquet"},
        )
        
        assert msg.type == MessageType.ASSIGN
        assert msg.task == "Baue Sales-Scorecard (MRR, WinRate, CycleTime) für Q3"


class TestMessageFactory:
    """Test MessageFactory."""

    def test_create_from_type(self):
        """Test creating messages from type."""
        msg = MessageFactory.create(
            message_type=MessageType.REQUEST,
            sender="agent://test",
            intent="test",
        )
        
        assert isinstance(msg, RequestMessage)
        assert msg.type == MessageType.REQUEST

    def test_create_from_dict(self):
        """Test creating messages from dict."""
        data = {
            "type": "inform",
            "sender": "agent://test",
            "intent": "test",
            "payload": {"result": "success"},
        }
        
        msg = MessageFactory.from_dict(data)
        
        assert isinstance(msg, InformMessage)
        assert msg.type == MessageType.INFORM

    def test_create_from_json(self):
        """Test creating messages from JSON."""
        json_str = json.dumps({
            "type": "failure",
            "sender": "agent://test",
            "intent": "test",
            "status": {"code": "error"},
        })
        
        msg = MessageFactory.from_json(json_str)
        
        assert isinstance(msg, FailureMessage)
        assert msg.type == MessageType.FAILURE

    def test_create_unknown_type(self):
        """Test creating message with unknown type raises error."""
        with pytest.raises(ValueError, match="Unknown message type"):
            MessageFactory.create(
                message_type="unknown_type",  # type: ignore
                sender="agent://test",
                intent="test",
            )


class TestCorrelationTracking:
    """Test correlation ID tracking across messages."""

    def test_request_response_correlation(self):
        """Test correlation between request and response."""
        # Create request
        request = RequestMessage(
            sender="agent://orchestrator",
            to=["agent://worker"],
            intent="process",
            task="Do something",
        )
        
        # Create response with correlation
        response = InformMessage(
            sender="agent://worker",
            to=["agent://orchestrator"],
            intent="result",
            payload={"status": "done"},
            correlation={
                "conversationId": "conv-123",
                "inReplyTo": request.id,
            },
        )
        
        assert response.correlation["inReplyTo"] == request.id
        assert response.correlation["conversationId"] == "conv-123"

