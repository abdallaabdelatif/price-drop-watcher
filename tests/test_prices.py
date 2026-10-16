import pytest

from price_drop_watcher.prices import parse_price


@pytest.mark.parametrize("text,expected", [
    ("1,234.56", 123456), ("EGP 100", 10000), ("100.5 EGP", 10050),
    ("  EGP\u00a01,000.00\n", 100000), ("0.01", 1), ("12", 1200),
    ("123456789012345678901234567890.12", 12345678901234567890123456789012),
])
def test_valid_price(text, expected):
    assert parse_price(text, "EGP") == expected


@pytest.mark.parametrize("text", [
    "", "0", "0.00", "-1", "+1", "1,23", "12,34,567", "1.234",
    "100 90", "EGP 100 USD", "$100", "100,50", "1.000,50", "NaN",
    "Infinity", "1e3", "EGP 100 EGP", "100.", "١٠٠", "1 000", "01,000",
])
def test_invalid_price(text):
    with pytest.raises(ValueError):
        parse_price(text, "EGP")


def test_invalid_currency():
    with pytest.raises(ValueError):
        parse_price("100", "egp")
