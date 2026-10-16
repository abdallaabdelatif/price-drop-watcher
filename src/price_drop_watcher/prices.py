"""Strict two-decimal currency parsing without rounding."""

import re
from decimal import Decimal, localcontext


def parse_price(text: str, currency: str) -> int:
    """Return positive minor units; accept an optional leading/trailing code."""
    if re.fullmatch(r"[A-Z]{3}", currency) is None:
        raise ValueError("Currency must contain three uppercase letters")
    amount = text.strip()
    if amount.startswith(currency):
        amount = amount[len(currency):].strip()
    elif amount.endswith(currency):
        amount = amount[:-len(currency)].strip()
    if re.fullmatch(r"(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)(?:\.[0-9]{1,2})?", amount) is None:
        raise ValueError("Price must be one amount with comma grouping and dot decimals")
    digits = amount.replace(",", "")
    with localcontext() as context:
        context.prec = max(28, len(digits) + 2)
        minor = int(Decimal(digits) * 100)
    if minor <= 0:
        raise ValueError("Price must be positive")
    return minor
