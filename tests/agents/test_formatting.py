"""Tests for Formatting Agent."""

import pytest
from fastapi.testclient import TestClient

from agents.formatting.formatter import FormattingError, Locale, format_number
from agents.formatting.main import app

client = TestClient(app)


class TestFormatter:
    """Tests for formatter module."""

    def test_format_en_us(self):
        """Test English (US) formatting."""
        result = format_number(1234.56, "en-US", 2)
        assert result == "1,234.56"

    def test_format_de_de(self):
        """Test German formatting."""
        result = format_number(1234.56, "de-DE", 2)
        assert result == "1.234,56"

    def test_format_fr_fr(self):
        """Test French formatting."""
        result = format_number(1234.56, "fr-FR", 2)
        assert result == "1 234,56"

    def test_format_zero_decimals(self):
        """Test formatting with zero decimals."""
        result = format_number(1234.56, "en-US", 0)
        assert result == "1,235"  # Rounded

    def test_format_three_decimals(self):
        """Test formatting with three decimals."""
        result = format_number(1234.5678, "en-US", 3)
        assert result == "1,234.568"  # Rounded

    def test_format_negative_number(self):
        """Test formatting negative numbers."""
        result = format_number(-1234.56, "en-US", 2)
        assert result == "-1,234.56"

    def test_format_small_number(self):
        """Test formatting small numbers."""
        result = format_number(42.5, "en-US", 2)
        assert result == "42.50"

    def test_format_large_number(self):
        """Test formatting large numbers."""
        result = format_number(1234567.89, "en-US", 2)
        assert result == "1,234,567.89"

    def test_invalid_locale(self):
        """Test invalid locale raises error."""
        with pytest.raises(FormattingError, match="Invalid locale"):
            format_number(1234.56, "invalid", 2)

    def test_negative_decimals(self):
        """Test negative decimals raises error."""
        with pytest.raises(FormattingError, match="Decimals must be non-negative"):
            format_number(1234.56, "en-US", -1)

    def test_default_locale(self):
        """Test default locale is en-US."""
        result = format_number(1234.56)
        assert result == "1,234.56"

    def test_default_decimals(self):
        """Test default decimals is 2."""
        result = format_number(1234.5)
        assert result == "1,234.50"


class TestFormattingAgent:
    """Tests for Formatting Agent API."""

    def test_health_check(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "formatting"

    def test_successful_formatting(self):
        """Test successful formatting via LAM protocol."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "format",
            "payload": {"value": 1234.56, "locale": "en-US", "decimals": 2},
            "correlation": {"conversation_id": "test-123"},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "inform"
        assert data["sender"] == "agent://formatting/main"
        assert data["payload"]["formatted"] == "1,234.56"

    def test_default_locale_and_decimals(self):
        """Test default locale and decimals."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "format",
            "payload": {"value": 1234.56},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["payload"]["formatted"] == "1,234.56"

    def test_missing_value_parameter(self):
        """Test missing value parameter returns error."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "format",
            "payload": {},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 400

    def test_invalid_locale_returns_failure(self):
        """Test invalid locale returns LAM failure message."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "format",
            "payload": {"value": 1234.56, "locale": "invalid"},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "failure"
        assert "Invalid locale" in data["payload"]["error"]

    def test_german_locale(self):
        """Test German locale formatting."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "format",
            "payload": {"value": 1234.56, "locale": "de-DE", "decimals": 2},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["payload"]["formatted"] == "1.234,56"

