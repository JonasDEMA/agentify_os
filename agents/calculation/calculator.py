"""Calculator module - Core calculation logic."""

from enum import Enum


class Operator(str, Enum):
    """Supported mathematical operators."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class CalculationError(Exception):
    """Custom exception for calculation errors."""

    pass


def calculate(num1: float, num2: float, operator: str) -> float:
    """Perform mathematical calculation.

    Args:
        num1: First number
        num2: Second number
        operator: Operation to perform (add, subtract, multiply, divide)

    Returns:
        Result of the calculation

    Raises:
        CalculationError: If operator is invalid or division by zero
    """
    try:
        op = Operator(operator.lower())
    except ValueError as e:
        raise CalculationError(
            f"Invalid operator: {operator}. Must be one of: {[o.value for o in Operator]}"
        ) from e

    if op == Operator.ADD:
        return num1 + num2
    elif op == Operator.SUBTRACT:
        return num1 - num2
    elif op == Operator.MULTIPLY:
        return num1 * num2
    elif op == Operator.DIVIDE:
        if num2 == 0:
            raise CalculationError("Division by zero is not allowed")
        return num1 / num2

    # Should never reach here due to enum validation
    raise CalculationError(f"Unhandled operator: {operator}")

