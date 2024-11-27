import pytest
from unittest.mock import patch
import re

from simple_money_lib.currency import Currency
from simple_money_lib.errors import CurrencyNotFoundError, CurrencyCodeInvalid
from simple_money_lib.collections.currency_collections import CurrencyCollection
from simple_money_lib.currencies.all import EUR, RUB

@pytest.fixture
def sample_collection():
    """Fixture to create a sample CurrencyCollection."""
    return CurrencyCollection("USD", EUR, "RUB", name="Collection name here", description="Description comes")


def test_collection_initialization(sample_collection):
    """Test initialization of a CurrencyCollection."""
    assert sample_collection.name == "Collection name here"
    assert sample_collection.description == "Description comes"
    assert len(sample_collection._currencies) == 3
    assert "USD" in sample_collection
    assert "EUR" in sample_collection
    assert RUB in sample_collection
    assert "AED" not in sample_collection


def test_currency_object_membership(sample_collection):
    """Test membership checks with Currency objects."""
    usd = Currency("USD")
    jpy = Currency("JPY")  # Not in the collection
    assert usd in sample_collection
    assert jpy not in sample_collection


def test_string_membership(sample_collection):
    """Test membership checks with string codes."""
    assert "RUB" in sample_collection
    assert "AED" not in sample_collection


def test_iteration_over_collection(sample_collection):
    """Test iterating over a CurrencyCollection."""
    currencies = list(sample_collection)
    assert len(currencies) == 3
    assert all(isinstance(currency, Currency) for currency in currencies)
    assert {currency.code for currency in currencies} == {"USD", "EUR", "RUB"}


def test_repr(sample_collection):
    """Test the string representation of a CurrencyCollection."""
    assert repr(sample_collection) == "CurrencyCollection(USD, EUR, RUB)"


def test_dynamic_addition_to_collection():
    """Test creating and adding new currencies dynamically."""
    with patch("simple_money_lib.currency.save_user_currencies"):
        # Register the custom currencies
        btc = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
        eth = Currency.register("ETH", numeric=1001, sub_unit=8, name="Ethereum")

        # Create a collection with one custom currency
        collection = CurrencyCollection("BTC", name="Crypto Collection", description="Top cryptocurrencies")
        assert "BTC" in collection
        assert collection.name == "Crypto Collection"
        assert collection.description == "Top cryptocurrencies"

        # Add a second custom currency dynamically
        collection._currencies["ETH"] = eth  # Simulate dynamic addition
        assert "ETH" in collection
        assert eth in collection


def test_invalid_currency():
    """Test invalid input to CurrencyCollection."""
    with pytest.raises(ValueError, match="Invalid currency: 123"):
        CurrencyCollection(123, name="Invalid Collection")

    with pytest.raises(ValueError, match="Invalid currency: None"):
        CurrencyCollection(None, name="Invalid Collection")


def test_empty_collection():
    """Test an empty CurrencyCollection."""
    empty_collection = CurrencyCollection(name="Empty", description="No currencies here")
    assert len(empty_collection._currencies) == 0
    assert "USD" not in empty_collection
    assert repr(empty_collection) == "CurrencyCollection()"

def test_contains_valid_and_invalid():
    """Test valid and invalid currency membership checks."""
    collection = CurrencyCollection("USD", EUR, "RUB", "XYZ1")

    # Valid currencies
    assert "USD" in collection
    assert "EUR" in collection
    assert Currency("USD") in collection

    # Invalid currencies
    assert "XYZ1" not in collection
    assert "123" not in collection
    # Ensure invalid currency objects are not used directly
    with pytest.raises(CurrencyNotFoundError):
        Currency("XYZ1")  # Verifies that creating an invalid Currency raises an exception


def test_initialization_with_invalid_currencies():
    """Test initialization with invalid currencies (valid name but not defined)."""
    collection = CurrencyCollection("USD", "EUR", "INVALID")
    assert len(collection._currencies) == 2  # Only "USD" and "EUR"
    assert "INVALID" not in collection

def test_invalid_currency_code_in_initialization():
    """Test that invalid currency codes raise an error during initialization."""
    with pytest.raises(CurrencyCodeInvalid, match=re.escape("Invalid currency code: '123'")):
        CurrencyCollection("USD", "EUR", "123")  # '123' is invalid

    with pytest.raises(CurrencyCodeInvalid, match=re.escape("Invalid currency code: '@$#'")):
        CurrencyCollection("USD", "EUR", "@$#")  # '@$#' is invalid

    with pytest.raises(CurrencyCodeInvalid, match=re.escape("Invalid currency code: ''")):
        CurrencyCollection("USD", "EUR", "")  # Empty string is invalid

