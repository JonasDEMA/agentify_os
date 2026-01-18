"""Formatter module - Number formatting logic."""

from enum import Enum


class Locale(str, Enum):
    """Supported locales for number formatting."""

    EN_US = "en-US"
    DE_DE = "de-DE"
    FR_FR = "fr-FR"


class FormattingError(Exception):
    """Custom exception for formatting errors."""

    pass


def format_number(value: float, locale: str = "en-US", decimals: int = 2) -> str:
    """Format a number according to locale specifications.

    Args:
        value: Number to format
        locale: Locale string (en-US, de-DE, fr-FR)
        decimals: Number of decimal places

    Returns:
        Formatted number string

    Raises:
        FormattingError: If locale is invalid or decimals is negative
    """
    # Validate decimals
    if decimals < 0:
        raise FormattingError("Decimals must be non-negative")

    # Validate and normalize locale
    try:
        loc = Locale(locale)
    except ValueError as e:
        raise FormattingError(
            f"Invalid locale: {locale}. Must be one of: {[l.value for l in Locale]}"
        ) from e

    # Round to specified decimals
    rounded = round(value, decimals)

    # Format based on locale
    if loc == Locale.EN_US:
        # English (US): 1,234.56
        return _format_en_us(rounded, decimals)
    elif loc == Locale.DE_DE:
        # German: 1.234,56
        return _format_de_de(rounded, decimals)
    elif loc == Locale.FR_FR:
        # French: 1 234,56
        return _format_fr_fr(rounded, decimals)

    # Should never reach here due to enum validation
    raise FormattingError(f"Unhandled locale: {locale}")


def _format_en_us(value: float, decimals: int) -> str:
    """Format number for en-US locale (1,234.56)."""
    # Format with decimals
    formatted = f"{value:,.{decimals}f}"
    return formatted


def _format_de_de(value: float, decimals: int) -> str:
    """Format number for de-DE locale (1.234,56)."""
    # First format with en-US style
    formatted = f"{value:,.{decimals}f}"
    # Swap separators: , -> . and . -> ,
    formatted = formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return formatted


def _format_fr_fr(value: float, decimals: int) -> str:
    """Format number for fr-FR locale (1 234,56)."""
    # First format with en-US style
    formatted = f"{value:,.{decimals}f}"
    # Replace comma with space, dot with comma
    formatted = formatted.replace(",", " ").replace(".", ",")
    return formatted

