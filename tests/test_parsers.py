import pytest
from unittest.mock import patch
from decimal import Decimal
from simple_money_lib import Currency
from simple_money_lib.money_parser import MoneyParserBase

# Fixture to initialize the MoneyParserBase instance
@pytest.fixture
def parser():
    """Fixture to initialize the MoneyParserBase instance."""
    return MoneyParserBase()

# Auto-use fixture to mock save_user_currencies and prevent disk writes
@pytest.fixture(autouse=True)
def mock_save_user_currencies():
    """Mock save_user_currencies to prevent actual writes to disk."""
    with patch("simple_money_lib.currency.save_user_currencies") as mock_save:
        yield mock_save

def test_valid_with_currency_suffix(parser):
    result = parser.parse("21.34 USD")
    assert result == (Decimal("21.34"), "USD")

def test_valid_with_currency_prefix(parser):
    result = parser.parse("EUR 567.89")
    assert result == (Decimal("567.89"), "EUR")

def test_valid_without_space(parser):
    result = parser.parse("CNY1.23")
    assert result == (Decimal("1.23"), "CNY")

def test_valid_without_currency(parser):
    result = parser.parse("123.45")
    assert result == (Decimal("123.45"), None)

def test_invalid_format(parser):
    with pytest.raises(ValueError):
        parser.parse("Invalid input")

def test_empty_string(parser):
    with pytest.raises(ValueError):
        parser.parse("")

def test_negative_amount_with_currency(parser):
    result = parser.parse("-42.00 GBP")
    assert result == (Decimal("-42.00"), "GBP")

def test_amount_with_currency_ending_with_digit(parser):
    # Register a custom currency for the test
    Currency.register(
        code="BTC_8",
        numeric=None,  # Assuming no numeric code for BTC_8
        sub_unit=8,    # Custom sub-unit for BTC_8
        name="Bitcoin (8 decimals)"
    )

    # Run the test
    result = parser.parse("100 BTC_8")
    assert result == (Decimal("100"), "BTC_8")

# def test_large_amount(parser):
#     result = parser.parse("1234567890.12345 JPY")
#     assert result == (Decimal("1234567890.12345"), "JPY")
#
# def test_invalid_number_format(parser):
#     with pytest.raises(ValueError):
#         parser.parse("123.45.67 USD")
#
# def test_currency_case_insensitivity(parser):
#     # Assuming case insensitivity for currency matching
#     result = parser.parse("21.34 usd")
#     assert result == (Decimal("21.34"), "usd")
#
# def test_currency_not_found_but_amount_valid(parser):
#     result = parser.parse("456.78")
#     assert result == (Decimal("456.78"), None)
