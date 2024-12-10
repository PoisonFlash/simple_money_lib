import pytest
from unittest.mock import patch
import re

from decimal import Decimal
from simple_money_lib.money_wip import Money
from simple_money_lib.currency import Currency
from simple_money_lib.currencies.all import EUR, USD, RUB

# @pytest.fixture(autouse=True)
# def mock_user_defined_currencies():
#     """Mock _user_defined_currencies with a temporary dictionary."""
#     with patch("simple_money_lib.currency._user_defined_currencies", {}):
#         yield

@pytest.fixture(autouse=True)
def mock_save_user_currencies():
    """Mock save_user_currencies to prevent actual writes to disk."""
    with patch("simple_money_lib.currency.save_user_currencies") as mock_save:
        yield mock_save

def test_money_positional_arguments():
    m = Money(10, 'EUR')
    assert m.amount == Decimal('10.00')
    assert m.currency.code == 'EUR'

def test_money_positional_arguments2():
    m = Money(10, EUR)
    assert m.amount == Decimal('10.00')
    assert m.currency.code == 'EUR'

def test_money_mixed_arguments():
    m = Money(10, currency='EUR')
    assert m.amount == Decimal('10.00')
    assert m.currency.code == 'EUR'

def test_money_mixed_arguments2():
    m = Money(10, currency=EUR)
    assert m.amount == Decimal('10.00')
    assert m.currency.code == 'EUR'

def test_money_named_arguments():
    m = Money(amount=10, currency='EUR')
    assert m.amount == Decimal('10.00')
    assert m.currency.code == 'EUR'

def test_money_default_currency():
    m = Money(10)
    assert m.amount == Decimal('10.00')
    assert m.currency.code == 'XXX'  # Default currency

def test_money_string_argument():
    m = Money("100 USD")
    assert m.amount == Decimal('100.00')
    assert m.currency.code == 'USD'

def test_money_too_many_arguments():
    with pytest.raises(TypeError, match="Too many positional arguments provided to Money"):
        Money(10, 'EUR', 'extra')

def test_money_invalid_currency_type():
    with pytest.raises(TypeError, match="'currency' must be a Currency instance or a valid currency code string"):
        Money(10, currency=123)  # Invalid type for currency

def test_money_invalid_amount_type():
    with pytest.raises(TypeError,
                       match="'amount' must be a Decimal, int, float, or str representing a valid numeric value."):
        Money(object(), 'USD')  # Invalid type for amount

def test_money_invalid_mixed_arguments():
    with pytest.raises(TypeError, match="Unexpected keyword arguments: amount"):
        Money(10, amount=15)

def test_money_invalid_string_parse():
    with pytest.raises(ValueError, match="Unknown currency: 'invalid'"):
        Money("invalid USD")  # Invalid string input

def test_money_invalid_string_parse():
    with pytest.raises(ValueError, match="Invalid value: 'USD invalid'"):
        Money("USD invalid")  # Invalid string input

def test_money_no_arguments():
    with pytest.raises(TypeError, match=re.escape("Invalid arguments: args=(), kwargs={}")):
        Money()  # No arguments provided

def test_money_zero_amount():
    m = Money(0, 'USD')
    assert m.amount == Decimal('0.00')
    assert m.currency.code == 'USD'

def test_money_float_amount():
    m = Money(12.3456, 'EUR')
    assert m.amount == Decimal('12.34')  # Rounded DOWN to two decimal places

def test_money_large_amount():
    m = Money(1e6, 'USD')  # 1 million
    assert m.amount == Decimal('1000000.00')
    assert m.currency.code == 'USD'

def test_money_edge_currency_code():
    m = Money(10, 'JPY')
    assert m.amount == Decimal('10')  # JPY typically has no subunits
    assert m.currency.code == 'JPY'

def test_money_str_representation():
    m = Money(123.45, 'USD')
    assert str(m) == "123.45 USD"

def test_money_repr_representation():
    m = Money(123.45, 'USD')
    assert repr(m) == "Money(amount=123.45, currency='USD')"

@patch("simple_money_lib.currency.save_user_currencies")
def test_money_custom_currency(mock_save):
    custom_currency = Currency.register('BTC', sub_unit=8, numeric=None, name="Bitcoin")  # 8 decimal places for Bitcoin
    m = Money(0.12345678, custom_currency)
    assert m.amount == Decimal('0.12345678')
    assert m.currency.code == 'BTC'

def test_money_default_currency_subunit():
    m = Money(123)
    assert m.amount == Decimal('123.00')  # Default subunit for XXX assumed as 2
    assert m.currency.code == 'XXX'


def test_addition_with_zero():
    usd = Currency("USD")
    money = Money(10, usd)

    assert money + 0 == money  # Identity operation
    assert 0 + money == money  # Reverse addition works


def test_reverse_subtraction_with_zero():
    usd = Currency("USD")
    money = Money(10, usd)

    assert 0 - money == -money  # Negation via reverse subtraction


def test_subtraction_between_money_objects():
    usd = Currency("USD")
    money1 = Money(20, usd)
    money2 = Money(10, usd)

    assert money1 - money2 == Money(10, usd)


def test_addition_between_money_objects():
    usd = Currency("USD")
    money1 = Money(10, usd)
    money2 = Money(15, usd)

    assert money1 + money2 == Money(25, usd)


def test_currency_mismatch():
    usd = Currency("USD")
    eur = Currency("EUR")
    money_usd = Money(10, usd)
    money_eur = Money(5, eur)

    with pytest.raises(TypeError, match="Cannot add or subtract Money objects with different currencies"):
        money_usd + money_eur

    with pytest.raises(TypeError, match="Cannot add or subtract Money objects with different currencies"):
        money_usd - money_eur


def test_addition_invalid_type():
    usd = Currency("USD")
    money = Money(10, usd)

    with pytest.raises(TypeError):
        money + 5  # Adding an integer other than 0 should fail


def test_subtraction_invalid_type():
    usd = Currency("USD")
    money = Money(10, usd)

    with pytest.raises(TypeError):
        money - 5  # Subtracting an integer other than 0 should fail


def test_reverse_subtraction_invalid_type():
    usd = Currency("USD")
    money = Money(10, usd)

    with pytest.raises(TypeError):
        5 - money  # Reverse subtraction with invalid type should fail


def test_equality_with_money_objects():
    usd = Currency("USD")
    money1 = Money(10, usd)
    money2 = Money(10, usd)

    assert money1 == money2
    assert not (money1 != money2)


def test_equality_with_zero():
    usd = Currency("USD")
    money = Money(0, usd)

    assert money == 0  # Money(0, USD) == 0
    assert 0 == money  # 0 == Money(0, USD)
    assert not (money != 0)


def test_inequality():
    usd = Currency("USD")
    money1 = Money(10, usd)
    money2 = Money(20, usd)

    assert money1 != money2
    assert not (money1 == money2)

def test_multiplication_with_valid_numeric_types():
    usd = Currency("USD")
    money = Money(10, usd)

    # Test multiplication with int
    result = money * 2
    assert result == Money(20, usd)

    # Test multiplication with float
    result = money * 2.5
    assert result == Money(25, usd)

    # Test multiplication with Decimal
    result = money * Decimal("1.5")
    assert result == Money(15, usd)

    # Test reverse multiplication with int
    result = 3 * money
    assert result == Money(30, usd)

    # Test reverse multiplication with float
    result = 0.5 * money
    assert result == Money(5, usd)

    # Test reverse multiplication with Decimal
    result = Decimal("2") * money
    assert result == Money(20, usd)


def test_multiplication_with_invalid_types():
    usd = Currency("USD")
    money = Money(10, usd)

    # Test multiplication with string
    with pytest.raises(TypeError, match="Unsupported operand type\\(s\\) for \\*: 'Money' and 'str'"):
        result = money * "string"

    # Test reverse multiplication with string
    with pytest.raises(TypeError, match="Unsupported operand type\\(s\\) for \\*: 'Money' and 'str'"):
        result = "string" * money

    # Test multiplication with list
    with pytest.raises(TypeError, match="Unsupported operand type\\(s\\) for \\*: 'Money' and 'list'"):
        result = money * [1, 2]

    # Test reverse multiplication with list
    with pytest.raises(TypeError, match="Unsupported operand type\\(s\\) for \\*: 'Money' and 'list'"):
        result = [1, 2] * money


def test_multiplication_with_money_instances():
    usd = Currency("USD")
    money1 = Money(10, usd)
    money2 = Money(5, usd)

    # Test multiplication of two Money instances
    with pytest.raises(TypeError, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'Money'")):
        result = money1 * money2

    # Test reverse multiplication of two Money instances
    with pytest.raises(TypeError, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'Money'")):
        result = money2 * money1
