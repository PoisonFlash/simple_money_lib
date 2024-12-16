import pytest
from unittest.mock import patch

from decimal import Decimal
from simple_money_lib import Currency
from simple_money_lib.parsers import SimpleMoneyParser, SimpleParserWithSubstitutions


# Fixture to initialize the MoneyParserBase instance
@pytest.fixture
def parser():
    """Fixture to initialize the MoneyParserBase instance."""
    return SimpleMoneyParser()

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

    result = parser.parse("BTC_8 200")
    assert result == (Decimal("200"), "BTC_8")

    result = parser.parse("2BTC_8")
    assert result == (Decimal("2"), "BTC_8")

def test_amount_with_currency_ending_with_digit_no_space(parser):
    # Reuse custom currency from the previous test
    # Run the test
    with pytest.raises(ValueError, match="Invalid monetary amount: '_8100'"):
        parser.parse("BTC_8100")

def test_invalid_amount_with_underscores(parser):
    test_cases = [
        ("_8100 BTC", ValueError),  # Leading underscore in the amount
        ("BTC _8100", ValueError),  # Leading underscore in the amount after currency
        ("BTC_8100", ValueError),  # Ambiguous: Is it BTC_8 or 8100 BTC?
        ("8100_BTC", ValueError),  # Underscore in the middle of the amount
        ("8100_", ValueError),  # Trailing underscore
    ]

    for test_input, expected_exception in test_cases:
        with pytest.raises(expected_exception):
            parser.parse(test_input)

def test_valid_amount_with_custom_currency(parser):
    test_cases = [
        ("100BTC_8", (Decimal("100"), "BTC_8")),  # Custom currency, no space
        ("BTC_8 100", (Decimal("100"), "BTC_8")),  # Space between custom currency and amount
        ("100 BTC_8", (Decimal("100"), "BTC_8")),  # Space before custom currency
    ]

    for test_input, expected_output in test_cases:
        result = parser.parse(test_input)
        assert result == expected_output, f"Failed on '{test_input}'"

def test_large_amount(parser):
    result = parser.parse("1234567890.12345 JPY")
    assert result == (Decimal("1234567890.12345"), "JPY")

def test_invalid_number_format(parser):
    with pytest.raises(ValueError):
        parser.parse("123.45.67 USD")

def test_currency_case_insensitivity(parser):
    # Assuming case insensitivity for currency matching
    result = parser.parse("21.34 usd")
    assert result == (Decimal("21.34"), "USD")

def test_currency_not_found_but_amount_valid(parser):
    result = parser.parse("456.78")
    assert result == (Decimal("456.78"), None)

def test_invalid_numeric_formats(parser):
    test_cases = [
        ("123,45,67USD", ValueError),  # Too many commas
        ("USD123.45.67", ValueError),  # Invalid number format
        ("USD123..45", ValueError),    # Double decimal points
    ]

    for test_input, expected_exception in test_cases:
        with pytest.raises(expected_exception):
            parser.parse(test_input)

def test_substitution_with_symbols():
    substitutions = {"$": "USD", ",": ""}
    parser = SimpleParserWithSubstitutions(substitutions=substitutions)

    test_cases = [
        ("1,250.50$", (Decimal("1250.50"), "USD")),  # Correctly substituted
        ("$1,250.50", (Decimal("1250.50"), "USD")),  # Correctly substituted
        ("1250.50 USD", (Decimal("1250.50"), "USD")),  # No substitution needed
        ("1,250.50 EUR", (Decimal("1250.50"), "EUR")),  # Different currency
        # ("1,250.50", ValueError),  # Invalid: results in '1,250.50'
    ]

    for test_input, expected_output in test_cases:
        result = parser.parse(test_input)
        assert result == expected_output, f"Failed on '{test_input}'"

def test_bad_substitution():
    substitutions = {"$": "USD", ",": ".", "₿": "ZZZZZ"}
    parser = SimpleParserWithSubstitutions(substitutions=substitutions)

    test_cases = [
        ("1,250.50", ValueError),  # Invalid: results in '1.250.50'
        ("1,50₿", ValueError),  # Invalid: ZZZZZ is not recognized
    ]

    for test_input, expected_output in test_cases:
        with pytest.raises(expected_output):
            parser.parse(test_input)

def test_substitution_ending_with_digit():
    # Register a custom currency for the test
    Currency.register(
        code="BTC_12",
        numeric=None,  # Assuming no numeric code for BTC_8
        sub_unit=12,  # Custom sub-unit for BTC_8
        name="Bitcoin (12 decimals)"
    )
    substitutions = {"₿": "BTC_12"}
    parser = SimpleParserWithSubstitutions(substitutions=substitutions)

    test_cases = [
        ("1.5₿", (Decimal("1.5"), "BTC_12")),  # Correctly substituted
        ("₿1.5", (Decimal("1.5"), "BTC_12")),  # Correctly substituted
    ]

    for test_input, expected_output in test_cases:
        result = parser.parse(test_input)
        assert result == expected_output, f"Failed on '{test_input}'"