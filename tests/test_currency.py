import pytest

import threading

from simple_money_lib.currency import Currency
from simple_money_lib.errors import *

# Reset the class for each test to clean state
@pytest.fixture(autouse=True)
def reset_currency_registry():
    Currency._registry.clear()
    Currency.strict_mode = True

def test_missing_code():
    with pytest.raises(TypeError):
        Currency(numeric="840", sub_unit=2, name="Missing Code")

def test_get_currency():
    USD = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    assert Currency.get('USD') is USD

def test_currency_not_registered_error():
    with pytest.raises(CurrencyNotRegisteredError) as exc_info:
        Currency.get("XYZ")
    assert exc_info.value.code == "XYZ"
    assert str(exc_info.value) == "Currency with code 'XYZ' is not registered."

def test_currency_exists_error():
    Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    with pytest.raises(CurrencyExistsError) as exc_info:
        Currency("USD", numeric="840", sub_unit=2, name="Duplicate US Dollar")
    assert exc_info.value.code == "USD"
    assert str(exc_info.value) == "Currency with code 'USD' is already registered."

def test_singleton_behavior_default():
    _USD = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")

    # Attempt to register the same currency should raise CurrencyExistsError
    with pytest.raises(CurrencyExistsError) as exc_info:
        Currency("USD", numeric="840", sub_unit=2, name="Duplicate US Dollar")

    # Verify exception details
    assert exc_info.value.code == "USD"
    assert str(exc_info.value) == "Currency with code 'USD' is already registered."

def test_singleton_behavior_strict():
    Currency.strict_mode = True
    _USD = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")

    # Attempt to register the same currency should raise CurrencyExistsError
    with pytest.raises(CurrencyExistsError) as exc_info:
        Currency("USD", numeric="840", sub_unit=2, name="Duplicate US Dollar")

    # Verify exception details
    assert exc_info.value.code == "USD"
    assert str(exc_info.value) == "Currency with code 'USD' is already registered."

def test_singleton_behavior_relaxed():
    Currency.strict_mode = False
    USD1 = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    USD2 = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    assert USD1 is USD2

def test_all_currencies():
    USD = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    EUR = Currency("EUR", numeric="978", sub_unit=2, name="Euro")
    all_currencies = Currency.all_currencies()

    assert "USD" in all_currencies
    assert "EUR" in all_currencies
    assert all_currencies["USD"] is USD
    assert all_currencies["EUR"] is EUR
    assert len(all_currencies) == 2

def test_string_representation():
    USD = Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    USD = Currency.get('USD')
    assert str(USD) == "USD"
    assert repr(USD) == "Currency(code='USD', name='US Dollar', numeric='840')"

def test_thread_safety():
    Currency.strict_mode = False
    def register_jpy():
        Currency("JPY", numeric="392", sub_unit=0, name="Japanese yen")

    threads = [threading.Thread(target=register_jpy) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Ensure only one instance of USD exists
    assert len(Currency.all_currencies()) == 1
    assert "JPY" in Currency._registry

def test_numeric_code_stored_correctly():
    # Register two currencies with different numeric codes
    Currency("USD", numeric="840", sub_unit=2, name="US Dollar")
    Currency("XCD", numeric="951", sub_unit=2, name="East Caribbean Dollar")

    # Retrieve all registered currencies
    all_currencies = Currency.all_currencies()

    # Ensure both currencies are registered and their numeric codes are correct
    assert len(all_currencies) == 2
    assert all_currencies["USD"].numeric == "840"
    assert all_currencies["XCD"].numeric == "951"

def test_currency_extension():
    class CryptoCurrency(Currency):
        pass

    BTC = CryptoCurrency("BTC", numeric=None, sub_unit=8, name="Bitcoin")
    assert str(BTC) == "BTC"
    assert isinstance(BTC, CryptoCurrency)
