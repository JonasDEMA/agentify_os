"""Tests for Calculation Agent."""

import pytest
from fastapi.testclient import TestClient

from agents.calculation.calculator import CalculationError, Operator, calculate
from agents.calculation.main import app

client = TestClient(app)


class TestCalculator:
    """Tests for calculator module."""

    def test_addition(self):
        """Test addition operation."""
        result = calculate(10, 5, "add")
        assert result == 15

    def test_subtraction(self):
        """Test subtraction operation."""
        result = calculate(10, 5, "subtract")
        assert result == 5

    def test_multiplication(self):
        """Test multiplication operation."""
        result = calculate(10, 5, "multiply")
        assert result == 50

    def test_division(self):
        """Test division operation."""
        result = calculate(10, 5, "divide")
        assert result == 2.0

    def test_division_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(CalculationError, match="Division by zero"):
            calculate(10, 0, "divide")

    def test_invalid_operator(self):
        """Test invalid operator raises error."""
        with pytest.raises(CalculationError, match="Invalid operator"):
            calculate(10, 5, "modulo")

    def test_case_insensitive_operator(self):
        """Test operators are case insensitive."""
        result = calculate(10, 5, "ADD")
        assert result == 15

    def test_negative_numbers(self):
        """Test calculation with negative numbers."""
        result = calculate(-10, 5, "add")
        assert result == -5

    def test_decimal_numbers(self):
        """Test calculation with decimal numbers."""
        result = calculate(10.5, 2.5, "multiply")
        assert result == 26.25


class TestCalculationAgent:
    """Tests for Calculation Agent API."""

    def test_health_check(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "calculation"

    def test_successful_calculation(self):
        """Test successful calculation via LAM protocol."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "calculate",
            "payload": {"num1": 10, "num2": 5, "operator": "multiply"},
            "correlation": {"conversation_id": "test-123"},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "inform"
        assert data["sender"] == "agent://calculation/main"
        assert data["payload"]["result"] == 50

    def test_missing_parameters(self):
        """Test missing parameters returns error."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "calculate",
            "payload": {"num1": 10},  # Missing num2 and operator
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 400

    def test_division_by_zero_returns_failure(self):
        """Test division by zero returns LAM failure message."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "calculate",
            "payload": {"num1": 10, "num2": 0, "operator": "divide"},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "failure"
        assert "Division by zero" in data["payload"]["error"]

    def test_invalid_operator_returns_failure(self):
        """Test invalid operator returns LAM failure message."""
        lam_request = {
            "type": "request",
            "sender": "agent://test/client",
            "intent": "calculate",
            "payload": {"num1": 10, "num2": 5, "operator": "invalid"},
        }

        response = client.post("/tasks", json=lam_request)
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "failure"
        assert "Invalid operator" in data["payload"]["error"]

