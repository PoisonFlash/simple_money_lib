import pytest
import re
from decimal import Decimal
from simple_money_lib.money_wip import Money
from simple_money_lib.currency import Currency
from simple_money_lib.currencies.all import EUR, USD, RUB

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
    with pytest.raises(TypeError, match="Amount must be a Decimal, int, float, or str representing a numeric value."):
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

def test_money_custom_currency():
    custom_currency = Currency.register('BTC', sub_unit=8, numeric=None, name="Bitcoin")  # 8 decimal places for Bitcoin
    m = Money(0.12345678, custom_currency)
    assert m.amount == Decimal('0.12345678')
    assert m.currency.code == 'BTC'

def test_money_default_currency_subunit():
    m = Money(123)
    assert m.amount == Decimal('123.00')  # Default subunit for XXX assumed as 2
    assert m.currency.code == 'XXX'
