import decimal

import pytest
from unittest.mock import patch
import re

import threading

from decimal import Decimal
from simple_money_lib.money import Money
from simple_money_lib.currency import Currency
from simple_money_lib.currencies.all import XXX, EUR
from simple_money_lib.exceptions import CurrencyMismatch, MoneyDivisionIllegal, MoneyInvalidOperation
import simple_money_lib.parsers as parsers
from simple_money_lib.utils.default_currency import DefaultCurrency


@pytest.fixture(autouse=True)
def reset_global_rounding():
    # Save the original rounding mode
    original_rounding = Money.rounding.get_default()

    # Yield control to the test
    yield

    # Reset the global rounding mode after each test
    Money.rounding.set_default(original_rounding)

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
    with pytest.raises(ValueError,
                       match="'amount' must be a Decimal, int, float, or str representing a valid numeric value."):
        Money(object(), 'USD')  # Invalid type for amount

def test_money_invalid_mixed_arguments():
    with pytest.raises(TypeError, match="Unexpected keyword arguments: amount"):
        Money(10, amount=15)

def test_money_invalid_string_parse():
    with pytest.raises(ValueError, match="Invalid monetary amount: 'invalid'"):
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

    with pytest.raises(CurrencyMismatch):
        money_usd + money_eur

    with pytest.raises(CurrencyMismatch):
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
    with pytest.raises(MoneyInvalidOperation, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'str'")):
        money * "string"

    # Test reverse multiplication with string
    with pytest.raises(MoneyInvalidOperation, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'str'")):
        "string" * money

    # Test multiplication with list
    with pytest.raises(MoneyInvalidOperation, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'list'")):
        money * [1, 2]

    # Test reverse multiplication with list
    with pytest.raises(MoneyInvalidOperation, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'list'")):
        [1, 2] * money


def test_multiplication_with_money_instances():
    usd = Currency("USD")
    money1 = Money(10, usd)
    money2 = Money(5, usd)

    # Test multiplication of two Money instances
    with pytest.raises(MoneyInvalidOperation, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'Money'")):
        money1 * money2

    # Test reverse multiplication of two Money instances
    with pytest.raises(MoneyInvalidOperation, match=re.escape("Unsupported operand type(s) for *: 'Money' and 'Money'")):
        money2 * money1

def test_truediv_with_valid_numeric_types():
    usd = Currency("USD")
    money = Money(20, usd)

    # Division with int
    result = money / 4
    assert result == Money(5, usd)

    # Division with float
    result = money / 2.5
    assert result == Money(8, usd)

    # Division with Decimal
    Money.rounding.set(decimal.ROUND_HALF_DOWN)
    result = money / Decimal("3")
    assert result == Money(6.67, usd)

    Money.rounding.set(decimal.ROUND_DOWN)
    result = money / Decimal("3")
    assert result == Money(6.66, usd)


def test_truediv_with_zero():
    usd = Currency("USD")
    money = Money(20, usd)

    # Division by zero
    with pytest.raises(ZeroDivisionError):
        money / 0


def test_truediv_with_invalid_types():
    usd = Currency("USD")
    money = Money(20, usd)

    # Division with unsupported type
    with pytest.raises(MoneyInvalidOperation, match="Unsupported operand type\\(s\\) for /: 'Money' and 'str'"):
        money / "string"

    with pytest.raises(MoneyInvalidOperation, match="Unsupported operand type\\(s\\) for /: 'Money' and 'list'"):
        money / [1, 2]


def test_divide_with_adjustment():
    Money.rounding.set(decimal.ROUND_DOWN)
    usd = Currency("USD")
    money = Money(20, usd)

    # Division with remainder
    result, adjustment = money.divide_with_adjustment(7)
    assert result == Money(2.85, usd)
    assert adjustment == Money(0.05, usd)

    # Verify original value
    assert (result * 7 + adjustment) == money

    # No remainder
    result, adjustment = money.divide_with_adjustment(4)
    assert result == Money(5, usd)
    assert adjustment == Money(0, usd)

def test_divide_with_adjustment_half_down():
    Money.rounding.set(decimal.ROUND_HALF_DOWN)
    usd = Currency("USD")
    money = Money(20, usd)

    # Division with remainder
    result, adjustment = money.divide_with_adjustment(7)
    assert result == Money(2.86, usd)
    assert adjustment == Money(-0.02, usd)

    # Verify original value
    assert (result * 7 + adjustment) == money

    # No remainder
    result, adjustment = money.divide_with_adjustment(4)
    assert result == Money(5, usd)
    assert adjustment == Money(0, usd)
    Money.rounding.set(decimal.ROUND_DOWN)

def test_rtruediv_unsupported():
    usd = Currency("USD")
    money = Money(20, usd)

    # Reverse division (unsupported)
    with pytest.raises(MoneyDivisionIllegal):
        10 / money

def test_rounding_single_thread():
    Money.rounding.set(decimal.ROUND_HALF_UP)
    money = Money(10.25, "USD")
    result = money / 3
    assert str(result) == "3.42 USD"

    Money.rounding.set(decimal.ROUND_DOWN)
    result = money / 3
    assert str(result) == "3.41 USD"

def test_rounding_multi_thread():
    results = {}

    def thread_func(thread_id, rounding_mode):
        Money.rounding.set(rounding_mode)
        money = Money(10.25, "USD")
        results[thread_id] = str(money / 3)

    threads = [
        threading.Thread(target=thread_func, args=(1, decimal.ROUND_HALF_UP)),
        threading.Thread(target=thread_func, args=(2, decimal.ROUND_DOWN)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results[1] == "3.42 USD"
    assert results[2] == "3.41 USD"

def test_floordiv_money():
    usd = Currency("USD")
    money = Money(20, usd)

    result = money // 6
    assert result == Money(3, usd)

def test_floordiv_zero():
    usd = Currency("USD")
    money = Money(20, usd)

    with pytest.raises(ZeroDivisionError):
        money // 0

def test_floordiv_invalid():
    usd = Currency("USD")
    money = Money(20, usd)

    with pytest.raises(
            MoneyInvalidOperation,
            match=re.escape("Unsupported operand type(s) for //: 'Money' and 'str'")
    ):
        money // "string"

def test_rfloordiv_invalid():
    usd = Currency("USD")
    money = Money(20, usd)

    with pytest.raises(MoneyDivisionIllegal):
        10 // money

def test_modulo_with_valid_numeric_types():
    usd = Currency("USD")
    money = Money(20, usd)

    # Modulo with int
    result = money % 6
    assert result == Money(2, usd)

    # Modulo with float
    result = money % 7.5
    assert result == Money(5, usd)

    # Modulo with Decimal
    result = money % Decimal("7")
    assert result == Money(6, usd)

def test_modulo_with_zero():
    usd = Currency("USD")
    money = Money(20, usd)

    # Modulo by zero
    with pytest.raises(ZeroDivisionError):
        money % 0

def test_modulo_with_invalid_types():
    usd = Currency("USD")
    money = Money(20, usd)

    # Modulo with string
    with pytest.raises(MoneyInvalidOperation, match="Unsupported operand type\\(s\\) for %: 'Money' and 'str'"):
        money % "string"

    # Reverse modulo with int
    with pytest.raises(MoneyDivisionIllegal):
        6 % money

def test_modulo_by_money():
    usd = Currency("USD")
    money = Money(20, usd)

    # Modulo by zero
    with pytest.raises(MoneyDivisionIllegal):
        100 % money

def test_exponentiation_not_supported():
    usd = Currency("USD")
    money = Money(100, usd)

    # Forward exponentiation
    with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ** or pow(): 'Money' and 'int'")):
        money ** 2

    # Reverse exponentiation
    with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ** or pow(): 'int' and 'Money'")):
        2 ** money

def test_abs_positive_value():
    usd = Currency("USD")
    money = Money(50.05, usd)
    assert abs(money) == Money(50.05, usd)

def test_abs_negative_value():
    usd = Currency("USD")
    money = Money(-50, usd)
    assert abs(money) == Money(50, usd)

def test_abs_zero_value():
    usd = Currency("USD")
    money = Money(0, usd)
    assert abs(money) == Money(0, usd)

from decimal import ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_FLOOR, ROUND_CEILING

def test_set_rounding_explicit_value():
    # Explicitly set thread-local rounding
    Money.rounding.set(ROUND_HALF_DOWN)
    assert Money.rounding.get() == ROUND_HALF_DOWN

def test_set_rounding_defaults_to_global():
    # Set global default rounding
    Money.rounding.set_default(ROUND_CEILING)

    # Set thread-local rounding to use the global default
    Money.rounding.set()
    assert Money.rounding.get() == ROUND_CEILING

def test_set_global_rounding_changes_default():
    # Set a new global default
    Money.rounding.set_default(ROUND_FLOOR)

    # Reset thread-local rounding to use the global default
    Money.rounding.reset()
    assert Money.rounding.get() == ROUND_FLOOR

def test_reset_rounding_uses_global_default():
    # Set global rounding to ROUND_HALF_UP
    Money.rounding.set_default(ROUND_HALF_UP)

    # Override thread-local rounding
    Money.rounding.set(ROUND_FLOOR)
    assert Money.rounding.get() == ROUND_FLOOR

    # Reset to use global default
    Money.rounding.reset()
    assert Money.rounding.get() == ROUND_HALF_UP

def test_thread_local_rounding_is_independent():
    # Set global rounding to ROUND_HALF_DOWN
    Money.rounding.set_default(ROUND_HALF_DOWN)

    # Thread 1: Set ROUND_CEILING
    Money.rounding.set(ROUND_CEILING)
    assert Money.rounding.get() == ROUND_CEILING

    # Reset and ensure global default applies
    Money.rounding.reset()
    assert Money.rounding.get() == ROUND_HALF_DOWN

def test_round_to_fewer_decimals():
    usd = Currency("USD")
    amount = Money("2.359", usd)

    # Round to 1 decimal place
    result = round(amount, 1)
    assert result == Money("2.30", usd)

def test_round_to_more_decimals_than_subunit():
    usd = Currency("USD")
    amount = Money("2.35", usd)

    # Attempt to round to 3 decimal places (exceeds subunit precision)
    result = round(amount, 3)
    assert result == amount  # Should remain unchanged

def test_round_to_zero_decimals():
    usd = Currency("USD")
    amount = Money("2.359", usd)

    # Round to 0 decimal places
    result = round(amount, 0)
    assert result == Money("2", usd)

def test_round_respects_default_rounding():
    Money.rounding.set_default(ROUND_HALF_UP)
    usd = Currency("USD")
    amount = Money("2.359", usd)

    # Default rounding mode ROUND_HALF_UP
    result = round(amount, 1)
    assert result == Money("2.40", usd)

def test_comparisons_valid():
    usd = Currency("USD")
    money1 = Money("10.00", usd)
    money2 = Money("15.00", usd)

    # Valid comparisons
    assert money1 < money2
    assert money1 <= money2
    assert money2 > money1
    assert money2 >= money1
    assert money1 <= Money("10.00", usd)
    assert money1 >= Money("10.00", usd)

def test_comparisons_invalid_currency():
    usd = Currency("USD")
    eur = Currency("EUR")
    money1 = Money("10.00", usd)
    money2 = Money("10.00", eur)

    # Invalid comparison due to different currencies
    with pytest.raises(CurrencyMismatch):
        _ = money1 < money2

def test_comparisons_invalid_type():
    usd = Currency("USD")
    money1 = Money("10.00", usd)

    # Comparison with non-Money object should raise TypeError
    with pytest.raises(TypeError, match="'<' not supported between instances of 'Money' and 'int'"):
        _ = money1 < 10

def test_iter():
    eur = Currency("EUR")
    money = Money(100, eur)

    # Unpacking as a tuple
    amount, currency = money
    assert amount == 100
    assert currency is eur

    # Iterating over the Money object
    result = list(money)
    assert result == [100, eur]

def test_amount_and_currency_code():
    money = Money(100, EUR)

    amount, currency = money.amount_and_currency_code()
    assert amount == 100
    assert isinstance(currency, str)
    assert currency == 'EUR'

def test_as_dict():
    usd = Currency("USD")
    money = Money(100, usd)

    # Dictionary representation
    assert money.as_dict() == {'amount': 100, 'currency': usd}

def test_getitem():
    usd = Currency("USD")
    money = Money(100, usd)

    # Accessing components like a dictionary
    assert money['amount'] == 100
    assert money['currency'] == usd

    # Attempting to access an invalid key
    with pytest.raises(KeyError, match="'invalid_key'"):
        _ = money['invalid_key']

def test_keys():
    usd = Currency("USD")
    money = Money(100, usd)

    # Check available keys
    assert money.keys() == ['amount', 'currency']

def test_contains():
    usd = Currency("USD")
    money = Money(100, usd)

    # Valid keys
    assert 'amount' in money
    assert 'currency' in money

    # Invalid keys
    assert 'invalid_key' not in money

def test_items():
    usd = Currency("USD")
    money = Money(100, usd)

    # Iterating over key-value pairs
    items = list(money.items())
    assert items == [('amount', 100), ('currency', usd)]

    # Direct unpacking from items
    for key, value in money.items():
        if key == 'amount':
            assert value == 100
        elif key == 'currency':
            assert value == usd

@pytest.mark.usefixtures("mock_save_user_currencies")
class TestMoneyParsers:
    def setup_method(self):
        """Reset parser settings before each test."""
        Money.parser.set_default(parsers.BaseParser())
        Money.parser.set(None)

    def test_global_parser(self):
        """Verify the global parser is used when no thread-local parser is set."""
        parser = parsers.SimpleParserWithSubstitutions({"$": "USD", ",": ""})
        Money.parser.set_default(parser)

        money = Money("1,000.50$")
        assert str(money) == "1000.50 USD"

    def test_thread_local_parser(self):
        """Verify the thread-local parser overrides the global parser."""
        global_parser = parsers.BaseParser()
        thread_local_parser = parsers.SimpleParserWithSubstitutions({"€": "EUR"})

        Money.parser.set_default(global_parser)
        Money.parser.set(thread_local_parser)

        money = Money("€123.45")
        assert str(money) == "123.45 EUR"

    def test_thread_local_parser_does_not_affect_global(self):
        """Verify thread-local parser settings do not change global behavior."""
        global_parser = parsers.SimpleParserWithSubstitutions({"$": "USD"})
        Money.parser.set_default(global_parser)

        Money.parser.set(parsers.SimpleParserWithSubstitutions({"€": "EUR"}))

        # Thread-local parser is ignored outside the current thread
        money = Money("€123.45")
        assert str(money) == "123.45 EUR"  # Global parser handles this

    def test_parser_thread_safety(self):
        """Test that parsers are thread-safe and do not interfere across threads."""
        exceptions = []
        def thread1_task():
            try:
                Money.parser.set(parsers.SimpleParserWithSubstitutions({"$": "USD"}))
                money = Money("$50")
                assert str(money) == "50.00 USD"  # Pass
                Money("€50")  # Fail
            except Exception as e:
                exceptions.append(e)

        def thread2_task():
            try:
                Money.parser.set(parsers.SimpleParserWithSubstitutions({"€": "EUR"}))
                money = Money("€50")
                assert str(money) == "50.00 EUR"  # Pass
                Money("$100")  # Fail
            except Exception as e:
                exceptions.append(e)

        thread1 = threading.Thread(target=thread1_task)
        thread2 = threading.Thread(target=thread2_task)

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        assert len(exceptions) == 2
        with pytest.raises(ValueError):
            raise exceptions[0]
        with pytest.raises(ValueError):
            raise exceptions[1]

    def test_reset_thread_local_parser(self):
        """Test resetting thread-local parser restores global parser."""
        global_parser = parsers.SimpleParserWithSubstitutions({"$": "USD"})
        Money.parser.set_default(global_parser)

        Money.parser.set(parsers.SimpleParserWithSubstitutions({"€": "EUR"}))
        Money.parser.set(None)

        money = Money("$123.45")
        assert str(money) == "123.45 USD"  # Global parser is now used

class TestDefaultCurrencyStandalone:
    def setup_method(self):
        """Reset the default currency before each test."""
        DefaultCurrency.set(XXX)

    def test_default_currency_initial(self):
        """Verify the initial default currency is 'XXX'."""
        assert DefaultCurrency.get().code == "XXX"

    def test_set_default_currency(self):
        """Test setting the default currency."""
        DefaultCurrency.set("USD")
        assert DefaultCurrency.get().code == "USD"

    def test_set_default_currency_with_currency_object(self):
        """Test setting the default currency using a Currency object."""
        DefaultCurrency.set(Currency("EUR"))
        assert DefaultCurrency.get().code == "EUR"

    def test_thread_safety(self):
        """Test that default currency changes are thread-safe."""
        def set_currency_in_thread(code):
            DefaultCurrency.set(code)
            assert DefaultCurrency.get().code == code

        thread1 = threading.Thread(target=set_currency_in_thread, args=("RUB",))
        thread2 = threading.Thread(target=set_currency_in_thread, args=("KES",))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # After threads, check the last set currency
        final_currency = DefaultCurrency.get()
        assert final_currency.code in ("RUB", "KES")  # Either thread's update is valid

    def test_reset_default_currency(self):
        """Verify resetting to 'XXX' works."""
        DefaultCurrency.set("USD")
        assert DefaultCurrency.get().code == "USD"

        DefaultCurrency.set(XXX)
        assert DefaultCurrency.get() is XXX


class TestMoneyDefaultCurrency:
    def setup_method(self):
        """Reset the global default currency to 'XXX' before each test."""
        Money.default_currency.set(XXX)

    def test_default_currency_applied(self):
        """Test that the default currency is applied when no currency is specified."""
        money = Money(100)  # No currency specified
        assert money.currency.code == "XXX"
        assert money.amount == 100

    def test_set_default_currency_globally(self):
        """Test that changing the global default currency affects new Money instances."""
        Money.default_currency.set("USD")
        money = Money(200)  # No currency specified
        assert money.currency.code == "USD"
        assert money.amount == 200

    def test_default_currency_with_currency_specified(self):
        """Test that specifying a currency overrides the default currency."""
        Money.default_currency.set("USD")
        money = Money(300, "EUR")
        assert money.currency.code == "EUR"
        assert money.amount == 300

    def test_thread_safety_of_default_currency(self):
        """Test that changes to the default currency are thread-safe."""
        def set_default_currency_in_thread(code):
            Money.default_currency.set(code)
            assert Money.default_currency.get().code == code

        thread1 = threading.Thread(target=set_default_currency_in_thread, args=("USD",))
        thread2 = threading.Thread(target=set_default_currency_in_thread, args=("EUR",))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Check final state
        final_currency = Money.default_currency.get()
        assert final_currency.code in ("USD", "EUR")  # Either thread's update is valid
