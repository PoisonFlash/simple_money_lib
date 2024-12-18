import pytest

from decimal import Decimal

from simple_money_lib.parsers.complex_parser import ComplexMoneyParser
from _inactive.context_templates import *


no_currency_value: str = 'SEK'


# Set up the context
@pytest.fixture(scope="module", autouse=True)
def setup_context():
    DefaultCurrencyContext.activate()


def test_zero_decimals():
    test_cases = [
        ("0", (Decimal('0.00'), no_currency_value)),
        ("0.0", (Decimal('0.00'), no_currency_value)),
        ("0,0", (Decimal('0.00'), no_currency_value)),
        ("0.00", (Decimal('0.00'), no_currency_value)),
        ("0,00", (Decimal('0.00'), no_currency_value)),
        ("0USD", (Decimal('0.00'), 'USD')),
        ("USD0.0", (Decimal('0.00'), 'USD')),
        ("0,0 USD", (Decimal('0.00'), 'USD')),
        ("USD 0.00", (Decimal('0.00'), 'USD')),
        ("0,00EUR", (Decimal('0.00'), 'EUR')),
    ]

    mp = ComplexMoneyParser()

    for test_input, expected_output in test_cases:
        result = mp.parse(test_input)
        assert result == expected_output, f"Failed on '{test_input}'"


def test_non_zero_decimals():
    test_cases = [
        ("0.01", (Decimal('0.01'), no_currency_value)),
        ("0.1", (Decimal('0.10'), no_currency_value)),
        ("0,10", (Decimal('0.10'), no_currency_value)),
        ("0.77", (Decimal('0.77'), no_currency_value)),
        ("0.03USD", (Decimal('0.03'), 'USD')),
        ("USD0.03", (Decimal('0.03'), 'USD')),
        ("0,3 USD", (Decimal('0.30'), 'USD')),
        ("USD 0.30", (Decimal('0.30'), 'USD')),
        ("123,31EUR", (Decimal('123.31'), 'EUR')),
        ("123,31", (Decimal('123.31'), no_currency_value)),
    ]

    mp = ComplexMoneyParser()

    for test_input, expected_output in test_cases:
        result = mp.parse(test_input)
        assert result == expected_output, f"Failed on '{test_input}'"


def test_money_parser():
    test_cases = [
        ("kr000", (Decimal('0.00'), 'SEK')),
        ("000kr", (Decimal('0.00'), 'SEK')),
        ("$1,250.50", (Decimal('1250.50'), 'USD')),
        ("1,250.50$", (Decimal('1250.50'), 'USD')),
        ("€ 1 250,50", (Decimal('1250.50'), 'EUR')),
        ("USD 1000", (Decimal('1000'), 'USD')),
        ("50.55 kr", (Decimal('50.55'), 'SEK')),
        ("kr.55", (Decimal('0.55'), 'SEK')),
        ("0", (Decimal('0.00'), 'SEK')),
        (".5", (Decimal('0.50'), 'SEK'))  # Adjust based on behavior
    ]

    mp = ComplexMoneyParser()

    for test_input, expected_output in test_cases:
        result = mp.parse(test_input)
        # print(result[0], str(result[1]))
        assert result == expected_output, f"Failed on '{test_input}'"
