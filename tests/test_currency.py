import pytest
from unittest.mock import patch

import threading

from simple_money_lib.currency import Currency
from simple_money_lib.errors import CurrencyExistsError, CurrencyCodeInvalid

# Reset the class for each test to clean state
@pytest.fixture(autouse=True)
def reset_currency_registry():
    Currency._registry.clear()
    Currency.strict_mode = False

@pytest.fixture(autouse=True)
def mock_user_defined_currencies():
    """Mock _user_defined_currencies with a temporary dictionary."""
    with patch("simple_money_lib.currency._user_defined_currencies", {}):
        yield

@pytest.fixture(autouse=True)
def mock_save_user_currencies():
    """Mock save_user_currencies to prevent actual writes to disk."""
    with patch("simple_money_lib.currency.save_user_currencies") as mock_save:
        yield mock_save

def test_is_valid_code():
    """Test the _is_valid_code static method."""
    valid_codes = ["USD", "btc", "CRYPTO_1", "abc123", "A123456"]
    invalid_codes = ["", "AB", "ABCDEFGHI", "1USD", "U@SD", None, 12345]

    for code in valid_codes:
        assert Currency._is_valid_code(code) is True

    for code in invalid_codes:
        assert Currency._is_valid_code(code) is False

def test_currency_code_validation():
    """Test that valid and invalid codes are handled correctly in __new__ and register."""
    # Valid codes that need to be registered first
    valid_codes = ["USD", " btc ", "CRYPTO_1", "abc123"]
    for code in valid_codes:
        # Dynamically register valid codes to avoid reliance on predefined metadata
        Currency.register(code.strip().upper(), numeric=999, sub_unit=2, name=f"Test Currency {code.strip().upper()}")
        currency = Currency(code)
        assert currency.code == code.strip().upper()

    # Invalid codes
    invalid_codes = ["", "AB", "ABCDEFGHI", "1USD", "U@SD", None, 12345]
    for code in invalid_codes:
        with pytest.raises(CurrencyCodeInvalid, match=f"Invalid currency code: '{code}'"):
            Currency(code)

def test_predefined_currency():
    """Test creation of predefined currency."""
    usd = Currency("USD")
    assert usd.code == "USD"
    assert usd.name == "United States dollar"
    assert usd.sub_unit == 2
    assert usd.numeric == 840

def test_register_new_currency():
    """Test registering a new currency."""
    btc = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    assert btc.code == "BTC"
    assert btc.name == "Bitcoin"
    assert btc.sub_unit == 8
    assert btc.numeric == 1000

def test_register_default_mode_is_non_strict():
    """Test non-strict mode returns existing instance."""
    btc1 = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    btc2 = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    assert btc1 is btc2

def test_register_strict_mode():
    """Test strict mode prevents duplicates."""
    Currency.strict_mode = True
    Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    with pytest.raises(CurrencyExistsError):
        Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")

def test_register_non_strict_mode():
    Currency.strict_mode = False
    """Test non-strict mode returns existing instance."""
    btc1 = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    btc2 = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    assert btc1 is btc2

def test_thread_safety():
    """Test thread safety of register."""
    results = []
    Currency.strict_mode = False
    def register_btc():
        try:
            btc = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
            results.append(btc)
        except Exception as e:
            results.append(e)

    threads = [threading.Thread(target=register_btc) for _ in range(50)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # All threads should return the same instance
    assert len(results) == 50
    assert all(r is results[0] for r in results)

@patch("simple_money_lib.currency.save_user_currencies")
def test_register_saves_user_currencies(mock_save):
    """Test that user-defined currencies are saved after registration."""
    Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
    mock_save.assert_called_once()
